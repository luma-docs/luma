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
  headings: string;
  content: string;
  section: string;
}

interface SearchResult {
  id: string;
  title: string;
  path: string;
  section: string;
}

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
      fields: ["title", "headings", "content"],
      storeFields: ["title", "path", "section"],
      searchOptions: {
        boost: { title: 3, headings: 2, content: 1 },
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
                <div className={styles.resultTitle}>{result.title}</div>
                {result.section && (
                  <div className={styles.resultSection}>{result.section}</div>
                )}
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
