#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Package build and test script
Build and test packages locally before PyPI deployment.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd, description="", check=True):
    """Execute command"""
    print(f"\n🔨 {description}")
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def clean_build_dirs():
    """Clean build directories"""
    print("\n🧹 Cleaning build directories")
    
    dirs_to_clean = ['dist', 'build', 'encoding_mcp.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Deleted: {dir_name}/")
    
    # Clean __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                print(f"Deleted: {full_path}")
                dirs.remove(dir_name)


def check_dependencies():
    """Check required dependencies"""
    print("\n📋 Checking required dependencies")
    
    required_packages = ['build', 'twine', 'pytest', 'flake8', 'mypy', 'black']
    missing_packages = []
    
    for package in required_packages:
        result = subprocess.run([sys.executable, '-m', package, '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            missing_packages.append(package)
        else:
            print(f"✅ {package}: installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with the following command:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_tests():
    """Run tests"""
    print("\n🧪 Running tests")
    
    # Linting
    if not run_command([sys.executable, '-m', 'flake8', 'encoding_mcp'], "Flake8 linting", check=False):
        print("⚠️ Linting warnings found, but continuing.")
    
    # Type checking
    if not run_command([sys.executable, '-m', 'mypy', 'encoding_mcp'], "MyPy type checking", check=False):
        print("⚠️ Type check warnings found, but continuing.")
    
    # Unit tests
    return run_command([sys.executable, '-m', 'pytest', 'tests/', '-v'], "Unit tests")


def build_package():
    """Build package"""
    print("\n📦 Building package")
    return run_command([sys.executable, '-m', 'build'], "Package build")


def check_package():
    """Validate package"""
    print("\n🔍 Validating package")
    
    # Validate package with twine
    if not run_command([sys.executable, '-m', 'twine', 'check', 'dist/*'], "Twine package validation"):
        return False
    
    # Check package contents
    dist_files = list(Path('dist').glob('*'))
    print(f"\n📄 Generated files:")
    for file in dist_files:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    return True


def test_installation():
    """Test package installation"""
    print("\n🚀 Testing package installation")
    
    # Find wheel file
    wheel_files = list(Path('dist').glob('*.whl'))
    if not wheel_files:
        print("❌ Wheel file not found.")
        return False
    
    wheel_file = wheel_files[0]
    
    # Test installation in temporary environment
    test_commands = [
        [sys.executable, '-m', 'pip', 'install', '--force-reinstall', str(wheel_file)],
        [sys.executable, '-c', 'import encoding_mcp; print(f"Version: {encoding_mcp.__version__}")'],
        [sys.executable, '-c', 'from encoding_mcp.server import main; print("Server module loaded successfully")']
    ]
    
    for cmd in test_commands:
        if not run_command(cmd, f"Installation test: {' '.join(cmd)}"):
            return False
    
    return True


def main():
    """Main function"""
    print("🚀 Encoding MCP Package Build and Test Script")
    print("=" * 50)
    
    # Check if current directory is project root
    if not Path('pyproject.toml').exists():
        print("❌ pyproject.toml file not found. Please run from project root.")
        sys.exit(1)
    
    steps = [
        ("Dependency check", check_dependencies),
        ("Clean build directories", clean_build_dirs),
        ("Run tests", run_tests),
        ("Build package", build_package),
        ("Validate package", check_package),
        ("Test installation", test_installation),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{'=' * 20} {step_name} {'=' * 20}")
        
        if callable(step_func):
            success = step_func()
        else:
            success = step_func
        
        if not success:
            failed_steps.append(step_name)
            print(f"❌ {step_name} failed")
        else:
            print(f"✅ {step_name} succeeded")
    
    print("\n" + "=" * 50)
    print("📊 Build and Test Results")
    print("=" * 50)
    
    if failed_steps:
        print(f"❌ Failed steps: {', '.join(failed_steps)}")
        print("\n⚠️ Please fix the issues and try again.")
        sys.exit(1)
    else:
        print("✅ All steps completed successfully!")
        print("\n🚀 Ready for PyPI deployment!")
        print("\nNext steps:")
        print("1. Upload to TestPyPI: twine upload --repository testpypi dist/*")
        print("2. Upload to PyPI: twine upload dist/*")
        print("3. Or auto-deploy with Git tag: git tag v1.x.x && git push origin v1.x.x")


if __name__ == '__main__':
    main()
