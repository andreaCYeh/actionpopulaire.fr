from dataclasses import dataclass
from functools import partial

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.elus.models import types_elus, StatutMandat, MandatMunicipal
from agir.lib.http import add_query_params_to_url
from agir.people.models import Person


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)


@dataclass
class SubscriptionMessageInfo:
    code: str
    subject: str
    from_email: str = settings.EMAIL_FROM


SUBSCRIPTION_TYPE_LFI = "LFI"
SUBSCRIPTION_TYPE_NSP = "NSP"
SUBSCRIPTION_TYPE_EXTERNAL = "EXT"
SUBSCRIPTION_TYPE_ADMIN = "ADM"

SUBSCRIPTION_TYPE_CHOICES = (
    (SUBSCRIPTION_TYPE_LFI, "LFI",),
    (SUBSCRIPTION_TYPE_NSP, "NSP",),
    (SUBSCRIPTION_TYPE_EXTERNAL, "Externe"),
)
SUBSCRIPTION_FIELD = {
    SUBSCRIPTION_TYPE_LFI: "is_insoumise",
    SUBSCRIPTION_TYPE_NSP: "is_2022",
}

SUBSCRIPTIONS_EMAILS = {
    SUBSCRIPTION_TYPE_LFI: {
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE",
            subject="Plus qu'un clic pour vous inscrire",
            from_email="La France insoumise <nepasrepondre@lafranceinsoumise.fr>",
        ),
        "already_subscribed": SubscriptionMessageInfo(
            "ALREADY_SUBSCRIBED_LFI_MESSAGE", "Vous êtes déjà inscrits !",
        ),
        "welcome": SubscriptionMessageInfo(
            "WELCOME_LFI_MESSAGE", "Bienvenue sur la plateforme de la France insoumise"
        ),
    },
    SUBSCRIPTION_TYPE_NSP: {
        "confirmation": SubscriptionMessageInfo(
            code="SUBSCRIPTION_CONFIRMATION_NSP_MESSAGE",
            subject="Confirmez votre e-mail pour valider votre signature !",
            from_email="Nous sommes pour <nepasrepondre@noussommespour.fr>",
        )
    },
    SUBSCRIPTION_TYPE_EXTERNAL: {},
}
SUBSCRIPTION_NEWSLETTERS = {
    SUBSCRIPTION_TYPE_LFI: {Person.NEWSLETTER_LFI},
    SUBSCRIPTION_TYPE_NSP: set(),
    SUBSCRIPTION_TYPE_EXTERNAL: set(),
}

SUBSCRIPTION_EMAIL_SENT_REDIRECT = {
    SUBSCRIPTION_TYPE_LFI: f"{settings.MAIN_DOMAIN}/consulter-vos-emails/",
    SUBSCRIPTION_TYPE_NSP: f"{settings.NSP_DOMAIN}/validez-votre-e-mail/",
}

SUBSCRIPTION_SUCCESS_REDIRECT = {
    SUBSCRIPTION_TYPE_LFI: f"{settings.MAIN_DOMAIN}/bienvenue/",
    SUBSCRIPTION_TYPE_NSP: f"{settings.NSP_DOMAIN}/signature-confirmee/",
}


def save_subscription_information(person, type, data, new=False):
    person_fields = set(f.name for f in Person._meta.get_fields())

    # mise à jour des différents champs
    for f in person_fields.intersection(data):
        # Si la personne n'est pas nouvelle on ne remplace que les champs vides
        setattr(person, f, data[f] if new else getattr(person, f) or data[f])

    person.newsletters = list(SUBSCRIPTION_NEWSLETTERS[type].union(person.newsletters))

    if type in SUBSCRIPTION_FIELD and not getattr(person, SUBSCRIPTION_FIELD[type]):
        setattr(person, SUBSCRIPTION_FIELD[type], True)
    subscriptions = person.meta.setdefault("subscriptions", {})
    if type not in subscriptions:
        subscriptions[type] = {"date": timezone.now().isoformat()}
        if referrer_id := data.get("referrer", data.get("referer")):
            try:
                referrer = Person.objects.get(referrer_id=referrer_id)
            except Person.DoesNotExist:
                pass
            else:
                subscriptions[type]["referrer"] = str(referrer.pk)

                # l'import se fait ici pour éviter les imports circulaires
                from ..tasks import notify_referrer

                transaction.on_commit(
                    partial(
                        notify_referrer.delay,
                        referrer_id=str(referrer.id),
                        referred_id=str(person.id),
                        referral_type=type,
                    )
                )

    if data.get("mandat"):
        subscriptions[type]["mandat"] = data["mandat"]

    with transaction.atomic():
        if data.get("mandat"):
            defaults = {"statut": StatutMandat.INSCRIPTION_VIA_PROFIL}
            if data["mandat"] == "maire":
                defaults["mandat"] = MandatMunicipal.MANDAT_MAIRE
                data["mandat"] = "municipal"
            model = types_elus[data["mandat"]]
            try:
                model.objects.get_or_create(person=person, defaults=defaults)
            except model.MultipleObjectsReturned:
                pass

        person.save()


def subscription_success_redirect_url(type, id, data):
    params = {"agir_id": str(id)}
    params.update({f"agir_{k}": v for k, v in data.items()})
    url = SUBSCRIPTION_SUCCESS_REDIRECT[type]
    return add_query_params_to_url(url, params, as_fragment=True)
