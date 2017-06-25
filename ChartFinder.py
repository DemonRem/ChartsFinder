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

import requests

from multiprocessing import Queue

# Import Glade File

builder = Gtk.Builder()

builder.add_from_file("ChartFinder.glade")

# Main class

class ChartFinder:

    # Initialization

    def __init__(self):

        # Set main objects

        self.icao_code = builder.get_object("icao_code")

        self.aboutdialog = builder.get_object("aboutdialog1")

        self.status_label = builder.get_object("status_label")

        self.main_win = builder.get_object("window1")

        self.main_win.show_all()

    # Get Chart

    def get_chart(self,widget=None):

        icao = self.icao_code.get_text()

        try:

            response = requests.get("http://vau.aero/navdb/chart/{0}.pdf".format(icao))

            response.raise_for_status()

            with open("{0}.pdf".format(icao), 'wb') as f:

                f.write(response.content)

            self.status_label.set_label("Chart Downloaded")

        except:

            try:

             response = requests.get("ottomanva.com/lib/charts/{0}.pdf".format(icao))

             response.raise_for_status()

             with open("{0}.pdf".format(icao), 'wb') as f:

                f.write(response.content)

             self.status_label.set_label("Chart Downloaded")

            except:

                try:

                    response = requests.get("https://yinlei.org/x-plane10/jep/{0}.pdf".format(icao))

                    response.raise_for_status()

                    with open("{0}.pdf".format(icao), 'wb') as f:

                        f.write(response.content)

                    self.status_label.set_label("Chart Downloaded")

                except:

                    try:

                        response = requests.get("www.fly-sea.com/charts/{0}.pdf".format(icao))

                        response.raise_for_status()

                        with open("{0}.pdf".format(icao), "wb") as f:

                            f.write(response.content)

                        self.status_label.set_label("Chart Downloaded")

                    except:

                        try:

                            response = requests.get("www.uvairlines.com/admin/resources/charts/{0}.pdf".format(icao))

                            response.raise_for_status()

                            with open("{0}.pdf".format(icao), "wb") as f:

                                f.write(response.content)

                            self.status_label.set_label("Chart Downloaded")

                        except:

                            self.status_label.set_label("Chart not found")

    # Set about dialog

    def about_dialog(self,widget=None):

        self.aboutdialog.run()

        self.aboutdialog.hide_on_delete()

    def quit(self,widget=None):

        Gtk.main_quit()
		
def main():
	builder.connect_signals(ChartFinder())
	Gtk.main()

main()