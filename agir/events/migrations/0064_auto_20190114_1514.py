# Generated by Django 2.1.5 on 2019-01-14 14:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("events", "0063_merge_20181221_1249")]

    operations = [
        migrations.AlterField(
            model_name="calendaritem",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="calendaritem",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="event",
            name="coordinates_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Coordonnées manuelles"),
                    (10, "Coordonnées automatiques précises"),
                    (20, "Coordonnées automatiques approximatives (niveau rue)"),
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
        migrations.AlterField(
            model_name="event",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="eventimage",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="eventimage",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="eventsubtype",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="eventsubtype",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="rsvp",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="rsvp",
            name="modified",
            field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
    ]
