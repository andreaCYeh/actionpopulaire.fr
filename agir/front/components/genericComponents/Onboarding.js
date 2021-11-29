import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import style from "@agir/front/genericComponents/_variables.scss";

import onboardingEventImage from "./images/onboarding__event.jpg";
import onboardingActionImage from "./images/onboarding__action.jpg";

const ONBOARDING_TYPE = {
  event: {
    img: onboardingEventImage,
    title: <>Organisez un événement près de chez vous&nbsp;!</>,
    body: (
      <>
        Agissez et organisez un événement de soutien, tel qu’une action de
        solidarité, une réunion en ligne pour discuter du programme, une écoute
        collective des futurs meetings... Organisez-vous avec d’autres membres
        pour soutenir la campagne&nbsp;!
      </>
    ),
    createLabel: "Créer un événement",
    createRoute: "createEvent",
  },
  group__suggestions: {
    title: "Rejoignez un groupe proche de chez vous",
    body: (
      <>
        <p>
          Les groupes d'action permettent aux militants de s’organiser dans leur
          quartier ou dans leur ville.
        </p>
        <p>
          Rejoignez un groupe, agissez sur le terrain et organisez des moments
          de réflexions politiques&nbsp;!
        </p>
      </>
    ),
    mapIframe: "groupsMap",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "groupMap",
    color: "secondary",
  },
  group__creation: {
    title: <>Ou bien créez votre groupe&nbsp;!</>,
    body: (
      <>
        <p>
          Commencez dès aujourd’hui à organiser des actions pour soutenir la
          candidature de Jean-Luc Mélenchon.{" "}
        </p>
        <p>
          Besoin d’inspiration pour animer votre groupe&nbsp;? &nbsp;
          <a
            href="https://infos.actionpopulaire.fr/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Voici quelques pistes
          </a>
          .
        </p>
      </>
    ),
    createLabel: "Créer un groupe",
    createRouteId: "createGroup",
  },
  fullGroup__creation: {
    title: <>Ou bien animez votre propre groupe et invitez-y vos amis&nbsp;!</>,
    body: ({ routes }) => [
      <span key="text">
        Créez votre groupe en quelques clics, et commencez dès aujourd’hui à
        organiser des actions pour soutenir la candidature de Jean-Luc
        Mélenchon. Besoin d’inspiration pour animer votre groupe&nbsp;?{" "}
      </span>,
      routes.newGroupHelp && (
        <a key="link" href={routes.newGroupHelp}>
          Voici quelques pistes.
        </a>
      ),
    ],
    createLabel: "Créer un groupe d'action",
    createRouteId: "createGroup",
  },
  group__nsp: {
    img: onboardingActionImage,
    title: "Rejoignez ou organisez un groupe d'action",
    body: (
      <>
        Les groupes d'actions permettent aux militants de s’organiser dans leur
        quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain
        et organisez des moments de réflexions politiques&nbsp;!
      </>
    ),
    createLabel: "Créer un groupe",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "groupMap",
    createRouteId: "createGroup",
  },
  group__action: {
    img: onboardingActionImage,
    title:
      "Rejoignez un groupe d’action de votre ville pour militer localement",
    body: (
      <>
        Les groupes d’actions permettent aux militants de s’organiser dans leur
        quartier ou dans leur ville. Rejoignez un groupe, agissez sur le terrain
        et organisez des moments de réflexions politiques&nbsp;!
      </>
    ),
    createLabel: "Créer un groupe",
    mapLabel: "Voir les groupes dans ma ville",
    mapRoute: "groupMap",
    createRouteId: "createGroup",
  },
};

const Map = styled.iframe`
  margin: 0;
  padding: 0;
  width: 100%;
  height: 338px;
  border: none;
  overflow: hidden;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const StyledBlock = styled.section`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: space-between;
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    padding: 0;
  }

  header {
    div {
      display: block;
      margin-bottom: 28px;
      width: 100%;
      height: 233px;
      background-repeat: no-repeat;
      background-position: center center;
      background-size: cover;
      border-radius: ${style.borderRadius};

      @media (max-width: ${style.collapse}px) {
        height: 138px;
        margin-bottom: 24px;
      }
    }
  }

  article {
    margin: 0 0 0.5rem;

    a {
      font-weight: 700;
      text-decoration: underline;
    }
  }

  footer {
    display: flex;
    flex-direction: row;
    margin-bottom: 1rem;

    @media (max-width: ${style.collapse}px) {
      flex-direction: column;
      align-items: flex-start;
    }

    ${Button} {
      @media (min-width: ${style.collapse}px) {
        margin-right: 11px;
      }
      @media (max-width: ${style.collapse}px) {
        margin-bottom: 11px;
      }
    }
  }
`;

const Onboarding = (props) => {
  const { type, routes } = props;

  const mapIframe = useResponsiveMemo(
    null,
    type && ONBOARDING_TYPE[type]?.mapIframe
  );

  if (!type || !ONBOARDING_TYPE[type]) {
    return null;
  }

  const {
    img,
    title,
    body,
    mapLabel,
    mapRoute,
    createLabel,
    createRoute,
    createRouteId,
    color,
  } = ONBOARDING_TYPE[type];

  return (
    <StyledBlock>
      <header>
        {img && <div style={{ backgroundImage: `url(${img})` }} />}
        {mapIframe && routes[mapIframe] && <Map src={routes[mapIframe]} />}
        <h3>{title}</h3>
      </header>
      <article>
        <p>{typeof body === "function" ? body(props) : body}</p>
      </article>
      <footer>
        {createRoute && (
          <Button link color="secondary" route={createRoute}>
            {createLabel || "Créer"}
          </Button>
        )}
        {createRouteId && routes[createRouteId] && (
          <Button link color="secondary" href={routes[createRouteId]}>
            {createLabel || "Créer"}
          </Button>
        )}
        {routes[mapRoute] && (
          <Button link route={mapRoute} color={color}>
            {mapLabel || "Voir la carte"}
          </Button>
        )}
      </footer>
    </StyledBlock>
  );
};

Onboarding.propTypes = {
  type: PropTypes.oneOf(Object.keys(ONBOARDING_TYPE)),
  routes: PropTypes.shape({
    createGroup: PropTypes.string,
    newGroupHelp: PropTypes.string,
  }),
};

export default Onboarding;
