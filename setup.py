from cx_Freeze import setup, Executable

# Get an error without this
excludes = ["PyQt5.uic"]

# Set requirements
packages = ["idna", "requests", "queue", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "bs4", "os", "configparser",
            "ast", "threading", "time", "shutil", "sys"]

# Include project files
includes = ["AddResDialog.py", "ConfigEditor.py", "Downloader.py", "SettingsWindow.py", "icon.svg"]

setup(
        name = "Charts Finder",
        version = "1.1",
        description = "Charts Finder",
        author = "Abdullah Radwan",
        options = {"build_exe" : {"packages": packages, "excludes": excludes, "include_files": includes, "include_msvcr": True}},
        executables = [Executable("ChartsFinder.py", base = "Win32GUI")])
