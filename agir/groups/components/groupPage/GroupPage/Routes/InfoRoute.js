import { Helmet } from "react-helmet";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupLocation from "@agir/groups/groupPage/GroupLocation";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupOrders from "@agir/groups/groupPage/GroupOrders";

import { EmptyMessages } from "@agir/groups/groupPage/EmptyContent";

import {
  ShortAgendaRoutePreview,
  AgendaRoutePreview,
  MessagesRoutePreview,
} from "./RoutePreviews";

const StyledShareCard = styled.div`
  box-shadow: rgba(0, 35, 44, 0.5) 0px 0px 1px,
    rgba(0, 35, 44, 0.08) 0px 2px 0px;

  & > * {
    box-shadow: none;
  }
`;

const MobileInfoRoute = (props) => {
  const { group, groupSuggestions, goToMessagesTab } = props;
  return (
    <>
      {group && (group.hasUpcomingEvents || group.hasPastEvents) ? (
        group.isMember ? (
          <ShortAgendaRoutePreview {...props} />
        ) : (
          <AgendaRoutePreview {...props} />
        )
      ) : null}
      {group && group.hasMessages ? (
        <MessagesRoutePreview {...props} />
      ) : group.isManager ? (
        <EmptyMessages goToMessages={goToMessagesTab} />
      ) : null}
      <GroupContactCard {...group} />
      <GroupOrders {...group} />
      <GroupDescription {...group} />
      <GroupLinks {...group} />
      <GroupFacts {...group} />
      <GroupLocation {...group} />
      {group.routes && group.routes.donations && (
        <GroupDonation url={group.routes.donations} />
      )}
      <StyledShareCard>
        <ShareCard title="Partager le lien du groupe" />
      </StyledShareCard>

      {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 ? (
        <div style={{ paddingTop: "2rem" }}>
          <GroupSuggestions groups={groupSuggestions} />
        </div>
      ) : null}
    </>
  );
};

const DesktopInfoRoute = (props) => {
  const { group, goToMessagesTab } = props;

  return (
    <>
      {group && (group.hasUpcomingEvents || group.hasPastEvents) ? (
        group.isMember ? (
          <ShortAgendaRoutePreview {...props} />
        ) : (
          <AgendaRoutePreview {...props} />
        )
      ) : null}
      {group && group.hasMessages ? (
        <MessagesRoutePreview {...props} />
      ) : group.isManager ? (
        <EmptyMessages goToMessages={goToMessagesTab} />
      ) : null}
      {group &&
      (group.hasUpcomingEvents || group.hasPastEvents || group.hasMessages) ? (
        <>
          <GroupLocation {...group} />
          <ShareCard title="Partager le lien du groupe" />
        </>
      ) : (
        <>
          <GroupDescription {...group} maxHeight="auto" outlined />
          <ShareCard title="Inviter vos ami·es à rejoindre le groupe" />
          <GroupLocation {...group} />
        </>
      )}
    </>
  );
};

MobileInfoRoute.propTypes = DesktopInfoRoute.propTypes = {
  user: PropTypes.object,
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    hasPastEvents: PropTypes.bool,
    hasUpcomingEvents: PropTypes.bool,
    hasMessages: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  messages: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
  goToMessagesTab: PropTypes.func,
  onClickMessage: PropTypes.func,
  isLoadingMessages: PropTypes.bool,
};

const InfoRoute = (props) => (
  <>
    <Helmet>
      <title>{props.group && props.group.name} - Action populaire</title>
    </Helmet>
    <ResponsiveLayout
      {...props}
      MobileLayout={MobileInfoRoute}
      DesktopLayout={DesktopInfoRoute}
    />
  </>
);

InfoRoute.propTypes = {
  group: PropTypes.shape({
    name: PropTypes.string,
  }),
};
export default InfoRoute;
