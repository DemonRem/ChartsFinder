from cx_Freeze import setup, Executable
import os
import site

# Get the site-package folder
site_dir = site.getsitepackages()[1]

# Set DLLs path
include_dll_path = os.path.join(site_dir, "gnome")

# Set missing DLLs
missing_dll = ['libgtk-3-0.dll',
               'libgdk-3-0.dll',
               'libatk-1.0-0.dll',
               'libcairo-gobject-2.dll',
               'libgdk_pixbuf-2.0-0.dll',
               'libjpeg-8.dll',
               'libpango-1.0-0.dll',
               'libpangocairo-1.0-0.dll',
               'libpangoft2-1.0-0.dll',
               'libpangowin32-1.0-0.dll']


# Set GTK libraries
gtk_libs = ['etc', 'lib', 'share']

# Set project files
project_files = ["ChartsFinder.glade", "ConfigEditor.py", "Downloader.py", "notify-send.exe"]

# Create the list of includes as cx_freeze likes
include_files = []

# Add missing dll files
for dll in missing_dll: include_files.append((os.path.join(include_dll_path, dll), dll))

# Add GTK libraries
for lib in gtk_libs: include_files.append((os.path.join(include_dll_path, lib), lib))

# Add project files
for file in project_files: include_files.append(file)

# Set executables
executables = [Executable("ChartsFinder.py", base="Win32GUI")]

buildOptions = dict(
    includes = ["gi", "requests", 'idna', 'queue', 'os', 'configparser', 'ast', 'threading', 'subprocess', 'time', 'bs4'],
    packages = ["gi", "requests", 'idna', 'queue', 'os', 'configparser', 'ast', 'threading', 'subprocess', 'time', 'bs4'],
    include_files = include_files
    )

setup(
    name = "Charts Finder",
    author = "Abdullah Radwan",
    version = "1.0.6",
    description = "Get charts for your flight!",
    options = dict(build_exe = buildOptions),
    executables = executables
)