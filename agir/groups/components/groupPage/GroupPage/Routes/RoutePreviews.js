import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupEventList from "@agir/groups/groupPage/GroupEventList";
import DiscussionAnnouncement from "@agir/groups/groupPage/DiscussionAnnouncement";

const RoutePreview = styled.div`
  margin: 0;
  padding: 0 0 1.5rem;
  width: 100%;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 0;
    padding: 1.5rem 1rem;
    background: ${style.black25};

    & + & {
      border-top: 1px solid ${style.black100};
    }
  }

  & > div {
    & > h3 {
      margin-top: 0;
      margin-bottom: 1rem;
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      font-size: 1rem;
      font-weight: 600;

      button {
        background: none;
        border: none;
        outline: none;
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        margin-left: 1rem;
        padding: 0;
        color: ${style.primary500};
        font-weight: inherit;
        font-size: inherit;

        @media (max-width: ${style.collapse}px) {
          margin-left: auto;
        }

        &:hover,
        &:focus {
          text-decoration: underline;
          cursor: pointer;
        }

        & > * {
          flex: 0 0 auto;
        }

        ${RawFeatherIcon} {
          margin-left: 0.5rem;
          margin-top: 1px;
        }
      }
    }

    & > article {
      margin-top: 1rem;
      padding: 0;
      width: 100%;

      @media (max-width: ${style.collapse}px) {
        border: none;
      }

      & > * {
        @media (max-width: ${style.collapse}px) {
          margin: 0;
          background-color: ${style.white};

          & + & {
            margin-top: 1rem;
          }
        }
      }
    }

    & > h3 + article {
      margin-top: 0;
    }
  }
`;

export const AgendaRoutePreview = (props) => {
  const { upcomingEvents, pastEvents, goToAgendaTab } = props;

  const { lastEvent, isUpcoming } = useMemo(() => {
    if (Array.isArray(upcomingEvents) && upcomingEvents.length > 0) {
      return { isUpcoming: true, lastEvent: [upcomingEvents[0]] };
    }
    if (Array.isArray(pastEvents) && pastEvents.length > 0) {
      return { isUpcoming: false, lastEvent: [pastEvents[0]] };
    }
    return { isUpcoming: false, lastEvent: null };
  }, [upcomingEvents, pastEvents]);

  return (
    <RoutePreview>
      <PageFadeIn ready={!!lastEvent} wait={<Skeleton boxes={1} />}>
        <h3>
          <span>{isUpcoming ? "Événement à venir" : "Dernier événement"}</span>
          {goToAgendaTab && (
            <button onClick={goToAgendaTab}>
              Agenda{" "}
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                strokeWidth={3}
              />
            </button>
          )}
        </h3>
        {lastEvent && <GroupEventList events={lastEvent} />}
      </PageFadeIn>
    </RoutePreview>
  );
};
AgendaRoutePreview.propTypes = {
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
};

export const MessagesRoutePreview = (props) => {
  const {
    user,
    messages,
    goToMessagesTab,
    onClickMessage,
    isLoadingMessages,
  } = props;

  const [
    discussionAnnouncement,
    onCloseDiscussionAnnouncement,
  ] = useCustomAnnouncement("DiscussionAnnouncement");

  if (
    (!isLoadingMessages && !Array.isArray(messages)) ||
    messages.length === 0
  ) {
    return null;
  }
  return (
    <RoutePreview>
      <PageFadeIn ready={!isLoadingMessages} wait={<Skeleton boxes={1} />}>
        <h3>
          <span>Derniers messages</span>
          {goToMessagesTab && (
            <button onClick={goToMessagesTab}>
              Messages{" "}
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                strokeWidth={3}
              />
            </button>
          )}
        </h3>
        <DiscussionAnnouncement
          isActive={!!discussionAnnouncement}
          onClose={onCloseDiscussionAnnouncement}
          link={discussionAnnouncement && discussionAnnouncement.link}
        />
        <article>
          {Array.isArray(messages)
            ? messages.map((message) => (
                <MessageCard
                  key={message.id}
                  user={user}
                  message={message}
                  comments={message.comments || message.recentComments || []}
                  onClick={onClickMessage}
                  withBottomButton
                />
              ))
            : null}
        </article>
      </PageFadeIn>
    </RoutePreview>
  );
};
MessagesRoutePreview.propTypes = {
  user: PropTypes.object,
  messages: PropTypes.arrayOf(PropTypes.object),
  goToMessagesTab: PropTypes.func,
  onClickMessage: PropTypes.func,
  isLoadingMessages: PropTypes.bool,
};

export default RoutePreview;
