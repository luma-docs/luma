import React from 'react';
import Link from 'next/link';

interface Page {
  title: string;  // Name of the page
  path: string;  // Path to the page
}

interface Reference {
  ref: string;  // Name of the Python object
}

interface Section {
  section: string; // Name of the section
  contents: (Page | Reference)[];
}

export type NavigationItem = Page | Reference | Section;

interface SideNavProps {
  items: NavigationItem[];
}


export function SideNav({ items }: SideNavProps) {
  return (
    <nav className="sidenav">
      {items.map((item, itemIndex) => {
        if ('path' in item) {
          // Remove the '.md' extension from the path
          const href = `/${item.path.slice(0, -3)}`;                    // Add leading '/' to the href
          return (
            <li key={`page-${itemIndex}`}>
              <Link href={href}>{item.title}</Link>
            </li>
          );
        }

        if ('ref' in item) {
          return (
            <li key={`ref-${itemIndex}`}>
              <span>{item.ref}</span>
            </li>
          );
        }

        if ('section' in item) {
          return (
            <div key={`section-${itemIndex}`}>
              <span>{item.section}</span>
              <ul className="flex column">
                {item.contents.map((content, contentIndex) => {
                  if ('path' in content) {
                    // Remove the '.md' extension from the path
                    const href = `/${content.path.slice(0, -3)}`;                    // Add leading '/' to the href
                    return (
                      <li
                        key={`content-page-${itemIndex}-${contentIndex}`}
                      >
                        <Link href={href}>{content.title}</Link>
                      </li>
                    );
                  }
                  if ('ref' in content) {
                    const href = `/reference/${content.ref}`;
                    return (
                      <li key={`content-ref-${itemIndex}-${contentIndex}`}>
                        <Link href={href}>{content.ref}</Link>
                      </li>
                    );
                  }
                  return null; // Default case for type safety
                })}
              </ul>
            </div>
          );
        }
      })}
      <style jsx>
        {`
          nav {
            position: sticky;
            top: var(--top-nav-height);
            height: calc(100vh - var(--top-nav-height));
            flex: 0 0 auto;
            overflow-y: auto;
            padding: 2.5rem 2rem 2rem;
            border-right: 1px solid var(--border-color);
          }
          span {
            font-size: larger;
            font-weight: 500;
            padding: 0.5rem 0 0.5rem;
          }
          ul {
            padding: 0;
          }
          li {
            list-style: none;
            margin: 0;
          }
          li :global(a) {
            text-decoration: none;
          }
          li :global(a:hover),
          li.active :global(a) {
            text-decoration: underline;
          }
        `}
      </style>
    </nav>
  );
}
