# -*- coding: utf-8 -*-

'''
--------------------- Copyright Block ----------------------

Chart Finder Program (ver 0.1)
Copyright (C) 2017 Abdullah Radwan

License: GNU GPL v3.0

TERMS OF USE:
	Permission is granted to use this code, with or
	without modification, in any website or application
	provided that credit is given to the original work
	with a link back to Abdullah Radwan.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY.

PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.'''

# Import main libs

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

import requests, os, configparser, ast

# Import Glade File

builder = Gtk.Builder()

builder.add_from_file("ChartFinder.glade")

# Main class

class ChartFinder:

    # Initialization

    def __init__(self):

        # Set default value

        self.resources_list = ["http://vau.aero/navdb/chart/{0}.pdf","http://sa-ivao.net/charts_file/CHART-{0}.PDF",
                          "ottomanva.com/lib/charts/{0}.pdf","https://yinlei.org/x-plane10/jep/{0}.pdf",
                          "www.fly-sea.com/charts/{0}.pdf","www.uvairlines.com/admin/resources/charts/{0}.pdf"
                          ]

        # Import main objects

        self.settings_win = builder.get_object("settings_win")

        self.icao_code = builder.get_object("icao_code")

        self.aboutdialog = builder.get_object("aboutdialog")

        self.status_label = builder.get_object("status_label")

        self.res_entry = builder.get_object("resources_entry")

        self.add_label = builder.get_object("add_label")

        self.des_folder = builder.get_object("dest_folder")

        self.main_win = builder.get_object("main_win")

        # Set main objects

        self.read_config()

    # Get Chart

    def get_chart(self,widget=None):

        self.icao = self.icao_code.get_text()

        x = 0

        while True:

            try:

                response = requests.get((self.resources_list[x].format(self.icao)))

            except:

                self.status_label.set_label("Chart not found")

            if response.status_code == requests.codes.ok:

                with open("{0}.pdf".format(self.icao), 'wb') as f:

                    f.write(response.content)

                try:

                    destf = self.dest

                    destf = destf[8:]

                except:

                    destf = "folder"


                if destf == 'folder':

                    self.status_label.set_label("Chart Downloaded")

                    break

                else:

                    os.rename("{0}.pdf".format(self.icao),destf + "/{0}.pdf".format(self.icao))

                    self.status_label.set_label("Chart Downloaded")

                    break

            else:

                x = x + 1

                if x > len(self.resources_list):

                    self.status_label.set_label("Chart not found")

                    break

                else:

                    continue

    # Add new resource

    def add_resource(self,widget=None):

        res = self.res_entry.get_text()

        self.resources_list.append(res)

        self.add_label.set_label("Resource Added")

    # Read config

    def read_config(self):

        self.main_win.show_all()

        config = configparser.RawConfigParser()

        config.read("config.cfg")

        config1 = config.read("config.cfg")

        if config1 == []:

            return None

        else:

            self.dest = config.get("Settings","Path")

            self.resources_list = ast.literal_eval(config.get("Settings","ResourcesList"))

    # Write Config

    def write_config(self,widget=None):

        config = configparser.RawConfigParser()

        config.add_section('Settings')

        config.set("Settings", "Path", self.des_folder.get_uri())

        config.set("Settings", "ResourcesList", self.resources_list)

        with open('config.cfg', 'wt') as configfile:

            config.write(configfile)

    # Open settings window

    def show_settings(self,widget=None):

        self.settings_win.show_all()

    # Set about dialog

    def about_dialog(self,widget=None):

        self.aboutdialog.run()

        self.aboutdialog.hide_on_delete()

    def hide_settings(self,widget=None,data=None):
        self.settings_win.hide_on_delete()
        return True

    def quit(self,widget=None):

        Gtk.main_quit()
		
def main():
    builder.connect_signals(ChartFinder())
    Gtk.main()

main()