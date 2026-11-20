# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The discovery of the root of a project and of the configuration file of a tool, in Python and in
  TypeScript, with the conformance cases that both implementations run.
- The declaration `hodegos.yml`, format `hodegos:configuration@1`, by which a project adds folders
  to the places searched.
- The option `start` of `discover`, in Python and in TypeScript: the search of the root begins in
  the folder named by `start`. The root option, the configuration option and the variable
  `<NAME>_ROOT` keep resolving against the current folder. The current folder also stays the root
  when the search finds none.
- The port `FileSystem` of the Python package, with its default `LocalFileSystem`, taken by
  `discover` as the argument `files`. A discovery reaches every path through the port.
- A second run of each conformance case, on a tree served from memory through the port.

### Changed

- **Breaking:** the subfolder `config/` is a place of the configuration of a tool, searched after
  `.config/` and before the table of `pyproject.toml`. Therefore, a folder holding
  `config/<name>.<extension>` is a root of the tool, and that file competes with the other places.

### Removed

- **Breaking:** the declaration `hodegos.yml` and its format `hodegos:configuration@1`. The schema
  `specs/schemas/configuration.schema.json` and the error codes `invalid-declaration` and
  `competing-declarations` are removed with the declaration. A configuration outside the places of
  a folder is named by the configuration option of the tool.
- **Breaking:** the module `hodegos.declaration`. The constant `DOT_CONFIG` of `hodegos.discovery`
  is replaced by `CONFIG_FOLDERS`.
- **Breaking:** the TypeScript exports `DECLARATION_PLACES` and `FORMAT`. The export `DOT_CONFIG` is
  replaced by `CONFIG_FOLDERS`.
- **Breaking:** the runtime dependency of the Python package on PyYAML, and of the TypeScript
  package on `yaml`. PyYAML and `yaml` now serve the tests only.
