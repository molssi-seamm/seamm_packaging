===============
SEAMM Packaging
===============
Tools to create packing lists and packages for the SEAMM environment.

* Free software: BSD license
* Documentation: https://molssi-seamm.github.io
* Code: https://github.com/molssi-seamm/packaging

Features
--------

* TODO

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

    docker run --rm -v $PWD:/home ghcr.io/molssi-seamm/seamm-mopac:<version> seamm ?flowchart?

where `flowchart` is an optional flowchart to load into SEAMM.

Acknowledgements
----------------

Developed by the Molecular Sciences Software Institute (MolSSI_),
which receives funding from the `National Science Foundation`_ under
awards OAC-1547580 and CHE-2136142.

.. _MolSSI: https://www.molssi.org
.. _`National Science Foundation`: https://www.nsf.gov
