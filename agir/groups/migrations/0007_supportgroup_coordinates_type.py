# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-28 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("groups", "0006_membership_notifications_enabled")]

    operations = [
        migrations.AddField(
            model_name="supportgroup",
            name="coordinates_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Coordonnées manuelles"),
                    (10, "Coordonnées automatiques précises"),
                    (20, "Coordonnées automatiques approximatives (niveau rue)"),
                    (30, "Coordonnées automatiques approximatives (ville)"),
                    (50, "Coordonnées automatiques (qualité inconnue)"),
                    (255, "Coordonnées introuvables"),
                ],
                editable=False,
                help_text="Comment les coordonnées ci-dessus ont-elle été acquéries",
                null=True,
                verbose_name="type de coordonnées",
            ),
        )
    ]
