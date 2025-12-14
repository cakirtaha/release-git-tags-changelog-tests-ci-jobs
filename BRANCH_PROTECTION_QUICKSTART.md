# Branch Protection Quick Start

## 🎯 Goal
Block all merges to `master` until CI jobs (`quality` and `deploy`) pass successfully.

## ⚡ Quick Setup (Choose One Method)

### Method 1: GitHub Web UI (5 minutes)

1. **Go to Settings**
   ```
   https://github.com/YOUR-USERNAME/YOUR-REPO/settings/branches
   ```

2. **Add Protection Rule**
   - Click "Add rule" or "Add branch protection rule"
   - Branch name pattern: `master`

3. **Enable These Settings** ✅
   - ✅ Require a pull request before merging
     - Required approvals: `1`
     - ✅ Dismiss stale reviews
   - ✅ Require status checks to pass
     - ✅ Require branches to be up to date
     - Select: `quality`, `deploy`
   - ✅ Require conversation resolution
   - ✅ Require linear history
   - ✅ Do not allow bypassing
   - ❌ Allow force pushes (uncheck)
   - ❌ Allow deletions (uncheck)

4. **Save**
   - Click "Create" or "Save changes"

---

### Method 2: Automated Script (1 minute)

#### Option A: Bash Script
```bash
# Make executable
chmod +x scripts/setup-branch-protection.sh

# Run script
./scripts/setup-branch-protection.sh
```

#### Option B: Python Script
```bash
# Install dependencies
pip install requests

# Set GitHub token
export GITHUB_TOKEN=$(gh auth token)

# Run script
python scripts/setup-branch-protection.py
```

---

### Method 3: GitHub CLI (30 seconds)

```bash
# Install gh CLI (if not installed)
brew install gh  # macOS
# Or: curl -sS https://webi.sh/gh | sh  # Linux

# Login
gh auth login

# Apply protection (replace OWNER and REPO)
gh api repos/OWNER/REPO/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["quality","deploy"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}'
```

---

## ✅ Verify Setup

### Test 1: Try Direct Push (Should Fail)
```bash
git checkout master
echo "test" > test.txt
git add test.txt
git commit -m "test: direct push"
git push origin master
```

**Expected:**
```
remote: error: GH006: Protected branch update failed
remote: Cannot push to master without a pull request
```

### Test 2: Create PR (Merge Blocked Until CI Passes)
```bash
git checkout -b test-branch
echo "print('test')" > src/project1/test.py
git add src/project1/test.py
git commit -m "feat: test branch protection"
git push origin test-branch
```

**Expected on GitHub:**
- ❌ Merge button disabled
- Message: "Required status checks must pass before merging"
- CI must run and pass before merge is allowed

---

## 📋 What's Protected?

### Required Before Merge:
1. ✅ **Pull Request created** (no direct pushes)
2. ✅ **CI job `quality` passes**
3. ✅ **CI job `deploy` passes**
4. ✅ **1 approval** from reviewer
5. ✅ **All comments resolved**
6. ✅ **Branch up to date** with master

### Blocked Actions:
- ❌ Direct push to master
- ❌ Force push to master
- ❌ Deleting master branch
- ❌ Merging without CI passing
- ❌ Merging without review
- ❌ Merging with unresolved comments

---

## 🔍 Check Current Protection

```bash
# Using GitHub CLI
gh api repos/OWNER/REPO/branches/master/protection | jq .

# Check required status checks
gh api repos/OWNER/REPO/branches/master/protection | jq '.required_status_checks.contexts'

# Expected output:
# [
#   "quality",
#   "deploy"
# ]
```

---

## 🛠️ Common Commands

### Update Required Status Checks
```bash
gh api repos/OWNER/REPO/branches/master/protection \
  --method PATCH \
  --field required_status_checks='{"strict":true,"contexts":["quality","deploy","new-job"]}'
```

### Change Required Approvals
```bash
gh api repos/OWNER/REPO/branches/master/protection \
  --method PATCH \
  --field required_pull_request_reviews='{"required_approving_review_count":2}'
```

### Disable Branch Protection (Temporary)
```bash
gh api repos/OWNER/REPO/branches/master/protection --method DELETE
```

### Re-enable Branch Protection
```bash
./scripts/setup-branch-protection.sh
```

---

## 🚨 Troubleshooting

### Problem: Status checks don't appear in dropdown

**Solution:** Push a commit to trigger CI first
```bash
git commit --allow-empty -m "chore: trigger CI"
git push origin master
```

Wait for workflow to complete, then refresh branch protection page.

---

### Problem: Can't see "quality" or "deploy" in status check list

**Cause:** Job names don't match

**Check workflow file** (`.github/workflows/ci.yml`):
```yaml
jobs:
  quality:    # ← Use this name
    name: Code Quality  # ← Not this
```

Use the **job ID** (`quality`), not the `name` field.

---

### Problem: "This branch is out of date"

**Solution:** Update branch before merging
```bash
# On GitHub, click "Update branch" button

# Or locally:
git checkout your-branch
git pull origin master
git push origin your-branch
```

---

### Problem: Admin can't bypass rules

**Cause:** "Do not allow bypassing" is enabled

**Solution:**
1. Go to Settings → Branches
2. Edit protection rule
3. Uncheck "Do not allow bypassing the above settings"
4. Save

---

## 📚 Related Guides

- **Full Setup Guide:** `BRANCH_PROTECTION_GUIDE.md`
- **CODEOWNERS:** `.github/CODEOWNERS`
- **Pre-commit Hooks:** `PRE_COMMIT_GUIDE.md`
- **Auto-Release:** `MULTI_PROJECT_RELEASE_GUIDE.md`

---

## 🎓 Best Practices

1. **Start with these settings**, adjust as needed
2. **Don't bypass** unless emergency
3. **Use CODEOWNERS** for critical files
4. **Monitor audit log** for bypass events
5. **Update status checks** when adding new CI jobs

---

## 📞 Quick Help

### Get Help
```bash
gh api repos/OWNER/REPO/branches/master/protection --help
```

### View Audit Log
```
https://github.com/OWNER/REPO/settings/branch_protection_rules
```

### GitHub Documentation
```
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
```

---

## ✨ Summary

**Your CI jobs (`quality` and `deploy`) must pass before ANY merge to master!**

Changes now require:
1. Pull Request
2. CI success
3. Code review
4. Resolved comments

**No exceptions. No direct pushes. No force pushes.**

This ensures code quality and prevents broken code from reaching master.
