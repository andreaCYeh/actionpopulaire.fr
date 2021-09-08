import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import Modal from "@agir/front/genericComponents/Modal";
import style from "@agir/front/genericComponents/_variables.scss";

const ModalContainer = styled.div`
  background: white;
  height: 50%;
  min-height: 365px;
  width: 40%;
  margin: 5% auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    width: 90%;
    height: 70%;
    min-height: 400px;
  }
`;

const ModalContent = styled.div`
  display: inline-flex;
  flex-direction: column;
  padding: 1rem;

  h1 {
    font-size: 1rem;
  }

  > ${Button} {
    margin-bottom: 1rem;
    color: white;
  }
`;

const ModalConfirmation = (props) => {
  const {
    shouldShow = false,
    onClose,
    title,
    description,
    dismissLabel = "Terminer",
    confirmationLabel = "",
    confirmationUrl = "",
  } = props;

  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
      <ModalContainer>
        <ModalContent>
          <h1>{title}</h1>
          {description}

          <Spacer size="1rem" />
          {!!confirmationUrl && (
            <Button
              style={{ backgroundColor: style.primary500 }}
              type="button"
              link
              route={confirmationUrl}
            >
              {confirmationLabel}
            </Button>
          )}
          <Button
            type="button"
            onClick={onClose}
            style={{ color: style.black1000 }}
          >
            {dismissLabel}
          </Button>
        </ModalContent>
      </ModalContainer>
    </Modal>
  );
};

ModalConfirmation.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default ModalConfirmation;
