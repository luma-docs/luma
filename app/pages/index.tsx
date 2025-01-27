import { useEffect } from 'react';
import { useRouter } from "next/router";
import { getConfig } from './_app';

export default function Home() {
  const config = getConfig();

  let destination = '/';

  if (config != null) {
    const first = config?.navigation[0];
    if ('path' in first) {
      destination = `/${first.path.slice(0, -3)}`;
    }
  }

  const router = useRouter();

  // Redirect index to first page in sidebar
  useEffect(() => {
    router.push(destination);
  }, [router]);
  
  return null;
}
