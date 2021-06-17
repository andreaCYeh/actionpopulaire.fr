from django.db import transaction

from agir.activity.models import Activity
from agir.notifications.types import SubscriptionType


@transaction.atomic()
def new_event_suggestion_notification(event, recipient):
    activity_config = {
        "type": SubscriptionType.TYPE_EVENT_SUGGESTION,
        "event": event,
    }
    if event.organizers_groups.count() > 0:
        activity_config["supportgroup"] = event.organizers_groups.first()
    else:
        activity_config["individual"] = event.organizers.first()

    Activity.objects.create(
        **activity_config, recipient=recipient,
    )
