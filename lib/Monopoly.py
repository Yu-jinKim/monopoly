from functools import partial
import sys
import time

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsScene,
    QGraphicsView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor

import core
import Board
import Player
import Tile


class Monopoly(QWidget):
    """ actual game, display the board and everything 
    
    Methods for controlling the game
    """

    def __init__(self, players, debug = False):
        super().__init__()

        self.players = list(players.keys())
        self.player2color = players
        self.die1 = None
        self.die2 = None
        self.sum_dice = None
        self.doubles = 0
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
        self.possessions = QTableWidget()
        roll_button = QPushButton("Roll")

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.board = Board.Board(self.player2color)
        self.board.setParent(self)
        self.scene.addItem(self.board)
        self.view.setScene(self.scene)

        self.possessions.setContentsMargins(0, 0, 50, 50)

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
        """ Get next player. Reset generator when over """

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
        tiles = self.current_player.get_possessions()

        if tiles:
            sorted_tiles = sorted(tiles, key = lambda x: x.get_price())

            self.possessions_info.setText("You have these properties:")

            if sorted_tiles != []:
                color2tiles = {}

                for tile in sorted_tiles:
                    color2tiles.setdefault(tile.get_color(), []).append(tile)

                self.possessions.setColumnCount(len(color2tiles))
                self.possessions.setRowCount(max((len(v) for k, v in color2tiles.items())))

                for column, (color, tiles) in enumerate(color2tiles.items()):
                    for row, tile in enumerate(tiles):
                        set_color = QColor()
                        set_color.setNamedColor(color)
                        cell = QTableWidgetItem()
                        cell.setBackground(QBrush(set_color, style = Qt.SolidPattern))
                        
                        if color == "#000000":
                            cell.setForeground(QBrush(QColor(255, 255, 255)))
                        
                        cell.setText(f"{tile.get_name()}")

                        self.possessions.setItem(row, column, cell)
        else:
            self.possessions.clearContents()

    def update_buttons(self, tile2houses):
        house_eligible_tiles = [tile for tile, nb_houses in tile2houses.items() if nb_houses < 4]

        if house_eligible_tiles:
            buy_houses = QPushButton("Buy houses")
            self.buttons_layout.addWidget(buy_houses)
            buy_houses.clicked.connect(partial(self.add_houses_dialog, tile2houses))

        hotel_eligible_tiles = [tile for tile, nb_houses in tile2houses.items() if nb_houses == 4]
        
        if hotel_eligible_tiles:
            buy_hotel = QPushButton("Buy hotel")
            self.buttons_layout.addWidget(buy_hotel)
            buy_hotel.clicked.connect(partial(self.add_hotel_dialog, hotel_eligible_tiles))

    def update_interface(self):
        """ Call all update around the board display methods """

        self.update_turn()
        self.update_balance()
        self.update_position()
        self.update_possessions()

        group2tiles = self.current_player.has_one_group()
        tile2houses = {}

        if group2tiles:
            for tiles in group2tiles.values():
                for tile in tiles:
                    tile2houses[tile] = tile.get_nb_houses()

            self.update_buttons(tile2houses)

    def add_houses_dialog(self, tile2houses):
        self.house_window = QDialog()

        main_layout = QVBoxLayout()
        tiles_layout = QGridLayout()
        button_layout = QHBoxLayout()
        
        button = QPushButton("Buy")

        for row, (tile, nb_houses) in enumerate(tile2houses.items()):
            if nb_houses != 4:
                nb_houses_to_add = QComboBox()
                
                for i in range(0, 4 - nb_houses + 1):
                    nb_houses_to_add.addItem(f"{i}")

                tiles_layout.addWidget(nb_houses_to_add, row, 0)
                tile_label = QLabel(f"{tile.get_name()}")
                tile_label.setStyleSheet(f"color: {tile.get_color()}")
                tiles_layout.addWidget(tile_label, row, 1)

        button_layout.addWidget(button)
        main_layout.addLayout(tiles_layout)
        main_layout.addLayout(button_layout)
        self.house_window.setLayout(main_layout)

        button.clicked.connect(partial(self.add_houses, tiles_layout))

        self.house_window.exec_()

    def add_houses(self, gridlayout):
        nb_row = gridlayout.rowCount()
        total_price = 0
        tile2nb_house_to_add = {}

        for row in range(nb_row):
            nb_house_to_add = int(gridlayout.itemAtPosition(row, 0).widget().currentText())
            tile_name = gridlayout.itemAtPosition(row, 1).widget().text()
            tile = self.board.get_tile(tile_name)

            tile2nb_house_to_add[tile] = nb_house_to_add
            total_price += tile.get_house_price() * nb_house_to_add

        if all(value == 0 for value in tile2nb_house_to_add.values()):
            self.popup("You didn't pick any houses to add")

        if total_price <= self.current_player.get_balance():
            for tile, nb_houses in tile2nb_house_to_add.items():
                tile.add_houses(nb_houses)
                tile.display_houses()

            self.house_window.done(0)
        
        else:
            self.popup("You don't have enough money to pay")
            
    def add_hotel_dialog(self, hotel_eligible_tiles):
        self.hotel_window = QDialog()

        main_layout = QVBoxLayout()
        tiles_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        hotel_options = QGroupBox()
        button = QPushButton("Buy")

        for tile in hotel_eligible_tiles:
            box = QCheckBox(f"{tile.get_name()}")
            box.setStyleSheet(f"color: {tile.get_color()}")
            tiles_layout.addWidget(box)

        hotel_options.setLayout(tiles_layout)
        button_layout.addWidget(button)
        main_layout.addWidget(hotel_options)
        main_layout.addLayout(button_layout)
        self.hotel_window.setLayout(main_layout)

        button.clicked.connect(partial(self.add_hotel, hotel_options))

        self.hotel_window.exec_()

    def add_hotel(self, groupbox):
        boxes = groupbox.findChildren(QCheckBox)
        hotel_price = 0
        hotels_to_add = []

        for box in boxes:
            if box.checkState() == 2:
                tile_name = box.text()
                tile = self.board.get_tile(tile_name)
                hotel_price += tile.get_house_price()
                hotels_to_add.append(tile)

        if hotel_price <= self.current_player.get_balance():
            for tile in hotels_to_add:
                tile.add_hotel()
            self.hotel_window.done(0)
        else:
            self.popup("You don't have enough money to buy those hotels")

    def order_players(self):
        """ roll dices for players and order them
        
        Returns: ordered players (list of Player)
        """

        rolls = []

        for player in self.players:
            rolls.append(sum(core.roll()[0:2]))

        rolls_players = sorted(set(zip(rolls, self.players)), key=lambda x: -x[0])
        ordered_players = [player for roll, player in rolls_players]

        message = "Order of players:\n"

        for roll, player in rolls_players:
            message += f"- {player} rolled {roll}\n"

        self.message_box.setText(message)
        self.message_box.exec_()

        return ordered_players

    def popup(self, message):
        """ Popup QMessageBox with param message 
        
        Args:
            message: str
        """

        self.message_box.setText(message)
        self.message_box.exec_()

    def update_token_position(self, current_tile, new_tile, message):
        """ Update the token position on the board 
        
        Remove from current tile
        Add to new tile
        Call display method

        Args:
            current_tile: Tile
            new_tile: Tile
            message: str
        """

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

    def play_turn(self, debug = False):
        """ Play the turn 
        
        Roll dice
        Move player
        Interact with the board
        Update interface

        Args:
            debug: bool
        """

        if not debug:
            self.roll()

        if not all((self.die1, self.die2, self.sum_dice)):
            return

        if self.current_player.in_jail():
            if self.die1 == self.die2:
                self.current_player.out_of_jail()
                self.popup("You're out of prison")
            else:
                self.current_player.pass_turn()
                
                if self.current_player.in_jail() == 0:
                    self.popup("You're out of prison")
                else:
                    self.popup(
                        f"You have {self.current_player.in_jail()} turns left in jail"
                    )

            self.pass_player_turn()
            self.update_interface()

        else:
            current_tile, passed_start = self.move_player()
            self.interact_board(current_tile, passed_start)

            if self.die1 == self.die2:
                self.doubles += 1

                if self.doubles == 3:
                    self.send_player_to_jail()
                    self.pass_player_turn()
                    self.update_interface()
                else:
                    self.update_interface()
            else:
                self.doubles = 0
                self.pass_player_turn()
                self.update_interface()

        if len(self.ordered_players) == 1:
            self.end_game(self.ordered_players[0])

    def roll(self):
        """ roll and get new position """

        self.die1, self.die2, self.sum_dice = core.roll()
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

        Returns:
            new_tile (Tile object)
            bool
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

        # use the fake position to get the new tile
        new_tile = self.board.get_tile(tile_pos = new_board_pos)

        self.update_token_position(
            current_tile,
            new_tile,
            f"You landed on {new_tile.get_name()}"
        )

        return new_tile, passed_start

    def send_player_to_jail(self):
        """ Send the current player to jail """

        current_tile = self.board.get_player_tile(self.current_player)
        jail_tile = self.board.get_tile(tile_name = "Visit Jail")
        
        self.update_token_position(
            current_tile,
            jail_tile,
            "You got sent to jail"
        )

        self.current_player.go_to_jail()

    def interact_board(self, tile, passed_start):
        """ Interaction with the board

        Buy properties, pay rent, pay taxes...

        Args:
            tile (Tile)
            passed_start (bool)
        """

        tile_name = tile.get_name()
        tile_board_pos = tile.get_board_pos()

        # Check that player didn't landed on Start or Jail before giving start money
        if passed_start and tile_name not in ["Start", "Go to Jail"]:
            start_tile = self.board.get_tile("Start")
            start_money = start_tile.get_price()
            self.current_player.receive(start_money)
            message = f"You earned {start_money} after passing through the Start tile"
            self.popup(message)

        if tile_board_pos in core.PROPERTIES:
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
                        self.current_player.add_possession(tile)
                        tile.set_owner(self.current_player)
                        message = f"You now have {tile_name} and {self.current_player.get_balance()}"
                        self.popup(message)
        
        elif tile_board_pos in core.SPECIAL_CASES:
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
        """ Check for player's real estate to see if bankrupt 
        
        Returns: bool
        """
        
        real_estate = 0
        player_properties = self.current_player.get_possessions()

        for tile in player_properties:
            real_estate += tile.get_mortgage()

        if real_estate < self.sum_to_pay:
            return True
        else:
            return False

    def mortgaging(self):
        """ Propose all player properties for mortgaging (checkboxes) """
        
        properties = self.current_player.get_possessions()

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
        Get the properties selected for mortgage
        Check if the sum is enough to pay the sum due
        Remove the properties from the player
        """

        boxes = self.mortgage_options.findChildren(QCheckBox)
        mortgage_money = 0
        chosen_mortgaged_properties = []

        for box in boxes:
            if box.checkState() == 2:
                name, mortgage_worth = box.text().split("-")
                mortgage_money += int(float(mortgage_worth))
                chosen_mortgaged_properties.append(name)

        if mortgage_money >= self.sum_to_pay:
            for name in chosen_mortgaged_properties:
                tile = self.board.get_tile(name)
                self.current_player.remove_possession(tile)
                tile.remove_owner()
            self.mortgaging_window.done(0)
        else:
            message = f"""
                You didn't give enough properties to mortgage:
                Properties worth {mortgage_money} vs sum to pay {self.sum_to_pay}
            """
            self.popup(message)

    def player_lost(self):
        """ Remove the player from the game """

        self.popup(f"{self.current_player} lost")
        self.ordered_players.remove(self.current_player)
        tile = self.board.get_player_tile(self.current_player)
        token = tile.get_token(self.current_player)
        tile.remove_token(token)
        tile.remove_token_layout(token)

    def end_game(self, winner):
        """ Open a QDialog to ask if the players want to restart 
        
        Args: winner (Player)
        """

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
        """ Send reboot exit code to the main event loop """
        QApplication.exit(self.parent().parent().EXIT_CODE_REBOOT)

    def exit_game(self):
        """ Send exit code to the main event loop """
        QApplication.exit(-1)


def main():
    pass

if __name__ == "__main__":
    main()