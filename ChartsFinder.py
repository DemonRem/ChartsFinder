#!/usr/bin/python3
# Start file on Linux and Mac

# -*- coding: utf-8 -*-

# --------------------- Copyright Block ----------------------
# Charts Finder Program (Version 1.0.6a)
# Copyright (C) 2018 Abdullah Radwan
# License: GNU GPL v3.0
# TERMS OF USE:
#	Permission is granted to use this code, with or
#	without modification, in any website or application
#	provided that credit is given to the original work
#	with a link back to Abdullah Radwan.
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY.
# PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK
# ------------------------------------------------------------

# Import Main libraries
from threading import Thread
import gi
import time
import sys
import Downloader
import ConfigEditor

# Specific a GTK version and import it
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

# Import Glade File
builder = Gtk.Builder()

builder.add_from_file("ChartsFinder.glade")


class ChartsFinder:

    # Initialization
    def __init__(self):

        # Import main objects
        self.settings_win = builder.get_object("settings_win")

        self.icao_entry = builder.get_object("icao_code")

        self.about_dialog = builder.get_object("about_dialog")

        self.status_label = builder.get_object("status_label")

        self.stat_label = builder.get_object("stat_label")

        self.folder_chooser = builder.get_object("dest_folder")

        self.open_chart_check = builder.get_object("open_chart_check")

        self.notify_check = builder.get_object("view_notify_check")

        self.res_liststore = builder.get_object("res_list")

        self.res_treeview = builder.get_object("res_treeview")

        self.res_win = builder.get_object("add_res_win")

        self.res_entry = builder.get_object("res_entry")

        self.order_entry = builder.get_object("order_entry")

        self.res_combo = builder.get_object("res_combo")

        self.res_stat_label = builder.get_object("add_res_stat_label")

        self.get_button = builder.get_object("get_chart")

        self.path_label = builder.get_object("path_label")

        self.main_win = builder.get_object("main_win")

        # Set main objects
        self.config = ConfigEditor.ConfigEditor(self.notify_check, self.open_chart_check)

        # Read config data
        config = self.config.read_config()

        # Set data from return values
        self.dest_folder = config[0]

        self.resources_list = config[1]

        # Show main windows
        self.main_win.show_all()

    def set_res_view(self):

        # Clear liststore
        self.res_liststore.clear()

        # Start adding resources
        x = 0

        while x < len(self.resources_list):

            self.res_liststore.append([x, self.resources_list[x][0]])

            x += 1

    # On button click
    def get_charts(self, widget=None):

        # Thread init
        GLib.threads_init()

        # Start Thread
        Thread(target=Downloader.Downloader(self.resources_list, self.dest_folder, self.status_label, self.get_button,
                                            self.icao_entry, self.notify_check, self.open_chart_check).download).start()

    # Move a resource up
    def move_res_up(self, widget=None):

        # Get selection class
        res_select = self.res_treeview.get_selection()

        # Get selected value from selection class
        model, treeiter = res_select.get_selected()

        if treeiter is not None:

            # Get order
            order = model[treeiter][0]

            # Get specific res list in resource list
            res = self.resources_list[order]

            # If order is the first (0)
            if order is 0:

                self.stat_label.set_label("You can't move the first item up")

            else:

                # Remove the resource
                self.resources_list.pop(order)

                # Insert new one with higher order
                self.resources_list.insert(order - 1, res)

                # Update view
                self.set_res_view()

                self.stat_label.set_label("A resource was moved up")

        else: self.stat_label.set_label("Please select a resource")

    # Move a resource down
    def move_res_down(self, widget=None):

        # Get selection class
        res_select = self.res_treeview.get_selection()

        # Get selected value from selection class
        model, treeiter = res_select.get_selected()

        if treeiter is not None:

            # Get order
            order = model[treeiter][0]

            # Get specific res list in resource list
            res = self.resources_list[order]

            # If order is the last
            if order + 1 == len(self.resources_list): self.stat_label.set_label("You can't move the last item down")

            else:

                # Remove the resource
                self.resources_list.pop(order)

                # Insert new one with lower order
                self.resources_list.insert(order + 1, res)

                # Update view
                self.set_res_view()

                self.stat_label.set_label("A resource was moved down")

        else: self.stat_label.set_label("Please select a resource")

    # Add new resource
    def add_res(self, widget=None):

        # Get resource
        res = self.res_entry.get_text()

        # Make order integer
        try: order = int(self.order_entry.get_text())

        # If order isn't integer
        except: self.res_stat_label.set_label("Please enter a number in order filed"); return

        # Add resource to resources list
        if self.res_combo.get_active_text() == "Folder":

            self.resources_list.insert(order, [res, "Folder"])

            self.set_res_view()

            self.stat_label.set_label("A folder resource was added")

        elif self.res_combo.get_active_text() == "Normal":

            self.resources_list.insert(order, [res, "Normal"])

            self.set_res_view()

            self.stat_label.set_label("A normal resource was added")

        else: self.res_stat_label.set_label("Please choose a type")

        self.res_win.hide()

    # Remove a resource
    def rem_res(self, widget=None):

        # Get selection class
        res_select = self.res_treeview.get_selection()

        # Get selected value from selection class
        model, treeiter = res_select.get_selected()

        if treeiter is not None:

            # Remove from resource list
            self.resources_list.pop(model[treeiter][0])

            # Set resource view
            self.set_res_view()

            self.stat_label.set_label("A resource was removed")

        else: self.stat_label.set_label("Please select a resource")

    # Reset resources
    def rest_res(self, widget=None):

        self.resources_list = [["http://www.armats.com/arm/aviation/products/eAIP/pdf/UD-AD-2.{0}-en-GB.pdf", "Normal"],
                               ["http://www.sia-enna.dz/PDF/AIP/AD/AD2/{0}/", "Folder"],
                               ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % time.strftime("%y%m",time.gmtime()),"Normal"],
                               ["http://vau.aero/navdb/chart/{0}.pdf", "Normal"],
                               ["http://ottomanva.com/lib/charts/{0}.pdf", "Normal"],
                               ["https://yinlei.org/x-plane10/jep/{0}.pdf", "Normal"],
                               ["http://sa-ivao.net/charts_file/{0}.pdf", "Normal"],
                               ["http://www.fly-sea.com/charts/{0}.pdf", "Normal"],
                               ["http://www.europlanet.de/vaFsP/charts/{0}.pdf", "Normal"],
                               ["http://uvairlines.com/admin/resources/charts/{0}.pdf", "Normal"],
                               ["https://www.virtualairlines.eu/charts/{0}.pdf", "Normal"]
                               ]

        self.set_res_view()

        self.stat_label.set_label("Resources was reset")

    # Set path, will activated when open choose file dialog
    def set_path(self, widget=None):

        # If something is selected
        if self.folder_chooser.get_uri() is not None:

            # If system is Windows, we will start from 8 to hide root slash
            if sys.platform == "win32": start = 8

            # Else, start from 7 to show root slash
            else: start = 7

            self.dest_folder = self.folder_chooser.get_uri()[start:]

            self.path_label.set_label("   Path: " + self.dest_folder + " ")

    # Open settings window
    def show_settings(self, widget=None):

        self.set_res_view()

        self.path_label.set_label("   Path: " + self.dest_folder + " ")

        self.settings_win.show_all()

    # Show add resource dialog
    def show_res_win(self, widget=None):

        self.res_win.run()

        self.res_win.hide_on_delete()
        # If no hide_on_delete, the windows can't shown again

    # Set about dialog
    def show_about_dialog(self, widget=None):

        self.about_dialog.run()

        self.about_dialog.hide_on_delete()

    # Hide settings window
    def hide_settings(self, widget=None, data=None):

        self.settings_win.hide_on_delete()

        return True
        # the windows can't shown again if there's no return True

    # End the program
    def quit(self, widget=None):

        self.config.write_config(self.dest_folder, self.resources_list)

        Gtk.main_quit()


# Connect class to builder
builder.connect_signals(ChartsFinder())

# Start the program
Gtk.main()
