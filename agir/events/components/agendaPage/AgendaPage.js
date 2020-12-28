import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import Layout from "@agir/front/dashboardComponents/Layout";
import Agenda from "@agir/events/agendaPage/Agenda";

const AgendaPage = (props) => {
  return (
    <Layout active="events" smallBackgroundColor={style.black25} hasBanner>
      <Agenda {...props} />
    </Layout>
  );
};

export default AgendaPage;

AgendaPage.propTypes = Agenda.propTypes;
