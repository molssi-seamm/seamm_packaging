=================
Support for MacOS
=================

This directory containes the necessary files to add applications for SEAMM and the
Dashboard for MacOS. The files are

- **Dashboard.app/**

  - **Contents/**

    - **Info.plist** This file contains the information about the application, such as the
      name, version, and the icon to use. This file is used by MacOS to display the
      application in the Finder and in the Dock.

    - **MacOS/** This directory contains the executable file for the application.

      - **Dashboard** This is the executable file for the application. It is a shell script.

    - **Resources/** This directory contains the icon for the application.

      - **Dashboard.icns** This is the icon for the application. It is used by MacOS to display
	the application in the Finder and in the Dock.

      - **seamm-environment.yml** This is the Docker Compose file that is used to start
	the SEAMM enviromnet -- the *Dashboard* and *JobServer*

- **Makefile** This file contains targets to make the ZIP files for the documentation.

- **SEAMM.app/**

  - **Contents/**

    - **Info.plist** This file contains the information about the application, such as the
      name, version, and the icon to use. This file is used by MacOS to display the
      application in the Finder and in the Dock.

    - **MacOS/** This directory contains the executable file for the application.

      - **SEAMM** This is the executable file for the application. It is a shell script.

    - **Resources/** This directory contains the icon for the application.

      - **SEAMM.icns** This is the icon for the application. It is used by MacOS to display
	the application in the Finder and in the Dock.

	
Whenever changes are made to the two app directories, **make** should be run to put the
ZIP files into the **molssi-seamm.github.io** package and the documentation should be remade.
