"""
Package Renaming Script
Rename litenetlib-python to litenetlib-0952 for better version identification
"""

import os
import shutil

def rename_in_file(file_path, old_name, new_name):
    """Replace package name in file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(old_name, new_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated: {file_path}")

def main():
    old_name = "litenetlib-python"
    new_name = "litenetlib-0952"
    
    print(f"Renaming package: {old_name} -> {new_name}\n")
    
    # Files to update
    files_to_update = [
        "setup.py",
        "pyproject.toml",
        "README.md",
        "PYPI_PUBLISHING_GUIDE.md",
        "PYPI_QUICK_REFERENCE.md",
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            rename_in_file(file_path, old_name, new_name)
    
    # Also update import in some Python files
    py_files = [
        "publish_to_testpypi.py",
        "test_testpypi_simple.py",
        "test_testpypi_install.py",
    ]
    
    for file_path in py_files:
        if os.path.exists(file_path):
            # Only update mentions in comments/docstrings
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated = False
            for i, line in enumerate(lines):
                if old_name in line and not line.strip().startswith('import'):
                    lines[i] = line.replace(old_name, new_name)
                    updated = True
            
            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"  Updated: {file_path}")
    
    print(f"\nDone! Package renamed to: {new_name}")

if __name__ == "__main__":
    main()
