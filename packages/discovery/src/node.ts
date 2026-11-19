// Adapter of the file system of Node, the only module of the package that imports Node.

import { readFile, stat } from "node:fs/promises";

import type { FileSystem } from "./file-system.js";

/** File system of the local host, read through Node. */
export const nodeFileSystem: FileSystem = {
  async isFile(path: string): Promise<boolean> {
    try {
      return (await stat(path)).isFile();
    } catch {
      return false;
    }
  },
  async readText(path: string): Promise<string> {
    return readFile(path, "utf8");
  },
};
