import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import PushModal from "@agir/front/allPages/PushModal";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import TopBar from "@agir/front/allPages/TopBar";
import SWRContext from "@agir/front/allPages/SWRContext";

const renderLegacyPageComponents = () => {
  let renderElement = document.getElementById("mainApp");
  if (!renderElement) {
    renderElement = document.createElement("div");
    renderElement.id = "mainApp";
    document.body.appendChild(renderElement);
  }
  const hideFeedbackButton =
    !!window?.Agir?.hideFeedbackButton ||
    document.querySelectorAll("form[method='post']")?.length > 0;

  renderReactComponent(
    <SWRContext>
      <GlobalContextProvider>
        <TopBar hideBannerDownload />
        <PushModal isActive />
        {hideFeedbackButton ? null : <FeedbackButton />}
      </GlobalContextProvider>
    </SWRContext>,
    renderElement
  );
};

onDOMReady(renderLegacyPageComponents);
