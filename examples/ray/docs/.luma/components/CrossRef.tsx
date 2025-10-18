import Link from "next/link";
import { ReactNode } from "react";

interface CrossRefProps {
  href: string;
  children: ReactNode;
}
import qualname_to_path from "../data/apis.json";

export function CrossRef({ href, children }: CrossRefProps) {
  if (href in qualname_to_path) {
    href = qualname_to_path[href as keyof typeof qualname_to_path];
  }
  return <Link href={href}>{children}</Link>;
}

export default CrossRef;
