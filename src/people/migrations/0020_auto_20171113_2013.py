# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-13 19:16
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.migrations import SeparateDatabaseAndState


class Migration(migrations.Migration):
    dependencies = [
        ('people', '0019_auto_20171107_1641'),
    ]

    operations = [
        SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name='personemail',
                    old_name='bounced',
                    new_name='_bounced',
                )
            ]
        ),
        SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='personemail',
                    name='_bounced',
                    field=models.BooleanField(db_column='bounced', default=False, help_text='Indique que des mails envoyés ont été rejetés par le serveur distant', verbose_name='email rejeté'),
                ),

            ]
        )
    ]
