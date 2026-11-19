from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import socket
import pyautogui as pag
import ctypes
import mouse
import time
import keyboard
import ctypes
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
import json

CSIDL_MYPICTURES = 0x0027


pictures_folder = Path.home() / "Pictures"
anki_pic_folder = pictures_folder / "auto_anki_pictures"
anki_pic_folder.mkdir(parents=True, exist_ok=True)
new_img_path = ""

class RegionScreenCapture(QWidget):
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.painter_visible = True

        self.dpr = app.primaryScreen().devicePixelRatio()
        self.start = pag.position()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Enable transparent window background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.move(
            round(self.start.x / self.dpr),
            round(self.start.y / self.dpr)
        )

        self.resize(10, 10)
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_selection)
        self.timer.start(10)

    def paintEvent(self, event):

        if not self.painter_visible:
            return

        painter = QPainter(self)

        painter.setBrush(QColor(255, 255, 255, 40))
        painter.setPen(QPen(QColor(255, 255, 255, 255), 2))

        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))

    def hide_painter(self):
        self.painter_visible = False
        self.update()


    def update_selection(self):

        current = pag.position()

        x1 = self.start.x / self.dpr
        y1 = self.start.y / self.dpr

        x2 = current.x / self.dpr
        y2 = current.y / self.dpr

        x = min(x1, x2)
        y = min(y1, y2)

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        self.setGeometry(
            round(x),
            round(y),
            max(2, round(width)),
            max(2, round(height))
        )


        if mouse.is_pressed(button='left'):
            self.hide_painter()
            #print(f"Mouse is pressed")
            QTimer.singleShot(100, self.capture_screenshot)
            self.timer.stop()

        self.update()

    def capture_screenshot(self):
        global new_img_path

        current = pag.position()

        capture_x = min(self.start.x, current.x)
        capture_y = min(self.start.y, current.y)

        capture_width = abs(current.x - self.start.x)
        capture_height = abs(current.y - self.start.y)
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H-%M-%S")
        pag.screenshot(
            region=(
                capture_x,
                capture_y,
                capture_width,
                capture_height
            )
        ).save(f"{anki_pic_folder}\\{date_time}.png")
        new_img_path = f"{anki_pic_folder}\\{date_time}.png"
        self.close()

    def closeEvent(self, event):
        self.finished.emit()
        event.accept()

app = QApplication(sys.argv)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 8080
addr = ("127.0.0.1",port)
while True:
    if keyboard.is_pressed("u") and keyboard.is_pressed('alt'):
        mess = {
                    "action": "open_window",
                    "data": []
                }
        sock.sendto(json.dumps(mess).encode(),addr)

    if keyboard.is_pressed("i") and keyboard.is_pressed('alt'):
        mess = {
            "action": "add_card",
            "data": []
        }
        sock.sendto(json.dumps(mess).encode(),addr)
    if keyboard.is_pressed("o") and keyboard.is_pressed("alt"):

        tracker = RegionScreenCapture()

        loop = QEventLoop()
        tracker.finished.connect(loop.quit)

        tracker.show()
        loop.exec()

        mess = {
            "action": "add_front_img",
            "data": [new_img_path]
        }

        sock.sendto(json.dumps(mess).encode(), addr)
        
    if keyboard.is_pressed("p") and keyboard.is_pressed("alt"):

        tracker = RegionScreenCapture()

        loop = QEventLoop()
        tracker.finished.connect(loop.quit)

        tracker.show()
        loop.exec()

        mess = {
            "action": "add_back_img",
            "data": [new_img_path]
        }

        sock.sendto(json.dumps(mess).encode(), addr)

    if keyboard.is_pressed("y") and keyboard.is_pressed('alt'):
        break

    time.sleep(0.05)

sock.close()


#app = QApplication(sys.argv)
#tracker = RegionScreenCapture()
#tracker.show()
#sys.exit(app.exec())


