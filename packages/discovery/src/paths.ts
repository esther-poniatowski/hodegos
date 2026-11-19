// Absolute POSIX paths, normalized lexically as the Python implementation normalizes them, so that
// both implementations name the same folders without resolving symbolic links.

/** Return `path` resolved against the absolute folder `base`, normalized lexically. */
export function resolvePath(base: string, path: string): string {
  return normalize(path.startsWith("/") ? path : `${base}/${path}`);
}

/** Return an absolute path without empty segments, `.` segments, or resolvable `..` segments. */
export function normalize(path: string): string {
  if (!path.startsWith("/")) {
    throw new Error(`path ${path} must be absolute`);
  }
  const segments: string[] = [];
  for (const segment of path.split("/")) {
    if (segment === "" || segment === ".") continue;
    if (segment === "..") segments.pop();
    else segments.push(segment);
  }
  return `/${segments.join("/")}`;
}

/** Return the path of `name` below the folder `folder`. */
export function join(folder: string, name: string): string {
  return folder === "/" ? `/${name}` : `${folder}/${name}`;
}

/** Return `folder` followed by each of its ancestors, up to the top of the file system. */
export function selfAndParents(folder: string): string[] {
  const chain = [folder];
  let current = folder;
  while (current !== "/") {
    const cut = current.lastIndexOf("/");
    current = cut === 0 ? "/" : current.slice(0, cut);
    chain.push(current);
  }
  return chain;
}
