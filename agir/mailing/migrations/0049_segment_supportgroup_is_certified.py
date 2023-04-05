# Generated by Django 3.2.18 on 2023-04-05 08:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailing", "0048_segment_excluded_events"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="segment",
            options={"verbose_name": "Segment", "verbose_name_plural": "Segments"},
        ),
        migrations.AddField(
            model_name="segment",
            name="supportgroup_is_certified",
            field=models.BooleanField(
                default=False, verbose_name="Limiter aux membres de groupes certifiés"
            ),
        ),
    ]
