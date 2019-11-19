import sys

from PyQt5.QtWidgets import (
    QGraphicsGridLayout,
    QGraphicsWidget,
    QGraphicsLinearLayout,
    QGraphicsTextItem,
    QGraphicsEllipseItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

import Player
import Tile


class Token(QGraphicsWidget):
    """ Player token class """

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

    def fill_token(self, color):
        """ Color the token with the chosen color
        
        Args: color (Qt.color)    
        """

        set_color = QColor()
        set_color.setNamedColor(color)

        self.token.setBrush(QBrush(
            set_color, style = Qt.SolidPattern
        ))


def main():
    pass

if __name__ == "__main__":
    main()