import rules

from .models import StatutMandat, types_elus
from ..lib.rules import is_authenticated_person

# TODO: ajouter une règle pour donner la permission acces_parrainages
from ..people.models import Person


@rules.predicate
def est_elu_verifie(role, obj=None):
    if role.person.membre_reseau_elus in [
        Person.MEMBRE_RESEAU_NON,
        Person.MEMBRE_RESEAU_EXCLUS,
    ]:
        return False
    return any(
        model.objects.filter(person=role.person, statut=StatutMandat.CONFIRME).exists()
        for model in types_elus.values()
    )


# rules.add_perm("elus.acces_parrainages", is_authenticated_person & est_elu_verifie)
