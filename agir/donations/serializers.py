import json

from rest_framework import serializers

from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.groups.models import SupportGroup
from agir.lib.utils import front_url_lazy
from agir.lib.serializers import PhoneField

MAX_AMOUNT_LFI = 750000
MAX_AMOUNT_2022 = 460000

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
    amount = serializers.IntegerField(min_value=1, required=True)
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
        if attrs["to"] == TO_2022 and attrs["amount"] > MAX_AMOUNT_2022:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Les dons versés par une personne physique ne peuvent excéder {int(MAX_AMOUNT_LFI / 100)} € par an pour un  ou des partis ou groupements politiques "
                }
            )

        if attrs["to"] == TO_LFI and attrs["amount"] > MAX_AMOUNT_LFI:
            raise serializers.ValidationError(
                detail={
                    "amount": f"Le maximum du montant total de donation pour une personne aux candidats à l'élection présidentielle ne peut pas excéder {int(MAX_AMOUNT_2022 / 100)} €"
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


class SendDonationSerializer(serializers.Serializer):

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    location_address1 = serializers.CharField(max_length=100)
    location_city = serializers.CharField(max_length=100)
    location_zip = serializers.CharField(max_length=20)
    location_country = serializers.CharField(max_length=100)

    contact_phone = PhoneField(max_length=30, required=True)
    nationality = serializers.CharField(max_length=100)

    subscribed_lfi = serializers.BooleanField(required=False)

    payment_mode = serializers.CharField(max_length=20)

    amount = serializers.IntegerField(min_value=1, required=True)
    to = serializers.ChoiceField(
        choices=((TO_LFI, "la France insoumise"), (TO_2022, "Mélenchon 2022")),
        default=TO_LFI,
    )
    type = serializers.ChoiceField(
        choices=((TYPE_SINGLE_TIME, "une seule fois"), (TYPE_MONTHLY, "tous les mois")),
        required=True,
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )
