# -*- coding: utf-8 -*-

'''
--------------------- Copyright Block ----------------------

Chart Finder Program (ver 1.0)
Copyright (C) 2018 Abdullah Radwan

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

from gi.repository import Gtk, GObject, GLib

import requests, os, configparser, ast, _thread, shutil, time

# Import Glade File

builder = Gtk.Builder()

builder.add_from_file("ChartFinder.glade")

# Main class

class ChartFinder:

    # Initialization

    def __init__(self):

        # Set default value

        self.airac = time.strftime("%y%m", time.gmtime())

        self.resources_list = ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac,"http://vau.aero/navdb/chart/{0}.pdf","http://sa-ivao.net/charts_file/CHART-{0}.PDF",
                          "ottomanva.com/lib/charts/{0}.pdf","https://yinlei.org/x-plane10/jep/{0}.pdf",
                          "www.fly-sea.com/charts/{0}.pdf","www.uvairlines.com/admin/resources/charts/{0}.pdf"
                          ]

        # Import main objects

        self.settings_win = builder.get_object("settings_win")

        self.icao_code = builder.get_object("icao_code")

        self.aboutdialog = builder.get_object("aboutdialog")

        self.status_label = builder.get_object("status_label")

        self.stat_label = builder.get_object("stat_label")

        self.des_folder = builder.get_object("dest_folder")

        self.open_check = builder.get_object("checkbutton1")

        self.res_liststore = builder.get_object("res_list")

        self.treeview = builder.get_object("treeview1")

        self.res_win = builder.get_object("add_res_win")

        self.res_entry = builder.get_object("res_entry")

        self.order_entry = builder.get_object("order_entry")

        self.res_stat_label = builder.get_object("add_res_stat_label")

        self.main_win = builder.get_object("main_win")

        # Set main objects

        self.read_config()

    # Get Chart

    def get_chart(self):

        # Get ICAO code

        self.icao = self.icao_code.get_text().upper()

        x = 0

        while True:

            try:

                # Check if chart exist in resource

                response = requests.get((self.resources_list[x].format(self.icao)))

            except:

                # If chart isn't exist

                GLib.idle_add(self.status_label.set_label,"Chart not found")

                break

            # If chart exists on the server

            if response.status_code == requests.codes.ok:

                # Write the chart to pdf file

                with open("{0}.pdf".format(self.icao), 'wb') as f:

                    f.write(response.content)

                try:

                    # If a folder has been selected to save to it.

                    destf = self.dest

                    self.destf = destf[8:]

                except:

                    # If no folder has been selected

                    self.destf = "folder"

                if self.destf == 'folder':

                    GLib.idle_add(self.status_label.set_label,"Chart Downloaded")

                    # If user want to open chart

                    if self.open_check.get_active() == True:

                        os.startfile("{0}.pdf".format(self.icao))

                    break

                # If a folder has been selected

                else:

                    try:

                        # Trying to move chart

                        shutil.move("{0}.pdf".format(self.icao),self.destf)

                    except:

                        # The error will occur only if chart is already exists

                        GLib.idle_add(self.status_label.set_label, "Chart Already Exists")

                    GLib.idle_add(self.status_label.set_label,"Chart Downloaded")

                    if self.open_check.get_active() == True:

                        os.startfile(self.destf + "/{0}.pdf".format(self.icao))

                    break

            # If chart isn't exist on server

            else:

                # Trying with another resource

                x = x + 1

                # If resources has over

                if x > len(self.resources_list):

                    GLib.idle_add(self.status_label.set_label,"Chart not found")

                    break

    # Add resource to TreeView

    def add_res_view(self):

        # Clear liststore

        self.res_liststore.clear()

        # Start adding resources

        x = 0

        while x < len(self.resources_list):

            self.res_liststore.append([x, self.resources_list[x]])

            x = x + 1

    # On button click

    def get_charts(self,widget=None):

        # Thread init

        GLib.threads_init()

        self.status_label.set_label("Downloading...")

        # Start Thread

        _thread.start_new_thread(self.get_chart,())

    # Add new resource

    def add_res(self,widget=None):

        # Get resource

        res = self.res_entry.get_text()

        try:

            # Make order integer

            order = int(self.order_entry.get_text())

        except:

            order = None

        # If order isn't integer

        if order == None:

            self.res_stat_label.set_label("Please enter a number in order filed")

        else:

            # Add resource to resources list

            self.resources_list.insert(order,res)

            self.add_res_view()

            self.res_win.hide()

    # Remove a resource

    def rem_res(self,widget=None):

        # Get selection class

        select = self.treeview.get_selection()

        # Get selected value from selection class

        model, treeiter = select.get_selected()

        if treeiter is not None:

            # Remove resource from resources list

            self.resources_list.pop(model[treeiter][0])

            self.add_res_view()

            print("Resource removed")

        else:

            self.stat_label.set_label("Please select a resource")

    # Read config

    def read_config(self):

        self.main_win.show_all()

        config = configparser.RawConfigParser()

        config.read("config.cfg")

        config1 = config.read("config.cfg")

        # If no config file

        if config1 == []:

            self.add_res_view()

        else:

            # Get config data

            self.dest = config.get("Settings","Path")

            # If no resource list

            if ast.literal_eval(config.get("Settings","ResourcesList")) == []:

                # Use the default list

                self.add_res_view()

            else:

                # Get the resource list from config file

                self.resources_list = ast.literal_eval(config.get("Settings","ResourcesList"))

                try:

                    # Update Airac to fltplan server URL

                    a = self.resources_list.index("http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

                    # Remove the old one

                    self.resources_list.pop(a)

                    # Add new Airac

                    self.resources_list.insert(a,"http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

                except:

                    pass

                self.add_res_view()

            # Set open PDF

            self.open_check.set_active(ast.literal_eval(config.get("Settings","OpenPDF")))

        print("Config Read")

    # Write Config

    def write_config(self,widget=None):

        config = configparser.RawConfigParser()

        config.add_section('Settings')

        config.set("Settings", "Path", self.des_folder.get_uri())

        config.set("Settings", "ResourcesList", self.resources_list)

        config.set("Settings","OpenPDF",self.open_check.get_active())

        with open('config.cfg', 'wt') as configfile:

            config.write(configfile)

        print("Config Written")

    # Open settings window

    def show_settings(self,widget=None):

        self.settings_win.show_all()

    def show_res_win(self,widget=None):

        self.res_win.run()

        # If no hide_on_delete, the windows can't shown again

        self.res_win.hide_on_delete()

    # Set about dialog

    def about_dialog(self,widget=None):

        self.aboutdialog.run()

        self.aboutdialog.hide_on_delete()

    def hide_settings(self,widget=None,data=None):

        self.settings_win.hide_on_delete()

        # the windows can't shown again if no return True

        return True

    # End the program

    def quit(self,widget=None):

        self.write_config()

        Gtk.main_quit()
		
def main():

    builder.connect_signals(ChartFinder())

    Gtk.main()

main()