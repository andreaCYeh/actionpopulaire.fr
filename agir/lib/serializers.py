from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions, validators
from rest_framework.fields import empty
from django_countries.serializer_fields import CountryField
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import BaseSerializer
from rest_framework_gis.fields import GeometryField


class NullAsBlankMixin:
    """Field mixin that makes a null input be interpreted as the empty string instead.

    This field is used to accept null values for char fields and still follow
    Django convention of not using NULL values for text fields and to use the empty
    string for "no data".

    See: https://docs.djangoproject.com/en/1.11/ref/models/fields/#null

    """

    def get_value(self, dictionary):
        value = super(NullAsBlankMixin, self).get_value(dictionary)
        if value is None:
            return ""
        return value


class NullableCharField(NullAsBlankMixin, serializers.CharField):
    """CharField that interprets a `null` input as the empty string."""

    def __init__(self, **kwargs):
        kwargs.setdefault("allow_blank", True)
        super(NullableCharField, self).__init__(**kwargs)


class NullableCountryField(NullAsBlankMixin, CountryField):
    """CharField that interprets a `null` input as the empty string."""

    pass


class LocationSerializer(serializers.Serializer):
    name = serializers.CharField(source="location_name")
    address1 = serializers.CharField(source="location_address1")
    address2 = serializers.CharField(
        source="location_address2", required=False, allow_blank=True
    )
    zip = serializers.CharField(source="location_zip")
    city = serializers.CharField(source="location_city")
    country = CountryField(source="location_country")

    address = serializers.SerializerMethodField()

    shortAddress = serializers.CharField(source="short_address", required=False)

    shortLocation = serializers.CharField(source="short_location", required=False)

    coordinates = GeometryField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if not ["name"] and not data["zip"] and not data["city"]:
            return None
        return data

    def get_address(self, obj):
        parts = [
            obj.location_address1,
            obj.location_address2,
            f"{obj.location_zip} {obj.location_city}".strip(),
        ]

        if obj.location_country and obj.location_country != "FR":
            parts.append(obj.location_country.name)

        return "\n".join(p for p in parts if p)


class LegacyBaseAPISerializer(serializers.ModelSerializer):
    """
    A legacy serializer that handles id fields (both internal and nationbuilder) and creation/modification time fields
    """

    _id = serializers.UUIDField(
        label=_("UUID"),
        source="id",
        read_only=True,
        help_text=_("UUID interne à l'API pour identifier la ressource"),
    )

    id = serializers.IntegerField(
        label=_("ID sur NationBuilder"),
        source="nb_id",
        required=False,
        allow_null=True,
        help_text=_(
            "L'identifiant de la ressource correspondante sur NationBuilder, si importé."
        ),
    )

    _created = serializers.DateTimeField(
        label=_("Créé le"),
        source="created",
        read_only=True,
        help_text=_("Date de création de la ressource"),
    )

    _updated = serializers.DateTimeField(
        label=_("Mise à jour le"),
        source="modified",
        read_only=True,
        help_text=_("Date de mise à jour de la ressource"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "id" in self.fields:
            self.fields["id"].validators.append(
                validators.UniqueValidator(queryset=self.Meta.model.objects.all())
            )


class RelatedLabelField(serializers.SlugRelatedField):
    """A related field that shows a slug and can be used to create a new related model object"""

    def __init__(self, slug_field=None, **kwargs):
        if slug_field is None:
            slug_field = "label"

        super().__init__(slug_field, **kwargs)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail("invalid")


class ExistingRelatedLabelField(RelatedLabelField):
    def __init__(self, slug_field=None, **kwargs):
        super().__init__(slug_field, **kwargs)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except (TypeError, ValueError, ObjectDoesNotExist):
            self.fail("invalid")


class PhoneField(serializers.CharField):
    def get_attribute(self, instance):
        if instance.contact_hide_phone:
            return None
        return super().get_attribute(instance)


class NestedContactSerializer(serializers.Serializer):
    """A nested serializer for the fields defined by :py:class:`lib.models.ContactMixin`
    """

    name = serializers.CharField(
        label="Nom du contact",
        required=True,
        allow_blank=True,
        max_length=255,
        source="contact_name",
    )

    email = serializers.EmailField(
        label="Adresse email du contact",
        required=True,
        allow_blank=True,
        source="contact_email",
    )

    phone = PhoneField(
        label="Numéro de téléphone du contact",
        required=True,
        allow_blank=True,
        max_length=30,
        source="contact_phone",
    )

    hidePhone = serializers.BooleanField(
        label="Ne pas rendre le numéro de téléphone public",
        required=False,
        default=False,
        source="contact_hide_phone",
        write_only=True,
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class NestedLocationSerializer(serializers.Serializer):
    """A nested serializer for the fields defined by :py:class:`lib.models.LocationMixin`

    All these fields will be collected and serialized as a a JSON object.
    """

    name = NullableCharField(
        label="nom du lieu", max_length=255, required=True, source="location_name",
    )
    address = NullableCharField(
        label="adresse complète",
        max_length=255,
        required=False,
        source="location_address",
    )
    address1 = NullableCharField(
        label="adresse (1ère ligne)",
        max_length=100,
        required=True,
        source="location_address1",
    )
    address2 = NullableCharField(
        label="adresse (2ème ligne)",
        max_length=100,
        required=False,
        source="location_address2",
    )
    city = NullableCharField(
        label="ville", max_length=100, required=True, source="location_city"
    )
    zip = NullableCharField(
        label="code postal", max_length=20, required=True, source="location_zip"
    )
    state = NullableCharField(
        label="état", max_length=40, required=False, source="location_state"
    )
    country = NullableCountryField(
        label="pays", required=True, source="location_country"
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class LegacyLocationMixin(serializers.ModelSerializer):
    location = NestedLocationSerializer(label=_("Lieu"), required=False)

    @staticmethod
    def _flatten_location(validated_data):
        if "location" in validated_data:
            field_content = validated_data.pop("location")

            for key, value in field_content.items():
                validated_data[key] = value

        return validated_data

    def create(self, validated_data):
        return super(LegacyLocationMixin, self).create(
            self._flatten_location(validated_data)
        )

    def update(self, instance, validated_data):
        return super(LegacyLocationMixin, self).update(
            instance, self._flatten_location(validated_data)
        )


class LegacyContactMixin(serializers.ModelSerializer):
    contact = NestedContactSerializer(
        label=_("Informations du contact"), required=False
    )

    @staticmethod
    def _flatten_contact(validated_data):
        if "contact" in validated_data:
            field_content = validated_data.pop("contact")

            for key, value in field_content.items():
                validated_data[key] = value

        return validated_data

    def create(self, validated_data):
        return super(LegacyContactMixin, self).create(
            self._flatten_contact(validated_data)
        )

    def update(self, instance, validated_data):
        return super(LegacyContactMixin, self).update(
            instance, self._flatten_contact(validated_data)
        )


class LegacyLocationAndContactMixin(LegacyLocationMixin, LegacyContactMixin):
    pass


class UpdatableListSerializer(serializers.ListSerializer):
    matching_attr = None

    def get_additional_fields(self):
        return {}

    def update(self, instances, validated_data):
        instance_mapping = {
            getattr(instance, self.matching_attr): instance for instance in instances
        }
        try:
            data_mapping = {item[self.matching_attr]: item for item in validated_data}
        except KeyError:
            raise exceptions.ValidationError(
                _("Données invalides en entrée"), code="invalid_data"
            )

        ret = []

        additional_fields = self.get_additional_fields()

        for matching_value, data in data_mapping.items():
            instance = instance_mapping.get(matching_value, None)

            # add additional field to data before saving it
            data.update(additional_fields)

            if instance is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(instance, data))

        for matching_value, instance in instance_mapping.items():
            if matching_value not in data_mapping:
                instance.delete()

        return ret


class ContactMixinSerializer(serializers.Serializer):
    name = serializers.CharField(source="contact_name")
    email = serializers.CharField(source="contact_email")
    phone = serializers.SerializerMethodField(source="contact_phone")

    def get_phone(self, obj):
        if obj.contact_hide_phone:
            return None
        return obj.contact_phone

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if all(not v for v in data.values()):
            return None
        return data


class FlexibleFieldsMixin(BaseSerializer):
    def __init__(self, instance=None, data=empty, fields=None, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

        if fields is not None:
            for f in set(self.fields).difference(fields):
                del self.fields[f]


class CurrentPersonDefault:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current user's person.
    """

    requires_context = True

    def __call__(self, serializer_field):
        user = serializer_field.context["request"].user
        if user is None or user.is_anonymous or not user.person:
            return None

        return user.person
