import { nodes } from "@markdoc/markdoc";
import { CodeBlock } from "../../components";
import { Tag } from "@markdoc/markdoc";
import { Node, Config } from "@markdoc/markdoc";

export const fence = {
  render: CodeBlock,
  attributes: nodes.fence.attributes,
  transform(node: Node, config: Config) {
    const attributes = node.transformAttributes(config);
    // Don't transform the content (children) of the fence to avoid rendering tags like
    // {% note %}
    return new Tag("Fence", { ...attributes }, [node.attributes.content]);
  },
};
