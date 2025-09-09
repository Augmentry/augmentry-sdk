#!/usr/bin/env python3
"""
Script to upload the augmentry package to PyPI
Run this script manually with your PyPI credentials
"""

import subprocess
import sys
import os

def upload_to_pypi():
    """Upload the package to PyPI"""
    
    print("Augmentry Python SDK - PyPI Upload")
    print("=" * 50)
    
    # Check if dist folder exists
    if not os.path.exists("dist"):
        print("❌ Error: dist/ folder not found. Run 'python -m build' first.")
        return False
    
    # List files in dist
    dist_files = os.listdir("dist")
    print(f"Files to upload: {dist_files}")
    
    # Check if twine is installed
    try:
        result = subprocess.run([sys.executable, "-m", "twine", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"Twine version: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ Error: twine not installed. Run 'pip install twine'")
        return False
    
    # Validate packages first
    print("\nValidating packages...")
    try:
        result = subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"], 
                              check=True, text=True)
        print("✅ Package validation passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package validation failed: {e}")
        return False
    
    print("\nTo upload to PyPI, run one of these commands:")
    print("\n1. Upload to Test PyPI (recommended first):")
    print("   python -m twine upload --repository testpypi dist/* --skip-existing")
    print("   You'll need your TestPyPI API token")
    
    print("\n2. Upload to main PyPI:")
    print("   python -m twine upload dist/* --skip-existing")
    print("   You'll need your PyPI API token")
    
    print("\n3. Or set up credentials in ~/.pypirc:")
    print("""
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = YOUR_PYPI_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = YOUR_TESTPYPI_API_TOKEN_HERE
""")
    
    return True

def check_version_consistency():
    """Check that version is consistent across files"""
    print("\nChecking version consistency...")
    
    # Check __init__.py
    init_file = "augmentry/__init__.py"
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
            if '__version__ = "1.0.2"' in content:
                print("✅ __init__.py version: 1.0.2")
            else:
                print("❌ __init__.py version mismatch")
                return False
    
    # Check setup.py
    setup_file = "setup.py"
    if os.path.exists(setup_file):
        with open(setup_file, 'r') as f:
            content = f.read()
            if 'version="1.0.2"' in content:
                print("✅ setup.py version: 1.0.2")
            else:
                print("❌ setup.py version mismatch")
                return False
    
    # Check pyproject.toml
    pyproject_file = "pyproject.toml"
    if os.path.exists(pyproject_file):
        with open(pyproject_file, 'r') as f:
            content = f.read()
            if 'version = "1.0.2"' in content:
                print("✅ pyproject.toml version: 1.0.2")
            else:
                print("❌ pyproject.toml version mismatch")
                return False
    
    print("✅ All versions are consistent: 1.0.2")
    return True

def main():
    """Main function"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Working directory: {os.getcwd()}")
    
    # Check version consistency
    if not check_version_consistency():
        return
    
    # Upload
    upload_to_pypi()

if __name__ == "__main__":
    main()