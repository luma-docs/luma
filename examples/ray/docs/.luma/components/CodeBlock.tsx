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

  React.useEffect(() => {
    if (ref.current) Prism.highlightElement(ref.current, false);
  }, [children]);

  return (
    <div className={styles.code} aria-live="polite">
      <pre ref={ref} className={`language-${language}`}>
        {children}
      </pre>
    </div>
  );
}
