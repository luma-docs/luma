import * as React from "react";
import styles from "./Tabs.module.css";

interface TabProps {
  name: string;
  children: React.ReactNode;
}

export function Tab({ children }: TabProps) {
  return <>{children}</>;
}

interface TabsProps {
  children: React.ReactNode;
}

export function Tabs({ children }: TabsProps) {
  const [activeTab, setActiveTab] = React.useState(0);

  // Extract tab information from children
  const tabs = React.Children.toArray(children).filter(
    (child): child is React.ReactElement<TabProps> =>
      React.isValidElement(child) && child.type === Tab,
  );

  if (tabs.length === 0) {
    return null;
  }

  return (
    <div className={styles.tabs}>
      <div className={styles.tabButtons}>
        {tabs.map((tab, index) => (
          <button
            key={index}
            className={`${styles.tabButton} ${
              activeTab === index ? styles.active : ""
            }`}
            onClick={() => setActiveTab(index)}
          >
            {tab.props.name}
          </button>
        ))}
      </div>
      <div className={styles.tabContent}>{tabs[activeTab]}</div>
    </div>
  );
}
