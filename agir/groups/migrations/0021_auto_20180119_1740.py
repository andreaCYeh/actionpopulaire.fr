# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-19 16:40
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("groups", "0020_auto_20180119_1451")]

    operations = [
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="color",
            field=models.CharField(
                blank=True,
                help_text="La couleur associée aux marqueurs sur la carte.",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(regex="^#[0-9a-f]{6}$")
                ],
                verbose_name="couleur",
            ),
        ),
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="icon_anchor_x",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="ancre de l'icône (x)"
            ),
        ),
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="icon_anchor_y",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="ancre de l'icône (y)"
            ),
        ),
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="popup_anchor_x",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="ancre de la popup (x)"
            ),
        ),
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="popup_anchor_y",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="ancre de la popup (y)"
            ),
        ),
    ]
