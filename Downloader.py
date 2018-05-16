from gi.repository import GLib
from threading import Thread
from bs4 import BeautifulSoup
import time
import os
import shutil
import requests
import subprocess


class Downloader:

    def __init__(self, system, res_list, dest_folder, status_label, get_button, icao_entry, show_notify,
                 open_chart):

        # Set variables
        self.system = system

        self.resources_list = res_list

        self.dest_folder = dest_folder

        self.status_label = status_label

        self.get_button = get_button

        self.icao_entry = icao_entry

        self.view_notify = show_notify

        self.open_chart = open_chart

        self.message = []

        self.cancel = False

    def download(self):

        # Get entries as an upper case list separated with space
        icao = self.icao_entry.get_text().upper().split()

        if not icao == []:

            # Disable button and entry box
            GLib.idle_add(self.get_button.set_sensitive, False)

            GLib.idle_add(self.icao_entry.set_sensitive, False)

            airport = 0

            # This loop will run the resources loop 1 per airport
            while airport < len(icao):

                # Set ICAO code
                icao_code = icao[airport]

                # Set download
                GLib.idle_add(self.status_label.set_label, "Downloading %s charts..." % icao_code)

                if self.view_notify:

                    Thread(target=subprocess.call,
                           args=(["notify-send", "-i", "info", "Charts Finder", "Downloading %s charts..." % icao_code],)
                           ).start()

                time.sleep(1)

                resource = 0

                # Resources loop
                while True:

                    exist = self.check_chart(icao_code)

                    # If charts already exists
                    if exist[1]:

                        self.message = ["%s charts already exists" % icao_code, "error"]

                        if self.open_chart: self.open_file(exist[0])

                        break

                    try:

                        # Check if chart exist in resource's server
                        response = requests.get(self.resources_list[resource][0].format(icao_code), stream=True)

                    except:

                        # If chart isn't exist
                        self.message = ["Can't find %s charts" % icao_code, "error"]

                        break

                    # If chart exists on the server
                    if response.status_code == requests.codes.ok:

                        # If resource is folder
                        if self.resources_list[resource][1] == "Folder":

                            # Set path
                            path = os.path.join(self.dest_folder, icao_code)

                            try:

                                # Create chart folder
                                if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                                # Create airport folder in chart folder
                                os.mkdir(path)

                            except:

                                # Can't create airport folder
                                self.message = ["Can't create %s charts folder" % icao_code, "error"]

                                break

                            # Set HTML parser
                            parser = BeautifulSoup(response.content, "html.parser")

                            # Download multiple charts
                            # Set URL
                            url = self.resources_list[resource][0].format(icao_code)

                            # Get each link
                            for link in parser.find_all('a'):

                                # If current link is url
                                current_link = link.get('href')

                                # Search for pdf files
                                if current_link.endswith('pdf'):

                                    # Set chart name by remove last 4 chars (.pdf)
                                    chart_name = current_link[:-4]

                                    # Set file path
                                    file_path = os.path.join(path, current_link)

                                    # Get current link data
                                    file_response = requests.get(url.format(icao_code) + current_link, stream=True)

                                    # Open file
                                    file = open(file_path, 'wb')

                                    # Set status label
                                    GLib.idle_add(self.status_label.set_label, "Downloading %s %s chart..." % (icao_code, chart_name))

                                    for chunk in file_response.iter_content():

                                        file.write(chunk)

                                        # If process canceled stop write file
                                        if self.cancel: break

                                    file.close()

                                    # Remove folder with its contents if canceled
                                    if self.cancel: shutil.rmtree(path); break

                            # Finish download all files
                            self.message = ["%s charts downloaded" % icao_code, "info"]

                            if self.open_chart: self.open_file(path)

                            break

                        # If resource is normal
                        else:

                            try:

                                # Create chart folder
                                if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                            except:

                                # Can't create folder
                                self.message = ["Can't create %s charts folder" % icao_code, "error"]

                                break

                            # Set file path
                            file_path = os.path.join(self.dest_folder, icao_code + ".pdf")

                            # Open file
                            file = open(file_path, 'wb')

                            for chunk in response.iter_content():

                                file.write(chunk)

                                if self.cancel: break

                            file.close()

                            # Remove chart file if process canceled
                            if self.cancel: os.remove(file_path); break

                            self.message = ["%s charts downloaded" % icao_code, "info"]

                            if self.open_chart: self.open_file(file_path)

                            break

                    # If chart isn't exist on server, will try with another resource
                    else: resource += 1

                if self.cancel: break

                GLib.idle_add(self.status_label.set_label, self.message[0])

                if self.view_notify:

                    Thread(target=subprocess.call,
                           args=(["notify-send", "-i", self.message[1], "Charts Finder", self.message[0]],)).start()

                airport += 1

                # If no another airport, no need to delay
                try: icao[airport]; time.sleep(3)

                except: pass

            # Return button and entry to active
            GLib.idle_add(self.get_button.set_sensitive, True)

            GLib.idle_add(self.icao_entry.set_sensitive, True)

        else: GLib.idle_add(self.status_label.set_label, "Please enter an ICAO code")

    def check_chart(self, icao_code):

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
    def open_file(self, file_name):

        # If system is Windows, we will use os.startfile
        if self.system == "win32": Thread(target=os.startfile, args=(file_name,)).start()

        # Else, use open for Mac or xdg-open for Linux
        else:

            opener = "open" if self.system == "darwin" else "xdg-open"

            Thread(target=subprocess.call, args = ([opener, file_name],)).start()
