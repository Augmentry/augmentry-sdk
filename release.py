#!/usr/bin/env python3
"""
Release automation script for Augmentry Python SDK
"""

import subprocess
import sys
import os
import re
from typing import List, Optional

def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True, capture_output=True)

def get_current_version() -> Optional[str]:
    """Get the current version from __init__.py"""
    init_file = "augmentry/__init__.py"
    if not os.path.exists(init_file):
        return None
    
    with open(init_file, 'r') as f:
        content = f.read()
        match = re.search(r'__version__ = "([^"]+)"', content)
        return match.group(1) if match else None

def update_version_in_file(filepath: str, old_version: str, new_version: str) -> bool:
    """Update version in a specific file"""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Different patterns for different files
    if filepath.endswith('__init__.py'):
        pattern = f'__version__ = "{old_version}"'
        replacement = f'__version__ = "{new_version}"'
    elif filepath.endswith('setup.py'):
        pattern = f'version="{old_version}"'
        replacement = f'version="{new_version}"'
    elif filepath.endswith('pyproject.toml'):
        pattern = f'version = "{old_version}"'
        replacement = f'version = "{new_version}"'
    else:
        return False
    
    if pattern in content:
        content = content.replace(pattern, replacement)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Updated {filepath}: {old_version} → {new_version}")
        return True
    else:
        print(f"❌ Pattern not found in {filepath}: {pattern}")
        return False

def increment_version(version: str, part: str = "patch") -> str:
    """Increment version number"""
    major, minor, patch = map(int, version.split('.'))
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def build_package() -> bool:
    """Build the package"""
    print("\n🔨 Building package...")
    
    # Clean previous builds
    for dir_name in ["build", "dist", "*.egg-info"]:
        if dir_name.endswith("*"):
            # Handle glob patterns
            import glob
            for path in glob.glob(dir_name):
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
        else:
            if os.path.exists(dir_name):
                import shutil
                shutil.rmtree(dir_name)
    
    # Build
    try:
        result = run_command([sys.executable, "-m", "build"])
        print("✅ Package built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def validate_package() -> bool:
    """Validate the built package"""
    print("\n🔍 Validating package...")
    
    try:
        result = run_command([sys.executable, "-m", "twine", "check", "dist/*"])
        print("✅ Package validation passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package validation failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Main release function"""
    print("Augmentry Python SDK Release Tool")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("❌ Could not determine current version")
        return
    
    print(f"Current version: {current_version}")
    
    # Ask for new version or increment type
    print("\nOptions:")
    print("1. Auto-increment patch version (recommended)")
    print("2. Auto-increment minor version")
    print("3. Auto-increment major version")
    print("4. Enter custom version")
    
    # For automation, let's increment patch version
    new_version = increment_version(current_version, "patch")
    print(f"New version will be: {new_version}")
    
    # Update version in all files
    print("\n📝 Updating version numbers...")
    files_to_update = [
        "augmentry/__init__.py",
        "setup.py", 
        "pyproject.toml"
    ]
    
    all_updated = True
    for filepath in files_to_update:
        if not update_version_in_file(filepath, current_version, new_version):
            all_updated = False
    
    if not all_updated:
        print("❌ Failed to update all version files")
        return
    
    # Build package
    if not build_package():
        return
    
    # Validate package
    if not validate_package():
        return
    
    print("\n🎉 Release preparation complete!")
    print(f"Version updated: {current_version} → {new_version}")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Run: python -m twine upload --repository testpypi dist/* --skip-existing")
    print("3. Test the package from Test PyPI")
    print("4. Run: python -m twine upload dist/* --skip-existing")
    print("5. Verify the package is available on PyPI")

if __name__ == "__main__":
    main()