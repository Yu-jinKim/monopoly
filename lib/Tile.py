import sys

from PyQt5.QtWidgets import (
    QGraphicsGridLayout,
    QGraphicsWidget,
    QGraphicsLinearLayout,
    QGraphicsTextItem,
)
from PyQt5.QtCore import Qt

import core
import Board
import Player
import Token


class Tile(QGraphicsWidget):
    """ Tile class """

    def __init__(self, name, board_pos, price, rent,
                       mortgage, players, parent
    ):
        super().__init__(parent=parent)
        self.name = name
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
            if self.board_pos in core.PROPERTIES:
                money_info = QGraphicsTextItem(f"Price: {self.price}", parent=self.info)

            elif self.board_pos in core.SPECIAL_CASES:
                if name == "Start":
                    money_start = QGraphicsTextItem(f"Free monay: {self.price}", parent=self.info)

                    for player, color in players.items():
                        token = Token.Token(player, color)
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

    def is_owned(self) -> bool:
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
        """ Display the tokens on the tile according to their number
        
        i.e. if there's 4, i want a 2x2 grid
             if there's 5 or more, i want a 3xn grid
        """

        if len(self.tokens) >= 4:
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

    def paint(self, painter, option, widget):
        painter.drawRects(self.boundingRect())


def main():
    pass

if __name__ == "__main__":
    main()