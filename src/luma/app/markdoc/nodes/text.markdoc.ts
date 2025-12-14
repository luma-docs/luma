import { Tag, Node, Config } from "@markdoc/markdoc";
import { linkifyUrlsToHtml } from "linkify-urls";

export const text = {
  transform(node: Node, config: Config) {
    const content = node.attributes.content;

    if (typeof content !== "string") {
      return content;
    }

    // Use linkify-urls to convert URLs to HTML
    const linkedHtml = linkifyUrlsToHtml(content);

    // If no URLs were found, linkifyUrlsToHtml returns the original string
    if (linkedHtml === content) {
      return content;
    }

    // Parse the HTML and convert to Markdoc Tags
    // The HTML will be in the format: "text <a href="...">url</a> more text"
    const parts: Array<string | Tag> = [];
    const anchorRegex = /<a href="([^"]+)">([^<]+)<\/a>/g;
    let lastIndex = 0;
    let match;

    while ((match = anchorRegex.exec(linkedHtml)) !== null) {
      // Add text before the link
      if (match.index > lastIndex) {
        parts.push(linkedHtml.substring(lastIndex, match.index));
      }

      // Add the link as a plain <a> tag for external URLs
      const href = match[1];
      const linkText = match[2];
      parts.push(new Tag("Link", { href }, [linkText]));

      lastIndex = anchorRegex.lastIndex;
    }

    // Add any remaining text after the last link
    if (lastIndex < linkedHtml.length) {
      parts.push(linkedHtml.substring(lastIndex));
    }

    return parts.length > 0 ? parts : content;
  },
};
