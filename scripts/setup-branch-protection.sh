##!/bin/bash
#
## ============================================================================
## Branch Protection Setup Script
## ============================================================================
## This script configures branch protection for the master branch using
## GitHub CLI (gh). It ensures all CI jobs must pass before merging.
##
## Prerequisites:
## - GitHub CLI installed: brew install gh
## - Authenticated: gh auth login
##
## Usage:
##   ./setup-branch-protection.sh
## ============================================================================
#
#set -e  # Exit on error
#
## Colors for output
#RED='\033[0;31m'
#GREEN='\033[0;32m'
#YELLOW='\033[1;33m'
#BLUE='\033[0;34m'
#NC='\033[0m' # No Color
#
## Configuration
#BRANCH="master"
#REQUIRED_STATUS_CHECKS='["quality", "deploy"]'
#REQUIRED_APPROVALS=1
#
#echo ""
#echo "=================================================="
#echo "  Branch Protection Setup for '${BRANCH}' branch"
#echo "=================================================="
#echo ""
#
## Check if gh CLI is installed
#if ! command -v gh &> /dev/null; then
#    echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed${NC}"
#    echo ""
#    echo "Install it with:"
#    echo "  macOS:   brew install gh"
#    echo "  Linux:   curl -sS https://webi.sh/gh | sh"
#    echo "  Windows: winget install GitHub.cli"
#    echo ""
#    exit 1
#fi
#
## Check if authenticated
#if ! gh auth status &> /dev/null; then
#    echo -e "${RED}❌ Error: Not authenticated with GitHub${NC}"
#    echo ""
#    echo "Run: gh auth login"
#    echo ""
#    exit 1
#fi
#
## Get repository information
#REPO_INFO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
#if [ -z "$REPO_INFO" ]; then
#    echo -e "${RED}❌ Error: Not in a GitHub repository or unable to detect repository${NC}"
#    exit 1
#fi
#
#echo -e "${BLUE}📦 Repository:${NC} $REPO_INFO"
#echo -e "${BLUE}🌿 Branch:${NC} $BRANCH"
#echo ""
#
## Show what will be configured
#echo "Configuration to be applied:"
#echo ""
#echo "✅ Require status checks to pass before merging"
#echo "   - Required checks: quality, deploy"
#echo "   - Require branch to be up to date"
#echo ""
#echo "✅ Require pull request reviews"
#echo "   - Required approving reviews: $REQUIRED_APPROVALS"
#echo "   - Dismiss stale reviews on new commits"
#echo "   - Require approval of most recent push"
#echo ""
#echo "✅ Require conversation resolution before merging"
#echo ""
#echo "✅ Require linear history (no merge commits)"
#echo ""
#echo "✅ Enforce restrictions for administrators"
#echo ""
#echo "❌ Block force pushes"
#echo "❌ Block branch deletion"
#echo ""
#
## Confirm before applying
#read -p "Apply these settings? (y/N): " -n 1 -r
#echo ""
#if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#    echo -e "${YELLOW}⚠️  Cancelled${NC}"
#    exit 0
#fi
#
#echo ""
#echo "Applying branch protection..."
#echo ""
#
## Apply branch protection using GitHub API via gh CLI
#gh api \
#  --method PUT \
#  "repos/$REPO_INFO/branches/$BRANCH/protection" \
#  --input - << EOF
#{
#  "required_status_checks": {
#    "strict": true,
#    "contexts": $REQUIRED_STATUS_CHECKS
#  },
#  "enforce_admins": true,
#  "required_pull_request_reviews": {
#    "dismiss_stale_reviews": true,
#    "require_code_owner_reviews": false,
#    "required_approving_review_count": $REQUIRED_APPROVALS,
#    "require_last_push_approval": true
#  },
#  "restrictions": null,
#  "required_linear_history": true,
#  "allow_force_pushes": false,
#  "allow_deletions": false,
#  "required_conversation_resolution": true,
#  "lock_branch": false,
#  "allow_fork_syncing": true
#}
#EOF
#
#if [ $? -eq 0 ]; then
#    echo ""
#    echo -e "${GREEN}✅ Branch protection applied successfully!${NC}"
#    echo ""
#    echo "Summary:"
#    echo "  - Direct pushes to '$BRANCH' are now blocked"
#    echo "  - All changes must go through Pull Requests"
#    echo "  - CI jobs (quality, deploy) must pass before merging"
#    echo "  - $REQUIRED_APPROVALS approval(s) required before merging"
#    echo ""
#    echo "View settings at:"
#    echo "  https://github.com/$REPO_INFO/settings/branches"
#    echo ""
#else
#    echo ""
#    echo -e "${RED}❌ Error: Failed to apply branch protection${NC}"
#    echo ""
#    echo "Common issues:"
#    echo "  - Insufficient permissions (need admin access)"
#    echo "  - Branch doesn't exist yet"
#    echo "  - Repository is private and requires specific permissions"
#    echo ""
#    exit 1
#fi
#
## Verify settings
#echo "Verifying configuration..."
#echo ""
#
#PROTECTION=$(gh api "repos/$REPO_INFO/branches/$BRANCH/protection" 2>/dev/null)
#
#if [ -n "$PROTECTION" ]; then
#    echo -e "${GREEN}✅ Verification successful${NC}"
#    echo ""
#    echo "Current required status checks:"
#    echo "$PROTECTION" | grep -o '"contexts":\[.*\]' || echo "  (unable to parse)"
#    echo ""
#else
#    echo -e "${YELLOW}⚠️  Unable to verify settings (may still be applied)${NC}"
#fi
#
#echo ""
#echo "=================================================="
#echo "  Setup Complete!"
#echo "=================================================="
#echo ""
