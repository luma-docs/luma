import React from 'react';
import { useRouter } from 'next/router';
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
  const router = useRouter();

  return (
    <nav className="sidenav">
      <ul className="flex column">

        {items.map((item, itemIndex) => {
          if ('path' in item) {
            // Remove the '.md' extension from the path
            const href = `/${item.path.slice(0, -3)}`;
            const active = router.asPath === href;
            return (
              <li key={`page-${itemIndex}`} className={active ? 'active' : ''}>
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
              <div>
                <span style={{ paddingTop: itemIndex === 0 ? '0' : '1rem' }}>
                  {item.section}
                </span>
                <ul className="flex column">
                  {item.contents.map((content, contentIndex) => {
                    if ('path' in content) {
                      // Remove the '.md' extension from the path
                      const href = `/${content.path.slice(0, -3)}`;
                      const active = router.asPath === href;
                      return (
                        <li
                          key={`content-page-${itemIndex}-${contentIndex}`}
                          className={active ? 'active' : ''}
                        >
                          <Link href={href}>{content.title}</Link>
                        </li>
                      );
                    }
                    if ('ref' in content) {
                      const href = `/reference/${content.ref}`;
                      const active = router.asPath === href;
                      return (
                        <li
                          key={`content-ref-${itemIndex}-${contentIndex}`}
                          className={active ? 'active' : ''}
                        >
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
      </ul>

      <style jsx>
        {`
          nav {
            position: sticky;
            flex: 0 0 auto;
            overflow-y: auto;
            height: 100vh;
            padding: 1.5rem 2rem 2rem;
            border-right: 1px solid var(--border-color);
          }
          span {
            font-size: larger;
            font-weight: 500;
            padding: 1rem 0 0.5rem;
            display: inline-block; 
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
