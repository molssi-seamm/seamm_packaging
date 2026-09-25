"""The SEAMM package list: every package the installer manages, by type.

Every package comes from PyPI; there are no channels or per-package dependency
tables any more -- each package declares its own dependencies. The nightly job
(see packaging.py) resolves this list with uv into a universal lock file and
publishes both to Zenodo, where the installer reads them.

"excluded plug-ins" are packages that exist but are not installed: retired,
shelved, or living in their own environment. "development packages" are what
`seamm-manager install development` adds.

Phase 3 of the 2026-09-25 campaign replaces "seamm-installer" here with
"seamm-manager" once that package exists on PyPI; seamm-installer is then frozen.
"""

metadata = {
    "Core package": {
        "molsystem": {"description": "The molecular/crystal data model for " "SEAMM"},
        "seamm": {
            "description": "The core of the SEAMM environment and "
            "graphical interface."
        },
        "seamm-ase": {"description": "Connector between SEAMM and ASE"},
        "seamm-bsse": {
            "description": "A library for the common code for "
            "n-body BSSE calculations"
        },
        "seamm-datastore": {
            "description": "Manages the data in the "
            "datastore for the SEAMM "
            "Dashboard"
        },
        "seamm-exec": {
            "description": "Classes to execute background codes " "for SEAMM"
        },
        "seamm-ff-util": {
            "description": "Utility routines for handling " "forcefields in SEAMM"
        },
        "seamm-geometric": {"description": "Connector between geomeTRIC and " "SEAMM"},
        "seamm-installer": {
            "description": "The installer/updater for SEAMM "
            "(Simulation Environment for "
            "Atomistic and Molecular "
            "Simulations)."
        },
        "seamm-jobserver": {
            "description": "The JobServer for the SEAMM " "environment."
        },
        "seamm-mdi": {
            "description": "A reusable MolSSI Driver Interface "
            "(MDI) facility for driving engines "
            "from SEAMM steps."
        },
        "seamm-slurm": {
            "description": "SLURM back-end (submit/poll/cancel) "
            "for SEAMM, with local and SSH "
            "transports."
        },
        "seamm-thermochemistry": {
            "description": "A library for "
            "standardizing the quantum "
            "chemsitry energy "
            "reference."
        },
        "seamm-util": {"description": "Utility methods for the SEAMM " "environment"},
        "seamm-widgets": {"description": "Specialized tkinter widgets for " "SEAMM"},
    },
    "MolSSI plug-in": {
        "atomic-charges-step": {
            "description": "A SEAMM plug-in for "
            "calculation atomic charges "
            "using DDEC6, Bader, etc."
        },
        "control-parameters-step": {
            "description": "A SEAMM plug-in for "
            "defining command-line "
            "parameters for a "
            "flowchart."
        },
        "crystal-builder-step": {
            "description": "A SEAMM plug-in for "
            "creating crystals from "
            "prototypes, including "
            "Strukturbericht "
            "designations."
        },
        "custom-step": {
            "description": "A SEAMM plug-in for custom Python "
            "scripts in a flowchart."
        },
        "dftbplus-step": {
            "description": "A SEAMM plug-in for DFTB+, a "
            "fast quantum mechanical "
            "simulation code."
        },
        "diffusivity-step": {
            "description": "A SEAMM plug-in for " "calculating diffusivity"
        },
        "dimer-builder-step": {
            "description": "A SEAMM plug-in for "
            "building dimer structures "
            "exploring the angular and "
            "radial space."
        },
        "energy-step": {
            "description": "A SEAMM plug-in for calculating "
            "the energy and forces of many "
            "structures with a model chemistry "
            "served over MDI."
        },
        "energy-scan-step": {
            "description": "A SEAMM plug-in for "
            "calculating energy profiles "
            "along coordinates"
        },
        "extract-clusters-step": {
            "description": "A SEAMM plug-in for "
            "extracting molecular "
            "clusters (n-mers) from "
            "bulk or trajectory "
            "structures."
        },
        "fhi-aims-step": {"description": "A SEAMM plug-in for FHI-aims"},
        "forcefield-step": {
            "description": "A SEAMM plug-in for setting up "
            "a forcefield or EAM potentials "
            "for subsequent simulations."
        },
        "from-smiles-step": {
            "description": "A SEAMM plug-in for creating "
            "structures from SMILES, "
            "InChI, InChIKey, or name."
        },
        "gaussian-step": {"description": "A SEAMM plug-in for Gaussian"},
        "geometry-analysis-step": {
            "description": "A SEAMM plug-in for "
            "analysis of the "
            "geometry of (small) "
            "molecules"
        },
        "golden-step": {
            "description": "A SEAMM plug-in that snapshots the "
            "current system to a JSON file and "
            "optionally verifies it against a "
            "reference, for golden testing."
        },
        "lammps-step": {
            "description": "A SEAMM plug-in for LAMMPS, a "
            "forcefield-based molecular "
            "dynamics (MD) code."
        },
        "loop-step": {
            "description": "A SEAMM plug-in which provides loops " "in flowcharts."
        },
        "model-chemistry-step": {
            "description": "A SEAMM step for setting "
            "the model chemistry for "
            "subsequent steps."
        },
        "mopac-step": {
            "description": "A SEAMM plug-in to setup, run and "
            "analyze semiempirical calculations "
            "with MOPAC"
        },
        "normal-mode-sampling-step": {
            "description": "A SEAMM plug-in for "
            "Wigner/thermal "
            "normal-mode sampling "
            "of the Hessian to "
            "generate displaced "
            "structures."
        },
        "orca-step": {
            "description": "A SEAMM plug-in for ORCA (accurate "
            "molecular QM, incl. DLPNO-CCSD(T))"
        },
        "packmol-step": {
            "description": "A SEAMM plug-in for building "
            "periodic boxes of fluid using "
            "Packmol"
        },
        "psi4-step": {
            "description": "A SEAMM plug-in to setup, run and "
            "analyze quantum chemistry "
            "calculations using Psi4"
        },
        "qcarchive-step": {
            "description": "A SEAMM plug-in for connecting " "with QCArchive"
        },
        "quickmin-step": {
            "description": "A SEAMM plug-in for simple, "
            "quick minimization using a "
            "forcefield"
        },
        "rdkit-step": {
            "description": "A SEAMM plug-in for RDKit " "descriptors/features"
        },
        "reaction-path-step": {
            "description": "A SEAMM plugin for finding "
            "transition states and "
            "reaction paths"
        },
        "read-structure-step": {
            "description": "A SEAMM plug-in to read "
            "structures from file "
            "formats common in "
            "computational chemistry"
        },
        "set-cell-step": {
            "description": "A SEAMM plug-in for setting the " "periodic (unit) cell."
        },
        "strain-step": {
            "description": "A SEAMM plug-in for straining " "periodic systems"
        },
        "structure-step": {
            "description": "A SEAMM plug-in for optimizing "
            "structures based on energy"
        },
        "subflowchart-step": {"description": "A SEAMM plug-in for " "subflowcharts"},
        "supercell-step": {
            "description": "A SEAMM plug-in for building "
            "supercells of periodic "
            "systems."
        },
        "table-step": {
            "description": "A SEAMM plug-in for data tables in " "a flowchart."
        },
        "thermal-conductivity-step": {
            "description": "A SEAMM plug-in for " "calculating thermal " "conductivity"
        },
        "thermochemistry-step": {
            "description": "A SEAMM plug-in for "
            "calculating "
            "thermochemical functions"
        },
        "thermomechanical-step": {
            "description": "A SEAMM plug-in for "
            "calculating "
            "thermomechanical "
            "properties"
        },
        "vasp-step": {
            "description": "A SEAMM plug-in for VASP, a " "planewave DFT code"
        },
        "xnn-step": {
            "description": "A SEAMM plug-in for machine-learned "
            "force fields trained with xnn, "
            "provided as model chemistries and run "
            "as MDI engines."
        },
        "xtb-step": {
            "description": "A SEAMM plug-in for the xTB family of "
            "extended tight-binding methods"
        },
    },
    "3rd-party plug-in": {
        "pyxtal-step": {
            "description": "A SEAMM plug-in for PyXtal, "
            "which builds atomic and "
            "molecular crystals."
        }
    },
    # Not installed: retired, shelved, or living in their own environment.
    "excluded plug-ins": [
        "seamm-dashboard",  # retired 2026-09; replaced by seamm-webui
        "cassandra-step",
        "chemical-formula",
        "cms-plots",
        "seamm-cookiecutter",
        "seamm-dashboard-client",
        "solvate-step",
        "nwchem-step",
        "properties-step",
        "torchani-step",  # shelved 2026-09-25: needs substantial work
        # These live in their own environments created by the plug-in installers
        "lammps-mdi",  # MDI engine for LAMMPS, in the seamm-lammps environment
        "xnns",  # the xnn MLFF code, in the seamm-xnn environment
        "seamm-webui",  # its own environment, made by the installer
    ],
    "development packages": [
        "black",
        "build",
        "codecov",
        "flake8",
        "pydata-sphinx-theme",
        "pygments",
        "pystemmer",
        "pytest",
        "pytest-cov",
        "rinohtype",
        "seamm-cookiecutter",
        "sphinx",
        "sphinx-copybutton",
        "sphinx-design",
        "sphinx-rtd-theme",
        "twine",
        "watchdog",
    ],
}
