---
tags:
  - decision
status: accepted
created: 2026-11-19
revised: 2026-11-20
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Discovery contract decision
---
# Discovery contract

> [!QUESTION] Goal: how do the tools find their root and their configuration file, and where may a project keep that file?

The [tool boundaries audit](https://github.com/esther-poniatowski/geonexus/blob/main/docs/_audits/tool-boundaries/fixed-conventions.md) of Geonexus found two defects:

- nine tools implement the discovery of a configuration file each with code of their own;
- every tool searches `config/tools/`, a folder fixed by the house of the tools, but none of them searches the places that the wider ecosystem accepts.

On 2026-11-18, the researcher decided three points:

- one small library discovers the configuration of every tool, with the same mechanisms in Python and in TypeScript;
- the library searches the accepted places and a path declared by the consumer, so that Geonexus keeps `config/tools/`;
- the library is named Hodegos.

On 2026-11-20, the researcher replaced the second point. The library searches the accepted places only, and `config/` becomes one of them. When a project keeps a configuration elsewhere, the project names the file with the configuration option of each tool. The [amendment of 2026-11-20](discovery-contract.md#^amendment-2026-11-20) records the decisions of that day.

The present record settles the remaining choices. The [discovery specification](../specification.md) states the result normatively.

## Decision

**Accepted places only.** The places of a folder are the four places listed by the [discovery specification](../specification.md#^places), `config/` among them. A configuration kept elsewhere is named by the configuration option of the tool. Therefore, the location policy of a tool depends on no file of Hodegos shared with the other tools. ^accepted-places

**Location, not parsing.** Hodegos returns the root and the file of the configuration, and each tool parses its own format. Hodegos returns the content of one place only, the table of `pyproject.toml`. Hodegos parses `pyproject.toml` anyway, since the presence of the table decides whether `pyproject.toml` is a place. ^location-only

**A convention fixed by the tool.** The name, the extensions and the stacking of a tool are values of the tool, passed to every discovery. Therefore, every extension comes from the tool, and Hodegos fixes none. ^tool-convention

**Two implementations on one set of cases.** The Python package and the TypeScript package run the same conformance cases. Both packages read files through a port of one shape. In TypeScript, a plugin of Obsidian supplies an adapter of its vault, and a separate entry supplies the adapter of Node. In Python, a tool supplies an adapter of a state served from memory or from Git, and the local file system is the default. ^two-implementations

**A start separate from the current folder.** The search of the root begins at a start chosen by the tool, the current folder by default. The root option, the configuration option and the variable `<NAME>_ROOT` keep resolving against the current folder. The current folder also stays the root when the search finds none. Therefore, a tool such as Ktisma can search from the folder of a source file, and resolve the values of its command line against the current folder. ^search-start

**Codes as the contract of errors.** Each error carries a code shared by both implementations, and the cases state an expected error by its code. The messages may differ. ^error-codes

**Lexical paths.** Both implementations normalize paths lexically and leave symbolic links unresolved, since the ports expose no link. ^lexical-paths

## Amendment of 2026-11-20

On 2026-11-20, the researcher took four decisions. The four decisions replace part of the decision of 2026-11-18: ^amendment-2026-11-20

1. **No declaration of the project.** The declaration `hodegos.yml` coupled the location policy of every tool to one shared file. An invalid declaration stopped every tool of a project, and a consumer had to learn a file of Hodegos. The declaration is removed, together with each artifact that served it only: its schema, its cases, and its error codes `invalid-declaration` and `competing-declarations`.
2. **`config/` is an accepted place.** The subfolder `config/` is searched after `.config/` and before the table of `pyproject.toml`. Two places holding a configuration remain `competing-places`.
3. **A port of the files in Python.** `discover` takes an optional reader of files, the local file system by default. Therefore, a tool reads a configuration inside a state served from memory or from Git, without copying the state to disk.
4. **A start of the search separate from the current folder**, in both implementations, as the decision [`^search-start`](discovery-contract.md#^search-start) states.

The amendment replaced two decisions of 2026-11-18. Their text, as the record stated it, follows.

**A declaration file of the project.** A project lists its extra folders once, in `hodegos.yml` at its root or in `.config/`. One line serves every tool, and the declaration is committed with the project. ^declaration-file

**YAML 1.1 for the declaration.** The TypeScript package parses the declaration as YAML 1.1, as PyYAML does, so that both implementations read the same values from a declaration. ^yaml-version

The amendment also revised three decisions. The decision `^tool-convention` no longer names an extra folder of the project. The decisions `^two-implementations` and `^lexical-paths` name a port in both packages, instead of a port of the TypeScript package only. On 2026-11-18, the record also required Geonexus to add `hodegos.yml`. That consequence was removed with the declaration.

## Options compared

**Where a project keeps a configuration outside the places of a folder.** On 2026-11-18, the criteria were a declaration committed with the project, one declaration for every tool, and an equal reach from both languages. On 2026-11-20, the criteria became three:

- the location policy of a tool depends on no file of Hodegos shared with the other tools;
- a consumer learns no file of Hodegos;
- both languages reach the answer equally.

The criterion of a declaration committed with the project was dropped. The chosen option meets that criterion only for a project that moves its files into `config/`. Four options were weighed against the criteria of 2026-11-20.

- *The configuration option of each tool*, with `config/` among the accepted places, meets the three criteria. When a project moves its files into `config/`, the files stay committed with the project. When a project keeps its files in another folder, such as `config/tools/`, the project passes the configuration option at each invocation of each tool. That option is committed only where the invocations are.
- *A declaration file*, `hodegos.yml`, met the criteria of 2026-11-18, since one committed line served every tool. The declaration file lost on 2026-11-20 for three reasons. First, the declaration coupled the location policy of every tool to one shared file. Second, an invalid declaration stopped every tool of the project. Third, a consumer had to learn a file of Hodegos besides the file of its tool. A path of each tool in the declaration file served a configuration file named against the convention, and no tool needed it once Kataskeue named its file after itself. That option was removed with the declaration file.
- *An environment variable of each tool*, such as `<NAME>_CONFIG`, meets the three criteria. However, the variable stays outside the repository, so every shell, editor and continuous integration job must set it. When the variable is missing, the search falls back to the accepted places and reports no error.
- *A table of `pyproject.toml`* fails the third criterion, since the TypeScript package does not read `pyproject.toml`. Moreover, only a Python project holds a `pyproject.toml`.

The table of `pyproject.toml` stays an accepted place, although an invalid `pyproject.toml` stops every Python tool that reads it. That shared failure exists outside Hodegos already, since the build of a Python project reads the same `pyproject.toml`.

The declaration file would win again if three conditions held together:

- several tools of one project keep their files in one folder outside the accepted places, and the project cannot move the files;
- the invocations of those tools cannot carry the configuration option, as when an editor or a hook runs a tool without arguments;
- no variable can be set in the environment of those invocations.

In that case, the declaration file would be the only route that works, at the cost of a shared failure and of a file of Hodegos to learn.

**Where the search of the root begins.** A tool could pass the folder of a source file as the current folder instead of a start. However, the root option, the configuration option and the variable would resolve against the folder of the source file in that case, and the fallback root would become that folder. A separate start changes the search only.

**How the Python package reaches the files of a state.** A tool could copy the files of a state into a temporary folder before each discovery, as the record resolver of Anagraphe does. However, the copy must know the places of Hodegos in advance, and it writes to disk on each read. A port lets Hodegos ask for the places itself.

**Whether Hodegos parses the configuration.** Parsing would give every tool one reader of YAML and TOML. However, each tool validates its own format with its own errors, so a parser in Hodegos would hold the formats of all the tools. The location stays the shared concern.

## Constraints that decide the form

- **The tools are written in Python and in TypeScript.** Kataskeue and Ekphrasis read configuration files, and Ekphrasis runs inside Obsidian, also on mobile, and a mobile host offers no module of Node.
- **The logic is short.** The [tool roles](https://github.com/esther-poniatowski/geonexus/blob/main/docs/_decisions/tool-roles.md) of Geonexus admit two implementations of a logic of a few hundred lines when one set of cases binds both.
- **Two competing places stop the tool.** The convention of the tools already reports two configuration files rather than choosing one silently, and Hodegos keeps that rule for every place.

## Consequences

- Each tool replaces its own discovery with a call to Hodegos, and deletes its constants of places.
- When a project keeps the files of its tools in another folder, the project moves each file into an accepted place, such as `config/`, or names each file with the configuration option of its tool. Geonexus keeps `config/tools/`, removes its `hodegos.yml`, and names each file by the configuration option of its tool.
- The record resolver of Anagraphe reads states served from Git. Such a tool passes an adapter of the port to `discover`, instead of copying the state to disk.
- The section on the root and the configuration file of the command-line conventions of Keystone refers to this specification instead of restating the places.
