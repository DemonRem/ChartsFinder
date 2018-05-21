from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog,\
    QTabWidget, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox
import time
import ConfigEditor
import AddResDialog


class SettingsWindow(QDialog):

    def __init__(self, system, icon):

        # Init super
        super().__init__()

        # Read config data
        config = ConfigEditor.ConfigEditor(system).read_config()

        # Set data from return values
        self.dest_folder = config[0]

        self.resources_list = config[1]

        self.open_file = config[2]

        self.view_notify = config[3]

        # Set window title
        self.setWindowTitle("Settings - Charts Finder")

        # Set flags to hide minimize button
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.icon = icon

        # Set icon
        self.setWindowIcon(self.icon)

        # Set main layout
        main_layout = QVBoxLayout(self)

        # Set tabs
        tabs = QTabWidget(self)

        # Set general tab
        self.gen_tab = QWidget(self)

        # Set resources tab
        self.res_tab = QWidget(self)

        # Add tabs
        tabs.addTab(self.gen_tab, "General")

        tabs.addTab(self.res_tab, "Resources")

        # Set tabs
        self.set_gen_tab()

        self.set_res_tab()

        main_layout.addWidget(tabs)

        self.setLayout(main_layout)

    def set_gen_tab(self):

        # Set general layout
        gen_layout = QVBoxLayout(self)

        # Set path layout
        path_layout = QHBoxLayout(self)

        # Set path label
        self.path_label = QLabel("Path: " + self.dest_folder, self)

        # Add it to path layout
        path_layout.addWidget(self.path_label)

        # Change path button
        path_button = QPushButton("Change path", self)

        # Connect on click to change path
        path_button.clicked.connect(self.change_path)

        # Add it to path layout
        path_layout.addWidget(path_button)

        # Add path layout to general layout
        gen_layout.addLayout(path_layout)

        # Set open file check
        open_file_check = QCheckBox("Open chart after download", self)

        # Toggle if open file is true
        if self.open_file: open_file_check.toggle()

        # Connect to toggled event
        open_file_check.toggled.connect(self.open_file_toggled)

        # Add it to general layout
        gen_layout.addWidget(open_file_check)

        # Set notify check
        notify_check = QCheckBox("Show notifications", self)

        # Toggle if view notify is true
        if self.view_notify: notify_check.toggle()

        # Connect on toggle
        notify_check.toggled.connect(self.notify_toggled)

        # Add it to general layout
        gen_layout.addWidget(notify_check)

        # Set tab layout to general layout
        self.gen_tab.setLayout(gen_layout)

    def set_res_tab(self):

        # Set resource layout
        res_layout = QVBoxLayout(self)

        # Set resources label
        res_label = QLabel("Resources", self)

        # Set alignments to top and center
        res_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Add it to resource layout
        res_layout.addWidget(res_label)

        # Set resources table
        self.res_table = QTableWidget(self)

        # Set column and names
        self.res_table.setColumnCount(2)

        self.res_table.setHorizontalHeaderLabels(["Type", "Resource"])

        # Call set resources table
        self.set_res_table()

        # Add it to resources layout
        res_layout.addWidget(self.res_table)

        # Set arrows layout
        arrows_layout = QHBoxLayout(self)

        # Set up button
        up_button = QPushButton("Up", self)

        # Connect it to move res up method
        up_button.clicked.connect(self.move_res_up)

        # Add it to arrows layout
        arrows_layout.addWidget(up_button)

        # Set down button
        down_button = QPushButton("Down", self)

        # Connect to move resource down method
        down_button.clicked.connect(self.move_res_down)

        # Add it to arrows layout
        arrows_layout.addWidget(down_button)

        # Add arrows layout to resources layout
        res_layout.addLayout(arrows_layout)

        # Set edit layout
        edit_layout = QHBoxLayout(self)

        # Set add button
        add_button = QPushButton("Add", self)

        # Set on click to add resource method
        add_button.clicked.connect(self.add_res)

        # Add it to edit layout
        edit_layout.addWidget(add_button)

        # Set remove button
        rem_button = QPushButton("Remove", self)

        # Connect on click to remove resource method
        rem_button.clicked.connect(self.rem_res)

        # Add it to edit layout
        edit_layout.addWidget(rem_button)

        # Add edit layout to resource layout
        res_layout.addLayout(edit_layout)

        # Set reset button
        reset_button = QPushButton("Reset resources", self)

        # Connect to reset resources method
        reset_button.clicked.connect(self.reset_res)

        # Add it to resource layout
        res_layout.addWidget(reset_button)

        # Set status label
        self.status_label = QLabel(self)

        # Add it to resource layout
        res_layout.addWidget(self.status_label)

        # Set tab layout to resources layout
        self.res_tab.setLayout(res_layout)

    # Change path
    def change_path(self):

        # Get path from file dialog
        path = str(QFileDialog.getExistingDirectory(self, "Select charts directory"))

        # If a path selected
        if not path == "":

            self.dest_folder = path

            self.path_label.setText("Path: " + self.dest_folder)

    def open_file_toggled(self, stat): self.open_file = stat

    def notify_toggled(self, stat): self.view_notify = stat

    # Set resources table
    def set_res_table(self):

        # Set rows to 0, to remove all data
        self.res_table.setRowCount(0)

        # Set rows to resources list items
        self.res_table.setRowCount(len(self.resources_list))

        resource = 0

        while resource < len(self.resources_list):

            # Set type
            self.res_table.setItem(resource, 0, QTableWidgetItem(self.resources_list[resource][1]))

            # Set resources
            self.res_table.setItem(resource, 1, QTableWidgetItem(self.resources_list[resource][0]))

            resource += 1

        # Resize columns to content
        self.res_table.resizeColumnsToContents()

    # Move resource up
    def move_res_up(self):

        # Get order from current row
        order = self.res_table.currentRow()

        # If item isn't the first item
        if not order == 0:

            # Get resource
            resource = self.resources_list[order]

            # Remove it from list
            self.resources_list.pop(order)

            # Add it with lower order (Increase prointy)
            self.resources_list.insert(order - 1, resource)

            # Call set resources table
            self.set_res_table()

            # Set status label
            self.status_label.setText("Resource '%s' was moved up" % resource[0])

        # Set error message
        else: self.status_label.setText("You can't move the first item up")

    # Move resource down
    def move_res_down(self):

        # Get order from current row
        order = self.res_table.currentRow()

        # If order isn't the last item
        if not order == len(self.resources_list) - 1:

            # Get resource from order
            resource = self.resources_list[order]

            # Remove it
            self.resources_list.pop(order)

            # Add it with higher order (Lower prointy)
            self.resources_list.insert(order + 1, resource)

            # Set resources table
            self.set_res_table()

            # Set status text
            self.status_label.setText("Resource '%s' was moved down" % resource[0])

        else: self.status_label.setText("You can't move the last item down")

    def add_res(self):

        self.addres_dialog = AddResDialog.AddResDialog(len(self.resources_list), self.icon)

        self.addres_dialog.exec()

        if self.addres_dialog.ok:

            self.resources_list.insert(self.addres_dialog.order, [self.addres_dialog.resource, self.addres_dialog.type])

            self.set_res_table()

            self.status_label.setText("Resource '%s' was added" % self.addres_dialog.resource)

    # Remove resource
    def rem_res(self):

        try:

            # Get order from selected row
            order = self.res_table.currentRow()

            # Get current resource
            resource = self.resources_list[order][0]

            # Remove resource
            self.resources_list.pop(order)

            # Set table
            self.set_res_table()

            # Set status label
            self.status_label.setText("Resource '%s' was removed" % resource)

        except: self.status_label.setText("Nothing to remove")

    # Reset resources
    def reset_res(self):

        # Open question dialog
        response = QMessageBox().question(self, "Reset resources", "Are you sure you want to reset resources?",
                                          QMessageBox.Yes, QMessageBox.No)

        # If yes
        if response == QMessageBox.Yes:

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

            self.set_res_table()

            self.status_label.setText("Resources was reset")
