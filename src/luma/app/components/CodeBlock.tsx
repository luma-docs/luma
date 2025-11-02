import Prism from "prismjs";
import * as React from "react";

import styles from "./CodeBlock.module.css";

interface CodeBlockProps {
  children: React.ReactNode;
  "data-language": string;
}

export function CodeBlock({
  children,
  "data-language": language,
}: CodeBlockProps) {
  const ref = React.useRef(null);
  const isOutput = language === "output";

  React.useEffect(() => {
    if (ref.current && !isOutput) Prism.highlightElement(ref.current, false);
  }, [children, isOutput]);

  return (
    <div
      className={`${styles.code} ${isOutput ? styles.output : ""}`}
      aria-live="polite"
    >
      {isOutput && <div className={styles.label}>Output</div>}
      <pre ref={ref} className={isOutput ? "" : `language-${language}`}>
        {children}
      </pre>
    </div>
  );
}
