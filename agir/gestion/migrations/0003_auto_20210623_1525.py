# Generated by Django 3.1.12 on 2021-06-23 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0002_auto_20210623_1524"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="type",
            field=models.CharField(
                choices=[
                    ("DEV", "Devis"),
                    ("CON", "Contrat"),
                    ("FAC", "Facture"),
                    ("JUS", "Justificatif de dépense"),
                    ("JUS-BIL", "Billet de train"),
                    ("JUS-TRAIN", "Justificatif de train"),
                    ("JUS-CEM", "Carte d'embarquement"),
                    ("PAY", "Preuve de paiement"),
                    ("PAY-CHK", "Scan du chèque"),
                    ("PAY-TKT", "Ticket de caisse"),
                    ("GRA", "Attestation de gratuité"),
                    ("EXA", "Exemplaire fourni"),
                    ("PHO", "Photographie de l'objet ou de l'événement"),
                    ("AUT", "Autre (à détailler dans les commentaires)"),
                ],
                max_length=10,
                verbose_name="Type de document",
            ),
        ),
    ]
