from enum import Enum

NUM_HOTELS = 7
MAX_MERGEABLE_SIZE = 11  # Hotels with size > 11 cannot be merged
SIZE_BRACKETS = [1, 2, 3, 4, 5, 6, 12, 21, 31, 41]
BASE_PRICE = 200
PRICE_INCR = 100

class HotelName(Enum):
    CONTI = 0
    IMPERIELLE = 1
    AMRICAIN = 2
    FESTIVUS = 3
    WORLDWIDE = 4
    TOBER = 5
    LEXOR = 6

class Hotel:
    def __init__(self, hotel_name: HotelName):
        self.name = hotel_name

    def level(self):
        if self.name.value <= 1:
            return 2
        elif self.name.value <= 4:
            return 1
        return 0

    def share_price(self, size: int):
        """
        Share price is a function of hotel level and size
        """
        price = BASE_PRICE + PRICE_INCR * self.level()
        for val in SIZE_BRACKETS:
            if size <= val:
                break
            price += 100
        return price
    