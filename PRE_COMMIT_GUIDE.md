# Pre-Commit Hooks Guide

## What is Pre-Commit?

Pre-commit is a framework that runs automated checks **before** you commit code. It catches issues early, automatically fixes many problems, and ensures consistent code quality across your team.

## What's Already Set Up

Pre-commit hooks are now **installed and active** in this repository! Every time you run `git commit`, the following checks will automatically run:

### 1. File Hygiene Hooks
- **Trailing Whitespace** - Removes unnecessary spaces at end of lines
- **End of File Fixer** - Ensures files end with a newline
- **Case Conflict Checker** - Prevents filename conflicts across operating systems
- **JSON/YAML/TOML Validators** - Catches syntax errors in config files
- **Large File Checker** - Prevents committing files over 500KB
- **Merge Conflict Checker** - Catches unresolved merge markers (<<<<<<)
- **Branch Protection** - Prevents direct commits to main/master

### 2. Python Code Quality
- **Ruff Linter** - Checks for code quality issues (unused imports, undefined variables, etc.)
- **Ruff Formatter** - Auto-formats code (like Black)
- **MyPy** - Type checking for Python type hints
- **Bandit** - Security vulnerability scanning

### 3. Commit Message Validation
- **Conventional Commits** - Ensures commit messages follow standard format

## How It Works

When you run `git commit`, pre-commit will:

1. **Check staged files** against all configured hooks
2. **Automatically fix** issues when possible (formatting, trailing whitespace, etc.)
3. **Show errors** for issues it can't auto-fix
4. **Stop the commit** if any hook fails
5. **Let you review changes** and try again

## Installation (Already Done!)

Pre-commit is already installed in this repository. If you're setting up on a new machine, run:

```bash
# Install dev dependencies (includes pre-commit)
uv pip install --system -e ".[dev]"

# Install the git hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## Usage Examples

### Example 1: Successful Commit

```bash
# Make some changes
echo "print('Hello World')" > src/project1/hello.py

# Stage the file
git add src/project1/hello.py

# Commit with proper message format
git commit -m "feat: add hello world script"
```

**What happens:**
```
Remove trailing whitespace........Passed
Fix end of files.................Passed
Check for case conflicts.........Passed
Check JSON syntax................Passed
Check YAML syntax................Passed
Check TOML syntax................Passed
Check for large files............Passed
Check for merge conflicts........Passed
Prevent commits to main/master...Passed
Ruff linter......................Passed
Ruff formatter...................Passed
MyPy type checker................Passed
Bandit security checker..........Passed
Check commit message format......Passed

[master abc1234] feat: add hello world script
 1 file changed, 1 insertion(+)
```

### Example 2: Auto-Fix (Formatting Issues)

```bash
# Create a file with formatting issues
cat > src/project1/messy.py << 'EOF'
import sys
import os


def  bad_function(  ):
    x=1+2
    return    x
EOF

# Stage and commit
git add src/project1/messy.py
git commit -m "feat: add messy code"
```

**What happens:**
```
Remove trailing whitespace........Passed
Fix end of files.................Fixed
...
Ruff linter......................Fixed
Ruff formatter...................Fixed
...
```

**Result:** Pre-commit auto-fixes the formatting, but the commit **fails** so you can review the fixes:

```bash
# Review what was fixed
git diff src/project1/messy.py

# Re-stage the fixed file
git add src/project1/messy.py

# Try commit again
git commit -m "feat: add messy code"
# Now it passes!
```

### Example 3: Bad Commit Message

```bash
git add some_file.py
git commit -m "updated stuff"
```

**What happens:**
```
Check commit message format......Failed
- hook id: conventional-pre-commit
- exit code: 1

Commit message does not follow Conventional Commits format.
Expected: type(scope): description
Examples:
  - feat: add new feature
  - fix: resolve login bug
  - docs: update README

Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
```

**Fix it:**
```bash
# Use proper format
git commit -m "feat: update user authentication"
```

### Example 4: Security Issue Detected

```bash
# Create file with security issue
cat > src/project1/insecure.py << 'EOF'
import subprocess

def run_command(user_input):
    subprocess.call(user_input, shell=True)  # Security risk!
EOF

git add src/project1/insecure.py
git commit -m "feat: add command runner"
```

**What happens:**
```
Bandit security checker..........Failed
- hook id: bandit
- exit code: 1

Issue: [B602:subprocess_popen_with_shell_equals_true] subprocess call with shell=True identified
Severity: High   Confidence: High
Location: src/project1/insecure.py:4
```

**Fix it:** Rewrite the code to be secure:
```python
import subprocess

def run_command(user_input):
    # Safe: shell=False and use list instead of string
    subprocess.call(user_input.split(), shell=False)
```

## Commit Message Format

All commit messages must follow **Conventional Commits** format:

```
type(optional-scope): description

[optional body]

[optional footer]
```

### Allowed Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add user login` |
| `fix` | Bug fix | `fix: resolve null pointer error` |
| `docs` | Documentation only | `docs: update installation guide` |
| `style` | Code style (formatting, semicolons) | `style: fix indentation` |
| `refactor` | Code restructuring | `refactor: simplify auth logic` |
| `perf` | Performance improvement | `perf: optimize database queries` |
| `test` | Add or update tests | `test: add user model tests` |
| `build` | Build system or dependencies | `build: update to Python 3.12` |
| `ci` | CI/CD changes | `ci: add pre-commit workflow` |
| `chore` | Other changes | `chore: update .gitignore` |
| `revert` | Revert previous commit | `revert: undo feature X` |

### Examples

```bash
# Good commit messages
git commit -m "feat: add user authentication system"
git commit -m "fix: resolve login redirect bug"
git commit -m "docs: add API documentation"
git commit -m "refactor(auth): simplify token validation"

# Bad commit messages (will be rejected)
git commit -m "updated files"           # No type
git commit -m "Add new feature"         # Wrong capitalization
git commit -m "feature: add login"      # Wrong type (use 'feat')
```

## Running Hooks Manually

### Run on All Files

Test all hooks on every file in your repository:

```bash
pre-commit run --all-files
```

**When to use:**
- After updating `.pre-commit-config.yaml`
- To check entire codebase
- Before making a pull request

### Run on Specific Files

```bash
pre-commit run --files src/project1/myfile.py
```

### Run Specific Hook

```bash
# Only run ruff
pre-commit run ruff --all-files

# Only check commit message format
pre-commit run conventional-pre-commit --hook-stage commit-msg
```

## Bypassing Hooks (Use Sparingly!)

Sometimes you need to commit without running hooks (emergencies only):

```bash
git commit --no-verify -m "fix: emergency hotfix"
```

**Warning:** Only use `--no-verify` when absolutely necessary. Your code will skip all quality checks!

## Updating Hooks

Pre-commit hooks are versioned. To update to latest versions:

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Then test the updates
pre-commit run --all-files
```

## Configuration Files

### `.pre-commit-config.yaml`
Defines which hooks to run and their configuration.

**Key sections:**
- `repos` - List of hook repositories
- `hooks` - Specific hooks to enable
- `args` - Arguments passed to each hook

### `pyproject.toml`
Contains tool-specific configurations:

```toml
[tool.ruff]
line-length = 100      # Max line length
target-version = "py312"

[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]       # Skip assert warnings

[tool.mypy]
ignore_missing_imports = true
show_error_codes = true
```

## Troubleshooting

### Hook Fails But You Don't Know Why

```bash
# Run with verbose output
pre-commit run --all-files --verbose
```

### Hooks Not Running

```bash
# Check if hooks are installed
ls -la .git/hooks/

# Should see: pre-commit and commit-msg files

# Reinstall if missing
pre-commit install
pre-commit install --hook-type commit-msg
```

### Clean Hook Cache

If hooks behave strangely, clean the cache:

```bash
pre-commit clean
pre-commit install
```

### Skip Specific Hook Temporarily

Add to `.pre-commit-config.yaml`:

```yaml
- id: mypy
  name: MyPy type checker
  exclude: ^src/legacy/  # Skip legacy code
```

## Hook Execution Order

Hooks run in this order:

1. **File hygiene** (trailing whitespace, etc.)
2. **Formatting** (ruff-format)
3. **Linting** (ruff, mypy)
4. **Security** (bandit)
5. **Commit message** (conventional-pre-commit)

If any hook fails, the commit is **aborted** and later hooks don't run.

## What Each Command Does

### `pre-commit install`
```bash
pre-commit install
```
**What it does:**
- Creates a file at `.git/hooks/pre-commit`
- This script runs before every `git commit`
- Executes all configured hooks

### `pre-commit install --hook-type commit-msg`
```bash
pre-commit install --hook-type commit-msg
```
**What it does:**
- Creates a file at `.git/hooks/commit-msg`
- Runs after you write commit message
- Validates commit message format

### `pre-commit run`
```bash
pre-commit run --all-files
```
**What it does:**
- Manually triggers pre-commit hooks
- `--all-files` = Check every file, not just staged ones
- Useful for testing or running on entire codebase

**Options:**
- `--files FILE [FILE ...]` - Run on specific files
- `--verbose` - Show detailed output
- `--show-diff-on-failure` - Show what changed

### `pre-commit autoupdate`
```bash
pre-commit autoupdate
```
**What it does:**
- Checks for newer versions of hooks
- Updates `rev:` fields in `.pre-commit-config.yaml`
- Example: `rev: v4.5.0` → `rev: v4.6.0`

## Integration with CI/CD

Pre-commit also runs in GitHub Actions (see `.github/workflows/ci.yml`):

```yaml
- name: Run pre-commit hooks
  run: pre-commit run --all-files
```

This ensures code quality even if someone bypasses local hooks with `--no-verify`.

## Best Practices

1. **Never bypass hooks** unless it's an emergency
2. **Write good commit messages** following Conventional Commits
3. **Run `pre-commit run --all-files`** before pushing
4. **Update hooks regularly** with `pre-commit autoupdate`
5. **Add new hooks** as your project grows (more security checks, etc.)

## Performance Tips

Pre-commit can be slow on large repositories. Speed it up:

```bash
# Install hooks with faster updates
pre-commit install --install-hooks

# Run hooks in parallel (default)
# Already enabled in .pre-commit-config.yaml
```

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `pre-commit install` | Install pre-commit hooks |
| `pre-commit run --all-files` | Run all hooks on all files |
| `pre-commit run ruff` | Run only ruff hook |
| `pre-commit autoupdate` | Update hooks to latest versions |
| `pre-commit clean` | Clean hook cache |
| `git commit --no-verify` | Bypass hooks (emergency only!) |

## Summary

Pre-commit hooks are now **active** in this repository. Every commit will be:
- ✅ **Formatted** automatically
- ✅ **Linted** for code quality
- ✅ **Scanned** for security issues
- ✅ **Type-checked** for correctness
- ✅ **Validated** for commit message format

Just commit as usual - the hooks will run automatically! If issues are found, fix them and commit again.

---

**Happy coding with automated quality checks!**
