import { CrossRef } from "../../components";
import { Node, Config, Tag } from "@markdoc/markdoc";

export const link = {
  render: CrossRef,
  attributes: {
    href: {
      type: String,
    },
  },
  transform(node: Node, config: Config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);

    // If text looks like a link (e.g., "https://google.com"), we transform the text
    // into a Link tag. The problem is that if the text of a Markdown link looks like
    // a link (e.g., "[https://google.com](https://google.com)"), then we create nested
    // Link tags, and Next raises an error.
    //
    // To prevent this issue, we return nested Link tags directly.
    if (children[0] instanceof Tag && children[0].name === "Link") {
      return children[0];
    }

    return new Tag("Link", { ...attributes }, children);
  },
};
