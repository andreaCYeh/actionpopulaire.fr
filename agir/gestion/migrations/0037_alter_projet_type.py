# Generated by Django 3.2.13 on 2022-06-04 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0036_projet_date_evenement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projet",
            name="type",
            field=models.CharField(
                choices=[
                    ("CON", "Conférence de presse"),
                    ("REU", "Réunion publique et meetings"),
                    ("REU-loc", "Réunion publique organisée localement"),
                    ("REU-ora", "Réunion publique avec un orateur national"),
                    ("REU-can", "Réunion publique avec un candidat"),
                    ("REU-mee", "Meeting"),
                    ("DEB", "Débats et conférences"),
                    ("DEB-aso", "Débat organisé par une association"),
                    ("DEB-con", "Conférence"),
                    ("DEB-caf", "Café-débat"),
                    ("DEB-pro", "Projection et débat"),
                    ("MAN", "Manifestations et événements publics"),
                    ("MAN-loc", "Manifestation ou marche organisée localement"),
                    ("MAN-nat", "Manifestation ou marche nationale"),
                    ("MAN-pic", "Pique-nique ou apéro citoyen"),
                    ("MAN-eco", "Écoute collective"),
                    ("MAN-fet", "Fête (auberge espagnole)"),
                    ("MAN-car", "Caravane"),
                    ("ACT", "Autres actions publiques"),
                    ("TEL", "Émission ou débat télévisé"),
                    ("EVE", "Événements spécifiques"),
                    ("EVE-AMF", "AMFiS d'été"),
                    ("EVE-CON", "Convention"),
                    ("INT", "Evenement Interne"),
                    ("INT-for", "Formation"),
                    ("RH", "Dépenses RH mensuelles"),
                ],
                max_length=10,
                verbose_name="Type de projet",
            ),
        ),
    ]
