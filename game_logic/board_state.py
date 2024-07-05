
from typing import List
from collections import deque

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *

class CellState:
    """
    There are 4 basic types of state a cell can be in:
    0. Unoccupied
    1. Occupied, and not a part of any hotel
    2. Occupied, and part of one of the 7 types of hotels
    3. Occupied, and part of a Dead Zone 
    
    self.occupied is True in all cases except Case 0
    self.hotel is NO_HOTEL in all cases except case 2
    self.dead_zone is False in all cases except case 3
    """
    def __init__(self):
        self.occupied = False
        self.hotel = Hotel.NO_HOTEL
        self.dead_zone = False

    def __repr__(self):
        pass

class BoardState:
    def __init__(self):
        self.board = [[CellState() for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.hotel_sizes = [0] * NUM_HOTELS

        # TODO - auxiliary tracking structures

    def place_tile(self, tile: Tile) -> GameEvent:
        """
        pre: tile must be a valid Tile that hasn't been placed before.
        """
        cell = self.cell(tile)
        neighbor_cells = self.get_neighbor_cells(tile)
        neighbor_hotels = list(set(c.hotel for c in neighbor_cells if c.hotel != Hotel.NO_HOTEL))
        num_neighboring_hotels = len(neighbor_hotels)
        cell.occupied = True

        if num_neighboring_hotels == 0:
            # Case 0: isolated tile
            if not any(nc.occupied for nc in neighbor_cells):
                return GameEvent.NOOP  
            else:
                # Case 1: starts a chain
                return GameEvent.START_CHAIN
        elif num_neighboring_hotels == 1:
            # Case 2: absorbed into existing chain
            self.mark_recursive(tile, neighbor_hotels[0])
            return GameEvent.JOIN_CHAIN
        elif num_neighboring_hotels == 2:
            return self.execute_merger(tile, neighbor_hotels)
        else:
            # TODO - check if merge is possible
            # For now disallow multiway merges
            can_merge = False
            if can_merge:
                return GameEvent.MULTIWAY_MERGER
            
    def available_hotels(self) -> List[Hotel]:
        return [hotel for hotel in Hotel if hotel.value < Hotel.NO_HOTEL.value and self.hotel_sizes[hotel.value] == 0]
    
    def execute_merger(self, tile: Tile, neighbor_hotels: List[Hotel]):
        h0, h1 = neighbor_hotels[0], neighbor_hotels[1]
        s0, s1 = self.hotel_sizes[h0.value], self.hotel_sizes[h1.value]

        # Check if merge is possible
        can_merge = (s0 <= MAX_MERGEABLE_SIZE or s1 <= MAX_MERGEABLE_SIZE)
        if not can_merge:
            return GameEvent.DEAD_TILE
        
        # merge smaller into larger. TODO - handle equality case
        if s0 < s1:
            s0, s1 = s1, s0
            h0, h1 = h1, h0

        # h0 is now larger hotel
        self.mark_recursive(tile, h0)
        self.hotel_sizes[h1.value] = 0 
        return GameEvent.MERGER
        
    def mark_recursive(self, tile: Tile, hotel: Hotel):
        self.cell(tile).occupied = True
        q = deque([tile])
        while q:
            curr_tile = q.pop()
            self.mark_hotel(curr_tile, hotel)
            for neighbor_tile in self.get_neighbor_tiles(curr_tile):
                nc = self.cell(neighbor_tile)
                if nc.occupied and nc.hotel != hotel and not nc.dead_zone:
                    print(f"Appending {neighbor_tile}")
                    q.append(neighbor_tile)

    def mark_hotel(self, tile: Tile, hotel: Hotel):
        print(f"Marking tile {tile} with hotel {hotel}")
        self.cell(tile).hotel = hotel
        self.hotel_sizes[hotel.value] += 1
    
    def mark_dead_tile(self, tile: Tile):
        cell = self.cell(tile)
        cell.occupied = True
        cell.hotel = Hotel.NO_HOTEL
        cell.dead_zone = True

    def get_neighbor_tiles(self, tile: Tile) -> List[Tile]:
        dirs = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        r, c = tile.row, tile.col 
        neighbor_tiles = [Tile(r + dr, c + dc) for (dr, dc) in dirs]
        return [nt for nt in neighbor_tiles if nt.is_valid()]
        
    def get_neighbor_cells(self, tile: Tile) -> List[CellState]:
        return [self.cell(nt) for nt in self.get_neighbor_tiles(tile)]
       
    def cell(self, tile: Tile):
        """Get the cell state for the given tile."""
        return self.board[tile.row][tile.col]
