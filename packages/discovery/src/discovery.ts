// Discovery of the root of a project and of the configuration of a tool, as the specification of
// Hodegos states it and as the Python implementation performs it, without the table of
// `pyproject.toml`.

import { DiscoveryError } from "./errors.js";
import type { FileSystem } from "./file-system.js";
import { join, normalize, resolvePath, selfAndParents } from "./paths.js";
import { checkTool, fileNames, rootVariable, type Tool } from "./tool.js";

/** Subfolders holding the file of a tool, searched after the folder itself and in this order. */
export const CONFIG_FOLDERS: readonly string[] = [".config", "config"];

/** The values of one invocation of a tool. */
export interface Invocation {
  /** Current folder, absolute. */
  readonly cwd: string;
  /**
   * Folder where the search of the root begins, relative to the current folder, such as the folder
   * of a source file; the current folder by default. The start changes the search only: the root
   * option, the configuration option and the variable keep resolving against the current folder.
   * The current folder also stays the root when the search finds none.
   */
  readonly start?: string | null;
  /** Value of the root option, relative to the current folder. */
  readonly root?: string | null;
  /** Value of the configuration option, relative to the current folder. */
  readonly config?: string | null;
  /** Environment variables; none by default. */
  readonly environ?: Readonly<Record<string, string | undefined>>;
}

/** Root of a command and the file of the configuration that it reads, or null without one. */
export interface Discovery {
  readonly root: string;
  readonly configuration: string | null;
}

/**
 * Resolve the root of a command and locate the configuration of the tool.
 *
 * The root is the first answer of: the root option; the variable `<NAME>_ROOT` when set and not
 * empty; the nearest folder, from the start upward, holding a configuration in one of its places,
 * or the outermost such folder for a stacked tool; the current folder. The configuration is the
 * file named by the configuration option, else the single place of the root holding one. The places
 * of a folder are the file `<name>.<extension>`, the same file in `.config/`, and the same file in
 * `config/`. Every file is read through `files`.
 */
export async function discover(
  tool: Tool,
  invocation: Invocation,
  files: FileSystem,
): Promise<Discovery> {
  checkTool(tool);
  const current = normalize(invocation.cwd);
  const root = await resolveRoot(tool, invocation, current, files);
  const config = invocation.config;
  if (config !== undefined && config !== null) {
    const given = resolvePath(current, config);
    if (!(await files.isFile(given))) {
      throw new DiscoveryError(
        "missing-config",
        `no configuration file at ${given}, named by option`,
      );
    }
    return { root, configuration: given };
  }
  const found = await locations(tool, root, files);
  if (found.length > 1) {
    throw new DiscoveryError(
      "competing-places",
      `two places hold a configuration of ${tool.name}: ${found.join(" and ")}; keep one`,
    );
  }
  return { root, configuration: found[0] ?? null };
}

async function resolveRoot(
  tool: Tool,
  invocation: Invocation,
  current: string,
  files: FileSystem,
): Promise<string> {
  const option = invocation.root;
  if (option !== undefined && option !== null) return resolvePath(current, option);
  const variable = invocation.environ?.[rootVariable(tool)] ?? "";
  if (variable !== "") return resolvePath(current, variable);
  const start = invocation.start;
  const begin = start === undefined || start === null ? current : resolvePath(current, start);
  let outermost: string | null = null;
  for (const folder of selfAndParents(begin)) {
    if ((await locations(tool, folder, files)).length > 0) {
      if (tool.stacked !== true) return folder;
      outermost = folder;
    }
  }
  return outermost ?? current;
}

async function locations(tool: Tool, folder: string, files: FileSystem): Promise<string[]> {
  const bases = [folder, ...CONFIG_FOLDERS.map((subfolder) => join(folder, subfolder))];
  const found: string[] = [];
  for (const base of bases) {
    for (const name of fileNames(tool)) {
      const path = join(base, name);
      if (await files.isFile(path)) found.push(path);
    }
  }
  return found;
}
