from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QAction, QLineEdit,
                             QPushButton, QMessageBox, QSystemTrayIcon, QProgressDialog)
import sys
import os
import SettingsWindow
import ConfigEditor
import Downloader

about = '''
Charts Finder <br>
Get charts for your flight! <br> <br>

Version: 1.1 <br>
Build date: May 2018 <br>
Check for updates here: <a href='https://bit.ly/2GA0vdo'>https://bit.ly/2GA0vdo</a> <br> <br>

Copyright © Abdullah Radwan <br>
Contact: <a href='mailto:abbodmar@gmail.com?subject=Charts%20Finder'>abbodmar@gmail.com</a>
'''


class ChartsFinder(QMainWindow):

    def __init__(self):

        # Call super init
        super().__init__()

        # Set icon path by getting current path with icon.svg
        icon = QIcon(os.path.join(os.path.abspath(os.path.split(sys.argv[0])[0]), "icon.svg"))

        self.system = sys.platform

        # Set system tray, used to show notifications
        self.system_tray = QSystemTrayIcon(icon)

        self.system_tray.show()

        # Set window title
        self.setWindowTitle("Charts Finder")

        # Set window flags to disable minimaize button
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Set window icon
        self.setWindowIcon(QIcon(icon))

        # Make instance of settings window
        self.settings = SettingsWindow.SettingsWindow(self.system, icon)

        # Call set menu
        self.set_menu()

        # Set main layout
        main_layout = QVBoxLayout(self)

        # Set application name label
        app_label = QLabel("Charts Finder", self)

        # Set alignment to center and top
        app_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Add it to main layout
        main_layout.addWidget(app_label)

        # Set ICAO label and line edit box
        enter_layout = QHBoxLayout(self)

        # Set ICAO label
        enter_label = QLabel("Enter ICAO codes:", self)

        # Add it to enter layout
        enter_layout.addWidget(enter_label)

        # Set ICAO line edit
        self.icao_edit = QLineEdit(self)

        # Set hint
        self.icao_edit.setPlaceholderText("Separate with space")

        # If 'Enter' key pressed, connect to get charts
        self.icao_edit.returnPressed.connect(self.get_charts)

        # Add it to enter layout
        enter_layout.addWidget(self.icao_edit)

        # Add enter layout to main_layout
        main_layout.addLayout(enter_layout)

        # Set get charts button
        self.get_button = QPushButton("Get charts", self)

        # Connect on click to get charts
        self.get_button.clicked.connect(self.get_charts)

        # Add it to main layout
        main_layout.addWidget(self.get_button)

        # Set status bar
        self.status_bar = self.statusBar()

        # Add it to main layout
        main_layout.addWidget(self.status_bar)

        # Set main widget
        widget = QWidget(self)

        # Set widget layout
        widget.setLayout(main_layout)

        # Set view to main widget
        self.setCentralWidget(widget)

        # Set progress dialog
        self.progress_dialog = QProgressDialog(self)

        # Connect cancel event to cancel method
        self.progress_dialog.canceled.connect(self.cancel_download)

        # Reset it to hide it (.hide() doesn't work)
        self.progress_dialog.reset()

    # If user closes the window
    def closeEvent(self, *args, **kwargs):

        # Call cancel download if there is any download
        self.cancel_download()

        # Call write config
        ConfigEditor.ConfigEditor(self.system).write_config(self.settings.dest_folder, self.settings.resources_list,
                                                            self.settings.open_file, self.settings.view_notify)

        # Hide system tray icon
        self.system_tray.hide()

    # Set menu bar
    def set_menu(self):

        # Get window menu bar
        menu = self.menuBar()

        # Set settings action
        settings_action = QAction("Settings", self)

        # On click, with execute the settings window (run it in main thread)
        settings_action.triggered.connect(self.settings.exec)

        # Add action to menu bar
        menu.addAction(settings_action)

        # Set about action
        about_action = QAction("About", self)

        # On click, call show about method
        about_action.triggered.connect(self.show_about)

        # Add action to menu bar
        menu.addAction(about_action)

    # Get charts
    def get_charts(self):

        # Make instance of downloader
        self.downloader = Downloader.Downloader(self.system, self.settings.resources_list,
                                                self.settings.dest_folder,  self.progress_dialog, self.status_bar,
                                                self.icao_edit.text().upper().split(), self.settings.view_notify,
                                                self.settings.open_file, self.system_tray)

        # Set downloader thread
        self.downloader_thread = QThread(self)

        # On thread start will execute download method
        self.downloader_thread.started.connect(self.downloader.download)

        # Move downloader to thread
        self.downloader.moveToThread(self.downloader_thread)

        # Connect PyQt5 slot and signals
        self.downloader.start_download_process.connect(self.start_download_process)

        self.downloader.show_dialog.connect(self.show_dialog)

        self.downloader.set_progress.connect(self.set_progress)

        self.downloader.reset_dialog.connect(self.progress_dialog.reset)

        self.downloader.finish_download_process.connect(self.finish_download_process)

        # Start thread
        self.downloader_thread.start()

    # Set progress, called from downloader thread
    def set_progress(self, progress): self.progress_dialog.setValue(progress)

    # Start the whole download process
    def start_download_process(self):

        # Disable the line edit and 'Get charts' button
        self.icao_edit.setEnabled(False)

        self.get_button.setEnabled(False)

    # Show the progress dialog
    def show_dialog(self): self.progress_dialog.setVisible(True)

    # Finish the whole download process
    def finish_download_process(self):

        # Reset progress dialog
        self.progress_dialog.reset()

        # Enable line edit and 'Get charts' button
        self.icao_edit.setEnabled(True)

        self.get_button.setEnabled(True)

    # Cancel download
    def cancel_download(self):

        # Try and except because it used by close event
        try:

            # Reset progress dialog
            self.progress_dialog.reset()

            # Cancel downloader
            self.downloader.cancel = True

        except: pass

    # Show about dialog
    def show_about(self): QMessageBox().about(self, "About Charts Finder", about)


# To make errors appear in IDEA
def except_hook(cls, exception, traceback): sys.__excepthook__(cls, exception, traceback)

# Connect error to error function
sys.excepthook = except_hook

# Set application
app = QApplication(sys.argv)

# Make instance
charts_finder = ChartsFinder()

# Show window
charts_finder.show()

# Execute application
sys.exit(app.exec())