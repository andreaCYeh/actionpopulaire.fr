import Helmet from "react-helmet";
import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useEffect } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import logger from "@agir/lib/utils/logger";
import * as api from "@agir/events/common/api";
import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  setAdminLink,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";
import {
  getIsConnected,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";
import { useIsOffline } from "@agir/front/offline/hooks";

import Link from "@agir/front/app/Link";
import EventHeader from "./EventHeader";
import EventLocationCard from "./EventLocationCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import EventDescriptionCard from "./EventDescriptionCard";
import EventPhotosCard from "./EventPhotosCard";
import {
  Column,
  Container,
  ResponsiveLayout,
  Row,
} from "@agir/front/genericComponents/grid";
import Footer from "@agir/front/dashboardComponents/Footer";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage.js";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import defaultEventImage from "@agir/front/genericComponents/images/banner-map-background.svg";
import EventReportCard from "./EventReportCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import ClickableMap from "@agir/carte/common/Map/ClickableMap";

const log = logger(__filename);

const GroupCards = styled.div`
  & > * {
    margin-bottom: 1rem;
  }
`;
const CardLikeSection = styled.section``;
const StyledColumn = styled(Column)`
  a,
  strong {
    font-weight: 600;
  }

  & > ${Card}, & > ${CardLikeSection} {
    font-size: 14px;
    font-weight: 400;

    @media (max-width: ${style.collapse}px) {
      padding: 1.375rem;
      box-shadow: none;
      border-bottom: 1px solid #c4c4c4;
      margin-bottom: 0;
    }

    &:empty {
      display: none;
    }
  }

  & > ${CardLikeSection} {
    & > h3 {
      margin: 0;
    }
    & > ${Card} {
      padding: 1.375rem 0;
      box-shadow: none;
    }
  }
`;

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 2.5rem 1rem 1.5rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  @media (${(props) => props.theme.collapse}px) {
    display: none;
  }

  svg {
    height: 16px;
  }
`;

const StyledGroupImage = styled.div``;
const StyledMap = styled.div`
  flex: 0 0 424px;
  clip-path: polygon(100% 0%, 100% 100%, 0% 100%, 11% 0%);
  position: relative;
  background-size: 0 0;

  @media (max-width: ${style.collapse}px) {
    clip-path: none;
    width: 100%;
    height: 155px;
    flex-basis: 155px;
    background-size: contain;
    background-position: center center;
    background-repeat: no-repeat;
  }

  & > * {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
  }

  ${StyledGroupImage} {
    background-position: center center;
    background-repeat: no-repeat;
    background-size: contain;

    &:first-child {
      background-size: cover;
      opacity: 0.2;
    }
  }
`;

const MobileLayout = (props) => {
  const { name, contact, routes, groups, illustration, location, subtype } =
    props;
  const hasMap =
    location?.coordinates && Array.isArray(location?.coordinates?.coordinates);

  return (
    <>
      <StyledMap
        style={{
          backgroundColor: illustration?.thumbnail
            ? style.white
            : style.secondary500,
          backgroundImage: !illustration?.thumbnail
            ? `url(${defaultEventImage})`
            : undefined,
        }}
      >
        {illustration ? (
          <>
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${illustration?.thumbnail})` }}
            />
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${illustration?.thumbnail})` }}
            />
          </>
        ) : hasMap ? (
          <ClickableMap
            location={location}
            zoom={11}
            iconConfiguration={subtype}
          />
        ) : null}
      </StyledMap>
      <Container>
        <Row>
          <StyledColumn stack>
            <Card>
              <EventHeader {...props} />
            </Card>
            <EventLocationCard
              name={name}
              timezone={props.timezone}
              schedule={props.schedule}
              location={location}
              routes={routes}
              subtype={subtype}
              isStatic={true}
              hideMap={illustration === null}
            />
            <EventInfoCard {...props} />
            <EventPhotosCard {...props} />
            <EventReportCard {...props} />
            <EventDescriptionCard {...props} />
            {contact && <ContactCard {...contact} />}
            {routes?.facebook && <EventFacebookLinkCard {...props} />}
            <ShareCard url={routes?.details} />
            {Array.isArray(groups) && groups.length > 0 && (
              <CardLikeSection>
                <b>Organisé par</b>
                {groups.map((group, key) => (
                  <GroupCard key={key} {...group} isEmbedded />
                ))}
              </CardLikeSection>
            )}
          </StyledColumn>
        </Row>
      </Container>
    </>
  );
};

const DesktopLayout = (props) => {
  const { logged, groups, contact, participantCount, routes, subtype } = props;

  return (
    <Container
      style={{
        margin: "0 auto 4rem",
        padding: "0 4rem",
        maxWidth: "1336px",
        width: "100%",
      }}
    >
      <Row style={{ minHeight: 56 }}>
        <Column grow>
          {logged && (
            <IndexLinkAnchor route="events">
              <FeatherIcon name="arrow-left" /> &nbsp; Liste des événements
            </IndexLinkAnchor>
          )}
        </Column>
      </Row>
      <Row gutter={32}>
        <Column grow>
          <div>
            <EventHeader {...props} />
            <EventPhotosCard {...props} />
            <EventReportCard {...props} />
            <EventDescriptionCard {...props} />
            {Array.isArray(groups) && groups.length > 0 && (
              <GroupCards>
                <h3 style={{ marginTop: "2.5rem" }}>Organisé par</h3>
                {groups.map((group, key) => (
                  <GroupCard key={key} {...group} isEmbedded />
                ))}
              </GroupCards>
            )}
          </div>
        </Column>
        <StyledColumn width="380px">
          <EventLocationCard {...props} />
          {contact && <ContactCard {...contact} />}
          {(participantCount > 1 || groups?.length > 0 || subtype?.label) && (
            <EventInfoCard {...props} />
          )}
          {routes?.facebook && <EventFacebookLinkCard {...props} />}
          <ShareCard url={routes?.details} />
        </StyledColumn>
      </Row>
    </Container>
  );
};

export const EventPage = (props) => {
  const { startTime, endTime, ...rest } = props;
  const start =
    typeof startTime === "string"
      ? DateTime.fromISO(startTime).setLocale("fr")
      : typeof startTime === "number"
      ? DateTime.fromMillis(startTime).setLocale("fr")
      : null;
  const end =
    typeof endTime === "string"
      ? DateTime.fromISO(endTime).setLocale("fr")
      : typeof endTime === "number"
      ? DateTime.fromMillis(endTime).setLocale("fr")
      : null;
  const schedule = Interval.fromDateTimes(start, end);
  return (
    <ResponsiveLayout
      {...rest}
      startTime={start}
      endTime={end}
      schedule={schedule}
      DesktopLayout={DesktopLayout}
      MobileLayout={MobileLayout}
    />
  );
};

EventPage.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  rsvp: PropTypes.string,
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.object),
  illustration: PropTypes.shape({
    thumbnail: PropTypes.string,
  }),
  description: PropTypes.string,
  startTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    .isRequired,
  endTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
    staticMapUrl: PropTypes.string,
  }),
  contact: PropTypes.shape(ContactCard.propTypes),
  options: PropTypes.shape({ price: PropTypes.string }),
  groups: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
  routes: PropTypes.shape({
    page: PropTypes.string,
    map: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    manage: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
    facebook: PropTypes.string,
    addPhoto: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
  appRoutes: PropTypes.object,
  logged: PropTypes.bool,
  onlineUrl: PropTypes.string,
};

MobileLayout.propTypes = DesktopLayout.propTypes = {
  ...EventPage.propTypes,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
};

const DesktopSkeleton = () => (
  <Container style={{ margin: "4rem auto", padding: "0 4rem" }}>
    <Row gutter={32}>
      <Column grow>
        <Skeleton />
      </Column>
      <Column width="380px">
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

const MobileSkeleton = () => (
  <Container style={{ margin: "2rem auto", padding: "0 1rem" }}>
    <Row>
      <Column>
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

export const ConnectedEventPage = (props) => {
  const { eventPk } = props;
  const isOffline = useIsOffline();
  const isConnected = useSelector(getIsConnected);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const dispatch = useDispatch();

  const { data: eventData, error } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  log.debug("Event data", eventData);

  useEffect(() => {
    if (
      eventData &&
      eventData.isOrganizer &&
      eventData.routes &&
      eventData.routes.manage
    ) {
      dispatch(
        setTopBarRightLink({
          href: eventData.routes.manage,
          label: "Gestion de l'événement",
        })
      );
    }
    if (eventData && eventData.routes && eventData.routes.admin) {
      dispatch(
        setAdminLink({
          href: eventData.routes.admin,
          label: "Administration",
        })
      );
    }
  }, [eventData, dispatch]);

  if (
    error?.message === "NetworkError" ||
    [403, 404].includes(error?.response?.status) ||
    (isOffline && !eventData)
  )
    return (
      <NotFoundPage
        isTopBar={false}
        title="Événement"
        subtitle="Cet événement"
        reloadOnReconnection={false}
      />
    );

  return (
    <>
      {eventData && (
        <Helmet>
          <title>{eventData.name} — Action Populaire</title>
        </Helmet>
      )}
      {isSessionLoaded && eventData ? (
        <EventPage {...eventData} logged={isConnected} />
      ) : (
        <ResponsiveLayout
          DesktopLayout={DesktopSkeleton}
          MobileLayout={MobileSkeleton}
        />
      )}
      <Footer />
    </>
  );
};

ConnectedEventPage.propTypes = {
  eventPk: PropTypes.string,
};

export default ConnectedEventPage;
