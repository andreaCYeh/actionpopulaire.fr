import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { useLocation, Redirect, useRouteMatch } from "react-router-dom";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import { getMenuRoute, getRoutes } from "./routes.config";
import { useAuthentication } from "@agir/front/authentication/hooks";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement/ObjectManagement";

const cancelEvent = { label: "Annuler l'événement", onClick: () => {} };

export const EventSettings = (props) => {
  const { event, basePath } = props;
  const routes = useMemo(() => getRoutes(basePath, event), [basePath, event]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);
  const isAuthorized = useAuthentication(globalRouteConfig.eventSettings);
  const routeMenuMatch = useRouteMatch(menuRoute.path);
  const { pathname } = useLocation();
  const isDesktop = useIsDesktop();

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

  // Open first panel on Desktop
  if (isDesktop && routeMenuMatch?.isExact) {
    return <Redirect to="general/" />;
  }

  return (
    <ObjectManagement
      title={event?.name}
      eventPk={event?.id}
      basePath={basePath}
      routes={routes}
      menuLink={menuRoute.getLink()}
      redirectTo={redirectTo}
      cancel={cancelEvent}
      isPast={event?.isPast}
    />
  );
};
EventSettings.propTypes = {
  event: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    type: PropTypes.string,
    isOrganizer: PropTypes.bool,
    isPast: PropTypes.bool,
    endTime: PropTypes.string,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default EventSettings;
