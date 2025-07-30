#!/usr/bin/env python3
"""
PR Reviewer Helper - Main CLI entry point.
Automates personal code reviews by extracting GitHub PR metadata and generating readable diffs.
"""

import sys
import argparse
from typing import Optional

from config import get_config
from utils.github_api import GitHubAPI
from utils.git_ops import GitOps
from utils.file_writer import FileWriter


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive PR review file for ChatGPT analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py 123
  python main.py 456 --output-dir ./reviews
  python main.py 789 --include-comments --include-review-comments
  python main.py --pr 123
  python main.py --pr 456 --output-dir ./reviews
        """
    )
    
    # Support both positional and --pr argument for Docker compatibility
    parser.add_argument(
        'pr_number',
        nargs='?',
        type=int,
        help='Pull request number (can also use --pr)'
    )
    
    parser.add_argument(
        '--pr',
        type=int,
        help='Pull request number (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./reviews',
        help='Output directory for review files (default: ./reviews)'
    )
    
    parser.add_argument(
        '--include-comments',
        action='store_true',
        help='Include PR comments in the review file'
    )
    
    parser.add_argument(
        '--include-review-comments',
        action='store_true',
        help='Include review comments in the review file'
    )
    
    parser.add_argument(
        '--skip-diff',
        action='store_true',
        help='Skip generating diff (useful for large PRs)'
    )
    
    parser.add_argument(
        '--clean-cache',
        action='store_true',
        help='Clean the repository cache before running'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    # Determine PR number from either positional argument or --pr flag
    pr_number = args.pr or args.pr_number
    if pr_number is None:
        print("Error: PR number is required. Use either positional argument or --pr flag.")
        print("Examples:")
        print("  python main.py 123")
        print("  python main.py --pr 123")
        sys.exit(1)
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = get_config()
        
        if not config.validate():
            print("Error: Invalid configuration. Please check your .env file.")
            sys.exit(1)
        
        if not config.validate_repository_format():
            print("Error: Repository format in GITHUB_REPOSITORY is invalid. Must be 'owner/repo'")
            sys.exit(1)
        
        # Initialize GitHub API
        print("Initializing GitHub API...")
        github_api = GitHubAPI(config.github_token)
        
        if not github_api.test_connection():
            print("Error: Failed to connect to GitHub API. Please check your token.")
            sys.exit(1)
        
        # Get PR data
        print(f"Fetching PR #{pr_number} from {config.repository}...")
        pr = github_api.get_pull_request(config.repository, pr_number)
        metadata = github_api.extract_pr_metadata(pr)
        
        print(f"PR Title: {metadata['title']}")
        print(f"Author: {metadata['author_name']}")
        print(f"Changes: +{metadata['additions']} -{metadata['deletions']} lines")
        
        # Initialize file writer
        file_writer = FileWriter(args.output_dir)
        
        # Get comments if requested
        comments = None
        if args.include_comments:
            print("Fetching PR comments...")
            comments = github_api.get_pr_comments(pr)
        
        review_comments = None
        if args.include_review_comments:
            print("Fetching review comments...")
            review_comments = github_api.get_review_comments(pr)
        
        # Generate diff if not skipped
        diff_content = ""
        diff_stats = ""
        commit_history = ""
        
        if not args.skip_diff:
            print("Setting up repository for diff generation...")
            # Pass GitHub token to GitOps for authenticated access
            git_ops = GitOps(github_token=config.github_token)
            
            # Clean cache if requested
            if args.clean_cache:
                print("Cleaning repository cache...")
                git_ops.cleanup_cache()
            
            # Clone or update repository
            repo_url = f"https://github.com/{config.repository}.git"
            repo_path = git_ops.clone_or_update_repository(repo_url, config.repository)
            
            try:
                # Get diff content
                diff_content = git_ops.get_diff(
                    repo_path, 
                    metadata['base_branch'], 
                    metadata['head_branch']
                )
                
                # Get diff statistics
                diff_stats = git_ops.get_diff_stat(
                    repo_path, 
                    metadata['base_branch'], 
                    metadata['head_branch']
                )
                
                # Get commit history
                commit_history = git_ops.get_commit_history(
                    repo_path, 
                    metadata['base_branch'], 
                    metadata['head_branch']
                )
                
            except Exception as e:
                print(f"Error generating diff: {e}")
                print("Continuing without diff content...")
        
        # Write review file
        print("Writing review file...")
        output_file = file_writer.write_review_file(
            repo_name=config.repository,
            pr_number=pr_number,
            metadata=metadata,
            diff_content=diff_content,
            diff_stats=diff_stats,
            comments=comments,
            review_comments=review_comments,
            commit_history=commit_history
        )
        
        if output_file:
            file_size = file_writer.get_file_size(output_file)
            print(f"\n✅ Review file generated successfully!")
            print(f"📁 File: {output_file}")
            print(f"📊 Size: {file_size}")
            print(f"\nYou can now copy the contents of this file to ChatGPT for analysis.")
        else:
            print("❌ Failed to generate review file.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 