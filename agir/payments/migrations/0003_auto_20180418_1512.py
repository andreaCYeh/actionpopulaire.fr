# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-18 13:12
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [("payments", "0002_index")]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                max_length=128, null=True, verbose_name="numéro de téléphone"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="type",
            field=models.CharField(max_length=255, verbose_name="type"),
        ),
    ]
