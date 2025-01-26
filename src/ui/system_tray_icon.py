from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
import os
import ctypes

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, app, parent=None):
        super().__init__(QIcon(os.path.join('assets', 'ww-logo.png')), parent)
        self.app = app
        self.setToolTip('Whisper Writer')

        tray_menu = QMenu(parent)

        settings_action = QAction('Open Settings', self.app)
        settings_action.triggered.connect(self.app.settings_window.show)
        tray_menu.addAction(settings_action)

        show_terminal_action = QAction('Show Terminal', self.app)
        show_terminal_action.triggered.connect(self.show_terminal)
        tray_menu.addAction(show_terminal_action)

        hide_terminal_action = QAction('Hide Terminal', self.app)
        hide_terminal_action.triggered.connect(self.hide_terminal)
        tray_menu.addAction(hide_terminal_action)

        exit_action = QAction('Exit', self.app)
        exit_action.triggered.connect(self.app.exit_app)
        tray_menu.addAction(exit_action)

        self.setContextMenu(tray_menu)
        self.show()

    def hide_terminal(self):
        """
        Hide the terminal window.
        """
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  # 0 is SW_HIDE

    def show_terminal(self):
        """
        Show the terminal window.
        """
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)  # 5 is SW_SHOW
