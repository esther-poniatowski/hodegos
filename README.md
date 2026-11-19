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
- the table `[tool.<tool>]` of `pyproject.toml`, for a Python tool.

A project may add folders of its own in a declaration, `hodegos.yml`. Then, each tool parses its own file.

### Motivation

Several tools implement the same search, each with code of its own, and the implementations differ in their details. Each tool also searches a folder fixed by the house of the tools, but none of the places accepted elsewhere. Hodegos replaces these implementations with one. The folder of the house moves into the declaration of the project that uses it.

### Status

Pre-alpha. The Python package passes every [conformance case](specs/cases/discovery.yml). The TypeScript package passes every case except those on `pyproject.toml`, a place that the TypeScript package does not read. The [discovery contract](docs/adr/discovery-contract.md) is accepted.

---

## Quick Start

A Python tool declares its convention once, then calls `discover` with the values of its options:

```python
from hodegos import Tool, discover

TOOL = Tool("anagraphe", ("yml",), pyproject=True)

found = discover(TOOL, root=root_option, config=config_option)
print(found.root, found.configuration)
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

A project that keeps the configuration files of its tools in `config/tools/` declares that folder at its root, in `hodegos.yml`:

```yaml
_schema: hodegos:configuration@1
folders:
  - config/tools
```

---

## Documentation

The [documentation index](docs/_index.md) is the entry point.

---

## Contributing

Contributions follow the [contribution guidelines](CONTRIBUTING.md).

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
