metadata = {
    "Core package": {
        "molsystem": {
            "description": "The molecular/crystal data model for SEAMM",
            "dependencies": {
                "libsqlite": {
                    "comment": "libsqlite version 3.49.1 is badly broken!",
                    "pinning": "!=3.49.1",
                    "repository": "conda-forge",
                },
                "pubchempy": {
                    "comment": "Currently ommitted from molsystem requirements...",
                    "repository": "conda-forge",
                },
            },
            "repository": "conda-forge",
        },
        "seamm": {
            "description": "The core of the SEAMM environment and graphical interface.",
            "dependencies": {
                "pmw": {
                    "comment": "conda-forge version is old and does not work",
                    "repository": "pypi",
                },
                "psutil": {
                    "comment": "pip cannot install, so insist on conda",
                    "repository": "conda-forge",
                },
            },
            "repository": "conda-forge",
        },
        "seamm-ase": {
            "description": "Connector between SEAMM and ASE",
            "repository": "pypi",
        },
        "seamm-dashboard": {
            "description": (
                "The Web Dashboard for SEAMM (Simulation Environment for Atomistic "
                "and Molecular Simulations)."
            ),
            "dependencies": {
                "connexion": {
                    "comment": "Dashboard fails with version 3, so...",
                    "pinning": "<3.0",
                    "repository": "conda-forge",
                },
                "flask-jwt-extended": {
                    "comment": "Later version caused problems logging in",
                    "pinning": "=4.5.3",
                    "repository": "conda-forge",
                },
                "pyjwt": {
                    "comment": "Later version caused problems logging in",
                    "pinning": "=2.9.0",
                    "repository": "conda-forge",
                },
            },
            "repository": "conda-forge",
        },
        "seamm-datastore": {
            "description": "Manages the data in the datastore for the SEAMM Dashboard",
            "repository": "conda-forge",
        },
        "seamm-exec": {
            "description": "Classes to execute background codes for SEAMM",
            "repository": "pypi",
        },
        "seamm-ff-util": {
            "description": "Utility routines for handling forcefields in SEAMM",
            "repository": "conda-forge",
        },
        "seamm-geometric": {
            "description": "Connector between geomeTRIC and SEAMM",
            "repository": "pypi",
        },
        "seamm-installer": {
            "description": (
                "The installer/updater for SEAMM (Simulation Environment for "
                "Atomistic and Molecular Simulations)."
            ),
            "repository": "conda-forge",
        },
        "seamm-jobserver": {
            "description": "The JobServer for the SEAMM environment.",
            "repository": "pypi",
        },
        "seamm-util": {
            "description": "Utility methods for the SEAMM environment",
            "repository": "conda-forge",
            "dependencies": {
                "kaleido": {
                    "comment": "does not exist on conda forge",
                    "repository": "pypi",
                },
            },
        },
        "seamm-widgets": {
            "description": "Specialized tkinter widgets for SEAMM",
            "repository": "conda-forge",
        },
    },
    "MolSSI plug-in": {
        "control-parameters-step": {
            "description": (
                "A SEAMM plug-in for defining command-line parameters for a flowchart."
            ),
            "repository": "pypi",
        },
        "crystal-builder-step": {
            "description": (
                "A SEAMM plug-in for creating crystals from prototypes, including "
                "Strukturbericht designations."
            ),
            "repository": "pypi",
        },
        "custom-step": {
            "description": "A SEAMM plug-in for custom Python scripts in a flowchart.",
            "repository": "pypi",
        },
        "dftbplus-step": {
            "description": (
                "A SEAMM plug-in for DFTB+, a fast quantum mechanical simulation code."
            ),
            "repository": "pypi",
        },
        "diffusivity-step": {
            "description": "A SEAMM plug-in for calculating diffusivity",
            "repository": "pypi",
        },
        "energy-scan-step": {
            "description": (
                "A SEAMM plug-in for calculating energy profiles along coordinates"
            ),
            "repository": "pypi",
        },
        "fhi-aims-step": {
            "description": "A SEAMM plug-in for FHI-aims",
            "repository": "pypi",
        },
        "forcefield-step": {
            "description": (
                "A SEAMM plug-in for setting up a forcefield or EAM potentials for "
                "subsequent simulations."
            ),
            "repository": "pypi",
        },
        "from-smiles-step": {
            "description": (
                "A SEAMM plug-in for creating structures from SMILES, InChI, InChIKey, "
                "or name."
            ),
            "repository": "pypi",
        },
        "gaussian-step": {
            "description": "A SEAMM plug-in for Gaussian",
            "repository": "pypi",
        },
        "geometry-analysis-step": {
            "description": (
                "A SEAMM plug-in for analysis of the geometry of (small) molecules"
            ),
            "repository": "pypi",
        },
        "lammps-step": {
            "description": (
                "A SEAMM plug-in for LAMMPS, a forcefield-based molecular dynamics "
                "(MD) code."
            ),
            "repository": "pypi",
        },
        "loop-step": {
            "description": "A SEAMM plug-in which provides loops in flowcharts.",
            "repository": "pypi",
        },
        "mopac-step": {
            "description": (
                "A SEAMM plug-in to setup, run and analyze semiempirical calculations "
                "with MOPAC"
            ),
            "repository": "pypi",
        },
        "packmol-step": {
            "description": (
                "A SEAMM plug-in for building periodic boxes of fluid using Packmol"
            ),
            "repository": "pypi",
        },
        "psi4-step": {
            "description": (
                "A SEAMM plug-in to setup, run and analyze quantum chemistry "
                "calculations using Psi4"
            ),
            "repository": "pypi",
        },
        "qcarchive-step": {
            "description": "A SEAMM plug-in for connecting with QCArchive",
            "dependencies": {
                "qcportal": {
                    "comment": (
                        "qcportal requires apsw, which must be compiled if using pip."
                    ),
                    "repository": "conda-forge",
                }
            },
            "repository": "pypi",
        },
        "quickmin-step": {
            "description": (
                "A SEAMM plug-in for simple, quick minimization using a forcefield"
            ),
            "repository": "pypi",
        },
        "rdkit-step": {
            "description": "A SEAMM plug-in for RDKit descriptors/features",
            "repository": "pypi",
        },
        "reaction-path-step": {
            "description": (
                "A SEAMM plugin for finding transition states and reaction paths"
            ),
            "repository": "pypi",
        },
        "read-structure-step": {
            "description": (
                "A SEAMM plug-in to read structures from file formats common in "
                "computational chemistry"
            ),
            "repository": "pypi",
        },
        "set-cell-step": {
            "description": "A SEAMM plug-in for setting the periodic (unit) cell.",
            "repository": "pypi",
        },
        "strain-step": {
            "description": "A SEAMM plug-in for straining periodic systems",
            "repository": "pypi",
        },
        "structure-step": {
            "description": "A SEAMM plug-in for optimizing structures based on energy",
            "repository": "pypi",
        },
        "subflowchart-step": {
            "description": "A SEAMM plug-in for subflowcharts",
            "repository": "pypi",
        },
        "supercell-step": {
            "description": (
                "A SEAMM plug-in for building supercells of periodic systems."
            ),
            "repository": "pypi",
        },
        "table-step": {
            "description": "A SEAMM plug-in for data tables in a flowchart.",
            "repository": "pypi",
        },
        "thermal-conductivity-step": {
            "description": "A SEAMM plug-in for calculating thermal conductivity",
            "repository": "pypi",
        },
        "thermochemistry-step": {
            "description": "A SEAMM plug-in for calculating thermochemical functions",
            "repository": "pypi",
        },
        "thermomechanical-step": {
            "description": "A SEAMM plug-in for calculating thermomechanical properties",
            "repository": "pypi",
        },
        "torchani-step": {
            "description": "A SEAMM plug-in for the TorchANI ML models",
            "repository": "pypi",
        },
        "vasp-step": {
            "description": "A SEAMM plug-in for VASP, a planewave DFT code",
            "repository": "pypi",
        },
    },
    "3rd-party plug-in": {
        "pyxtal-step": {
            "description": (
                "A SEAMM plug-in for PyXtal, which builds atomic and molecular "
                "crystals."
            ),
            "repository": "pypi",
        },
    },
    "excluded plug-ins": [
        "cassandra-step",
        "chemical-formula",
        "cms-plots",
        "seamm-cookiecutter",
        "seamm-dashboard-client",
        "solvate-step",
        "nwchem-step",
        "properties-step",
    ],
    "conda development packages": [
        "black",
        "codecov",
        "flake8",
        "nodejs",
        "pydata-sphinx-theme",
        "pytest",
        "pytest-cov",
        "pygments",
        "sphinx",
        "sphinx-design",
        "twine",
        "watchdog",
    ],
    "pypi development packages": [
        "build",
        "rinohtype",
        "seamm-cookiecutter",
        "sphinx-copybutton",
        "sphinx-rtd-theme",
        "pystemmer",
    ],
}
