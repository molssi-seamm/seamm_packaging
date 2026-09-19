===============
SEAMM Packaging
===============
Maintains the list of packages that make up the SEAMM environment, and publishes it
where the SEAMM installer can find it.

* Free software: BSD license
* Documentation: https://molssi-seamm.github.io
* Code: https://github.com/molssi-seamm/seamm_packaging

What this does
--------------

``seamm_installer`` does not hard-code the packages it installs. It reads a package
list, ``SEAMM_packages.json``, from the latest published version of the Zenodo record
`10.5281/zenodo.7789853 <https://doi.org/10.5281/zenodo.7789853>`_. This project
generates that list and keeps it current.

The list is built from ``seamm_packaging/metadata.py``, which is the single place a
package is declared. It has three groups of packages that go into the SEAMM
environment:

* **Core package** -- the framework and its libraries (``seamm``, ``molsystem``,
  ``seamm-jobserver``, ...)
* **MolSSI plug-in** -- the steps maintained by MolSSI
* **3rd-party plug-in** -- steps maintained elsewhere

Each entry gives a description, whether the package comes from ``conda-forge`` or
``pypi``, and optionally dependencies that need special handling (pinning, or forcing a
particular repository). ``excluded plug-ins`` records packages deliberately left out,
for instance because they live in their own Conda environment (``lammps-mdi``,
``xnns``, ``seamm-webui``). The two ``development packages`` lists are the extra tools
the installer adds for developers.

Nightly the ``Check`` GitHub Action:

#. builds a full environment from the metadata, resolving all the packages to their
   current versions on conda-forge and PyPI;
#. compares the result with the committed ``environments/SEAMM_packages.json``;
#. if anything changed, regenerates ``environments/seamm.yml`` and
   ``environments/seamm_pinned.yml``, uploads the three files as a new version of the
   Zenodo record, commits the result, and creates a GitHub release.

Releases are tagged with the date (``2026.9.19``); further releases on the same day get
a ``.1``, ``.2``, ... suffix. A Slack message announces each one.

Adding a package
----------------

#. Add it to the appropriate group in ``seamm_packaging/metadata.py``. Use the PyPI
   name (lowercase, hyphens) since that is what Conda and pip report.
#. Run ``make format lint`` and commit to ``main``.
#. Either wait for the nightly run or start one by hand (below).

Running the workflow by hand
----------------------------

The ``Check`` workflow can be started from the Actions tab on GitHub, or with

.. code-block:: bash

    gh workflow run Check.yaml

It does exactly what the nightly run does, and does nothing if the package list is
unchanged.

Running locally
---------------

The package installs three commands, all run from the top level of the checkout:

``create_full_environment_file``
    Writes ``test.yml``, a Conda environment file listing every package in the
    metadata, which is what the workflow feeds to Conda.

``check_for_changes``
    Given the resolved environment (the workflow activates it first), updates
    ``environments/`` and uploads to Zenodo if the package list changed.

``upload_to_zenodo``
    Uploads the current contents of ``environments/`` as a new version of the Zenodo
    record and publishes it. Needs the ``ZENODO_TOKEN`` environment variable. For a
    dry run that leaves the new version as an unpublished draft, use Python::

        from seamm_packaging import upload_to_zenodo
        upload_to_zenodo(publish=False)

Zenodo allows only one unpublished draft per record. If a run fails part way through
the draft is discarded, and if one is nevertheless left behind the next run reuses it.
An empty ``"doi"`` in the committed ``SEAMM_packages.json`` means the last upload
failed; the next run notices and uploads again.

Acknowledgements
----------------

Developed by the Molecular Sciences Software Institute (MolSSI_),
which receives funding from the `National Science Foundation`_ under
awards OAC-1547580 and CHE-2136142.

.. _MolSSI: https://www.molssi.org
.. _`National Science Foundation`: https://www.nsf.gov
