// Convention of one tool: its name, the extensions of its file, and how it searches its root. The
// table of `pyproject.toml` is a place of Python tools only, so this implementation does not read
// it.

import { DiscoveryError } from "./errors.js";

const TOOL_NAME = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const EXTENSION = /^[a-z0-9]+$/;

/** Convention of one tool, fixed by the tool and passed to every discovery. */
export interface Tool {
  /** Name of the tool, which names its file `<name>.<extension>` and its variable `<NAME>_ROOT`. */
  readonly name: string;
  /** Extensions admitted for the file, without their dot, such as `["yml"]`. */
  readonly extensions: readonly string[];
  /** Whether the tool stacks one file per folder, so that its root is the outermost folder. */
  readonly stacked?: boolean;
}

/** Reject a tool whose name or extensions depart from their form. */
export function checkTool(tool: Tool): void {
  if (!TOOL_NAME.test(tool.name)) {
    throw new DiscoveryError(
      "invalid-request",
      `tool name ${JSON.stringify(tool.name)}: write lowercase letters and digits, words joined by single hyphens`,
    );
  }
  if (tool.extensions.length === 0) {
    throw new DiscoveryError("invalid-request", `tool ${tool.name}: admit at least one extension`);
  }
  for (const extension of tool.extensions) {
    if (!EXTENSION.test(extension)) {
      throw new DiscoveryError(
        "invalid-request",
        `extension ${JSON.stringify(extension)} of tool ${tool.name}: write lowercase letters and digits, without the dot`,
      );
    }
  }
}

/** Return the name of the environment variable that names the root of the tool. */
export function rootVariable(tool: Tool): string {
  return `${tool.name.toUpperCase().replace(/-/g, "_")}_ROOT`;
}

/** Return the names of the configuration file, one per extension, in the order of the extensions. */
export function fileNames(tool: Tool): string[] {
  return tool.extensions.map((extension) => `${tool.name}.${extension}`);
}
