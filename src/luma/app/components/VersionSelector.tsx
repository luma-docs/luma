import React, { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/router";
import styles from "./VersionSelector.module.css";

export default function VersionSelector() {
  const [versions, setVersions] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const package_name = process.env.NEXT_PUBLIC_PACKAGE_NAME;
  const currentVersion = router.basePath.substring(1) || "latest";

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        const response = await fetch(
          `https://api.luma-docs.org/dev/packages/${package_name}/versions`,
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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Don't show selector if there's only one or no versions
  if (versions.length <= 1) {
    return null;
  }

  return (
    <div ref={containerRef} className={styles.container}>
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
        <svg
          className={styles.chevron}
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {isOpen ? (
            <path
              d="M12 10L8 6L4 10"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ) : (
            <path
              d="M4 6L8 10L12 6"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
        </svg>
      </button>
    </div>
  );
}
