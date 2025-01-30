import { useEffect } from 'react';
import { useRouter } from "next/router";
import { GetConfig } from './_app';

export default function Home() {
  const config = GetConfig();
  const router = useRouter();

  // Redirect index to first page in sidebar
  useEffect(() => {
    let destination = '/';

    if (config != null) {
      const first = config?.navigation[0];
      if ('path' in first) {
        destination = `/${first.path.slice(0, -3)}`;
      }
    }

    router.push(destination);
  }, [router, config]);
  
  return null;
}
