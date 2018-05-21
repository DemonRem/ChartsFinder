from threading import Thread
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
import time
import os
import shutil
import requests


class Downloader(QObject):

    # Set main signals
    start_download_process = pyqtSignal()

    show_dialog = pyqtSignal()

    set_progress = pyqtSignal(int)

    reset_dialog = pyqtSignal()

    finish_download_process = pyqtSignal()

    def __init__(self, system, res_list, dest_folder, progress_dialog, status_bar, icao_list, show_notify, open_file,
                 system_tray):

        # Init the super class
        super().__init__()

        # Set variables
        self.system = system

        self.resources_list = res_list

        self.dest_folder = dest_folder

        self.progress_dialog = progress_dialog

        self.status_bar = status_bar

        self.icao_list = icao_list

        self.view_notify = show_notify

        self.open_file = open_file

        self.system_tray = system_tray

        self.message = []

        self.cancel = False

    @pyqtSlot()
    def download(self):

        # If ICAO list isn't empty
        if not self.icao_list == []:

            # Call start download process
            self.start_download_process.emit()

            airport = 0

            # This loop will run the resources loop 1 per airport
            while airport < len(self.icao_list):

                # Set ICAO code
                icao_code = self.icao_list[airport]

                # Show message in status bar
                self.status_bar.showMessage("Searching for %s charts..." % icao_code)

                # Sleep for 1 sec
                time.sleep(1)

                resource = 0

                # Resources loop
                while True:

                    # Break loop if process canceled
                    if self.cancel: break

                    # Get result from check exist method
                    exist = self.check_exist(icao_code)

                    # If charts already exists
                    if exist[1]:

                        # Set message
                        self.message = ["%s charts already exists" % icao_code, QSystemTrayIcon.Warning]

                        # Open exists chart
                        if self.open_file: self.open_path(exist[0])

                        break

                    try:

                        # Check if chart exist in resource's server
                        response = requests.get(self.resources_list[resource][0].format(icao_code), stream=True)

                    except:

                        # Except will occur if resources over
                        self.message = ["Can't find %s charts" % icao_code, QSystemTrayIcon.Warning]

                        break

                    # If chart exists on the server
                    if response.status_code == requests.codes.ok:

                        # If resource is folder
                        if self.resources_list[resource][1] == "Folder":

                            # Set HTML parser
                            parser = BeautifulSoup(response.content, "html.parser")

                            # Download multiple charts
                            # Set URL
                            url = self.resources_list[resource][0].format(icao_code)

                            # Set path
                            path = os.path.join(self.dest_folder, icao_code)

                            try:

                                # Create chart folder
                                if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                                # Create airport folder in chart folder
                                os.mkdir(path)

                            except:

                                # Can't create airport folder
                                self.message = ["Can't create %s charts folder" % icao_code, QSystemTrayIcon.Critical]

                                break

                            element = 0

                            # Get each link
                            for link in parser.find_all('a'):

                                # If current link is url
                                current_link = link.get('href')

                                # Search for pdf files
                                if current_link.endswith('pdf'):

                                    # If notify is enabled and this is the first element (Avoid release notification
                                    # for each download)
                                    if self.view_notify and element == 0:

                                        self.system_tray.showMessage("Charts Finder", "Downloading %s charts..." % icao_code,
                                                                     QSystemTrayIcon.Information)

                                    # Set chart name by remove last 4 chars (.pdf)
                                    chart_name = current_link[:-4]

                                    # Set file path
                                    file_path = os.path.join(path, current_link)

                                    # Set status bar message
                                    self.status_bar.showMessage("Downloading %s charts..." % icao_code)

                                    # Set progress dialog title
                                    self.progress_dialog.setWindowTitle("Download %s charts" % icao_code)

                                    # Set status label
                                    self.progress_dialog.setLabelText("Downloading %s %s chart..." % (icao_code, chart_name))

                                    # Set progress to 0
                                    self.set_progress.emit(0)

                                    # Get current link data
                                    folder_response = requests.get(url.format(icao_code) + current_link, stream=True)

                                    # Get file size
                                    file_size = int(folder_response.headers['Content-Length'])

                                    # Call show dialog
                                    self.show_dialog.emit()

                                    # Set maximum to file size
                                    self.progress_dialog.setMaximum(file_size)

                                    # Open file
                                    file = open(file_path, 'wb')

                                    # Set progress to 1024
                                    progress = 1024

                                    for byte in folder_response.iter_content(1024):

                                        # If process canceled stop write file
                                        if self.cancel: break

                                        # Write data
                                        file.write(byte)

                                        # Set progress
                                        self.set_progress.emit(progress)

                                        QApplication.processEvents()

                                        # Set progress
                                        progress += 1024

                                    # Close file
                                    file.close()

                                    # Remove folder with its contents if canceled
                                    if self.cancel: shutil.rmtree(path); break

                                    # Call reset dialog
                                    self.reset_dialog.emit()

                                    element += 1

                            # Break if download canceled
                            if self.cancel: break

                            # Finish download all files
                            self.message = ["%s charts downloaded" % icao_code, QSystemTrayIcon.Information]

                            if self.open_file: self.open_path(path)

                            break

                        # If resource is normal
                        else:

                            try:

                                # Create chart folder
                                if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                            except:

                                # Can't create folder
                                self.message = ["Can't create %s charts folder" % icao_code, QSystemTrayIcon.Critical]

                                break

                            if self.view_notify:

                                self.system_tray.showMessage("Charts Finder", "Downloading %s charts..." % icao_code,
                                                             QSystemTrayIcon.Information)

                            # Set file path
                            file_path = os.path.join(self.dest_folder, icao_code + ".pdf")

                            # Get file size
                            file_size = int(response.headers['Content-Length'])

                            # Set status bar
                            self.status_bar.showMessage("Downloading %s charts..." % icao_code)

                            # Set progress dialog title
                            self.progress_dialog.setWindowTitle("Download %s charts" % icao_code)

                            # Set text
                            self.progress_dialog.setLabelText("Downloading %s charts..." % icao_code)

                            # Set progress to 0
                            self.set_progress.emit(0)

                            # Call show dialog
                            self.show_dialog.emit()

                            # Set maximum to file size
                            self.progress_dialog.setMaximum(file_size)

                            # Open file
                            file = open(file_path, 'wb')

                            progress = 1024

                            for chunk in response.iter_content(1024):

                                if self.cancel: break

                                file.write(chunk)

                                self.set_progress.emit(progress)

                                QApplication.processEvents()

                                progress += 1024

                            file.close()

                            # Remove chart file if process canceled
                            if self.cancel: os.remove(file_path); break

                            self.message = ["%s charts downloaded" % icao_code, QSystemTrayIcon.Information]

                            if self.open_file: self.open_path(file_path)

                            break

                    # If chart isn't exist on server, will try with another resource
                    else: resource += 1

                if self.cancel: break

                # Set message to current message
                self.status_bar.showMessage(self.message[0])

                if self.view_notify: self.system_tray.showMessage("Charts Finder", self.message[0], self.message[1])

                airport += 1

                # If no another airport, no need to delay
                try:

                    self.icao_list[airport]

                    self.reset_dialog.emit()

                    time.sleep(3)

                except: break

        # No ICAO code entered
        else: self.status_bar.showMessage("Please enter an ICAO code")

        if self.cancel: self.status_bar.showMessage("Download canceled")

        self.finish_download_process.emit()

    def check_exist(self, icao_code):

        exist = False

        # Try for folder chart first
        path = os.path.join(self.dest_folder, icao_code)

        if os.path.exists(path): exist = True

        # Try for normal chart
        else:

            path = os.path.join(self.dest_folder, icao_code + ".pdf")

            if os.path.exists(path): exist = True

        return [path, exist]

    # Open file or path after download
    def open_path(self, path):

        # If system is Windows, we will use os.startfile
        if self.system == "win32": Thread(target=os.startfile, args=(path,)).start()

        # Else, use open for Mac or xdg-open for Linux
        else:

            opener = "open " if self.system == "darwin" else "xdg-open "

            Thread(target=os.system, args=(opener + path,)).start()
