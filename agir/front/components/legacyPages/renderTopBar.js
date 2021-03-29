import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: TopBar },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("../allPages/TopBar"),
    import("../globalContext/GlobalContext"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <GlobalContextProvider>
        <TopBar />
      </GlobalContextProvider>,
      document.getElementById("top-bar")
    );
  };
  onDOMReady(showHeader);
})();
