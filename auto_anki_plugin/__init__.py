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
    def __init__(self, anki_manager):
        super().__init__()

        self.anki_manager = anki_manager

        self.setWindowTitle("Auto Anki Plugin")
        self.resize(width, height//10)
        self.move(0, 0)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Create widgets
        self.deck_dropdown = QComboBox()
        self.deck_dropdown.addItems(mw.col.decks.all_names())

        self.add_front_text_btn = QPushButton("Add Front Text")
        self.add_back_text_btn = QPushButton("Add Back Text")
        self.add_card_btn = QPushButton("Add Card")

        # Connect buttons
        qconnect(
            self.add_front_text_btn.clicked,
            self.on_add_front
        )

        qconnect(
            self.add_back_text_btn.clicked,
            self.on_add_back
        )

        qconnect(
            self.add_card_btn.clicked,
            self.on_add_card
        )

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.deck_dropdown)
        layout.addWidget(self.add_front_text_btn)
        layout.addWidget(self.add_back_text_btn)
        layout.addWidget(self.add_card_btn)

        self.setLayout(layout)

    def on_add_front(self):
        self.anki_manager.add_front("Example front")

    def on_add_back(self):
        self.anki_manager.add_back("Example back")

    def on_add_card(self):
        self.anki_manager.set_deck(self.deck_dropdown.currentText())
        self.anki_manager.add_card()


class AnkiManager:
    def __init__(self):
        self.front = []
        self.back = []

    def add_card(self):
        pass

    def add_front(self, front, note_type): 
       pass


    def add_back(self, back, note_type):
        pass

    def set_deck(self, deck_name):
        pass

class AnkiManagerConcrete(AnkiManager):
    def set_deck(self, deck_name):
        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

    def add_card(self):
        card = mw.col.newNote()

        if not self.front or not self.back:
            return

        for i in range(len(self.front)):
            front_text, front_note_type = self.front[i]
            if (front_note_type == "TEXT"):
                card["Front"] = f"{front_text}<br>"
            if (front_note_type == "IMAGE"):
                image_path = front_text
                image_name = mw.col.media.add_file(image_path)
                card["Front"] = f'<img src="{image_name}"><br>'


        for i in range(len(self.back)):
            back_text, back_note_type = self.back[i]
            if (back_note_type == "TEXT"):
                card["Back"] = f"{back_text}<br>"
            if (back_note_type == "IMAGE"):
                image_path = back_text
                image_name = mw.col.media.add_file(image_path)
                card["Back"] = f'<img src="{image_name}"><br>'

        mw.col.addNote(card)
        self.front.clear()
        self.back.clear()   

    def add_front(self, front, note_type):
        self.front.append((front, note_type))

    def add_back(self, back, note_type):
        self.back.append((back, note_type))


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
        anki_manager = AnkiManagerConcrete()
        window = Gui(anki_manager)

    window.show()
    window.raise_()
    window.activateWindow()


controller = EventController()

event_listener = EventListener()
event_listener.event_received.connect(controller.handle_event)

action = QAction("Auto Anki", mw)
qconnect(action.triggered, open_window)
mw.form.menuTools.addAction(action)

