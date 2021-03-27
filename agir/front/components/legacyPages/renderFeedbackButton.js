import onDOMReady from "@agir/lib/utils/onDOMReady";

(async function () {
  const [
    { default: React },
    { renderReactComponent },
    { default: FeedbackButton },
    { GlobalContextProvider },
  ] = await Promise.all([
    import("react"),
    import("@agir/lib/utils/react"),
    import("../allPages/FeedbackButton"),
    import("../globalContext/GlobalContext"),
  ]);

  const showHeader = () => {
    renderReactComponent(
      <GlobalContextProvider>
        <FeedbackButton />
      </GlobalContextProvider>,
      document.getElementById("feedback-button")
    );
  };
  onDOMReady(showHeader);
})();
