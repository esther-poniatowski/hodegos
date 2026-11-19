// Reader of the declaration of a project, `hodegos.yml`, which lists the folders searched besides
// the accepted places. YAML 1.1 is parsed, as PyYAML parses it, so that a value such as `yes` has
// one meaning in both implementations.

import { parse } from "yaml";

import { DiscoveryError } from "./errors.js";
import type { FileSystem } from "./file-system.js";
import { join } from "./paths.js";

/** Key holding the format identifier of the declaration. */
export const FORMAT_KEY = "_schema";
/** Format identifier of `hodegos.yml` read by this release. */
export const FORMAT = "hodegos:configuration@1";
/** Key listing the declared folders. */
export const FOLDERS_KEY = "folders";
/** Places of the declaration below a folder. At most one of them may hold a file. */
export const DECLARATION_PLACES: readonly string[] = ["hodegos.yml", ".config/hodegos.yml"];

/** Return the folders declared below `folder`, relative to it; empty without a declaration. */
export async function readDeclaredFolders(folder: string, files: FileSystem): Promise<string[]> {
  const found: string[] = [];
  for (const place of DECLARATION_PLACES) {
    const path = join(folder, place);
    if (await files.isFile(path)) found.push(path);
  }
  if (found.length > 1) {
    throw new DiscoveryError(
      "competing-declarations",
      `two declarations compete: ${found.join(" and ")}; keep one`,
    );
  }
  const [path] = found;
  return path === undefined ? [] : parseDeclaration(path, await files.readText(path));
}

function parseDeclaration(path: string, text: string): string[] {
  let raw: unknown;
  try {
    raw = parse(text, { version: "1.1" });
  } catch (error) {
    throw invalid(path, `cannot be read: ${String(error)}`);
  }
  if (typeof raw !== "object" || raw === null || Array.isArray(raw)) {
    throw invalid(path, "must hold a mapping");
  }
  const record = raw as Record<string, unknown>;
  const unknown = Object.keys(record)
    .filter((key) => key !== FORMAT_KEY && key !== FOLDERS_KEY)
    .sort();
  if (unknown.length > 0) {
    throw invalid(
      path,
      `declares unknown keys: ${unknown.join(", ")}; admitted keys: ${FORMAT_KEY}, ${FOLDERS_KEY}`,
    );
  }
  if (record[FORMAT_KEY] !== FORMAT) {
    throw invalid(path, `must declare ${FORMAT_KEY}: ${FORMAT}`);
  }
  const folders = record[FOLDERS_KEY];
  if (folders === undefined || folders === null) return [];
  if (!Array.isArray(folders)) {
    throw invalid(path, `${FOLDERS_KEY} must be a list of folders`);
  }
  return folders.map((item: unknown) => declaredFolder(path, item));
}

function declaredFolder(path: string, item: unknown): string {
  if (typeof item !== "string") {
    throw invalid(path, `declared folder ${JSON.stringify(item)} must be a string`);
  }
  const text = item.replace(/\/+$/, "");
  const segments = text.split("/");
  if (
    text === "" ||
    item.startsWith("/") ||
    text.includes("\\") ||
    segments.some((segment) => segment === "" || segment === "." || segment === "..")
  ) {
    throw invalid(
      path,
      `declared folder ${JSON.stringify(item)} must be a non-empty path below the folder of the declaration, with no segment '.' or '..'`,
    );
  }
  return text;
}

function invalid(path: string, reason: string): DiscoveryError {
  return new DiscoveryError("invalid-declaration", `${path}: ${reason}`);
}
