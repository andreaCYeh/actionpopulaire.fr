import { Footer } from "./Footer";

export default {
  component: Footer,
  title: "Dashboard/Footer",
};

const Template = Footer;

const routes = {
  dashboard: "#dashboard",
  search: "#search",
  personalInformation: "#personalInformation",
  contactConfiguration: "#contactConfiguration",
  signIn: "#signIn",
  logIn: "#logIn",
  createGroup: "#createGroup",
  createEvent: "#createEvent",
  groupsMap: "#groupsMap",
  eventsMap: "#eventsMap",
  events: "#events",
  groups: "#groups",
  activity: "#activity",
  "required-activity": "#required-activity",
  menu: "#menu",
  donations: "#donations",
  contact: "#contact",
  lafranceinsoumise: {
    home: "#lfi:home",
    groupsMap: "#lfi:groupsMap",
    eventsMap: "#lfi:eventsMap",
    thematicTeams: "#lfi:thematicTeams",
  },
  noussommespour: {
    home: "#nsp:home",
    groupsMap: "#nsp:groupsMap",
    eventsMap: "#nsp:eventsMap",
  },
  jlmBlog: "#jlmBlog",
  linsoumission: "#linsoumission",
};
export const Anonymous = Template.bind({});
Anonymous.args = {
  isSignedIn: false,
  routes,
};

export const SignedIn = Template.bind({});
SignedIn.args = {
  routes,
  isSignedIn: true,
};
