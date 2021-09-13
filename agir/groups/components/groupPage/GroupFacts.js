import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";

import Card from "./GroupPageCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledList = styled.ul`
  display: inline-flex;
  flex-flow: column wrap;
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 14px;
  font-weight: 400;

  @media (max-width: ${style.collapse}px) {
    display: block;
  }

  li {
    display: flex;
    min-width: 160px;
    align-items: baseline;
    min-height: 26px;

    span + span {
      padding-left: 0.5rem;
    }
  }
`;

const GroupFacts = (props) => {
  const { subtypes, facts } = props;

  if (
    (!Array.isArray(subtypes) || subtypes.length === 0) &&
    (!facts || Object.values(facts).filter(Boolean).length === 0)
  ) {
    return null;
  }

  const {
    eventCount,
    activeMemberCount,
    isCertified,
    creationDate,
    lastActivityDate,
  } = facts;

  return (
    <Card title="À propos">
      <StyledList>
        {!!eventCount && (
          <li>
            <FeatherIcon name="calendar" small inline />
            <span>
              {eventCount} événement{eventCount > 1 && "s"}
            </span>
          </li>
        )}
        {!!activeMemberCount && (
          <li>
            <FeatherIcon name="users" small inline />
            <span>
              {activeMemberCount}{" "}
              {activeMemberCount > 1 ? "membres actifs" : "membre actif"}
            </span>
          </li>
        )}
        {!!isCertified && (
          <li>
            <FeatherIcon name="check-circle" small inline />
            <span>Groupe certifié</span>
          </li>
        )}
        {!!creationDate && (
          <li>
            <FeatherIcon name="clock" small inline />
            <span>Créé {timeAgo(creationDate)}</span>
          </li>
        )}
        {!!lastActivityDate && (
          <li>
            <FeatherIcon name="rss" small inline />
            <span>Dernière activité&nbsp;: {timeAgo(lastActivityDate)}</span>
          </li>
        )}
        {Array.isArray(subtypes) && subtypes.length > 0 && (
          <li>
            <FeatherIcon name="folder" small inline />
            <span>{subtypes.join(", ")}</span>
          </li>
        )}
      </StyledList>
    </Card>
  );
};

GroupFacts.propTypes = {
  facts: PropTypes.shape({
    eventCount: PropTypes.number,
    activeMemberCount: PropTypes.number,
    isCertified: PropTypes.bool,
    creationDate: PropTypes.string,
    lastActivityDate: PropTypes.string,
  }),
  subtypes: PropTypes.arrayOf(PropTypes.string),
};
export default GroupFacts;
