import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/router";
import styles from "./VersionSelector.module.css";

export default function VersionSelector() {
  const [versions, setVersions] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const package_name = process.env.NEXT_PUBLIC_PACKAGE_NAME;
  const currentVersion = router.basePath.substring(1) || "latest";

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        const response = await fetch(
          `https://luma-projects.s3.us-east-1.amazonaws.com/${package_name}/versions.json`,
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            `API error: ${response.status} - ${errorData.error || response.statusText}`,
          );
        }

        const data = await response.json();
        setVersions(data);
      } catch (error) {
        console.error("Error fetching versions:", error);
      }
    };

    fetchVersions();
  }, [router.basePath, package_name]);

  const handleVersionSelect = useCallback((version: string) => {
    const targetPath = version === "latest" ? "/" : `/${version}`;
    window.location.href = window.location.origin + targetPath;
  }, []);

  const toggleDropdown = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  return (
    <div className={styles.container}>
      {isOpen && (
        <div className={styles.dropdown}>
          {versions
            .filter((version) => version !== currentVersion)
            .map((version) => (
              <button
                key={version}
                className={styles.versionOption}
                onClick={() => handleVersionSelect(version)}
              >
                {version}
              </button>
            ))}
        </div>
      )}
      <button
        className={isOpen ? styles.versionButtonActive : styles.versionButton}
        onClick={toggleDropdown}
      >
        {currentVersion}
        <div className={styles.listIcon}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>
    </div>
  );
}
