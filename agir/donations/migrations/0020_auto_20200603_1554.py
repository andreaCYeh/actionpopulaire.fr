# Generated by Django 2.2.12 on 2020-06-03 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0019_fix_monthlyallocations_triggers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spendingrequest',
            options={'permissions': (('review_spendingrequest', 'Peut traiter les demandes de dépenses'),), 'verbose_name': 'Demande de dépense ou remboursement', 'verbose_name_plural': 'Demandes de dépense ou remboursement'},
        ),
    ]
