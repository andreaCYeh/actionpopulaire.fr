from django import forms
from django.core.exceptions import ValidationError

from agir.people.models import Person
from agir.people.person_forms.fields import is_actual_model_field
from agir.people.person_forms.forms import BasePersonForm


def get_people_form_class(
    person_form_instance, additional_model_fields=None, base_form=BasePersonForm
):
    """Returns the form class for the specific person_form_instance

    :param person_form_instance: the person_form model object for which the form class must be generated
    :param base_form: an optional base form to use instead of the default BasePersonForm
    :return: a form class that can be used to generate a form for the person_form_instance
    """
    # the list of 'person_fields' that will also be saved on the person model when saving the form
    form_person_fields = [
        field["id"]
        for fieldset in person_form_instance.custom_fields
        for field in fieldset["fields"]
        if is_actual_model_field(field)
    ]

    if additional_model_fields is not None:
        form_person_fields.extend(additional_model_fields)

    form_class = forms.modelform_factory(
        Person, fields=form_person_fields, form=base_form
    )

    form_class.person_form_instance = person_form_instance

    return form_class


def validate_custom_fields(custom_fields):
    if not isinstance(custom_fields, list):
        raise ValidationError("La valeur doit être une liste")
    for fieldset in custom_fields:
        if not (fieldset.get("title") and isinstance(fieldset["fields"], list)):
            raise ValidationError(
                'Les sections doivent avoir un "title" et une liste "fields"'
            )

        for i, field in enumerate(fieldset["fields"]):
            if field["id"] == "location":
                initial_field = fieldset["fields"].pop(i)
                for location_field in [
                    "location_country",
                    "location_state",
                    "location_city",
                    "location_zip",
                    "location_address2",
                    "location_address1",
                ]:
                    fieldset["fields"].insert(
                        i,
                        {
                            "id": location_field,
                            "person_field": True,
                            "required": False
                            if location_field == "location_address2"
                            else initial_field.get("required", True),
                        },
                    )
                continue
            if is_actual_model_field(field):
                continue
            elif not field.get("label") or not field.get("type"):
                raise ValidationError("Les champs doivent avoir un label et un type")
