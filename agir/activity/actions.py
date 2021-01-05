from django.db.models import Prefetch, Q, Subquery, OuterRef
from django.utils import timezone

from .models import Activity, Announcement
from .serializers import ActivitySerializer, AnnouncementSerializer
from ..events.models import Event


def get_activity(person):
    return (
        Activity.objects.unrequired_action()
        .filter(recipient=person)
        .prefetch_related(
            Prefetch("event", Event.objects.with_serializer_prefetch(person),)
        )[:40]
    )


def get_serialized_activity(request):
    if hasattr(request.user, "person"):
        person = request.user.person
        activities = get_activity(person)

        activity_serializer = ActivitySerializer(
            instance=activities, many=True, context={"request": request}
        )
        return activity_serializer.data

    return []


def get_required_action_activity(person):
    required_action_activities = (
        Activity.objects.required_action()
        .filter(recipient=person)
        .prefetch_related(
            Prefetch("event", Event.objects.with_serializer_prefetch(person),)
        )
    )
    # On affiche toutes les activités avec action requise non traitées
    unread_required_action_activities = required_action_activities.exclude(
        status=Activity.STATUS_INTERACTED
    )
    # On affiche les 20 dernières activités avec action requise déjà traitées
    read_required_action_activities = required_action_activities.filter(
        status=Activity.STATUS_INTERACTED
    ).order_by("-created")[:20]

    return required_action_activities.filter(
        pk__in=[a.pk for a in unread_required_action_activities]
        + [a.pk for a in read_required_action_activities]
    ).order_by("-created")


def get_serialized_required_action_activity(request):
    if hasattr(request.user, "person"):
        person = request.user.person
        activities = get_required_action_activity(person)

        activity_serializer = ActivitySerializer(
            instance=activities, many=True, context={"request": request}
        )
        return activity_serializer.data

    return []


def get_announcements(person=None):
    today = timezone.now()
    cond = Q(start_date__lt=today) & (Q(end_date__isnull=True) | Q(end_date__gt=today))

    # Les annonces sont affichés :
    # - avec les plus grandes priorités d'abord
    # - à priorité égale, les plus récentes d'abord
    # - à priorité et date de début égales, celles qui disparaitront les premières d'abord
    announcements = Announcement.objects.filter(cond).order_by(
        "-priority", "-start_date", "end_date"
    )

    if person:
        return [
            a
            for a in announcements.annotate(
                activity_id=Subquery(
                    Activity.objects.filter(
                        recipient_id=person.id, announcement_id=OuterRef("id")
                    ).values("id")[:1]
                )
            ).select_related("segment")
            if a.segment is None
            or a.segment.get_subscribers_queryset().filter(pk=person.id).exists()
        ]
    else:
        return announcements.filter(segment__isnull=True)


def get_serialized_announcements(request):
    person = getattr(request.user, "person", None)
    announcements = get_announcements(person)

    serializer = AnnouncementSerializer(
        instance=announcements, many=True, context={"request": request}
    )
    return serializer.data
