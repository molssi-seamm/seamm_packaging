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


def _response_detail(response):
    """A printable description of an HTTP response for error messages.

    Zenodo does not always answer with JSON (e.g. an empty body, or an HTML error
    page), and calling ``response.json()`` on such a body raises a JSONDecodeError
    that hides the real error. This never raises.
    """
    try:
        return pprint.pformat(response.json())
    except ValueError:
        text = response.text.strip()
        return text if text else "<empty response body>"


FORMAT = 2
LOCK_FILE = "seamm.lock.txt"
DATABASE_FILE = "SEAMM_packages.json"


def _write_database(path, plist):
    with path.open("w") as fd:
        json.dump(plist, fd, indent=4, sort_keys=True)


def _write_commit_message(lines):
    with Path("commit_message.txt").open("w") as fd:
        fd.write("New SEAMM package database\n\n")
        for i, line in enumerate(lines):
            fd.write(f"{i}. {line}\n")


def update_package_list(packages, lock, environments="environments", python="3.12"):
    """Update the package database and lock file if anything changed.

    Parameters
    ----------
    packages : {str: dict}
        The freshly resolved packages: name -> {description, type, version}.
    lock : str
        The freshly compiled universal lock text.
    environments : str or pathlib.Path
        Path to the environments/ directory holding the database and lock.
    python : str
        The minimum Python version the lock was resolved for.

    Returns
    -------
    (bool, dict)
        Whether anything changed (and so a commit and an upload are needed),
        and the packages.

    Notes
    -----
    The database format (``"format": 2``) has no channels: every package comes
    from PyPI. The Zenodo identifiers (``doi``, ``conceptdoi``, ``zenodo_id``)
    are filled in by ``upload_to_zenodo`` after a successful upload; an empty
    ``doi`` therefore means the last upload failed and must be retried.
    """
    environments = Path(environments)
    environments.mkdir(exist_ok=True)
    path = environments / DATABASE_FILE
    lock_path = environments / LOCK_FILE

    message = []
    changed = False
    plist = None
    if path.exists():
        try:
            with path.open("r") as fd:
                plist = json.load(fd)
        except json.JSONDecodeError:
            plist = None
        if plist is not None and plist.get("format") != FORMAT:
            print(f"The package database is not format {FORMAT}; replacing it.")
            message.append(f"Package database converted to format {FORMAT}")
            plist = None

    if plist is None:
        changed = True
        print("Starting a new package database.")
        if not message:
            message.append("Initial package database")
        old_packages = {}
        old_lock = ""
        zenodo = {"doi": "", "conceptdoi": "", "zenodo_id": ""}
    else:
        print("Checking for changes in SEAMM")
        old_packages = plist["packages"]
        old_lock = lock_path.read_text() if lock_path.exists() else ""
        zenodo = {k: plist.get(k, "") for k in ("doi", "conceptdoi", "zenodo_id")}

    for package, data in packages.items():
        newv = data["version"]
        newtype = data["type"]
        if package not in old_packages:
            changed = True
            print(f"  New package: {package} {newv}")
            message.append(f"{package} added to SEAMM")
            continue
        oldv = old_packages[package]["version"]
        oldtype = old_packages[package]["type"]
        if oldv != newv:
            changed = True
            print(f"  {package}: from {oldv} to {newv}")
            message.append(f"{package} changed from {oldv} to {newv}")
        if oldtype != newtype:
            changed = True
            print(f"  {package}: from {oldtype} to {newtype}")
            message.append(f"{package} changed from {oldtype} to {newtype}")
    for package in old_packages:
        if package not in packages:
            changed = True
            print(f"  Removed package: {package}")
            message.append(f"{package} removed from SEAMM")

    if lock != old_lock:
        if not changed:
            print("  The lock file changed (a dependency, not a SEAMM package).")
            message.append("Dependencies in the lock file changed")
        changed = True

    if not changed and zenodo["doi"] == "":
        # A previous run updated the database but failed to upload it to
        # Zenodo (the DOI is filled in only after a successful upload).
        changed = True
        print("The package database has no DOI: a previous upload failed.")
        message.append("Re-uploading the package database to Zenodo")

    if not changed:
        print("The package database has not changed.")
        return False, packages

    print("The package database has changed.")
    plist = {
        "format": FORMAT,
        "python": python,
        "lock": LOCK_FILE,
        "date": datetime.now(timezone.utc).isoformat(),
        "doi": "",
        "conceptdoi": zenodo["conceptdoi"],
        "zenodo_id": zenodo["zenodo_id"],
        "metadata": metadata,
        "packages": packages,
    }
    _write_database(path, plist)
    lock_path.write_text(lock)
    _write_commit_message(message)
    return True, packages


RECORD_METADATA = {
    "title": "SEAMM Package List",
    "upload_type": "dataset",
    "description": (
        "<p>The package list for the SEAMM environment (Simulation Environment "
        "for Atomistic and Molecular Simulations), and the universal lock file "
        "resolved from it with uv: the pinned, known-good set of every package "
        "and dependency, for all platforms, that the SEAMM installer uses.</p>"
    ),
    "creators": [
        {
            "name": "Saxe, Paul",
            "affiliation": "MolSSI, Virginia Tech",
            "orcid": "0000-0002-8641-9448",
        }
    ],
    "license": "cc-by-4.0",
    "access_right": "open",
    "keywords": ["SEAMM", "package list", "uv", "lock file"],
}


def upload_to_zenodo(publish=True, environments="environments"):
    """Upload the package database and lock file to Zenodo.

    The first time (no ``zenodo_id`` in the database) a brand-new record is
    created; afterwards a new version of that record. On success the
    database on disk is updated with the DOI, concept DOI and record id, so
    the commit that follows carries them.

    Parameters
    ----------
    publish : bool = True
        Whether to publish. If False the draft is uploaded and then *discarded*,
        so a dry run leaves nothing behind on Zenodo.
    environments : str or pathlib.Path
        Path to the environments/ directory.

    Returns
    -------
    str
        The DOI of the new version ("" for a dry run).

    Notes
    -----
    Zenodo allows only one draft (unpublished) version per record. If anything
    goes wrong after the draft is created it is discarded again, so that a
    failed run does not block the next one. As a second line of defense,
    `add_version` reuses an existing draft if one is found.
    """
    environments = Path(environments)
    path = environments / DATABASE_FILE
    with path.open() as fd:
        plist = json.load(fd)

    zenodo_id = plist.get("zenodo_id", "")
    if zenodo_id:
        record = add_version(str(zenodo_id))
        print(f"Zenodo draft {record.data['id']} of record {zenodo_id}")
    else:
        record = create_record()
        print(f"Zenodo NEW record, draft {record.data['id']}")

    try:
        for filename in record.files():
            print(f"removing file {filename}")
            record.remove_file(filename)

        doi = record.data.get("doi") or record.data.get("metadata", {}).get(
            "prereserve_doi", {}
        ).get("doi", "")
        conceptdoi = record.data.get("conceptdoi", "")

        plist["doi"] = doi
        plist["conceptdoi"] = conceptdoi
        plist["zenodo_id"] = record.data["id"]
        _write_database(path, plist)

        for name in (DATABASE_FILE, LOCK_FILE):
            text = (environments / name).read_text()
            print(f"adding file {name}")
            record.add_file(name, contents=text)

        if publish:
            record.publish()
            # After publishing the record knows its final identifiers.
            plist["doi"] = record.data.get("doi", doi)
            plist["conceptdoi"] = record.data.get("conceptdoi", conceptdoi)
            plist["zenodo_id"] = record.data["id"]
            _write_database(path, plist)
            print(f"published {plist['doi']} (record {plist['zenodo_id']})")
            return plist["doi"]
        else:
            print("dry run: discarding the draft (publish=False)")
            record.discard()
            plist["doi"] = ""
            plist["conceptdoi"] = ""
            plist["zenodo_id"] = zenodo_id
            _write_database(path, plist)
            return ""
    except Exception:
        print(f"Upload failed, discarding draft {record.data['id']}")
        try:
            record.discard()
        except Exception as e:
            print(f"   ...could not discard the draft: {e}")
        plist["doi"] = ""
        _write_database(path, plist)
        raise


def create_record():
    """Create a brand-new Zenodo deposition for the package list.

    Used once, the first time the database is uploaded; every later upload is
    a new version of this record (`add_version`). A DOI is pre-reserved so the
    uploaded files can carry it.
    """
    token = os.environ["ZENODO_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = "https://zenodo.org/api/deposit/depositions"
    data = {"metadata": {**RECORD_METADATA, "prereserve_doi": True}}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 201:
        raise RuntimeError(
            f"Error creating a Zenodo record: code = {response.status_code}"
            f"\n\n{_response_detail(response)}"
        )
    result = response.json()
    logger.debug(f"\n{pprint.pformat(result)}")
    return Record(result, token, metadata={})


def find_draft(conceptrecid, token):
    """Find an existing unpublished draft of the given concept record, if any.

    Parameters
    ----------
    conceptrecid : int or str
        The concept record id that all versions share.
    token : str
        The Zenodo access token.

    Returns
    -------
    dict or None
        The deposition data of the draft, or None if there is no draft.
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://zenodo.org/api/deposit/depositions"
    params = {"status": "draft", "all_versions": "true", "size": 100}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error listing Zenodo drafts: code = {response.status_code}"
            f"\n\n{_response_detail(response)}"
        )

    for deposition in response.json():
        if str(deposition.get("conceptrecid")) == str(
            conceptrecid
        ) and not deposition.get("submitted", True):
            # The listing is abbreviated (no "bucket" link, etc.), so fetch the
            # full deposition.
            response = requests.get(deposition["links"]["self"], headers=headers)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Error getting Zenodo draft {deposition['id']}: "
                    f"code = {response.status_code}"
                    f"\n\n{_response_detail(response)}"
                )
            return response.json()
    return None


def add_version(_id):
    """Create a new record object for uploading a new version to Zenodo.

    If a draft of a new version already exists -- typically left behind by an
    earlier run that failed part way through -- it is reused, because Zenodo refuses
    to create a second draft ("files.enabled: Please remove all files first").
    """
    token = os.environ["ZENODO_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # The concept record id, shared by all versions, from the published record
    url = f"https://zenodo.org/api/deposit/depositions/{_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(
            f"Error in add_version getting record {_id}: code = {response.status_code}"
            f"\n\n{_response_detail(response)}"
        )
    conceptrecid = response.json()["conceptrecid"]

    draft = find_draft(conceptrecid, token)
    if draft is not None:
        print(f"Reusing the existing Zenodo draft {draft['id']}")
        logger.debug(f"\n{pprint.pformat(draft)}")
        result = draft
    else:
        url = f"https://zenodo.org/api/deposit/depositions/{_id}/actions/newversion"

        logger.debug(f"add_version {url=}")

        response = requests.post(url, headers=headers)

        logger.debug(f"{response.status_code=}")
        logger.debug(f"\n{_response_detail(response)}")

        if response.status_code != 201:
            raise RuntimeError(
                f"Error in add_version: code = {response.status_code}"
                f"\n\n{_response_detail(response)}"
            )

        result = response.json()

        # The result is for the original DOI, so get the data for the new one
        url = result["links"]["latest_draft"]
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                "Error in add_version get latest draft: "
                f"code = {response.status_code}"
                f"\n\n{_response_detail(response)}"
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
                f"\n\n{_response_detail(response)}"
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

    def discard(self):
        """Discard (delete) this draft from Zenodo.

        Only unpublished drafts can be discarded; the published versions of a record
        are permanent.
        """
        if self.submitted:
            raise RuntimeError("A published record cannot be discarded.")

        url = self.data["links"]["self"]
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.delete(url, headers=headers)

        if response.status_code not in (200, 204):
            raise RuntimeError(
                f"Error in discard: code = {response.status_code}"
                f"\n\n{_response_detail(response)}"
            )

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
                        f"\n\n{_response_detail(response)}"
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
                        f"\n\n{_response_detail(response)}"
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
                f"\n\n{_response_detail(response)}"
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

                if response.status_code not in (200, 204):
                    raise RuntimeError(
                        f"Error in remove_file: code = {response.status_code}"
                        f"\n\n{_response_detail(response)}"
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
                f"\n\n{_response_detail(response)}"
            )

        self.data = response.json()
        self.metadata = {}
