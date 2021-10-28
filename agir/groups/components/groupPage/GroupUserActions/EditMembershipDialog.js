import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledDialog from "./StyledDialog";

const JoinGroupDialog = (props) => {
  const { shouldShow, isLoading, onUpdate, onClose } = props;

  const [personalInfoConsent, setPersonalInfoConsent] = useState(
    props?.personalInfoConsent || false
  );

  const handleCheck = (e) => {
    setPersonalInfoConsent(e.target.checked);
  };

  const handleUpdate = () => {
    onUpdate({ personalInfoConsent });
  };

  return (
    <ModalConfirmation
      shouldShow={shouldShow}
      onClose={!isLoading ? onClose : undefined}
      shouldDismissOnClick={false}
    >
      <StyledDialog>
        <header>
          <h3>Modifier les informations que je partage avec le groupe</h3>
        </header>
        <article>
          <CheckboxField
            label="Nom public et adresse e-mail (obligatoire)"
            readOnly
            disabled
            value
          />
          <CheckboxField
            label="Coordonées complètes (nom complet, téléphone et adresse)."
            onChange={handleCheck}
            disabled={isLoading}
            value={personalInfoConsent}
          />
        </article>
        <footer>
          <Button
            disabled={isLoading}
            loading={isLoading}
            onClick={handleUpdate}
            color="primary"
            block
            wrap
          >
            Mettre à jour
          </Button>
        </footer>
      </StyledDialog>
    </ModalConfirmation>
  );
};

JoinGroupDialog.propTypes = {
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
  onUpdate: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default JoinGroupDialog;
