""" Monopoly game

GUI done in PyQt5 using monopoly_core.py
"""

import argparse
from functools import partial
import sys
import time

from PyQt5.QtWidgets import (
    QLineEdit,
    QWidget,
    QApplication,
    QLabel,
    QMainWindow,
    QGridLayout,
    QColorDialog,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QErrorMessage,
)
from PyQt5.QtGui import QColor 

sys.path.append("lib")

import lib.core
from lib.Monopoly import Monopoly
from lib.Player import Player


class MainWindow(QMainWindow):
    """ main window where i display the various widgets """

    EXIT_CODE_REBOOT = 100

    def __init__(self, debug: bool = False):
        super().__init__()

        self.debug = debug
        self.setWindowTitle("Monopoly")
        self.central_widget = QStackedWidget()

        self.title_screen = TitleScreen()
        self.title_screen.start_game.clicked.connect(self.choose_names)

        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.title_screen)

    def choose_names(self) -> None:
        """ check the nb players field, open the names screen """

        try:
            nb_players = int(self.title_screen.nb_players.text())

            if nb_players > 6:
                error = QErrorMessage()
                error.showMessage("Can't have more than 6 players")
                error.exec_()
                return
            elif nb_players <= 0:
                error = QErrorMessage()
                error.showMessage("Are you kinding me?")
                error.exec_()
                return

        except Exception as e:
            error = QErrorMessage()
            error.showMessage(f"{e}")
            error.exec_()
        else:
            self.names_screen = NamesPlayers(nb_players)
            self.central_widget.addWidget(self.names_screen)
            self.central_widget.setCurrentWidget(self.names_screen)

            self.names_screen.confirm_button.clicked.connect(self.create_players)

    def create_players(self) -> None:
        """ check the names fields, open the game screen """

        players = {}

        if self.names_screen.player_colors == []:
            for i in range(len(self.names_screen.player_names)):
                self.names_screen.player_colors.append("#FFFFFF")

        for player, color in zip(
            self.names_screen.player_names,
            self.names_screen.player_colors
        ):
            name = player.text().strip()

            if name == "":
                error = QErrorMessage()
                error.showMessage("Please give all players names")
                error.exec_()
                return
            else:
                names = [player.get_name() for player in players]
                
                if name in names:
                    error = QErrorMessage()
                    error.showMessage("2 players can't have the same name")
                    error.exec_()
                    return

            players[Player(name)] = color

        self.game = Monopoly(players, self.debug)
        self.central_widget.addWidget(self.game)
        self.central_widget.setCurrentWidget(self.game)


class TitleScreen(QWidget):
    """ title screen, ask how many players """

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        description_layout = QHBoxLayout()
        nb_players_layout = QGridLayout()
        button_layout = QHBoxLayout()

        description = QLabel("Hallo, this is my Monopoly GUI game. 6 players max plz")
        label = QLabel("How many players? :")
        self.nb_players = QLineEdit()
        self.start_game = QPushButton("Start game")

        description_layout.addWidget(description)
        nb_players_layout.addWidget(label, 2, 0)
        nb_players_layout.addWidget(self.nb_players, 2, 1)
        button_layout.addWidget(self.start_game)

        for layout in [description_layout, nb_players_layout, button_layout]:
            main_layout.addLayout(layout)

        self.setLayout(main_layout)


class NamesPlayers(QWidget):
    """ name screen, ask the names of the players """

    def __init__(self, nb_players):
        super().__init__()

        self.player_names = []
        self.player_colors = []

        main_layout = QVBoxLayout()
        names_layout = QGridLayout()
        button_layout = QHBoxLayout()

        button_list = []

        for i in range(nb_players):
            label = QLabel("Name :")
            player_name = QLineEdit()
            color_button = QPushButton("Color")
            color_button.setStyleSheet("background-color: white")
            names_layout.addWidget(label, i, 0)
            names_layout.addWidget(player_name, i, 1)
            names_layout.addWidget(color_button, i, 2)
            button_list.append(color_button)
            self.player_names.append(player_name)
            color_button.clicked.connect(partial(self.open_colordialog, color_button))

        self.confirm_button = QPushButton("Confirm")

        button_layout.addWidget(self.confirm_button)

        main_layout.addLayout(names_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def open_colordialog(self, button):
        """ Open color dialog to get color for token
        
        Args:
            button: QPushButton
        """

        color_dialog = QColorDialog()
        if color_dialog.exec_() == QColorDialog.Accepted:
            button.setStyleSheet(
                "background-color: {}".format(color_dialog.selectedColor().name())
            )
        button.clearFocus()
        self.player_colors.append(color_dialog.selectedColor().name())


def main():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", default = False, action="store_true")

    args = parser.parse_args()

    reboot_code = MainWindow.EXIT_CODE_REBOOT

    # trick to get to restart the app when the game is over
    while reboot_code == MainWindow.EXIT_CODE_REBOOT:
        app = QApplication(sys.argv)

        window = MainWindow(args.debug)
        window.show()

        reboot_code = app.exec_()
        app = None
