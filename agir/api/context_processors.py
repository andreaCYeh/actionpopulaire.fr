from django.conf import settings


def domain_names(request):
    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
    }
