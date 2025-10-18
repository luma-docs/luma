import Head from "next/head";

import { SideNav, TableOfContents } from "../components";
import { Footer } from "../components/Footer";
import VersionSelector from "../components/VersionSelector";
import "prismjs";
// Import other Prism themes here
import "prismjs/components/prism-bash.min";
import "prismjs/components/prism-python.min";
import "prismjs/components/prism-yaml.min";
import "prismjs/components/prism-markdown.min";
import "../styles/prism-theme.css";
import { useRouter } from "next/router";

import "prismjs";
import "prismjs/components/prism-bash.min";
import "prismjs/components/prism-python.min";
import "prismjs/components/prism-yaml.min";

import "../styles/prism-theme.css";
import "../styles/globals.css";

import type { AppProps } from "next/app";
import type { MarkdocNextJsPageProps } from "@markdoc/next.js";
import { RenderableTreeNodes, Tag } from "@markdoc/markdoc";

import configData from "../data/config.json";
import { Config } from "../types/config";
const config = configData as Config;

import { TableOfContentsItem } from "../components/TableOfContents";

function collectHeadings(
  node: RenderableTreeNodes,
  sections: TableOfContentsItem[] = [],
) {
  // I think this function assumes the root node is an 'article' tag?
  if (Tag.isTag(node)) {
    if (node.name === "Heading") {
      const title = node.children[0];

      const id = node.attributes.id || "ham"; // Assuming you have an ID generator
      const level = node.attributes.level || 1; // Default to level 1 if not provided

      if (typeof title === "string") {
        sections.push({
          id,
          level,
          title,
        });
      }
    }

    if (node.children) {
      for (const child of node.children) {
        collectHeadings(child, sections);
      }
    }
  }

  return sections;
}
import { useEffect } from "react";

export type MyAppProps = MarkdocNextJsPageProps;

export default function MyApp({ Component, pageProps }: AppProps<MyAppProps>) {
  const { markdoc } = pageProps;
  const router = useRouter();

  useEffect(() => {
    const handleRouteChange = () => {
      const main = document.querySelector(".main");
      if (main) {
        main.scrollTop = 0;
      }
    };

    router.events.on("routeChangeComplete", handleRouteChange);

    return () => {
      router.events.off("routeChangeComplete", handleRouteChange);
    };
  }, [router]);

  // The Luma CLI should copy the user-provided favicon to 'favicon.ico' in the public
  // directory. If no favicon is provided, use the default favicon.
  const faviconHref = config?.favicon
    ? `${router.basePath}/favicon.ico`
    : `${router.basePath}/default-favicon.ico`;

  const toc = pageProps.markdoc?.content
    ? collectHeadings(pageProps.markdoc.content)
    : [];

  let title = `${config?.name || "Untitled"} Docs`;
  if (toc.length > 0) {
    title = `${toc[0].title} – ${config?.name} Docs`;
  }
  if (markdoc) {
    if (markdoc.frontmatter.title) {
      title = `${markdoc.frontmatter.title} – ${config?.name} Docs`;
    }
  }

  let description = null;
  if (markdoc) {
    if (markdoc.frontmatter.description) {
      description = markdoc.frontmatter.description;
    }
  }

  const validTocItems = toc.filter(
    (item: TableOfContentsItem) =>
      item.id && (item.level === 2 || item.level === 3),
  );

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="referrer" content="strict-origin" />
        <meta name="title" content={title} />
        {description && <meta name="description" content={description} />}
        <link rel="shortcut icon" href={faviconHref} />
        <link rel="icon" href={faviconHref} />
      </Head>
      <div className="page">
        <SideNav items={config?.navigation || []} />
        <main className="main">
          <div className="container">
            <div className="content">
              <div className="content-wrapper">
                <Component {...pageProps} />
              </div>
              <Footer />
            </div>
            {validTocItems.length > 1 ? (
              <TableOfContents toc={validTocItems} />
            ) : (
              <div className="toc-placeholder" />
            )}
          </div>
          {process.env.NEXT_PUBLIC_RELEASE_VERSION != null && (
            <VersionSelector />
          )}
        </main>
      </div>
      <style jsx>
        {`
          .page {
            position: fixed;
            display: flex;
            width: 100vw;
            flex-grow: 1;
          }
          .main {
            overflow: auto;
            flex-grow: 1;
            height: 100vh;
            font-size: 16px;
          }
          .container {
            position: relative;
            max-width: 90rem;
            margin: 0 auto;
            padding-right: 4rem;
            display: flex;
            justify-content: center;
            min-height: 100%;
          }
          .content {
            width: 640px;
            margin: 0 auto 1rem;
            padding-top: 48px;
            display: flex;
            flex-direction: column;
            min-height: calc(100vh - 48px - 96px - 4rem);
          }
          .content-wrapper {
            flex: 1 0 auto;
            padding-bottom: 2rem;
          }
          .content-wrapper :global(*:first-child) {
            margin-top: 0;
          }
          .toc-placeholder {
            flex: 0 0 250px; /* Same as TOC width */
          }
        `}
      </style>
    </>
  );
}
