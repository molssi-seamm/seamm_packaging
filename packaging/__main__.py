import json
from pathlib import Path

from .packaging import find_packages, create_env_files

if __name__ == "__main__":
    changed, packages = find_packages()
    if changed:
        print("Packages have changed, updating environment files")
        create_env_files(packages)
