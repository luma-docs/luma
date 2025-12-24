import React, { useState, useEffect, useRef, useMemo } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/router";
import MiniSearch from "minisearch";
import styles from "./SearchBar.module.css";

import searchIndexData from "../data/search-index.json";

interface SearchDocument {
  id: string;
  title: string;
  path: string;
  content: string;
  section: string;
  heading: string;
  headingLevel: number;
  type: string;
}

interface SearchResult {
  id: string;
  title: string;
  path: string;
  section: string;
  heading: string;
  headingLevel: number;
  type: string;
}

// Icon components
const PageIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M9 1H3.5C3.10218 1 2.72064 1.15804 2.43934 1.43934C2.15804 1.72064 2 2.10218 2 2.5V13.5C2 13.8978 2.15804 14.2794 2.43934 14.5607C2.72064 14.842 3.10218 15 3.5 15H12.5C12.8978 15 13.2794 14.842 13.5607 14.5607C13.842 14.2794 14 13.8978 14 13.5V6M9 1L14 6M9 1V6H14M5 8.5H11M5 11H11"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const HeadingIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M3 5.5H13M3 10.5H13M6.5 3L5.5 13M10.5 3L9.5 13"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const CodeIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M10 12L14 8L10 4M6 4L2 8L6 12"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

// Helper to get the icon for a result
const getResultIcon = (result: SearchResult) => {
  if (result.type === "reference") {
    return <CodeIcon />;
  } else if (result.heading) {
    return <HeadingIcon />;
  } else {
    return <PageIcon />;
  }
};

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Build search index (memoized)
  const searchIndex = useMemo(() => {
    const documents = searchIndexData as SearchDocument[];

    const miniSearch = new MiniSearch({
      fields: ["title", "heading", "content"],
      storeFields: [
        "title",
        "path",
        "section",
        "heading",
        "headingLevel",
        "type",
      ],
      searchOptions: {
        boost: { title: 3, heading: 2, content: 1 },
        fuzzy: 0.2,
        prefix: true,
      },
    });

    miniSearch.addAll(documents);
    return miniSearch;
  }, []);

  // Handle search query
  useEffect(() => {
    if (!searchIndex || !query.trim()) {
      setResults([]);
      setSelectedIndex(0);
      return;
    }

    try {
      const searchResults = searchIndex.search(query);
      const limitedResults = searchResults.slice(0, 8).map((result) => ({
        id: result.id,
        title: result.title,
        path: result.path,
        section: result.section,
        heading: result.heading,
        headingLevel: result.headingLevel,
        type: result.type,
      }));
      setResults(limitedResults);
      setSelectedIndex(0);
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    }
  }, [query, searchIndex]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) {
      if (e.key === "Escape") {
        closeModal();
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % results.length);
        break;
      case "ArrowUp":
        e.preventDefault();
        setSelectedIndex(
          (prev) => (prev - 1 + results.length) % results.length,
        );
        break;
      case "Enter":
        e.preventDefault();
        if (results[selectedIndex]) {
          navigateToResult(results[selectedIndex]);
        }
        break;
      case "Escape":
        e.preventDefault();
        closeModal();
        break;
    }
  };

  // Navigate to selected result
  const navigateToResult = (result: SearchResult) => {
    router.push(result.path);
    closeModal();
  };

  // Close modal and reset state
  const closeModal = () => {
    setIsOpen(false);
    setQuery("");
    setResults([]);
    setSelectedIndex(0);
  };

  // Handle "/" keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Only trigger if not already focused on an input
      if (
        event.key === "/" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA"
      ) {
        event.preventDefault();
        setIsOpen(true);
      }
    };

    document.addEventListener("keydown", handleKeyPress);
    return () => document.removeEventListener("keydown", handleKeyPress);
  }, []);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const modalContent = isOpen && (
    <div className={styles.modalOverlay} onClick={closeModal}>
      <div className={styles.modalPanel} onClick={(e) => e.stopPropagation()}>
        <div className={styles.inputWrapper}>
          <svg
            className={styles.searchIcon}
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667zM14 14l-2.9-2.9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <input
            ref={inputRef}
            type="text"
            className={styles.input}
            placeholder="Search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>

        {results.length > 0 && (
          <div ref={dropdownRef} className={styles.results}>
            {results.map((result, index) => (
              <button
                key={result.id}
                className={`${styles.result} ${
                  index === selectedIndex ? styles.resultSelected : ""
                }`}
                onClick={() => navigateToResult(result)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className={styles.resultIcon}>{getResultIcon(result)}</div>
                <div className={styles.resultContent}>
                  <div className={styles.resultTitle}>
                    {result.heading ? (
                      <>
                        <span className={styles.resultPageTitle}>
                          {result.title}
                        </span>
                        <span className={styles.resultHeadingSeparator}>
                          {" "}
                          ›{" "}
                        </span>
                        <span className={styles.resultHeading}>
                          {result.heading}
                        </span>
                      </>
                    ) : (
                      result.title
                    )}
                  </div>
                  {result.section && (
                    <div className={styles.resultSection}>{result.section}</div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {query.trim() && results.length === 0 && (
          <div className={styles.noResults}>No results found</div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Trigger button in sidenav */}
      <div className={styles.container}>
        <button
          className={styles.triggerButton}
          onClick={() => setIsOpen(true)}
        >
          <svg
            className={styles.searchIcon}
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667zM14 14l-2.9-2.9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className={styles.triggerText}>Search...</span>
          <kbd className={styles.keyboardShortcut}>/</kbd>
        </button>
      </div>

      {/* Portal modal to document.body */}
      {typeof document !== "undefined" &&
        modalContent &&
        createPortal(modalContent, document.body)}
    </>
  );
}
