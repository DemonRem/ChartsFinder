from bs4 import BeautifulSoup
from gi.repository import GLib
from threading import Thread
import time
import os
import sys
import requests
import subprocess


class Downloader:

    def __init__(self, res_list, dest_folder, status_label, get_button, icao_entry, notify_check, open_chart_check):

        # Set variables
        self.resources_list = res_list

        self.dest_folder = dest_folder

        self.status_label = status_label

        self.get_button = get_button

        self.icao_entry = icao_entry

        self.view_notify = notify_check.get_active()

        self.open_chart = open_chart_check.get_active()

    def download(self):

        icao = self.icao_entry.get_text().upper().split()

        if not icao == []:

            # x is resources number, z is airports number
            x = 0

            z = 0

            # This loop will run the inner loop 1 per airport
            while z < len(icao):

                # Set ICAO code
                icao_code = icao[z]

                # Disable button and entry box
                GLib.idle_add(self.get_button.set_sensitive, False)

                GLib.idle_add(self.icao_entry.set_sensitive, False)

                # Set download
                GLib.idle_add(self.status_label.set_label, "Downloading %s charts..." % icao_code)

                if self.view_notify:
                    Thread(target=subprocess.call,
                           args=(["notify-send", "ChartsFinder", "Downloading %s charts..." % icao_code],)).start()

                time.sleep(1)

                # Resources loop
                while True:

                    # If charts already exists
                    if self.check_chart(icao_code):

                        GLib.idle_add(self.status_label.set_label, "%s charts already exists" % icao_code)

                        if self.view_notify:
                            Thread(target=subprocess.call,
                                   args=(["notify-send", "Charts Finder", "%s charts already exists" % icao_code],)).start()

                        break

                    try:

                        # Check if chart exist in resource's server
                        response = requests.get(self.resources_list[x][0].format(icao_code))

                    except:

                        # If chart isn't exist
                        GLib.idle_add(self.status_label.set_label, "%s charts not found" % icao_code)

                        # Run notify
                        if self.view_notify:
                            Thread(target=subprocess.call,
                                   args=(["notify-send", "Charts Finder", "%s charts not found" % icao_code],)).start()

                        break

                    # If chart exists on the server
                    if response.status_code == requests.codes.ok:

                        # If resource is folder
                        if self.resources_list[x][1] == "Folder":

                            # Set path
                            path = os.path.join(self.dest_folder, icao_code)

                            try:

                                # Create airport folder in path
                                if not os.path.exists(path): os.mkdir(path)

                            except:

                                # Can't create airport folder
                                GLib.idle_add(self.status_label.set_label, "Can't create %s charts folder" % icao_code)

                                if self.view_notify:
                                    Thread(target=subprocess.call,
                                           args=(["notify-send", "Charts Finder", "Can't create %s charts folder" % icao_code],)).start()

                                break

                            # Set HTML parser
                            parser = BeautifulSoup(response.content, "html.parser")

                            # Download multiple charts
                            # Set URL
                            url = self.resources_list[x][0].format(icao_code)

                            # Get each link
                            for link in parser.find_all('a'):

                                # If current link is url
                                current_link = link.get('href')

                                # Search for pdf files
                                if current_link.endswith('pdf'):

                                    # Set file path
                                    file_path = os.path.join(path, current_link)

                                    # Write each file
                                    with open(file_path, 'wb') as f:

                                        f.write(requests.get(url.format(icao_code) + current_link).content)

                                        f.close()

                            GLib.idle_add(self.status_label.set_label, "%s charts Downloaded" % icao_code)

                            if self.view_notify:
                                    Thread(target=subprocess.call,
                                           args=(["notify-send", "Charts Finder", "%s charts downloaded" % icao_code],)).start()

                            if self.open_chart: self.open_file(path)

                        # If resource is normal
                        else:

                            try:

                                # Create chart folder
                                if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                            except:

                                # Can't create folder
                                GLib.idle_add(self.status_label.set_label,
                                                "Can't create %s charts folder" % icao_code)

                                if self.view_notify:
                                    Thread(target=subprocess.call,
                                            args=(["notify-send", "Charts Finder",
                                                    "Can't create %s charts folder" % icao_code],)).start()

                                break

                            # Set file path
                            file_path = os.path.join(self.dest_folder, "{0}.pdf".format(icao_code))

                            # Write the chart to pdf file
                            with open(file_path, 'wb') as f:

                                f.write(response.content)

                                f.close()

                            try:

                                # Move success
                                GLib.idle_add(self.status_label.set_label, "%s charts downloaded" % icao_code)

                                if self.view_notify:
                                    Thread(target=subprocess.call,
                                           args=(["notify-send", "Charts Finder", "%s charts downloaded" % icao_code],)).start()

                                if self.open_chart: self.open_file(file_path)

                            except:

                                # Move failed
                                GLib.idle_add(self.status_label.set_label, "Can't move %s charts" % icao_code)

                                if self.view_notify:
                                    Thread(target=subprocess.call,
                                           args=(["notify-send", "Charts Finder", "Can't move %s charts" % icao_code],)).start()

                            break

                    # If chart isn't exist on server
                    else:

                        # Trying with another resource
                        x += 1

                time.sleep(2)

                z += 1

        else: GLib.idle_add(self.status_label.set_label, "Please enter an ICAO code")

        # Return button to active
        GLib.idle_add(self.get_button.set_sensitive, True)

        GLib.idle_add(self.icao_entry.set_sensitive, True)

    def check_chart(self, icao_code):

        exist = False

        # Try for folder chart first
        path = os.path.join(self.dest_folder, icao_code)

        if os.path.exists(path): exist = True

        # Try for normal chart
        else:

            path = os.path.join(self.dest_folder, icao_code + ".pdf")

            if os.path.exists(path): exist = True

        return exist

    # Open file or path after download
    def open_file(self, filename):

        # If system is Windows, we will use os.startfile
        if sys.platform == "win32": Thread(target=os.startfile, args=(filename,)).start()

        # Else, use open for Mac or xdg-open for Linux
        else:

            opener = "open" if sys.platform == "darwin" else "xdg-open"

            Thread(target=subprocess.call, args = ([opener, filename],)).start()
