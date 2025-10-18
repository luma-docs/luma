import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import styles from "./TableOfContents.module.css";

export interface TableOfContentsItem {
  id: string;
  title: string;
  level: number;
}

interface TableOfContentsProps {
  toc: TableOfContentsItem[];
}

export function TableOfContents({ toc }: TableOfContentsProps) {
  const [activeId, setActiveId] = React.useState("");
  const router = useRouter();

  React.useEffect(() => {
    const callback = (entries: IntersectionObserverEntry[]) => {
      // Get all entries that are currently visible
      const visibleEntries = entries.filter((entry) => entry.isIntersecting);

      if (visibleEntries.length === 0) {
        // If nothing is visible, don't change the state
        return;
      }

      // Get the first visible heading by its position in the document
      // (not the order it became visible)
      const sortedEntries = Array.from(visibleEntries).sort((a, b) => {
        const aPosition = a.target.getBoundingClientRect().top;
        const bPosition = b.target.getBoundingClientRect().top;
        return aPosition - bPosition;
      });

      const firstVisible = sortedEntries[0];
      setActiveId(`#${firstVisible.target.id}`);
    };

    // Create observer with smaller negative rootMargin to be more precise
    const observer = new IntersectionObserver(callback, {
      rootMargin: "-10% 0px -70% 0px",
    });

    // Reset state and re-observe headings
    const setupObserver = () => {
      // Clear existing state
      setActiveId("");

      // Observe all h2 and h3 headings
      const headings = document.querySelectorAll("h2, h3");
      headings.forEach((heading) => {
        if (heading.id) {
          observer.observe(heading);
        }
      });

      // Set initial active heading if we're already scrolled to one
      const visibleHeading = Array.from(headings).find((heading) => {
        const rect = heading.getBoundingClientRect();
        return rect.top >= 0 && rect.top <= window.innerHeight * 0.3;
      });

      if (visibleHeading?.id) {
        setActiveId(`#${visibleHeading.id}`);
      } else if (headings[0]?.id) {
        setActiveId(`#${headings[0].id}`);
      }
    };

    // Initial setup
    setupObserver();

    // Reset on route change
    router.events.on("routeChangeComplete", setupObserver);

    return () => {
      observer.disconnect();
      router.events.off("routeChangeComplete", setupObserver);
    };
  }, [router]);

  if (toc.length <= 1) {
    return null;
  }

  return (
    <nav className={styles.toc}>
      <div className={styles.header}>
        <div className={styles.iconWrapper}>
          <svg
            viewBox="0 0 24 24"
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.25"
            strokeLinecap="round"
            className={styles.icon}
          >
            <line x1="0" y1="10" x2="12" y2="10" />
            <line x1="0" y1="16" x2="16" y2="16" />
            <line x1="0" y1="22" x2="9" y2="22" />
          </svg>
        </div>
        <span className={styles.headerText}>On this page</span>
      </div>
      <ul className={styles.list}>
        {toc.map((item) => {
          const href = `#${item.id}`;
          const active = activeId === href;
          return (
            <li
              key={item.title}
              className={[
                styles.item,
                active ? styles.active : undefined,
                item.level === 3 ? styles.padded : undefined,
              ]
                .filter(Boolean)
                .join(" ")}
            >
              <Link href={href} className={styles.link}>
                {item.title}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
