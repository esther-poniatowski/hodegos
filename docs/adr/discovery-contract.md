---
tags:
  - decision
status: accepted
created: 2026-11-19
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Discovery contract decision
---
# Discovery contract

> [!QUESTION] Goal: how do the tools find their root and their configuration file, and how does a project add a place of its own?

The [tool boundaries audit](https://github.com/esther-poniatowski/geonexus/blob/main/docs/_audits/tool-boundaries/fixed-conventions.md) of Geonexus found two defects:

- nine tools implement the discovery of a configuration file each with code of their own;
- every tool searches `config/tools/`, a folder fixed by the house of the tools, but none of them searches the places that the wider ecosystem accepts.

On 2026-11-18, the researcher decided three points:

- one small library discovers the configuration of every tool, with the same mechanisms in Python and in TypeScript;
- the library searches the accepted places and a path declared by the consumer, so that Geonexus keeps `config/tools/`;
- the library is named Hodegos.

The present record settles the remaining choices. The [discovery specification](../specification.md) states the result normatively.

## Decision

**A declaration file of the project.** A project lists its extra folders once, in `hodegos.yml` at its root or in `.config/`. One line serves every tool, and the declaration is committed with the project. ^declaration-file

**Location, not parsing.** Hodegos returns the root and the file of the configuration, and each tool parses its own format. Hodegos returns the content of one place only, the table of `pyproject.toml`. Hodegos parses `pyproject.toml` anyway, since the presence of the table decides whether `pyproject.toml` is a place. ^location-only

**A convention fixed by the tool.** The name, the extensions and the stacking of a tool are values of the tool, passed to every discovery. Therefore, every extension and every extra folder comes from the tool or from the project, and Hodegos fixes none. ^tool-convention

**Two implementations on one set of cases.** The Python package and the TypeScript package run the same conformance cases. The TypeScript package reaches files through a port, so that a plugin of Obsidian supplies an adapter of its vault, and a separate entry supplies the adapter of Node. ^two-implementations

**Codes as the contract of errors.** Each error carries a code shared by both implementations, and the cases state an expected error by its code. The messages may differ. ^error-codes

**Lexical paths.** Both implementations normalize paths lexically and resolve no symbolic link, since the port of the TypeScript package reaches no link. ^lexical-paths

**YAML 1.1 for the declaration.** The TypeScript package parses the declaration as YAML 1.1, as PyYAML does, so that both implementations read the same values from a declaration. ^yaml-version

## Options compared

**Where a project declares its extra folders.** The criteria were a declaration committed with the project, one declaration for every tool, and an equal reach from both languages.

- *A declaration file* meets the three criteria. The declaration file adds one file to a project that uses an extra folder.
- *An environment variable* stays outside the repository, so every shell, editor and continuous integration job must set the variable. When the variable is missing, the search falls back to the accepted places and reports no error.
- *A table of `pyproject.toml`* is out of reach of the TypeScript package. Moreover, only a Python project holds a `pyproject.toml`.
- *A path of each tool in the declaration file* serves a configuration file named against the convention. No tool needs it once Kataskeue names its file after itself.

**Whether Hodegos parses the configuration.** Parsing would give every tool one reader of YAML and TOML. However, each tool validates its own format with its own errors, so a parser in Hodegos would hold the formats of all the tools. The location stays the shared concern.

## Constraints that decide the form

- **The tools are written in Python and in TypeScript.** Kataskeue and Ekphrasis read configuration files, and Ekphrasis runs inside Obsidian, also on mobile, and a mobile host offers no module of Node.
- **The logic is short.** The [tool roles](https://github.com/esther-poniatowski/geonexus/blob/main/docs/_decisions/tool-roles.md) of Geonexus admit two implementations of a logic of a few hundred lines when one set of cases binds both.
- **Two competing places stop the tool.** The convention of the tools already reports two configuration files rather than choosing one silently, and Hodegos keeps that rule for every place.

## Consequences

- Each tool replaces its own discovery with a call to Hodegos, and deletes its constants of places.
- Geonexus adds `hodegos.yml`, listing `config/tools`, before any tool drops `config/tools/` from its own places.
- The section on the root and the configuration file of the command-line conventions of Keystone refers to this specification instead of restating the places.
