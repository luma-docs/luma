import { RenderableTreeNodes, Tag } from "@markdoc/markdoc";

/**
 * Recursively extracts plain text from Markdoc RenderableTreeNodes,
 * including text content from inline code elements.
 *
 * @param children - Array of Markdoc renderable tree nodes
 * @returns The concatenated text content
 */
export function extractTextFromChildren(
  children: RenderableTreeNodes[],
): string {
  let text = "";
  for (const child of children) {
    if (typeof child === "string") {
      text += child;
    } else if (Tag.isTag(child)) {
      // Handle inline code and other inline elements
      if (child.name === "code" && child.attributes.content) {
        text += child.attributes.content;
      } else if (child.children) {
        // Recursively extract text from nested children
        text += extractTextFromChildren(child.children);
      }
    }
  }
  return text;
}
