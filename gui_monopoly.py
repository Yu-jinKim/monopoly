""" Monopoly game

GUI done in PyQt5 using monopoly_core.py
"""

import argparse
import sys
import time
from functools import partial
from PyQt5.QtWidgets import (
    QLineEdit,
    QWidget,
    QApplication,
    QLabel,
    QMainWindow,
    QGridLayout,
    QGroupBox,
    QCheckBox,
    QDialog,
    QColorDialog,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QErrorMessage,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsGridLayout,
    QGraphicsWidget,
    QGraphicsLinearLayout,
    QGraphicsTextItem,
    QGraphicsEllipseItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor
import monopoly_core as mp_core


class MainWindow(QMainWindow):
    """ main window where i display the various widgets """

    EXIT_CODE_REBOOT = 100

    def __init__(self, debug = False):
        super().__init__()

        self.debug = debug
        self.setWindowTitle("Monopoly")
        self.central_widget = QStackedWidget()

        self.title_screen = TitleScreen()
        self.title_screen.start_game.clicked.connect(self.choose_names)

        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.title_screen)

    def choose_names(self):
        """ check the nb players field, open the names screen """

        try:
            nb_players = int(self.title_screen.nb_players.text())

            if nb_players > 6:
                error = QErrorMessage()
                error.showMessage("Can't have more than 6 players")
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

    def create_players(self):
        """ check the names fields, open the game screen """

        players = {}

        if self.names_screen.player_colors == []:
            for i in range(len(self.names_screen.player_names)):
                self.names_screen.player_colors.append("#000000")


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

            players[mp_core.Player(name)] = color

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

        description = QLabel("Hallo, this is my Monopoly GUI game")
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
        color_dialog = QColorDialog()
        if color_dialog.exec_() == QColorDialog.Accepted:
            button.setStyleSheet(
                "background-color: {}".format(color_dialog.selectedColor().name())
            )
        button.clearFocus()
        self.player_colors.append(color_dialog.selectedColor().name())


class Monopoly(QWidget):
    """ actual game, display the board and everything """

    def __init__(self, players, debug = False):
        super().__init__()

        self.players = list(players.keys())
        self.player2color = players
        self.die1 = None
        self.die2 = None
        self.sum_dice = None
        self.debug = debug

        self.main_layout = QVBoxLayout()
        self.turn_layout = QHBoxLayout()
        self.board_layout = QHBoxLayout()
        self.player_info_layout = QGridLayout()
        self.buttons_layout = QHBoxLayout()

        self.message_box = QMessageBox()
        self.ask = QMessageBox()

        if len(self.players) > 1:
            self.ordered_players = self.order_players()
        else:
            self.ordered_players = self.players

        self.player_generator()

        self.turn_label = QLabel()
        self.balance_info = QLabel()
        self.balance = QLabel()
        self.position_info = QLabel()
        self.position = QLabel()
        self.possessions_info = QLabel()
        self.possessions = QLabel()
        roll_button = QPushButton("Roll")

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.board = Board(self.player2color)
        self.board.setParent(self)
        self.scene.addItem(self.board)
        self.view.setScene(self.scene)

        self.pass_player_turn()
        self.update_interface()

        self.turn_layout.addWidget(self.turn_label)
        self.turn_layout.setAlignment(Qt.AlignCenter)
        self.board_layout.addWidget(self.view)
        self.player_info_layout.addWidget(self.balance_info, 1, 0, Qt.AlignCenter)
        self.player_info_layout.addWidget(self.balance, 2, 0, Qt.AlignCenter)
        self.player_info_layout.addWidget(self.position_info, 1, 1, Qt.AlignCenter)
        self.player_info_layout.addWidget(self.position, 2, 1, Qt.AlignCenter)
        self.player_info_layout.addWidget(self.possessions_info, 1, 2, Qt.AlignCenter)
        self.player_info_layout.addWidget(self.possessions, 2, 2, Qt.AlignCenter)
        self.buttons_layout.addWidget(roll_button)
        
        if debug:
            debug_button = QPushButton("Choose roll")
            self.buttons_layout.addWidget(debug_button)

        self.main_layout.addLayout(self.turn_layout)
        self.main_layout.addLayout(self.board_layout)
        self.main_layout.addLayout(self.player_info_layout)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

        roll_button.clicked.connect(self.play_turn)

        if debug:
            debug_button.clicked.connect(self.debug_roll)

    def player_generator(self):
        """ Generator for player turns """

        self.gen = (player for player in self.ordered_players)

    def pass_player_turn(self):
        try:
            self.current_player = next(self.gen)
        except StopIteration:
            self.player_generator()
            self.current_player = next(self.gen)

    def get_current_player(self):
        return self.current_player

    def update_turn(self):
        self.turn_label.setText(f"Turn of {self.current_player}")
        self.turn_label.setStyleSheet(
            f"background-color: {self.player2color[self.current_player]}"
        )
        self.turn_label.setFont(QFont("Comic Sans MS", 20, QFont.Bold))

    def update_balance(self):
        self.balance_info.setText("Money left:")
        self.balance.setText(f"{self.current_player.get_balance()}")

    def update_position(self):
        tile = self.board.get_player_tile(self.current_player)

        self.position_info.setText("Current position:")
        self.position.setText(f"{tile.get_name()}")

    def update_possessions(self):
        self.possessions_info.setText("You have these properties:")
        self.possessions.setText(f"{self.current_player.get_possessions()}")

    def update_interface(self):
        self.update_turn()
        self.update_balance()
        self.update_position()
        self.update_possessions()

    def order_players(self):
        """ roll dices for players and order them """

        rolls = []

        for player in self.players:
            rolls.append(sum(mp_core.roll()[0:2]))

        rolls_players = sorted(set(zip(rolls, self.players)), key=lambda x: -x[0])
        ordered_players = [player for roll, player in rolls_players]

        message = "Order of players:\n"

        for roll, player in rolls_players:
            message += f"- {player} rolled {roll}\n"

        self.message_box.setText(message)
        self.message_box.exec_()

        return ordered_players

    def popup(self, message):
        self.message_box.setText(message)
        self.message_box.exec_()

    def update_token_position(self, current_tile, new_tile, message):
        # add/remove token from new/current tile
        current_player_token = current_tile.get_token(self.current_player)
        current_tile.remove_token(current_player_token)
        new_tile.add_token(current_player_token)

        # remove token from layout
        current_tile.remove_token_layout(current_player_token)

        # add token in layout
        new_tile.display_game_pieces()

        # change token's tile
        current_player_token.set_tile(new_tile)

        time.sleep(0.5)

        self.popup(message)

    def play_turn(self, doubles = 0, debug = False):
        """ Play the turn 
        
        Roll dice
        Move player
        Interact with the board
        Check bankrupcy
        """

        if not debug:
            self.roll()

        if not all((self.die1, self.die2, self.sum_dice)):
            return

        if self.current_player.in_jail():
            if self.die1 == self.die2:
                self.current_player.out_of_jail()
            else:
                self.current_player.pass_turn()

            self.pass_player_turn()

        else:
            current_tile, passed_start = self.move_player()
            self.interact_board(current_tile, passed_start)

            if self.die1 == self.die2:
                doubles += 1

                if doubles == 3:
                    self.send_player_to_jail()
                    self.pass_player_turn()
                    self.update_interface()
                else:
                    self.update_interface()
                    self.play_turn(doubles)
            else:
                self.pass_player_turn()
                self.update_interface()

        if len(self.ordered_players) == 1:
            self.end_game(self.ordered_players[0])

    def roll(self):
        """ roll and get new position """

        self.die1, self.die2, self.sum_dice = mp_core.roll()
        self.popup(f"{self.current_player} rolled {self.die1} and {self.die2}: {self.sum_dice}")

    def debug_roll(self):
        """ Window to choose which value you get for rolling 
        Debug/testing thing
        """

        self.debug_window = QDialog()
        main_layout = QVBoxLayout()
        names_layout = QGridLayout()
        button_layout = QHBoxLayout()

        self.die1_debug = QLineEdit()
        self.die2_debug = QLineEdit()
        button = QPushButton("Confirm")

        for i, die in enumerate([self.die1_debug, self.die2_debug]):
            label = QLabel("Die value :")
            names_layout.addWidget(label, i, 0)
            names_layout.addWidget(die, i, 1)

        button_layout.addWidget(button)
        main_layout.addLayout(names_layout)
        main_layout.addLayout(button_layout)
        self.debug_window.setLayout(main_layout)
        
        button.clicked.connect(self.debug_clicked)

        self.debug_window.exec_()

    def debug_clicked(self):
        """ Get the values typed and feed them to the play turn function """

        self.die1 = int(self.die1_debug.text())
        self.die2 = int(self.die2_debug.text())
        self.sum_dice = self.die1 + self.die2
        self.debug_window.done(0)
        self.play_turn(debug = True)

    def move_player(self):
        """ Move player on the board

        Get new position --> new tile
        Remove player from old tile
        Add player to new tile
        """
        
        passed_start = False

        # get the new tile according to the position of current player
        current_tile = self.board.get_player_tile(self.current_player)
        current_board_pos = current_tile.get_board_pos()
        new_board_pos = current_board_pos + self.sum_dice

        # if player gets passed last position of the board
        # "reset" the number to loop through the board
        if new_board_pos >= 40:
            new_board_pos -= 40
            passed_start = True

        # use the real position to get the fake position
        new_fake_pos = list(
            self.board.board_positions.keys()
        )[list(self.board.board_positions.values()).index(new_board_pos)]

        # use the fake position to get the new tile
        new_tile = self.board.get_tile(tile_pos = new_fake_pos)

        self.update_token_position(
            current_tile,
            new_tile,
            f"You landed on {new_tile.get_name()}"
        )

        return new_tile, passed_start

    def send_player_to_jail(self):
        """ Send the current player to jail """

        current_tile = self.board.get_player_tile(self.current_player)
        jail_tile = self.board.get_tile(tile_name = "Go to Jail")
        
        self.update_token_position(
            current_tile,
            jail_tile,
            "You landed in jail"
        )

        self.current_player.go_to_jail()

    def interact_board(self, tile, passed_start):
        """ Interaction with the board

        Buy properties, pay rent, pay taxes...
        """

        tile_name = tile.get_name()
        tile_board_pos = tile.get_board_pos()

        if passed_start and tile_name not in ["Start", "Go to Jail"]:
            start_tile = self.board.get_tile("Start")
            start_money = start_tile.get_price()
            self.current_player.receive(start_money)
            message = f"You earned {start_money} after passing through the Start tile"
            self.popup(message)

        if tile_board_pos in mp_core.PROPERTIES:
            if tile.is_owned():
                owner = tile.get_owner()

                if owner != self.current_player:
                    rent = tile.get_rent()

                    if self.current_player.get_balance() >= rent:
                        new_balance = self.current_player.pay(rent)
                        owner_balance = owner.receive(rent)
                        message = f"""
                            You have landed on {owner}'s property
                            You have to pay {rent}:
                             - {self.current_player} now have {new_balance}
                             - {owner} now have {owner_balance}
                        """
                        self.popup(message)
                    else:
                        self.sum_to_pay = rent
                        bankrupt = self.player_bankrupt()

                        if bankrupt:
                            self.player_lost()
                        else:
                            self.mortgaging()

            else:
                price = tile.get_price()
                player_balance = self.current_player.get_balance()

                if player_balance < price:
                    message = f"You don't have enough money to buy {tile_name} ({price})"
                    self.popup(message)
                else:    
                    buy = self.ask.question(
                        self,
                        "",
                        f"Buy {tile_name} for {price}?",
                        self.ask.Yes | self.ask.No
                    )
                    self.ask.exec_()
                    
                    if buy == self.ask.Yes:
                        self.current_player.add_possession(tile_name, price)
                        tile.set_owner(self.current_player)
                        message = f"You now have {tile_name} and {self.current_player.get_balance()}"
                        self.popup(message)
        
        elif tile_board_pos in mp_core.SPECIAL_CASES:
            tile_value = tile.get_price()
            suffix_message = f"for landing on {tile_name}"
            
            if tile_name == "Start":
                self.current_player.receive(tile_value * 2)
                message = f"You receive {tile_value * 2} {suffix_message}"
                self.popup(message)

            elif tile_name in ["Income Tax", "Super Tax"]:
                if self.current_player.get_balance() >= tile_value:
                    self.current_player.pay(tile_value)
                    self.board.free_parking += tile_value
                    message = f"You pay {tile_value} {suffix_message}"
                    self.popup(message)
                else:
                    self.sum_to_pay = tile_value
                    bankrupt = self.player_bankrupt()
                    
                    if bankrupt:
                        self.player_lost()
                    else:
                        self.mortgaging()

            elif tile_name == "Go to Jail":
                self.send_player_to_jail()

            elif tile_name == "Free Parking":
                self.current_player.receive(self.board.free_parking)
                message = f"You receive {self.board.free_parking} {suffix_message}"
                self.board.free_parking = 0
                self.popup(message)

        elif tile_name == "Chance" or tile_name == "Community Chest":
            pass

    def player_bankrupt(self):
        """ Check for player's real estate to see if bankrupt """
        
        real_estate = 0
        player_properties_names = self.current_player.get_possessions()

        for prop_name in player_properties_names:
            prop_tile = self.board.get_tile(prop_name)
            real_estate += prop_tile.get_mortgage()

        if real_estate < self.sum_to_pay:
            return True
        else:
            return False

    def mortgaging(self):
        """ Mortgaging properties to avoid bankrupcy """
        
        player_properties_names = self.current_player.get_possessions()
        properties = []
        self.chosen_mortgaged_properties = {}

        for prop_name in player_properties_names:
            properties.append(self.board.get_tile(prop_name))

        self.mortgaging_window = QDialog()

        main_layout = QVBoxLayout()
        groupbox_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.mortgage_options = QGroupBox()
        button = QPushButton("Mortgage")

        for prop in properties:
            box = QCheckBox(f"{prop.get_name()}-{prop.get_mortgage()}")
            groupbox_layout.addWidget(box)

        button_layout.addWidget(button)
        self.mortgage_options.setLayout(groupbox_layout)

        main_layout.addWidget(self.mortgage_options)
        main_layout.addLayout(button_layout)

        self.mortgaging_window.setLayout(main_layout)

        button.clicked.connect(self.mortgage_clicked)

        self.mortgaging_window.exec_()

    def mortgage_clicked(self):
        """
        Propose properties for possible mortgages
        Check if the sum is enough to pay the sum due
        Remove the properties from the player
        """

        boxes = self.mortgage_options.findChildren(QCheckBox)
        mortgage_money = 0

        for box in boxes:
            if box.checkState() == 2:
                name, mortgage_worth = box.text().split("-")
                mortgage_money += int(float(mortgage_worth))
                self.chosen_mortgaged_properties[name] = mortgage_worth

        if mortgage_money >= self.sum_to_pay:
            for name, worth in self.chosen_mortgaged_properties.items():
                tile = self.board.get_tile(name)
                self.current_player.remove_possession(name, int(float(worth)))
                tile.remove_owner()
                self.mortgaging_window.done(0)
        else:
            message = f"""
                You didn't give enough properties to mortgage:
                Properties worth {mortgage_money} vs sum to pay {self.sum_to_pay}
            """
            self.popup(message)

    def player_lost(self):
        self.popup(f"{self.current_player} lost")
        self.ordered_players.remove(self.current_player)
        tile = self.board.get_player_tile(self.current_player)
        token = tile.get_token(self.current_player)
        tile.remove_token(token)
        tile.remove_token_layout(token)

    def end_game(self, winner):
        self.end_window = QDialog()
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        message = QLabel(
            f"""
                Game over:
                {winner} has won !

                Replay a game?
            """)
        
        no_button = QPushButton("No")
        yes_button = QPushButton("Yes")

        button_layout.addWidget(no_button)
        button_layout.addWidget(yes_button)
        
        main_layout.addWidget(message)
        main_layout.addLayout(button_layout)
        self.end_window.setLayout(main_layout)

        no_button.clicked.connect(self.exit_game)
        yes_button.clicked.connect(self.restart)

        self.end_window.exec_()

    def restart(self):
        QApplication.exit(self.parent().parent().EXIT_CODE_REBOOT)

    def exit_game(self):
        QApplication.exit(-1)

class Board(QGraphicsWidget):
    def __init__(self, players):
        super().__init__()
        self.free_parking = 0
        self.total_tokens = []

        for player, color in players.items():
            self.total_tokens.append(Token(player, color))

        self.board_layout = QGraphicsGridLayout()
        self.board_layout.setSpacing(0)

        self.properties = [
            "Free Parking", "Strand", "Chance", "Fleet Street", "Trafalgar Square",
            "Fenchurch Street station", "Leicester Square", "Coventry Street", "Water Works", "Piccadilly", "Go to Jail",
            "Vine Street", "", "", "", "", "", "", "", "", "", "Regent Street",
            "Marlborough Street", "", "", "", "", "", "", "", "", "", "Oxford Street",
            "Community Chest", "", "", "", "", "", "", "", "", "", "Community Chest",
            "Bow Street", "", "", "", "", "", "", "", "", "", "Bond Street",
            "Marylebine station", "", "", "", "", "", "", "", "", "", "Liverpool Street station",
            "Northumberland Avenue", "", "", "", "", "", "", "", "", "", "Chance",
            "Whitehall", "", "", "", "", "", "", "", "", "", "Park Lane",
            "Electric Company", "", "", "", "", "", "", "", "", "", "Super Tax",
            "Pall Mall", "", "", "", "", "", "", "", "", "", "Mayfair",
            "Visit Jail", "Pentonville Road", "Euston Road", "Chance", "The Angel Islington", "King's Cross station",
            "Income Tax", "Whitechapel Road", "Community Chest", "Old Kent Road", "Start"
        ]

        self.board_positions = {
            0: 20, 1: 21, 2: 22, 3: 23, 4: 24,
            5: 25, 6: 26, 7: 27, 8: 28, 9: 29,
            10: 30, 11: 19, 21: 31, 22: 18, 32: 32,
            33: 17, 43: 33, 44: 16, 54: 34, 55: 15,
            65: 35, 66: 14, 76: 36, 77: 13, 87: 37,
            88: 12, 98: 38, 99: 11, 109: 39, 110: 10,
            111: 9, 112: 8, 113: 7, 114: 6, 115: 5,
            116: 4, 117: 3, 118: 2, 119: 1, 120: 0
        }

        positions = [(i, j) for i in range(11) for j in range(11)]

        for position, name in zip(positions, self.properties):
            if name == "":
                continue
            
            fake_pos = grid2pos(position)
            board_pos = self.board_positions[fake_pos]
            
            if board_pos in mp_core.PROPERTIES:
                price = mp_core.PROPERTIES[board_pos][name]["Price"]
                rent = mp_core.PROPERTIES[board_pos][name]["Rent"]
                mortgage = price / 2
            
            elif board_pos in mp_core.SPECIAL_CASES:
                price = mp_core.SPECIAL_CASES[board_pos][name]
                rent, mortgage = None, None

            elif board_pos in mp_core.CHANCES or board_pos in mp_core.COMMUNITY_CHESTS:
                price, rent, mortgage = None, None, None

            self.board_layout.addItem(
                Tile(
                    name,
                    fake_pos,
                    board_pos,
                    price,
                    rent,
                    mortgage,
                    players,
                    parent=self
                    ),
                *position
            )

        self.setLayout(self.board_layout)

    def get_player_tile(self, current_player):
        for i in range(0, 40):
            tile = self.board_layout.itemAt(i)

            if tile.has_tokens():
                tokens = tile.get_all_tokens()

                for token in tokens:
                    player = token.get_player()

                    if player == current_player:
                        return tile

    def get_tile(self, tile_name = None, tile_pos = None):
        """ Get tile object from name or pos """
        
        for i in range(0, 40):
            tile = self.board_layout.itemAt(i)
            
            if tile_name == tile.get_name():
                return tile

            if tile_pos == tile.get_fake_pos():
                return tile


class Tile(QGraphicsWidget):
    def __init__(self, name, fake_pos, board_pos,
                 price, rent, mortgage, players, parent
    ):
        super().__init__(parent=parent)
        self.name = name
        self.fake_pos = fake_pos
        self.board_pos = board_pos
        self.price = price
        self.rent =  rent
        self.mortgage = mortgage
        self.tokens = []
        self.owner = False

        self.layout = QGraphicsLinearLayout()
        self.token_layout = QGraphicsGridLayout()
        self.token_layout.setSpacing(0.5)

        self.name_on_tile = QGraphicsWidget()
        self.info = QGraphicsWidget()

        self.layout.setOrientation(Qt.Vertical)
        self.setContentsMargins(75, 0, 90, 0)

        property_name = QGraphicsTextItem(self.name, parent=self.name_on_tile)
        
        if name in parent.properties:
            if self.board_pos in mp_core.PROPERTIES:
                money_info = QGraphicsTextItem(f"Price: {self.price}", parent=self.info)

            elif self.board_pos in mp_core.SPECIAL_CASES:
                if name == "Start":
                    money_start = QGraphicsTextItem(f"Free monay: {self.price}", parent=self.info)

                    for player, color in players.items():
                        token = Token(player, color)
                        token.set_tile(self)
                        self.tokens.append(token)

                    self.display_game_pieces()

                elif name in ["Income Tax", "Super Tax"]:
                    money_tax = QGraphicsTextItem(f"Tax: -{self.price}", parent=self.info)

        self.layout.addItem(self.name_on_tile)
        self.layout.addItem(self.info)
        self.layout.addItem(self.token_layout)
        self.setLayout(self.layout)

        self.layout.setAlignment(self.layout, Qt.AlignCenter)

    def is_owned(self):
        if self.owner:
            return True
        else:
            return False

    def set_owner(self, player):
        self.owner = player

    def get_owner(self):
        return self.owner

    def remove_owner(self):
        self.owner = False

    def add_token(self, token):
        self.tokens.append(token)

    def remove_token(self, token):
        self.tokens.remove(token)

    def remove_token_layout(self, token):
        self.token_layout.removeItem(token)

    def get_name(self):
        return self.name

    def get_fake_pos(self):
        return self.fake_pos

    def get_board_pos(self):
        return self.board_pos

    def get_token(self, player):
        for token in self.tokens:
            if player == token.get_player():
                return token

        return

    def get_all_tokens(self):
        return self.tokens

    def get_price(self):
        return self.price

    def get_rent(self):
        return self.rent
    
    def get_mortgage(self):
        return self.mortgage

    def has_tokens(self):
        if self.tokens != []:
            return True
        else:
            return False

    def display_game_pieces(self):
        if len(self.tokens) == 6 or len(self.tokens) == 5 or len(self.tokens) == 4:
            sub_layout = True
            sub_pos = 0
        else:
            sub_layout = False

        for i, token in enumerate(self.tokens):
            if (len(self.tokens) == 4 and i >= 2) or (
                len(self.tokens) >= 5 and i >= 3
            ):
                if sub_layout:
                    self.token_layout.addItem(token, 1, sub_pos)
                    sub_pos += 1
            else:
                self.token_layout.addItem(token, 0, i)

        return self.token_layout



    def paint(self, painter, option, widget):
        painter.drawRects(self.boundingRect())


class Token(QGraphicsWidget):
    def __init__(self, player, color):
        super().__init__()
        self.player = player
        self.token = QGraphicsEllipseItem(0, 0, 20, 20, parent = self)
        self.fill_token(color)

    def get_current_tile(self):
        return self.current_tile

    def set_tile(self, new_tile):
        self.current_tile = new_tile

    def get_player(self):
        return self.player

    def fill_token(self, color = Qt.white):
        set_color = QColor(0, 0, 0)
        set_color.setNamedColor(color)

        self.token.setBrush(QBrush(
            set_color, style = Qt.SolidPattern
        ))


def grid2pos(values):
    row, column = values
    pos = (row * 10) + row + column
    return pos


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
