import sys

from PyQt5.QtWidgets import (
    QGraphicsGridLayout,
    QGraphicsWidget,
    QGraphicsLinearLayout,
    QGraphicsTextItem,
    QGraphicsRectItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen

import core
import Board
import Player
import Token


class Tile(QGraphicsWidget):
    """ Tile class """

    def __init__(self, name, board_pos, price,
                 rent, mortgage, players, color,
                 group_name, number_in_group,
                 house_price, parent,
    ):
        super().__init__(parent=parent)
        self.name = name
        self.board_pos = board_pos
        self.price = price
        self.rent =  rent
        self.mortgage = mortgage
        self.color = color
        self.group_name = group_name
        self.number_in_group = number_in_group
        self.tokens = []
        self.owner = False
        self.house_price = house_price
        self.nb_houses = 0
        self.hotel = False

        self.layout = QGraphicsLinearLayout()
        self.token_layout = QGraphicsGridLayout()

        self.color_property = QGraphicsWidget()
        self.name_on_tile = QGraphicsWidget()
        self.info = QGraphicsWidget()

        self.layout.setOrientation(Qt.Vertical)

        property_name = QGraphicsTextItem(self.name, parent=self.name_on_tile)
        
        if name in parent.properties:
            if self.board_pos in core.PROPERTIES:
                money_info = QGraphicsTextItem(f"Price: {self.price}", parent=self.info)
                self.color_rect = self.color_tile(color)

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
            
        self.token_layout.setColumnMaximumWidth(0, 22)
        self.token_layout.setColumnMaximumWidth(1, 22)
        self.token_layout.setColumnMaximumWidth(2, 22)
        self.token_layout.setSpacing(1)

        self.layout.addItem(self.color_property)
        self.layout.addItem(self.name_on_tile)
        self.layout.addItem(self.info)
        self.layout.addItem(self.token_layout)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 100, 0)

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

    def add_houses(self, number):
        self.nb_houses += number
        self.display_houses()

    def add_hotel(self):
        self.nb_houses = 0
        self.hotel = True
        self.display_hotel()

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
        if self.hotel:
            return self.rent * self.parent().hotel_multiplier
        elif self.nb_houses:
            return self.rent * self.parent().house2mutliplier[self.nb_houses]
        else:
            return self.rent
    
    def get_mortgage(self):
        return self.mortgage

    def get_color(self):
        return self.color

    def get_group(self):
        return self.group_name

    def get_nb_houses(self):
        return self.nb_houses

    def get_house_price(self):
        return self.house_price

    def get_number_in_group(self):
        return self.number_in_group

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

    def display_houses(self):
        for i in range(self.nb_houses):
            width, height = self.color_rect.boundingRect().getRect()[2:]
            set_color = QColor()
            set_color.setNamedColor("#00FF00")
            house = QGraphicsRectItem(width/4 * i + 5, height/4, width/4 - 10, height/2)
            house.setParentItem(self.color_rect)
            house.setBrush(QBrush(set_color, style = Qt.Dense1Pattern))

    def display_hotel(self):
        if self.hotel:
            width, height = self.color_rect.boundingRect().getRect()[2:]
            houses = self.color_rect.childItems()

            for house in houses:
                house.setParentItem(None)

            rect_color = QColor()
            rect_color.setNamedColor("#FF0000")
            pen_color = QColor()
            pen_color.setNamedColor("#00A500")
            pen = QPen()
            pen.setBrush(QBrush(pen_color))
            pen.setWidth(2)

            hotel = QGraphicsRectItem(width/4, height/4, width/2, height/2)
            hotel.setParentItem(self.color_rect)
            hotel.setBrush(QBrush(rect_color, style = Qt.Dense1Pattern))
            hotel.setPen(pen)

    def paint(self, painter, option, widget):
        painter.drawRects(self.boundingRect())

    def color_tile(self, color):
        set_color = QColor()
        set_color.setNamedColor(color)
        color_rect = QGraphicsRectItem(0, 0, 150, 25, parent=self.color_property)
        color_rect.setBrush(QBrush(set_color, style = Qt.SolidPattern))
        return color_rect


def main():
    pass

if __name__ == "__main__":
    main()