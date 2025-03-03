from pathlib import Path
from tempfile import NamedTemporaryFile

from .conda import Conda
from .packaging import (
    create_full_environment,
    list_packages,
    update_package_list,
    create_env,
    create_full_env,
    upload_to_zenodo,
)


def create_full_environment_file(filename="test.yml"):
    """Create the full environment file on disk."""
    environment = create_full_env()
    Path(filename).write_text(environment)


def check_for_changes(environment=None, environments="environments"):
    packages = list_packages(environment=environment)
    changed, packages = update_package_list(packages, environments=environments)

    if changed:
        print("Packages have changed, updating environment files")

        env = create_env(packages)
        (environments / "seamm.yml").write_text(env)

        env = create_env(packages, pinned=True)
        (environments / "seamm_pinned.yml").write_text(env)

        print("Uploading to ZENODO")
        doi = upload_to_zenodo()
        print(f"   new DOI = {doi}")
    else:
        print("Packages have not changed, so nothing to do")

    return changed


if __name__ == "__main__":
    # Find the environment file.
    root = Path(__file__).parent.parent
    environments = root / "environments"

    if True:
        with NamedTemporaryFile(suffix=".yml", delete=False) as fp:
            environment_file = Path(fp.name)
            create_full_environment_file(environment_file)
            create_full_environment(environment_file)
            changed = check_for_changes("SEAMM_Packages", environments=environments)

    # Clean up
    environment_file.unlink()
    conda = Conda()
    if conda.exists("SEAMM_Packages"):
        print("Removing the existing environment 'SEAMM_Packages'")
        conda.remove_environment("SEAMM_Packages")
