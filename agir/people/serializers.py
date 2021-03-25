from django.conf import settings
from django.db import transaction
from django.http import Http404
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from agir.elus.models import MandatMunicipal, StatutMandat, types_elus
from agir.front.serializer_utils import MediaURLField
from agir.lib.data import french_zipcode_to_country_code, FRANCE_COUNTRY_CODES
from agir.lib.serializers import (
    LegacyBaseAPISerializer,
    LegacyLocationMixin,
    RelatedLabelField,
    FlexibleFieldsMixin,
)
from . import models
from .actions.subscription import (
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTION_TYPE_CHOICES,
    subscription_success_redirect_url,
    save_subscription_information,
    SUBSCRIPTION_EMAIL_SENT_REDIRECT,
)
from .models import Person
from .tasks import send_confirmation_email
from ..lib.token_bucket import TokenBucket

person_fields = {f.name: f for f in models.Person._meta.get_fields()}
subscription_mail_bucket = TokenBucket("SubscriptionMail", 5, 600)


class PersonEmailSerializer(serializers.ModelSerializer):
    """Basic PersonEmail serializer used to show and edit PersonEmail"""

    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)
        queryset = models.PersonEmail.objects.all()
        try:
            pk = self.context["view"].kwargs["pk"]
        except KeyError:
            pk = None
        if pk is not None:
            try:
                queryset = queryset.exclude(person__id=pk)
            except ValueError:
                queryset = queryset.exclude(person__nb_id=pk)

        self.fields["address"] = serializers.EmailField(
            max_length=254, validators=[UniqueValidator(queryset=queryset)]
        )

    bounced = serializers.BooleanField()

    class Meta:
        model = models.PersonEmail
        fields = ("address", "bounced", "bounced_date")


class LegacyPersonSerializer(LegacyLocationMixin, LegacyBaseAPISerializer):
    tags = RelatedLabelField(
        many=True, required=False, queryset=models.PersonTag.objects.all()
    )

    email_opt_in = serializers.BooleanField(source="subscribed", required=False)

    email = serializers.EmailField(required=True)

    bounced = serializers.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self, LegacyUnprivilegedPersonSerializer):
            self.fields["emails"] = PersonEmailSerializer(
                required=False, many=True, context=self.context
            )

    def validate_email(self, value):

        try:
            pe = models.PersonEmail.objects.get_by_natural_key(value)
        except models.PersonEmail.DoesNotExist:
            return value

        if pe.person == self.instance:
            return pe.address

        raise serializers.ValidationError("Email already exists", code="unique")

    def update(self, instance, validated_data):
        emails = validated_data.pop("emails", None)
        email = validated_data.pop("email", None)
        with transaction.atomic():
            super().update(instance, validated_data)
            if emails is not None:
                for item in emails:
                    instance.add_email(
                        item["address"],
                        bounced=item.get("bounced", None),
                        bounced_date=item.get("bounced_date", None),
                    )

            if email is not None:
                if emails is None or email not in [item["address"] for item in emails]:
                    instance.add_email(email)
                instance.set_primary_email(email)

        return instance

    class Meta:
        model = models.Person
        fields = (
            "url",
            "_id",
            "id",
            "email",
            "emails",
            "first_name",
            "last_name",
            "bounced",
            "bounced_date",
            "_created",
            "_updated",
            "email_opt_in",
            "tags",
            "location",
        )
        read_only_fields = ("url", "_id", "_created", "_updated")
        extra_kwargs = {"url": {"view_name": "legacy:person-detail"}}


class LegacyUnprivilegedPersonSerializer(LegacyPersonSerializer):
    class Meta:
        model = models.Person
        fields = (
            "url",
            "_id",
            "email",
            "first_name",
            "last_name",
            "email_opt_in",
            "location",
        )
        read_only_fields = ("url", "_id")
        extra_kwargs = {"url": {"view_name": "legacy:person-detail"}}


class PersonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonTag
        fields = ("url", "id", "label", "description")


class SubscriptionRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=SUBSCRIPTION_TYPE_CHOICES, default=SUBSCRIPTION_TYPE_LFI, required=False
    )

    email = serializers.EmailField(required=True,)
    location_zip = serializers.CharField(required=True)
    first_name = serializers.CharField(
        max_length=person_fields["first_name"].max_length, required=False
    )
    last_name = serializers.CharField(
        max_length=person_fields["last_name"].max_length, required=False
    )
    contact_phone = PhoneNumberField(required=False)
    location_country = CountryField(required=False)
    mandat = serializers.ChoiceField(
        choices=("municipal", "maire", "departemental", "regional"), required=False
    )

    referrer = serializers.CharField(required=False)

    PERSON_FIELDS = ["location_zip", "first_name", "last_name", "contact_phone"]

    def validate_email(self, value):
        if not subscription_mail_bucket.has_tokens(value):
            raise serializers.ValidationError(
                "Si vous n'avez pas encore reçu votre email de validation, attendez quelques instants."
            )
        return value

    def validate_contact_phone(self, value):
        return value and str(value)

    def validate(self, data):
        if (
            not data.get("location_country")
            or data.get("location_country") in FRANCE_COUNTRY_CODES
        ):
            data["location_country"] = french_zipcode_to_country_code(
                data["location_zip"]
            )

        return data

    def save(self):
        """Saves the subscription information.

        If there's already a person with that email address in the database, just update that row.

        If not, create and send a message with a confirmation link to that email address.
        """
        email = self.validated_data["email"]
        type = self.validated_data["type"]

        send_confirmation_email.delay(**self.validated_data)

        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            self.result_data = {
                "status": "new",
                "url": SUBSCRIPTION_EMAIL_SENT_REDIRECT[type],
            }
        else:
            save_subscription_information(person, type, self.validated_data)

            self.result_data = {
                "status": "known",
                "id": str(person.id),
                "url": subscription_success_redirect_url(
                    type, person.id, self.validated_data
                ),
            }
            return person


class NewslettersField(serializers.DictField):
    child = serializers.BooleanField()

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        allowed_keys = {key for key, label in Person.NEWSLETTERS_CHOICES}
        wrong_keys = set(value).difference(allowed_keys)
        errors = [f"{key} n'est pas un nom de newsletter" for key in wrong_keys]

        if errors:
            raise ValidationError(errors)

        return value


class ManageNewslettersRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    newsletters = NewslettersField(required=False, default={})

    def validate_id(self, value):
        try:
            self.person = Person.objects.get(pk=value)
        except Person.DoesNotExist:
            raise ValidationError("Cette ID ne correspond pas à une personne connue")

    def save(self):
        for newsletter, target_status in self.validated_data["newsletters"].items():
            if newsletter in self.person.newsletters and not target_status:
                self.person.newsletters.remove(newsletter)
            elif newsletter not in self.person.newsletters and target_status:
                self.person.newsletters.append(newsletter)
        self.person.save()


class RetrievePersonRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        non_empty = sum(1 for k, v in attrs.items() if v)
        if non_empty != 1:
            raise ValidationError("Indiquez soit un email, soit un id")

        return attrs

    def retrieve(self):
        try:
            if "id" in self.validated_data:
                return Person.objects.get(id=self.validated_data["id"])
            return Person.objects.get_by_natural_key(self.validated_data["email"])
        except Person.DoesNotExist:
            raise Http404("Aucune personne trouvée")


class PersonNewsletterListField(serializers.ListField):
    child = serializers.ChoiceField(choices=Person.NEWSLETTERS_CHOICES)


class PersonMandatField(serializers.Field):
    requires_context = True
    types = tuple(types_elus.keys())
    choices = dict([(mandat, mandat) for mandat in types_elus.keys()])
    default_error_messages = {
        "invalid": "Le type de mandat n'est pas valide",
    }

    def get_defaults(self, mandat_type):
        defaults = {"statut": StatutMandat.INSCRIPTION_VIA_PROFIL}
        if mandat_type == "maire":
            defaults["mandat"] = MandatMunicipal.MANDAT_MAIRE
        return defaults

    def get_value(self, dictionary):
        return dictionary

    def get_attribute(self, instance):
        return instance

    def to_representation(self, person):
        return [
            mandat
            for mandat in self.types
            if types_elus[mandat]
            .objects.filter(person=person, **self.get_defaults(mandat))
            .exists()
        ]

    def to_internal_value(self, data):
        if not hasattr(data, "mandat") or not data["mandat"]:
            return None
        mandat_type = data.pop("mandat")
        mandat = None
        if not mandat_type in self.types:
            return self.fail("invalid", data=data)
        try:
            types_elus[mandat_type].objects.get_or_create(
                person=self.context["request"].user.person,
                defaults=self.get_defaults(mandat_type),
            )
        except types_elus[mandat_type].MultipleObjectsReturned:
            pass

        return data


class PersonSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)

    firstName = serializers.CharField(
        label="Prénom",
        max_length=person_fields["first_name"].max_length,
        required=False,
        source="first_name",
    )
    lastName = serializers.CharField(
        label="Nom",
        max_length=person_fields["last_name"].max_length,
        required=False,
        source="last_name",
    )
    displayName = serializers.CharField(
        label="Nom public",
        help_text="Le nom que tout le monde pourra voir. Indiquez par exemple votre prénom ou un pseudonyme.",
        max_length=person_fields["display_name"].max_length,
        required=True,
        source="display_name",
    )
    image = MediaURLField(required=False, label="Image de profil")
    contactPhone = PhoneNumberField(
        source="contact_phone", required=False, label="Numéro de téléphone"
    )

    isInsoumise = serializers.BooleanField(source="is_insoumise", required=False)
    is2022 = serializers.BooleanField(source="is_2022", required=False)

    mandat = PersonMandatField(required=False)

    referrerId = serializers.CharField(source="referrer_id", required=False)

    newsletters = PersonNewsletterListField(required=False, allow_empty=True)

    gender = serializers.CharField(required=False)

    zip = serializers.CharField(
        required=False, source="location_zip", label="Code postal"
    )

    class Meta:
        model = models.Person
        fields = (
            "id",
            "email",
            "firstName",
            "lastName",
            "displayName",
            "image",
            "contactPhone",
            "isInsoumise",
            "is2022",
            "referrerId",
            "newsletters",
            "gender",
            "zip",
            "mandat",
        )
