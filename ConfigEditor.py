import ast
import configparser
import time
import os


class ConfigEditor:

    def __init__(self, notify_check, open_chart_check):

        # Set variables
        self.airac = time.strftime("%y%m", time.gmtime())

        self.notify_check = notify_check

        self.open_chart_check = open_chart_check

    def read_config(self):

        # Read config file
        config = configparser.RawConfigParser()

        config1 = config.read("config.cfg")

        # If no config file
        if config1 == []:

            # Reset resources
            self.set_res()

            # Set folder to default folder
            self.dest_folder = os.getcwd() + "\\Charts\\"

        else:
            # Get config data:

            # Get destination folder
            self.dest_folder = config.get("Settings", "Path")

            # Get the resource list from config file
            self.resources_list = ast.literal_eval(config.get("Settings", "ResourcesList"))

            # Update fltplan airac
            try:

                # Get where is it
                g = 0

                while g < len(self.resources_list):

                    try:

                        # Index resource
                        a = self.resources_list[g].index(
                            "http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

                        b = g

                        break

                    except: g += 1

                # Remove the old one
                self.resources_list.pop[b](0)

                # Add new Airac
                self.resources_list[b].insert(a, "http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

            # If fltplan not exists
            except: pass

            # Set open chart
            self.open_chart_check.set_active(ast.literal_eval(config.get("Settings", "OpenPDF")))

            # Set view notifications
            self.notify_check.set_active(ast.literal_eval(config.get("Settings", "ViewNotify")))

        # Return destination folder and resource list
        return [self.dest_folder, self.resources_list]

    def write_config(self, dest_folder, res_list):

        config = configparser.RawConfigParser()

        config.add_section('Settings')

        config.set("Settings", "Path", dest_folder)

        config.set("Settings", "ResourcesList", res_list)

        config.set("Settings", "OpenPDF", self.open_chart_check.get_active())

        config.set("Settings", "ViewNotify", self.notify_check.get_active())

        with open('config.cfg', 'wt') as configfile:
            config.write(configfile)

    def set_res(self):

        # Set default resources
        self.resources_list = [["http://www.armats.com/arm/aviation/products/eAIP/pdf/UD-AD-2.{0}-en-GB.pdf", "Normal"],
                               ["http://www.sia-enna.dz/PDF/AIP/AD/AD2/{0}/", "Folder"],
                               ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac, "Normal"],
                               ["http://vau.aero/navdb/chart/{0}.pdf", "Normal"],
                               ["http://ottomanva.com/lib/charts/{0}.pdf", "Normal"],
                               ["https://yinlei.org/x-plane10/jep/{0}.pdf", "Normal"],
                               ["http://sa-ivao.net/charts_file/{0}.pdf", "Normal"],
                               ["http://www.fly-sea.com/charts/{0}.pdf", "Normal"],
                               ["http://uvairlines.com/admin/resources/charts/{0}.pdf", "Normal"],
                               ["https://www.virtualairlines.eu/charts/{0}.pdf", "Normal"]
                               ]
