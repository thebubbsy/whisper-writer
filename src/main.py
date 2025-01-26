import os
import sys
from audioplayer import AudioPlayer # type: ignore
from PyQt5.QtCore import QObject, QProcess, pyqtSlot, pyqtSignal, QMetaObject, Qt, Q_ARG # type: ignore
from PyQt5.QtGui import QIcon                      # type: ignore
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox  # type: ignore

from key_listener import KeyListener
from result_thread import ResultThread
from ui.settings_window import SettingsWindow
from ui.status_window import StatusWindow
from ui.system_tray_icon import SystemTrayIcon
from ui.transparent_window import TransparentWindow
from transcription import create_local_model
from input_simulation import InputSimulator
from utils import ConfigManager

class WhisperWriterApp(QObject):
    statusSignal = pyqtSignal(str)
    resultSignal = pyqtSignal(str)

    def __init__(self):
        """
        Initialize the application, opening settings window if no configuration file is found.
        """
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(os.path.join('assets', 'ww-logo.png')))

        ConfigManager.initialize()

        self.settings_window = SettingsWindow()
        self.settings_window.settings_closed.connect(self.on_settings_closed)
        self.settings_window.settings_saved.connect(self.restart_app)

        self.transparent_window = TransparentWindow()

        self.type_result = False # Type the result out when it is received.
        self.use_clipboard = False # Copy the result to the clipboard when it is received.

        if ConfigManager.config_file_exists():
            self.initialize_components()
        else:
            print('No valid configuration file found. Opening settings window...')
            self.settings_window.show()

        self.hide_terminal()

    def initialize_components(self):
        """
        Initialize the components of the application.
        """
        self.input_simulator = InputSimulator(self.transparent_window)

        self.key_listener = KeyListener()
        self.key_listener.add_callback("on_activate_typing_and_clipboard", lambda: self.on_activation(type_result=True, use_clipboard=True))
        self.key_listener.add_callback("on_paste", self.transparent_window.reset_window)

        self.local_model = create_local_model()

        self.result_thread = None

        if not ConfigManager.get_config_value('misc', 'hide_status_window'):
            self.status_window = StatusWindow()

        self.create_tray_icon()
        self.start_listening()

    def create_tray_icon(self):
        """
        Create the system tray icon and its context menu.
        """
        self.tray_icon = SystemTrayIcon(self)

    def hide_terminal(self):
        """
        Hide the terminal window.
        """
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  # 0 is SW_HIDE

    def show_terminal(self):
        """
        Show the terminal window.
        """
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)  # 5 is SW_SHOW

    def start_listening(self):
        """
        Start listening for the activation key.
        """
        self.key_listener.start()

    def cleanup(self):
        if self.key_listener:
            self.key_listener.stop()
        if self.input_simulator:
            self.input_simulator.stop()
        if self.result_thread and self.result_thread.isRunning():
            self.result_thread.stop()

    def exit_app(self):
        """
        Exit the application.
        """
        self.cleanup()
        QApplication.quit()

    def restart_app(self):
        """Restart the application to apply the new settings."""
        self.cleanup()
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def on_settings_closed(self):
        """
        If settings is closed without saving on first run, initialize the components with default values.
        """
        if not os.path.exists(os.path.join('src', 'config.yaml')):
            QMessageBox.information(
                self.settings_window,
                'Using Default Values',
                'Settings closed without saving. Default values are being used.'
            )
            self.initialize_components()

    def on_activation(self, type_result, use_clipboard):
        """
        Called when the activation key combination is pressed.
        """
        self.type_result = type_result
        self.use_clipboard = use_clipboard

        # Show the transparent window immediately
        QMetaObject.invokeMethod(self.transparent_window, "display_text", Qt.QueuedConnection, Q_ARG(str, ""))

        if self.result_thread and self.result_thread.isRunning():
            self.result_thread.stop_recording()
            return

        self.start_result_thread()

    def start_result_thread(self):
        """
        Start the result thread to record audio and transcribe it.
        """
        if self.result_thread and self.result_thread.isRunning():
            return

        self.result_thread = ResultThread(self.local_model)
        self.result_thread.statusSignal.connect(self.handle_status_signal)
        self.result_thread.resultSignal.connect(self.handle_result_signal)
        self.result_thread.start()

    @pyqtSlot(str)
    def handle_status_signal(self, status):
        """
        Handle status signals from the result thread.
        """
        if hasattr(self, 'status_window') and not ConfigManager.get_config_value('misc', 'hide_status_window'):
            self.status_window.updateStatus(status)

    @pyqtSlot(str)
    def handle_result_signal(self, result):
        """
        Handle result signals from the result thread.
        """
        self.on_transcription_complete(result)

    @pyqtSlot(str)
    def on_transcription_complete(self, result):
        """
        When the transcription is complete, display the result in the transparent window.
        """
        QMetaObject.invokeMethod(self.transparent_window, "display_text", Qt.QueuedConnection, Q_ARG(str, result))

        # Always copy the result to the clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(result)

        if ConfigManager.get_config_value('misc', 'noise_on_completion'):
            AudioPlayer(os.path.join('assets', 'soft-beep.wav')).play(block=True)

        self.key_listener.start()

    def run(self):
        """
        Start the application.
        """
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    app = WhisperWriterApp()
    app.run()
