# -*- coding: utf-8 -*-

"""Resolve the SEAMM package list into a universal lock file with uv.

``uv pip compile --universal`` solves the whole package set once, for every
platform, from PyPI, and writes a pinned requirements file with environment
markers where a dependency is platform-specific. That file is the "known-good
set" the installer passes to ``uv pip install`` as constraints, and the
versions it pins for the SEAMM packages themselves are what the package list
records.
"""

import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from .metadata import metadata

logger = logging.getLogger("seamm_packages")

PACKAGE_TYPES = ("Core package", "MolSSI plug-in", "3rd-party plug-in")

# Lines in a compiled requirements file look like
#     name==1.2.3
#     name==1.2.3 ; sys_platform == 'win32'
# with comment lines ("    # via ...") in between.
_PIN = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)==(?P<version>[^\s;]+)")


def normalize(name):
    """The canonical form of a distribution name: lower case, '-' separators."""
    return re.sub(r"[-_.]+", "-", name).lower()


def find_uv():
    """The path to the ``uv`` executable.

    Looks on ``PATH`` first, then where uv's own installer puts it.
    """
    uv = shutil.which("uv")
    if uv is None:
        candidate = Path.home() / ".local" / "bin" / "uv"
        if candidate.exists():
            uv = str(candidate)
    if uv is None:
        raise RuntimeError(
            "Cannot find 'uv'. Install it with\n"
            "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        )
    return uv


def package_names():
    """All the installable packages in the metadata, in a stable order."""
    names = []
    for _type in PACKAGE_TYPES:
        names.extend(sorted(metadata[_type]))
    return names


def compile_lock(names, python_version="3.12", uv=None):
    """Run ``uv pip compile --universal`` over ``names`` and return the lock text.

    Parameters
    ----------
    names : [str]
        The packages to resolve (top-level requirements, unpinned).
    python_version : str
        The minimum Python version the lock must satisfy.
    uv : str or None
        Path to uv; found automatically if None.

    Returns
    -------
    str
        The compiled, pinned requirements ("lock") text.
    """
    if uv is None:
        uv = find_uv()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        requirements = tmp / "requirements.in"
        requirements.write_text("\n".join(names) + "\n")
        lock = tmp / "seamm.lock.txt"
        command = [
            uv,
            "pip",
            "compile",
            "--universal",
            f"--python-version={python_version}",
            "--no-header",
            "--quiet",
            str(requirements),
            "-o",
            str(lock),
        ]
        logger.debug(" ".join(command))
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env={**os.environ, "UV_NO_PROGRESS": "1"},
        )
        if result.returncode != 0:
            raise RuntimeError(
                "uv pip compile failed:\n" + result.stderr.strip() + "\n"
            )
        return lock.read_text()


def parse_lock(text):
    """The ``{name: version}`` pins in a compiled requirements file.

    Names are normalized. A package that appears more than once (with
    different markers) keeps the first version seen; that only happens when a
    dependency differs by platform, never for the SEAMM packages themselves.
    """
    versions = {}
    for line in text.splitlines():
        match = _PIN.match(line.strip())
        if match:
            name = normalize(match.group("name"))
            versions.setdefault(name, match.group("version"))
    return versions


def resolve(python_version="3.12", uv=None):
    """Resolve the SEAMM package list.

    Returns
    -------
    (dict, str)
        The package dictionary ``{name: {"description", "type", "version"}}`` for
        every package in the metadata, and the lock text.
    """
    names = package_names()
    print(
        f"Resolving {len(names)} SEAMM packages with uv (universal, Python "
        f">= {python_version})."
    )
    lock = compile_lock(names, python_version=python_version, uv=uv)
    versions = parse_lock(lock)

    packages = {}
    missing = []
    for _type in PACKAGE_TYPES:
        for name, data in metadata[_type].items():
            key = normalize(name)
            if key not in versions:
                missing.append(name)
                continue
            packages[name] = {
                "description": data["description"],
                "type": _type,
                "version": versions[key],
            }
    if missing:
        raise RuntimeError(
            "These packages are in the metadata but not in the resolved lock: "
            + ", ".join(missing)
        )
    return packages, lock
