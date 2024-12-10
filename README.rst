===============
SEAMM Packaging
===============
Tools to create packing lists and packages for the SEAMM environment.

* Free software: BSD license
* Documentation: https://molssi-seamm.github.io
* Code: https://github.com/molssi-seamm/packaging

HOWTO
-----

The automated packaging system is designed to create a package for the SEAMM
environment using GitHub Actions. However, this is currently not working because PyPi
has restricted programmatic access to the API. The following instructions are for
running by hand.

#. Clone the repository and ensure it is up to date
#. From the PyPi website search for "seamm" and save the pages as "search1.html",
   "search2.html", etc. in the Downloads directory
#. Run the script in the top level of the project:

   .. code-block:: bash

       python -m seamm_packaging

   This should update the package info and upload it to Zenodo.

#. Push the changes to the repository
#. Make a new release
#. Manually invoke the GitHub Action "Release" to do the rest.
   
seamm Docker image
------------------------
There is a Docker image available for SEAMM. It is available at the Github Container
Registry (ghcr.io) as

.. code-block:: bash

    ghcr.io/molssi-seamm/seamm:<version>

Where <version> is the explicit version tag for the desired image. The tag `latest` is
quite confusing, and does not mean the latest version of the image, so we recomend using
explcit versions rather than `latest`.

The container is run with the following command:

.. code-block:: bash

    docker run --rm -v $PWD:/home ghcr.io/molssi-seamm/seamm:<version> ?flowchart?

where `flowchart` is an optional flowchart to load into SEAMM.

Acknowledgements
----------------

Developed by the Molecular Sciences Software Institute (MolSSI_),
which receives funding from the `National Science Foundation`_ under
awards OAC-1547580 and CHE-2136142.

.. _MolSSI: https://www.molssi.org
.. _`National Science Foundation`: https://www.nsf.gov
