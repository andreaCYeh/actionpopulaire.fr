# Generated by Django 3.2.14 on 2022-07-13 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailing", "0042_auto_20220712_1327"),
    ]

    operations = [
        migrations.AlterField(
            model_name="segment",
            name="elu",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Peu importe"),
                    ("M", "Uniquement les membres du réseau des élus"),
                    ("E", "Tous les élus, sauf les exclus du réseau"),
                    (
                        "R",
                        "Les membres du réseau plus tout ceux à qui on a pas encore demandé",
                    ),
                ],
                max_length=1,
                verbose_name="Est un élu",
            ),
        ),
    ]
