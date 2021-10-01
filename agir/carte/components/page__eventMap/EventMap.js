import React from "react";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes, getUser } from "@agir/front/globalContext/reducers";
import MapPage from "@agir/carte/common/MapPage";

const EventMap = () => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  if (!routes || !routes.eventsMap) {
    return null;
  }

  return (
    <MapPage
      type="events"
      createLinkProps={{
        as: "Link",
        route: "createEvent",
        children: "Créer un événement dans mon quartier",
      }}
      searchUrl="/evenements/liste/"
      mapURL={routes.eventsMap}
      user={user}
    />
  );
};

export default EventMap;
