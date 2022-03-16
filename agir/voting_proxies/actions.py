from copy import deepcopy
from datetime import timedelta
from functools import partial

from data_france.models import Commune
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction
from django.db.models import Count, Q, Case, When, Value
from django.utils import timezone

from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    save_subscription_information,
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_AP,
)
from agir.people.models import Person
from agir.voting_proxies import tasks
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest
from agir.voting_proxies.tasks import (
    send_voting_proxy_request_confirmation,
    send_voting_proxy_request_accepted_text_messages,
    send_voting_proxy_request_confirmed_text_messages,
)

# TODO: Choose a proxy-to-request distance limit (in meters)
PROXY_TO_REQUEST_DISTANCE_LIMIT = 30000  # 30 KM
PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT = 10


def create_or_update_voting_proxy_request(data):
    data = deepcopy(data)
    email = data.pop("email")
    voting_dates = data.pop("votingDates")
    updated = False
    voting_proxy_request_pks = []

    for voting_date in voting_dates:
        (voting_proxy_request, created) = VotingProxyRequest.objects.update_or_create(
            voting_date=voting_date,
            email=email,
            defaults={**data},
        )
        voting_proxy_request_pks.append(voting_proxy_request.id)
        if not created:
            updated = True

    data.update({"email": email, "votingDates": voting_dates, "updated": updated})
    send_voting_proxy_request_confirmation.delay(voting_proxy_request_pks)

    return data


def create_or_update_voting_proxy(data):
    data["voting_dates"] = list(data.get("voting_dates"))
    email = data.pop("email")

    person_data = {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "date_of_birth": data.get("date_of_birth", ""),
        "email": email,
        "contact_phone": data.get("contact_phone", ""),
        "is_2022": True,
    }

    with transaction.atomic():
        is_new_person = False
        try:
            with transaction.atomic():
                person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            person = Person.objects.create_person(**person_data)
            is_new_person = True

        person_data["newsletters"] = data.pop("newsletters", [])
        save_subscription_information(
            person, SUBSCRIPTION_TYPE_AP, person_data, new=is_new_person
        )

        # Update person address if needed
        address = data.pop("address", None)
        city = data.pop("city", None)
        zip = data.pop("zip", None)
        if address:
            person.location_address1 = address
        if city:
            person.location_city = city
        if zip:
            person.location_zip = zip
        elif data.get("commune", None) and data["commune"].codes_postaux.exists():
            person.location_zip = data["commune"].codes_postaux.first().code
        person.save()

        voting_proxy, created = VotingProxy.objects.update_or_create(
            email=email, defaults={**data, "person_id": person.pk}
        )
        if voting_proxy.status == VotingProxy.STATUS_INVITED:
            voting_proxy.status = VotingProxy.STATUS_CREATED
            voting_proxy.save()

    if is_new_person and "welcome" in SUBSCRIPTIONS_EMAILS[SUBSCRIPTION_TYPE_AP]:
        from agir.people.tasks import send_welcome_mail

        send_welcome_mail.delay(person.pk, type=SUBSCRIPTION_TYPE_AP)

    geocode_person.delay(person.pk)

    data.update(
        {
            "id": voting_proxy.id,
            "updated": not created,
            "person_id": person.id,
            "email": email,
            "status": voting_proxy.status,
        }
    )

    return data


def update_voting_proxy(instance, data):
    if "voting_dates" in data:
        data["voting_dates"] = list(data.get("voting_dates"))
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def get_voting_proxy_requests_for_proxy(voting_proxy, voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        status=VotingProxyRequest.STATUS_CREATED,
        voting_date__in=voting_proxy.available_voting_dates,
        proxy__isnull=True,
    ).exclude(email=voting_proxy.email)

    # Use consulate match for non-null consulate proxies
    if voting_proxy.consulate_id is not None:
        voting_proxy_requests = voting_proxy_requests.filter(
            consulate_id=voting_proxy.consulate_id,
        ).annotate(distance=Value(0))
    # Use voting_proxy person address to request commune distance,
    # fallback to commune match for non-null commune proxies
    else:
        near_requests = None
        if voting_proxy.person and voting_proxy.person.coordinates:
            near_requests = (
                voting_proxy_requests.filter(commune__mairie_localisation__isnull=False)
                .annotate(
                    distance=Distance(
                        "commune__mairie_localisation", voting_proxy.person.coordinates
                    )
                )
                .filter(distance__lte=PROXY_TO_REQUEST_DISTANCE_LIMIT)
            )
        if near_requests and near_requests.exists():
            voting_proxy_requests = near_requests
        else:
            voting_proxy_requests = voting_proxy_requests.filter(
                commune_id=voting_proxy.commune_id,
            ).annotate(distance=Value(0))

    if len(voting_proxy_request_pks) > 0:
        voting_proxy_requests = voting_proxy_requests.filter(
            id__in=voting_proxy_request_pks
        )

    voting_proxy_requests = voting_proxy_requests.annotate(
        polling_station_match=Case(
            When(
                commune_id=voting_proxy.commune_id,
                polling_station_number__isnull=False,
                polling_station_number__iexact=voting_proxy.polling_station_number,
                then=1,
            ),
            default=0,
        )
    )

    # group by email to prioritize requests with the greatest matching date count
    voting_proxy_requests = (
        voting_proxy_requests.values("email")
        .annotate(ids=ArrayAgg("id"))
        .annotate(matching_date_count=Count("voting_date"))
        .order_by("-matching_date_count", "-polling_station_match", "distance")
    )

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist

    return VotingProxyRequest.objects.filter(
        id__in=voting_proxy_requests.first()["ids"]
    ).order_by("voting_date")


def accept_voting_proxy_requests(voting_proxy, voting_proxy_requests):
    voting_proxy_request_pks = list(voting_proxy_requests.values_list("pk", flat=True))
    with transaction.atomic():
        voting_proxy.status = VotingProxy.STATUS_AVAILABLE
        voting_proxy.save()
        voting_proxy_requests.update(
            status=VotingProxyRequest.STATUS_ACCEPTED, proxy=voting_proxy
        )

    transaction.on_commit(
        partial(
            send_voting_proxy_request_accepted_text_messages.delay,
            voting_proxy_request_pks,
        )
    )


def decline_voting_proxy_requests(voting_proxy, voting_proxy_requests):
    voting_proxy.status = VotingProxy.STATUS_UNAVAILABLE
    voting_proxy.save()


def confirm_voting_proxy_requests(voting_proxy_requests):
    voting_proxy_request_pks = list(voting_proxy_requests.values_list("pk", flat=True))
    voting_proxy_requests.update(status=VotingProxyRequest.STATUS_CONFIRMED)
    send_voting_proxy_request_confirmed_text_messages.delay(voting_proxy_request_pks)


def send_matching_requests_to_proxy(proxy, matching_request_ids):
    proxy.last_matched = timezone.now()
    proxy.save()
    tasks.send_matching_request_to_voting_proxy.delay(
        proxy.id, list(matching_request_ids)
    )


def match_available_proxies_with_requests(
    pending_requests, notify_proxy=send_matching_requests_to_proxy
):
    fulfilled_request_ids = []

    # Retrieve all available proxy that has not been matched in the last two days
    available_proxies = (
        VotingProxy.objects.filter(
            status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
        )
        .exclude(last_matched__date__gt=timezone.now() - timedelta(days=2))
        .order_by("-voting_dates__len")
    )

    # Try to match available voting proxies with pending requests
    for proxy in available_proxies:
        pending_requests = pending_requests.exclude(id__in=fulfilled_request_ids)
        if not pending_requests.exists():
            break
        try:
            matching_request_ids = get_voting_proxy_requests_for_proxy(
                proxy, pending_requests.values_list("id", flat=True)
            ).values_list("id", flat=True)
        except VotingProxyRequest.DoesNotExist:
            pass
        else:
            notify_proxy(proxy, matching_request_ids)
            fulfilled_request_ids += matching_request_ids

    return fulfilled_request_ids


def invite_voting_proxy_candidates(candidates):
    voting_proxy_candidates = [
        VotingProxy(
            status=VotingProxy.STATUS_INVITED,
            person=candidate,
            email=candidate.email,
            first_name=candidate.first_name if candidate.first_name else "-",
            last_name=candidate.last_name if candidate.first_name else "-",
            contact_phone=candidate.contact_phone if candidate.first_name else "-",
            polling_station_number="",
        )
        for candidate in candidates
    ]
    voting_proxy_candidates = VotingProxy.objects.bulk_create(
        voting_proxy_candidates, ignore_conflicts=True
    )
    voting_proxy_candidates_ids = [
        voting_proxy_candidate.pk for voting_proxy_candidate in voting_proxy_candidates
    ]
    tasks.send_voting_proxy_candidate_invitation_email.delay(
        voting_proxy_candidates_ids
    )

    return voting_proxy_candidates_ids


def get_voting_proxy_candidates_queryset(request, blacklist_ids):
    candidates = (
        Person.objects.exclude(
            id__in=VotingProxy.objects.values_list("person_id", flat=True)
        )
        .exclude(emails__address=None)
        .filter(is_2022=True, newsletters__len__gt=0)
    )
    if request and request["email"]:
        candidates = candidates.exclude(emails__address=request["email"])
    if blacklist_ids:
        candidates = candidates.exclude(id__in=blacklist_ids)

    return candidates


def find_voting_proxy_candidates_for_requests(
    pending_requests, send_invitations=invite_voting_proxy_candidates
):
    possibly_fulfilled_request_ids = []
    candidate_ids = []

    # Find candidates for consulate requests
    for request in (
        pending_requests.exclude(consulate__pays__isnull=True)
        .values("email", "consulate__pays")
        .annotate(ids=ArrayAgg("id"))
    ):
        candidates = get_voting_proxy_candidates_queryset(
            request, candidate_ids
        ).filter(location_country__in=request["consulate__pays"].split(","))[
            :PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT
        ]

        if candidates.exists():
            invited_candidate_ids = send_invitations(candidates)
            candidate_ids += invited_candidate_ids
            possibly_fulfilled_request_ids += request["ids"]

    # Find candidates for commune requests
    for request in (
        pending_requests.exclude(commune__isnull=True)
        .values(
            "email",
            "commune__id",
            "commune__mairie_localisation",
        )
        .annotate(ids=ArrayAgg("id"))
    ):
        candidates = get_voting_proxy_candidates_queryset(request, candidate_ids)

        # Match by distance for geolocalised communes
        if request["commune__mairie_localisation"]:
            candidates = candidates.exclude(coordinates__isnull=True).filter(
                coordinates__dwithin=(
                    request["commune__mairie_localisation"],
                    D(m=PROXY_TO_REQUEST_DISTANCE_LIMIT),
                )
            )
        # Try to match by city code / zip code for non-geolocalised communes
        else:
            commune = Commune.objects.get(id=request["commune__id"])
            candidates = (
                candidates.exclude(
                    location_citycode__isnull=True, location_zip__isnull=True
                )
                .filter(
                    Q(location_citycode=commune.code)
                    | Q(
                        location_zip__in=commune.codes_postaux.values_list(
                            "code", flat=True
                        )
                    )
                )
                .distinct()
            )

        if candidates.exists():
            # Give priority with people with the most recent event rsvps
            candidates = candidates.annotate(
                rsvp_count=Count(
                    "rsvps",
                    filter=Q(
                        rsvps__event__end_time__gte=timezone.now() - timedelta(days=365)
                    ),
                    distinct=True,
                )
            ).order_by("-rsvp_count")[:PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT]

            invited_candidate_ids = send_invitations(candidates)
            candidate_ids += invited_candidate_ids
            possibly_fulfilled_request_ids += request["ids"]

    return possibly_fulfilled_request_ids, candidate_ids
