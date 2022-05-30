import React from "react";

import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer";

import lfiLogo from "@agir/front/genericComponents/logos/lfi.svg";
import linsoumissionLogo from "@agir/front/genericComponents/logos/linsoumission.svg";
import melenchon2022Logo from "@agir/front/genericComponents/logos/melenchon2022.svg";
import nupesLogo from "@agir/front/genericComponents/logos/nupes.svg";

const StyledArticle = styled.article`
  padding: 0 1.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 1000px;
    margin: 0 auto;
    text-align: center;
  }

  & > * {
    margin: 0;
  }

  h4 {
    font-size: 1.625rem;
    font-weight: 700;

    &::first-letter {
      text-transform: uppercase;
    }

    span {
      display: none;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        display: inline;
      }
    }
  }

  p {
    font-size: 0.875rem;
    padding: 1rem 0 1.25rem;
    line-height: 1.7;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      padding: 0.5rem 0 1.5rem;
    }
  }

  nav {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      display: flex;
      flex-flow: row nowrap;
      justify-content: space-between;
      align-items: center;
    }

    a {
      display: block;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 5rem;
      border-radius: ${(props) => props.theme.borderRadius};
      border: 1px solid ${(props) => props.theme.black200};
      padding: 0 12px;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        flex: 1 1 270px;
      }

      &:hover {
        border-color: ${(props) => props.theme.black500};
      }
    }
  }
`;

const HomeExternalLinks = () => {
  return (
    <StyledArticle>
      <h4>
        <span>Retrouver</span> l'actualité <span>des campagnes</span>
      </h4>
      <p>
        Action Populaire est le réseau social d’action de la France Insoumise et
        de Jean-Luc Mélenchon pour l'élection présidentielle de 2022. Pour
        retrouver l’actualité, rendez-vous sur nos sites&nbsp;:
      </p>
      <nav>
        <a href="https://lafranceinsoumise.fr/">
          <img
            src={lfiLogo}
            alt="logo de la France insoumise"
            width="136"
            height="51"
          />
        </a>
        <Spacer size="1rem" />
        <a href="https://nupes-2022.fr">
          <img
            src={nupesLogo}
            alt="logo de la Nouvelle Union Populaire Écologique et Sociale"
            width="200"
            height="67"
          />
        </a>
        <Spacer size="1rem" />
        <a href="https://linsoumission.fr">
          <img
            src={linsoumissionLogo}
            alt="logo de l'insoumission"
            width="176"
            height="48"
          />
        </a>
        <Spacer size="1rem" />
        <a href="https://melenchon2022.fr">
          <img
            src={melenchon2022Logo}
            alt="logo de la campagne Jean-Luc Mélenchon 2022"
            width="200"
            height="26"
          />
        </a>
      </nav>
    </StyledArticle>
  );
};

export default HomeExternalLinks;
