import React from "react";
import Link from "next/link";
import styles from "./TopNav.module.css";
import { Tab, NavigationItem } from "../types/config";

interface TopNavProps {
  tabs: Tab[];
  activeTabIndex: number;
}

function getFirstPagePath(items: NavigationItem[]): string | null {
  for (const item of items) {
    if (item.type === "page") {
      return `/${item.path.slice(0, -3)}`;
    } else if (item.type === "section") {
      const path = getFirstPagePath(item.contents);
      if (path) return path;
    } else if (item.type === "reference") {
      return `/${item.relative_path.slice(0, -3)}`;
    }
  }
  return null;
}

export function TopNav({ tabs, activeTabIndex }: TopNavProps) {
  return (
    <nav className={styles.container}>
      <div className={styles.tabList}>
        {tabs.map((tab, index) => {
          const firstPagePath = getFirstPagePath(tab.contents);
          const isActive = index === activeTabIndex;

          if (!firstPagePath) {
            return null;
          }

          return (
            <Link
              key={index}
              href={firstPagePath}
              className={`${styles.tab} ${isActive ? styles.tabActive : ""}`}
            >
              {tab.title}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
