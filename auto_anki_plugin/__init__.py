# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from aqt.addcards import *

from aqt.qt import QApplication
import socket
import threading


port = 8080

screen = QApplication.primaryScreen()
geometry = screen.availableGeometry()

width = geometry.width()
height = geometry.height()

class Gui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Anki Plugin")
        self.resize(width, height//10)
        self.move(0,0)
        self.setWindowFlags((Qt.WindowType.WindowStaysOnTopHint))

        # Create widgets
        self.deck_dropdown = QComboBox()
        self.deck_dropdown.addItems(mw.col.decks.all_names())
        
        self.add_front_text_btn = QPushButton("Add Front Text")

        self.add_back_text_btn = QPushButton("Add Back Text")

        self.add_card_btn = QPushButton("Add Card")



        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.deck_dropdown)
        layout.addWidget(self.add_front_text_btn)
        layout.addWidget(self.add_back_text_btn)
        layout.addWidget(self.add_card_btn)


        self.setLayout(layout)
        
class AnkiManager:
    def __init__(self):
        self.front = []
        self.back = []

    def add_card(self):
        pass

    def add_front(self, front):
        pass

    def add_back(self, back):
        pass

class AnkiManagerConcrete(AnkiManager):
    def add_card(self):
        # Implement the logic to add a card to Anki
        pass

    def add_front(self, front):
        self.front.append(front)

    def add_back(self, back):
        self.back.append(back)


class EventListener(QObject):
    event_received = pyqtSignal(str)  # Add this
    def __init__(self):
        super().__init__()
        self.action_to_parem_len_map = {
            "add_front": 1,
            "add_back": 1,
            "add_card": 1
        }

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("localhost", port))
        self.listener_thread = threading.Thread(
            target=self.listen_for_events,
            daemon=True
        )
        self.listener_thread.start()

    def listen_for_events(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            action = data.decode('utf-8').strip()
            self.socket.sendto(b'ACK', addr)

            self.event_received.emit(action)

class EventController(QObject):
    @pyqtSlot(str)
    def handle_event(self, action):
        if action == "open_window":
            open_window()

window = None

def open_window():
    global window

    if window is None:
        window = Gui()

    window.show()
    window.raise_()
    window.activateWindow()


controller = EventController()

event_listener = EventListener()
event_listener.event_received.connect(controller.handle_event)

action = QAction("Auto Anki", mw)
qconnect(action.triggered, open_window)
mw.form.menuTools.addAction(action)

