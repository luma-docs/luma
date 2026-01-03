import { Config, Node, Tag } from "@markdoc/markdoc";

export const image = {
  render: "img",
  attributes: {
    src: { type: String, required: true },
    alt: { type: String },
    title: { type: String }
  },
  transform(node: Node, config: Config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);

    const version = process.env.NEXT_PUBLIC_RELEASE_VERSION || null;
    const basePath = version ? `/${version}` : "";
    var imagePath = attributes.src

    if (imagePath.startsWith("/")) {
        imagePath = imagePath.slice(1)
    }

    const modifiedSrc = imagePath.startsWith("http")
      ? imagePath 
      : `${basePath}/${imagePath}`;
    
    return new Tag(
      this.render,
      { ...attributes, src: modifiedSrc },
      children
    );
  }
};
