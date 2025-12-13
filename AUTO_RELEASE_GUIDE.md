# Auto-Release Workflow Guide

## Overview

This project includes an automated release system that triggers whenever code is pushed to `src/project1/`. The system automatically:
- Bumps the version by 0.1
- Generates a changelog
- Creates a git tag
- Publishes a GitHub release

## How It Works

### Version Bumping Logic

The workflow increments the **minor version** by 1 each time:

- `v0.1.0` → `v0.2.0`
- `v0.2.0` → `v0.3.0`
- `v0.9.0` → `v1.0.0` ⭐ (automatic rollover)
- `v1.0.0` → `v1.1.0`
- `v1.9.0` → `v2.0.0` ⭐ (automatic rollover)

### Trigger Conditions

The workflow **only** runs when:
1. Code is pushed to the `master` branch
2. At least one file in `src/project1/` has changed

**Examples:**
- ✅ Modify `src/project1/main.py` → Release triggers
- ✅ Add new file `src/project1/utils.py` → Release triggers
- ❌ Modify `src/project2/file.py` → No release
- ❌ Modify `README.md` → No release

## Workflow Steps Explained

### Step 1: Checkout Repository
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```
**What it does:** Downloads your repository code to the GitHub Actions runner.
**Why `fetch-depth: 0`:** Fetches complete git history (not just the latest commit), which is needed for changelog generation.

### Step 2: Setup Python
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
```
**What it does:** Installs Python 3.12 on the runner.
**Why we need it:** To run Python scripts that parse `pyproject.toml` and calculate versions.

### Step 3: Install UV
```yaml
- uses: astral-sh/setup-uv@v4
```
**What it does:** Installs the `uv` package manager (fast Python package installer).
**Why we need it:** Your project uses `uv` for dependency management.

### Step 4: Get Current Version
```bash
CURRENT_VERSION=$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")
```
**What it does:**
- Installs the `toml` library
- Parses `pyproject.toml`
- Extracts the current version number
- Saves it to GitHub Actions output variable

**Example:** If `pyproject.toml` contains `version = "0.1.0"`, this extracts `0.1.0`

### Step 5: Calculate New Version
```bash
MAJOR=$(echo $CURRENT | cut -d. -f1)  # Extract major version
MINOR=$(echo $CURRENT | cut -d. -f2)  # Extract minor version
NEW_MINOR=$((MINOR + 1))              # Increment by 1

if [ $NEW_MINOR -eq 10 ]; then        # Check for rollover
  MAJOR=$((MAJOR + 1))                # Bump major
  NEW_MINOR=0                         # Reset minor to 0
fi

NEW_VERSION="${MAJOR}.${NEW_MINOR}.0"
```
**What it does:**
- Splits version into major.minor parts
- Adds 1 to the minor version
- If minor becomes 10, it rolls over (e.g., `0.9` → `1.0`)

**Examples:**
- `0.1.0` → major=0, minor=1 → new_minor=2 → `0.2.0`
- `0.9.0` → major=0, minor=9 → new_minor=10 → major=1, new_minor=0 → `1.0.0`

### Step 6: Update pyproject.toml
```bash
sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
```
**What it does:** Uses `sed` (stream editor) to find and replace the version line.
- `s/PATTERN/REPLACEMENT/` = substitute pattern with replacement
- `^version = .*` = matches lines starting with "version = " followed by anything
- Replaces entire line with new version

**Before:** `version = "0.1.0"`
**After:** `version = "0.2.0"`

### Step 7: Generate Changelog
```bash
git log --pretty=format:"- %s (%an)" -- src/project1/
```
**What it does:**
- Creates a markdown file `CHANGELOG_v{VERSION}.md`
- Adds release metadata (version, date)
- Lists all commits that modified `src/project1/`
- Shows commit message and author for each change

**`git log` options explained:**
- `--pretty=format:"- %s (%an)"` = Format as "- Subject (Author Name)"
- `-- src/project1/` = Only show commits affecting this directory
- `${PREV_TAG}..HEAD` = Commits between last tag and current HEAD

**Example output:**
```markdown
# Release v0.2.0

**Released on:** 2024-12-13

## Changes since v0.1.0

- Add user authentication (John Doe)
- Fix login bug (Jane Smith)
- Update documentation (Bob Johnson)

---
*This release was automatically generated for changes in `src/project1/`*
```

### Step 8: Commit Version Bump
```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add pyproject.toml
git commit -m "chore: bump version to $NEW_VERSION [skip ci]"
```
**What it does:**
- Configures git with GitHub Actions bot identity
- Stages the modified `pyproject.toml`
- Creates a commit

**Why `[skip ci]`:** Prevents infinite loop. Without this, the commit would trigger the CI workflow, which might trigger another release, etc.

### Step 9: Create and Push Tag
```bash
git tag -a "v0.2.0" -m "Release version 0.2.0"
git push --follow-tags
```
**What it does:**
- `git tag -a` = Creates an **annotated** tag (includes metadata)
- Annotated tags store: tagger name, email, date, and message
- `--follow-tags` = Pushes both commits and associated tags

**Why tags matter:** Tags are permanent markers in git history that releases reference.

### Step 10: Create GitHub Release
```yaml
- uses: softprops/action-gh-release@v1
  with:
    tag_name: v0.2.0
    name: Release v0.2.0 - Project1
    body_path: CHANGELOG_v0.2.0.md
```
**What it does:**
- Creates a formal release on GitHub's "Releases" page
- Associates release with the git tag
- Uses changelog as release description
- `generate_release_notes: true` adds GitHub's auto-generated notes (contributors, PR links)

### Step 11: Summary
```bash
echo "### 🎉 Release Complete!" >> $GITHUB_STEP_SUMMARY
```
**What it does:** Adds a formatted summary to the GitHub Actions run page so you can quickly see what happened.

## How to Test

### Option 1: Make a Real Change
1. Modify a file in `src/project1/`:
   ```bash
   echo "print('Hello World')" > src/project1/test.py
   git add src/project1/test.py
   git commit -m "feat: add hello world script"
   git push origin master
   ```

2. Watch the workflow run in GitHub Actions

3. Check for:
   - New tag `v0.2.0` in your repository
   - Updated `pyproject.toml` with `version = "0.2.0"`
   - New release on GitHub Releases page

### Option 2: Manual Workflow Trigger
You could add `workflow_dispatch` to the workflow triggers for manual testing:

```yaml
on:
  push:
    branches: [master]
    paths: ['src/project1/**']
  workflow_dispatch:  # Add this line
```

## Troubleshooting

### Issue: Workflow doesn't trigger
**Check:**
- Are you pushing to `master` branch?
- Did you modify files in `src/project1/`?
- Is the workflow file at `.github/workflows/auto-release.yml`?

### Issue: Permission denied when pushing tags
**Solution:** Ensure `GITHUB_TOKEN` has `contents: write` permission (already configured in workflow)

### Issue: Version not updating correctly
**Check:**
- Is `pyproject.toml` formatted correctly?
- Does it have a `version` field under `[project]`?

## Permissions Required

The workflow needs these permissions (already configured):
- **contents: write** - Create tags, push commits, create releases
- **pull-requests: write** - For potential future PR automation

## Security Considerations

- The workflow uses `GITHUB_TOKEN` (automatically provided, scoped to repository)
- Bot commits are clearly labeled as `github-actions[bot]`
- `[skip ci]` prevents infinite workflow loops
- Only triggers on `master` branch to prevent abuse

## Customization

### Change version increment
Modify step 5 in `.github/workflows/auto-release.yml`:
```bash
# For 0.01 increments (0.1 -> 0.11 -> 0.12)
NEW_MINOR=$((MINOR + 1))

# For 1.0 increments (1.0 -> 2.0 -> 3.0)
NEW_MAJOR=$((MAJOR + 1))
NEW_VERSION="${NEW_MAJOR}.0.0"
```

### Watch multiple directories
Change the `paths` filter:
```yaml
paths:
  - 'src/project1/**'
  - 'src/project2/**'  # Add more paths
```

### Change changelog format
Modify step 7 to use different git log formatting:
```bash
# Group by type (feat, fix, etc.)
git log --pretty=format:"%s" | grep "^feat:" >> $CHANGELOG_FILE
git log --pretty=format:"%s" | grep "^fix:" >> $CHANGELOG_FILE
```

## Files Modified by Workflow

1. **`pyproject.toml`** - Version number updated
2. **Git tags** - New tag created (e.g., `v0.2.0`)
3. **Temporary changelog** - `CHANGELOG_v{VERSION}.md` (created during workflow, used for release notes)

## What Gets Created

1. **Git commit** - "chore: bump version to X.Y.Z [skip ci]"
2. **Git tag** - `vX.Y.Z`
3. **GitHub Release** - Visible on `https://github.com/{owner}/{repo}/releases`
4. **Release notes** - Generated from commits to `src/project1/`

---

**Next Steps:** Push a change to `src/project1/` and watch the magic happen! 🚀
