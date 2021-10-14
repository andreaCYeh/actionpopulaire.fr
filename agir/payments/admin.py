from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.db.models import Sum
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import escape, format_html, format_html_join
from rangefilter.filter import DateRangeFilter

from agir.checks.models import CheckPayment
from agir.donations.form_fields import MoneyField
from agir.lib.admin import PersonLinkMixin
from agir.lib.utils import front_url
from agir.payments.actions.payments import (
    notify_status_change,
    change_payment_status,
    PaymentException,
)
from agir.payments.actions.subscriptions import terminate_subscription
from agir.payments.models import Subscription, Payment
from agir.payments.payment_modes import PAYMENT_MODES
from . import models
from .types import PAYMENT_TYPES


def notify_status_action(model_admin, request, queryset):
    for p in queryset:
        notify_status_change(p)


notify_status_action.short_description = "Renotifier le statut"


def change_payments_status_action(status, description):
    def action(modeladmin, request, queryset):
        try:
            with transaction.atomic():
                now = timezone.now().astimezone(timezone.utc).isoformat()

                for payment in queryset.filter(status=CheckPayment.STATUS_WAITING):
                    if not PAYMENT_MODES[payment.mode].can_admin:
                        raise PaymentException(
                            "Paiement n°{} ne peut pas être changé manuellement".format(
                                payment.id
                            )
                        )

                    change_payment_status(payment, status)
                    payment.events.append(
                        {
                            "change_status": status,
                            "date": now,
                            "origin": "payment_admin_action",
                        }
                    )
                    payment.save()
                    notify_status_change(payment)
        except PaymentException as exception:
            modeladmin.message_user(request, exception, level=messages.WARNING)

    # have to change the function name so that django admin see that they are different functions
    action.__name__ = f"change_to_{status}"
    action.short_description = description

    return action


class PaymentManagementAdminMixin:
    def status_buttons(self, payment):
        if payment.status not in [
            Payment.STATUS_WAITING,
            Payment.STATUS_REFUSED,
            Payment.STATUS_ABANDONED,
        ]:
            return "-"

        if not PAYMENT_MODES[payment.mode].can_admin:
            return format_html(
                '<a href="{}" target="_blank" class="button">Effectuer le paiement en ligne</a>',
                front_url("payment_retry", args=[payment.pk]),
            )

        statuses = [
            (Payment.STATUS_COMPLETED, "Valider"),
            (Payment.STATUS_CANCELED, "Annuler"),
            (Payment.STATUS_REFUSED, "Refuser"),
        ]

        return format_html_join(
            " ",
            '<button type="submit" class="button" name="_changestatus" value="{}">{}</button>',
            ((status, label) for status, label in statuses),
        )

    status_buttons.short_description = "Actions"

    def change_mode_buttons(self, payment):
        if (
            payment.status == Payment.STATUS_COMPLETED
            or payment.status == Payment.STATUS_CANCELED
        ):
            return payment.get_mode_display()

        if (admin_modes := PAYMENT_TYPES[payment.type].admin_modes) is not None:
            if callable(PAYMENT_TYPES[payment.type].admin_modes):
                admin_modes = admin_modes(payment)

            payment_modes = {k: v for k, v in PAYMENT_MODES.items() if k in admin_modes}
        else:
            payment_modes = PAYMENT_MODES

        return format_html_join(
            " ",
            '<button type="submit" class="button" name="_changemode" {} value="{}">{}</button>',
            (
                ("disabled" if payment.mode == id else "", id, mode.label)
                for id, mode in payment_modes.items()
            ),
        )

    change_mode_buttons.short_description = "Mode de paiement"

    def save_form(self, request, form, change):
        with transaction.atomic():
            if "_changemode" in request.POST:
                if request.POST["_changemode"] not in PAYMENT_MODES:
                    raise SuspiciousOperation()

                mode = request.POST["_changemode"]
                payment = form.instance
                now = timezone.now().astimezone(timezone.utc).isoformat()

                payment.mode = mode
                payment.events.append(
                    {
                        "change_mode": mode,
                        "date": now,
                        "origin": self.opts.app_label + "_admin_change_mode",
                    }
                )

            if "_changestatus" in request.POST:
                if int(request.POST["_changestatus"]) not in [
                    Payment.STATUS_COMPLETED,
                    Payment.STATUS_REFUSED,
                    Payment.STATUS_CANCELED,
                ]:
                    raise SuspiciousOperation()

                status = request.POST["_changestatus"]
                payment = form.instance
                now = timezone.now().astimezone(timezone.utc).isoformat()

                change_payment_status(payment, int(status))
                payment.events.append(
                    {
                        "change_status": status,
                        "date": now,
                        "origin": self.opts.app_label + "_admin_change_button",
                    }
                )
                notify_status_change(payment)

            return super().save_form(request, form, change)

    def response_change(self, request, payment):
        if "_changemode" in request.POST:
            if not PAYMENT_MODES[payment.mode].can_admin:
                return HttpResponseRedirect(payment.get_payment_url())

            self.message_user(
                request, "Le mode de paiement a bien été modifié.", messages.SUCCESS
            )
            return HttpResponseRedirect(request.path)

        if "_changestatus" in request.POST:
            self.message_user(
                request, "Le statut du paiement a bien été modifié.", messages.SUCCESS
            )
            return HttpResponseRedirect(request.path)

        return super().response_change(request, payment)


class PaymentAdminForm(forms.ModelForm):
    price = MoneyField(
        label="Modifier le prix avant le paiement",
        help_text="La modification arbitraire du montant sera enregistrée si vous validez le paiement.",
    )


class PaymentChangeList(ChangeList):
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)
        self.sum = self.queryset.aggregate(sum=Sum("price"))["sum"] or 0


@admin.register(models.Payment)
class PaymentAdmin(PaymentManagementAdminMixin, admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = (
        "id",
        "get_type_display",
        "person",
        "email",
        "first_name",
        "last_name",
        "get_price_display",
        "status",
        "created",
        "get_mode_display",
    )
    readonly_fields = (
        "get_type_display",
        "person",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "location_address1",
        "location_address2",
        "location_zip",
        "location_city",
        "location_country",
        "meta",
        "events",
        "status",
        "change_mode_buttons",
        "get_price_display",
    )
    fields = readonly_fields

    def get_changelist(self, request, **kwargs):
        return PaymentChangeList

    def get_fields(self, request, payment=None):
        if payment is not None and payment.status in [
            Payment.STATUS_WAITING,
            Payment.STATUS_ABANDONED,
            Payment.STATUS_REFUSED,
        ]:
            fields = list(super().get_fields(request, payment))
            fields.insert(-2, "price")
            fields[-1] = "status_buttons"
            return fields
        return super().get_fields(request, payment)

    def get_readonly_fields(self, request, payment=None):
        if payment is not None and payment.status in [
            Payment.STATUS_WAITING,
            Payment.STATUS_ABANDONED,
            Payment.STATUS_REFUSED,
        ]:
            return super().get_readonly_fields(request, payment) + ("status_buttons",)
        return super().get_readonly_fields(request, payment)

    list_filter = ("status", "type", "mode", ("created", DateRangeFilter))
    search_fields = ("email", "first_name", "last_name", "=id")

    actions = [
        notify_status_action,
        change_payments_status_action(Payment.STATUS_COMPLETED, "Marquer comme reçu"),
        change_payments_status_action(Payment.STATUS_CANCELED, "Marqué comme annulé"),
    ]

    def save_form(self, request, form, change):
        with transaction.atomic():
            payment = form.instance
            if (
                change
                and "price" in form.changed_data
                and payment.price != form["price"].initial
            ):
                now = timezone.now().astimezone(timezone.utc).isoformat()
                payment.events.append(
                    {
                        "new_price": payment.price,
                        "old_price": form["price"].initial,
                        "date": now,
                        "origin": self.opts.app_label + "_admin_change_price",
                    }
                )
                self.message_user(
                    request, "Le montant a bien été modifié.", messages.SUCCESS
                )

            return super().save_form(request, form, change)

    def has_add_permission(self, request):
        return False


@admin.register(models.Subscription)
class SubscriptionAdmin(PersonLinkMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "person_link",
        "get_price_display",
        "type",
        "status",
        "created",
        "mode",
        "day_of_month",
    )
    readonly_fields = (
        "mode",
        "type",
        "person_link",
        "get_price_display",
        "status",
        "terminate_button",
    )
    fields = readonly_fields
    list_filter = ("status", "mode", ("created", DateRangeFilter))
    search_fields = ("person__search", "=id")

    def get_changelist(self, request, **kwargs):
        return PaymentChangeList

    def get_urls(self):
        return [
            path(
                "<int:subscription_pk>/terminate/",
                self.admin_site.admin_view(self.terminate_view),
                name="payments_subscription_terminate",
            )
        ] + super().get_urls()

    def terminate_button(self, subscription):
        if subscription._state.adding:
            return "-"
        else:
            return format_html(
                '<a href="{}" class="button">Désactiver l\'abonnement</a>',
                reverse(
                    "admin:payments_subscription_terminate", args=(subscription.pk,)
                ),
            )

    def terminate_view(self, request, subscription_pk):
        try:
            subscription = Subscription.objects.get(
                pk=subscription_pk, status=Subscription.STATUS_ACTIVE
            )
        except Subscription.DoesNotExist:
            raise Http404()

        if request.method == "POST":
            terminate_subscription(subscription)

            return redirect("admin:payments_subscription_change", subscription_pk)

        context = {
            "title": "Désactiver le paiment récurent: %s" % escape(subscription_pk),
            "is_popup": True,
            "opts": self.model._meta,
            "subscription": subscription,
            "change": True,
            "add": False,
            "save_as": False,
            "show_save": True,
            "has_delete_permission": self.has_delete_permission(request, subscription),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request, subscription),
            "has_view_permission": self.has_view_permission(request, subscription),
            "has_editable_inline_admin_formsets": False,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request, "admin/subscriptions/terminate_subscription.html", context
        )
