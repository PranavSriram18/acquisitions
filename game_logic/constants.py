
from enum import Enum

# Board parameters
NUM_ROWS = 3
NUM_COLS = 4

# Player parameters
TILES_PER_PLAYER = 6

# Hotel parameters
NUM_HOTELS = 7  # There are 7 types of hotels
TOTAL_SHARES = 25  # There are 25 available shares per hotel
MAX_MERGEABLE_SIZE = 11  # Hotels with size > 11 cannot be merged
SIZE_BRACKETS = [1, 2, 3, 4, 5, 6, 12, 21, 31, 41]
BASE_PRICE = 200
PRICE_INCR = 100

class Hotel(Enum):
    CONTI = 0
    IMPERIELLE = 1
    AMRICAIN = 2
    FESTIVUS = 3
    WORLDWIDE = 4
    TOBER = 5
    LEXOR = 6
    NO_HOTEL = 7

    def __str__(self):
        return f"{self.name[:2]}" if self.value < NUM_HOTELS else "XX"
    
    @classmethod
    def from_str(cls, s: str):
        if len(s) >= 2:
            s = s[0:2]
            for hotel in cls:
                if hotel.name[0:2] == s:
                    return hotel
        return cls.NO_HOTEL
        


def share_price(hotel: Hotel, size: int):
    """
    Share price is a function of hotel level and size
    """
    if hotel.name.value <= 1:
        level = 2
    elif hotel.name.value <= 4:
        level = 1
    else:
        level = 0
    price = BASE_PRICE + PRICE_INCR * level()
    for val in SIZE_BRACKETS:
        if size <= val:
            break
        price += 100
    return price

def majority_holder_award(hotel: Hotel, size: int):
    return 10 * share_price(hotel, size)

def minority_holder_award(hotel: Hotel, size: int):
    return 5 * share_price(hotel, size)

# Game events
class GameEvent(Enum):
    NOOP = 0
    JOIN_CHAIN = 1
    START_CHAIN = 2
    MERGER = 3
    DEAD_TILE = 4
    MULTIWAY_MERGER = 5
