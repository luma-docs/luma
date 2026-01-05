import React from "react";
import Link from "next/link";
import styles from "./TopNav.module.css";
import { Tab, NavigationItem } from "../types/config";
import { stripFileExtension } from "../lib/utils";

interface TopNavProps {
  tabs: Tab[];
  activeTabIndex: number;
}

function getFirstPagePath(items: NavigationItem[]): string | null {
  for (const item of items) {
    if (item.type === "page") {
      return `/${stripFileExtension(item.path)}`;
    } else if (item.type === "section") {
      const path = getFirstPagePath(item.contents);
      if (path) return path;
    } else if (item.type === "reference") {
      return `/${stripFileExtension(item.relative_path)}`;
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
