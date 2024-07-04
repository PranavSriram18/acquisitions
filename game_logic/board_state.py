
from typing import List

from constants import *
from tile import *

class CellState:
    def __init__(self):
        self.occupied = False
        self.hotel = HotelName.NO_HOTEL

class BoardState:
    def __init__(self):
        self.board = [[CellState() for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        # tracks sizes of each hotel on board
        self.hotel_sizes = [0] * NUM_HOTELS

        # TODO - auxiliary tracking structures

    def place_tile(self, tile: Tile) -> GameEvent:
        """
        \pre: tile must be a valid Tile that hasn't been placed before.
        """
        row, col = tile.row, tile.col
        cell = self.board[row][col]
        neighbor_cells = self.get_neighbors(tile)
        neighbor_hotels = [c.hotel for c in neighbor_cells if c.hotel != HotelName.NO_HOTEL]
        num_neighboring_hotels = len(set(neighbor_hotels))
        cell.occupied = True

        if num_neighboring_hotels == 0:
            # Case 0: isolated tile
            if not any([nc.occupied for nc in neighbor_cells]):
                return GameEvent.NOOP  
            else:
                # Case 1: starts a chain
                return GameEvent.START_CHAIN
        elif num_neighboring_hotels == 1:
            # Case 2: absorbed into existing chain
            cell.hotel = neighbor_hotels[0]
            self.run_bfs(cell)  # TODO
            return GameEvent.JOIN_CHAIN
        elif num_neighboring_hotels == 2:
            # TODO - check if merge is possible
            can_merge = True
            if can_merge:
                return GameEvent.MERGER
        else:
            # TODO - check if merge is possible
            can_merge = True
            if can_merge:
                return GameEvent.MULTIWAY_MERGER
            
    def get_neighbors(self, tile: Tile) -> List[CellState]:
        dirs = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        r, c = tile.row, tile.col 
        neighbors = [(r + dr, c + dc) for (
            dr, dc) in dirs if Tile(r + dr, c + dc).is_valid()]
        return [self.board[r][c] for r, c in neighbors]
       
