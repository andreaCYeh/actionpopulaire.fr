# Generated by Django 3.1.13 on 2021-11-29 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0015_auto_20210928_1654"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("waiting-payment", "Paiement en attente"),
                    ("group-invitation", "Invitation à un groupe"),
                    ("new-follower", "Nouveau·lle abonné·e dans le groupe"),
                    ("new-member", "Nouveau membre dans le groupe"),
                    (
                        "member-status-changed",
                        "Un membre actif du groupe a été passé au statut abonné·e",
                    ),
                    (
                        "group-membership-limit-reminder",
                        "Les membres du groupes sont de plus en plus nombreux",
                    ),
                    ("new-message", "Nouveau message dans un de vos groupes"),
                    ("new-comment", "Nouveau commentaire dans un de vos groupes"),
                    (
                        "new-comment-restricted",
                        "Nouveau commentaire dans une de vos discussions",
                    ),
                    ("waiting-location-group", "Préciser la localisation du groupe"),
                    (
                        "waiting-location-event",
                        "Préciser la localisation d'un événement",
                    ),
                    (
                        "group-coorganization-invite",
                        "Invitation à coorganiser un événement reçue",
                    ),
                    (
                        "group-coorganization-accepted",
                        "Invitation à coorganiser un événement acceptée",
                    ),
                    (
                        "group-coorganization-accepted-from",
                        "Invitation de leur groupe à coorganiser mon événement acceptée",
                    ),
                    (
                        "group-coorganization-accepted-to",
                        "Invitation de mon groupe à coorganiser leur événement acceptée",
                    ),
                    ("group-info-update", "Mise à jour des informations du groupe"),
                    (
                        "accepted-invitation-member",
                        "Invitation à rejoindre un groupe acceptée",
                    ),
                    ("new-attendee", "Un nouveau participant à votre événement"),
                    ("event-update", "Mise à jour d'un événement"),
                    ("new-event-mygroups", "Votre groupe organise un événement"),
                    ("new-report", "Nouveau compte-rendu d'événement"),
                    ("cancelled-event", "Événement annulé"),
                    ("referral-accepted", "Personne parrainée"),
                    ("announcement", "Associée à une annonce"),
                    (
                        "transferred-group-member",
                        "Un membre d'un groupe a été transferé vers un autre groupe",
                    ),
                    (
                        "new-members-through-transfer",
                        "De nouveaux membres ont été transferés vers le groupe",
                    ),
                    ("group-creation-confirmation", "Groupe créé"),
                    ("event-suggestion", "Événement suggéré"),
                    (
                        "reminder-docs-event-eve",
                        "Rappel à la veille d'un événement des documents à envoyer",
                    ),
                    (
                        "reminder-docs-event-nextday",
                        "Rappel au lendemain d'un événement des documents à envoyer",
                    ),
                    (
                        "reminder-report-form-for-event",
                        "Rappel au lendemain d'un événement de l'éventuel formulaire de bilan à remplir",
                    ),
                ],
                max_length=50,
                verbose_name="Type",
            ),
        ),
    ]
