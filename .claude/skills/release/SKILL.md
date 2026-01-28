# Release Workflow

## Pre-Release Checklist

1. Run pre-commit locally to catch issues before CI:
   ```bash
   uv run pre-commit run --all-files
   ```

2. Update version in `pyproject.toml`

3. Update lockfile:
   ```bash
   uv lock
   ```

4. Commit and push to main

## Creating a Release

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
GITHUB_TOKEN= gh release create vX.Y.Z --repo kinra-ai/kin-code --title "vX.Y.Z" --notes "Release notes here"
```

## What Gets Triggered

On release publish:
- **build-and-upload.yml** - Builds binaries for all platforms (Linux, macOS, Windows x86_64/ARM64)
- **release.yml** - Publishes to PyPI and triggers Homebrew tap update

## Homebrew Tap

The `kinra-ai/homebrew-tap` repo (_reference/homebrew-tap) receives a `repository_dispatch` event and creates a PR to update the formula. Merge the PR to complete the release.

## Important Notes

- **PyPI is immutable**: Once a version is uploaded, it cannot be replaced. Failed releases require a version bump.
- **Always run pre-commit first**: CI failures after PyPI upload mean you'll need to bump the version again.
- **GITHUB_TOKEN prefix**: Use `GITHUB_TOKEN=` before `gh` commands if the environment has a stale token.

## Monitoring

- Build status: https://github.com/kinra-ai/kin-code/actions/workflows/build-and-upload.yml
- PyPI status: https://github.com/kinra-ai/kin-code/actions/workflows/release.yml
- Homebrew PRs: https://github.com/kinra-ai/homebrew-tap/pulls
- PyPI package: https://pypi.org/project/kin-code/
