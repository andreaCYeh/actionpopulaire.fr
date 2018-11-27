# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-11 15:31
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("people", "0027_remove_personform_personal_information")]

    operations = [
        migrations.AlterField(
            model_name="personform",
            name="fields",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                default=list, verbose_name="Champs"
            ),
        ),
        migrations.RenameField(
            model_name="personform", old_name="fields", new_name="custom_fields"
        ),
    ]
