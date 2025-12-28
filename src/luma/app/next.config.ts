const withMarkdoc = require("@markdoc/next.js");

const version = process.env.NEXT_PUBLIC_RELEASE_VERSION
  ? process.env.NEXT_PUBLIC_RELEASE_VERSION
  : null;

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ["md", "mdoc", "js", "jsx", "ts", "tsx"],
  basePath: version ? `/${version}` : "",
  reactStrictMode: true,
};

// 4. Wrap the final config with Markdoc and export it
module.exports = withMarkdoc(/* options */)(nextConfig);
