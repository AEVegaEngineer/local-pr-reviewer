"""
File writer utilities for formatting and outputting PR review data.
Handles formatting for ChatGPT readability.
"""

import os
from datetime import datetime
from typing import Dict, Any, List


class FileWriter:
    """File writer for formatting PR review data."""
    
    def __init__(self, output_dir: str = "."):
        """Initialize FileWriter with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def format_metadata_section(self, metadata: Dict[str, Any]) -> str:
        """Format PR metadata into a readable section."""
        section = "=" * 80 + "\n"
        section += "PULL REQUEST METADATA\n"
        section += "=" * 80 + "\n\n"
        
        # Basic information
        section += f"PR #{metadata['number']}: {metadata['title']}\n"
        section += f"Author: {metadata['author_name']} (@{metadata['author']})\n"
        section += f"State: {metadata['state'].upper()}\n"
        section += f"URL: {metadata['url']}\n\n"
        
        # Branch information
        section += f"Base Branch: {metadata['base_branch']}\n"
        section += f"Head Branch: {metadata['head_branch']}\n"
        section += f"Base SHA: {metadata['base_sha'][:8]}\n"
        section += f"Head SHA: {metadata['head_sha'][:8]}\n\n"
        
        # Statistics
        section += f"Changes: +{metadata['additions']} -{metadata['deletions']} lines\n"
        section += f"Files Changed: {metadata['changed_files']}\n"
        section += f"Commits: {metadata['commits_count']}\n"
        section += f"Comments: {metadata['comments_count']}\n"
        section += f"Review Comments: {metadata['review_comments_count']}\n\n"
        
        # Labels and assignees
        if metadata['labels']:
            section += f"Labels: {', '.join(metadata['labels'])}\n"
        if metadata['assignees']:
            section += f"Assignees: {', '.join(metadata['assignees'])}\n"
        if metadata['reviewers']:
            section += f"Reviewers: {', '.join(metadata['reviewers'])}\n"
        section += "\n"
        
        # Timestamps
        section += f"Created: {metadata['created_at']}\n"
        section += f"Updated: {metadata['updated_at']}\n\n"
        
        # Description
        section += "DESCRIPTION:\n"
        section += "-" * 40 + "\n"
        section += metadata['description'] + "\n\n"
        
        return section
    
    def format_diff_section(self, diff_content: str, diff_stats: str = "") -> str:
        """Format diff content into a readable section."""
        section = "=" * 80 + "\n"
        section += "CODE CHANGES\n"
        section += "=" * 80 + "\n\n"
        
        if diff_stats:
            section += "CHANGE SUMMARY:\n"
            section += "-" * 40 + "\n"
            section += diff_stats + "\n\n"
        
        section += "DETAILED DIFF:\n"
        section += "-" * 40 + "\n"
        section += diff_content + "\n\n"
        
        return section
    
    def format_comments_section(self, comments: List[Any]) -> str:
        """Format PR comments into a readable section."""
        if not comments:
            return ""
        
        section = "=" * 80 + "\n"
        section += "COMMENTS\n"
        section += "=" * 80 + "\n\n"
        
        for i, comment in enumerate(comments, 1):
            section += f"Comment #{i} by @{comment.user.login}:\n"
            section += f"Posted: {comment.created_at.isoformat()}\n"
            section += "-" * 40 + "\n"
            section += comment.body + "\n\n"
        
        return section
    
    def format_review_comments_section(self, review_comments: List[Any]) -> str:
        """Format review comments into a readable section."""
        if not review_comments:
            return ""
        
        section = "=" * 80 + "\n"
        section += "REVIEW COMMENTS\n"
        section += "=" * 80 + "\n\n"
        
        for i, comment in enumerate(review_comments, 1):
            section += f"Review Comment #{i} by @{comment.user.login}:\n"
            section += f"File: {comment.path}\n"
            section += f"Line: {comment.line}\n"
            section += f"Posted: {comment.created_at.isoformat()}\n"
            section += "-" * 40 + "\n"
            section += comment.body + "\n\n"
        
        return section
    
    def format_commit_history_section(self, commit_history: str) -> str:
        """Format commit history into a readable section."""
        if not commit_history:
            return ""
        
        section = "=" * 80 + "\n"
        section += "COMMIT HISTORY\n"
        section += "=" * 80 + "\n\n"
        section += commit_history + "\n\n"
        
        return section
    
    def write_review_file(self, 
                         repo_name: str, 
                         pr_number: int, 
                         metadata: Dict[str, Any],
                         diff_content: str = "",
                         diff_stats: str = "",
                         comments: List[Any] = None,
                         review_comments: List[Any] = None,
                         commit_history: str = "") -> str:
        """Write complete PR review data to a formatted text file."""
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pr_review_{repo_name.replace('/', '_')}_{pr_number}_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        # Build content
        content = ""
        content += self.format_metadata_section(metadata)
        
        if commit_history:
            content += self.format_commit_history_section(commit_history)
        
        if diff_content or diff_stats:
            content += self.format_diff_section(diff_content, diff_stats)
        
        if comments:
            content += self.format_comments_section(comments)
        
        if review_comments:
            content += self.format_review_comments_section(review_comments)
        
        # Add footer
        content += "=" * 80 + "\n"
        content += f"Review generated on: {datetime.now().isoformat()}\n"
        content += f"Repository: {repo_name}\n"
        content += f"Pull Request: #{pr_number}\n"
        content += "=" * 80 + "\n"
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Review file written to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error writing review file: {e}")
            return ""
    
    def get_file_size(self, filepath: str) -> str:
        """Get human-readable file size."""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except Exception:
            return "Unknown" 