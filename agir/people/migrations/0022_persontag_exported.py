# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0021_full_text_search")]

    operations = [
        migrations.AddField(
            model_name="persontag",
            name="exported",
            field=models.BooleanField(
                default=False, verbose_name="Exporté vers mailtrain"
            ),
        )
    ]
