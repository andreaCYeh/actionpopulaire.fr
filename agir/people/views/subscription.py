import urllib.parse

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.authentication.utils import hard_login
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.lib.http import add_query_params_to_url
from agir.lib.utils import get_client_ip
from agir.people.actions.subscription import (
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTION_TYPE_NSP,
    SUBSCRIPTION_FIELD,
    SUBSCRIPTIONS_EMAILS,
    subscription_success_redirect_url,
    save_subscription_information,
)
from agir.people.forms import (
    AnonymousUnsubscribeForm,
    SimpleSubscriptionForm,
    OverseasSubscriptionForm,
)
from agir.people.models import Person
from agir.people.token_buckets import is_rate_limited_for_subscription
from agir.lib.tasks import geocode_person


class UnsubscribeView(SimpleOpengraphMixin, FormView):
    template_name = "people/unsubscribe.html"
    success_url = reverse_lazy("unsubscribe_success")
    form_class = AnonymousUnsubscribeForm

    meta_title = "Ne plus recevoir de emails"
    meta_description = "Désabonnez-vous des emails de la France insoumise"

    def form_valid(self, form):
        form.unsubscribe()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            email=self.request.user.person.email
            if self.request.user.is_authenticated
            else None,
            **kwargs,
        )


class ConfirmationMailSentView(TemplateView):
    template_name = "people/confirmation_mail_sent.html"


class BaseSubscriptionView(SimpleOpengraphMixin, FormView):
    success_url = reverse_lazy("subscription_mail_sent")
    meta_title = "Rejoignez Action Populaire"
    meta_description = "Rejoignez Action Populaire"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("dashboard"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if is_rate_limited_for_subscription(
            ip=get_client_ip(self.request), email=form.cleaned_data["email"]
        ):
            form.add_error(
                field=None,
                error=ValidationError(
                    "Vous avez fait trop de tentatives en peu de temps. Merci de patienter un peu."
                ),
            )
            return self.form_invalid(form)

        form.send_confirmation_email()
        return super().form_valid(form)


class SimpleSubscriptionView(BaseSubscriptionView):
    template_name = "people/simple_subscription.html"
    form_class = SimpleSubscriptionForm


class OverseasSubscriptionView(BaseSubscriptionView):
    template_name = "people/overseas_subscription.html"
    form_class = OverseasSubscriptionForm


class ConfirmSubscriptionView(View):
    response_class = TemplateResponse
    error_template = "people/confirmation_mail_error.html"
    error_messages = {
        "invalid": _(
            "Il semble que celui-ci est invalide. Avez-vous bien cliqué sur le bouton, ou copié la totalité du lien ?"
        ),
        "expired": _("Il semble que celui-ci est expiré."),
        "already_created": "Votre inscription était déjà confirmée.",
    }
    allowed_fields = [
        "email",
        "location_zip",
        "location_address1",
        "location_address2",
        "location_city",
        "location_country",
        "contact_phone",
        "first_name",
        "last_name",
        "contact_phone",
        "type",
        "referer",
        "referrer",
        "mandat",
    ]
    show_already_created_message = True
    default_type = SUBSCRIPTION_TYPE_LFI

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        if "email" not in params or "token" not in params:
            return self.error_page(message=self.error_messages["invalid"])

        token = params.pop("token")

        if not set(params).issubset(self.allowed_fields):
            return self.error_page(self.error_messages["invalid"])

        if not subscription_confirmation_token_generator.check_token(token, **params):
            return self.error_page(self.error_messages["expired"])

        self.type = params.pop("type", self.default_type)

        self.perform_create(params)
        return self.success_page(params)

    def error_page(self, message):
        return self.render(
            self.error_template,
            {
                "message": message,
                "show_retry": self.default_type == SUBSCRIPTION_TYPE_LFI,
            },
        )

    def perform_create(self, params):
        with transaction.atomic():
            try:
                # double transaction sinon la transaction externe n'est plus utilisable après l'exception
                with transaction.atomic():
                    self.person = Person.objects.create_person(params["email"])
                    already_created = False
            except IntegrityError:
                self.person = Person.objects.get_by_natural_key(params["email"])
                already_created = True

            save_subscription_information(self.person, self.type, params, new=True)

        if already_created and self.show_already_created_message:
            messages.add_message(
                self.request, messages.INFO, self.error_messages["already_created"]
            )
        elif not already_created and "welcome" in SUBSCRIPTIONS_EMAILS[self.type]:
            from ..tasks import send_welcome_mail

            send_welcome_mail.delay(self.person.pk, type=self.type)

        hard_login(self.request, self.person)

        if self.person.coordinates_type is None:
            geocode_person.delay(self.person.pk)

    def render(self, template, context=None, **kwargs):
        if context is None:
            context = {}

        return self.response_class(
            request=self.request, template=[template], context=context, **kwargs
        )

    def success_page(self, params):
        return HttpResponseRedirect(
            subscription_success_redirect_url(self.type, self.person.id, params)
        )
