import React, { useState, useEffect, useCallback } from "react";
import useSWR from "swr";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField.js";
import ImageField from "@agir/front/formComponents/ImageField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";
import {
  updateGroup,
  getGroupPageEndpoint,
} from "@agir/groups/groupPage/api.js";

import { StyledTitle } from "./styledComponents.js";

const [GROUP_IS_2022, GROUP_LFI] = ["de l'équipe", "du groupe"];

const GroupGeneralPage = (props) => {
  const { onBack, illustration, groupPk } = props;

  const { data: group, mutate } = useSWR(
    getGroupPageEndpoint("getGroup", { groupPk })
  );

  const [isNewImage, setIsNewImage] = useState(false);
  const [isCertified, setIsCertified] = useState(false);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  }, []);

  const handleChangeImage = useCallback(
    async (value) => {
      setErrors((errors) => ({ ...errors, image: null }));

      if (!!value) {
        setIsNewImage(true);
        setFormData((formData) => ({ ...formData, image: value }));
        return;
      }

      if (isNewImage) {
        setIsNewImage(false);
        setFormData((formData) => ({ ...formData, image: null }));
        return;
      }

      // TODO : remove image of group from api
    },
    [isNewImage]
  );

  const handleDescriptionChange = useCallback((value) => {
    // lose focus if uncomment :
    // setErrors((errors) => ({ ...errors, ["description"]: null }));
    setFormData((formData) => ({ ...formData, ["description"]: value }));
  }, []);

  const handleChangeCertified = useCallback((event) => {
    setIsCertified(event.target.checked);
    setErrors((errors) => ({ ...errors, image: null }));
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      setErrors({});
      setIsLoading(true);
      const form = new FormData();
      Object.keys(formData).forEach((e) => {
        if (e === "image" && !isNewImage) return;
        form.append(e, formData[e]);
      });

      if (isNewImage && !isCertified) {
        setErrors((errors) => ({
          ...errors,
          image:
            "Vous devez acceptez les licences pour envoyer votre image en conformité.",
        }));
        setIsLoading(false);
        return;
      }

      const res = await updateGroup(groupPk, form);
      setIsLoading(false);
      if (!!res.error) {
        setErrors(res.error);
        return;
      }
      mutate((group) => {
        return { ...group, ...res.data };
      });
    },
    [formData, groupPk, isCertified, isNewImage]
  );

  useEffect(() => {
    setFormData({
      name: group?.name,
      description: group?.description,
      image: group?.image,
    });
    setIsNewImage(false);
  }, [group]);

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Général</StyledTitle>

      <Spacer size="1rem" />

      <TextField
        id="name"
        name="name"
        label={`Nom ${" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}*`}
        onChange={handleChange}
        value={formData.name}
        error={errors?.name}
      />

      <Spacer size="1rem" />

      <RichTextField
        id="description"
        name="description"
        label={`Description ${
          " " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)
        }*`}
        placeholder=""
        onChange={handleDescriptionChange}
        value={formData.description}
        error={errors?.description}
      />

      <h4>Image de la bannière</h4>
      <span>
        Elle apparaîtra sur la page sur les réseaux sociaux.
        <br />
        Utilisez une image à peu près deux fois plus large que haute. Elle doit
        faire au minimum 1200px de large et 630px de haut pour une qualité
        optimale.
      </span>

      <Spacer size="1rem" />
      <ImageField
        name="image"
        value={formData.image}
        onChange={handleChangeImage}
        error={errors?.image}
      />

      {isNewImage && (
        <>
          <Spacer size="0.5rem" />
          <CheckboxField
            value={isCertified}
            label={
              <>
                En important une image, je certifie être le propriétaire des
                droits et accepte de la partager sous licence libre{" "}
                <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/fr/">
                  Creative Commons CC-BY-NC 3.0
                </a>
                .
              </>
            }
            onChange={handleChangeCertified}
          />
        </>
      )}

      <Spacer size="2rem" />
      <Button color="secondary" $wrap disabled={isLoading}>
        Enregistrer
      </Button>
    </form>
  );
};

export default GroupGeneralPage;
