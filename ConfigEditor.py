import ast
import configparser
import time
import os


class ConfigEditor:

    def __init__(self, system): self.set_config_path(system)

    def read_config(self):

        # Read config file
        config = configparser.RawConfigParser()

        config1 = config.read(self.config_file_path)

        # If no config file, reset resources and set destination folder to 'Charts' folder
        if config1 == []: self.reset_config()

        else:

            try:

                # Get config data

                # Get destination folder
                self.dest_folder = config.get("Settings", "path")

                # Get the resource list from config file
                self.resources_list = ast.literal_eval(config.get("Settings", "resources_list"))

                # Set open chart
                self.open_file = ast.literal_eval(config.get("Settings", "open_file"))

                # Set view notifications
                self.view_notify = ast.literal_eval(config.get("Settings", "view_notify"))

            # Reset config if read fail
            except: self.reset_config()

        # Return destination folder and resource list
        return [self.dest_folder, self.resources_list, self.open_file, self.view_notify]

    def write_config(self, dest_folder, res_list, open_file, view_notify):

        config = configparser.RawConfigParser()

        config.add_section('Settings')

        config.set("Settings", "path", dest_folder)

        config.set("Settings", "resources_list", res_list)

        config.set("Settings", "open_file", open_file)

        config.set("Settings", "view_notify", view_notify)

        with open(self.config_file_path, 'wt') as configfile:

            config.write(configfile)

            configfile.close()

    def set_config_path(self, system):

        # If system is Windows, we will write config file in main path
        if system == "win32": self.config_file_path = "config.cfg"

        # Else, we will write config file to '.charts-finder' folder
        else:

            self.config_file_path = ".charts-finder/config.cfg"

            # Create folder if it not exists
            if not os.path.exists(".charts-finder"): os.mkdir(".charts-finder")

    def reset_config(self):

        self.dest_folder = os.path.join(os.getcwd(), "Charts")

        self.open_file = True

        self.view_notify = True

        self.show_progressbar = True

        # Set default resources
        self.resources_list = [["http://www.armats.com/arm/aviation/products/eAIP/pdf/UD-AD-2.{0}-en-GB.pdf", "Normal"],
                               ["http://www.sia-enna.dz/PDF/AIP/AD/AD2/{0}/", "Folder"],
                               ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % time.strftime("%y%m", time.gmtime()), "Normal"],
                               ["http://vau.aero/navdb/chart/{0}.pdf", "Normal"],
                               ["http://ottomanva.com/lib/charts/{0}.pdf", "Normal"],
                               ["https://yinlei.org/x-plane10/jep/{0}.pdf", "Normal"],
                               ["http://sa-ivao.net/charts_file/{0}.pdf", "Normal"],
                               ["http://www.fly-sea.com/charts/{0}.pdf", "Normal"],
                               ["http://uvairlines.com/admin/resources/charts/{0}.pdf", "Normal"],
                               ["https://www.virtualairlines.eu/charts/{0}.pdf", "Normal"]
                               ]
