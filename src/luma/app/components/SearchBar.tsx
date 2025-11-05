import React, { useState, useEffect, useRef, useMemo } from "react";
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
  const [isFocused, setIsFocused] = useState(false);
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
        setIsOpen(false);
        inputRef.current?.blur();
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
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  // Navigate to selected result
  const navigateToResult = (result: SearchResult) => {
    router.push(result.path);
    setIsOpen(false);
    setQuery("");
    inputRef.current?.blur();
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
        inputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyPress);
    return () => document.removeEventListener("keydown", handleKeyPress);
  }, []);

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

  return (
    <div className={styles.container}>
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
          onFocus={() => {
            setIsOpen(true);
            setIsFocused(true);
          }}
          onBlur={() => setIsFocused(false)}
          onKeyDown={handleKeyDown}
        />
        {!isFocused && <kbd className={styles.keyboardShortcut}>/</kbd>}
      </div>

      {isOpen && results.length > 0 && (
        <div ref={dropdownRef} className={styles.dropdown}>
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
    </div>
  );
}
