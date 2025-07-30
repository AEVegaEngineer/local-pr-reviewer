"""
Git operations utilities for generating diffs between branches.
Handles local git operations and diff formatting.
"""

import subprocess
import tempfile
import os
from typing import Optional, Tuple
import sys


class GitOps:
    """Git operations wrapper for diff generation."""
    
    def __init__(self, repo_path: Optional[str] = None, github_token: Optional[str] = None):
        """Initialize GitOps with optional repository path and GitHub token."""
        self.repo_path = repo_path or os.getcwd()
        self.github_token = github_token
        # Use environment variable for cache directory (Docker compatibility)
        self.repo_cache_dir = os.getenv('PR_REVIEWER_CACHE_DIR', 
                                       os.path.join(os.path.expanduser("~"), ".pr_reviewer_cache"))
        os.makedirs(self.repo_cache_dir, exist_ok=True)
    
    def get_cached_repo_path(self, repo_name: str) -> str:
        """Get the path to a cached repository."""
        # Convert repo name to safe directory name
        safe_name = repo_name.replace('/', '_')
        return os.path.join(self.repo_cache_dir, safe_name)
    
    def is_repo_cached(self, repo_name: str) -> bool:
        """Check if a repository is already cached."""
        cached_path = self.get_cached_repo_path(repo_name)
        return os.path.exists(cached_path) and self.is_git_repo(cached_path)
    
    def get_authenticated_repo_url(self, repo_name: str) -> str:
        """Get authenticated repository URL using GitHub token."""
        if self.github_token:
            return f"https://{self.github_token}@github.com/{repo_name}.git"
        else:
            return f"https://github.com/{repo_name}.git"
    
    def clone_or_update_repository(self, repo_url: str, repo_name: str) -> str:
        """Clone a repository or update existing one."""
        cached_path = self.get_cached_repo_path(repo_name)
        
        if self.is_repo_cached(repo_name):
            print(f"Repository already cached at {cached_path}, checking for updates...")
            return self.update_cached_repository(cached_path, repo_name)
        else:
            print(f"Cloning repository to {cached_path}...")
            # Use authenticated URL for cloning
            auth_repo_url = self.get_authenticated_repo_url(repo_name)
            return self.clone_repository_to_path(auth_repo_url, cached_path)
    
    def clone_repository_to_path(self, repo_url: str, target_path: str) -> str:
        """Clone a repository to a specific path."""
        try:
            # Remove existing directory if it exists
            if os.path.exists(target_path):
                import shutil
                shutil.rmtree(target_path)
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", repo_url, target_path],
                capture_output=True, 
                text=True, 
                check=True
            )
            print(f"Repository cloned to {target_path}")
            return target_path
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            print(f"stderr: {e.stderr}")
            if "could not read Username" in e.stderr or "Authentication failed" in e.stderr:
                print("This appears to be a private repository. Please ensure your GitHub token has 'repo' permissions.")
            sys.exit(1)
    
    def update_cached_repository(self, repo_path: str, repo_name: str) -> str:
        """Update an existing cached repository."""
        try:
            # Configure git to use token for authentication if available
            if self.github_token:
                subprocess.run(
                    ["git", "config", "credential.helper", "store"],
                    cwd=repo_path, 
                    check=True, 
                    capture_output=True
                )
                
                # Set up credential helper to use token
                credential_url = f"https://{self.github_token}@github.com"
                subprocess.run(
                    ["git", "config", "credential.helper", f"!echo 'username={self.github_token}'; echo 'password={self.github_token}'"],
                    cwd=repo_path, 
                    check=True, 
                    capture_output=True
                )
            
            # Fetch all branches and tags
            subprocess.run(
                ["git", "fetch", "--all", "--tags"], 
                cwd=repo_path, 
                check=True, 
                capture_output=True
            )
            
            # Check if we need to update (compare local and remote)
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                cwd=repo_path, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip() != "0":
                print(f"Repository is {result.stdout.strip()} commits behind, updating...")
                # Reset to match remote
                subprocess.run(
                    ["git", "reset", "--hard", "origin/main"], 
                    cwd=repo_path, 
                    check=True, 
                    capture_output=True
                )
                
                # Clean untracked files
                subprocess.run(
                    ["git", "clean", "-fd"], 
                    cwd=repo_path, 
                    check=True, 
                    capture_output=True
                )
                
                print(f"Repository updated at {repo_path}")
            else:
                print(f"Repository is up to date at {repo_path}")
            
            return repo_path
        except subprocess.CalledProcessError as e:
            print(f"Error updating repository: {e}")
            # If update fails, try to re-clone
            print("Update failed, re-cloning repository...")
            auth_repo_url = self.get_authenticated_repo_url(repo_name)
            return self.clone_repository_to_path(auth_repo_url, repo_path)
    
    def fetch_and_checkout(self, repo_path: str, branch: str) -> bool:
        """Fetch and checkout a specific branch."""
        try:
            # Fetch all branches
            subprocess.run(["git", "fetch", "--all"], 
                         cwd=repo_path, check=True, capture_output=True)
            
            # Checkout the branch
            subprocess.run(["git", "checkout", branch], 
                         cwd=repo_path, check=True, capture_output=True)
            
            # Pull latest changes
            subprocess.run(["git", "pull", "origin", branch], 
                         cwd=repo_path, check=True, capture_output=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error fetching/checkout branch {branch}: {e}")
            return False
    
    def get_diff(self, repo_path: str, base_branch: str, head_branch: str) -> str:
        """Generate diff between two branches."""
        try:
            # Ensure we're on the base branch
            self.fetch_and_checkout(repo_path, base_branch)
            
            # Generate diff
            cmd = ["git", "diff", f"origin/{base_branch}...origin/{head_branch}"]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error generating diff: {e}")
            return ""
    
    def get_diff_stat(self, repo_path: str, base_branch: str, head_branch: str) -> str:
        """Generate diff statistics between two branches."""
        try:
            # Ensure we're on the base branch
            self.fetch_and_checkout(repo_path, base_branch)
            
            # Generate diff stats
            cmd = ["git", "diff", "--stat", f"origin/{base_branch}...origin/{head_branch}"]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error generating diff stats: {e}")
            return ""
    
    def get_commit_history(self, repo_path: str, base_branch: str, head_branch: str) -> str:
        """Get commit history between two branches."""
        try:
            # Ensure we're on the base branch
            self.fetch_and_checkout(repo_path, base_branch)
            
            # Get commit history
            cmd = ["git", "log", "--oneline", f"origin/{base_branch}..origin/{head_branch}"]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history: {e}")
            return ""
    
    def get_file_list(self, repo_path: str, base_branch: str, head_branch: str) -> list:
        """Get list of files changed between two branches."""
        try:
            # Ensure we're on the base branch
            self.fetch_and_checkout(repo_path, base_branch)
            
            # Get list of changed files
            cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...origin/{head_branch}"]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Error getting file list: {e}")
            return []
    
    def cleanup_cache(self):
        """Clean up the entire cache directory."""
        try:
            import shutil
            if os.path.exists(self.repo_cache_dir):
                shutil.rmtree(self.repo_cache_dir)
                print(f"Cleaned up cache directory: {self.repo_cache_dir}")
        except Exception as e:
            print(f"Error cleaning up cache directory: {e}")
    
    def cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Error cleaning up temporary directory: {e}")
    
    def is_git_repo(self, path: str) -> bool:
        """Check if a path is a git repository."""
        try:
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  cwd=path, capture_output=True, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False 