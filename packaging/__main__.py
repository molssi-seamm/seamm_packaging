import json
from pathlib import Path

from .packaging import find_packages, create_env_files

if __name__ == "__main__":
    changed, packages = find_packages()
    if True or changed:
        create_env_files(packages)
