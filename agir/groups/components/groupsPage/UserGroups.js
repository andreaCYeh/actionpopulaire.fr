import PropTypes from "prop-types";
import React, { useMemo } from "react";

import GroupList from "./GroupList";
import GroupCard from "@agir/groups/groupComponents/GroupCard";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const StyledContainer = styled.div`
  padding-bottom: 64px;

  @media (max-width: ${style.collapse}px) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
`;

const GroupsPage = ({ groups }) => {
  const [joined, followed] = useMemo(() => {
    if (!Array.isArray(groups)) {
      return [[], []];
    }
    const joined = [];
    const followed = [];
    groups.forEach((group) => {
      group.isActiveMember ? joined.push(group) : followed.push(group);
    });
    return [joined, followed];
  }, [groups]);

  if (!Array.isArray(groups) || groups.length === 0) {
    return null;
  }

  return (
    <StyledContainer>
      {joined.length > 0 && (
        <GroupList>
          {joined.map((group) => (
            <GroupCard
              key={group.id}
              {...group}
              displayDescription={false}
              displayType={false}
              displayGroupLogo={false}
              displayMembership={false}
            />
          ))}
        </GroupList>
      )}
      {followed.length > 0 && (
        <GroupList>
          {joined.length > 0 && <h3>Groupes suivis</h3>}
          {followed.map((group) => (
            <GroupCard
              key={group.id}
              {...group}
              displayDescription={false}
              displayType={false}
              displayGroupLogo={false}
              displayMembership={false}
            />
          ))}
        </GroupList>
      )}
    </StyledContainer>
  );
};

GroupsPage.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.object),
};

export default GroupsPage;
