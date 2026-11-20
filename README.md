# hodegos

![Maintenance](https://img.shields.io/maintenance/yes/2026)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Finds the root of a project and the configuration file of a tool, in Python and in TypeScript.

---

## Overview

Before a command of a tool reads its inputs, the command needs two answers: the root of the project that it works on, and the file of its configuration. Hodegos gives both answers with one set of rules. The root comes from the root option, from the variable `<TOOL>_ROOT`, or from the nearest folder that holds a configuration of the tool. The configuration lies in one of the places accepted for every tool:

- `<tool>.<extension>` at the root;
- the same file in `.config/`;
- the same file in `config/`;
- the table `[tool.<tool>]` of `pyproject.toml`, for a Python tool.

A configuration kept in another folder is named by the configuration option of the tool. Each tool parses the file found by Hodegos.

### Motivation

Several tools implement the same search, each with code of its own, and the implementations differ in their details. Each tool also searches a folder fixed by the house of the tools, but none of the places accepted elsewhere. Hodegos replaces these implementations with one. Hodegos searches the accepted places instead of the folder of the house, and the accepted places include `config/`.

### Status

Pre-alpha. The Python package passes every [conformance case](specs/cases/discovery.yml), on the local file system and on a tree served from memory. The TypeScript package passes every case in both runs, except the cases on `pyproject.toml`, a place not read by the TypeScript package. The [discovery contract](docs/adr/discovery-contract.md) is accepted.

---

## Quick Start

A Python tool declares its convention once, then calls `discover` with the values of its options:

```python
from hodegos import Tool, discover

TOOL = Tool("anagraphe", ("yml",), pyproject=True)

found = discover(TOOL, root=root_option, config=config_option)
print(found.root, found.configuration)
```

The search of the root may begin elsewhere than the current folder, such as in the folder of a source file. The options keep resolving against the current folder:

```python
found = discover(TOOL, start=source.parent, root=root_option, config=config_option)
```

When a tool reads a state served from memory or from Git, the tool passes an adapter of the port `FileSystem`. The port answers `is_file` and `read_text`, and the local file system is its default:

```python
found = discover(TOOL, cwd=state_root, files=state_files)
```

A TypeScript tool passes its current folder and a port to the files of its host:

```typescript
import { discover } from "@hodegos/discovery";
import { nodeFileSystem } from "@hodegos/discovery/node";

const found = await discover(
  { name: "kataskeue", extensions: ["yml"] },
  { cwd: process.cwd(), root: rootOption, config: configOption, environ: process.env },
  nodeFileSystem,
);
```

The invocation also takes `start`: the search of the root begins in that folder.

---

## Documentation

The [documentation index](docs/_index.md) is the entry point.

---

## Contributing

Contributions follow the [contribution guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
