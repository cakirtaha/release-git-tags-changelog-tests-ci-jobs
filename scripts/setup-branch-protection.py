# #!/usr/bin/env python3
#
# """
# Branch Protection Setup Script (Python)
# ========================================
#
# This script configures branch protection for the master branch using the
# GitHub API. It ensures all CI jobs must pass before merging.
#
# Prerequisites:
# - Python 3.7+
# - requests library: pip install requests
# - GitHub token with repo permissions
#
# Usage:
#     # Using environment variable
#     export GITHUB_TOKEN="your_token_here"
#     python setup-branch-protection.py
#
#     # Or using gh CLI token
#     export GITHUB_TOKEN=$(gh auth token)
#     python setup-branch-protection.py
# """
#
# import os
# import sys
# from typing import Any
#
# import requests
#
# # Configuration
# OWNER = os.getenv("GITHUB_OWNER", "")  # Set via environment or edit here
# REPO = os.getenv("GITHUB_REPO", "")  # Set via environment or edit here
# BRANCH = "master"
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
#
# # Branch Protection Configuration
# PROTECTION_CONFIG: dict[str, Any] = {
#     "required_status_checks": {
#         "strict": True,  # Require branch to be up to date before merging
#         "contexts": [
#             "quality",  # Code Quality job from ci.yml
#             "deploy",  # Deploy job from ci.yml
#         ],
#     },
#     "enforce_admins": True,  # Apply rules to administrators too
#     "required_pull_request_reviews": {
#         "dismiss_stale_reviews": True,  # Re-approve after new commits
#         "require_code_owner_reviews": False,  # Don't require CODEOWNERS approval
#         "required_approving_review_count": 1,  # Number of approvals needed
#         "require_last_push_approval": True,  # Approve most recent push
#         "dismissal_restrictions": {},  # No restrictions on who can dismiss
#     },
#     "restrictions": None,  # No push restrictions (blocks all direct pushes)
#     "required_linear_history": True,  # Prevent merge commits
#     "allow_force_pushes": False,  # Block force pushes
#     "allow_deletions": False,  # Block branch deletion
#     "required_conversation_resolution": True,  # Resolve all comments
#     "lock_branch": False,  # Don't lock branch (allow PRs)
#     "allow_fork_syncing": True,  # Allow fork syncing
# }
#
#
# def print_header(text: str) -> None:
#     """Print formatted header"""
#     print("")
#     print("=" * 60)
#     print(f"  {text}")
#     print("=" * 60)
#     print("")
#
#
# def print_success(text: str) -> None:
#     """Print success message"""
#     print(f"✅ {text}")
#
#
# def print_error(text: str) -> None:
#     """Print error message"""
#     print(f"❌ {text}", file=sys.stderr)
#
#
# def print_warning(text: str) -> None:
#     """Print warning message"""
#     print(f"⚠️  {text}")
#
#
# def print_info(text: str) -> None:
#     """Print info message"""
#     print(f"ℹ️  {text}")
#
#
# def get_repo_info() -> tuple:
#     """Get repository information from git remote"""
#     import subprocess
#
#     try:
#         # Get remote URL
#         result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
#         remote_url = result.stdout.strip()
#
#         # Parse owner and repo from URL
#         # Handles both HTTPS and SSH URLs
#         if "github.com" in remote_url:
#             # Remove .git suffix
#             remote_url = remote_url.replace(".git", "")
#
#             # Extract owner/repo
#             if "https://" in remote_url:
#                 # https://github.com/owner/repo
#                 parts = remote_url.split("github.com/")[1].split("/")
#             else:
#                 # git@github.com:owner/repo
#                 parts = remote_url.split(":")[1].split("/")
#
#             if len(parts) >= 2:
#                 return parts[0], parts[1]
#
#         return None, None
#
#     except subprocess.CalledProcessError:
#         return None, None
#
#
# def apply_branch_protection(owner: str, repo: str, branch: str, token: str) -> bool:
#     """
#     Apply branch protection rules using GitHub API
#
#     Args:
#         owner: Repository owner
#         repo: Repository name
#         branch: Branch name to protect
#         token: GitHub personal access token
#
#     Returns:
#         True if successful, False otherwise
#     """
#     url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
#
#     headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"}
#
#     print("Applying branch protection...")
#     print("")
#
#     try:
#         response = requests.put(url, headers=headers, json=PROTECTION_CONFIG, timeout=30)
#
#         if response.status_code == 200:
#             print_success("Branch protection applied successfully!")
#             return True
#         elif response.status_code == 401:
#             print_error("Authentication failed. Check your GITHUB_TOKEN.")
#             print_info("Generate a token at: https://github.com/settings/tokens")
#             print_info("Required scopes: repo (full control)")
#             return False
#         elif response.status_code == 403:
#             print_error("Permission denied. You need admin access to this repository.")
#             return False
#         elif response.status_code == 404:
#             print_error(f"Repository or branch not found: {owner}/{repo}/{branch}")
#             print_info("Make sure the branch exists and you have access.")
#             return False
#         else:
#             print_error(f"Failed with status code: {response.status_code}")
#             print_error(f"Response: {response.text}")
#             return False
#
#     except requests.exceptions.RequestException as e:
#         print_error(f"Request failed: {e}")
#         return False
#
#
# def verify_protection(owner: str, repo: str, branch: str, token: str) -> None:
#     """Verify branch protection is configured correctly"""
#     url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
#
#     headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"}
#
#     print("")
#     print("Verifying configuration...")
#     print("")
#
#     try:
#         response = requests.get(url, headers=headers, timeout=30)
#
#         if response.status_code == 200:
#             data = response.json()
#             print_success("Verification successful")
#             print("")
#             print("Current settings:")
#             print(f"  • Required status checks: {data.get('required_status_checks', {}).get('contexts', [])}")
#             print(f"  • Required approvals: {data.get('required_pull_request_reviews', {}).get('required_approving_review_count', 0)}")
#             print(f"  • Enforce for admins: {data.get('enforce_admins', {}).get('enabled', False)}")
#             print(f"  • Linear history: {data.get('required_linear_history', {}).get('enabled', False)}")
#         else:
#             print_warning("Unable to verify settings (may still be applied)")
#
#     except requests.exceptions.RequestException:
#         print_warning("Verification request failed (settings may still be applied)")
#
#
# def main():
#     """Main execution function"""
#     print_header("Branch Protection Setup")
#
#     # Get configuration
#     owner = OWNER
#     repo = REPO
#
#     # Auto-detect repository if not specified
#     if not owner or not repo:
#         print_info("Auto-detecting repository from git remote...")
#         owner, repo = get_repo_info()
#
#         if not owner or not repo:
#             print_error("Unable to detect repository. Please set GITHUB_OWNER and GITHUB_REPO")
#             print("")
#             print("Usage:")
#             print("  export GITHUB_OWNER=your-username")
#             print("  export GITHUB_REPO=your-repo")
#             print("  python setup-branch-protection.py")
#             sys.exit(1)
#
#     # Check for GitHub token
#     if not GITHUB_TOKEN:
#         print_error("GITHUB_TOKEN environment variable not set")
#         print("")
#         print("Get your token from: https://github.com/settings/tokens")
#         print("Required scopes: repo (full control)")
#         print("")
#         print("Then set it:")
#         print("  export GITHUB_TOKEN=your_token_here")
#         print("")
#         print("Or use GitHub CLI:")
#         print("  export GITHUB_TOKEN=$(gh auth token)")
#         sys.exit(1)
#
#     # Display configuration
#     print(f"📦 Repository: {owner}/{repo}")
#     print(f"🌿 Branch: {BRANCH}")
#     print("")
#
#     # Show what will be configured
#     print("Configuration to be applied:")
#     print("")
#     print("✅ Require status checks to pass before merging")
#     print(f"   - Required checks: {', '.join(PROTECTION_CONFIG['required_status_checks']['contexts'])}")
#     print("   - Require branch to be up to date")
#     print("")
#     print("✅ Require pull request reviews")
#     print(f"   - Required approving reviews: {PROTECTION_CONFIG['required_pull_request_reviews']['required_approving_review_count']}")
#     print("   - Dismiss stale reviews on new commits")
#     print("   - Require approval of most recent push")
#     print("")
#     print("✅ Require conversation resolution before merging")
#     print("✅ Require linear history (no merge commits)")
#     print("✅ Enforce restrictions for administrators")
#     print("❌ Block force pushes")
#     print("❌ Block branch deletion")
#     print("")
#
#     # Confirm
#     response = input("Apply these settings? (y/N): ")
#     if response.lower() not in ["y", "yes"]:
#         print_warning("Cancelled")
#         sys.exit(0)
#
#     print("")
#
#     # Apply protection
#     success = apply_branch_protection(owner, repo, BRANCH, GITHUB_TOKEN)
#
#     if success:
#         # Show summary
#         print("")
#         print("Summary:")
#         print(f"  • Direct pushes to '{BRANCH}' are now blocked")
#         print("  • All changes must go through Pull Requests")
#         print(f"  • CI jobs ({', '.join(PROTECTION_CONFIG['required_status_checks']['contexts'])}) must pass")
#         print(f"  • {PROTECTION_CONFIG['required_pull_request_reviews']['required_approving_review_count']} approval(s) required")
#         print("")
#         print("View settings at:")
#         print(f"  https://github.com/{owner}/{repo}/settings/branches")
#
#         # Verify
#         verify_protection(owner, repo, BRANCH, GITHUB_TOKEN)
#
#         print("")
#         print_header("Setup Complete!")
#     else:
#         print("")
#         print_header("Setup Failed")
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("")
#         print_warning("Cancelled by user")
#         sys.exit(0)
