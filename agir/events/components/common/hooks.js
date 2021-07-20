import { useMemo } from "react";
import useSWR from "swr";

import { getEventEndpoint } from "./api";

export const useEventFormOptions = () => {
  const { data: eventOptions } = useSWR(
    getEventEndpoint("eventPropertyOptions")
  );

  const organizerGroup = useMemo(() => {
    if (eventOptions && Array.isArray(eventOptions.organizerGroup)) {
      return [
        ...eventOptions.organizerGroup.map((group) => ({
          ...group,
          label: group.name,
          value: group.id,
        })),
        {
          id: null,
          value: null,
          label: "À titre individuel",
          contact: eventOptions.defaultContact,
        },
      ];
    }
  }, [eventOptions]);

  return eventOptions
    ? {
        ...eventOptions,
        organizerGroup,
      }
    : {};
};

export const useMissingRequiredEventDocuments = () => {
  const { data: projects, ...rest } = useSWR(getEventEndpoint("eventProjects"));

  if (Array.isArray(projects)) {
    return {
      projects: projects.filter((project) => project.missingDocumentCount > 0),
      ...rest,
    };
  }

  return { projects, ...rest };
};
