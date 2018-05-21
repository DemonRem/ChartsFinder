from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QComboBox, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QPushButton


class AddResDialog(QDialog):

    def __init__(self, res_len, icon):

        # Call super init
        super().__init__()

        # Set title
        self.setWindowTitle("Add resource - Settings")

        # Set flags to disable minimize button
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Set icon
        self.setWindowIcon(icon)

        self.ok = False

        # Set main layout
        main_layout = QVBoxLayout(self)

        # Set resource layout
        res_layout = QHBoxLayout(self)

        # Set resource label
        res_label = QLabel("Enter resource:", self)

        # Add it to resource layout
        res_layout.addWidget(res_label)

        # Set resource line edit
        self.res_edit = QLineEdit(self)

        # Add it to resource layout
        res_layout.addWidget(self.res_edit)

        # Add resource layout to main layout
        main_layout.addLayout(res_layout)

        # Set order layout
        order_layout = QHBoxLayout(self)

        # Set order label
        order_label = QLabel("Enter order:", self)

        # Add it to order layout
        order_layout.addWidget(order_label)

        # Set order spin
        self.order_spin = QSpinBox(self)

        # Set minimum to 1
        self.order_spin.setMinimum(1)

        # Set maximum to resource list items + 1
        self.order_spin.setMaximum(res_len + 1)

        # Add it to order layout
        order_layout.addWidget(self.order_spin)

        # Add order layout to main layout
        main_layout.addLayout(order_layout)

        # Set type layout
        type_layout = QHBoxLayout(self)

        # Add type label
        type_label = QLabel("Choose type:", self)

        # Add it to type layout
        type_layout.addWidget(type_label)

        # Set type combo
        self.type_combo = QComboBox(self)

        # Add types
        self.type_combo.addItem("Normal")

        self.type_combo.addItem("Folder")

        # Add it to type layout
        type_layout.addWidget(self.type_combo)

        # Add type layout to main layout
        main_layout.addLayout(type_layout)

        # Set add button
        add_button = QPushButton("Add", self)

        # Connect to add resource
        add_button.clicked.connect(self.add_res)

        # Add it to main layout
        main_layout.addWidget(add_button)

        self.status_label = QLabel(self)

        main_layout.addWidget(self.status_label)

        # Set layout to main layout
        self.setLayout(main_layout)

    # Add resource
    def add_res(self):

        # Get resource
        resource = str(self.res_edit.text())

        # If resource is empty
        if resource == "":

            self.status_label.setText("Please enter a resource")

            return

        # If http:// or https:// isn't included
        elif not resource[:8] == "https://":

            if not resource[:7] == "http://":

                self.status_label.setText("You must include 'http://' or 'https://'")

                return

        self.resource = resource

        self.ok = True

        # Get order
        self.order = int(self.order_spin.value()) - 1

        # Get type
        self.type = self.type_combo.currentText()

        # Hide window
        self.deleteLater()