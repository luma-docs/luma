import type { NextConfig } from "next";

const withMarkdoc = require('@markdoc/next.js');
const version = process.env.NEXT_PUBLIC_RELEASE_VERSION ? process.env.NEXT_PUBLIC_RELEASE_VERSION : null;

module.exports = withMarkdoc(/* options */)({
  pageExtensions: ['md', 'mdoc', 'js', 'jsx', 'ts', 'tsx'],
  basePath: version ? `/${version}` : '',
});

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
};

export default nextConfig;
