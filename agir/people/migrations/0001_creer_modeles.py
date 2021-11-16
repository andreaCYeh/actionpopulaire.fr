# Generated by Django 3.1.3 on 2021-01-05 10:59
from django.contrib.postgres.operations import UnaccentExtension

import agir.lib.form_fields
import agir.lib.model_fields
import agir.lib.models
import agir.people.model_fields
import agir.people.models
import agir.people.person_forms.models
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import phonenumber_field.modelfields
import uuid

CREATE_TEXT_CONFIGURATIONS = """
CREATE TEXT SEARCH CONFIGURATION french_unaccented (COPY = french);
ALTER TEXT SEARCH CONFIGURATION french_unaccented
    ALTER MAPPING FOR
        asciiword, asciihword, hword_asciipart,
         word, hword, hword_part
    WITH unaccent, french_stem;  
    
CREATE TEXT SEARCH CONFIGURATION simple_unaccented ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION simple_unaccented
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, simple;
"""

DROP_TEXT_CONFIGURATIONS = """
DROP TEXT SEARCH CONFIGURATION french_unaccented;
DROP TEXT SEARCH CONFIGURATION simple_unaccented;
"""

CREATE_CASELESS_EMAIL_INDEX = """
CREATE UNIQUE INDEX uppercase_email ON people_personemail (upper(address));
"""

REMOVE_CASELESS_EMAIL_INDEX = """
DROP INDEX uppercase_email;
"""

ADD_SEARCH_TRIGGERS_AND_FUNCTIONS = """
CREATE FUNCTION email_to_tsvector(email people_personemail.address%TYPE) RETURNS tsvector AS $$
DECLARE
  email_parts text[];
BEGIN
  email_parts := string_to_array(email, '@');
  RETURN 
    setweight(
      to_tsvector('simple_unaccented', email) ||
      to_tsvector('simple_unaccented', regexp_replace(email_parts[1], '[-._]', ' ', 'g')) ,
    'A') ||
    setweight(to_tsvector('simple_unaccented', email_parts[2]), 'D');
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION get_people_tsvector(
  _id people_person.id%TYPE, first_name people_person.first_name%TYPE,
  last_name people_person.last_name%TYPE, location_zip people_person.location_zip%TYPE
) RETURNS tsvector AS $$
DECLARE
  email RECORD;
  search tsvector;
BEGIN
    --
    -- Return the search vector associated with the person information
    --
    search :=
      setweight(
        to_tsvector('simple_unaccented', coalesce(first_name, '')) || 
        to_tsvector('simple_unaccented', coalesce(last_name, '')), 'B'
      ) ||
      setweight(to_tsvector('simple_unaccented', coalesce(location_zip, '')), 'D');

    FOR email in SELECT address FROM people_personemail WHERE person_id = _id LOOP
      search := search || email_to_tsvector(email.address);
    END LOOP;

    RETURN search;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION process_update_person() RETURNS TRIGGER AS $$
DECLARE
    do_update bool default FALSE;
    email RECORD;
    temp_search tsvector;
BEGIN
    --
    -- Trigger function to update search field on person instance when it is created or modified
    -- 
    --
    IF (NEW.first_name <> OLD.first_name) THEN do_update = TRUE;
    ELSIF (NEW.last_name <> OLD.last_name) THEN do_update = TRUE;
    ELSIF (NEW.location_zip <> OLD.location_zip) THEN do_update = TRUE;
    END IF;

    IF do_update THEN
        NEW.search := get_people_tsvector(NEW.id, NEW.first_name, NEW.last_name, NEW.location_zip);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_people_search_field_from_id(person_id people_person.id%TYPE) RETURNS VOID AS $$
BEGIN
  --
  -- Update search vector for the person identified by person_id
  -- 
  UPDATE people_person SET search = get_people_tsvector(id, first_name, last_name, location_zip) WHERE id = person_id;
END
$$ LANGUAGE plpgsql;

CREATE FUNCTION process_update_email() RETURNS TRIGGER AS $$
BEGIN
  --
  -- Trigger function to update the corresponding person's search vector
  -- when an email is inserted, updated or delete
  --
  IF (tg_op = 'INSERT') THEN
    PERFORM update_people_search_field_from_id(NEW.person_id);
  ELSIF (tg_op = 'DELETE') THEN
    PERFORM update_people_search_field_from_id(OLD.person_id);
  ELSIF (tg_op = 'UPDATE' AND (OLD.address <> NEW.address OR OLD.person_id <> NEW.person_id)) THEN
    PERFORM update_people_search_field_from_id(NEW.person_id);
  END IF;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_person_search_field_when_modified
BEFORE INSERT OR UPDATE ON people_person
  FOR EACH ROW EXECUTE PROCEDURE process_update_person();

CREATE TRIGGER update_search_field_when_email_modified
AFTER INSERT OR UPDATE OR DELETE ON people_personemail
  FOR EACH ROW EXECUTE PROCEDURE process_update_email();

UPDATE people_person SET search = get_people_tsvector(id, first_name, last_name, location_zip);
"""

REMOVE_SEARCH_TRIGGERS_AND_FUNCTIONS = """
DROP TRIGGER update_search_field_when_email_modified ON people_personemail;
DROP FUNCTION process_update_email();
DROP FUNCTION update_people_search_field_from_id(people_person.id%TYPE);
DROP TRIGGER update_person_search_field_when_modified ON people_person;
DROP FUNCTION process_update_person();
DROP FUNCTION get_people_tsvector(
  people_person.id%TYPE, people_person.first_name%TYPE, people_person.last_name%TYPE, people_person.location_zip%TYPE
);
DROP FUNCTION email_to_tsvector(people_personemail.address%TYPE);
"""


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="UUID interne à l'API pour identifier la ressource",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "coordinates",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        geography=True,
                        null=True,
                        srid=4326,
                        verbose_name="coordonnées",
                    ),
                ),
                (
                    "coordinates_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Coordonnées manuelles"),
                            (10, "Coordonnées automatiques précises"),
                            (
                                20,
                                "Coordonnées automatiques approximatives (niveau rue)",
                            ),
                            (
                                25,
                                "Coordonnées automatique approximatives (arrondissement)",
                            ),
                            (30, "Coordonnées automatiques approximatives (ville)"),
                            (50, "Coordonnées automatiques (qualité inconnue)"),
                            (254, "Pas de position géographique"),
                            (255, "Coordonnées introuvables"),
                        ],
                        editable=False,
                        help_text="Comment les coordonnées ci-dessus ont-elle été acquises",
                        null=True,
                        verbose_name="type de coordonnées",
                    ),
                ),
                (
                    "location_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="nom du lieu"
                    ),
                ),
                (
                    "location_address1",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="adresse (1ère ligne)"
                    ),
                ),
                (
                    "location_address2",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="adresse (2ème ligne)"
                    ),
                ),
                (
                    "location_citycode",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="code INSEE"
                    ),
                ),
                (
                    "location_city",
                    models.CharField(blank=True, max_length=100, verbose_name="ville"),
                ),
                (
                    "location_zip",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="code postal"
                    ),
                ),
                (
                    "location_state",
                    models.CharField(blank=True, max_length=40, verbose_name="état"),
                ),
                (
                    "location_country",
                    django_countries.fields.CountryField(
                        blank=True, default="FR", max_length=2, verbose_name="pays"
                    ),
                ),
                (
                    "auto_login_salt",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "is_insoumise",
                    models.BooleanField(default=False, verbose_name="Insoumis⋅e"),
                ),
                (
                    "is_2022",
                    models.BooleanField(default=False, verbose_name="Soutien 2022"),
                ),
                (
                    "membre_reseau_elus",
                    models.CharField(
                        choices=[
                            ("I", "Inconnu / Non pertinent"),
                            ("S", "Souhaite faire partie du réseau des élus"),
                            ("O", "Fait partie du réseau des élus"),
                            ("N", "Ne souhaite pas faire partie du réseau des élus"),
                            ("E", "Exclus du réseau"),
                        ],
                        default="I",
                        help_text="Pertinent uniquement si la personne a un ou plusieurs mandats électoraux.",
                        max_length=1,
                        verbose_name="Membre du réseau des élus",
                    ),
                ),
                (
                    "newsletters",
                    agir.lib.model_fields.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("LFI", "Lettre d'information de la France insoumise"),
                                ("2022", "Lettre d'information NSP"),
                                (
                                    "2022_exceptionnel",
                                    "NSP : informations exceptionnelles",
                                ),
                                ("2022_en_ligne", "NSP actions en ligne"),
                                ("2022_chez_moi", "NSP agir près de chez moi"),
                                ("2022_programme", "NSP processus programme"),
                            ],
                            max_length=255,
                        ),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "subscribed_sms",
                    models.BooleanField(
                        blank=True,
                        default=True,
                        help_text="Nous envoyons parfois des SMS plutôt que des emails lors des grands événements&nbsp;! Vous ne recevrez que les informations auxquelles vous êtes abonné⋅e.",
                        verbose_name="Recevoir les SMS d'information",
                    ),
                ),
                (
                    "event_notifications",
                    models.BooleanField(
                        blank=True,
                        default=True,
                        help_text="Vous recevrez des messages quand les informations des événements auxquels vous souhaitez participer sont mis à jour ou annulés.",
                        verbose_name="Recevoir les notifications des événements",
                    ),
                ),
                (
                    "group_notifications",
                    models.BooleanField(
                        blank=True,
                        default=True,
                        help_text="Vous recevrez des messages quand les informations du groupe change, ou quand le groupe organise des événements.",
                        verbose_name="Recevoir les notifications de mes groupes",
                    ),
                ),
                (
                    "draw_participation",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Vous pourrez être tiré⋅e au sort parmis les Insoumis⋅es pour participer à des événements comme la Convention.Vous aurez la possibilité d'accepter ou de refuser cette participation.",
                        verbose_name="Participer aux tirages au sort",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=255, verbose_name="prénom"),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="nom de famille"
                    ),
                ),
                (
                    "contact_phone",
                    agir.people.model_fields.ValidatedPhoneNumberField(
                        blank=True,
                        max_length=128,
                        region=None,
                        unverified_value="U",
                        validated_field_name="contact_phone_status",
                        verbose_name="Numéro de téléphone de contact",
                    ),
                ),
                (
                    "contact_phone_status",
                    models.CharField(
                        choices=[
                            ("U", "Non vérifié"),
                            ("V", "Vérifié"),
                            ("P", "En attente de validation manuelle"),
                        ],
                        default="U",
                        help_text="Pour les numéros hors France métropolitaine, merci de les indiquer sous la forme internationale, en les préfixant par '+' et le code du pays.",
                        max_length=1,
                        verbose_name="Statut du numéro de téléphone",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("F", "Femme"),
                            ("M", "Homme"),
                            ("O", "Autre/Non défini"),
                        ],
                        max_length=1,
                        verbose_name="Genre",
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de naissance"
                    ),
                ),
                (
                    "mandates",
                    agir.people.model_fields.MandatesField(
                        blank=True, default=list, verbose_name="Mandats électoraux"
                    ),
                ),
                (
                    "meta",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Autres données"
                    ),
                ),
                (
                    "commentaires",
                    models.TextField(
                        blank=True,
                        help_text="ATTENTION : en cas de demande d'accès à ses données par la personne concernée par cette fiche, le contenu de ce champ lui sera communiqué. N'indiquez ici que des éléments factuels.",
                        verbose_name="Commentaires",
                    ),
                ),
                (
                    "search",
                    django.contrib.postgres.search.SearchVectorField(
                        editable=False, null=True, verbose_name="Données de recherche"
                    ),
                ),
                (
                    "referrer_id",
                    models.CharField(
                        default=agir.people.models.generate_referrer_id,
                        max_length=13,
                        unique=True,
                        verbose_name="Identifiant d'invitation",
                    ),
                ),
            ],
            options={
                "verbose_name": "personne",
                "verbose_name_plural": "personnes",
                "ordering": ("-created",),
                "permissions": [
                    (
                        "select_person",
                        "Peut lister pour sélectionner (dans un Select 2 par exemple)",
                    )
                ],
                "default_permissions": ("add", "change", "delete", "view"),
            },
        ),
        migrations.CreateModel(
            name="PersonForm",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                ("title", models.CharField(max_length=250, verbose_name="Titre")),
                ("slug", models.SlugField(unique=True, verbose_name="Slug")),
                ("published", models.BooleanField(default=True, verbose_name="Publié")),
                (
                    "result_url_uuid",
                    models.UUIDField(
                        editable=False,
                        null=True,
                        verbose_name="UUID pour l'affichage des résultats",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Date d'ouverture du formulaire",
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Date de fermeture du formulaire",
                    ),
                ),
                (
                    "editable",
                    models.BooleanField(
                        default=False,
                        verbose_name="Les répondant⋅e⋅s peuvent modifier leurs réponses",
                    ),
                ),
                (
                    "allow_anonymous",
                    models.BooleanField(
                        default=False,
                        verbose_name="Les répondant⋅es n'ont pas besoin d'être connecté⋅es",
                    ),
                ),
                (
                    "send_answers_to",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        verbose_name="Envoyer les réponses par email à une adresse email (facultatif)",
                    ),
                ),
                (
                    "description",
                    agir.lib.models.DescriptionField(
                        help_text="Description visible en haut de la page de remplissage du formulaire",
                        verbose_name="Description",
                    ),
                ),
                (
                    "send_confirmation",
                    models.BooleanField(
                        default=False, verbose_name="Envoyer une confirmation par email"
                    ),
                ),
                (
                    "confirmation_note",
                    agir.lib.models.DescriptionField(
                        help_text="Note montrée (et éventuellement envoyée par email) à l'utilisateur une fois le formulaire validé.",
                        verbose_name="Note après complétion",
                    ),
                ),
                (
                    "before_message",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="Note montrée à l'utilisateur qui essaye d'accéder au formulaire avant son ouverture.",
                        verbose_name="Note avant ouverture",
                    ),
                ),
                (
                    "after_message",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="Note montrée à l'utilisateur qui essaye d'accéder au formulaire après sa date de fermeture.",
                        verbose_name="Note de fermeture",
                    ),
                ),
                (
                    "unauthorized_message",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="Note montrée à tout utilisateur qui n'aurait pas le tag nécessaire pour afficher le formulaire.",
                        verbose_name="Note pour les personnes non autorisées",
                    ),
                ),
                (
                    "main_question",
                    models.CharField(
                        blank=True,
                        help_text="Uniquement utilisée si des choix de tags sont demandés.",
                        max_length=200,
                        verbose_name="Intitulé de la question principale",
                    ),
                ),
                (
                    "custom_fields",
                    models.JSONField(
                        default=agir.people.person_forms.models.default_custom_forms,
                        verbose_name="Champs",
                    ),
                ),
                (
                    "config",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Configuration"
                    ),
                ),
            ],
            options={"verbose_name": "Formulaire",},
        ),
        migrations.CreateModel(
            name="PersonTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "label",
                    models.CharField(max_length=50, unique=True, verbose_name="nom"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "exported",
                    models.BooleanField(
                        default=False, verbose_name="Exporté vers mailtrain"
                    ),
                ),
            ],
            options={"verbose_name": "tag",},
        ),
        migrations.CreateModel(
            name="PersonValidationSMS",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        editable=False,
                        max_length=128,
                        region=None,
                        verbose_name="Numéro de mobile",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        default=agir.people.models.generate_code,
                        editable=False,
                        max_length=8,
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="people.person",
                    ),
                ),
            ],
            options={
                "verbose_name": "SMS de validation",
                "verbose_name_plural": "SMS de validation",
            },
        ),
        migrations.CreateModel(
            name="PersonFormSubmission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "data",
                    models.JSONField(
                        default=dict,
                        encoder=agir.lib.form_fields.CustomJSONEncoder,
                        verbose_name="Données",
                    ),
                ),
                (
                    "form",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="people.personform",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_submissions",
                        to="people.person",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.AddField(
            model_name="personform",
            name="required_tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="authorized_forms",
                related_query_name="authorized_form",
                to="people.PersonTag",
            ),
        ),
        migrations.AddField(
            model_name="personform",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="forms",
                related_query_name="form",
                to="people.PersonTag",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="people", to="people.PersonTag"
            ),
        ),
        migrations.CreateModel(
            name="PersonEmail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "address",
                    models.EmailField(
                        help_text="L'adresse email de la personne, utilisée comme identifiant",
                        max_length=254,
                        verbose_name="adresse email",
                    ),
                ),
                (
                    "_bounced",
                    models.BooleanField(
                        db_column="bounced",
                        default=False,
                        help_text="Indique que des mails envoyés ont été rejetés par le serveur distant",
                        verbose_name="email rejeté",
                    ),
                ),
                (
                    "bounced_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Si des mails ont été rejetés, indique la date du dernier rejet",
                        null=True,
                        verbose_name="date de rejet de l'email",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails",
                        to="people.person",
                    ),
                ),
            ],
            options={"verbose_name": "Email", "order_with_respect_to": "person",},
        ),
        migrations.AddIndex(
            model_name="person",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search"], name="search_index"
            ),
        ),
        migrations.AddIndex(
            model_name="person",
            index=models.Index(fields=["contact_phone"], name="contact_phone_index"),
        ),
        UnaccentExtension(),
        migrations.RunSQL(
            sql=CREATE_TEXT_CONFIGURATIONS, reverse_sql=DROP_TEXT_CONFIGURATIONS,
        ),
        migrations.RunSQL(
            sql=CREATE_CASELESS_EMAIL_INDEX, reverse_sql=REMOVE_CASELESS_EMAIL_INDEX
        ),
        migrations.RunSQL(
            sql=ADD_SEARCH_TRIGGERS_AND_FUNCTIONS,
            reverse_sql=REMOVE_SEARCH_TRIGGERS_AND_FUNCTIONS,
        ),
    ]
