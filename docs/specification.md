---
tags: []
index: "[Hodegos documentation](docs/_index.md)"
aliases:
  - Discovery specification
---
# Discovery specification

> [!QUESTION] Goal: which root does a command of a tool take, and which configuration file does it read?

Both implementations of Hodegos follow this specification, and run its [conformance cases](../specs/cases/discovery.yml). A case states the expected outcome of one request, and an error is stated by its code. The [discovery contract](adr/discovery-contract.md) records why each rule holds.

## The convention of a tool

A tool fixes three values once, in its own code. ^tool

- **Name.** The name holds lowercase letters and digits, with words joined by single hyphens, such as `anagraphe` or `probe-tool`. The configuration file is named `<name>.<extension>`, and the variable of the root is `<NAME>_ROOT`, with each hyphen written as an underscore.
- **Extensions.** The tool admits at least one extension, written without its dot, such as `yml` or `toml`. Hodegos fixes no default extension.
- **Stacking.** A tool that stacks one configuration file per folder, such as Ktisma, is declared stacked.

A Python tool also declares whether the table `[tool.<name>]` of `pyproject.toml` is a place of its configuration. The TypeScript implementation does not read `pyproject.toml`, since `pyproject.toml` configures Python tools only.

A name or an extension of another form is an `invalid-request`.

## The places of a folder

Each folder holds the following places of the configuration of a tool, searched in this order: ^places

1. the file `<name>.<extension>` in the folder;
2. the same file in the subfolder `.config/`;
3. the same file in the subfolder `config/`;
4. the table `[tool.<name>]` of `pyproject.toml`, for a Python tool that reads it.

Two places holding a configuration are an error, so the order fixes only the order of the places named by that error. A file place holds a configuration when its path names a regular file, and a folder bearing the name of the file holds none. Therefore, a subfolder `config/` holding only the files of other tools holds no configuration of the tool. The table of `pyproject.toml` holds a configuration when `pyproject.toml` holds the table. A `pyproject.toml` that does not parse is an `invalid-pyproject`.

A configuration kept in another folder, such as `config/tools/`, is named by the configuration option of the tool. Hodegos reads no file that lists further places. ^other-folders

## The root

The root of a command is the first answer of: ^root

1. the root option, resolved against the current folder;
2. the variable `<NAME>_ROOT`, resolved against the current folder, when it is set and not empty;
3. the nearest folder holding a configuration of the tool in one of its places, searched upward from the start; for a stacked tool, the outermost such folder;
4. the current folder.

The start of the search is the current folder by default. A tool may give another start, such as the folder of a source file, and a relative start is resolved against the current folder. The start changes step 3 only. Steps 1, 2 and 4, and the configuration option, keep the current folder. ^start

The search of step 3 stops at the nearest folder holding a configuration, and runs to the top of the file system for a stacked tool only. For a Python tool that reads `pyproject.toml`, the search reads the `pyproject.toml` of each folder searched. Therefore, an invalid `pyproject.toml` met by the search stops the search with its error.

## The configuration

The configuration of a command is: ^configuration

1. the file named by the configuration option, resolved against the current folder; an option naming no file is a `missing-config`;
2. otherwise, the single place of the root holding a configuration; two places holding one are `competing-places`.

When no place holds a configuration, the outcome names none. Then, the tool decides whether to run on its defaults or to stop. For the table of `pyproject.toml`, the outcome carries the content of the table. For any other place, the tool parses the file itself.

## The files

Each implementation reads files through a port that answers two questions: whether a path names a regular file, and which text a file holds, decoded as UTF-8. A path that cannot be reached names no regular file. A discovery reaches every path through the port. The discovery asks whether each place and the file of the configuration option name a regular file, and reads the text of `pyproject.toml` only. Therefore, a tool can read a configuration inside a state served from memory or from Git, without copying the state to disk. ^files

- **Python.** `discover` takes the port as its optional argument `files`, and reads the local file system by default.
- **TypeScript.** `discover` takes the port as its third argument. The entry `@hodegos/discovery/node` supplies the adapter of Node, and a plugin of Obsidian supplies an adapter of its vault.

Only `pyproject.toml` needs the text of a file, so the TypeScript implementation never asks its port for a text. The TypeScript port keeps that question anyway, so that both ports have one shape. Each implementation runs the conformance cases twice: on the local file system, and on a tree served from memory through the port.

## Paths

Every path of an outcome is absolute and normalized lexically. The normalization drops the empty and `.` segments, and each `..` segment removes the segment before it. Both implementations leave symbolic links unresolved, so that they name the same folders. ^paths

## Versions

The contract of Hodegos consists of the places, the rules of the root and of the configuration, the codes of the errors, and the public interface of each package. The conformance cases state the rules of that contract. A breaking change alters the expected outcome of a case, or removes or changes incompatibly a member of a public interface. No release of Hodegos exists yet. Therefore, the contract changes in place, and the changelog records each breaking change. ^versions
