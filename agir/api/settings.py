"""
Django settings for src project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import json
import os
import re
import warnings
from pathlib import Path

import dj_database_url
import dj_email_url
import sentry_sdk
from django.contrib import messages
from django.contrib.messages import ERROR
from django.core.exceptions import ImproperlyConfigured
from django.utils.datetime_safe import datetime
from django.utils.timezone import make_aware
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

ADMIN_RE = re.compile("^([\w -]+) <([^>]+)>$")
YES_VALUES = ["y", "yes", "true", "t"]


# SECURITY WARNING: don't run with debug turned on in production!
ADMIN_PRODUCTION = os.environ.get("ADMIN_PRODUCTION", "false").lower() == "true"
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
ENABLE_DEBUG_TOOLBAR = os.environ.get("ENABLE_DEBUG_TOOLBAR", "false").lower() == "true"
ENABLE_SILK = os.environ.get("ENABLE_SILK", "false").lower() == "true"

# Risque de sécurité important ! Principalement utilisé pour le load testing
TRUST_X_FORWARDED_FOR = (
    os.environ.get("TRUST_X_FORWARDED_FOR", "false").lower() == "true"
)

# Rendre certains warnings silencieux
SILENCED_SYSTEM_CHECKS = [
    # On a remplacé django.contrib.auth.context_processors.auth par un équivalent, agir.authentication.context_processors.auth
    "admin.E402",
    # social_django utilise encore des champs postgres JSON (au lieu du nouveau JSONField de Django)
    "fields.W904",
]

# Django < 3.1 not compatible with GDAL 3
if os.environ.get("GDAL_LIBRARY_PATH"):
    GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH")

ENABLE_API = os.environ.get("ENABLE_API", "n").lower() in YES_VALUES or DEBUG
ENABLE_ADMIN = os.environ.get("ENABLE_ADMIN", "n").lower() in YES_VALUES or DEBUG
ENABLE_FRONT = os.environ.get("ENABLE_FRONT", "n").lower() in YES_VALUES or DEBUG

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_RUNNER = "agir.api.test_runner.TestRunner"

admins = os.environ.get("ADMINS")
if admins:
    admins = [ADMIN_RE.match(s.strip()) for s in admins.split(";")]
    if any(m is None for m in admins):
        raise ImproperlyConfigured(
            "ADMINS should be of the form 'Name 1 <address1@domain.fr>; Name 2 <address2@domain.fr>"
        )

    ADMINS = [m.groups() for m in admins]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET", "1d5a5&y9(220)phk0o9cqjwdpm$3+**d&+kru(2y)!5h-_qn4b"
)
SENDGRID_SES_WEBHOOK_USER = os.environ.get("SENDGRID_SES_WEBHOOK_USER", "fi")
SENDGRID_SES_WEBHOOK_PASSWORD = os.environ.get("SENDGRID_SES_WEBHOOK_PASSWORD", "prout")
SCANNER_API = os.environ.get("SCANNER_API", "http://agir.local:8000")
SCANNER_API_KEY = os.environ.get("SCANNER_API_KEY", "prout")
SCANNER_API_SECRET = os.environ.get("SCANNER_API_SECRET", "prout")

# these domain names are used when absolute URLs should be generated (e.g. to include in emails)
MAIN_DOMAIN = os.environ.get("MAIN_DOMAIN", "https://lafranceinsoumise.fr")
API_DOMAIN = os.environ.get(
    "API_DOMAIN",
    "http://agir.local:8000" if DEBUG else "https://api.lafranceinsoumise.fr",
)
FRONT_DOMAIN = os.environ.get(
    "FRONT_DOMAIN",
    "http://agir.local:8000" if DEBUG else "https://agir.lafranceinsoumise.fr",
)
MAP_DOMAIN = os.environ.get(
    "MAP_DOMAIN",
    "http://agir.local:8000" if DEBUG else "https://agir.lafranceinsoumise.fr",
)
NSP_DOMAIN = os.environ.get("NSP_DOMAIN", "http://localhost")
NSP_AGIR_DOMAIN = os.environ.get("NSP_AGIR_DOMAIN", "http://localhost")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,agir.local").split(",")

# Application definition

INSTALLED_APPS = [
    "agir.lib",
    "agir.authentication",
    "agir.people",
    "agir.events",
    "agir.groups",
    "agir.polls",
    "agir.msgs",
    "oauth2_provider",  # avant clients pour pouvoir redéfinir l'admin
    "agir.clients",
    "agir.front",
    "agir.carte",
    "agir.webhooks",
    "agir.payments",
    "agir.donations",
    "agir.system_pay",
    "agir.checks",
    "agir.loans",
    "agir.mailing",
    "agir.activity.apps.ActivityConfig",
    "agir.notifications",
    "agir.municipales.apps.MunicipalesConfig",
    "agir.legacy",
    "agir.telegram",
    "agir.elus.apps.ElusConfig",
    # default contrib apps
    "agir.api.apps.AdminAppConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # sitemaps
    "django.contrib.sitemaps",
    # redirect
    "django.contrib.sites",
    "django.contrib.redirects",
    # humanize
    "django.contrib.humanize",
    # rest_framework
    "rest_framework",
    # OTP for admin
    "django_otp",
    "django_otp.plugins.otp_totp",
    # date in admin
    "rangefilter",
    # geodjango
    "django.contrib.gis",
    "rest_framework_gis",
    # rules
    "rules.apps.AutodiscoverRulesConfig",
    # crispy forms
    "crispy_forms",
    # django filters
    "django_filters",
    # django_countries
    "django_countries",
    # phone number field
    "phonenumber_field",
    # stdimage
    "stdimage",
    # webpack
    "webpack_loader",
    # fi apps
    "nuntius",
    # push,
    "push_notifications",
    # security
    "corsheaders",
    "reversion",
    "social_django",
    "data_france",
    # profiling
    "silk",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "agir.lib.middleware.NoVaryCookieMiddleWare",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "agir.authentication.middleware.MailLinkMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    "silk.middleware.SilkyMiddleware",
]

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1", "192.168.33.1"]

SILKY_INTERCEPT_FUNC = lambda request: request.user.is_superuser and (
    request.GET.get("silk", False) or request.COOKIES.get("silk", False)
)
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_PERMISSIONS = lambda user: user.is_superuser

ROOT_URLCONF = "agir.api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "agir.authentication.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

if ENABLE_FRONT:
    TEMPLATES[0]["OPTIONS"]["context_processors"].extend(
        ["agir.api.context_processors.basic_information",]
    )

MESSAGE_TAGS = {ERROR: "danger"}
MESSAGE_LEVEL = messages.DEFAULT_LEVELS[
    os.environ.get("MESSAGE_LEVEL", "DEBUG" if DEBUG else "INFO")
]

WSGI_APPLICATION = "agir.api.wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(default="postgis://api:password@localhost/api")
}

# Mails

# by default configured for mailhog sending
email_config = dj_email_url.parse(os.environ.get("SMTP_URL", "smtp://localhost:1025/"))

EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]

# fixed for now ==> maybe more flexible?
EMAIL_TEMPLATES = {
    ################
    ## TEMPLATE LFI
    ################
    # WELCOME_MESSAGE variables: [PROFILE_LINK]
    "WELCOME_LFI_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/ac205f71-61a3-465b-8161-cec5729ecdbb.html",
    # CONFIRM_SUBSCRIPTION_MESSAGE variables: [CONFIRMATION_URL]
    "SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/cd878308-6fd7-4088-b525-a020c5bb3fe0.html",
    # ALREADY_SUBSCRIBED_MESSAGE: [AGO], [PANEL_LINK]
    "ALREADY_SUBSCRIBED_LFI_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/d7040d22-703f-4ac7-883c-d2f04c13be1a.html",
    # DONATION_MESSAGE variables : [PROFILE_LINK]
    "DONATION_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/cab3c2ee-9444-4c70-b16e-9f7dce7929b1.html",
    # INVITATION_SUBSCRIPTION_MESSAGE: [GROUP_NAME], [CONFIRMATION_URL] [SIGNAL_URL]
    "GROUP_INVITATION_WITH_SUBSCRIPTION_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/1db59e8e-0ebd-4dab-8b2d-e7a2d679d6aa.html",
    ################
    ## TEMPLATE NSP
    ################
    "SUBSCRIPTION_CONFIRMATION_NSP_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/7dd4eeb2-c7ce-40f6-a6c7-8207594b64f1.html",
    ################
    ## TEMPLATE AP
    ################
    # GROUP_INVITATION_ABUSE_MESSAGE
    "GROUP_INVITATION_ABUSE_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/5e8059a7-339a-40ff-8741-b5f742f2f63c.html",
    # DONATION_MESSAGE_EUROPEENNES variables : [PROFILE_LINK]
    "CARD_EXPIRATION": "https://mosaico.lafranceinsoumise.fr/emails/d571cda0-9227-4333-b4bd-fc067beb3ec8.html",
    # UNSUBSCRIBE_CONFIRMATION variables [MANAGE_SUBSCRIPTIONS_LINK]
    "UNSUBSCRIBE_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/232528e5-af31-45cc-bdc6-7ef4c2ecf789.html",
    # GROUP_CREATION variables: greetings, group_name,  MANAGE_GROUP_LINK
    "GROUP_CREATION": "https://mosaico.lafranceinsoumise.fr/emails/d852c994-f46d-41ce-89a5-05cfa553476d.html",
    # GROUP_CHANGED variables: GROUP_NAME, GROUP_CHANGES, GROUP_LINK
    "GROUP_CHANGED": "https://mosaico.lafranceinsoumise.fr/emails/e3932ae5-3648-4686-b607-4b744d15dfe8.html",
    # GROUP_SOMEONE_JOINED_NOTIFICATION variables: GROUP_NAME, PERSON_INFORMATION, MANAGE_GROUP_LINK
    "GROUP_SOMEONE_JOINED_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/d19f4012-40e5-44d9-87b6-e49ada121bed.html",
    # GROUP_EXTERNAL_JOIN_OPTION variables: [GROUP_NAME], [JOIN_LINK]
    "GROUP_EXTERNAL_JOIN_OPTIN": "https://mosaico.lafranceinsoumise.fr/emails/5c106c1d-a46f-4072-9c4e-2e3bfbfea069.html",
    # EVENT_CREATION variables: [EVENT_NAME], [CONTACT_{NAME,EMAIL,PHONE,PHONE_VISIBILITY], [LOCATION_{NAME,LOCATION}], [EVENT_LINK], [MANAGE_EVENT_LINK]
    "EVENT_CREATION": "https://mosaico.lafranceinsoumise.fr/emails/0add6793-5c29-406a-ac04-757ad77d5d33.html",
    # EVENT_CHANGED variables: EVENT_NAME, EVENT_CHANGES, EVENT_LINK, EVENT_QUIT_LINK
    "EVENT_CHANGED": "https://mosaico.lafranceinsoumise.fr/emails/7352ea4b-7766-46a9-9dc1-2e98bcd4c96e.html",
    # EVENT_RSVP_NOTIFICATION variables EVENT_NAME, PERSON_INFORMATION, MANAGE_EVENT_LINK
    "EVENT_RSVP_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/2bde68d8-58dc-48d3-94c0-0469c4f468eb.html",
    # EVENT_RSVP_CONFIRMATION variables EVENT_NAME  EVENT_SCHEDULE CONTACT_NAME CONTACT_EMAIL LOCATION_NAME LOCATION_ADDRESS EVENT_LINK
    "EVENT_RSVP_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/2413fa73-d309-4bcd-be24-3a42d4b6ece2.html",
    # EVENT_EXTERNAL_RSVP_OPTIN variables EVENT_NAME RSVP_LINK
    "EVENT_EXTERNAL_RSVP_OPTIN": "https://mosaico.lafranceinsoumise.fr/emails/e7c3e2f6-1089-4f49-82a7-608ab038e6d3.html",
    # EVENT_GUEST_CONFIRMATION variables EVENT_NAME  EVENT_SCHEDULE CONTACT_NAME CONTACT_EMAIL LOCATION_NAME LOCATION_ADDRESS EVENT_LINK
    "EVENT_GUEST_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/e07087c1-60f3-42e9-896a-497e9f589c55.html",
    # EVENT_CANCELLATION variables: EVENT_NAME
    "EVENT_CANCELLATION": "https://mosaico.lafranceinsoumise.fr/emails/40d5812b-aacc-4ab2-b7b6-d944bf90e9d6.html",
    # EVENT_SECRETARIAT_NOTIFICATION variables : EVENT_NAME EVENT_SCHEDULE CONTACT_NAME CONTACT_EMAIL LOCATION_NAME LOCATION_ADDRESS EVENT_LINK LEGAL_INFORMATIONS
    "EVENT_SECRETARIAT_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/d7ebb6a3-f693-4c33-934f-df4335b23621.html",
    # EVENT_ORGANIZER_VALIDATION_NOTIFICATION variables : EVENT_NAME EVENT_SCHEDULE LOCATION_NAME LOCATION_ADDRESS EVENT_LINK MANAGE_EVENT_LINK
    "EVENT_ORGANIZER_VALIDATION_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/668ac434-423b-43b8-9ae0-6d1f3d29c3d4.html",
    # SPENDING_REQUEST_TO_REVIEW_NOTIFICATION variables : SPENDING_REQUEST_NAME GROUP_NAME SPENDING_REQUEST_ADMIN_LINK
    "SPENDING_REQUEST_TO_REVIEW_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/12070f61-6aeb-4d2d-abe0-6ec347adf380.html",
    # FORM_CONFIRMATION variables : CONFIRMATION_NOTE
    "FORM_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/28866993-acf3-45a7-aefd-e75c58e8b52a.html",
    # FORM_NOTIFICATION variables : PERSON_EMAIL, INFORMATIONS
    "FORM_NOTIFICATION": "https://mosaico.lafranceinsoumise.fr/emails/8ac7b301-07dd-457f-8de7-7414f171858e.html",
    # LOGIN_MESSAGE variables: code, expiry_time, name
    "LOGIN_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/b3958815-c3c2-4f93-8b24-47a6c1dd36e2.html",
    # LOGIN_NO_ACCOUNT variables:
    "LOGIN_SIGN_UP_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/83367020-bfd1-409f-84f2-30df33790db5.html",
    # EVENT_REPORT variables: EVENT_NAME,EVENT_REPORT_SUMMARY, EVENT_REPORT_LINK, PREFERENCES_LINK, EMAIL
    "EVENT_REPORT": "https://mosaico.lafranceinsoumise.fr/emails/6bea2d8b-4c03-4f1d-8b97-5e7cecff0c5b.html",
    # CHANGE_MAIL_CONFIRMATION variables: CONFIRMATION_URL
    "CHANGE_MAIL_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/7a2c3dfb-adb5-41dc-baa0-74afba42551f.html",
    # MERGE_ACCOUNT_CONFIRMATION variables: CONFIRMATION_URL, REQUESTER_EMAIL
    "MERGE_ACCOUNT_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/ad6ea640-22fb-4280-9e32-71bb191f1678.html",
    # CONTRACT_CONFIRMATION
    "CONTRACT_CONFIRMATION": "https://mosaico.lafranceinsoumise.fr/emails/c63e76d7-d8a1-434c-bdd6-75337312ca28.html",
    # CHECK INFORMATION
    "CHECK_INFORMATION": "https://mosaico.lafranceinsoumise.fr/emails/b0850152-bf53-4979-b5d3-86f231fd98a8.html",
    # CONFIRM SUBSCRIPTION
    "CONFIRM_SUBSCRIPTION": "https://mosaico.lafranceinsoumise.fr/emails/eb8e6712-32d5-40bb-a69c-cdc1207e12dc.html",
    # TRANSFER_SENDER variables : TRANSFERER_NAME, GROUP_DESTINATION, MEMBER_LIST, MEMBER_COUNT
    "TRANSFER_SENDER": "https://mosaico.lafranceinsoumise.fr/emails/13cecf70-acd6-46a8-9bd8-63cf1bbb79ec.html",
    # TRANSFER_RECEIVER variables : GREETINGS, GROUP_SENDER, GROUP_SENDER_URL, MEMBERS_COUNT, GROUP_NAME, MEMBER_LIST
    "TRANSFER_RECEIVER": "https://mosaico.lafranceinsoumise.fr/emails/53046516-d961-4190-8302-4f239fd30caa.html",
    # YOU_HAVE_BEEN_TRANSFERED variables : GREETINGS, GROUP_SENDER, GROUP_SENDER_URL, GROUP_RECEIVER, GROUP_RECEIVER_URL
    "TRANSFER_ALERT": "https://mosaico.lafranceinsoumise.fr/emails/8eca0332-bcb0-4e1d-816f-9da8bfcb570b.html",
    # GROUP_ALERT_CAPACITY variables : GROUP_NAME, GROUP_NAME_URL, TRANSFER_LINK
    "GROUP_ALERT_CAPACITY_21": "https://mosaico.lafranceinsoumise.fr/emails/8add9bc8-ef7a-4fc6-8591-d4bc0c8ec226.html",
    # GROUP_MAX_CAPACITY variables : GROUP_NAME, TRANSFER_LINK
    "GROUP_ALERT_CAPACITY_30": "https://mosaico.lafranceinsoumise.fr/emails/a4cb42b0-1417-446a-af66-5d8e67b2047e.html",
    # NEW_MESSAGE variables: DISPLAY_NAME, AUTHOR_STATUS, MESSAGE_HTML, DISPLAY_NAME
    "NEW_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/0f9f599a-1dcf-4a49-963e-56078ce9d587.html",
    # EXISTING_EMAIL_SUBSCRIPTION
    "EXISTING_EMAIL_SUBSCRIPTION": "https://mosaico.lafranceinsoumise.fr/emails/f175251e-ad1a-430a-9c07-bb0d415263ff.html",
    # UNEXISTING_EMAIL_LOGIN variables: SUBSCRIPTION_URL
    "UNEXISTING_EMAIL_LOGIN": "https://mosaico.lafranceinsoumise.fr/emails/1cc10994-38d6-45ea-8f70-a3102eb955e9.html",
    # SUBSCRIPTION_CONFIRMATION_MESSAGE variables: CONFIRMATION_URL
    "SUBSCRIPTION_CONFIRMATION_MESSAGE": "https://mosaico.lafranceinsoumise.fr/emails/315b969b-87a7-4b2e-9d61-697af4cbd4a7.html",
}

EMAIL_FROM = os.environ.get(
    "EMAIL_FROM", "Action populaire <noreply@actionpopulaire.fr>"
)
EMAIL_SECRETARIAT = os.environ.get("EMAIL_SECRETARIAT", "nospam@lafranceinsoumise.fr")
EMAIL_EQUIPE_FINANCE = os.environ.get(
    "EMAIL_EQUIPE_FINANCE", "nospam@lafranceinsoumise.fr"
)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.environ.get("STATIC_ROOT")

STATICFILES_DIRS = [os.path.join(os.path.dirname(BASE_DIR), "assets")]
if not DEBUG:
    STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "components/",
        "STATS_FILE": os.path.join(
            STATICFILES_DIRS[0], "components", "webpack-stats.json"
        ),
    }
}
WEBPACK_LOADER_SKIP = os.environ.get("WEBPACK_LOADER_SKIP", "false").lower() == "true"
if WEBPACK_LOADER_SKIP:
    WEBPACK_LOADER["DEFAULT"]["LOADER_CLASS"] = "agir.front.build.DummyWebpackLoader"

MEDIA_URL = "/media/"

MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "media")

# Authentication

AUTH_USER_MODEL = "authentication.Role"

AUTHENTICATION_BACKENDS = [
    # Rules permission backend MUST be in first position
    "agir.clients.authentication.AccessTokenRulesPermissionBackend",
    # This backend is necessary to enforce database permissions
    "django.contrib.auth.backends.ModelBackend",
]

if ENABLE_ADMIN:
    # This backend is used to connect to the administration panel
    AUTHENTICATION_BACKENDS.append("agir.people.backend.PersonBackend")

if ENABLE_FRONT:
    AUTHENTICATION_BACKENDS.extend(
        [
            # This backend is used for email challenge connection
            "agir.authentication.backend.ShortCodeBackend",
            # This backend is used for connection through links found in emails
            "agir.authentication.backend.MailLinkBackend",
            # connection through Facebook
            "social_core.backends.facebook.FacebookOAuth2",
        ]
    )
    LOGIN_URL = "short_code_login"

OAUTH2_PROVIDER_APPLICATION_MODEL = "clients.Client"
OAUTH2_PROVIDER = {"SCOPES_BACKEND_CLASS": "agir.clients.scopes.ScopesBackend"}

# SOCIAL AUTH

SOCIAL_AUTH_STORAGE = "agir.authentication.social.storage.AgirDjangoStorage"
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_PIPELINE = (
    # Éléments par défaut pour récupérer les détails depuis les services tiers,
    # vérifier que le compte est actif, et vérifier si un utilisateur est déjà
    # associé
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    # Identifie s'il existe un compte sur agir avec l'adresse email.
    "social_core.pipeline.social_auth.associate_by_email",
    # Réalise l'association elle-même
    "social_core.pipeline.social_auth.associate_user",
    # Enregistre toutes les données associées comme un objet JSON sur l'association
    "social_core.pipeline.social_auth.load_extra_data",
    # Ajoute un message dans les cas où c'est pertinent
    "agir.authentication.social.pipeline.add_message",
)

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"locale": "fr_FR", "fields": "id, email"}
SOCIAL_AUTH_FACEBOOK_API_VERSION = "3.3"

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# URLS
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "dashboard"
SOCIAL_AUTH_LOGIN_URL = "short_code_login"
SOCIAL_AUTH_LOGIN_ERROR_URL = "social_login_error"

# Admin

OTP_TOTP_ISSUER = "api.lafranceinsoumise.fr"

# REST_FRAMEWORK

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        *(["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "agir.clients.authentication.AccessTokenAuthentication",
        "agir.clients.authentication.ClientAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "agir.lib.rest_framework_permissions.GlobalOrObjectPermissions",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "EXCEPTION_HANDLER": "agir.api.handlers.exception_handler",
}

# Access tokens

AUTH_REDIS_URL = os.environ.get("AUTH_REDIS_URL", "redis://localhost?db=0")
AUTH_REDIS_MAX_CONNECTIONS = 5
AUTH_REDIS_PREFIX = os.environ.get("AUTH_REDIS_PREFIX", "AccessToken:")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
LOG_FILE = os.environ.get("LOG_FILE", "./errors.log")
LOG_DISABLE_JOURNALD = os.environ.get("LOG_DISABLE_JOURNALD", "").lower() in [
    "y",
    "yes",
    "true",
]

if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "journald": {
                "level": "DEBUG",
                "class": "systemd.journal.JournaldLogHandler"
                if not LOG_DISABLE_JOURNALD
                else "logging.StreamHandler",
            },
            "admins_mail": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            "django.template": {
                "handlers": ["journald"],
                "level": "INFO",
                "propagate": False,
            },
            "django": {"handlers": ["journald"], "level": "DEBUG", "propagate": True},
            "celery": {"handlers": ["journald"], "level": "DEBUG", "propagate": True},
            "nuntius.signals": {
                "handlers": ["journald"],
                "level": "INFO",
                "propagate": False,
            },
            "nuntius": {"handlers": ["journald"], "level": "DEBUG", "propagate": True},
            "social": {
                "handlers": ["journald", "admins_mail"],
                "level": "DEBUG",
                "propagate": True,
            },
            "agir": {
                "handlers": ["journald", "admins_mail"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

    sentry_sdk.init(
        integrations=[DjangoIntegration(), RedisIntegration()], traces_sample_rate=0.1,
    )

# CACHING
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache"
        if not DEBUG
        else "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": os.environ.get("CACHING_REDIS_URL", "redis://localhost?db=0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "caching_",
    }
}


# SECURITY
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIAL = False
CORS_URLS_REGEX = r"^(?:/legacy/|/communes/chercher/|/api/)"

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    # should be useless, but we never know
    # SECURE_SSL_REDIRECT = True
    # removed because it created problems with direct HTTP connections on localhost
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

CRISPY_TEMPLATE_PACK = "bootstrap3"

# CELERY
CELERY_BROKER_URL = os.environ.get("BROKER_URL", "redis://")
# make sure there is a max_retries option
CELERY_BROKER_TRANSPORT_OPTIONS = {"max_retries": 4}
# make sure celery does not mess with the root logger
CELERY_WORKER_HIJACK_ROOT_LOGGER = DEBUG
# enable worker events to allow monitoring
CELERY_WORKER_SEND_TASK_EVENTS = True
# enable task events to allow monitoring
CELERY_TASK_SEND_SENT_EVENT = True

CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL", "redis://")

DEFAULT_EVENT_IMAGE = "front/images/default_event_pic.jpg"

PHONENUMBER_DEFAULT_REGION = "FR"

CONNECTION_LINK_VALIDITY = 7

# allow insecure transports for OAUTHLIB in DEBUG mode
if DEBUG:
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "y")

# Get the promo
PROMO_CODE_KEY = os.environb.get(b"PROMO_CODE_KEY", b"prout")
PROMO_CODE_TAG = os.environ.get("PROMO_CODE_TAG", "Code promo matériel")
CERTIFIED_GROUP_SUBTYPES = os.environ.get(
    "CERTIFIED_GROUP_SUBTYPES", "certifié,thématique certifié"
).split(",")
if os.environ.get("PROMO_CODE_DELAY") is not None:
    year, month, day = (
        int(value) for value in os.environ.get("PROMO_CODE_DELAY").split("-")
    )
    PROMO_CODE_DELAY = make_aware(datetime(year, month, day))
else:
    PROMO_CODE_DELAY = None
CERTIFIABLE_GROUP_TYPES = ["L", "B"]  # groupes locaux  # groupes thématiques
CERTIFIABLE_GROUP_SUBTYPES = ["comité d'appui"]

# HTML settings
USER_ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "br",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
    "h2",
    "h3",
    "h4",
]
ADMIN_ALLOWED_TAGS = USER_ALLOWED_TAGS + ["table", "tr", "td", "th"]

SITE_ID = 1

FILE_UPLOAD_PERMISSIONS = 0o644

PROMETHEUS_USER = os.environ.get("PROMETHEUS_USER", "prometheus")
PROMETHEUS_PASSWORD = os.environ.get("PROMETHEUS_PASSWORD", "password")

# Systempay
SYSTEMPAY_SITE_ID = os.environ.get("SYSTEMPAY_SITE_ID", 0)
SYSTEMPAY_PRODUCTION = os.environ.get("SYSTEMPAY_PRODUCTION", "false").lower() == "true"
SYSTEMPAY_CURRENCY = os.environ.get("SYSTEMPAY_CURRENCY", 978)
SYSTEMPAY_CERTIFICATE = os.environ.get("SYSTEMPAY_CERTIFICATE", "arbitrarystring")

DONATION_MINIMUM = 1 * 100  # 1 €
DONATION_MAXIMUM = 1000 * 100  # 1000 €
DONATION_MATOMO_GOAL = os.environ.get("DONATION_MATOMO_GOAL")
MONTHLY_DONATION_MINIMUM = 1 * 100  # 1 €
MONTHLY_DONATION_MAXIMUM = 400 * 100  # 400 €
MONTHLY_DONATION_DAY = 8
MONTHLY_DONATION_MATOMO_GOAL = os.environ.get("MONTHLY_DONATION_MATOMO_GOAL")

LOAN_MINIMUM = 400 * 100  # 400 €
LOAN_MAXIMUM = 100_000 * 100  # 100 000 €
LOAN_MAXIMUM_TOTAL = 207_119_700
LOAN_MAXIMUM_THANK_YOU_PAGE = (
    "https://lafranceinsoumise.fr/2019/04/07/succes-de-lemprunt-populaire/"
)

# France + most numerous communities in France
COUNTRIES_FIRST = ["FR", "PT", "DZ", "MA", "TR", "IT", "GB", "ES"]
COUNTRIES_FIRST_REPEAT = True

# allows the administrator to temporarily disable sending to specific domains
EMAIL_DISABLED_DOMAINS = (
    [d.lower() for d in os.environ.get("EMAIL_DISABLED_DOMAINS").split(",")]
    if "EMAIL_DISABLED_DOMAINS" in os.environ
    else []
)


# The first one will be the default one
PAYMENT_MODES = [
    "agir.system_pay.SystemPayPaymentMode",
    "agir.checks.DonationCheckPaymentMode",
    "agir.checks.EventCheckPaymentMode",
    "agir.pos.MoneyPaymentMode",
    "agir.pos.TPEPaymentMode",
    "agir.payments.imported.ImportedPaymentMode",
]

# OVH Settings
OVH_SMS_DISABLE = os.environ.get("OVH_SMS_DISABLE", "true").lower() == "true"
OVH_SMS_SERVICE = os.environ.get("OVH_SMS_SERVICE")
OVH_APPLICATION_KEY = os.environ.get("OVH_APPLICATION_KEY")
OVH_APPLICATION_SECRET = os.environ.get("OVH_APPLICATION_SECRET")
OVH_CONSUMER_KEY = os.environ.get("OVH_CONSUMER_KEY")
SMS_BUCKET_MAX = 3
SMS_BUCKET_INTERVAL = 600
SMS_BUCKET_IP_MAX = 10
SMS_BUCKET_IP_INTERVAL = 600


# Short login codes settings
SHORT_CODE_VALIDITY = 90
MAX_CONCURRENT_SHORT_CODES = 3

CALENDAR_MAXIMAL_DEPTH = 3

# configuration PRESSERO
PRESSERO_API_URL = os.environ.get("PRESSERO_API_URL", "").rstrip("/")
PRESSERO_USER_NAME = os.environ.get("PRESSERO_USER_NAME")
PRESSERO_SUBSCRIBER_ID = os.environ.get("PRESSERO_SUBSCRIBER_ID")
PRESSERO_CONSUMER_ID = os.environ.get("PRESSERO_CONSUMER_ID")
PRESSERO_PASSWORD = os.environ.get("PRESSERO_PASSWORD")
PRESSERO_SITE = os.environ.get("PRESSERO_SITE", "").rstrip("/")
PRESSERO_APPROBATOR_ID = os.environ.get("PRESSERO_APPROBATOR_ID")
PRESSERO_GROUP_ID = os.environ.get("PRESSERO_GROUP_ID")

# djan
DJAN_URL = "https://la-fi.fr/"
DJAN_API_KEY = os.environ.get("DJAN_API_KEY")

# nuntius
NUNTIUS_REDIS_CONNECTION_GETTER = "agir.api.redis.get_auth_redis_client"
NUNTIUS_PUBLIC_URL = FRONT_DOMAIN
NUNTIUS_SUBSCRIBER_MODEL = "people.Person"
NUNTIUS_SEGMENT_MODEL = "mailing.segment"
if not DEBUG:
    NUNTIUS_EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
NUNTIUS_MOSAICO_TEMPLATES = [
    (
        "/static/mosaico_templates/versafix-blank/template.html",
        "Template sans bannière",
    ),
    ("/static/mosaico_templates/versafix-fi/template.html", "Template LFI"),
    ("/static/mosaico_templates/versafix-nsp/template.html", "Template NSP"),
]

NUNTIUS_MAX_SENDING_RATE = int(os.environ.get("NUNTIUS_MAX_SENDING_RATE", 80))
NUNTIUS_MAX_CONCURRENT_SENDERS = int(
    os.environ.get("NUNTIUS_MAX_CONCURRENT_SENDERS", 6)
)
NUNTIUS_MAX_MESSAGES_PER_CONNECTION = int(
    os.environ.get("NUNTIUS_MAX_MESSAGES_PER_CONNECTION", 0)
)
NUNTIUS_POLLING_INTERVAL = int(os.environ.get("NUNTIUS_POLLING_INTERVAL", 2))

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_FOR_ANYMAIL_SES"),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_KEY_FOR_ANYMAIL_SES"),
        "region_name": "eu-west-1",
        "config": {"connect_timeout": 30, "read_timeout": 30},
    },
    "WEBHOOK_SECRET": os.environ.get("SENDGRID_SES_WEBHOOK_USER", "fi")
    + ":"
    + os.environ.get("SENDGRID_SES_WEBHOOK_PASSWORD", "fi"),
}

BANNER_CONFIG = {"thumbnail": (400, 250), "banner": (1200, 400)}

JITSI_GROUP_SIZE = 5
JITSI_SERVERS = os.environ.get("JITSI_SERVERS", "visio.lafranceinsoumise.fr").split(",")

# telegram
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")


# Municipales
SIGNATURES_DIR = os.environ.get("SIGNATURES_DIR")
municipales_campagnes_filename = os.environ.get("MUNICIPALES_CAMPAGNES")
if municipales_campagnes_filename:
    municipales_campagnes_filename = Path(municipales_campagnes_filename)
    if not municipales_campagnes_filename.is_absolute():
        municipales_campagnes_filename = (
            Path(BASE_DIR).parent / municipales_campagnes_filename
        )
    with municipales_campagnes_filename.open("r") as f:
        MUNICIPALES_CAMPAGNES = json.load(f)
else:
    MUNICIPALES_CAMPAGNES = []

# Push notifications
PUSH_NOTIFICATIONS_SETTINGS = {
    "UPDATE_ON_DUPLICATE_REG_ID": True,
    "UNIQUE_REG_ID": True,
    "WP_PRIVATE_KEY": os.environ.get("WEBPUSH_PRIVATE_KEY"),
    "WP_CLAIMS": {"sub": "mailto: site@lafranceinsoumise.fr"},
    "APNS_AUTH_KEY_PATH": os.environ.get(
        "APNS_AUTH_KEY_PATH", os.path.join(os.path.dirname(BASE_DIR), "..", "apns.p8")
    ),
    "APNS_AUTH_KEY_ID": os.environ.get("APNS_AUTH_KEY_ID"),
    "APNS_TEAM_ID": os.environ.get("APNS_TEAM_ID"),
    "APNS_TOPIC": os.environ.get("APNS_TOPIC", "fr.actionpopulaire.ios"),
    "APNS_USE_SANDBOX": os.environ.get("APNS_USE_SANDBOX", "true").lower() == "true",
}
