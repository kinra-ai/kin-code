# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-26

### Breaking Changes

This release completes the rebranding from "Mistral Vibe" to "Kin Code". The following breaking changes require attention when upgrading:

- **Model name change**: Default model renamed from `mistral-vibe-cli-latest` to `kin-code-latest`. Update your `config.toml` if you reference the old name directly.
- **History file renamed**: Command history file renamed from `vibehistory` to `kinhistory`. Your history will start fresh.
- **Ignore file renamed**: Project ignore file renamed from `.vibeignore` to `.kinignore`. The old file is still supported for backward compatibility.
- **Constants renamed**: Internal constants `VIBE_STOP_EVENT_TAG` and `VIBE_WARNING_TAG` renamed to `KIN_STOP_EVENT_TAG` and `KIN_WARNING_TAG`.
- **ACP authentication ID**: Changed from `vibe-setup` to `kin-setup`.
- **Test mock environment variable**: Changed from `VIBE_MOCK_LLM_DATA` to `KIN_MOCK_LLM_DATA`.
- **Binary renamed**: `vibe-acp` binary renamed to `kin-acp`.

### Migration Guide

1. **Config file**: No changes needed for most users. The model alias `devstral-2` remains the same.
2. **Ignore file**: Rename `.vibeignore` to `.kinignore`, or keep both (backward compatible).
3. **Environment variables**: `KIN_HOME` and `VIBE_HOME` both work; `KIN_HOME` is preferred.
4. **ACP clients**: Update any direct references to `vibe-acp` binary to `kin-acp`.

### Added

- Added `VIBE.md` and `.vibe.md` to trustable filenames for backward compatibility
- Added backward compatibility for `.vibeignore` ignore files

### Changed

- Logger names updated to use `kin` prefix
- User agent string updated to `Kin-Code/{version}`
- All documentation updated with new naming

## [1.3.5] - 2026-01-12

### Fixed

- bash tool not discovered by vibe-acp

## [1.3.4] - 2026-01-07

### Fixed

- markup in blinking messages
- safety around Bash and AGENTS.md
- explicit permissions to GitHub Actions workflows
- improve render performance in long sessions

## [1.3.3] - 2025-12-26

### Fixed

- Fix config desyncing issues

## [1.3.2] - 2025-12-24

### Added

- User definable reasoning field

### Fixed

- Fix rendering issue with spinner

## [1.3.1] - 2025-12-24

### Fixed

- Fix crash when continuing conversation
- Fix Nix flake to not export python

## [1.3.0] - 2025-12-23

### Added

- agentskills.io support
- Reasoning support
- Native terminal theme support
- Issue templates for bug reports and feature requests
- Auto update zed extension on release creation

### Changed

- Improve ToolUI system with better rendering and organization
- Use pinned actions in CI workflows
- Remove 100k -> 200k tokens config migration

### Fixed

- Fix `-p` mode to auto-approve tool calls
- Fix crash when switching mode
- Fix some cases where clipboard copy didn't work

## [1.2.2] - 2025-12-22

### Fixed

- Remove dead code
- Fix artefacts automatically attached to the release
- Refactor agent post streaming

## [1.2.1] - 2025-12-18

### Fixed

- Improve error message when running in home dir
- Do not show trusted folder workflow in home dir

## [1.2.0] - 2025-12-18

### Added

- Modular mode system
- Trusted folder mechanism for local .vibe directories
- Document public setup for vibe-acp in zed, jetbrains and neovim
- `--version` flag

### Changed

- Improve UI based on feedback
- Remove unnecessary logging and flushing for better performance
- Update textual
- Update nix flake
- Automate binary attachment to GitHub releases

### Fixed

- Prevent segmentation fault on exit by shutting down thread pools
- Fix extra spacing with assistant message

## [1.1.3] - 2025-12-12

### Added

- Add more copy_to_clipboard methods to support all cases
- Add bindings to scroll chat history

### Changed

- Relax config to accept extra inputs
- Remove useless stats from assistant events
- Improve scroll actions while streaming
- Do not check for updates more than once a day
- Use PyPI in update notifier

### Fixed

- Fix tool permission handling for "allow always" option in ACP
- Fix security issue: prevent command injection in GitHub Action prompt handling
- Fix issues with vLLM

## [1.1.2] - 2025-12-11

### Changed

- add `terminal-auth` auth method to ACP agent only if the client supports it
- fix `user-agent` header when using Mistral backend, using SDK hook

## [1.1.1] - 2025-12-10

### Changed

- added `include_commit_signature` in `config.toml` to disable signing commits

## [1.1.0] - 2025-12-10

### Fixed

- fixed crash in some rare instances when copy-pasting

### Changed

- improved context length from 100k to 200k

## [1.0.6] - 2025-12-10

### Fixed

- add missing steps in bump_version script
- move `pytest-xdist` to dev dependencies
- take into account config for bash timeout

### Changed

- improve textual performance
- improve README:
  - improve windows installation instructions
  - update default system prompt reference
  - document MCP tool permission configuration

## [1.0.5] - 2025-12-10

### Fixed

- Fix streaming with OpenAI adapter

## [1.0.4] - 2025-12-09

### Changed

- Rename agent in distribution/zed/extension.toml to mistral-vibe

### Fixed

- Fix icon and description in distribution/zed/extension.toml

### Removed

- Remove .envrc file

## [1.0.3] - 2025-12-09

### Added

- Add LICENCE symlink in distribution/zed for compatibility with zed extension release process

## [1.0.2] - 2025-12-09

### Fixed

- Fix setup flow for vibe-acp builds

## [1.0.1] - 2025-12-09

### Fixed

- Fix update notification

## [1.0.0] - 2025-12-09

### Added

- Initial release
