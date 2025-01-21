import React from 'react';
import Link from 'next/link';

export interface TableOfContentsItem {
  id: string;
  title: string;
  level: number;
}

interface TableOfContentsProps {
  toc: TableOfContentsItem[];
}

export function TableOfContents({ toc }: TableOfContentsProps) {
  console.log(toc);
  const items = toc.filter(
    (item) => item.id && (item.level === 2 || item.level === 3)
  );

  if (items.length <= 1) {
    return null;
  }

  return (
    <nav className="toc">
      <ul className="flex column">
        {items.map((item) => {
          const href = `#${item.id}`;
          const active =
            typeof window !== 'undefined' && window.location.hash === href;
          return (
            <li
              key={item.title}
              className={[
                active ? 'active' : undefined,
                item.level === 3 ? 'padded' : undefined,
              ]
                .filter(Boolean)
                .join(' ')}
            >
              <Link href={href}>
                {item.title}
              </Link>
            </li>
          );
        })}
      </ul>
      <style jsx>
        {`
          nav {
            position: sticky;
            flex: 0 0 auto;
            align-self: flex-start;
            margin-bottom: 1rem;
            margin-top: 2rem;
            padding: 0.5rem 0 0;
            border-left: 1px solid var(--border-color);
          }
          ul {
            margin: 0;
            padding: 0 1.5rem;
          }
          li {
            list-style-type: none;
            margin: 0 0 1rem;
          }
          li :global(a) {
            text-decoration: none;
          }
          li :global(a:hover),
          li.active :global(a) {
            text-decoration: underline;
          }
          li.padded {
            padding-left: 1rem;
          }
        `}
      </style>
    </nav>
  );
}
