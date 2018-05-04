
# -*- coding: utf-8 -*-

'''
--------------------- Copyright Block ----------------------
Charts Finder Program (Version 1.0.5a)
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

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GObject, GLib

from bs4 import BeautifulSoup

from threading import Thread

import requests, os, configparser, ast, shutil, time

# Import Glade File

builder = Gtk.Builder()

builder.add_from_file("ChartsFinder.glade")

# Main class

class ChartsFinder:

    # Initialization

    def __init__(self):

        # Set default value

        self.airac = time.strftime("%y%m", time.gmtime())

        self.resources_list = [["http://www.armats.com/arm/aviation/products/eAIP/pdf/UD-AD-2.{0}-en-GB.pdf","Normal"],["http://www.sia-enna.dz/PDF/AIP/AD/AD2/{0}/","Folder"],
                               ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac, "Normal"],["http://vau.aero/navdb/chart/{0}.pdf","Normal"],
                               ["http://ottomanva.com/lib/charts/{0}.pdf","Normal"],["https://yinlei.org/x-plane10/jep/{0}.pdf","Normal"],["http://sa-ivao.net/charts_file/CHART-{0}.PDF","Normal"],
                               ["http://www.fly-sea.com/charts/{0}.pdf","Normal"],["http://uvairlines.com/admin/resources/charts/{0}.pdf","Normal"],["https://www.virtualairlines.eu/charts/{0}.pdf","Normal"]
                              ]

        self.destf = None

        # Import main objects

        self.settings_win = builder.get_object("settings_win")

        self.icao_code = builder.get_object("icao_code")

        self.aboutdialog = builder.get_object("aboutdialog")

        self.status_label = builder.get_object("status_label")

        self.stat_label = builder.get_object("stat_label")

        self.des_folder = builder.get_object("dest_folder")

        self.open_check = builder.get_object("open_chart_check")

        self.notify_check = builder.get_object("view_notify_check")

        self.res_liststore = builder.get_object("res_list")

        self.res_treeview = builder.get_object("treeview1")

        self.res_win = builder.get_object("add_res_win")

        self.res_entry = builder.get_object("res_entry")

        self.order_entry = builder.get_object("order_entry")

        self.res_combo = builder.get_object("res_combo")

        self.res_stat_label = builder.get_object("add_res_stat_label")

        self.main_win = builder.get_object("main_win")

        # Set main objects

        self.read_config()

    # Get Chart

    def get_chart(self):

        # Get ICAO code

        self.icao = self.icao_code.get_text().upper().split()

        if self.icao == []:

            GLib.idle_add(self.status_label.set_label, "Please enter an ICAO code")

        else:

            # x is resources number, z is airports number

            x = 0

            z = 0

            # This loop will run the inner loop 1 per airport

            while z < len(self.icao):

                GLib.idle_add(self.status_label.set_label,"Downloading %s Charts..." % self.icao[z])

                if self.view_notify is True:

                    Thread(target=os.system, args=("notify-send ChartsFinder Downloading %s charts..." % self.icao[z],)).start()

                while True:

                    if self.destf is None:

                        path = os.getcwd() + "\\Charts\\" + self.icao[z]

                        if os.path.exists(path):

                            GLib.idle_add(self.status_label.set_label, "%s charts already exists" % self.icao[z])

                            if self.view_notify is True:

                                Thread(target=os.system, args=("notify-send ChartsFinder %s charts already exists" % self.icao[z],)).start()

                            break

                        else:

                            path = os.getcwd() + "\\Charts\\" + self.icao[z] + ".pdf"

                            if os.path.exists(path):

                                GLib.idle_add(self.status_label.set_label, "%s charts already exists" % self.icao[z])

                                if self.view_notify is True:

                                    Thread(target=os.system, args=("notify-send ChartsFinder %s charts already exists" % self.icao[z],)).start()

                                break

                    else:

                        path = self.destf + "/" + self.icao[z]

                        if os.path.exists(path):

                            GLib.idle_add(self.status_label.set_label, "%s charts already exists" % self.icao[z])

                            if self.view_notify is True:

                                Thread(target=os.system, args=("notify-send ChartsFinder %s charts already exists" % self.icao[z],)).start()

                            break

                        else:

                            path = self.destf + "/" + self.icao[z] + ".pdf"

                            if os.path.exists(path):

                                GLib.idle_add(self.status_label.set_label, "%s charts already exists" % self.icao[z])

                                if self.view_notify is True:

                                    Thread(target=os.system, args=("notify-send ChartsFinder %s charts already exists" % self.icao[z],)).start()

                                break

                    try:

                        # Check if chart exist in resource

                        response = requests.get((self.resources_list[x][0].format(self.icao[z])))

                    except:

                        # If chart isn't exist

                        GLib.idle_add(self.status_label.set_label,"%s charts not found" % self.icao[z])

                        # Run notify

                        if self.view_notify is True:

                            Thread(target=os.system, args=("notify-send ChartsFinder %s charts not found" % self.icao[z],)).start()

                        break

                    # If chart exists on the server

                    if response.status_code == requests.codes.ok:

                        # If resource is folder

                        if self.resources_list[x][1] == "Folder":

                            if self.destf == "folder":

                                path = os.getcwd() + "\\Charts\\" + self.icao[z]

                                os.mkdir(path)

                            else:

                                path = self.destf + "/" + self.icao[z]

                                os.mkdir(path)

                            sopa = BeautifulSoup(response.content, "html.parser")

                            # Download multiple charts

                            try:

                                # Set URL

                                self.url = self.resources_list[x][0].format(self.icao[z])

                                for link in sopa.find_all('a'):

                                    current_link = link.get('href')

                                    # Search for pdf files

                                    if current_link.endswith('pdf'):

                                        # Download it

                                        with open(current_link, 'wb') as f:

                                            f.write(requests.get(self.url.format(self.icao[z]) + current_link).content)

                                            f.close()

                                            shutil.move(current_link, path)


                                GLib.idle_add(self.status_label.set_label, "%s Charts Downloaded" % self.icao[z])

                                if self.view_notify == True:

                                    Thread(target=os.system,args=("notify-send ChartsFinder %s charts downloaded" % self.icao[z],)).start()

                            # If move fail

                            except:

                                GLib.idle_add(self.status_label.set_label, "Can't move %s charts" % self.icao[z])

                                if self.view_notify is True:

                                    Thread(target=os.system,args=("notify-send ChartsFinder Can't move %s charts" % self.icao[z],)).start()

                            break

                        # If resource is normal

                        elif self.resources_list[x][1] == "Normal":

                            # Write the chart to pdf file

                            with open("{0}.pdf".format(self.icao[z]), 'wb') as f:

                                f.write(response.content)

                                f.close()

                            # if no folder was selected, it will move to 'Charts' folder

                            if self.destf == 'folder':

                                try:

                                    shutil.move("{0}.pdf".format(self.icao[z]), "Charts/")

                                    GLib.idle_add(self.status_label.set_label, "%s charts downloaded" % self.icao[z])

                                    if self.view_notify is True:

                                        Thread(target=os.system, args=("notify-send ChartsFinder %s charts downloaded" % self.icao[z],)).start()

                                    # If user want to open chart

                                    if self.open_chart is True:

                                        Thread(target=os.startfile,args=("%s\\Charts\\%s.pdf" % (os.getcwd(),self.icao[z]),)).start()

                                except:

                                    GLib.idle_add(self.status_label.set_label,"Can't move %s charts" % self.icao[z])

                                    if self.view_notify is True:

                                        Thread(target=os.system, args=("notify-send ChartsFinder Can't move %s charts" % self.icao[z],)).start()

                                break

                            # If a folder has been selected

                            else:

                                try:

                                    # Trying to move chart

                                    shutil.move("{0}.pdf".format(self.icao[z]),self.destf)

                                    GLib.idle_add(self.status_label.set_label, "%s charts downloaded" % self.icao[z])

                                    if self.view_notify is True:

                                        Thread(target=os.system, args=("notify-send ChartsFinder %s charts downloaded" % self.icao[z],)).start()

                                    if self.open_chart is True:

                                        Thread(target=os.startfile,args=(self.destf + "/{0}.pdf".format(self.icao[z]),)).start()

                                except:

                                    GLib.idle_add(self.status_label.set_label,"Can't move %s charts" % self.icao[z])

                                    if self.view_notify is True:

                                        Thread(target=os.system, args=("notify-send ChartsFinder Can't move %s charts" % self.icao[z],)).start()

                                break

                    # If chart isn't exist on server

                    else:

                        # Trying with another resource

                        x += 1

                time.sleep(5)

                z += 1

    # Add resource to TreeView

    def add_res_view(self):

        # Clear liststore

        self.res_liststore.clear()

        # Start adding resources

        x = 0

        while x < len(self.resources_list):

            self.res_liststore.append([x, self.resources_list[x][0]])

            x = x + 1

    # On button click

    def get_charts(self,widget=None):

        # Thread init

        GLib.threads_init()

        self.view_notify = self.notify_check.get_active()

        self.open_chart = self.open_check.get_active()

        # Start Thread

        t = Thread(target=self.get_chart, args=())

        t.start()

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

            if self.res_combo.get_active_text() == "Folder":

                self.resources_list.insert(order,[res,"Folder"])

                self.add_res_view()

                self.stat_label.set_label("A folder resource was added")

            elif self.res_combo.get_active_text() == "Normal":

                self.resources_list.insert(order,[res,"Normal"])

                self.add_res_view()

                self.stat_label.set_label("A normal resource was added")

            else:

                self.res_stat_label.set_label("Please choose a type")

            self.res_win.hide()

    # Remove a resource

    def rem_res(self,widget=None):

        # Get selection class

        res_select = self.res_treeview.get_selection()

        # Get selected value from selection class

        model, treeiter = res_select.get_selected()

        if treeiter is not None:

            self.resources_list.pop(model[treeiter][0])

            self.add_res_view()

            self.stat_label.set_label("A resource was removed")

            print("Resource removed")

        else:

            self.stat_label.set_label("Please select a resource")

    def rest_res(self, widget=None):

        self.resources_list = [["http://www.armats.com/arm/aviation/products/eAIP/pdf/UD-AD-2.{0}-en-GB.pdf","Normal"],["http://www.sia-enna.dz/PDF/AIP/AD/AD2/{0}/","Folder"],
                               ["http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac, "Normal"],["http://vau.aero/navdb/chart/{0}.pdf","Normal"],
                               ["ottomanva.com/lib/charts/{0}.pdf","Normal"],["https://yinlei.org/x-plane10/jep/{0}.pdf","Normal"],["http://sa-ivao.net/charts_file/CHART-{0}.PDF","Normal"],
                               ["www.fly-sea.com/charts/{0}.pdf","Normal"],["www.uvairlines.com/admin/resources/charts/{0}.pdf","Normal"],["https://www.virtualairlines.eu/charts/{0}.pdf","Normal"]
                              ]

        self.add_res_view()

        self.stat_label.set_label("Resources Rested")

    # Move a res up

    def move_res_up(self,widget=None):

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

                self.stat_label.set_label("You can't up the first item")

            else:

                # Remove the resource

                self.resources_list.pop(order)

                # Insert new one with higher order

                self.resources_list.insert(order - 1,res)

                # Update view

                self.add_res_view()

                self.stat_label.set_label("A resource was moved up")


        else:

            self.stat_label.set_label("Please select a resource")

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

            if order + 1 == len(self.resources_list):

                self.stat_label.set_label("You can't down the last item")

            else:

                # Remove the resource

                self.resources_list.pop(order)

                # Insert new one with lower order

                self.resources_list.insert(order + 1, res)

                # Update view

                self.add_res_view()

                self.stat_label.set_label("A resource was moved down")


        else:

            self.stat_label.set_label("Please select a resource")


    # Read config

    def read_config(self):

        self.main_win.show_all()

        config = configparser.RawConfigParser()

        config1 = config.read("config.cfg")

        # If no config file

        if config1 == []:

            self.add_res_view()

        else:

            # Get config data

            # If self.dest = None

            try:

                self.destf = ast.literal_eval(config.get("Settings","Path"))[1:]

                self.destf = "folder"

            # else

            except:

                self.destf = config.get("Settings", "Path")

            self.notify_check.set_active(ast.literal_eval(config.get("Settings","ViewNotify")))

            # Get the resource list from config file

            self.resources_list = ast.literal_eval(config.get("Settings","ResourcesList"))

            try:

                # Get where is it

                g = 0

                while g < len(self.resources_list):

                    try:

                        a = self.resources_list[g].index("http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

                        b = g

                        break

                    except:

                        g += 1

                # Update Airac to fltplan server URL

                # Remove the old one

                self.resources_list.pop[b](0)

                # Add new Airac

                self.resources_list[b].insert(a,"http://imageserver.fltplan.com/merge/merge%s/{0}.pdf" % self.airac)

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

        config.set("Settings", "Path", self.destf)

        config.set("Settings", "ResourcesList", self.resources_list)

        config.set("Settings", "OpenPDF", self.open_check.get_active())

        config.set("Settings", "ViewNotify", self.notify_check.get_active())

        with open('config.cfg', 'wt') as configfile:

            config.write(configfile)

        print("Config Written")

    # Set path, will activated when open choose file dialog

    def set_path(self, widget=None):

        # If something is selected

        if self.des_folder.get_uri() is not None:

            self.destf = self.des_folder.get_uri()[8:]

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

        # the windows can't shown again if there's no return True

        return True

    # End the program

    def quit(self,widget=None):

        self.write_config()

        Gtk.main_quit()

builder.connect_signals(ChartsFinder())

Gtk.main()