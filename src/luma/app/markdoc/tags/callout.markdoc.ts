import { Callout, Note, Warning, Tip } from "../../components";

export const note = {
  render: Note,
  children: ["paragraph", "tag", "list"],
};

export const warning = {
  render: Warning,
  children: ["paragraph", "tag", "list"],
};

export const tip = {
  render: Tip,
  children: ["paragraph", "tag", "list"],
};
