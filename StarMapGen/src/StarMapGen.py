import os
import sys
from pathlib import Path

import wx

from SMGFrame import SMGFrame


def configureWorkingDirectory():
    """Use the executable directory for generated and loaded files."""

    if getattr(sys, "frozen", False):
        applicationDirectory = (
            Path(sys.executable)
            .resolve()
            .parent
        )

        os.chdir(applicationDirectory)


def main():
    configureWorkingDirectory()

    application = wx.App(False)
    SMGFrame()
    application.MainLoop()


if __name__ == "__main__":
    main()