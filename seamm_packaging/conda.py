# -*- coding: utf-8 -*-
import json
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys
import warnings

import semver

logger = logging.getLogger("seamm_packages")


class Conda(object):
    """
    Class for handling conda

    Attributes
    ----------

    """

    def __init__(self, logger=logger):
        logger.debug(f"Creating Conda {str(type(self))}")

        self._is_installed = False
        self._data = None
        self.logger = logger
        self.channels = ["local", "conda-forge"]
        self.root_path = None

        # self._initialize()

    def search(
        self,
        query=None,
        channels=None,
        override_channels=True,
        progress=True,
        newline=True,
        update=None,
    ):
        """Run conda search, returning a dictionary of packages.

        Parameters
        ----------
        query: str = None
            The pattern to search, Defaults to None, meaning all packages.
        channels: [str] = None
            A list of channels to search. defaults to the list in self.channels.
        override_channels: bool = True
            Ignore channels configured in .condarc and the default channel.
        progress : bool = True
            Whether to show progress dots.
        newline : bool = True
            Whether to print a newline at the end if showing progress
        update : None or method
            Method to call to e.g. update a progress bar

        Returns
        -------
        dict
            A dictionary of packages, with versions for each.
        """
        command = "conda search --json"
        if override_channels:
            command += " --override-channels"
        if channels is None:
            for channel in self.channels:
                command += f" -c {channel}"
        else:
            for channel in channels:
                command += f" -c {channel}"
        if query is not None:
            command += f" '{query}'"

        _, stdout, _ = self._execute(
            command, progress=progress, newline=newline, update=update
        )
        try:
            output = json.loads(stdout)
        except Exception as e:
            self.logger.warning(
                f"expected output from {command}, got {stdout}", exc_info=e
            )
            return None

        if "error" in output:
            return None

        result = {}
        for package, data in output.items():
            result[package] = {
                "channel": data[-1]["channel"],
                "version": data[-1]["version"],
                "description": "not available",
            }

        return result

    def _execute(
        self, command, poll_interval=2, progress=True, newline=True, update=None
    ):
        """Execute the command as a subprocess.

        Parameters
        ----------
        command : str
            The command, with any arguments, to execute.
        poll_interval : int
            Time interval in seconds for checking for output.
        progress : bool = True
            Whether to show progress dots.
        newline : bool = True
            Whether to print a newline at the end if showing progress
        update : None or method
            Method to call to e.g. update a progress bar
        """
        self.logger.info(f"running '{command}'")
        args = shlex.split(command)
        process = subprocess.Popen(
            args,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        n = 0
        stdout = ""
        stderr = ""
        while True:
            self.logger.debug("    checking if finished")
            result = process.poll()
            if result is not None:
                self.logger.info(f"    finished! result = {result}")
                break
            try:
                self.logger.debug("    calling communicate")
                output, errors = process.communicate(timeout=poll_interval)
            except subprocess.TimeoutExpired:
                self.logger.debug("    timed out")
                if progress:
                    if update is None:
                        print(".", end="")
                        n += 1
                        if n >= 50:
                            print("")
                            n = 0
                        sys.stdout.flush()
                    else:
                        update()
            else:
                if output != "":
                    stdout += output
                    self.logger.debug(output)
                if errors != "":
                    stderr += errors
                    self.logger.debug(f"stderr: '{errors}'")
        if progress and newline and n > 0:
            if update is None:
                print("")
        return result, stdout, stderr
