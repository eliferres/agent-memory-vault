# Changelog

## Unreleased

### Added
- Added a `pyproject.toml`, so `pipx install git+https://github.com/eliferres/agent-memory-vault` installs the linter as a `vault-lint` command, with `vault-lint --version`.

### Changed
- Reorganized the README: install and a first lint run come first, with the linter's real output, and the file table now sits in the section on how the vault is organized.

### Fixed
- Fixed a `[[link]]` to a name that two notes share passing the link check; it now fails as ambiguous and names every candidate note.

## [1.1.0](https://github.com/eliferres/agent-memory-vault/releases/tag/v1.1.0) - 2026-09-03

### Added
- Added macos-latest to the CI matrix alongside ubuntu-latest.

### Fixed
- Fixed the README's quoted operating contract to match CLAUDE.md byte for byte, after it had drifted three lines behind.
- Had INDEX name OPERATING-CONTRACT as the owner of the rules it summarizes.

## [1.0.0](https://github.com/eliferres/agent-memory-vault/releases/tag/v1.0.0) - 2026-08-31

First public release.
