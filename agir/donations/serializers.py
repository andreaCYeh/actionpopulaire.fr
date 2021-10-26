import json

from django.conf import settings
from rest_framework import serializers

from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url_lazy

TO_LFI = "LFI"
TO_2022 = "2022"

TYPE_SINGLE_TIME = "S"
TYPE_MONTHLY = "M"


class DonationAllocationSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(), required=True,
    )
    amount = serializers.IntegerField(min_value=1, required=True)


class CreateDonationSerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        min_value=settings.DONATION_MINIMUM, required=True
    )
    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
        default=TO_LFI,
    )
    type = serializers.ChoiceField(
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        help_text="En cas de don mensuel, votre carte sera débitée tous les 8 de chaque mois jusqu'à ce que vous"
        " interrompiez le don mensuel, ce que vous pouvez faire à n'importe quel moment.",
        required=True,
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )
    next = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        max_amount = settings.DONATION_MAXIMUM

        if attrs["type"] == TYPE_MONTHLY:
            max_amount = settings.MONTHLY_DONATION_MAXIMUM

        if attrs["amount"] > max_amount and attrs["to"] == TO_2022:
            raise serializers.ValidationError(
                detail={
                    "amount": "Le maximum du montant total de donation pour une personne aux candidats à l'élection "
                    f"présidentielle ne peut pas excéder {int(max_amount / 100)} €"
                }
            )

        if attrs["amount"] > max_amount and attrs["to"] == TO_LFI:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Les dons versés par une personne physique ne peuvent excéder {int(max_amount / 100)} €"
                }
            )

        return attrs

    def get_next(self, data):
        """
        Returns the redirection URL for the next donation step if validation succeeds
        """
        if data["to"] == TO_2022 and data["type"] == TYPE_MONTHLY:
            return front_url_lazy("monthly_donation_2022_information", absolute=True)
        if data["to"] == TO_2022:
            return front_url_lazy("donation_2022_information", absolute=True)
        if data["type"] == TYPE_MONTHLY:
            return front_url_lazy("monthly_donation_information", absolute=True)
        if data["type"] == TYPE_SINGLE_TIME:
            return front_url_lazy("donation_information", absolute=True)

    def create(self, validated_data):
        session = self.context["request"].session
        session[DONATION_SESSION_NAMESPACE] = {**validated_data}
        if "allocations" in validated_data:
            session[DONATION_SESSION_NAMESPACE]["allocations"] = json.dumps(
                [
                    {**allocation, "group": str(allocation["group"].id)}
                    for allocation in validated_data.get("allocations", [])
                ]
            )
        return validated_data
