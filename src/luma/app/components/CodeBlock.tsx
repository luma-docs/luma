import Prism from "prismjs";

import * as React from "react";

interface CodeBlockProps {
  children: React.ReactNode; // Typing children as ReactNode allows any valid React child
  "data-language": string; // Assuming language is a string
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
    <div className="code" aria-live="polite">
      <pre ref={ref} className={`language-${language}`}>
        {children}
      </pre>
      <style jsx>
        {`
          .code {
            position: relative;
          }

          /* Override Prism styles */
          .code :global(pre[class*="language-"]) {
            text-shadow: none;
            border-radius: 4px;
          }
        `}
      </style>
    </div>
  );
}
