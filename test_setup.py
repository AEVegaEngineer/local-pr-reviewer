#!/usr/bin/env python3
"""
Test script to verify PR Reviewer Helper setup.
Run this to check if everything is configured correctly.
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    required_packages = [
        'github',
        'dotenv',
        'click'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            return False
    
    return True

def test_local_imports():
    """Test if local modules can be imported."""
    print("\nTesting local imports...")
    
    local_modules = [
        'config',
        'utils.github_api',
        'utils.git_ops',
        'utils.file_writer'
    ]
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config import get_config
        config = get_config()
        
        # Test if required env vars are set
        if hasattr(config, 'github_token') and hasattr(config, 'github_username') and hasattr(config, 'repository'):
            print("✅ Configuration structure is correct")
            return True
        else:
            print("❌ Configuration is missing required attributes")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests."""
    print("PR Reviewer Helper - Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test local imports
    if not test_local_imports():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Copy env.template to .env")
        print("2. Add your GitHub token, username, and repository to .env")
        print("3. Run: python main.py 123")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 