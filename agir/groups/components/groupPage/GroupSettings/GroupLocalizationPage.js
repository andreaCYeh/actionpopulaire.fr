import React, { useState, useEffect, useCallback } from "react";
import useSWR from "swr";

import { Toast, TOAST_TYPES } from "@agir/front/globalContext/Toast.js";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import Map from "@agir/carte/common/Map";
import HeaderPanel from "./HeaderPanel";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import LocationField from "@agir/front/formComponents/LocationField.js";

import { StyledTitle } from "./styledComponents.js";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import {
  updateGroup,
  getGroupPageEndpoint,
} from "@agir/groups/groupPage/api.js";

const StyledMap = styled(Map)`
  height: 208px;
`;

const StyledMapConfig = styled(Map)`
  height: calc(100vh - 230px);

  @media (min-width: ${style.collapse}px) {
    height: 400px;
  }
`;

const GroupLocalizationPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const [formLocation, setFormLocation] = useState({});
  const [config, setConfig] = useState(null);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [toasts, setToasts] = useState([]);

  const { data: group, mutate } = useSWR(
    getGroupPageEndpoint("getGroup", { groupPk })
  );

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const handleInputChange = useCallback((_, name, value) => {
    setFormLocation((formLocation) => ({ ...formLocation, [name]: value }));
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      setErrors({});
      setIsLoading(true);
      const res = await updateGroup(groupPk, { location: formLocation });
      setIsLoading(false);
      if (!!res.error) {
        setErrors(res.error?.location);
        return;
      }
      setToasts([
        {
          message: "Informations mises à jour",
          type: TOAST_TYPES.SUCCESS,
        },
      ]);
      mutate((group) => {
        return { ...group, ...res.data };
      });
    },
    [formLocation]
  );

  useEffect(() => {
    setIsLoading(false);
    setFormLocation({
      name: group?.location.name,
      address1: group?.location.address1,
      address2: group?.location.address2,
      zip: group?.location.zip,
      city: group?.location.city,
      country: group?.location.country,
    });
  }, [group]);

  if (config) {
    return (
      <>
        <BackButton
          onClick={() => {
            setConfig(false);
          }}
        />
        <StyledTitle>Personnaliser la localisation</StyledTitle>

        <Spacer size="1rem" />
        <StyledMapConfig center={[-97.14704, 49.8844]} />

        <Spacer size="2rem" />
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Button color="secondary" $wrap disabled={isLoading}>
            Enregistrer les informations
          </Button>
        </div>
      </>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Localisation</StyledTitle>
      <Spacer size="1rem" />
      <StyledMap center={[-97.14704, 49.8844]} />
      <Spacer size="0.5rem" />
      {/* <Button small $wrap onClick={() => setConfig(true)}>
        Personnaliser la localisation sur la carte
      </Button> */}
      <Button as="a" small $wrap href={group?.routes?.geolocate}>
        Personnaliser la localisation sur la carte
      </Button>
      <Spacer size="1rem" />

      <span>
        Si vous ne souhaitez pas rendre votre adresse personnelle publique,
        indiquez un endroit à proximité (café, mairie...)
        <Spacer size="0.5rem" />
        <strong>
          Merci d'indiquer une adresse précise avec numéro de rue, sans quoi
          {" " + (group.is2022 ? "l'équipe" : "le groupe") + " "} n'apparaîtra
          pas sur la carte.
        </strong>
      </span>

      <Spacer size="1rem" />

      <LocationField
        name="location"
        location={formLocation}
        onChange={handleInputChange}
        error={errors && errors.location}
        required
      />

      <Spacer size="2rem" />
      <Button color="secondary" $wrap disabled={isLoading}>
        Enregistrer les informations
      </Button>

      {/* <hr />
      <Spacer size="1rem" />
      <a href="#" style={{ color: style.redNSP }}>
        Supprimer la localisation (déconseillé)
      </a> */}

      <Toast autoClose onClear={clearToasts} toasts={toasts} />
    </form>
  );
};

export default GroupLocalizationPage;
