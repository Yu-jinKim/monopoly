import sys

from PyQt5.QtWidgets import (
    QGraphicsGridLayout,
    QGraphicsWidget,
)

import core
import Player
import Tile
import Token


class Board(QGraphicsWidget):
    """ Board object on which the tiles will be """

    def __init__(self, players):
        super().__init__()
        self.free_parking = 0
        self.total_tokens = []

        for player, color in players.items():
            self.total_tokens.append(Token.Token(player, color))

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

        self.house2multiplier = {
            1: 5,
            2: 15,
            3: 45,
            4: 80,
        }

        self.hotel_multiplier = 125

        positions = [(i, j) for i in range(11) for j in range(11)]

        for position, name in zip(positions, self.properties):
            if name == "":
                continue
            
            # Give all the data necessary to the tile from the core code
            fake_pos = core.grid2pos(position)
            board_pos = self.board_positions[fake_pos]
            
            if board_pos in core.PROPERTIES:
                price = core.PROPERTIES[board_pos][name]["Price"]
                rent = core.PROPERTIES[board_pos][name]["Rent"]
                mortgage = price / 2
                color_property = core.PROPERTIES[board_pos][name]["Color"]
                group = core.COLOR2GROUP_INFO[color_property]["Name"]
                number = core.COLOR2GROUP_INFO[color_property]["Number"]
                house_price = core.COLOR2GROUP_INFO[color_property]["House price"]

            elif board_pos in core.SPECIAL_CASES:
                price = core.SPECIAL_CASES[board_pos][name]
                rent, mortgage = None, None
                house_price = None
                color_property, group, number = None, None, None

            elif board_pos in core.CHANCES or board_pos in core.COMMUNITY_CHESTS:
                price, rent, mortgage = None, None, None
                house_price = None
                color_property, group, number = None, None, None

            self.board_layout.addItem(
                Tile.Tile(
                    name,
                    board_pos,
                    price, rent, mortgage,
                    players,
                    color_property,
                    group,
                    number,
                    house_price,
                    parent=self
                    ),
                *position
            )

        self.setLayout(self.board_layout)

    def get_player_tile(self, current_player):
        """ Return tile on which the current player is on 
        
        Args: current_player (Player)
        """

        # Loop through the tiles
        for i in range(0, 40):
            tile = self.board_layout.itemAt(i)

            if tile.has_tokens():
                tokens = tile.get_all_tokens()

                for token in tokens:
                    player = token.get_player()

                    if player == current_player:
                        return tile

    def get_tile(self, tile_name = None, tile_pos = None):
        """ Get tile object from name or pos 
        
        Args:
            tile_name (str)
            tile_pos (int)
        Returns:
            tile (Tile)
        """
        
        for i in range(0, 40):
            tile = self.board_layout.itemAt(i)
            
            if tile_name == tile.get_name():
                return tile

            if tile_pos == tile.get_board_pos():
                return tile


def main():
    pass

if __name__ == "__main__":
    main()