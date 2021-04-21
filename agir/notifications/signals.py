from django.db.models.signals import post_save
from django.dispatch import receiver

from push_notifications.models import APNSDevice, WebPushDevice

from agir.activity.models import Activity
from agir.groups.models import Membership
from agir.notifications.actions import (
    create_default_person_subscriptions,
    create_default_group_membership_subscriptions,
)
from agir.notifications.models import Subscription
from agir.notifications.tasks import send_webpush_activity, send_apns_activity


@receiver(post_save, sender=Activity, dispatch_uid="push_new_activity")
def push_new_activity(sender, instance, created=False, **kwargs):
    if (
        instance is None
        or not created
        or not Subscription.objects.filter(
            person=instance.recipient,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=instance.type,
        ).exists()
    ):
        return

    # SEND WEBPUSH NOTIFICATIONS
    webpush_device_pks = [
        webpush_device.pk
        for webpush_device in WebPushDevice.objects.filter(
            user=instance.recipient.role, active=True
        )
    ]

    for webpush_device_pk in webpush_device_pks:
        send_webpush_activity.delay(instance.pk, webpush_device_pk)

    # SEND APPLE PUSH NOTIFICATION SERVICE NOTIFICATIONS
    apns_device_pks = [
        apns_device.pk
        for apns_device in APNSDevice.objects.filter(
            user=instance.recipient.role, active=True
        )
    ]

    for apns_device_pk in apns_device_pks:
        send_apns_activity.delay(instance.pk, apns_device_pk)


@receiver(
    post_save,
    sender=WebPushDevice,
    dispatch_uid="create_default_person_subscriptions__wp",
)
@receiver(
    post_save,
    sender=APNSDevice,
    dispatch_uid="create_default_person_subscriptions__apns",
)
def push_device_post_save_handler(sender, instance, created=False, **kwargs):
    is_first_device = (
        instance is not None
        and created is True
        and not Subscription.objects.filter(person=instance.user.person).exists()
        and APNSDevice.objects.filter(user=instance.user).count()
        + WebPushDevice.objects.filter(user=instance.user).count()
        == 1
    )

    if is_first_device:
        create_default_person_subscriptions(instance.user.person)


@receiver(
    post_save, sender=Membership, dispatch_uid="create_default_membership_subscriptions"
)
def membership_post_save_handler(sender, instance, created=False, **kwargs):
    if (
        instance is None
        or not created
        or Subscription.objects.filter(
            person=instance.person, membership=instance
        ).exists()
    ):
        return

    create_default_group_membership_subscriptions(instance.person, instance)
