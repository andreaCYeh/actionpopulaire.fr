import csv
import io
from collections import OrderedDict
from email.mime.text import MIMEText

from data_france.models import Commune
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management import BaseCommand
from django.utils import timezone

from agir.elections.data import (
    get_circonscription_legislative_for_commune,
    get_campaign_manager_for_circonscription_legislative,
)
from agir.voting_proxies.models import VotingProxyRequest

CSV_FIELDS = OrderedDict(
    {
        "first_name": "prenom",
        "last_name": "nom",
        "email": "email",
        "contact_phone": "telephone",
        "commune": "commune",
        "polling_station_number": "bureau_de_vote",
        "voter_id": "numero_national_electeur",
        "voting_date": "date_de_scrutin",
    }
)

EMAIL_TEMPLATE = """
=======================================================================
DEMANDE DE PROCURATIONS ÉLECTIONS LÉGISLATIVES DU 12 ET 19 JUIN 2022
=======================================================================

Bonjour {},


Veuillez trouver-ci jointe la liste des demandes de procuration de votre circonscription (ou à proximité) que nous avons 
reçu et qui sont toujours en attente d'un ou d'une volontaire.

Vous recevez ce message car vous avez été indiqué·e comme directeur·rice de campagne pour les législatives 2022 par les 
candidats de la circonscription {}.

Pour toute question, vous pouvez contacter l'équipe d'organisation des campagnes législatives à l'adresse 
legislatives@melenchon2022.fr.


Cordialement.

L'équipe d'Action populaire.
"""


class Command(BaseCommand):
    """
    Send reminder for non-confirmed accepted voting proxy requests
    """

    help = "Send pending voting proxy requests to campaign managers"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = False
        self.silent = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute without actually sending any notification or updating data",
        )
        parser.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="Display a progress bar during the script execution",
        )

    def log(self, message):
        if not self.silent:
            print(message)

    def get_pending_requests_csv_string(self, pending_requests):
        output = io.StringIO()
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow([label for key, label in CSV_FIELDS.items()])

        for request in pending_requests:
            writer.writerow(
                [getattr(request, key) for (key, label) in CSV_FIELDS.items()]
            )

        return output.getvalue()

    def send_voting_proxy_requests_to_campaign_manager(
        self, pending_requests, campaign_manager
    ):
        today = timezone.now().strftime("%Y-%m-%d")
        subject = f"[Législatives 2022] Demandes de procuration en attente - {today}"
        body = EMAIL_TEMPLATE.format(
            campaign_manager["prenom"], campaign_manager["circo"]
        )
        connection = get_connection()
        with connection:
            email = EmailMultiAlternatives(
                connection=connection,
                from_email="robot@actionpopulaire.fr",
                reply_to=("legislatives@melenchon2022.fr",),
                subject=subject,
                to=(campaign_manager["email"],),
                body=body,
            )
            csv_string = self.get_pending_requests_csv_string(pending_requests)
            attachment = MIMEText(csv_string)
            attachment.add_header("Content-Type", "text/csv")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"demandes_de_procuration-{today}.csv",
            )
            email.attach(attachment)
            email.send()

    def send_requests_to_campaign_manager(self, pending_requests, campaign_manager):
        self.log(
            f"Sending {pending_requests.count()} voting proxy request(s) "
            f"to circonscription {campaign_manager['circo']}'s campaign manager"
        )
        if self.dry_run:
            self.log(self.get_pending_requests_csv_string(pending_requests))
            return
        # Send email to campaign managers
        self.send_voting_proxy_requests_to_campaign_manager(
            pending_requests, campaign_manager
        )
        # Update pending request status to remove from auto matching
        pending_requests.update(status=VotingProxyRequest.STATUS_FORWARDED)

    def handle(
        self,
        *args,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        self.silent = silent

        commune_ids = (
            VotingProxyRequest.objects.pending()
            .exclude(commune_id__isnull=True)
            .order_by()
            .values_list("commune_id")
            .distinct()
        )
        by_circo = {}

        for commune in Commune.objects.filter(id__in=commune_ids):
            circo = get_circonscription_legislative_for_commune(commune)
            if circo and not by_circo.get(circo):
                by_circo[circo] = [commune.id]
            elif circo:
                by_circo[circo].append(commune.id)

        for circo, circo_commune_ids in by_circo.items():
            campaign_manager = get_campaign_manager_for_circonscription_legislative(
                circo
            )
            if campaign_manager:
                pending_requests = VotingProxyRequest.objects.pending().filter(
                    commune_id__in=circo_commune_ids
                )
                self.send_requests_to_campaign_manager(
                    pending_requests, campaign_manager
                )

        self.log("Bye!\n\n")
