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
  const ref = React.useRef<HTMLPreElement>(null);
  const isOutput = language === "output";

  React.useEffect(() => {
    if (ref.current && !isOutput) {
      Prism.highlightElement(ref.current, false);
      const html = ref.current.innerHTML;

      const processedHtml = html
        // Match >>> (three consecutive operator spans with &gt;)
        .replace(
          /(<span class="token operator">&gt;&gt;<\/span><span class="token operator">&gt;<\/span>)/g,
          '<span class="prompt-symbol">$1</span>',
        );
      ref.current.innerHTML = processedHtml;
    }
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
