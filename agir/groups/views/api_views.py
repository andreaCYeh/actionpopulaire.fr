import reversion
from django.contrib.gis.db.models.functions import Distance
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import F, Max, DateTimeField, Q
from django.db.models.functions import Greatest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, exceptions
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.donations.allocations import get_balance
from agir.donations.models import SpendingRequest
from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.groups.actions.notifications import (
    new_message_notifications,
    new_comment_notifications,
    someone_joined_notification,
)
from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import (
    SupportGroup,
    SupportGroupSubtype,
    Membership,
    SupportGroupExternalLink,
)
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
    SupportGroupSerializer,
    SupportGroupDetailSerializer,
    SupportGroupUpdateSerializer,
    MembershipSerializer,
    SupportGroupExternalLinkSerializer,
    MemberPersonalInformationSerializer,
)
from agir.lib.pagination import APIPaginator
from agir.lib.utils import front_url
from agir.msgs.actions import update_recipient_message
from agir.people.models import Person

__all__ = [
    "LegacyGroupSearchAPIView",
    "GroupSearchAPIView",
    "GroupSubtypesView",
    "UserGroupsView",
    "GroupDetailAPIView",
    "NearGroupsAPIView",
    "GroupEventsAPIView",
    "GroupPastEventsAPIView",
    "GroupUpcomingEventsAPIView",
    "GroupPastEventReportsAPIView",
    "GroupMessagesAPIView",
    "GroupMessageNotificationStatusAPIView",
    "GroupMessagesPrivateAPIView",
    "GroupSingleMessageAPIView",
    "GroupMessageCommentsAPIView",
    "GroupSingleCommentAPIView",
    "GroupMessageParticipantsAPIView",
    "JoinGroupAPIView",
    "FollowGroupAPIView",
    "QuitGroupAPIView",
    "GroupMembersAPIView",
    "GroupUpdateAPIView",
    "GroupInvitationAPIView",
    "MemberPersonalInformationAPIView",
    "GroupMemberUpdateAPIView",
    "GroupFinanceAPIView",
    "CreateSupportGroupExternalLinkAPIView",
    "RetrieveUpdateDestroySupportGroupExternalLinkAPIView",
    "GroupUpdateOwnMembershipAPIView",
]

from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    IsPersonPermission,
)
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment

from agir.msgs.serializers import (
    SupportGroupMessageSerializer,
    MessageCommentSerializer,
)

from agir.groups.tasks import invite_to_group


class LegacyGroupSearchAPIView(ListAPIView):
    "Vieille API encore utilisée par le composant js groupSelector du formulaire de dons"

    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupLegacySerializer
    pagination_class = APIPaginator
    permission_classes = (IsAuthenticated,)


class GroupSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupDetailSerializer
    pagination_class = APIPaginator
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=[
                "id",
                "name",
                "type",
                "location",
                "commune",
            ],
            **kwargs,
        )


class GroupSubtypesView(ListAPIView):
    serializer_class = SupportGroupSubtypeSerializer
    queryset = SupportGroupSubtype.objects.filter(
        visibility=SupportGroupSubtype.VISIBILITY_ALL
    )


class UserGroupsView(ListAPIView):
    serializer_class = SupportGroupSerializer
    permission_classes = (IsAuthenticated,)
    queryset = SupportGroup.objects.active()

    def get(self, request, *args, **kwargs):
        person = request.user.person
        person_groups = (
            self.get_queryset()
            .filter(memberships__person=self.request.user.person)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )
        person_groups = self.get_serializer(person_groups, many=True)
        group_suggestions = []

        if person.coordinates is not None:
            group_suggestions = (
                self.get_queryset()
                .exclude(memberships__person=self.request.user.person)
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[:3]
            )

            for group in group_suggestions:
                group.membership = None

        group_suggestions = self.get_serializer(group_suggestions, many=True)

        return Response(
            {"groups": person_groups.data, "suggestions": group_suggestions.data}
        )


class GroupDetailPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["groups.view_supportgroup"],
    }


class GroupDetailAPIView(RetrieveAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()


class NearGroupsAPIView(ListAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )
        self.check_object_permissions(request, self.supportgroup)
        super().initial(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=["id", "name", "iconConfiguration", "location", "routes"],
            **kwargs,
        )

    def get_queryset(self):
        if self.supportgroup.coordinates is None:
            return SupportGroup.objects.none()

        groups = (
            (
                SupportGroup.objects.active()
                .exclude(pk=self.supportgroup.pk)
                .exclude(coordinates__isnull=True)
            )
            .annotate(distance=Distance("coordinates", self.supportgroup.coordinates))
            .order_by("distance")
        )

        return groups[:3]


class GroupEventsAPIView(ListAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = EventListSerializer
    queryset = Event.objects.listed()

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )
        self.check_object_permissions(request, self.supportgroup)
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .distinct()
            .order_by("-start_time")
            .select_related("subtype")
        )
        return events

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class GroupUpcomingEventsAPIView(ListAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = EventListSerializer
    queryset = Event.objects.listed().upcoming()

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )
        self.check_object_permissions(request, self.supportgroup)
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .upcoming()
            .distinct()
            .order_by("start_time")
            .select_related("subtype")
        )
        return events

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class GroupPastEventsAPIView(ListAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = EventListSerializer
    queryset = Event.objects.listed().past()
    pagination_class = APIPaginator

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )

        self.check_object_permissions(request, self.supportgroup)

        super().initial(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .distinct()
            .order_by("-start_time")
            .select_related("subtype")
        )
        return events


class GroupPastEventReportsAPIView(ListAPIView):
    permission_classes = (GroupDetailPermissions,)
    serializer_class = EventListSerializer
    queryset = Event.objects.listed().past()

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )

        self.check_object_permissions(request, self.supportgroup)

        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .exclude(report_content="")
            .distinct()
            .order_by("-start_time")
            .select_related("subtype")
        )
        return events

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class GroupMessagesPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": [], "PATCH": [], "PUT": [], "DELETE": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessage"],
        "PATCH": ["msgs.change_supportgroupmessage"],
        "PUT": ["msgs.change_supportgroupmessage"],
        "DELETE": ["msgs.delete_supportgroupmessage"],
    }


class GroupMessagesNotificationPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "PUT": ["msgs.view_supportgroupmessage"],
    }


class GroupMessagesAPIView(ListCreateAPIView):
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessagesPermissions,
    )
    pagination_class = APIPaginator
    membershipType = Membership.MEMBERSHIP_TYPE_FOLLOWER

    def initial(self, request, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=kwargs["pk"])
        except SupportGroup.DoesNotExist:
            raise NotFound()

        super().initial(request, *args, **kwargs)
        self.check_object_permissions(request, self.supportgroup)

    def get_queryset(self):
        person = self.request.user.person
        memberships = self.supportgroup.memberships.filter(person=person)
        user_permission = 0
        if memberships.exists():
            user_permission = memberships.first().membership_type

        # Messages where user is author or allowed
        return (
            self.supportgroup.messages.filter(
                Q(deleted=False)
                & (Q(required_membership_type__lte=user_permission) | Q(author=person))
            )
            .select_related("author", "linked_event", "linked_event__subtype")
            .prefetch_related("comments")
            .order_by("-created")
        )

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.LIST_FIELDS, **kwargs
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            message = serializer.save(
                author=self.request.user.person,
                supportgroup=self.supportgroup,
                required_membership_type=self.membershipType,
            )

            new_message_notifications(message)
            update_recipient_message(message, self.request.user.person)


# Allow anyone to send private message
class GroupMessagesPrivateAPIView(GroupMessagesAPIView):
    permission_classes = (IsAuthenticated,)
    membershipType = Membership.MEMBERSHIP_TYPE_REFERENT

    def get(self):
        pass


# Get or set muted notification in recipient_mutedlist
class GroupMessageNotificationStatusAPIView(RetrieveUpdateAPIView):
    permission_classes = (GroupMessagesNotificationPermissions,)
    queryset = SupportGroupMessage.objects.all()

    def get(self, request, *args, **kwargs):
        message = self.get_object()
        person = self.request.user.person
        is_muted = message.recipient_mutedlist.filter(pk=person.pk).exists()
        return Response(is_muted)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        is_muted = request.data.get("isMuted", None)

        if not isinstance(is_muted, bool):
            raise ValidationError({"isMuted": "Ce champ est obligatoire"})

        person = self.request.user.person

        if is_muted:
            message.recipient_mutedlist.add(person)
        elif message.recipient_mutedlist.filter(pk=person.pk).exists():
            message.recipient_mutedlist.remove(person)

        return Response(is_muted)


@method_decorator(never_cache, name="get")
class GroupSingleMessageAPIView(RetrieveUpdateDestroyAPIView):
    queryset = (
        SupportGroupMessage.objects.filter(deleted=False)
        .select_related(
            "supportgroup", "linked_event", "linked_event__subtype", "author"
        )
        .prefetch_related("comments")
        .annotate(
            last_update=Greatest(
                Max("comments__created"), "created", output_field=DateTimeField()
            )
        )
    )
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (GroupMessagesPermissions,)

    def get_object(self):
        message = super().get_object()
        update_recipient_message(message, self.request.user.person)
        return message

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.DETAIL_FIELDS, **kwargs
        )

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class GroupMessageParticipantsAPIView(RetrieveAPIView):
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (GroupMessagesPermissions,)
    queryset = SupportGroupMessage.objects.all()

    def get(self, request, *args, **kwargs):
        """Returns list of active participants and total of persons included in discussion"""
        obj = SupportGroupMessage.objects.get(pk=kwargs["pk"])

        author = obj.author
        comment_authors = list(obj.comments.values_list("author_id", flat=True))
        comment_authors = set([author.id] + comment_authors)

        allowed_memberships = obj.supportgroup.memberships.filter(
            membership_type__gte=obj.required_membership_type
        )
        persons = [membership.person for membership in allowed_memberships]
        if author not in persons:
            persons = [author] + persons

        active_persons = []
        for p in persons:
            if not (p.id in comment_authors or p in obj.supportgroup.referents):
                continue
            image = ""
            if p.image and p.image.thumbnail:
                image = p.image.thumbnail.url
            membershipType = 0
            allowed = allowed_memberships.filter(person=p)
            if allowed.exists():
                membershipType = allowed.first().membership_type

            active_persons += (
                {
                    "id": p.id,
                    "displayName": p.display_name,
                    "membershipType": membershipType,
                    "isAuthor": author.id == p.id,
                    "isInComments": p.id in comment_authors,
                    "image": image,
                    "gender": p.gender,
                },
            )

        return Response(
            {
                "actives": active_persons,
                "commentAuthors": comment_authors,
                "total": len(persons),
            }
        )


class GroupMessageCommentsPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": [], "PATCH": [], "PUT": [], "DELETE": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessagecomment"],
        "PATCH": ["msgs.change_supportgroupmessagecomment"],
        "PUT": ["msgs.change_supportgroupmessagecomment"],
        "DELETE": ["msgs.delete_supportgroupmessagecomment"],
    }


class GroupMessageCommentsAPIView(ListCreateAPIView):
    serializer_class = MessageCommentSerializer
    permission_classes = (GroupMessageCommentsPermissions,)

    def initial(self, request, *args, **kwargs):
        try:
            self.message = SupportGroupMessage.objects.get(pk=kwargs["pk"])
        except SupportGroupMessage.DoesNotExist:
            raise NotFound()

        self.check_object_permissions(request, self.message)

        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return self.message.comments.filter(deleted=False)

    def perform_create(self, serializer):
        with transaction.atomic():
            comment = serializer.save(
                author=self.request.user.person, message=self.message
            )
            new_comment_notifications(comment)
            update_recipient_message(self.message, self.request.user.person)


class GroupSingleCommentAPIView(UpdateAPIView, DestroyAPIView):
    queryset = SupportGroupMessageComment.objects.filter(deleted=False)
    serializer_class = MessageCommentSerializer
    permission_classes = (GroupMessageCommentsPermissions,)

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class JoinGroupAPIView(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SupportGroup.objects.active()
    target_membership_type = Membership.MEMBERSHIP_TYPE_MEMBER

    def check_object_permissions(self, request, obj):
        if obj.is_full:
            raise PermissionDenied(detail={"error_code": "full_group"})

    def create(self, request, *args, **kwargs):
        supportgroup = self.get_object()
        try:
            membership = Membership.objects.get(
                supportgroup=supportgroup,
                person=request.user.person,
            )
            if membership.membership_type == self.target_membership_type:
                return Response(status=status.HTTP_204_NO_CONTENT)
            membership.membership_type = self.target_membership_type
            membership.save()
            return Response(status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            with transaction.atomic():
                membership = Membership.objects.create(
                    supportgroup=supportgroup,
                    person=request.user.person,
                    membership_type=self.target_membership_type,
                )
                someone_joined_notification(
                    membership, membership_count=supportgroup.active_members_count
                )
            return Response(status=status.HTTP_201_CREATED)


class FollowGroupAPIView(JoinGroupAPIView):
    target_membership_type = Membership.MEMBERSHIP_TYPE_FOLLOWER

    def check_object_permissions(self, request, obj):
        pass


class QuitGroupAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SupportGroup.objects.all()

    def destroy(self, request, *args, **kwargs):
        supportgroup = self.get_object()

        membership = get_object_or_404(
            Membership.objects.all(),
            supportgroup=supportgroup,
            person=request.user.person,
        )

        if (
            membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
            and not Membership.objects.filter(
                supportgroup=membership.supportgroup,
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
            )
            .exclude(id=membership.id)
            .exists()
        ):
            raise PermissionDenied(detail={"error_code": "group_last_referent"})

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupMembersViewPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["groups.change_supportgroup"],
    }


class GroupMembersAPIView(ListAPIView):
    permission_classes = (GroupMembersViewPermissions,)
    queryset = SupportGroup.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return (
            Membership.objects.filter(supportgroup_id=self.kwargs.get("pk"))
            .prefetch_related("person")
            .prefetch_related("person__emails")
        )


class GroupUpdatePermission(GlobalOrObjectPermissions):
    perms_map = {"PUT": [], "PATCH": []}
    object_perms_map = {
        "PUT": ["groups.change_supportgroup"],
        "PATCH": ["groups.change_supportgroup"],
    }


class GroupInvitationPermission(GlobalOrObjectPermissions):
    perms_map = {"POST": []}
    object_perms_map = {
        "POST": ["groups.change_supportgroup"],
    }


class GroupUpdateAPIView(UpdateAPIView):
    permission_classes = (GroupUpdatePermission,)
    queryset = SupportGroup.objects.all()
    serializer_class = SupportGroupUpdateSerializer


class GroupInvitationAPIView(GenericAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (GroupInvitationPermission,)

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        user_id = self.request.user.person.id
        email = request.data.get("email", "")
        if not email:
            raise exceptions.ValidationError(
                detail={"email": "L'adresse email ne peut être vide"},
                code="invalid_format",
            )

        try:
            validate_email(email)
        except:
            raise exceptions.ValidationError(
                detail={"email": "L'adresse email n'est pas valide"},
                code="invalid_format",
            )

        try:
            p = Person.objects.get_by_natural_key(email)
            Membership.objects.get(supportgroup=group, person=p)
        except (Person.DoesNotExist, Membership.DoesNotExist):
            pass
        else:
            raise exceptions.ValidationError(
                detail={"email": "Cette personne fait déjà partie de votre groupe !"},
                code="invalid_format",
            )

        invite_to_group.delay(group.pk, email, user_id)
        return Response(status=status.HTTP_201_CREATED)


class MemberPersonalInformationPermission(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["groups.change_membership_type"],
    }


class MemberPersonalInformationAPIView(RetrieveAPIView):
    queryset = Membership.objects.all()
    permission_classes = (MemberPersonalInformationPermission,)
    serializer_class = MemberPersonalInformationSerializer


class GroupMemberUpdatePermission(GlobalOrObjectPermissions):
    perms_map = {
        "PATCH": [],
    }
    object_perms_map = {
        "PATCH": ["groups.change_membership_type"],
    }


class GroupMemberUpdateAPIView(UpdateAPIView):
    queryset = Membership.objects.all()
    permission_classes = (GroupMemberUpdatePermission,)
    serializer_class = MembershipSerializer

    def check_request_data_permissions(self, request, obj):
        # Group manager can only change membership type for members / followers
        user_should_be_at_least_referent = (
            request.data.get("membershipType", 0) >= Membership.MEMBERSHIP_TYPE_MANAGER
            or obj.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        )
        if (
            user_should_be_at_least_referent
            and Membership.objects.get(
                person=request.user.person, supportgroup=obj.supportgroup
            ).membership_type
            < Membership.MEMBERSHIP_TYPE_REFERENT
        ):
            self.permission_denied(
                request,
                message=getattr("groups.change_membership_type", "message", None),
                code=getattr("groups.change_membership_type", "code", None),
            )

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        self.check_request_data_permissions(request, obj)


class GroupFinancePermission(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["groups.view_group_finance"],
    }


class GroupFinanceAPIView(GenericAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (GroupFinancePermission,)
    serializer_class = SupportGroupSerializer

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        donation = get_balance(group)
        spending_requests = [
            {
                "id": spending_request.id,
                "title": spending_request.title,
                "status": spending_request.get_status_display(),
                "date": spending_request.spending_date,
                "link": front_url(
                    "manage_spending_request", kwargs={"pk": spending_request.pk}
                ),
            }
            for spending_request in (
                SpendingRequest.objects.filter(group=group)
                .exclude(status=SpendingRequest.STATUS_PAID)
                .order_by("-spending_date")
                .only("id", "title", "status", "spending_date")
            )
        ]

        return Response(
            status=status.HTTP_200_OK,
            data={"donation": donation, "spendingRequests": spending_requests},
        )


class CreateSupportGroupExternalLinkPermissions(GlobalOrObjectPermissions):
    perms_map = {"POST": []}
    object_perms_map = {
        "POST": ["groups.change_supportgroup"],
    }


class CreateSupportGroupExternalLinkAPIView(CreateAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (CreateSupportGroupExternalLinkPermissions,)
    serializer_class = SupportGroupExternalLinkSerializer

    def create(self, request, *args, **kwargs):
        self.supportgroup = self.get_object()
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(supportgroup=self.supportgroup)


class RetrieveUpdateDestroySupportGroupExternalLinkPermisns(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": [], "PATCH": [], "DELETE": []}
    object_perms_map = {
        "GET": ["groups.view_supportgroup"],
        "PUT": ["groups.change_supportgroup"],
        "PATCH": ["groups.change_supportgroup"],
        "DELETE": ["groups.change_supportgroup"],
    }


class RetrieveUpdateDestroySupportGroupExternalLinkAPIView(
    RetrieveUpdateDestroyAPIView
):
    queryset = SupportGroupExternalLink.objects.all()
    permission_classes = (RetrieveUpdateDestroySupportGroupExternalLinkPermisns,)
    serializer_class = SupportGroupExternalLinkSerializer

    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj.supportgroup)


class GroupUpdateOwnMembershipPermission(GlobalOrObjectPermissions):
    perms_map = {
        "PATCH": [],
    }
    object_perms_map = {
        "PATCH": ["groups.update_own_membership"],
    }


class GroupUpdateOwnMembershipAPIView(UpdateAPIView):
    queryset = Membership.objects.all()
    permission_classes = (GroupUpdateOwnMembershipPermission,)
    serializer_class = MembershipSerializer
    lookup_url_kwarg = "group_pk"
    lookup_field = "supportgroup_id"

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.person is not None:
            return Membership.objects.filter(person=self.request.user.person)
        return Membership.objects.none()
