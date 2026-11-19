// =================================================================================================
// ESLint Configuration for @hodegos/discovery (flat config)
//
// Sections
// --------
// - Type-aware TypeScript rules.
// - Boundaries: the domain modules import neither a host library nor Node, so that the package
//   runs in Obsidian on mobile; only the Node adapter, the tests and the tool configurations import
//   Node.
// =================================================================================================
import { fileURLToPath } from "node:url";
import tseslint from "typescript-eslint";

const rootDir = fileURLToPath(new URL("../..", import.meta.url));

export default tseslint.config(
  { ignores: ["dist/", "node_modules/"] },
  ...tseslint.configs.recommendedTypeChecked,
  {
    languageOptions: {
      parserOptions: { project: "./tsconfig.json", tsconfigRootDir: rootDir },
    },
    rules: {
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/explicit-module-boundary-types": "error",
    },
  },
  {
    files: ["src/**/*.ts"],
    ignores: ["src/node.ts"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            { group: ["node:*", "obsidian", "fs", "path"], message: "The package runs on mobile." },
          ],
        },
      ],
    },
  },
);
