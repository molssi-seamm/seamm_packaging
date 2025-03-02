import collections.abc
import copy
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import pprint
import os

import requests
import packaging.version as pkgVersion  # noqa: F401

from .conda import Conda
from .metadata import metadata

upload_types = {
    "publication": "Publication",
    "poster": "Poster",
    "presentation": "Presentation",
    "dataset": "Dataset",
    "image": "Image",
    "video": "Video/Audio",
    "software": "Software",
    "lesson": "Lesson",
    "physicalobject": "Physical object",
    "other": "Other",
}


logger = logging.getLogger("seamm_packages")
logger.setLevel(logging.DEBUG)
logger.setLevel(0)


def create_full_environment(environment_file, progress=True):
    """Find the Python packages in SEAMM.

    Parameters
    ----------
    environment_file : str or pathlib.Path
        The environment file
    progress : bool = True
        Whether to print out dots to show progress.

    Returns
    -------
    dict(str, str)
        A dictionary with information about the packages.
    """
    print("Finding all the packages that make up SEAMM. This may take several minutes.")

    conda = Conda(logger=logger)

    print("Creating a new conda environment 'SEAMM_Packages'")
    result = conda.create_environment(
        str(environment_file), name="SEAMM_Packages", force=True
    )

    # Check for errors
    if "exception_name" in result:
        message = (
            "Conda env create failed:\n"
            "   encountered exception result['exception_name']\n"
        )
        if "message" in result:
            message += "\n"
            message += result["message"]
            message += "\n"
        print(message)
        raise RuntimeError(message)

    if "success" in result and not result["success"]:
        message = (
            "Conda env create failed:\n" "   'success' not in result, or not true.\n"
        )
        if "message" in result:
            message += "\n"
            message += result["message"]
            message += "\n"
        if "error" in result:
            message += "\n"
            message += result["error"]
            message += "\n"
        print(message)
        raise RuntimeError(message)

    packages = {}
    for item in result["actions"]["LINK"]:
        package = item["name"]
        if package in metadata["Core package"]:
            _type = "Core package"
            data = metadata["Core package"][package]
        elif package in metadata["MolSSI plug-in"]:
            _type = "MolSSI plug-in"
            data = metadata["MolSSI plug-in"][package]
        elif package in metadata["3rd-party plug-in"]:
            _type = "3rd-party plug-in"
            data = metadata["3rd-party plug-in"][package]
        else:
            _type = None
        if _type is not None:
            packages[package] = {
                "channel": "conda-forge",
                "description": data["description"],
                "type": _type,
                "version": item["version"],
            }
    for item in result["actions"]["PIP"]:
        tmp = item.split("-")
        package = "-".join(tmp[0:-1])
        version = tmp[-1]
        if package in metadata["Core package"]:
            _type = "Core package"
            data = metadata["Core package"][package]
        elif package in metadata["MolSSI plug-in"]:
            _type = "MolSSI plug-in"
            data = metadata["MolSSI plug-in"][package]
        elif package in metadata["3rd-party plug-in"]:
            _type = "3rd-party plug-in"
            data = metadata["3rd-party plug-in"][package]
        else:
            _type = None
        if _type is not None:
            packages[package] = {
                "channel": "pypi",
                "description": data["description"],
                "type": _type,
                "version": version,
            }

    return packages


def list_packages(environment=None):
    """Return the package list using Conda list"""
    conda = Conda(logger=logger)

    result = conda.list(environment=environment)

    packages = {}
    for package, data in result.items():
        if package in metadata["Core package"]:
            _type = "Core package"
            mdata = metadata["Core package"][package]
        elif package in metadata["MolSSI plug-in"]:
            _type = "MolSSI plug-in"
            mdata = metadata["MolSSI plug-in"][package]
        elif package in metadata["3rd-party plug-in"]:
            _type = "3rd-party plug-in"
            mdata = metadata["3rd-party plug-in"][package]
        else:
            _type = None
        if _type is not None:
            packages[package] = {
                "channel": data["channel"],
                "description": mdata["description"],
                "type": _type,
                "version": data["version"],
            }

    return packages


def update_package_list(packages, environments="environments"):
    """Update the package list for any changes

    Parameters
    ----------
    packages : {str: str}
        The new list of packages
    environments : str or pathlib.Path
        Path to environments/ directory

    Returns
    -------
    dict(str, str)
        A dictionary with information about the packages.
    """
    # Read the existing package database and see if there are changes
    message = []
    changed = False
    path = Path(environments) / "SEAMM_packages.json"
    if not path.exists():
        changed = True
        print("The package database does not exist.")

        plist = {
            "date": datetime.now(timezone.utc).isoformat(),
            "doi": "10.5281/zenodo.7860696",
            "metadata": metadata,
            "packages": packages,
        }
        with path.open("w") as fd:
            json.dump(plist, fd, indent=4, sort_keys=True)
        with Path("commit_message.txt").open("w") as fd:
            fd.write("Initial commit of the SEAMM package database")
    else:
        with path.open("r") as fd:
            try:
                plist = json.load(fd)
            except json.JSONDecodeError:
                plist = None
        if plist is None:
            changed = True
            print("The package database could not be read, so replacing.")

            plist = {
                "conceptdoi": "10.5281/zenodo.7789853",
                "date": datetime.now(timezone.utc).isoformat(),
                "doi": "10.5281/zenodo.7860696",
                "metadata": metadata,
                "packages": packages,
            }
            with path.open("w") as fd:
                json.dump(plist, fd, indent=4, sort_keys=True)
            with Path("commit_message.txt").open("w") as fd:
                fd.write("Could not read the SEAMM package database, so replacing")
        else:
            print("Checking for changes in SEAMM")
            old_packages = plist["packages"]
            for package in packages:
                logger.debug(f"Checking package {package}")
                newv = packages[package]["version"]
                if package not in old_packages:
                    changed = True
                    print(f"  New package: {package} {newv}")
                    message.append(f"{package} added to SEAMM")
                else:
                    oldv = old_packages[package]["version"]
                    oldchannel = old_packages[package]["channel"]
                    newchannel = packages[package]["channel"]
                    oldtype = old_packages[package]["type"]
                    newtype = packages[package]["type"]
                    logger.debug(f"    Old version: {oldv} ({oldchannel}) {oldtype}")
                    logger.debug(f"    New version: {newv} ({newchannel}) {newtype}")
                    if oldv != newv:
                        changed = True
                        if oldchannel != newchannel:
                            print(
                                f"  {package}: changed from {oldv} "
                                f"({oldchannel}) to {newv} ({newchannel})"
                            )
                            message.append(
                                f"{package} changed from {oldv} ({oldchannel}) to "
                                f"{newv} ({newchannel})"
                            )
                        else:
                            print(f"  {package}: from {oldv} to {newv}")
                            message.append(f"{package} changed from {oldv} to {newv}")
                    elif oldchannel != newchannel:
                        changed = True
                        print(f"  {package}: from {oldchannel} to {newchannel}")
                        message.append(
                            f"{package} changed from {oldchannel} to {newchannel}"
                        )
                    if oldtype != newtype:
                        changed = True
                        print(f"  {package}: from {oldtype} to {newtype}")
                        message.append(f"{package} changed from {oldtype} to {newtype}")
            if not changed:
                print("The package database has not changed.")
            else:
                print("The package database has changed.")

                plist = {
                    "conceptdoi": "10.5281/zenodo.7789853",
                    "date": datetime.now(timezone.utc).isoformat(),
                    "doi": "",
                    "metadata": metadata,
                    "packages": packages,
                }
                with path.open("w") as fd:
                    json.dump(plist, fd, indent=4, sort_keys=True)
                with Path("commit_message.txt").open("w") as fd:
                    fd.write("New SEAMM package database\n\n")
                    for i, line in enumerate(message):
                        fd.write(f"{i}. {line}\n")

    return changed, packages


def create_env(packages, pinned=False):
    """Create the environment files for the packages.

    Parameters
    ----------
    packages : dict(str, dict)
        The packages to create the environment files for.
    pinned : bool = False
        Whether to pin the versions
    """
    if pinned:
        print("Creating the pinned environment file for the packages.")
    else:
        print("Creating the environment file for the packages.")
    prelines = [
        """name: seamm
channels:
  - conda-forge
  - defaults
dependencies:
  - pip
  - python
"""
    ]
    # Creating the environment file with versions pinned
    lines = []
    # First the conda installable packages, including any dependencies
    for repo in ("conda-forge", "pypi"):
        if repo == "conda-forge":
            lines.extend(prelines)
            spc = 2 * " "
        else:
            lines.append("  # PyPi packages")
            lines.append("  - pip:")
            spc = 6 * " "

        for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
            lines.append(f"{spc}# {_type}s")
            for package in sorted(metadata[_type].keys()):
                if package in packages:
                    data = packages[package]
                    if data["channel"] == repo:
                        if pinned:
                            lines.append(f"{spc}- {package}=={data['version']}")
                        else:
                            lines.append(f"{spc}- {package}")
            lines.append("")

        # Are there any dependencies that require conda installs?
        dependencies = []
        for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
            for package, meta in metadata[_type].items():
                if package in packages and "dependencies" in meta:
                    for dependency, depdata in meta["dependencies"].items():
                        if depdata["repository"] == repo:
                            dependencies.append(
                                f"{spc}# {package}: {depdata['comment']}"
                            )
                            if "pinning" in depdata and depdata["pinning"] != "":
                                dependencies.append(
                                    f"{spc}- {dependency}{depdata['pinning']}"
                                )
                            else:
                                dependencies.append(f"{spc}- {dependency}")

        if len(dependencies) > 0:
            lines.append(f"{spc}# Dependencies that require special handling\n")
            lines.extend(dependencies)
            lines.append("")

    return "\n".join(lines)


def create_full_env():
    """Create the full environment file from the metadata.

    Parameters
    ----------
    """
    print("Creating the full environment file from the metadata.")
    prelines = [
        """name: seamm
channels:
  - conda-forge
  - defaults
dependencies:
  - pip
  - python
"""
    ]
    # Creating the environment file
    lines = []

    # First the conda installable packages, including any dependencies
    for repo in ("conda-forge", "pypi"):
        if repo == "conda-forge":
            lines.extend(prelines)
            spc = 2 * " "
        else:
            lines.append("  # PyPi packages")
            lines.append("  - pip:")
            spc = 6 * " "

        for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
            lines.append(f"{spc}# {_type}s")
            for package, data in sorted(metadata[_type].items(), key=lambda x: x[0]):
                if data["repository"] == repo:
                    lines.append(f"{spc}- {package}")
            lines.append("")

        # Are there any dependencies that require conda installs?
        dependencies = []
        for _type in ("Core package", "MolSSI plug-in", "3rd-party plug-in"):
            for package, meta in metadata[_type].items():
                if "dependencies" in meta:
                    for dependency, depdata in meta["dependencies"].items():
                        if depdata["repository"] == repo:
                            dependencies.append(
                                f"{spc}# {package}: {depdata['comment']}"
                            )
                            if "pinning" in depdata and depdata["pinning"] != "":
                                dependencies.append(
                                    f"{spc}- {dependency}{depdata['pinning']}"
                                )
                            else:
                                dependencies.append(f"{spc}- {dependency}")

        if len(dependencies) > 0:
            lines.append(f"{spc}# Dependencies that require special handling\n")
            lines.extend(dependencies)
            lines.append("")

    return "\n".join(lines)


def upload_to_zenodo():
    """Upload the packaging files to Zenodo."""
    # Create a new Record
    record = add_version()

    # Remove the current files
    for filename in record.files():
        record.remove_file(filename)

    # Update the metadata in the files
    doi = record.doi
    conceptdoi = record.conceptdoi

    path = Path("environments") / "SEAMM_packages.json"
    with path.open() as fd:
        tmp = json.load(fd)
        tmp["doi"] = doi
        tmp["conceptdoi"] = conceptdoi
    with path.open("w") as fd:
        json.dump(tmp, fd, indent=4, sort_keys=True)

    # Now we can add the files to Zenodo with the correct DOI, etc.
    for name in ("SEAMM_packages.json", "seamm.yml", "seamm_pinned.yml"):
        path = Path("environments") / name
        text = path.read_text()
        record.add_file(name, contents=text)

    # For some reason the version doesn't work...let's see what the record looks like.
    # print(record)

    # Update the version in the deposit
    # version = int(record.version)
    # record.version = str(version + 1)

    # And, finally, can publish!
    record.publish()

    return doi


def add_version(_id="10891078"):
    """Create a new record object for uploading a new version to Zenodo."""
    token = os.environ["ZENODO_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = f"https://zenodo.org/api/deposit/depositions/{_id}/actions/newversion"

    logger.debug(f"add_version {url=}")
    logger.debug(headers)

    response = requests.post(url, headers=headers)

    logger.debug(f"{response.status_code=}")
    logger.debug(f"\n{pprint.pformat(response.json())}")

    if response.status_code != 201:
        raise RuntimeError(
            f"Error in add_version: code = {response.status_code}"
            f"\n\n{pprint.pformat(response.json())}"
        )

    result = response.json()

    # The result is for the original DOI, so get the data for the new one
    url = result["links"]["latest_draft"]
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error in add_version get latest draft: code = {response.status_code}"
            f"\n\n{pprint.pformat(response.json())}"
        )

    result = response.json()

    metadata = {**result["metadata"]}

    return Record(result, token, metadata=metadata)


class Record(collections.abc.Mapping):
    """A class for handling uploading a record to Zenodo.

    Attributes
    ----------
    data : dict()
        The record data from Zenodo. See https://developers.zenodo.org/#depositions
    token : str
        The Zenodo access token for the user.
    metadata : dict()
        The metadata for updating the record.
    """

    def __init__(self, data, token, metadata={}):
        self.data = data
        self.token = token
        self.metadata = metadata

    # Provide dict like access to the widgets to make
    # the code cleaner

    def __getitem__(self, key):
        """Allow [] access to the widgets!"""
        return self.data[key]

    def __iter__(self):
        """Allow iteration over the object"""
        return iter(self.data)

    def __len__(self):
        """The len() command"""
        return len(self.data)

    def __str__(self):
        return pprint.pformat(self.data)

    @property
    def authors(self):
        """Synonym for creators"""
        return self.creators

    @authors.setter
    def authors(self, value):
        self.creators = value

    @property
    def conceptdoi(self):
        """The generic concept DOI."""
        if "conceptdoi" in self.data:
            return self.data["conceptdoi"]
        else:
            return None

    @property
    def creators(self):
        """The creators for the record."""
        if "creators" not in self.metadata:
            if "creators" in self.data["metadata"]:
                self.metadata["creators"] = copy.deepcopy(
                    self.data["metadata"]["creators"]
                )
            else:
                self.metadata["creators"] = []
        return self.metadata["creators"]

    @creators.setter
    def creators(self, value):
        self.metadata["creators"] = copy.deepcopy(value)

    @property
    def description(self):
        """The description for the record."""
        if "description" not in self.metadata:
            if "description" in self.data["metadata"]:
                self.metadata["description"] = self.data["metadata"]["description"]
            else:
                return None
        return self.metadata["description"]

    @description.setter
    def description(self, value):
        self.metadata["description"] = value

    @property
    def doi(self):
        """The (prereserved) DOI."""
        if "doi" in self.data and self.data["doi"] != "":
            return self.data["doi"]
        else:
            return self.data["metadata"]["prereserve_doi"]["doi"]

    @property
    def in_progress(self):
        """Whether the deposition is still in progress, i.e. editable.

        Returns
        -------
        bool
        """
        return self.data["state"] == "inprogress"

    @property
    def keywords(self):
        """The keywords for the record."""
        if "keywords" not in self.metadata:
            if "keywords" in self.data["metadata"]:
                self.metadata["keywords"] = copy.deepcopy(
                    self.data["metadata"]["keywords"]
                )
            else:
                self.metadata["keywords"] = []
        return self.metadata["keywords"]

    @keywords.setter
    def keywords(self, value):
        self.metadata["keywords"] = copy.deepcopy(value)

    @property
    def submitted(self):
        """Whether the record has been submitted.

        If so the files can't be changed, but it may be possible to edit the metadata.

        Returns
        -------
        bool
        """
        return self.data["submitted"]

    @property
    def title(self):
        """The title for the record."""
        if "title" not in self.metadata:
            if "title" in self.data["metadata"]:
                self.metadata["title"] = self.data["metadata"]["title"]
            else:
                return None
        return self.metadata["title"]

    @title.setter
    def title(self, value):
        self.metadata["title"] = value

    @property
    def upload_type(self):
        """The type of record in Zenodo."""
        if "upload_type" not in self.metadata:
            if "upload_type" in self.data["metadata"]:
                self.metadata["upload_type"] = self.data["metadata"]["upload_type"]
            else:
                return None
        return self.metadata["upload_type"]

    @upload_type.setter
    def upload_type(self, value):
        if value not in upload_types:
            raise ValueError(
                f"upload_type '{value}' must be one of "
                f"{', '.join(upload_types.keys())}"
            )
        self.metadata["upload_type"] = value

    @property
    def version(self):
        """The version for the record."""
        if "version" not in self.metadata:
            if "version" in self.data["metadata"]:
                self.metadata["version"] = self.data["metadata"]["version"]
            else:
                return None
        return self.metadata["version"]

    @version.setter
    def version(self, value):
        self.metadata["version"] = value

    def add_creator(self, name, affiliation=None, orcid=None, ignore_duplicates=False):
        """Add a creator (author) to the record.

        Parameters
        ----------
        name : str
            The creators name as "family name, other names"
        affiliation : str, optional
            The creators affiliation (University, company,...)
        orcid : str, optional
            The ORCID id of the creator.
        ignore_duplicates : bool = False
            Silently ignore duplicate records.
        """
        # Already exists?
        for creator in self.creators:
            if "orcid" in creator and orcid is None:
                if creator["orcid"] == orcid:
                    if ignore_duplicates:
                        return
                    raise RuntimeError(f"Duplicate entry for creator: {name}")
            elif creator["name"] == name:
                if ignore_duplicates:
                    return
            raise RuntimeError(f"Duplicate entry for creator: {name}")

        creator = {"name": name}
        if affiliation is not None:
            creator["affiliation"] = affiliation
        if orcid is not None:
            creator["orcid"] = orcid
        self.metadata["creators"].append(creator)

    def add_file(self, path, contents=None, binary=False):
        """Add the given file to the record.

        Parameters
        ----------
        path : str or pathlib.Path
            The path to the file to upload.
        binary : bool = False
            Whether to open as a binary file.
        """
        if self.submitted:
            raise RuntimeError("Files cannot be added to a submitted record.")

        if isinstance(path, str):
            path = Path(path).expanduser()

        url = self.data["links"]["bucket"] + "/" + path.name
        headers = {"Authorization": f"Bearer {self.token}"}
        if contents is None:
            mode = "rb" if binary else "r"
            with open(path, mode) as fd:
                response = requests.put(url, data=fd, headers=headers)
        else:
            response = requests.put(url, data=contents, headers=headers)

        if response.status_code != 201:
            raise RuntimeError(
                f"Error in add_file: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        # Add the new file to the metadata
        self.data["files"].append(response.json())

    def add_keyword(self, keyword):
        """Add a keyword to the record.

        Parameters
        ----------
        keyword : str
            The keyword
        """
        # Already exists?
        if keyword not in self.keywords:
            self.metadata["keywords"].append(keyword)

    def download_file(self, filename, path):
        """Download a file to a local copy.

        Parameters
        ----------
        filename : str
            The name of the file.
        path : pathlib.Path
            The path to download the file to. Can be a directory in which case
            the filename is used in that directory.

        Returns
        -------
        pathlib.Path
            The path to the downloaded file.
        """
        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():
            out_path = path / filename
        else:
            out_path = path

        headers = {
            "Content-Type": "application/json",
        }
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        for data in self.data["files"]:
            if data["filename"] == filename:
                url = data["links"]["download"]
                response = requests.get(url, headers=headers, stream=True)

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error in download_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )

                with open(out_path, "wb") as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)

                return out_path

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def files(self):
        """List of the files deposited.

        Returns
        -------
        [str]
        """
        if "files" in self.data:
            return [x["filename"] for x in self.data["files"]]
        else:
            return []

    def get_file(self, filename):
        """Get the contents of a file.

        Parameters
        ----------
        filename : str
            The name of the file.

        Returns
        -------
        str or byte
        """
        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        headers = {
            "Content-Type": "application/json",
        }
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        for data in self.data["files"]:
            if data["key"] == filename:
                url = data["links"]["self"]
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error in get_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )
                return response.text

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def publish(self):
        """Publish the record on Zenodo.

        This registers the DOI, and after this the files cannot be changed.
        Any new metadata is uploaded before publishing.
        """
        if len(self.metadata) > 0:
            self.update_metadata()

        url = self.data["links"]["publish"]
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(url, headers=headers)

        if response.status_code != 202:
            raise RuntimeError(
                f"Error in publish_metadata: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        self.data = response.json()

    def remove_file(self, filename):
        """Remove a file.

        Parameters
        ----------
        filename : str
            The name of the file.
        """
        if self.submitted:
            raise RuntimeError("Files cannot be removed from a submitted record.")

        if "files" not in self.data:
            raise RuntimeError("There are no files in the record.")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        for index, data in enumerate(self.data["files"]):
            if data["filename"] == filename:
                url = data["links"]["self"]
                response = requests.delete(url, headers=headers)

                if response.status_code != 204:
                    raise RuntimeError(
                        f"Error in remove_file: code = {response.status_code}"
                        f"\n\n{pprint.pformat(response.json())}"
                    )

                # Remove the entry from the metadata
                del self.data["files"][index]

                return

        raise RuntimeError(f"File '{filename}' is not part of the deposit.")

    def remove_keyword(self, keyword):
        """Remove a keyword from the record.

        Parameters
        ----------
        keyword : str
            The keyword
        """
        # Doesn't exist?
        if keyword not in self.keywords:
            self.metadata["keywords"].append(keyword)

    def update_metadata(self):
        """Update the metadata for the record in Zenodo."""
        url = self.data["links"]["self"]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        data = {"metadata": self.metadata}

        response = requests.put(url, json=data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error in update_metadata: code = {response.status_code}"
                f"\n\n{pprint.pformat(response.json())}"
            )

        self.data = response.json()
        self.metadata = {}
