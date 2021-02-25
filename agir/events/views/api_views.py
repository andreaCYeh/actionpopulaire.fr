from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from agir.events.models import Event
from agir.events.serializers import (
    EventSerializer,
    EventCreateOptionsSerializer,
    CreateEventSerializer,
)
from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions

__all__ = [
    "EventDetailAPIView",
    "EventRsvpedAPIView",
    "EventSuggestionsAPIView",
    "EventCreateOptionsAPIView",
    "CreateEventAPIView",
]

from agir.lib.tasks import geocode_person


class EventRsvpedAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=[
                "id",
                "name",
                # "participantCount",
                "illustration",
                "hasSubscriptionForm",
                "startTime",
                "endTime",
                "location",
                "isOrganizer",
                "rsvp",
                "canRSVP",
                "is2022",
                "routes",
                "groups",
                "distance",
                "compteRendu",
            ],
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        person = self.request.user.person
        queryset = Event.objects.public().with_serializer_prefetch(person)
        if person.is_2022_only:
            queryset = queryset.is_2022()

        return (
            queryset.upcoming()
            .filter(Q(attendees=person) | Q(organizers=person))
            .order_by("start_time", "end_time")
        ).distinct()


class EventDetailAPIView(RetrieveAPIView):
    permission_ = ("events.view_event",)
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class EventSuggestionsAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=[
                "id",
                "name",
                # "participantCount",
                "illustration",
                "hasSubscriptionForm",
                "startTime",
                "endTime",
                "location",
                "isOrganizer",
                "rsvp",
                "canRSVP",
                "is2022",
                "routes",
                "groups",
                "distance",
                "compteRendu",
            ],
            **kwargs
        )

    def get_queryset(self):
        person = self.request.user.person
        base_queryset = Event.objects.with_serializer_prefetch(person)

        groups_events = (
            base_queryset.upcoming()
            .filter(organizers_groups__in=person.supportgroups.all())
            .distinct()
        )

        organized_events = (
            base_queryset.past()
            .filter(organizers=person)
            .distinct()
            .order_by("-start_time")[:10]
        )

        past_events = (
            base_queryset.past()
            .filter(
                Q(rsvps__person=person)
                | Q(organizers_groups__in=person.supportgroups.all())
            )
            .distinct()
            .order_by("-start_time")[:10]
        )

        result = groups_events.union(organized_events, past_events)

        if person.coordinates is not None:
            near_events = (
                base_queryset.upcoming()
                .filter(
                    start_time__lt=timezone.now() + timedelta(days=30),
                    do_not_list=False,
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[:10]
            )

            result = (
                base_queryset.filter(
                    pk__in=[e.pk for e in near_events] + [e.pk for e in result]
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("start_time")
                .distinct()
            )
        else:
            result = result.order_by("start_time")

        return result


class EventCreateOptionsAPIView(RetrieveAPIView):
    permission_ = ("events.add_event",)
    serializer_class = EventCreateOptionsSerializer
    queryset = Event.objects.all()

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous or not user.person:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.person = user.person
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request


class CreateEventAPIView(CreateAPIView):
    permission_ = ("events.add_event",)
    serializer_class = CreateEventSerializer
    queryset = Event.objects.all()
