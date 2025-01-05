import { useRouter } from 'next/router'
import { FuncReference } from '../../components';

export default function Page() {
    const router = useRouter();
    const name = Array.isArray(router.query.name)
        ? router.query.name[0] // Use the first element if it's an array
        : router.query.name; // Keep it as is if it's a string

    if (!name) {
        return null; // Render nothing if `name` is null or undefined
    }

    return <FuncReference name={name} />;
}
