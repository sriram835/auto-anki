# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from aqt.addcards import *

from aqt.qt import QApplication
import socket
import json
import threading
import os
import anki

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

        qconnect(
            self.deck_dropdown.currentTextChanged,
            self.on_deck_changed
        )

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.deck_dropdown)
        layout.addWidget(self.add_front_text_btn)
        layout.addWidget(self.add_back_text_btn)
        layout.addWidget(self.add_card_btn)
        self.setLayout(layout)

    def on_add_front(self):
        text = get_user_input()
        self.anki_manager.add_front(text, "TEXT")

    def on_add_back(self):
        text = get_user_input()
        self.anki_manager.add_back(text, "TEXT")

    def on_add_card(self):
        self.anki_manager.set_deck(self.deck_dropdown.currentText())
        self.anki_manager.add_card()

    def on_deck_changed(self):
        self.anki_manager.set_deck(self.deck_dropdown.currentText())


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
    def __init__(self):
        super().__init__()
        self.deck_id = None

    def set_deck(self, deck_name):
        self.deck_id = mw.col.decks.id(deck_name)

    def add_card(self):
        card = mw.col.newNote()

        if not self.front or not self.back:
            return

        for i in range(len(self.front)):
            front_text, front_note_type = self.front[i]
            if (front_note_type == "TEXT"):
                card["Front"] += f"{front_text}<br>"
            if (front_note_type == "IMAGE"):
                image_path = front_text
                image_name = mw.col.media.add_file(image_path)
                card["Front"] += f'<img src="{image_name}"><br>'


        for i in range(len(self.back)):
            back_text, back_note_type = self.back[i]
            if (back_note_type == "TEXT"):
                card["Back"] += f"{back_text}<br>"
            if (back_note_type == "IMAGE"):
                image_path = back_text
                image_name = mw.col.media.add_file(image_path)
                card["Back"] += f'<img src="{image_name}"><br>'

        if (self.deck_id == None):
            self.set_deck("Default")
        mw.col.add_note(card, self.deck_id)
        self.front.clear()
        self.back.clear()   

    def add_front(self, front, note_type):
        self.front.append((front, note_type))

    def add_back(self, back, note_type):
        self.back.append((back, note_type))


class EventListener(QObject):
    event_received = pyqtSignal(dict)  # Add this
    def __init__(self):
        super().__init__()
        

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
            message = json.loads(data.decode("utf-8"))
            self.socket.sendto(b'ACK', addr)
            self.event_received.emit(message)



window = None
anki_manager = AnkiManagerConcrete()


class EventController(QObject):
    @pyqtSlot(dict)
    def handle_event(self, message):
        if message["action"] == "open_window":
            open_window()

        if message["action"] == "add_front_img":
            anki_manager.add_front(message["data"][0], "IMAGE")

        if message['action'] == "add_back_img":
            anki_manager.add_back(message["data"][0], "IMAGE")

        if message['action'] == "add_card":
            anki_manager.add_card()


def get_user_input(title="Enter Text", label="Enter your text:"):
    text, ok = QInputDialog.getText(
        None,
        title,
        label
    )

    if ok:
        return text

    return None

def open_window():
    global window

    if window is None:
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

config = mw.addonManager.getConfig(__name__)

addon_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(addon_dir, "config.json")

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)