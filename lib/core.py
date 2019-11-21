from typing import List, Tuple
from random import randint

PROPERTIES = {
    1: {"Old Kent Road": {"Rent": 2, "Price": 60, "Color": "#fe0090"}},
    3: {"Whitechapel Road": {"Rent": 4, "Price": 80, "Color": "#fe0090"}},
    5: {"King's Cross station": {"Rent": 25, "Price": 200, "Color": "#000000"}},
    6: {"The Angel Islington": {"Rent": 6, "Price": 100, "Color": "#00ffff"}},
    8: {"Euston Road": {"Rent": 6, "Price": 100, "Color": "#00ffff"}},
    9: {"Pentonville Road": {"Rent": 8, "Price": 120, "Color": "#00ffff"}},
    11: {"Pall Mall": {"Rent": 10, "Price": 140, "Color": "#6d0075"}},
    12: {"Electric Company": {"Rent": 1, "Price": 150, "Color": "#FFFFFF"}},
    13: {"Whitehall": {"Rent": 10, "Price": 140, "Color": "#6d0075"}},
    14: {"Northumberland Avenue": {"Rent": 12, "Price": 160, "Color": "#6d0075"}},
    15: {"Marylebine station": {"Rent": 25, "Price": 200, "Color": "#000000"}},
    16: {"Bow Street": {"Rent": 14, "Price": 180, "Color": "#ff6700"}},
    18: {"Marlborough Street": {"Rent": 14, "Price": 180, "Color": "#ff6700"}},
    19: {"Vine Street": {"Rent": 16, "Price": 200, "Color": "#ff6700"}},
    21: {"Strand": {"Rent": 18, "Price": 220, "Color": "#ff0000"}},
    23: {"Fleet Street": {"Rent": 18, "Price": 220, "Color": "#ff0000"}},
    24: {"Trafalgar Square": {"Rent": 20, "Price": 240, "Color": "#ff0000"}},
    25: {"Fenchurch Street station": {"Rent": 25, "Price": 200, "Color": "#000000"}},
    26: {"Leicester Square": {"Rent": 22, "Price": 260, "Color": "#e5c100"}},
    27: {"Coventry Street": {"Rent": 22, "Price": 260, "Color": "#e5c100"}},
    28: {"Water Works": {"Rent": 1, "Price": 150, "Color": "#FFFFFF"}},
    29: {"Piccadilly": {"Rent": 24, "Price": 280, "Color": "#e5c100"}},
    31: {"Regent Street": {"Rent": 26, "Price": 300, "Color": "#007e00"}},
    32: {"Oxford Street": {"Rent": 26, "Price": 300, "Color": "#007e00"}},
    34: {"Bond Street": {"Rent": 28, "Price": 320, "Color": "#007e00"}},
    35: {"Liverpool Street station": {"Rent": 25, "Price": 200, "Color": "#000000"}},
    37: {"Park Lane": {"Rent": 35, "Price": 350, "Color": "#000062"}},
    39: {"Mayfair": {"Rent": 50, "Price": 400, "Color": "#000062"}}
}

COLOR2GROUP_INFO = {
    "#fe0090": {"Name": "Rose-ish", "Number": 2, "House price": 50},
    "#00ffff": {"Name": "Cyan", "Number": 3, "House price": 50},
    "#6d0075": {"Name": "Purple-ish", "Number": 3, "House price": 100},
    "#ff6700": {"Name": "Orange", "Number": 3, "House price": 100},
    "#ff0000": {"Name": "Red", "Number": 3, "House price": 150},
    "#e5c100": {"Name": "Yellow", "Number": 3, "House price": 150},
    "#007e00": {"Name": "Green", "Number": 3, "House price": 200},
    "#000062": {"Name": "DarkBlue", "Number": 2, "House price": 200},
    "#000000": {"Name": "Stations", "Number": 4, "House price": None},
    "#FFFFFF": {"Name": "Utilities", "Number": 2, "House price": None}
}

SPECIAL_CASES = {
    0: {"Start": 200},
    4: {"Income Tax": 200},
    10: {"Visit Jail": None},
    20: {"Free Parking": None},
    30: {"Go to Jail": None},
    38: {"Super Tax": 100}
}

CHANCES = [7, 22, 36]

COMMUNITY_CHESTS = [2, 17, 33]

FREE_PARKING = 0

def roll() -> List[int]:
    """ roll 2 dice """
    die1 = randint(1, 6)
    die2 = randint(1, 6)
    sum_dice = sum((die1, die2))
    return die1, die2, sum_dice

def grid2pos(values: List[Tuple[int, int]]) -> int:
    """ List of board properties is basically a grid
    
    Args:
        values (list of int)
    Returns:
        pos (int)    
    """
    
    row, column = values
    pos = (row * 10) + row + column
    return pos


def main():
    pass


if __name__ == "__main__":
    main()