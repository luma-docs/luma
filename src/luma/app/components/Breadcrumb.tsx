import * as React from "react";

interface BreadcrumbProps {
  section: string;
}

export function Breadcrumb({ section }: BreadcrumbProps) {
  return (
    <>
      <div className="breadcrumb">{section}</div>
      <style jsx>{`
        .breadcrumb {
          color: var(--color-link-primary);
          font-weight: var(--font-weight-semibold);
          margin-bottom: 0.5rem;
        }
      `}</style>
    </>
  );
}
