from constants import *

class Tile:
    def __init__(self, row: int, col: int):
        """
        Initializes a Tile object. Client is responsible for calling is_valid.
        """
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
        
    def __repr__(self):
        row_char = chr(self.row + ord('A'))
        return f"{row_char}{self.col}"

    @classmethod
    def from_str(cls, s: str):
        """
        Initializes a Tile from a 2-character string, e.g. A4, B7, etc.
        Ensures that the input string is exactly 2 characters long and that 
        both characters are valid (row as a letter, column as a digit).
        """
        if len(s) == 2 or len(s) == 3:
            r = s[0]
            c = s[1] # TODO
            if r.isalpha() and c.isdigit():
                print("Input okay")
                row = ord(r.upper()) - ord('A')
                col = int(c)
                return cls(row, col)
        return Tile(-1, -1)

    def is_valid(self):
        return 0 <= self.row < NUM_ROWS and 0 <= self.col < NUM_COLS
    