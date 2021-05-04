import React, { useState, useEffect, useCallback } from "react";
import useSWR from "swr";

import { Toast, TOAST_TYPES } from "@agir/front/globalContext/Toast.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

import {
  updateGroup,
  getGroupPageEndpoint,
} from "@agir/groups/groupPage/api.js";

const GroupContactPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const [contact, setContact] = useState({});
  const [errors, setErrors] = useState({});
  const [isLoading, setIsloading] = useState(true);
  const [toasts, setToasts] = useState([]);

  const { data: group, mutate } = useSWR(
    getGroupPageEndpoint("getGroup", { groupPk })
  );

  const handleCheckboxChange = useCallback(
    (e) => {
      setContact({ ...contact, [e.target.name]: e.target.checked });
    },
    [contact]
  );

  const handleChange = useCallback(
    (e) => {
      setContact({ ...contact, [e.target.name]: e.target.value });
    },
    [contact]
  );

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      setErrors({});
      setIsloading(true);
      const res = await updateGroup(groupPk, { contact });
      setIsloading(false);
      if (!!res.error) {
        setErrors(res.error?.contact);
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
    [contact]
  );

  useEffect(() => {
    setIsloading(false);
    setContact(group?.contact);
  }, [group]);

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Moyens de contact</StyledTitle>

      <Spacer size="1rem" />

      <span>Ces informations seront affichées en public.</span>
      <Spacer size="0.5rem" />
      <span>
        Conseillé : créez une adresse e-mail pour votre
        {" " + (group.is2022 ? "équipe" : "groupe") + " "}et n’utilisez pas une
        adresse personnelle.
      </span>

      <Spacer size="2rem" />

      <TextField
        id="name"
        name="name"
        label="Personnes à contacter*"
        onChange={handleChange}
        value={contact?.name}
        error={errors?.name}
      />

      <Spacer size="1rem" />

      <TextField
        id="email"
        name="email"
        label={`Adresse e-mail ${
          " " + (group.is2022 ? "de l'équipe" : "du groupe")
        }*`}
        onChange={handleChange}
        value={contact?.email}
        error={errors?.email}
      />

      <Spacer size="1rem" />

      <TextField
        id="phone"
        name="phone"
        label="Numéro de téléphone à contacter*"
        onChange={handleChange}
        value={contact?.phone}
        error={errors?.phone}
      />

      <Spacer size="0.5rem" />

      <CheckboxField
        name="hidePhone"
        label="Cacher le numéro de téléphone"
        value={contact?.hidePhone}
        error={errors?.hidePhone}
        onChange={handleCheckboxChange}
      />

      <Spacer size="2rem" />
      <Button color="secondary" type="submit" disabled={isLoading}>
        Enregistrer
      </Button>

      <Toast autoClose onClear={clearToasts} toasts={toasts} />
    </form>
  );
};

export default GroupContactPage;
