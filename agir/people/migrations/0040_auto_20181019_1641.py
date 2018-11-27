# Generated by Django 2.0.9 on 2018-10-19 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0039_auto_20181016_1851")]

    operations = [
        migrations.AlterField(
            model_name="personform",
            name="required_tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="authorized_forms",
                related_query_name="authorized_form",
                to="people.PersonTag",
            ),
        )
    ]
