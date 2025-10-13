import React from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import styles from "./SideNav.module.css";

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
}: {
  item: Page | Reference | LinkType;
  key: string;
}) {
  const router = useRouter();

  let href: string;
  let isActive: boolean;
  let linkText: string;
  if (item.type == "page") {
    href = `/${item.path.slice(0, -3)}`;
    isActive = router.asPath === href;
    linkText = item.title;
  } else if (item.type == "link") {
    href = item.href;
    isActive = false;
    linkText = item.title;
  } else if (item.type == "reference") {
    const safe = item.title.toLowerCase().replace(/ /g, "-");
    href = `/${safe}`;
    isActive = router.asPath === href;
    linkText = item.title;
  } else {
    return null;
  }

  return (
    <li className={isActive ? styles.sideNavItemActive : ""}>
      <Link className={styles.sidenavItem} key={key} href={href}>
        {linkText}
      </Link>
    </li>
  );
}

export function SideNav({ items }: SideNavProps) {
  return (
    <nav className={styles.container}>
      <ul className={`${styles.sidenav}`}>
        {items.map((item, itemIndex) => {
          if (item.type == "page" || item.type == "reference") {
            return <SideNavLink item={item} key={`section-${itemIndex}`} />;
          }
          if (item.type == "section") {
            return (
              <div key={`section-${itemIndex}`}>
                <span
                  className={styles.sectionTitle}
                  style={{ paddingTop: itemIndex === 0 ? "0" : "1rem" }}
                >
                  {item.title}
                </span>
                {item.contents.map((subitem, subitemIndex) => {
                  return (
                    <SideNavLink
                      item={subitem}
                      key={`section-${itemIndex}-content-${subitemIndex}`}
                    />
                  );
                })}
              </div>
            );
          }
        })}
      </ul>
    </nav>
  );
}
