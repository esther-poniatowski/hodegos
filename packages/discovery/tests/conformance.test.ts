// Run the conformance cases of `specs/cases/discovery.yml` against the TypeScript implementation,
// on real temporary folders through the Node adapter. A case whose request reads `pyproject.toml`
// is skipped, since the table of `pyproject.toml` is a place of Python tools only.

import { mkdir, mkdtemp, realpath, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

import { afterEach, describe, expect, it } from "vitest";
import { parse } from "yaml";

import { discover, DiscoveryError, ERROR_CODES } from "../src/index.js";
import { nodeFileSystem } from "../src/node.js";

interface Request {
  tool: string;
  extensions: string[];
  pyproject: boolean;
  stacked: boolean;
  cwd: string;
  root: string | null;
  config: string | null;
  environ: Record<string, string>;
}

interface Expect {
  error?: string;
  root?: string;
  configuration?: string | null;
  table?: unknown;
}

interface Case {
  name: string;
  description: string;
  tree: Record<string, string>;
  request?: Partial<Request>;
  expect: Expect;
}

interface CasesDocument {
  defaults: { request: Request };
  cases: Case[];
}

const casesFile = fileURLToPath(new URL("../../../specs/cases/discovery.yml", import.meta.url));
const document = parse(readFileSync(casesFile, "utf8")) as CasesDocument;

const tops: string[] = [];
afterEach(async () => {
  await Promise.all(tops.splice(0).map((top) => rm(top, { recursive: true, force: true })));
});

async function build(tree: Record<string, string>): Promise<string> {
  const top = await realpath(await mkdtemp(join(tmpdir(), "hodegos-")));
  tops.push(top);
  for (const [path, content] of Object.entries(tree)) {
    const target = join(top, path);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, content, "utf8");
  }
  return top;
}

describe("conformance", () => {
  for (const testCase of document.cases) {
    const request: Request = { ...document.defaults.request, ...testCase.request };
    const run = request.pyproject ? it.skip : it;
    run(testCase.name, async () => {
      const top = await build(testCase.tree);
      const cwd = join(top, request.cwd);
      await mkdir(cwd, { recursive: true });
      const outcome = discover(
        { name: request.tool, extensions: request.extensions, stacked: request.stacked },
        { cwd, root: request.root, config: request.config, environ: request.environ },
        nodeFileSystem,
      );
      if (testCase.expect.error !== undefined) {
        await expect(outcome).rejects.toBeInstanceOf(DiscoveryError);
        await expect(outcome).rejects.toMatchObject({ code: testCase.expect.error });
        return;
      }
      const found = await outcome;
      expect({
        root: relative(top, found.root),
        configuration: found.configuration === null ? null : relative(top, found.configuration),
        table: null,
      }).toEqual(testCase.expect);
    });
  }

  it("names every error code in a case", () => {
    const named = new Set(
      document.cases.flatMap((testCase) =>
        testCase.expect.error === undefined ? [] : [testCase.expect.error],
      ),
    );
    expect([...named].sort()).toEqual([...ERROR_CODES].sort());
  });
});
