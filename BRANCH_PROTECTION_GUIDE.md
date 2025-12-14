# Branch Protection & Security Setup Guide

## Overview

This guide explains how to set up **enhanced branch protection** for the `master` branch to ensure:
- ✅ All CI jobs must pass before merging
- ✅ Code reviews are required
- ✅ No direct pushes to master (only via Pull Requests)
- ✅ Status checks are enforced
- ✅ Branch is up-to-date before merging

## Your CI Jobs

Based on `.github/workflows/ci.yml`, your CI workflow has these jobs:

1. **`quality`** - Code Quality
   - Runs pre-commit hooks
   - Runs tests with coverage
   - Uploads coverage reports

2. **`deploy`** - Deploy (placeholder)
   - Depends on `quality` job passing
   - Placeholder for future deployments

## Method 1: GitHub Web UI (Manual Setup)

### Step-by-Step Instructions

#### 1. Navigate to Branch Protection Settings

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. In the left sidebar, click **Branches**
4. Under "Branch protection rules", click **Add rule** or **Add branch protection rule**

#### 2. Configure Branch Name Pattern

In the **Branch name pattern** field, enter:
```
master
```

Or use a pattern for multiple branches:
```
main
master
production
```

#### 3. Enable Required Status Checks

✅ Check **Require status checks to pass before merging**

This prevents merging unless CI jobs pass.

**Sub-options:**
- ✅ Check **Require branches to be up to date before merging**
  - Forces branch to be rebased/merged with latest master before PR can merge

**Select required status checks:**
In the search box, you'll see available status checks. Select:
- ✅ `quality` (Code Quality job)
- ✅ `deploy` (Deploy job)

> **Note:** Status checks only appear after they've run at least once. If you don't see them, push a commit to trigger the CI workflow first.

#### 4. Enable Pull Request Reviews

✅ Check **Require a pull request before merging**

**Sub-options:**
- ✅ Check **Require approvals**
  - Set **Required number of approvals before merging**: `1` (or more)

- ✅ Check **Dismiss stale pull request approvals when new commits are pushed**
  - Re-approval required after new commits

- ☐ Optional: **Require review from Code Owners**
  - Requires approval from designated code owners (see CODEOWNERS section)

- ☐ Optional: **Restrict who can dismiss pull request reviews**
  - Only specific people can override reviews

- ✅ Check **Require approval of the most recent reviewable push**
  - Prevents approving old commits and then pushing new code

#### 5. Enable Additional Protections

✅ Check **Require conversation resolution before merging**
- All PR comments must be resolved

✅ Check **Require signed commits**
- Only GPG-signed commits allowed (optional, more strict)

✅ Check **Require linear history**
- Prevents merge commits, enforces rebase/squash

☐ Optional: **Require deployments to succeed before merging**
- For production branches with deployment workflows

✅ Check **Do not allow bypassing the above settings**
- Even admins must follow these rules

☐ Optional: **Restrict who can push to matching branches**
- Limit direct pushes to specific users/teams
- Recommended: Leave empty to block ALL direct pushes (force PR workflow)

✅ Check **Allow force pushes** - **UNCHECK THIS**
- Prevents force pushes that rewrite history

✅ Check **Allow deletions** - **UNCHECK THIS**
- Prevents branch deletion

#### 6. Save Configuration

Click **Create** (or **Save changes** if editing existing rule)

### Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│  Branch Protection Rule for `master`                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Branch name pattern: [master]                              │
│                                                              │
│  ✅ Require a pull request before merging                   │
│     ├─ ✅ Require approvals (1)                            │
│     ├─ ✅ Dismiss stale approvals on new commits           │
│     └─ ✅ Require approval of most recent push             │
│                                                              │
│  ✅ Require status checks to pass before merging            │
│     ├─ ✅ Require branches to be up to date                │
│     └─ Status checks:                                       │
│         ├─ ✅ quality                                       │
│         └─ ✅ deploy                                        │
│                                                              │
│  ✅ Require conversation resolution before merging          │
│                                                              │
│  ✅ Require linear history                                  │
│                                                              │
│  ✅ Do not allow bypassing the above settings               │
│                                                              │
│  ☐ Restrict who can push (leave empty = no direct pushes)  │
│                                                              │
│  ❌ Allow force pushes (UNCHECKED)                          │
│  ❌ Allow deletions (UNCHECKED)                             │
│                                                              │
│                          [Create]                            │
└─────────────────────────────────────────────────────────────┘
```

## Method 2: GitHub CLI (Programmatic Setup)

### Prerequisites

Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
curl -sS https://webi.sh/gh | sh

# Windows
winget install GitHub.cli

# Verify installation
gh --version
```

### Authenticate with GitHub

```bash
# Login to GitHub
gh auth login

# Select:
# - GitHub.com
# - HTTPS
# - Login with a web browser (or paste token)
```

### Configure Branch Protection

```bash
# Enable branch protection for master
gh api repos/{owner}/{repo}/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["quality","deploy"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1,"require_last_push_approval":true}' \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_conversation_resolution=true
```

**Replace `{owner}/{repo}` with your repository details:**
```bash
# Example for owner "cakirtaha" and repo "my-project"
gh api repos/cakirtaha/my-project/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["quality","deploy"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1,"require_last_push_approval":true}' \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_conversation_resolution=true
```

### Command Breakdown

**`required_status_checks`:**
```json
{
  "strict": true,              // Require branch to be up to date
  "contexts": [                // Required CI jobs
    "quality",
    "deploy"
  ]
}
```

**`required_pull_request_reviews`:**
```json
{
  "dismiss_stale_reviews": true,           // Re-approve after new commits
  "require_code_owner_reviews": false,     // Require CODEOWNERS approval
  "required_approving_review_count": 1,    // Number of approvals needed
  "require_last_push_approval": true       // Approve most recent push
}
```

**Other flags:**
- `enforce_admins=true` - Admins must follow rules too
- `restrictions=null` - No push restrictions (blocks all direct pushes)
- `required_linear_history=true` - No merge commits
- `allow_force_pushes=false` - Block force pushes
- `allow_deletions=false` - Block branch deletion
- `required_conversation_resolution=true` - Resolve all comments

### View Current Protection Settings

```bash
# Check current branch protection
gh api repos/{owner}/{repo}/branches/master/protection
```

### Disable Branch Protection (if needed)

```bash
# Remove all branch protection
gh api repos/{owner}/{repo}/branches/master/protection \
  --method DELETE
```

## Method 3: GitHub API with Script

Create a script to automate branch protection setup.

### Script: `setup-branch-protection.sh`

```bash
#!/bin/bash

# Configuration
OWNER="your-github-username"
REPO="your-repo-name"
BRANCH="master"
TOKEN="your-github-token"  # Or use: $(gh auth token)

# API Endpoint
API_URL="https://api.github.com/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection"

# Branch Protection Configuration
PROTECTION_CONFIG='{
  "required_status_checks": {
    "strict": true,
    "contexts": ["quality", "deploy"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1,
    "require_last_push_approval": true,
    "dismissal_restrictions": {}
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}'

# Apply branch protection
curl -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "${API_URL}" \
  -d "${PROTECTION_CONFIG}"

echo "✅ Branch protection applied to ${BRANCH}"
```

### Using the Script

```bash
# Make executable
chmod +x setup-branch-protection.sh

# Run script
./setup-branch-protection.sh
```

### Python Script Alternative

```python
#!/usr/bin/env python3

import requests
import os
import json

# Configuration
OWNER = "your-github-username"
REPO = "your-repo-name"
BRANCH = "master"
TOKEN = os.getenv("GITHUB_TOKEN")  # Or hardcode (not recommended)

# API URL
url = f"https://api.github.com/repos/{OWNER}/{REPO}/branches/{BRANCH}/protection"

# Headers
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Protection Configuration
protection_config = {
    "required_status_checks": {
        "strict": True,
        "contexts": ["quality", "deploy"]
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": False,
        "required_approving_review_count": 1,
        "require_last_push_approval": True
    },
    "restrictions": None,
    "required_linear_history": True,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_conversation_resolution": True
}

# Apply protection
response = requests.put(url, headers=headers, json=protection_config)

if response.status_code == 200:
    print("✅ Branch protection applied successfully!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

## Method 4: Terraform (Infrastructure as Code)

For teams using Terraform:

```hcl
resource "github_branch_protection" "master" {
  repository_id = github_repository.repo.node_id
  pattern       = "master"

  required_status_checks {
    strict   = true
    contexts = ["quality", "deploy"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = false
    required_approving_review_count = 1
    require_last_push_approval      = true
  }

  enforce_admins              = true
  require_conversation_resolution = true
  require_signed_commits      = false
  required_linear_history     = true

  allow_deletions    = false
  allow_force_pushes = false
}
```

## CODEOWNERS Setup (Optional but Recommended)

### What is CODEOWNERS?

CODEOWNERS designates specific people/teams to review changes to specific files or directories.

### Create `.github/CODEOWNERS`

```bash
# CODEOWNERS file defines who owns which parts of the codebase
# Format: path/pattern @username @team

# Global owners (fallback)
* @your-username

# Project-specific owners
/src/project1/ @team-project1 @username1
/src/project2/ @team-project2 @username2
/src/project3/ @team-project3 @username3

# Configuration files require senior approval
/.github/ @senior-dev @team-leads
/pyproject.toml @senior-dev
/versions.json @release-team

# Documentation
*.md @docs-team

# CI/CD workflows
/.github/workflows/ @devops-team @senior-dev

# Security-sensitive files
/.pre-commit-config.yaml @security-team
```

### Enable CODEOWNERS in Branch Protection

In GitHub UI:
1. Branch protection rules → **Require a pull request before merging**
2. Check ✅ **Require review from Code Owners**

Via GitHub CLI:
```bash
gh api repos/{owner}/{repo}/branches/master/protection \
  --method PUT \
  --field required_pull_request_reviews='{"require_code_owner_reviews":true,"required_approving_review_count":1}'
```

## Verification & Testing

### Test Branch Protection

1. **Try direct push to master (should fail):**
   ```bash
   git checkout master
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: direct push"
   git push origin master
   ```

   **Expected result:**
   ```
   remote: error: GH006: Protected branch update failed
   remote: error: Cannot push to master without a pull request
   ```

2. **Create PR without passing CI (should block merge):**
   ```bash
   git checkout -b test-branch
   echo "print('buggy code)" > src/project1/bug.py  # Syntax error
   git add src/project1/bug.py
   git commit -m "feat: add buggy code"
   git push origin test-branch
   ```

   Create PR on GitHub. You'll see:
   - ❌ CI checks failing
   - 🚫 **Merge** button disabled
   - Message: "Required status checks must pass before merging"

3. **Fix code and verify merge enabled:**
   ```bash
   echo "print('working code')" > src/project1/bug.py
   git add src/project1/bug.py
   git commit -m "fix: correct syntax error"
   git push origin test-branch
   ```

   Now:
   - ✅ CI checks pass
   - ✅ **Merge** button enabled (if reviewed)

### Verify Protection Settings

```bash
# Using GitHub CLI
gh api repos/{owner}/{repo}/branches/master/protection | jq .

# Check specific setting
gh api repos/{owner}/{repo}/branches/master/protection | jq '.required_status_checks.contexts'
```

**Expected output:**
```json
[
  "quality",
  "deploy"
]
```

## Common Issues & Solutions

### Issue 1: Status checks don't appear in dropdown

**Cause:** CI workflow hasn't run yet

**Solution:**
1. Push a commit to trigger CI
2. Wait for workflow to complete
3. Refresh GitHub branch protection page
4. Status checks should now appear

### Issue 2: "Required status checks not found"

**Cause:** Job names don't match

**Solution:**
Check your CI workflow job names:
```yaml
jobs:
  quality:    # ← This exact name must be in status checks
    name: Code Quality
```

Use the **job ID** (`quality`), not the `name` field.

### Issue 3: Can't merge even though CI passed

**Cause:** Branch not up to date

**Solution:**
Enable "Update branch" button on PR or:
```bash
git checkout your-branch
git pull origin master
git push origin your-branch
```

### Issue 4: Admin bypass not working

**Cause:** "Do not allow bypassing" is enabled

**Solution:**
Temporarily disable in branch protection settings, or have another admin approve.

## Best Practices

### 1. Start Strict, Relax Later
Begin with strict rules, loosen if needed:
- ✅ Require 2+ approvals initially
- ✅ Require CODEOWNERS reviews
- ✅ Enforce linear history

### 2. Use Rulesets for Multiple Branches
Instead of separate rules for `main`, `master`, `production`:
```
Branch name pattern: {main,master,production}
```

### 3. Separate Dev and Prod Rules
- `master`/`main`: Strict protection
- `develop`: Lighter protection (fewer required approvals)
- Feature branches: No protection

### 4. Monitor Bypass Events
Check who bypasses branch protection:
- Settings → Branches → View audit log

### 5. Use CODEOWNERS Granularly
```
/src/project1/critical/ @senior-dev @security
/src/project1/tests/ @any-developer
```

### 6. Automate Protection with CI
Add branch protection check to CI:
```yaml
- name: Verify branch protection
  run: |
    PROTECTION=$(gh api repos/${{ github.repository }}/branches/master/protection)
    if [ -z "$PROTECTION" ]; then
      echo "❌ Branch protection not configured!"
      exit 1
    fi
```

## Summary

To block merges to master until all CI jobs pass:

### Quick Setup (GitHub UI):
1. Settings → Branches → Add rule
2. Pattern: `master`
3. ✅ Require status checks: `quality`, `deploy`
4. ✅ Require pull request reviews (1 approval)
5. ✅ Require conversation resolution
6. ✅ Require linear history
7. ❌ Allow force pushes (uncheck)
8. ✅ Do not allow bypassing
9. Click **Create**

### Quick Setup (GitHub CLI):
```bash
gh api repos/{owner}/{repo}/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["quality","deploy"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

Your CI jobs (`quality` and `deploy`) must now pass before any PR can merge to `master`!
