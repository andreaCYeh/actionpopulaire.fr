from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.lib.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest


class CommuneListFilter(AutocompleteRelatedModelFilter):
    field_name = "commune"
    title = "commune"


class ConsulateListFilter(AutocompleteRelatedModelFilter):
    field_name = "consulate"
    title = "consulat"


class HasVotingProxyRequestsListFilter(admin.SimpleListFilter):
    title = "cette personne a au moins une procuration"
    parameter_name = "voting_proxy_requests"

    def lookups(self, request, model_admin):
        return (
            (1, "Oui"),
            (0, "Non"),
        )

    def queryset(self, request, queryset):
        if isinstance(self.value(), int):
            return queryset.filter(voting_proxy_requests__isnull=self.value() == 1)
        return queryset


class IsAvailableForVotingDateListFilter(admin.SimpleListFilter):
    title = "date de disponibilité"
    parameter_name = "voting_date"

    def lookups(self, request, model_admin):
        return VotingProxy.VOTING_DATE_CHOICES

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(voting_dates__contains=[self.value()])
        return queryset


class VoterModelAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "commune_consulate",
        "created__date",
        "status",
    )
    list_filter = (
        "status",
        CommuneListFilter,
        ConsulateListFilter,
    )
    autocomplete_fields = ("commune", "consulate")
    readonly_fields = ("created",)

    def created__date(self, instance):
        return instance.created.date()

    created__date.short_description = "date de création"

    def commune_consulate(self, instance):
        if instance.commune is not None:
            return instance.commune
        return instance.consulate

    commune_consulate.short_description = "commune / consulat"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("commune", "consulate")

    class Media:
        pass


@admin.register(VotingProxy)
class VotingProxyAdmin(VoterModelAdmin):
    list_display = (
        *VoterModelAdmin.list_display,
        "voting_dates",
        "person_link",
    )
    list_filter = (
        *VoterModelAdmin.list_filter,
        HasVotingProxyRequestsListFilter,
        IsAvailableForVotingDateListFilter,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person")

    def person_link(self, instance):
        if instance.person is None:
            return "-"
        href = reverse("admin:people_person_change", args=(instance.person_id,))
        return mark_safe(format_html(f'<a href="{href}">{instance.person}</a>'))

    person_link.short_description = "personne"


@admin.register(VotingProxyRequest)
class VotingProxyRequestAdmin(VoterModelAdmin):
    list_display = (
        *VoterModelAdmin.list_display,
        "voting_date__date",
        "proxy_link",
    )
    list_filter = (
        *VoterModelAdmin.list_filter,
        "voting_date",
        ("proxy", admin.EmptyFieldListFilter),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("proxy")

    def voting_date__date(self, instance):
        return instance.voting_date.strftime("%d %B %Y")

    voting_date__date.short_description = "date du scrutin"

    def proxy_link(self, instance):
        if instance.proxy is None:
            return "-"
        href = reverse(
            "admin:voting_proxies_votingproxy_change", args=(instance.proxy_id,)
        )
        return mark_safe(format_html(f'<a href="{href}">{instance.proxy}</a>'))

    proxy_link.short_description = "volontaire"
