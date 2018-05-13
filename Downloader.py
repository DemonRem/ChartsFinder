import time
import os
import shutil
import requests
from bs4 import BeautifulSoup
from gi.repository import GLib
from threading import Thread


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
                    Thread(target=os.system,
                           args=("notify-send ChartsFinder Downloading %s charts..." % icao_code,)).start()

                time.sleep(1)

                # Resources loop
                while True:

                    # If charts already exists
                    if self.check_chart(icao_code):

                        GLib.idle_add(self.status_label.set_label, "%s charts already exists" % icao_code)

                        if self.view_notify:
                            Thread(target=os.system,
                                   args=("notify-send ChartsFinder %s charts already exists" % icao_code,)).start()

                        break

                    try:

                        # Check if chart exist in resource's server
                        response = requests.get(self.resources_list[x][0].format(icao_code))

                    except:

                        # If chart isn't exist
                        GLib.idle_add(self.status_label.set_label, "%s charts not found" % icao_code)

                        # Run notify
                        if self.view_notify:
                            Thread(target=os.system,
                                   args=("notify-send ChartsFinder %s charts not found" % icao_code,)).start()

                        break

                    # If chart exists on the server
                    if response.status_code == requests.codes.ok:

                        # If resource is folder
                        if self.resources_list[x][1] == "Folder":

                            # Create airport folder in destination folder
                            path = self.dest_folder + icao_code

                            if not os.path.exists(path): os.mkdir(path)

                            # Set HTML parser
                            sopa = BeautifulSoup(response.content, "html.parser")

                            # Download multiple charts
                            try:

                                # Set URL
                                url = self.resources_list[x][0].format(icao_code)

                                # Get each link
                                for link in sopa.find_all('a'):

                                    # If current link is url
                                    current_link = link.get('href')

                                    # Search for pdf files
                                    if current_link.endswith('pdf'):

                                        # Write each file and move it
                                        with open(current_link, 'wb') as f:

                                            f.write(requests.get(url.format(icao_code) + current_link).content)

                                            f.close()

                                            shutil.move(current_link, path)

                                GLib.idle_add(self.status_label.set_label, "%s Charts Downloaded" % icao_code)

                                if self.view_notify:
                                    Thread(target=os.system,
                                           args=("notify-send ChartsFinder %s charts downloaded" % icao_code,)).start()

                                if self.open_chart: os.startfile(path)

                            # If move fail
                            except:

                                GLib.idle_add(self.status_label.set_label, "Can't move %s charts" % icao_code)

                                if self.view_notify:
                                    Thread(target=os.system,
                                           args=("notify-send ChartsFinder Can't move %s charts" % icao_code,)).start()

                            break

                        # If resource is normal
                        else:

                            # This will work if 'Charts' folder not exists
                            if not os.path.exists(self.dest_folder): os.mkdir(self.dest_folder)

                            # Write the chart to pdf file
                            with open("{0}.pdf".format(icao_code), 'wb') as f:

                                f.write(response.content)

                                f.close()

                            try:

                                # Trying to move chart
                                shutil.move("{0}.pdf".format(icao_code), self.dest_folder)

                                # Move success
                                GLib.idle_add(self.status_label.set_label, "%s charts downloaded" % icao_code)

                                if self.view_notify:
                                    Thread(target=os.system, args=(
                                        "notify-send ChartsFinder %s charts downloaded" % icao_code,)).start()

                                if self.open_chart:
                                    Thread(target=os.startfile,
                                            args=(self.dest_folder + "{0}.pdf".format(icao_code),)).start()

                            except:

                                # Move failed
                                GLib.idle_add(self.status_label.set_label, "Can't move %s charts" % icao_code)

                                if self.view_notify:
                                    Thread(target=os.system, args=(
                                        "notify-send ChartsFinder Can't move %s charts" % icao_code,)).start()

                            break

                    # If chart isn't exist on server
                    else:

                        # Trying with another resource
                        x += 1

                time.sleep(3)

                z += 1

        else: GLib.idle_add(self.status_label.set_label, "Please enter an ICAO code")

        # Return button to active
        GLib.idle_add(self.get_button.set_sensitive, True)

        GLib.idle_add(self.icao_entry.set_sensitive, True)

    def check_chart(self, icao_code):

        exist = False

        # Try for folder chart first
        path = self.dest_folder + icao_code

        if os.path.exists(path): exist = True

        # Try for normal chart
        else:

            path = self.dest_folder + icao_code + ".pdf"

            if os.path.exists(path): exist = True

        return exist
