# -*- coding: utf-8 -*-
import logging
import pprint
import re

import requests

logger = logging.getLogger("seamm_packages")

# Regular expressions for pypi query results.
SNIPPET_RE = re.compile(r"<a class=\"package-snippet\".*>")
NAME_RE = re.compile(r"<span class=\"package-snippet__name\">(.+)</span>")
VERSION_RE = re.compile(r".*<span class=\"package-snippet__version\">(.+)</span>")
DESCRIPTION_RE = re.compile(r".*<p class=\"package-snippet__description\">(.+)</p>")
CREATED_RE = re.compile(
    r".*<span class=\"package-snippet__created\"><time datetime=\"(.+)T"
)
NEXT_RE = re.compile(
    r'<a href="/search/.*page=(.+)" ' 'class="button button-group__button">Next</a>'
)


class Pip(object):
    """
    Class for handling pip

    Attributes
    ----------

    """

    def __init__(self):
        logger.debug("Creating Pip {str(type(self))}")

        self._base_url = "https://pypi.org/search/"

    def search(
        self,
        query=None,
        framework=None,
        exact=False,
        progress=False,
        newline=True,
        update=None,
    ):
        """Search PyPi for packages.

        Parameters
        ----------
        query : str
            The text of the query, if any.
        framework : str
            The framework classifier, if any.
        exact : bool = False
            Whether to only return the exact match, defaults to False.
        progress : bool = False
            Whether to show progress dots.
        newline : bool = True
            Whether to print a newline at the end if showing progress
        update : None or method
            Method to call to e.g. update a progress bar

        Returns
        -------
        [str]
            A list of packages matching the query.
        """
        # Can not have exact match if no query term
        if query is None:
            exact = False

        # Set up the arguments for the http get
        args = {"q": query}
        if framework is not None:
            args["c"] = f"Framework::{framework}"

        logger.debug(f"search query: {args}")

        # PyPi serves up the results one page at a time, so loop
        if progress:
            count = 0
        result = {}
        while True:
            response = requests.get(self._base_url, params=args)
            logger.log(5, f"response: {response.text}")

            snippets = SNIPPET_RE.split(response.text)

            for snippet in snippets:
                name = NAME_RE.findall(snippet)
                version = VERSION_RE.findall(snippet)
                description = DESCRIPTION_RE.findall(snippet)

                # Ignore any snippets without data, e.g. the first one.
                if len(name) > 0:
                    if not exact or name[0] == query:
                        if len(version) == 0:
                            version = None
                        else:
                            version = version[0]
                        if len(description) == 0:
                            description = "no description given"
                        else:
                            description = description[0]
                        result[name[0]] = {
                            "channel": "pypi",
                            "version": version,
                            "description": description,
                        }

                        if exact:
                            break

            if progress:
                if update is None:
                    count += 1
                    if count <= 50:
                        print(".", end="", flush=True)
                    else:
                        count = 1
                        print("\n.", end="", flush=True)
                else:
                    update()
            # See if there is a next page
            next_page = NEXT_RE.findall(snippet)
            if len(next_page) == 0:
                break
            else:
                args["page"] = next_page[0]

        if progress and newline and count > 0:
            if update is None:
                print("", flush=True)

        logger.debug(f"Package information:\n{pprint.pformat(result)}")

        return result

    def get_package_info(self, project):
        """Get the information for a project.

        Parameters
        ----------
        project : str
            The name of the project to get the information for.

        Returns
        -------
        dict
            A dictionary of the information about the project.
        """
        headers = {"user-agent": "SEAMM, psaxe@vt.edu"}
        response = requests.get(
            self._base_url + f"/pypi/{project}/json", headers=headers
        )
        return response.json()

    def parse_search(self, data, result={}):
        """Parse the PyPi search results.

        Parameters
        ----------
        data : str
            The text of the web page
        result : dict
            The dictionary to add the results to

        Returns
        -------
        dict
            The result dictionary
        """
        snippets = SNIPPET_RE.split(data)

        for snippet in snippets:
            name = NAME_RE.findall(snippet)
            version = VERSION_RE.findall(snippet)
            description = DESCRIPTION_RE.findall(snippet)
            created = CREATED_RE.findall(snippet)

            # Ignore any snippets without data, e.g. the first one.
            if len(name) > 0:
                if len(version) == 0:
                    if len(created) > 0:
                        version = created[0].replace("-", ".")
                        version = version.replace(".0", ".")
                    else:
                        version = None
                else:
                    version = version[0]
                if len(description) == 0:
                    description = "no description given"
                else:
                    description = description[0]
                result[name[0]] = {
                    "channel": "pypi",
                    "version": version,
                    "description": description,
                }

        return result
