import { Tabs, Tab } from "../../components";

export const tabs = {
  render: Tabs,
  children: ["paragraph", "tag", "list"],
};

export const tab = {
  render: Tab,
  children: ["paragraph", "tag", "list"],
  attributes: {
    name: {
      type: String,
      required: true,
    },
  },
};
