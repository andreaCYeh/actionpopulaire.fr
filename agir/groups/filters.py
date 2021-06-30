import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div, Submit
from django import forms
from django.conf import settings
from django.forms import CheckboxInput

from agir.groups.models import SupportGroup
from agir.lib.filters import DistanceFilter


class GroupFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(Div("q", css_class="col-md-8"), Div("type", css_class="col-md-4")),
            "certified",
        )
        self.helper.add_input(Submit("chercher", "Chercher"))


class GroupFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Chercher")

    type = django_filters.ChoiceFilter(
        field_name="type", label="Limiter au type", choices=SupportGroup.TYPE_CHOICES
    )

    distance = DistanceFilter(field_name="coordinates", label="Près de")

    certified = django_filters.BooleanFilter(
        method="filter_certified",
        label="Groupes certifiés uniquement",
        widget=CheckboxInput,
    )

    def filter_search(self, qs, name, terms):
        if terms:
            return qs.search(terms)
        return qs

    def filter_certified(self, qs, name, value):
        if value is True:
            return qs.filter(subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES)
        return qs

    @property
    def qs(self):
        # noinspection PyStatementEffect
        self.errors
        if self.form.cleaned_data.get("q"):
            return super().qs
        return self.queryset.none()

    class Meta:
        model = SupportGroup
        fields = []
        form = GroupFilterForm


class GroupAPIFilterSet(GroupFilterSet, django_filters.rest_framework.FilterSet):
    is_2022 = django_filters.BooleanFilter(
        method="filter_is_2022", label="Groupes d'action 2022 uniquement",
    )
    is_insoumise = django_filters.BooleanFilter(
        method="filter_is_insoumise", label="Groupes LFI uniquement",
    )
    exclude = django_filters.CharFilter(
        method="filter_exclude", label="Sauf l'id de groupe",
    )

    def filter_is_2022(self, qs, name, value):
        if value is True:
            return qs.is_2022()
        return qs

    def filter_is_insoumise(self, qs, name, value):
        if value is True:
            return qs.is_insoumise()
        return qs

    def filter_exclude(self, qs, name, value):
        return qs.exclude(pk__in=[value])
