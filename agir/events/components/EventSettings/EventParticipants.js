import PropTypes from "prop-types";
import React, { useMemo } from "react";
import useSWR from "swr";
import * as api from "@agir/events/common/api";

import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

import { routeConfig } from "./routes.config";
import { RouteConfig } from "@agir/front/app/routes.config.js";
const organisationLink = new RouteConfig(routeConfig.organisation);

const StyledLink = styled(Link)`
  font-size: 13px;
  display: inline-flex;
  align-items: center;
`;

const BlockTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;

  h3 {
    margin: 0;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  > div {
    margin-top: 3px;
  }
`;

const EventParticipants = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getParticipants", { eventPk })
  );

  // const group = useMemo(() => event?.groups?.length ? event.groups[0] : undefined, [event]);
  const participants = useMemo(() => event?.participants, [event]);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <BlockTitle>
        <h3>{participants.length} Participant·es</h3>
        <div>
          {/* <StyledLink href={"#"}>
            <RawFeatherIcon name="mail" height="13px" />
            Inviter à l’événement
          </StyledLink> */}
          <StyledLink
            to={organisationLink.getLink()}
            style={{ marginLeft: "10px" }}
          >
            <RawFeatherIcon name="settings" height="13px" />
            Inviter à co-organiser
          </StyledLink>
        </div>
      </BlockTitle>

      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails des membres"
        color="primary"
        url={participants?.map(({ email }) => email).join(", ") || ""}
        $wrap
      />

      {/* <Spacer size="1rem" />
      <MemberList key={0} members={[group]} /> */}
      <Spacer size="2rem" />
      <MemberList key={1} members={participants} />
      <Spacer size="1rem" />
    </>
  );
};
EventParticipants.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventParticipants;
