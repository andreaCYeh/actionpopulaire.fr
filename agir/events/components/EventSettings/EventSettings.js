import PropTypes from "prop-types";
import { DateTime } from "luxon";
import React, { useMemo } from "react";
import { useLocation, Redirect, useRouteMatch } from "react-router-dom";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import { getMenuRoute, getRoutes } from "./routes.config";
import { useAuthentication } from "@agir/front/authentication/hooks";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement/ObjectManagement";

export const EventSettings = (props) => {
  const { event, basePath } = props;
  const routes = useMemo(() => getRoutes(basePath, event), [basePath, event]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);
  const isAuthorized = useAuthentication(globalRouteConfig.eventSettings);
  const { pathname } = useLocation();
  const isDesktop = useIsDesktop();

  const cancelEvent = { label: "Annuler l'événement", onClick: () => {} };

  const redirectTo = useMemo(() => {
    if (!event?.isOrganizer) {
      return basePath;
    }
    if (isAuthorized === false) {
      return {
        pathname: globalRouteConfig.login.getLink(),
        state: { next: pathname },
      };
    }
    return null;
  }, [event, isAuthorized, basePath, pathname]);

  if (!event) {
    return null;
  }

  const routeMenuMatch = useRouteMatch(menuRoute.path);

  // Open first panel on Desktop
  if (isDesktop && routeMenuMatch?.isExact) {
    return <Redirect to="general/" />;
  }

  const now = DateTime.local();
  const isPast = now > event.endTime;

  return (
    <ObjectManagement
      title={event?.name}
      eventPk={event?.id}
      basePath={basePath}
      routes={routes}
      menuLink={menuRoute.getLink()}
      redirectTo={redirectTo}
      cancel={cancelEvent}
      isPast={isPast}
    />
  );
};
EventSettings.propTypes = {
  event: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    type: PropTypes.string,
    isManager: PropTypes.bool,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default EventSettings;
