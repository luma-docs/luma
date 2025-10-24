import { Tabs, Tab } from "../../components";

export const tabs = {
  render: Tabs,
  children: ["tag"],
};

export const tab = {
  render: Tab,
  children: ["paragraph", "fence", "list"],
  attributes: {
    name: {
      type: String,
      required: true,
    },
  },
};
