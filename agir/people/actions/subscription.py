from dataclasses import dataclass
from functools import partial

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.elus.models import types_elus, StatutMandat, MandatMunicipal
from agir.groups.models import Membership
from agir.lib.http import add_query_params_to_url
from agir.people.models import Person


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)


@dataclass
class SubscriptionMessageInfo:
    code: str
    subject: str
    from_email: str = settings.EMAIL_FROM


SUBSCRIPTION_TYPE_LFI = "LFI"
SUBSCRIPTION_TYPE_NSP = "NSP"
SUBSCRIPTION_TYPE_EXTERNAL = "EXT"
SUBSCRIPTION_TYPE_ADMIN = "ADM"
SUBSCRIPTION_TYPE_AP = "AP"
SUBSCRIPTION_TYPE_LJI = "LJI"

SUBSCRIPTION_TYPE_CHOICES = (
    (
        SUBSCRIPTION_TYPE_LFI,
        "LFI",
    ),
    (
        SUBSCRIPTION_TYPE_NSP,
        "NSP",
    ),
    (SUBSCRIPTION_TYPE_EXTERNAL, "Externe"),
    (SUBSCRIPTION_TYPE_AP, "Action Populaire"),
    (SUBSCRIPTION_TYPE_LJI, "Les jeunes insoumis"),
)
SUBSCRIPTION_FIELD = {
    # TODO: Vérifier ce qui est encore utilisé et ce qui ne l'est plus
    SUBSCRIPTION_TYPE_LFI: "is_political_support",
    SUBSCRIPTION_TYPE_NSP: "is_political_support",
    SUBSCRIPTION_TYPE_LJI: "is_political_support",
}

SUBSCRIPTIONS_EMAILS = {
    SUBSCRIPTION_TYPE_LFI: {
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE",
            subject="Plus qu'un clic pour vous inscrire",
            from_email=settings.EMAIL_FROM_LFI,
        ),
        "already_subscribed": SubscriptionMessageInfo(
            "ALREADY_SUBSCRIBED_LFI_MESSAGE",
            "Vous êtes déjà inscrit·e !",
        ),
        "welcome": SubscriptionMessageInfo(
            "WELCOME_LFI_MESSAGE", "Bienvenue sur la plateforme de la France insoumise"
        ),
    },
    SUBSCRIPTION_TYPE_NSP: {
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_NSP_MESSAGE",
            subject="Confirmez votre e-mail pour valider votre signature !",
            from_email=settings.EMAIL_FROM_MELENCHON_2022,
        )
    },
    SUBSCRIPTION_TYPE_LJI: {
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE",
            subject="Plus qu'un clic pour vous inscrire",
            from_email="Les Jeunes Insoumis·es <nepasrepondre@lafranceinsoumise.fr>",
        ),
        "already_subscribed": SubscriptionMessageInfo(
            "ALREADY_SUBSCRIBED_LFI_MESSAGE",
            "Vous êtes déjà inscrit·e !",
        ),
        "welcome": SubscriptionMessageInfo(
            "WELCOME_LFI_MESSAGE",
            "Bienvenue sur la plateforme de la France insoumise et des Jeunes Insoumis·es !",
        ),
    },
    SUBSCRIPTION_TYPE_EXTERNAL: {},
    SUBSCRIPTION_TYPE_AP: {
        "already_subscribed": SubscriptionMessageInfo(
            code="EXISTING_EMAIL_SUBSCRIPTION",
            subject="Vous êtes déjà inscrit·e !",
        ),
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_MESSAGE",
            subject="Plus qu'un clic pour vous inscrire",
        ),
    },
}

SUBSCRIPTION_NEWSLETTERS = {
    SUBSCRIPTION_TYPE_LFI: {*Person.MAIN_NEWSLETTER_CHOICES},
    SUBSCRIPTION_TYPE_LJI: {
        *Person.MAIN_NEWSLETTER_CHOICES,
        Person.Newsletter.LFI_LJI.value,
    },
    SUBSCRIPTION_TYPE_NSP: set(),
    SUBSCRIPTION_TYPE_EXTERNAL: set(),
    SUBSCRIPTION_TYPE_AP: set(),
}

SUBSCRIPTION_EMAIL_SENT_REDIRECT = {
    SUBSCRIPTION_TYPE_LFI: f"{settings.MAIN_DOMAIN}/consulter-vos-emails/",
    SUBSCRIPTION_TYPE_LJI: f"{settings.MAIN_DOMAIN}/consulter-vos-emails/",
    SUBSCRIPTION_TYPE_NSP: f"{settings.NSP_DOMAIN}/validez-votre-e-mail/",
    SUBSCRIPTION_TYPE_AP: f"{settings.FRONT_DOMAIN}/inscription/code/",
}

SUBSCRIPTION_SUCCESS_REDIRECT = {
    SUBSCRIPTION_TYPE_LFI: f"{settings.MAIN_DOMAIN}/bienvenue/",
    SUBSCRIPTION_TYPE_LJI: f"{settings.MAIN_DOMAIN}/bienvenue/",
    SUBSCRIPTION_TYPE_NSP: f"{settings.NSP_DOMAIN}/signature-confirmee/",
    SUBSCRIPTION_TYPE_AP: f"{settings.FRONT_DOMAIN}/bienvenue/",
}


def save_subscription_information(person, type, data, new=False):
    person_fields = set(f.name for f in Person._meta.get_fields())

    # mise à jour des différents champs
    for f in person_fields.intersection(data):
        # Si la personne n'est pas nouvelle on ne remplace que les champs vides
        setattr(person, f, data[f] if new else getattr(person, f) or data[f])

    person.newsletters = list(SUBSCRIPTION_NEWSLETTERS[type].union(person.newsletters))

    if type in SUBSCRIPTION_FIELD and not getattr(person, SUBSCRIPTION_FIELD[type]):
        setattr(person, SUBSCRIPTION_FIELD[type], True)

    subscriptions = person.meta.setdefault("subscriptions", {})
    if type not in subscriptions:
        subscriptions[type] = {"date": timezone.now().isoformat()}
        if referrer_id := data.get("referrer", data.get("referer")):
            try:
                referrer = Person.objects.get(referrer_id=referrer_id)
            except Person.DoesNotExist:
                pass
            else:
                subscriptions[type]["referrer"] = str(referrer.pk)

                # l'import se fait ici pour éviter les imports circulaires
                from ..tasks import notify_referrer

                transaction.on_commit(
                    partial(
                        notify_referrer.delay,
                        referrer_id=str(referrer.id),
                        referred_id=str(person.id),
                        referral_type=type,
                    )
                )

    # on fusionne les éventuelles metadata
    if data.get("metadata"):
        subscriptions[type].setdefault("metadata", {}).update(data["metadata"])

    if data.get("mandat"):
        subscriptions[type]["mandat"] = data["mandat"]

    with transaction.atomic():
        if data.get("mandat"):
            defaults = {"statut": StatutMandat.INSCRIPTION_VIA_PROFIL}
            if data["mandat"] == "maire":
                defaults["mandat"] = MandatMunicipal.MANDAT_MAIRE
                data["mandat"] = "municipal"
            model = types_elus[data["mandat"]]
            try:
                model.objects.get_or_create(person=person, defaults=defaults)
            except model.MultipleObjectsReturned:
                pass

        person.save()


def subscription_success_redirect_url(type, id, data):
    params = {"agir_id": str(id)}
    url = SUBSCRIPTION_SUCCESS_REDIRECT[type]
    if data.get("next", None):
        url = data.pop("next")
    params.update({f"agir_{k}": v for k, v in data.items()})
    return add_query_params_to_url(url, params, as_fragment=True)


CONTACT_PERSON_UPDATABLE_FIELDS = (
    "contact_phone",
    "location_address1",
    "location_zip",
    "location_city",
    "location_country",
    "newsletters",
)
DATE_2022_LIAISON_META_PROPERTY = "2022_liaison_since"


def save_contact_information(data):
    group = None
    has_group_notifications = data.pop("hasGroupNotifications")

    if "group" in data:
        group = data.pop("group")

    with transaction.atomic():
        try:
            if data.get("email"):
                person = Person.objects.get_by_natural_key(data["email"])
            else:
                # If no email address has been sent, check if the given phone number
                # relates to a unique Person instance (create a new person otherwise)
                person = Person.objects.get(contact_phone=data.get("contact_phone"))
            # If a person exists for this email or phone number, update some of the person's fields
            is_new = False
            person_patch = {
                key: value
                for key, value in data.items()
                if key in CONTACT_PERSON_UPDATABLE_FIELDS and not getattr(person, key)
            }
            if "newsletters" in data and person.newsletters:
                person_patch["newsletters"] = list(
                    set(data["newsletters"] + person.newsletters)
                )
            for key, value in person_patch.items():
                setattr(person, key, value)

            person.save()
        except (Person.DoesNotExist, Person.MultipleObjectsReturned):
            # Create a new person if none exists for the email
            data["meta"] = {
                "subscriptions": {
                    SUBSCRIPTION_TYPE_AP: {
                        "date": timezone.now().isoformat(),
                        "subscriber": str(data.pop("subscriber").id),
                    }
                }
            }
            person = Person.objects.create_person(data.pop("email", ""), **data)
            is_new = True

        if person.is_liaison and not person.meta.get(
            DATE_2022_LIAISON_META_PROPERTY, None
        ):
            person.meta[DATE_2022_LIAISON_META_PROPERTY] = timezone.now().isoformat(
                timespec="seconds"
            )
            person.save()

        from agir.people.tasks import notify_contact

        transaction.on_commit(
            partial(notify_contact.delay, str(person.id), is_new=is_new)
        )

    if group:
        # Create a follower type membership for the person if none exists already and
        # a group id has been sent
        Membership.objects.get_or_create(
            supportgroup=group,
            person=person,
            defaults={
                "membership_type": Membership.MEMBERSHIP_TYPE_FOLLOWER,
                "personal_information_sharing_consent": True,
                "default_subscriptions_enabled": has_group_notifications,
            },
        )

    return person
