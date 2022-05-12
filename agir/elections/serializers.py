from data_france.models import (
    Commune,
    CirconscriptionConsulaire,
    CirconscriptionLegislative,
)
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agir.elections.actions import create_or_update_polling_station_officer
from agir.elections.models import PollingStationOfficer


class VotingCommuneOrConsulateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.SerializerMethodField()
    value = serializers.IntegerField(read_only=True, source="id")
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, instance):
        if isinstance(instance, Commune):
            return f"{instance.code_departement} - {instance.nom_complet}"
        if isinstance(instance, CirconscriptionConsulaire):
            return str(instance)

    def get_type(self, instance):
        if isinstance(instance, Commune):
            return "commune"
        if isinstance(instance, CirconscriptionConsulaire):
            return "consulate"


class CreateUpdatePollingStationOfficerSerializer(serializers.ModelSerializer):
    person = serializers.UUIDField(read_only=True, source="person_id")

    firstName = serializers.CharField(
        required=True, source="first_name", label="Prénom"
    )
    lastName = serializers.CharField(
        required=True, source="last_name", label="Nom de famille"
    )
    birthName = serializers.CharField(
        required=False, allow_blank=True, source="birth_name", label="Nom de naissance"
    )
    birthDate = serializers.DateField(
        required=True, source="birth_date", label="Date de naissance"
    )
    birthCity = serializers.CharField(
        required=True, source="birth_city", label="Ville de naissance"
    )
    birthCountry = CountryField(
        required=True, source="birth_country", label="Pays de naissance"
    )

    address1 = serializers.CharField(
        required=True, source="location_address1", label="Adresse"
    )
    address2 = serializers.CharField(
        required=False,
        allow_blank=True,
        source="location_address2",
        label="Complément d'adresse",
    )
    zip = serializers.CharField(
        required=True, source="location_zip", label="Code postal"
    )
    city = serializers.CharField(required=True, source="location_city", label="Ville")
    country = CountryField(required=True, source="location_country", label="Pays")

    votingCirconscriptionLegislative = serializers.SlugRelatedField(
        required=True,
        allow_null=False,
        source="voting_circonscription_legislative",
        label="Circonscription législative",
        queryset=CirconscriptionLegislative.objects.all(),
        slug_field="code",
    )
    votingCommune = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        source="voting_commune",
        label="Commune",
        queryset=Commune.objects.filter(
            type__in=(Commune.TYPE_COMMUNE, Commune.TYPE_ARRONDISSEMENT_PLM),
        ).exclude(code__in=("75056", "69123", "13055")),
    )
    votingConsulate = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        source="voting_consulate",
        label="Circonscription consulaire",
        queryset=CirconscriptionConsulaire.objects.all(),
    )
    pollingStation = serializers.CharField(
        required=True,
        source="polling_station",
        label="bureau de vote",
    )
    voterId = serializers.CharField(
        required=True,
        source="voter_id",
        label="Numéro national d'électeur",
    )

    hasMobility = serializers.BooleanField(
        source="has_mobility", label="Mobilité", default=False
    )
    availableVotingDates = serializers.MultipleChoiceField(
        source="available_voting_dates",
        required=True,
        allow_empty=False,
        choices=[
            (str(date), label)
            for date, label in PollingStationOfficer.VOTING_DATE_CHOICES
        ],
        label="Dates de disponibilité",
    )

    email = serializers.EmailField(
        required=True, source="contact_email", label="Adresse e-mail"
    )
    phone = PhoneNumberField(
        required=True, source="contact_phone", label="Numéro de téléphone"
    )

    updated = serializers.BooleanField(
        default=False,
        read_only=True,
    )

    def validate_required_commune_or_consulate(self, attrs):
        commune = attrs.get("voting_commune", None)
        consulate = attrs.get("voting_consulate", None)

        if commune is None and consulate is None:
            raise ValidationError(
                {
                    "votingCommune": "Au moins une commune ou une circonscription consulaire doit être sélectionnée",
                    "votingConsulate": "Au moins une commune ou une circonscription consulaire doit être sélectionnée",
                },
                code="invalid_missing_commune_and_consulate",
            )

        if commune is not None and consulate is not None:
            raise ValidationError(
                {
                    "votingCommune": "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en "
                    "même temps",
                    "votingConsulate": "Une commune et une circonscription consulaire ne peuvent pas être sélectionnées en "
                    "même temps",
                },
                code="invalid_commune_and_consulate",
            )

    def validate_circonscription_legislative(self, attrs):
        commune = attrs.get("voting_commune", None)
        consulate = attrs.get("voting_consulate", None)
        circo = attrs.get("voting_circonscription_legislative", None)

        if commune is not None and commune.departement_id != circo.departement_id:
            raise ValidationError(
                {
                    "votingCommune": "La commune ne fait pas partie de la circonscription législative indiquée",
                },
                code="commune_and_circonscription_legislative_mismatch",
            )

        if consulate is not None and circo.departement_id is not None:
            raise ValidationError(
                {
                    "votingConsulate": "La circonscription consulaire ne fait pas partie de la circonscription législative indiquée",
                },
                code="consulate_and_circonscription_legislative_mismatch",
            )

    def validate(self, attrs):
        super().validate(attrs)
        self.validate_required_commune_or_consulate(attrs)
        self.validate_circonscription_legislative(attrs)

        return attrs

    def create(self, validated_data):
        return create_or_update_polling_station_officer(validated_data)

    class Meta:
        model = PollingStationOfficer
        fields = (
            "id",
            "person",
            "firstName",
            "lastName",
            "birthName",
            "gender",
            "birthDate",
            "birthCity",
            "birthCountry",
            "address1",
            "address2",
            "zip",
            "city",
            "country",
            "votingCirconscriptionLegislative",
            "votingCommune",
            "votingConsulate",
            "pollingStation",
            "voterId",
            "role",
            "hasMobility",
            "availableVotingDates",
            "email",
            "phone",
            "remarks",
            "updated",
        )
