"""
GitHub API utilities for extracting PR metadata.
Handles authentication and PR data retrieval.
"""

from github import Github
from github.PullRequest import PullRequest
from typing import Dict, Any, Optional
import sys


class GitHubAPI:
    """GitHub API wrapper for PR metadata extraction."""
    
    def __init__(self, token: str):
        """Initialize GitHub API client."""
        self.github = Github(token)
        self.user = self.github.get_user()
    
    def get_pull_request(self, repo_name: str, pr_number: int) -> PullRequest:
        """Get a specific pull request by repository name and PR number."""
        try:
            repo = self.github.get_repo(repo_name)
            return repo.get_pull(pr_number)
        except Exception as e:
            print(f"Error fetching PR {pr_number} from {repo_name}: {e}")
            sys.exit(1)
    
    def extract_pr_metadata(self, pr: PullRequest) -> Dict[str, Any]:
        """Extract comprehensive metadata from a pull request."""
        return {
            'number': pr.number,
            'title': pr.title,
            'description': pr.body or "No description provided",
            'author': pr.user.login,
            'author_name': pr.user.name or pr.user.login,
            'state': pr.state,
            'created_at': pr.created_at.isoformat(),
            'updated_at': pr.updated_at.isoformat(),
            'base_branch': pr.base.ref,
            'head_branch': pr.head.ref,
            'base_sha': pr.base.sha,
            'head_sha': pr.head.sha,
            'additions': pr.additions,
            'deletions': pr.deletions,
            'changed_files': pr.changed_files,
            'labels': [label.name for label in pr.labels],
            'assignees': [assignee.login for assignee in pr.assignees],
            'reviewers': [reviewer.login for reviewer in pr.requested_reviewers],
            'url': pr.html_url,
            'mergeable': pr.mergeable,
            'mergeable_state': pr.mergeable_state,
            'draft': pr.draft,
            'commits_count': pr.commits,
            'comments_count': pr.comments,
            'review_comments_count': pr.review_comments,
        }
    
    def get_pr_files(self, pr: PullRequest) -> list:
        """Get list of files changed in the PR."""
        try:
            return list(pr.get_files())
        except Exception as e:
            print(f"Error fetching PR files: {e}")
            return []
    
    def get_pr_comments(self, pr: PullRequest) -> list:
        """Get comments on the PR."""
        try:
            return list(pr.get_issue_comments())
        except Exception as e:
            print(f"Error fetching PR comments: {e}")
            return []
    
    def get_review_comments(self, pr: PullRequest) -> list:
        """Get review comments on the PR."""
        try:
            return list(pr.get_review_comments())
        except Exception as e:
            print(f"Error fetching review comments: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test GitHub API connection."""
        try:
            # Try to get the authenticated user
            _ = self.github.get_user()
            return True
        except Exception as e:
            print(f"GitHub API connection failed: {e}")
            return False 