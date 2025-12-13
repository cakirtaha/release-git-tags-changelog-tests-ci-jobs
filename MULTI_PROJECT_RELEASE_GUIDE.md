# Multi-Project Auto-Release Guide

## Overview

This repository now supports **independent releases for multiple projects** using a **single, scalable workflow**. Each project (`project1`, `project2`, `project3`) can have its own version and release cycle.

## Key Features

- **Single Workflow File**: One `.github/workflows/auto-release.yml` handles all projects
- **Dynamic Detection**: Automatically detects which projects changed
- **Independent Versioning**: Each project has its own version number
- **Parallel Releases**: Multiple projects can be released simultaneously
- **Project-Specific Tags**: Tags are prefixed with project name (e.g., `project1-v0.2.0`)
- **Separate Changelogs**: Each release includes only commits for that project

## How It Works

### 1. Version Tracking (`versions.json`)

All project versions are stored in a central `versions.json` file:

```json
{
  "projects": {
    "project1": {
      "version": "0.2.0",
      "description": "Project 1 - Main application"
    },
    "project2": {
      "version": "0.1.0",
      "description": "Project 2 - Secondary service"
    },
    "project3": {
      "version": "0.1.0",
      "description": "Project 3 - Utilities"
    }
  }
}
```

**Why JSON?**
- Easy to read and update programmatically
- Supports metadata (description, etc.)
- Can be extended with additional fields

### 2. Two-Job Workflow Architecture

#### Job 1: Detect Changed Projects

**What it does:**
- Compares current commit with previous commit
- Identifies which project directories (`src/project1/`, `src/project2/`, etc.) have changes
- Outputs a JSON array of changed projects

**Example output:**
```json
["project1", "project2"]
```

**Key commands:**
```bash
# Get changed files between commits
git diff --name-only HEAD^ HEAD

# Check if files match pattern
echo "$CHANGED_FILES" | grep -q "^src/project1/"

# Build JSON array
PROJECTS_JSON="[$(IFS=,; echo "${CHANGED_PROJECTS[*]}")]"
```

#### Job 2: Release Projects (Matrix Strategy)

**What it does:**
- Runs **once per changed project** using GitHub Actions matrix strategy
- Each project release runs **in parallel**
- Independent failure handling (one project failing doesn't stop others)

**Matrix strategy example:**
```yaml
strategy:
  matrix:
    project: ["project1", "project2"]  # From Job 1
  fail-fast: false
```

This creates **2 parallel jobs**:
- `Release project1`
- `Release project2`

## Workflow Step-by-Step

### Step 1: Detect Changes (Job 1)

```bash
# Compare current and previous commits
CHANGED_FILES=$(git diff --name-only HEAD^ HEAD)

# Loop through projects
for PROJECT in project1 project2 project3; do
  if echo "$CHANGED_FILES" | grep -q "^src/${PROJECT}/"; then
    CHANGED_PROJECTS+=("\"$PROJECT\"")
  fi
done
```

**Output:**
```
✓ Detected changes in project1
○ No changes in project2
○ No changes in project3

Projects with changes: ["project1"]
```

### Step 2: Get Current Version (Job 2)

```bash
# Read version from versions.json using Python
CURRENT_VERSION=$(python -c "import json; data = json.load(open('versions.json')); print(data['projects']['project1']['version'])")

# Output: 0.2.0
```

**Why Python?**
- Safer than shell JSON parsing
- Built-in JSON support
- Works consistently across platforms

### Step 3: Calculate New Version

Same logic as before:
```bash
MAJOR=0
MINOR=2
NEW_MINOR=$((MINOR + 1))  # 3

if [ $NEW_MINOR -eq 10 ]; then
  MAJOR=$((MAJOR + 1))
  NEW_MINOR=0
fi

NEW_VERSION="${MAJOR}.${NEW_MINOR}.0"  # 0.3.0
```

**Examples:**
- `project1: 0.2.0` → `0.3.0`
- `project2: 0.9.0` → `1.0.0`
- `project3: 1.5.0` → `1.6.0`

### Step 4: Update versions.json

```python
import json

# Read current data
with open('versions.json', 'r') as f:
    data = json.load(f)

# Update specific project
data['projects']['project1']['version'] = '0.3.0'

# Write back
with open('versions.json', 'w') as f:
    json.dump(data, f, indent=2)
```

**Result:**
```json
{
  "projects": {
    "project1": {
      "version": "0.3.0",  ← Updated
      "description": "Project 1 - Main application"
    }
  }
}
```

### Step 5: Generate Project-Specific Changelog

```bash
PROJECT="project1"
PREV_TAG="project1-v0.2.0"

# Only get commits that affected this project
git log ${PREV_TAG}..HEAD --pretty=format:"- %s (%an, %ar)" -- src/project1/
```

**Output:**
```markdown
# Release project1 v0.3.0

**Released on:** 2024-12-13 15:30:00 UTC
**Project:** `project1`

## Changes since project1-v0.2.0

- feat: add user authentication (John Doe, 2 hours ago)
- fix: resolve login bug (Jane Smith, 1 day ago)

## File Changes
```
 src/project1/auth.py    | 50 ++++++++++++++++++++
 src/project1/login.py   | 12 +++--
 2 files changed, 58 insertions(+), 4 deletions(-)
```
```

### Step 6: Create Project-Specific Tag

```bash
TAG_NAME="project1-v0.3.0"

# Create annotated tag
git tag -a "$TAG_NAME" -m "Release project1 version 0.3.0"

# Push
git push --follow-tags
```

**Tag naming convention:**
- `project1-v0.3.0`
- `project2-v1.2.0`
- `project3-v0.5.0`

This prevents tag conflicts and makes it clear which project each tag belongs to.

### Step 7: Create GitHub Release

```yaml
tag_name: project1-v0.3.0
name: project1 v0.3.0
body_path: CHANGELOG_project1_v0.3.0.md
```

**Release naming:**
- Title: `project1 v0.3.0`
- Tag: `project1-v0.3.0`
- Changelog: Project-specific commits only

## Usage Examples

### Example 1: Release Single Project

```bash
# Make changes to project1
echo "print('New feature')" > src/project1/feature.py

# Commit and push
git add src/project1/feature.py
git commit -m "feat(project1): add new feature"
git push origin master
```

**What happens:**
1. Workflow detects change in `src/project1/`
2. Reads current version: `0.2.0`
3. Calculates new version: `0.3.0`
4. Updates `versions.json`
5. Creates tag: `project1-v0.3.0`
6. Creates release: `project1 v0.3.0`

**Result:**
- `versions.json` shows `project1: 0.3.0`
- Tag `project1-v0.3.0` exists
- Release visible on GitHub

### Example 2: Release Multiple Projects Simultaneously

```bash
# Make changes to both project1 and project2
echo "print('Feature A')" > src/project1/feature_a.py
echo "print('Feature B')" > src/project2/feature_b.py

# Commit and push
git add src/project1/feature_a.py src/project2/feature_b.py
git commit -m "feat: add features to project1 and project2"
git push origin master
```

**What happens:**
1. Workflow detects changes in both `src/project1/` and `src/project2/`
2. Creates **2 parallel jobs**:
   - Job 1: Release project1 (0.2.0 → 0.3.0)
   - Job 2: Release project2 (0.1.0 → 0.2.0)
3. Both jobs run **simultaneously**
4. Creates 2 tags: `project1-v0.3.0`, `project2-v0.2.0`
5. Creates 2 releases

**Result:**
- `versions.json` updated for both projects
- 2 separate tags created
- 2 separate releases on GitHub

### Example 3: Add New Project (project4)

To add a new project, update 3 places:

1. **Create project directory:**
   ```bash
   mkdir src/project4
   ```

2. **Add to `versions.json`:**
   ```json
   {
     "projects": {
       "project1": {...},
       "project2": {...},
       "project3": {...},
       "project4": {
         "version": "0.1.0",
         "description": "Project 4 - New service"
       }
     }
   }
   ```

3. **Update workflow paths:**
   ```yaml
   paths:
     - 'src/project1/**'
     - 'src/project2/**'
     - 'src/project3/**'
     - 'src/project4/**'  # Add this
   ```

4. **Update detection loop:**
   ```bash
   for PROJECT in project1 project2 project3 project4; do
   ```

That's it! The workflow is now tracking project4.

## Key Commands Explained

### 1. Git Diff for Changed Files

```bash
git diff --name-only HEAD^ HEAD
```

**What it does:**
- `HEAD^` = Previous commit
- `HEAD` = Current commit
- `--name-only` = Show only file names, not content
- Outputs list of changed files

**Example output:**
```
src/project1/auth.py
src/project1/login.py
README.md
```

### 2. Grep Pattern Matching

```bash
echo "$CHANGED_FILES" | grep -q "^src/project1/"
```

**What it does:**
- `grep -q` = Quiet mode (exit code only, no output)
- `^src/project1/` = Lines starting with `src/project1/`
- Returns 0 (success) if match found, 1 if not

**Use case:**
```bash
if echo "$CHANGED_FILES" | grep -q "^src/project1/"; then
  echo "project1 changed!"
fi
```

### 3. Bash Array to JSON

```bash
CHANGED_PROJECTS=("\"project1\"" "\"project2\"")
PROJECTS_JSON="[$(IFS=,; echo "${CHANGED_PROJECTS[*]}")]"
```

**What it does:**
- `IFS=,` = Set delimiter to comma
- `"${CHANGED_PROJECTS[*]}"` = Join array elements
- Wraps in brackets to create JSON array

**Result:**
```json
["project1", "project2"]
```

### 4. GitHub Actions Matrix Strategy

```yaml
strategy:
  matrix:
    project: ${{ fromJson(needs.detect-changes.outputs.projects) }}
  fail-fast: false
```

**What it does:**
- `fromJson()` = Converts JSON string to array
- `matrix.project` = Current project in this job instance
- `fail-fast: false` = Don't stop other jobs if one fails

**Example:**
If `projects = ["project1", "project2"]`, this creates:
- Job: `Release project1` with `matrix.project = "project1"`
- Job: `Release project2` with `matrix.project = "project2"`

### 5. Git Pull with Rebase

```bash
git pull --rebase origin master || true
```

**What it does:**
- `--rebase` = Apply local commits on top of remote changes
- `|| true` = Don't fail if pull unsuccessful (handles race conditions)

**Why needed:**
When multiple projects release in parallel, they might conflict when pushing. This ensures the latest changes are incorporated.

### 6. Conditional File Staging

```bash
if [ "$PROJECT" == "project1" ]; then
  git add pyproject.toml
fi
```

**What it does:**
- Only stages `pyproject.toml` for project1
- Other projects don't modify this file

**Why:**
`pyproject.toml` is the main project version file, only updated for project1 (the primary project).

## Troubleshooting

### Issue: Workflow doesn't trigger for my project

**Check:**
1. Is your project directory in the `paths` filter?
   ```yaml
   paths:
     - 'src/yourproject/**'
   ```

2. Is your project in the detection loop?
   ```bash
   for PROJECT in project1 project2 yourproject; do
   ```

3. Did you add it to `versions.json`?

### Issue: Tag conflicts or wrong version

**Solution:**
- Check `versions.json` has correct current version
- Verify tag naming: `{project}-v{version}`
- Check for existing tags: `git tag -l "project1-*"`

### Issue: Multiple projects releasing causes conflicts

**Why it happens:**
When 2 projects release in parallel, both try to push `versions.json` at the same time.

**How it's handled:**
```bash
git pull --rebase origin master || true
```

This line pulls the latest changes (from the other project's release) before pushing.

## Version Management

### Current Version Tracking

Check all project versions:
```bash
cat versions.json
```

Check specific project:
```bash
python -c "import json; data = json.load(open('versions.json')); print(data['projects']['project1']['version'])"
```

### Manual Version Update

If you need to manually set a version:

```bash
# Update versions.json
python << EOF
import json
with open('versions.json', 'r') as f:
    data = json.load(f)
data['projects']['project2']['version'] = '1.5.0'
with open('versions.json', 'w') as f:
    json.dump(data, f, indent=2)
EOF

# Commit
git add versions.json
git commit -m "chore(project2): set version to 1.5.0"
git push origin master
```

### View Release History

List all releases:
```bash
git tag -l
```

List releases for specific project:
```bash
git tag -l "project1-*"
```

Output:
```
project1-v0.1.0
project1-v0.2.0
project1-v0.3.0
```

## GitHub Release Examples

### What You'll See on GitHub

**Releases page shows:**
- `project1 v0.3.0` (tagged `project1-v0.3.0`)
- `project2 v0.2.0` (tagged `project2-v0.2.0`)
- `project1 v0.2.0` (tagged `project1-v0.2.0`)

Each release has:
- **Tag**: `{project}-v{version}`
- **Title**: `{project} v{version}`
- **Changelog**: Only commits affecting that project
- **File changes**: Diff stats for that project only

## Advantages of This Approach

1. **Scalable**: Add new projects without duplicating workflows
2. **Efficient**: Parallel releases save time
3. **Clear Separation**: Each project has independent version history
4. **Flexible**: Easy to customize per-project behavior
5. **Maintainable**: Single workflow file to update
6. **Traceable**: Clear project-specific tags and changelogs

## Extending the Workflow

### Add Project-Specific Logic

Use conditionals based on `matrix.project`:

```yaml
- name: Run project-specific tests
  run: |
    if [ "${{ matrix.project }}" == "project1" ]; then
      pytest tests/project1/
    elif [ "${{ matrix.project }}" == "project2" ]; then
      npm test
    fi
```

### Add Custom Metadata

Extend `versions.json`:
```json
{
  "projects": {
    "project1": {
      "version": "0.3.0",
      "description": "Main application",
      "maintainer": "team-a",
      "language": "python"
    }
  }
}
```

### Filter by File Type

Only release if specific files changed:
```bash
if echo "$CHANGED_FILES" | grep -q "^src/${PROJECT}/.*\.py$"; then
  echo "Python files changed in $PROJECT"
fi
```

## Quick Reference

| Action | Command |
|--------|---------|
| Check versions | `cat versions.json` |
| List all tags | `git tag -l` |
| List project tags | `git tag -l "project1-*"` |
| Manual version update | Edit `versions.json` + commit |
| Add new project | Update `versions.json`, `paths`, and detection loop |
| View release | Go to GitHub Releases page |

## Summary

This multi-project release workflow provides:
- ✅ **One workflow** for all projects
- ✅ **Independent versioning** via `versions.json`
- ✅ **Dynamic detection** of changed projects
- ✅ **Parallel releases** using matrix strategy
- ✅ **Project-specific tags** (`project1-v0.3.0`)
- ✅ **Separate changelogs** per project
- ✅ **Scalable architecture** for adding new projects

Just commit to any project directory, and the workflow automatically detects and releases it!
