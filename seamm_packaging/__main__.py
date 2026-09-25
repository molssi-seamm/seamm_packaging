"""Console-script entry points for the nightly package-list job."""

import sys

from .packaging import update_package_list, upload_to_zenodo
from .resolve import resolve

PYTHON_VERSION = "3.12"


def resolve_packages(environments="environments"):
    """Console script: resolve the package list and write the database and
    lock without touching Zenodo. For looking before leaping.

    Returns 0, or 1 if the resolution fails.
    """
    try:
        packages, lock = resolve(python_version=PYTHON_VERSION)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1
    changed, _ = update_package_list(
        packages, lock, environments=environments, python=PYTHON_VERSION
    )
    width = max(len(p) for p in packages)
    for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
        print(f"\n{_type}s")
        for name, data in sorted(packages.items()):
            if data["type"] == _type:
                print(f"  {name:{width}s} {data['version']}")
    print(f"\n{'Changed' if changed else 'Unchanged'}; files in {environments}/")
    return 0


def check_for_changes(environments="environments", publish=True):
    """Console-script entry point: update the package list if it changed.

    Always returns 0 on success. The console script does ``sys.exit()`` on the
    return value, so returning the ``changed`` flag made every successful update
    exit with status 1.
    """
    _check_for_changes(environments=environments, publish=publish)
    return 0


def _check_for_changes(environments="environments", publish=True):
    packages, lock = resolve(python_version=PYTHON_VERSION)
    changed, packages = update_package_list(
        packages, lock, environments=environments, python=PYTHON_VERSION
    )

    if changed:
        print("Packages have changed; uploading to Zenodo")
        doi = upload_to_zenodo(publish=publish, environments=environments)
        print(f"   new DOI = {doi}")
    else:
        print("Packages have not changed, so nothing to do")

    return changed


def dry_run():
    """Console script: everything check_for_changes does, but the Zenodo draft is
    discarded instead of published. Leaves the database on disk with an empty
    DOI, so the next real run re-uploads."""
    _check_for_changes(publish=False)
    return 0


if __name__ == "__main__":
    sys.exit(check_for_changes())
