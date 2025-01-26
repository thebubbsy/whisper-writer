from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSlot
from PyQt5.QtGui import QFont, QCursor, QGuiApplication

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.text_label = QLabel(self)
        self.text_label.setFont(QFont('Segoe UI', 12))
        self.text_label.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white; padding: 10px 5px; border-radius: 10px;")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.follow_cursor)
        self.timer.start(16)  # Update position every 16 milliseconds (~60 FPS)

    @pyqtSlot(str)
    def display_text(self, text):
        self.text_label.setText("")
        self.adjust_size()
        self.move_near_cursor()
        self.show()
        self.typewrite_text(text)

    def adjust_size(self):
        self.text_label.adjustSize()
        self.setFixedSize(self.text_label.sizeHint().width() + 20, self.text_label.sizeHint().height() + 20)

    def move_near_cursor(self):
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_width = self.width()
        window_height = self.height()

        x = cursor_pos.x() - window_width - 20
        y = cursor_pos.y() - window_height // 2

        if x < 0:
            x = 20
        if y + window_height > screen_geometry.height():
            y = screen_geometry.height() - window_height - 20
        elif y < 0:
            y = 20

        self.move(x, y)

    def follow_cursor(self):
        if self.isVisible():
            self.move_near_cursor()

    def typewrite_text(self, text):
        interval = 10  # Interval between keystrokes in milliseconds

        def type_next_character(index):
            if index < len(text):
                current_text = self.text_label.text()
                self.text_label.setText(current_text + text[index])
                self.text_label.adjustSize()  # Adjust the size of the text label
                self.adjust_size()  # Adjust the size of the window
                QTimer.singleShot(interval, lambda: type_next_character(index + 1))

        type_next_character(0)

    def reset_window(self):
        self.text_label.setText("")
        self.hide()

    def closeEvent(self, event):
        self.hide()
        event.ignore()