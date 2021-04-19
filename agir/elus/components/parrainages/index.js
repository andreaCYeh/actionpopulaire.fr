import React from "react";
import onDOMReady from "@agir/lib/utils/onDOMReady";
import App from "@agir/elus/parrainages/App";
import { renderReactComponent } from "@agir/lib/utils/react";
import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

const displayInterface = () => {
  const elusProchesScript = document.getElementById("elusProches");
  let elusProchesData = [];

  if (elusProchesScript && elusProchesScript.type === "application/json") {
    elusProchesData = JSON.parse(elusProchesScript.textContent);
  }

  renderReactComponent(
    <GlobalContextProvider>
      <App elusProches={elusProchesData} />
    </GlobalContextProvider>,
    document.getElementById("app")
  );
};
onDOMReady(displayInterface);
