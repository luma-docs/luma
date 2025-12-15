import React from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import styles from "./SideNav.module.css";
import { SearchBar } from "./SearchBar";

import {
  Page,
  Reference,
  NavigationItem,
  Link as LinkType,
} from "../types/config";

interface SideNavProps {
  items: NavigationItem[];
}

function SideNavLink({
  item,
  key,
  addTopSpacing = false,
}: {
  item: Page | Reference | LinkType;
  key: string;
  addTopSpacing?: boolean;
}) {
  const router = useRouter();
  const currentPath = router.asPath.split("#")[0].split("?")[0];

  let href: string;
  let isActive: boolean;
  let linkText: string;
  if (item.type == "page") {
    href = `/${item.path.slice(0, -3)}`;
    isActive = currentPath === href;
    linkText = item.title;
  } else if (item.type == "link") {
    href = item.href;
    isActive = false;
    linkText = item.title;
  } else if (item.type == "reference") {
    href = `/${item.relative_path.slice(0, -3)}`;
    isActive = currentPath === href;
    linkText = item.title;
  } else {
    return null;
  }

  return (
    <li
      className={isActive ? styles.sideNavItemActive : ""}
      style={addTopSpacing ? { marginTop: "0.75rem" } : undefined}
    >
      <Link className={styles.sidenavItem} key={key} href={href}>
        {linkText}
      </Link>
    </li>
  );
}

export function SideNav({ items }: SideNavProps) {
  return (
    <nav className={styles.container}>
      <SearchBar />
      <ul className={`${styles.sidenav}`}>
        {items.map((item, itemIndex) => {
          if (item.type == "page" || item.type == "reference") {
            const previousItemIsSection =
              itemIndex > 0 && items[itemIndex - 1].type === "section";
            return (
              <SideNavLink
                item={item}
                key={`section-${itemIndex}`}
                addTopSpacing={previousItemIsSection}
              />
            );
          }
          if (item.type == "section") {
            return (
              <li key={`section-${itemIndex}`}>
                <span
                  className={styles.sectionTitle}
                  style={{ paddingTop: itemIndex === 0 ? "0" : "1rem" }}
                >
                  {item.title}
                </span>
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {item.contents.map((subitem, subitemIndex) => {
                    return (
                      <SideNavLink
                        item={subitem}
                        key={`section-${itemIndex}-content-${subitemIndex}`}
                      />
                    );
                  })}
                </ul>
              </li>
            );
          }
        })}
      </ul>
    </nav>
  );
}
