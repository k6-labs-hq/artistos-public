# Pre-commit Hooks Setup

This repository uses [pre-commit](https://pre-commit.com/) to automatically enforce code quality standards before commits.

## Quick Start

```bash
# Install development dependencies
pip install -r dev-requirements.txt

# Install pre-commit hooks
pre-commit install

# Now hooks run automatically on git commit!
```

## What Gets Checked

Pre-commit automatically runs these checks before each commit:

- ✅ **Trailing whitespace removal** (fixes Windows editor issues)
- ✅ **End-of-file newlines** (ensures consistent file endings)
- ✅ **Black formatting** (Python code formatter, 100 char line length)
- ✅ **Ruff linting** (Fast Python linter with auto-fix)
- ✅ **YAML validation** (catches syntax errors in config files)
- ✅ **Large file detection** (prevents accidental commits of 500KB+ files)

## Manual Usage

```bash
# Run on all files (useful after pulling changes)
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run trailing-whitespace --all-files

# Skip hooks for emergency commits (use sparingly!)
git commit --no-verify -m "emergency fix"
```

## Updating Hooks

```bash
# Update to latest hook versions
pre-commit autoupdate

# Clean cache and reinstall
pre-commit clean
pre-commit install
```

## CI/CD Integration

Pre-commit hooks also run in GitHub Actions on every PR to ensure consistent code quality across all contributions.

## Configuration

- `.pre-commit-config.yaml` - Hook configuration
- `.editorconfig` - Editor settings (trim whitespace, indent style)
- `dev-requirements.txt` - Development tool versions

## Troubleshooting

**Hooks fail on commit:**
- Most hooks auto-fix issues, just `git add` the fixed files and commit again
- For persistent issues, check the output for specific error messages

**Hooks are slow:**
- First run downloads tools (1-2 minutes)
- Subsequent runs are cached and very fast (<5 seconds)

**Need to bypass hooks:**
```bash
git commit --no-verify -m "reason for bypass"
```
