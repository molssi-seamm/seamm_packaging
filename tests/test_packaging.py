# -*- coding: utf-8 -*-
"""Tests for the uv-based package list: lock parsing, change detection, and
(when uv is available) a real universal resolution."""

import json
from pathlib import Path
import shutil

import pytest

from seamm_packaging.metadata import metadata
from seamm_packaging.packaging import FORMAT, LOCK_FILE, update_package_list
from seamm_packaging.resolve import (
    find_uv,
    normalize,
    package_names,
    parse_lock,
    resolve,
)

SAMPLE_LOCK = """\
alembic==1.20.0
    # via seamm-datastore
molsystem==2026.9.25
    # via
    #   seamm
    #   seamm-ff-util
Pillow==12.3.0
seamm==2026.9.25.1
pywin32==312 ; sys_platform == 'win32'
    # via docker
tzdata==2026.4 ; sys_platform == 'emscripten' or sys_platform == 'win32'
"""


def test_parse_lock_pins_and_markers():
    pins = parse_lock(SAMPLE_LOCK)
    assert pins["molsystem"] == "2026.9.25"
    assert pins["seamm"] == "2026.9.25.1"
    assert pins["pillow"] == "12.3.0"  # normalized name
    assert pins["pywin32"] == "312"  # marker stripped
    assert "via" not in pins


def test_normalize():
    assert normalize("Seamm_Widgets") == "seamm-widgets"
    assert normalize("seamm.util") == "seamm-util"


def test_package_names_cover_metadata():
    names = package_names()
    for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
        for name in metadata[_type]:
            assert name in names
    assert "torchani-step" not in names  # excluded


def _packages(**versions):
    return {
        name: {"description": name, "type": "MolSSI plug-in", "version": v}
        for name, v in versions.items()
    }


def test_update_package_list_lifecycle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # commit_message.txt is written here
    env = tmp_path / "environments"

    # 1. no database yet -> changed, format 2, empty DOI
    changed, _ = update_package_list(_packages(a="1", b="2"), "a==1\nb==2\n", env)
    assert changed
    db = json.loads((env / "SEAMM_packages.json").read_text())
    assert db["format"] == FORMAT
    assert db["doi"] == "" and db["zenodo_id"] == ""
    assert db["packages"]["a"]["version"] == "1"
    assert (env / LOCK_FILE).read_text() == "a==1\nb==2\n"
    assert "Initial" in Path("commit_message.txt").read_text()

    # simulate a successful upload
    db["doi"] = "10.5281/zenodo.1"
    db["zenodo_id"] = 1
    (env / "SEAMM_packages.json").write_text(json.dumps(db))

    # 2. same again -> unchanged
    changed, _ = update_package_list(_packages(a="1", b="2"), "a==1\nb==2\n", env)
    assert not changed

    # 3. a version bump -> changed, zenodo_id kept, doi cleared
    changed, _ = update_package_list(_packages(a="1", b="3"), "a==1\nb==3\n", env)
    assert changed
    db = json.loads((env / "SEAMM_packages.json").read_text())
    assert db["zenodo_id"] == 1 and db["doi"] == ""
    assert "b changed from 2 to 3" in Path("commit_message.txt").read_text()

    # 4. no DOI (upload failed last time) -> changed even with no package change
    changed, _ = update_package_list(_packages(a="1", b="3"), "a==1\nb==3\n", env)
    assert changed
    assert "Re-uploading" in Path("commit_message.txt").read_text()

    # 5. only a dependency in the lock changes -> changed
    db = json.loads((env / "SEAMM_packages.json").read_text())
    db["doi"] = "10.5281/zenodo.2"
    (env / "SEAMM_packages.json").write_text(json.dumps(db))
    changed, _ = update_package_list(
        _packages(a="1", b="3"), "a==1\nb==3\nnumpy==2.6\n", env
    )
    assert changed
    assert "lock file" in Path("commit_message.txt").read_text()

    # 6. a package removed -> changed
    db = json.loads((env / "SEAMM_packages.json").read_text())
    db["doi"] = "10.5281/zenodo.3"
    (env / "SEAMM_packages.json").write_text(json.dumps(db))
    changed, _ = update_package_list(_packages(a="1"), "a==1\nnumpy==2.6\n", env)
    assert changed
    assert "b removed" in Path("commit_message.txt").read_text()


def test_old_format_database_is_replaced(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env = tmp_path / "environments"
    env.mkdir()
    old = {"date": "x", "doi": "10.5281/zenodo.old", "packages": {}, "metadata": {}}
    (env / "SEAMM_packages.json").write_text(json.dumps(old))
    changed, _ = update_package_list(_packages(a="1"), "a==1\n", env)
    assert changed
    db = json.loads((env / "SEAMM_packages.json").read_text())
    assert db["format"] == FORMAT
    assert db["zenodo_id"] == ""  # a new record, not the old one
    assert "converted to format" in Path("commit_message.txt").read_text()


@pytest.mark.skipif(
    shutil.which("uv") is None and not (Path.home() / ".local/bin/uv").exists(),
    reason="uv not installed",
)
def test_real_resolve():
    """The whole SEAMM package set resolves from PyPI (network)."""
    find_uv()
    packages, lock = resolve(python_version="3.12")
    assert set(packages) == set(package_names())
    assert all(p["version"] for p in packages.values())
    assert "openbabel==" in lock  # via molsystem
    assert "conda" not in lock
