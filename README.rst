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

Each entry gives a description. Every package comes from PyPI and declares its own
dependencies, so there are no channels and no per-package dependency tables.
``excluded plug-ins`` records packages deliberately left out: retired
(``seamm-dashboard``), shelved (``torchani-step``), or living in their own environment
(``lammps-mdi``, ``xnns``, ``seamm-webui``). ``development packages`` are the extra
tools the installer adds for developers.

Nightly the ``Check`` GitHub Action:

#. resolves the whole package list from PyPI with ``uv pip compile --universal``,
   one solve valid for every platform, giving a pinned lock file;
#. compares the SEAMM package versions and the lock with the committed
   ``environments/SEAMM_packages.json`` and ``environments/seamm.lock.txt``;
#. if anything changed, uploads both files as a new version of the Zenodo record
   (creating the record the very first time), fills the DOI into the database,
   commits the result, and creates a GitHub release.

The lock file is the "known-good set": the installer passes it to ``uv pip install``
as constraints, so a fresh installation gets exactly the versions that resolved
together here. Releases are tagged with the date (``2026.9.25``); further releases on
the same day get a ``.1``, ``.2``, ... suffix. A Slack message announces each one.

Adding a package
----------------

#. Add it to the appropriate group in ``seamm_packaging/metadata.py``, by its PyPI
   name (lowercase, hyphens).
#. Run ``make format lint test`` and commit to ``main``.
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

``uv`` must be installed (``curl -LsSf https://astral.sh/uv/install.sh | sh``). The
package installs three commands, all run from the top level of the checkout:

``resolve_packages``
    Resolves the package list, prints every package with its version, and writes
    ``environments/SEAMM_packages.json`` and ``environments/seamm.lock.txt`` -- without
    touching Zenodo. Use it to see what a nightly run would do.

``packaging_dry_run``
    Everything the nightly run does, but the Zenodo draft is uploaded and then
    *discarded* rather than published, so nothing is left behind. Needs
    ``ZENODO_TOKEN``. Leaves the database with an empty DOI, so the next real run
    uploads again.

``check_for_changes``
    The real thing: resolve, compare, and if changed upload to Zenodo and publish.
    Needs ``ZENODO_TOKEN``.

Zenodo allows only one unpublished draft per record. If a run fails part way through
the draft is discarded, and if one is nevertheless left behind the next run reuses it.
An empty ``"doi"`` in the committed ``SEAMM_packages.json`` means the last upload
failed; the next run notices and uploads again. The record id (``"zenodo_id"``) in
the database is what later uploads add versions to; with no id, a new record is
created.

Acknowledgements
----------------

Developed by the Molecular Sciences Software Institute (MolSSI_),
which receives funding from the `National Science Foundation`_ under
awards OAC-1547580 and CHE-2136142.

.. _MolSSI: https://www.molssi.org
.. _`National Science Foundation`: https://www.nsf.gov
