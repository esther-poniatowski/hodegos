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
3. the same file in each folder listed by the declaration of the folder;
4. the table `[tool.<name>]` of `pyproject.toml`, for a Python tool that reads it.

Two places holding a configuration are an error, so the order fixes only the order of the places named by that error. A file place holds a configuration when its path names a regular file, and a folder bearing the name of the file holds none. The table of `pyproject.toml` holds a configuration when `pyproject.toml` holds the table. A `pyproject.toml` that does not parse is an `invalid-pyproject`.

## The declaration of a project

A project lists the folders searched besides the accepted places in one declaration, `hodegos.yml`, at its root or in its subfolder `.config/`. The [schema of the declaration](../specs/schemas/configuration.schema.json) states its format. For example, a project keeping the configuration files in `config/tools/` declares: ^declaration

```yaml
_schema: hodegos:configuration@1
folders:
  - config/tools
```

- **Format.** The key `_schema` must hold `hodegos:configuration@1`. Any other key than `_schema` and `folders` is an error, so that a misspelled key fails.
- **Folders.** Each folder is a string naming a path below the folder of the declaration, with segments separated by `/`, without a segment `.` or `..`, and with at most a trailing `/`.
- **Scope.** A declaration lists folders of its own folder only. A folder below it is searched through its own declaration.
- **Parsing.** The declaration is parsed as YAML 1.1, as PyYAML parses it. Therefore, the value `yes` is a boolean in both implementations, and is rejected as a folder.

A declaration departing from these rules, or failing to parse, is an `invalid-declaration`. Two declarations of one folder are `competing-declarations`.

## The root

The root of a command is the first answer of: ^root

1. the root option, resolved against the current folder;
2. the variable `<NAME>_ROOT`, resolved against the current folder, when it is set and not empty;
3. the nearest folder holding a configuration of the tool in one of its places, from the current folder upward; for a stacked tool, the outermost such folder;
4. the current folder.

The search of step 3 stops at the nearest folder holding a configuration, and runs to the top of the file system for a stacked tool only. The search reads the declaration of each folder that it meets, and its `pyproject.toml` for a Python tool that reads it. Therefore, an invalid declaration or `pyproject.toml` met by the search stops the search with its error.

## The configuration

The configuration of a command is: ^configuration

1. the file named by the configuration option, resolved against the current folder; an option naming no file is a `missing-config`;
2. otherwise, the single place of the root holding a configuration; two places holding one are `competing-places`.

When no place holds a configuration, the outcome names none. Then, the tool decides whether to run on its defaults or to stop. For the table of `pyproject.toml`, the outcome carries the content of the table. For any other place, the tool parses the file itself.

## Paths

Every path of an outcome is absolute and normalized lexically. The normalization drops the empty and `.` segments, and each `..` segment removes the segment before it. Both implementations leave symbolic links unresolved, so that they name the same folders. ^paths

## Versions

The format of the declaration and the codes of the errors form the contract of Hodegos. A new version of the format is required by any change that makes a valid declaration invalid or that changes the expected outcome of a case. A format that no release has published may change in place. ^versions
