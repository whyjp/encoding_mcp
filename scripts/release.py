#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Release creation script
Create a new version tag and push to GitHub to trigger automatic deployment.
"""

import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd, description=""):
    """Execute command"""
    print(f"\n🔨 {description}")
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return None


def get_current_version():
    """Get current version"""
    try:
        # Get version from Git tags
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().lstrip('v')
        else:
            # Get from __init__.py if no tags
            init_file = Path('encoding_mcp/__init__.py')
            if init_file.exists():
                content = init_file.read_text(encoding='utf-8')
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error checking version: {e}")
    
    return "0.0.0"


def get_git_tags():
    """Get Git tag list"""
    result = run_command(['git', 'tag', '--list'], "Query existing tags")
    if result:
        return result.split('\n')
    return []


def validate_version(version):
    """Validate version format"""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$'
    return re.match(pattern, version) is not None


def increment_version(version, part='patch'):
    """Increment version"""
    parts = version.split('.')
    if len(parts) != 3:
        return None
    
    try:
        major, minor, patch = map(int, parts)
        
        if part == 'major':
            return f"{major + 1}.0.0"
        elif part == 'minor':
            return f"{major}.{minor + 1}.0"
        elif part == 'patch':
            return f"{major}.{minor}.{patch + 1}"
        else:
            return None
    except ValueError:
        return None


def check_git_status():
    """Check Git status"""
    print("\n📋 Checking Git status")
    
    # Check current branch
    branch = run_command(['git', 'branch', '--show-current'], "Check current branch")
    if not branch:
        return False
    
    print(f"Current branch: {branch}")
    
    # Check for changes
    status = run_command(['git', 'status', '--porcelain'], "Check for changes")
    if status:
        print("❌ Uncommitted changes found:")
        print(status)
        return False
    
    # Check sync with remote
    result = subprocess.run(['git', 'fetch'], capture_output=True)
    if result.returncode != 0:
        print("❌ Failed to fetch from remote repository")
        return False
    
    # Check local vs remote difference
    behind = run_command(['git', 'rev-list', '--count', 'HEAD..@{u}'], "Compare with remote")
    if behind and behind != '0':
        print(f"❌ Local is {behind} commits behind remote.")
        print("Please run git pull.")
        return False
    
    print("✅ Git status is clean")
    return True


def create_release():
    """Create release"""
    print("🚀 Encoding MCP Release Creation Script")
    print("=" * 50)
    
    # Check if project root
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml file not found. Please run from project root.")
        return False
    
    # Check Git status
    if not check_git_status():
        return False
    
    # Get current version
    current_version = get_current_version()
    print(f"\n📌 Current version: {current_version}")
    
    # Show existing tags
    tags = get_git_tags()
    if tags and tags != ['']:
        print(f"Existing tags: {', '.join(tags[-5:])}")  # Show last 5 only
    
    # Get new version input
    print("\nEnter new version:")
    print("1. Direct input (e.g., 1.2.0)")
    print("2. Auto increment:")
    print(f"   - patch (current: {current_version} → {increment_version(current_version, 'patch')})")
    print(f"   - minor (current: {current_version} → {increment_version(current_version, 'minor')})")
    print(f"   - major (current: {current_version} → {increment_version(current_version, 'major')})")
    
    choice = input("\nSelect (version number or patch/minor/major): ").strip()
    
    if choice in ['patch', 'minor', 'major']:
        new_version = increment_version(current_version, choice)
    elif validate_version(choice):
        new_version = choice
    else:
        print("❌ Invalid version format.")
        return False
    
    if not new_version:
        print("❌ Failed to generate version")
        return False
    
    # Check tag duplication
    tag_name = f"v{new_version}"
    if tag_name in tags:
        print(f"❌ Tag {tag_name} already exists.")
        return False
    
    # Confirm
    print(f"\n📋 Release information:")
    print(f"   Version: {new_version}")
    print(f"   Tag: {tag_name}")
    
    confirm = input("\nCreate release? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False
    
    # Create tag
    tag_message = f"Release version {new_version}"
    if not run_command(['git', 'tag', '-a', tag_name, '-m', tag_message], f"Create tag {tag_name}"):
        return False
    
    # Push tag
    if not run_command(['git', 'push', 'origin', tag_name], f"Push tag {tag_name}"):
        print("❌ Failed to push tag. Deleting local tag.")
        subprocess.run(['git', 'tag', '-d', tag_name])
        return False
    
    print(f"\n✅ Release {tag_name} created successfully!")
    print("\n🔄 GitHub Actions workflow will run automatically:")
    print("1. Run tests")
    print("2. Build package")
    print("3. Deploy to PyPI")
    
    print(f"\n🌐 Check progress on GitHub:")
    print("https://github.com/whyjp/encoding_mcp/actions")
    
    return True


if __name__ == '__main__':
    try:
        success = create_release()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
