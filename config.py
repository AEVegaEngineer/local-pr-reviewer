"""
Configuration management for PR Reviewer Helper.
Handles environment variables and provides configuration utilities.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the PR Reviewer Helper."""
    
    def __init__(self):
        self.github_token = self._get_required_env('GITHUB_TOKEN')
        self.github_username = self._get_required_env('GITHUB_USERNAME')
        self.repository = self._get_required_env('GITHUB_REPOSITORY')
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set. "
                           f"Please add it to your .env file.")
        return value
    
    def _get_optional_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an optional environment variable."""
        return os.getenv(key, default)
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        try:
            # Test that required values are set
            _ = self.github_token
            _ = self.github_username
            _ = self.repository
            return True
        except ValueError:
            return False
    
    def validate_repository_format(self) -> bool:
        """Validate repository format."""
        if '/' not in self.repository or self.repository.count('/') != 1:
            return False
        owner, repo = self.repository.split('/')
        return bool(owner and repo)


def get_config() -> Config:
    """Get the application configuration."""
    return Config() 