# Generated by Django 3.2.18 on 2023-04-21 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("event_requests", "0008_eventthemetype_event_request_validation_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventasset",
            name="is_event_image",
            field=models.BooleanField(
                default=False,
                editable=False,
                verbose_name="Utiliser ce visuel comme image de bannière de l'événement",
            ),
        ),
        migrations.AddField(
            model_name="eventtheme",
            name="event_image_template",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"target_format": "png"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                related_query_name="+",
                to="event_requests.eventassettemplate",
                verbose_name="Template de l'image de bannière",
            ),
        ),
        migrations.AddField(
            model_name="eventthemetype",
            name="event_image_template",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"target_format": "png"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                related_query_name="+",
                to="event_requests.eventassettemplate",
                verbose_name="Template de l'image de bannière",
            ),
        ),
    ]
