import React from "react";

import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledFooter = styled.main`
  padding: 6rem 3.5rem;
  background-color: ${style.primary500};
  color: white;
  text-align: center;

  @media (min-width: ${style.collapse}px) {
    display: flex;
    flex-flow: row nowrap;
    justify-content: center;
    align-items: center;
  }

  h2 {
    margin: 0;
    font-size: 48px;
    letter-spacing: -0.04em;
    line-height: 1.3;
    font-weight: 700;
    color: inherit;

    @media (min-width: ${style.collapse}px) {
      flex: 0 0 auto;
    }
  }

  ${Button} {
    margin: 0;
    width: 100%;
    justify-content: center;
    height: 70px;
    font-size: 1.25rem;
    border: 1px solid ${style.white};

    @media (min-width: ${style.collapse}px) {
      flex: 0 0 200px;
    }
  }
`;

const HomeFooter = () => {
  return (
    <StyledFooter>
      <h2>Passez&nbsp;à l'action&nbsp;!</h2>
      <Spacer size="2rem" />
      <Button as="Link" to="/inscription/" color="tertiary">
        Je rejoins
      </Button>
      <Spacer size="1rem" />
      <Button as="Link" to="/connexion/" color="primary">
        Se connecter
      </Button>
    </StyledFooter>
  );
};

export default HomeFooter;
