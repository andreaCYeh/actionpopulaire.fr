# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-25 14:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("groups", "0021_auto_20180119_1740")]

    operations = [
        migrations.RemoveField(model_name="supportgroupsubtype", name="popup_anchor_x"),
        migrations.AlterField(
            model_name="supportgroupsubtype",
            name="popup_anchor_y",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="placement de la popup (par rapport au point)",
            ),
        ),
    ]
