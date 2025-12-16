import { Tag, Node, Config, RenderableTreeNode } from "@markdoc/markdoc";

import { Heading } from "../../components";
import { extractTextFromChildren } from "../utils";

function generateID(
  children: RenderableTreeNode[],
  attributes: { id?: string },
) {
  if (attributes.id && typeof attributes.id === "string") {
    return attributes.id;
  }
  const text = extractTextFromChildren(children);
  return text
    .replace(/[?]/g, "")
    .replace(/\s+/g, "-")
    .toLowerCase();
}

export const heading = {
  render: Heading,
  children: ["inline"],
  attributes: {
    id: { type: String },
    level: { type: Number, required: true, default: 1 },
    className: { type: String },
  },
  transform(node: Node, config: Config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);
    const id = generateID(children, attributes);

    return new Tag("Heading", { ...attributes, id }, children);
  },
};
