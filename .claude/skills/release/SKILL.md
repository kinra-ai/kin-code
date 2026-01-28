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

The `kinra-ai/homebrew-tap` repo (_reference/homebrew-tap) receives a `repository_dispatch` event and creates a PR to update the formula.

Merge the PR to complete the release:
```bash
GITHUB_TOKEN= gh pr merge <PR_NUMBER> --repo kinra-ai/homebrew-tap --squash --delete-branch
```

If the dispatch fails, manually trigger the Homebrew update:
```bash
GITHUB_TOKEN= gh workflow run update-formula.yml --repo kinra-ai/homebrew-tap -f version=X.Y.Z
```

## Important Notes

- **PyPI is immutable**: Once a version is uploaded, it cannot be replaced. Failed releases require a version bump.
- **Always run pre-commit first**: CI failures after PyPI upload mean you'll need to bump the version again.
- **GITHUB_TOKEN prefix**: Use `GITHUB_TOKEN=` before `gh` commands if the environment has a stale token.
- **Force-pushing tags doesn't re-trigger workflows**: If you need to fix a tag after release, you must delete and recreate the release (not just force-push the tag) to trigger the workflows again.
- **Binary attachment requires release event**: The `attach-to-release` job only runs when triggered by a release publish event. Manual `workflow_dispatch` triggers will build but not attach binaries.

## Fixing a Failed Release

If CI fails after the release is created but before PyPI upload:
1. Fix the issue and push to main
2. Delete the release: `GITHUB_TOKEN= gh release delete vX.Y.Z --repo kinra-ai/kin-code --yes`
3. Update the tag: `git tag -d vX.Y.Z && git tag vX.Y.Z && git push origin vX.Y.Z --force`
4. Recreate the release (this triggers all workflows properly)

If PyPI already uploaded successfully but binaries failed:
1. Fix the issue and push
2. Delete and recreate release (PyPI step will fail safely, binaries will attach)

## Monitoring

- Build status: https://github.com/kinra-ai/kin-code/actions/workflows/build-and-upload.yml
- PyPI status: https://github.com/kinra-ai/kin-code/actions/workflows/release.yml
- Homebrew PRs: https://github.com/kinra-ai/homebrew-tap/pulls
- PyPI package: https://pypi.org/project/kin-code/
