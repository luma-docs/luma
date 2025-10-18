import * as React from "react";
import styles from "./Callout.module.css";

interface CalloutProps {
  title: string;
  children: React.ReactNode;
  type: CalloutType;
}

export enum CalloutType {
  Note = "note",
  Warning = "warning",
  Tip = "tip",
}

function getClassName(type: CalloutType) {
  switch (type) {
    case CalloutType.Note:
      return styles.info;
    case CalloutType.Warning:
      return styles.warning;
    case CalloutType.Tip:
      return styles.tip;
  }
}

export function Callout({ title, children, type }: CalloutProps) {
  return (
    <div className={`${styles.callout} ${getClassName(type)}`}>
      <strong>{title}</strong>
      <span>{children}</span>
    </div>
  );
}

export function Note({ children }: CalloutProps) {
  return (
    <Callout title="Note" type={CalloutType.Note}>
      {children}
    </Callout>
  );
}

export function Warning({ children }: CalloutProps) {
  return (
    <Callout title="Warning" type={CalloutType.Warning}>
      {children}
    </Callout>
  );
}

export function Tip({ children }: CalloutProps) {
  return (
    <Callout title="Tip" type={CalloutType.Tip}>
      {children}
    </Callout>
  );
}
