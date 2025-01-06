import Link from 'next/link';
import { ReactNode } from 'react';

interface CrossRefProps {
  href: string;
  children: ReactNode;
}

export function CrossRef({href, children}: CrossRefProps) {
    return (
        <Link href={href.includes("https://") || href.includes("http://") ? href : `reference/${href}`}>
          {children ? children : href}
        </Link>
      );
}

export default CrossRef;
