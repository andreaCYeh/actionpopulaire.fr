import { ELU_STATUTS } from "./types";

export const ACTION_TYPES = {
  CHANGER_STATUT: "changer-statut",
  RESULTATS_RECHERCHE: "resultats-recherche",
  SELECTION: "selection",
};

export const initialState = () => {
  const elusInitiauxScript = document.getElementById("elusInitiaux");
  let elusInitiaux = { proches: [], aContacter: [], termines: [] };

  if (elusInitiauxScript && elusInitiauxScript.type === "application/json") {
    elusInitiaux = JSON.parse(elusInitiauxScript.textContent);
  }

  return {
    elusAContacter: elusInitiaux.aContacter,
    elusTermines: elusInitiaux.termines,
    elusProches: elusInitiaux.proches,
    elusRecherche: [],
    selection: null,
  };
};

export const reducer = (state, action) => {
  if (action.type === ACTION_TYPES.CHANGER_STATUT) {
    const {
      elusAContacter,
      elusTermines,
      elusProches,
      elusRecherche,
      selection,
    } = state;
    const nouvelElu = action.elu;

    return {
      // on l'ajoute ou on le retire de la liste des élus à contacter selon le statut
      elusAContacter:
        nouvelElu.statut === ELU_STATUTS.A_CONTACTER
          ? [nouvelElu, ...elusAContacter]
          : elusAContacter.filter((e) => e.id !== nouvelElu.id),
      // On le retire de la liste des élus proches (dans aucun cas un nouvel élu
      // ne peut rejoindre cette liste !)
      elusTermines:
        nouvelElu.statut === ELU_STATUTS.PERSONNELLEMENT_VU
          ? [nouvelElu, ...elusTermines]
          : elusTermines.filter((e) => e.id !== nouvelElu.id),
      elusProches: elusProches.filter((e) => e.id !== nouvelElu.id),
      // On intervertit le nouvel élu s'il était présent dans la liste des élus recherche
      elusRecherche: elusRecherche.map((e) =>
        e.id === nouvelElu.id ? nouvelElu : e
      ),
      selection: selection.id === nouvelElu.id ? nouvelElu : selection,
    };
  } else if (action.type === ACTION_TYPES.RESULTATS_RECHERCHE) {
    return {
      ...state,
      elusRecherche: action.resultats,
    };
  } else if (action.type === ACTION_TYPES.SELECTION) {
    return {
      ...state,
      selection: action.elu,
    };
  }

  return state;
};
