import { Helmet } from "react-helmet";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";

import {
  getIsSessionLoaded,
  getBackLink,
} from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";
import { Container } from "@agir/front/genericComponents/grid";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import EventForm from "./EventForm";

import illustration from "./images/team-spirit.svg";

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const Illustration = styled.div`
  width: 100%;
  height: 260px;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: center center;
  background-image: url(${illustration});
`;

const StyledInfoBlock = styled.div`
  margin: 0;
  padding: 0;

  @media (min-width: ${style.collapse}px) {
    display: ${({ $desktop }) => ($desktop ? "block" : "none")};
  }
  @media (max-width: ${style.collapse}px) {
    display: ${({ $mobile }) => ($mobile ? "block" : "none")};
  }

  & > * {
    margin: 0;
    padding: 0;
    font-size: 0.875rem;
    line-height: 1.5;
    font-weight: 400;
  }

  & > h3 {
    font-weight: 700;
  }

  ${Illustration} {
    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }
`;

const StyledContainer = styled(Container)`
  margin: 4rem auto;
  padding: 0;
  background-color: white;
  width: 100%;
  max-width: 1098px;
  display: grid;
  grid-template-columns: 1fr 300px;
  grid-gap: 1.5rem;

  @media (max-width: ${style.collapse}px) {
    margin: 0;
    display: block;
  }

  & > div {
    padding: 0 2rem;
  }

  & > div + div {
    padding: 0;

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  h2 {
    font-size: 26px;
    font-weight: 700;
    margin: 0;
  }
`;

const CreateEventSkeleton = () => (
  <StyledContainer>
    <div>
      <Skeleton boxes={5} />
    </div>
    <div width="348px">
      <Skeleton boxes={2} />
    </div>
  </StyledContainer>
);

const InfoBlock = (props) => (
  <StyledInfoBlock {...props}>
    <Illustration aria-hidden="true" />
    <Spacer size="1rem" />
    <p>
      En publiant votre événement, ce dernier sera visible à toutes les
      personnes aux alentours.
      <Spacer size="0.5rem" />
      <a
        href="https://infos.actionpopulaire.fr/groupes/nouvelle-equipe/"
        target="_blank"
        rel="noopener noreferrer"
      >
        Besoin d'idées d'événements&nbsp;?
      </a>
      <Spacer size="0.5rem" />
      <a
        href="https://infos.actionpopulaire.fr/"
        target="_blank"
        rel="noopener noreferrer"
      >
        Consulter le centre d'aide
      </a>
    </p>
  </StyledInfoBlock>
);

const CreateEvent = () => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);

  return (
    <>
      <Helmet>
        <title>Nouvel événement - Action populaire</title>
      </Helmet>
      <PageFadeIn wait={<CreateEventSkeleton />} ready={isSessionLoaded}>
        <StyledContainer>
          <div>
            {!!backLink && (
              <IndexLinkAnchor
                to={backLink.to}
                href={backLink.href}
                route={backLink.route}
                aria-label={backLink.label || "Retour à l'accueil"}
                title={backLink.label || "Retour à l'accueil"}
              >
                <RawFeatherIcon name="arrow-left" color={style.black1000} />
              </IndexLinkAnchor>
            )}
            <Spacer size="1.5rem" />
            <h2>Nouvel événement</h2>
            <InfoBlock $mobile />
            <Spacer size="1.5rem" />
            <EventForm />
          </div>
          <div>
            <InfoBlock $desktop />
          </div>
        </StyledContainer>
      </PageFadeIn>
    </>
  );
};

export default CreateEvent;
