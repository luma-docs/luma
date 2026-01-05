/**
 * Remove file extension from a path, handling both .md and .rst extensions.
 *
 * @param path - The file path with extension (e.g., "main.md" or "intro.rst")
 * @returns The path without the extension (e.g., "main" or "intro")
 */
export function stripFileExtension(path: string): string {
  if (path.endsWith(".md")) {
    return path.slice(0, -3);
  } else if (path.endsWith(".rst")) {
    return path.slice(0, -4);
  }
  return path;
}
