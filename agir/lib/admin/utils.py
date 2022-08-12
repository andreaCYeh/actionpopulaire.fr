from urllib.parse import urljoin

from django.conf import settings
from django.db.models import Model
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from agir.lib.http import add_query_params_to_url


def display_list_of_links(links):
    """Retourne une liste de liens à afficher dans l'admin Django

    :param links: un itérateur de tuples (link_target, link_text) ou (model_instance, link_text)
    :return: le code html de la liste de liens
    """
    links = (
        (
            get_admin_link(link_or_instance)
            if isinstance(link_or_instance, Model)
            else link_or_instance,
            text,
        )
        for link_or_instance, text in links
    )
    return format_html_join(mark_safe("<br>"), '<a href="{}">{}</a>', links)


def admin_url(viewname, args=None, kwargs=None, query=None, absolute=True):
    """Obtenir l'URL correspondant à une vue d'administration.

    Cette fonction renvoie un résultat même si les URLs de l'admin ne sont pas configurées
    dans ce processus django.

    :param viewname: le nom de la vue, avec ou sans le préfixe 'admin:'
    :param args: les éventuels arguments positionnels de la vue
    :param kwargs: les éventuels arguments par mot-clé de la vue
    :param query: le dictionnaire des arguments à ajouter en query string
    :param absolute: s'il faut ajouter le nom de domaine pour renvoyer une URL absolue
    :return: URL vers la vue
    """

    if not viewname.startswith("admin:"):
        viewname = f"admin:{viewname}"

    url = reverse(viewname, args=args, kwargs=kwargs, urlconf="agir.api.admin_urls")
    if absolute:
        url = urljoin(settings.API_DOMAIN, url)
    if query:
        url = add_query_params_to_url(url, query)
    return url


def get_admin_link(instance, absolute=False):
    """Raccourci pour obtenir le lien admin d'édition d'une instance de modèle quelconque

    :param instance: l'instance de modèle pour laquelle récupérer le lien
    :param absolute: s'il faut renvoyer une URL absolue (avec le nom de domaine)
    :return: URL vers la vue d'édition de l'instance
    """
    return admin_url(
        f"admin:{instance._meta.app_label}_{instance._meta.model_name}_change",
        args=(instance.pk,),
        absolute=absolute,
    )
