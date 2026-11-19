// Port to the files of the host. Node supplies it through `@hodegos/discovery/node`; a plugin of
// Obsidian supplies an adapter of its vault, which keeps the domain modules free of Node.

/** Read access to the files of the host, addressed by absolute POSIX paths. */
export interface FileSystem {
  /** Whether `path` names a regular file; false for a folder or an absent path. */
  isFile(path: string): Promise<boolean>;
  /** Return the content of the file at `path`, decoded as UTF-8. */
  readText(path: string): Promise<string>;
}
