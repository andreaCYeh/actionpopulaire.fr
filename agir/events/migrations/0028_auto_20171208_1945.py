# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-08 18:45
from __future__ import unicode_literals

from django.db import migrations
from agir.lib import models as lib_models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [("events", "0027_eventimage")]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="image",
            field=stdimage.models.StdImageField(
                blank=True,
                help_text="Vous pouvez ajouter une image de bannière : elle apparaîtra sur la page, et sur les réseaux sociaux en cas de partage. Préférez une image à peu près deux fois plus large que haute. Elle doit faire au minimum 1200 pixels de large et 630 de haut pour une qualité optimale.",
                upload_to=lib_models.UploadToInstanceDirectoryWithFilename(
                    filename="banner"
                ),
                verbose_name="image",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="report_image",
            field=stdimage.models.StdImageField(
                blank=True,
                help_text="Cette image apparaîtra en tête de votre compte-rendu, et dans les partages que vous ferez du compte-rendu sur les réseaux sociaux.",
                upload_to=lib_models.UploadToInstanceDirectoryWithFilename(
                    filename="report_banner"
                ),
                verbose_name="image de couverture",
            ),
        ),
    ]
