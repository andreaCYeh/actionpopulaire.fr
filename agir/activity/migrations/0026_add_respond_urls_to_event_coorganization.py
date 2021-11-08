# Generated by Django 3.1.13 on 2021-11-02 11:22

from django.db import migrations

from agir.lib.utils import front_url


TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
ACCEPT_URL_KEY = "acceptUrl"
REFUSE_URL_KEY = "refuseUrl"


def add_respond_urls_to_event_coorganization_activities(apps, schema_editor):
    Activity = apps.get_model("activity", "Activity")
    Invitation = apps.get_model("events", "Invitation")
    activities = Activity.objects.filter(type=TYPE_GROUP_COORGANIZATION_INVITE).exclude(
        meta__has_keys=[ACCEPT_URL_KEY, REFUSE_URL_KEY]
    )
    for activity in activities:
        invitation = Invitation.objects.filter(
            event=activity.event, group=activity.supportgroup
        ).first()
        if not invitation:
            continue
        activity.meta = {
            **activity.meta,
            ACCEPT_URL_KEY: front_url(
                "accept_event_group_coorganization",
                absolute=False,
                kwargs={"pk": invitation.pk},
            ),
            REFUSE_URL_KEY: front_url(
                "refuse_event_group_coorganization",
                absolute=False,
                kwargs={"pk": invitation.pk},
            ),
        }
        activity.save()


def reverse_add_respond_urls_to_event_coorganization_activities(apps, schema_editor):
    Activity = apps.get_model("activity", "Activity")
    activities = Activity.objects.filter(
        type=TYPE_GROUP_COORGANIZATION_INVITE,
        meta__has_keys=[ACCEPT_URL_KEY, REFUSE_URL_KEY],
    )
    for activity in activities:
        activity.meta = {
            key: value
            for key, value in activity.meta.items()
            if key not in [ACCEPT_URL_KEY, REFUSE_URL_KEY]
        }
        activity.save()


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0025_auto_20210928_1717"),
        ("events", "0012_auto_20211020_1345"),
    ]

    operations = [
        migrations.RunPython(
            add_respond_urls_to_event_coorganization_activities,
            reverse_add_respond_urls_to_event_coorganization_activities,
            atomic=True,
        ),
    ]
