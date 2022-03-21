import { useState } from "react";
import useSWR from "swr";

export const EVENT_TYPES = {
  nearEvents: "suggestions",
  groupEvents: "dans mes groupes",
  ongoingEvents: "en cours",
  pastEvents: "passés",
  organizedEvents: "organisés",
};

const ENDPOINT = {
  rsvpedEvents: "/api/evenements/rsvped/",
  nearEvents: "/api/evenements/suggestions/",
  groupEvents: "/api/evenements/mes-groupes/",
  ongoingEvents: "/api/evenements/rsvped/en-cours/",
  pastEvents: "/api/evenements/rsvped/passes/",
  organizedEvents: "/api/evenements/organises/",
  grandEvents: "/api/evenements/grands-evenements/",
};

export const getAgendaEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const useEventSuggestions = (isPaused = false) => {
  const [activeType, setActiveType] = useState(0);
  const activeKey = Object.keys(EVENT_TYPES)[activeType];
  const { data: events } = useSWR(activeKey && getAgendaEndpoint(activeKey), {
    isPaused,
  });

  return [Object.values(EVENT_TYPES), activeType, setActiveType, events];
};
