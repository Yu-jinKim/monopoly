from typing import List, Tuple
from random import randint

PROPERTIES = {
    1: {"Old Kent Road": {"Rent": 2, "Price": 60}},
    3: {"Whitechapel Road": {"Rent": 4, "Price": 80}},
    5: {"King's Cross station": {"Rent": 25, "Price": 200}},
    6: {"The Angel Islington": {"Rent": 6, "Price": 100}},
    8: {"Euston Road": {"Rent": 6, "Price": 100}},
    9: {"Pentonville Road": {"Rent": 8, "Price": 120}},
    11: {"Pall Mall": {"Rent": 10, "Price": 140}},
    12: {"Electric Company": {"Rent": 1, "Price": 150}},
    13: {"Whitehall": {"Rent": 10, "Price": 140}},
    14: {"Northumberland Avenue": {"Rent": 12, "Price": 160}},
    15: {"Marylebine station": {"Rent": 25, "Price": 200}},
    16: {"Bow Street": {"Rent": 14, "Price": 180}},
    18: {"Marlborough Street": {"Rent": 14, "Price": 180}},
    19: {"Vine Street": {"Rent": 16, "Price": 200}},
    21: {"Strand": {"Rent": 18, "Price": 220}},
    23: {"Fleet Street": {"Rent": 18, "Price": 220}},
    24: {"Trafalgar Square": {"Rent": 20, "Price": 240}},
    25: {"Fenchurch Street station": {"Rent": 25, "Price": 200}},
    26: {"Leicester Square": {"Rent": 22, "Price": 260}},
    27: {"Coventry Street": {"Rent": 22, "Price": 260}},
    28: {"Water Works": {"Rent": 1, "Price": 150}},
    29: {"Piccadilly": {"Rent": 24, "Price": 280}},
    31: {"Regent Street": {"Rent": 26, "Price": 300}},
    32: {"Oxford Street": {"Rent": 26, "Price": 300}},
    34: {"Bond Street": {"Rent": 28, "Price": 320}},
    35: {"Liverpool Street station": {"Rent": 25, "Price": 200}},
    37: {"Park Lane": {"Rent": 35, "Price": 350}},
    39: {"Mayfair": {"Rent": 50, "Price": 400}}
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