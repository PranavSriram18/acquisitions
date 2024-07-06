
from typing import List, Tuple
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
        self.hotel_sizes = [0] * (NUM_HOTELS + 1)

    def place_tile(self, tile: Tile) -> GameEvent:
        """
        pre: tile must be a valid Tile that hasn't been placed before.
        """
        cell = self.cell(tile)
        neighbor_cells = self.get_neighbor_cells(tile)
        neighbor_hotels = self.get_neighbor_hotels(tile)
        num_neighbor_hotels = len(neighbor_hotels)
        cell.occupied = True

        if num_neighbor_hotels == 0:
            # Case 0: isolated tile (all neighbors empty or dead)
            if not any(nc.occupied and not nc.dead_zone for nc in neighbor_cells):
                return GameEvent.NOOP
            else:
                # Case 1: possibly starts a chain
                return GameEvent.START_CHAIN
        elif num_neighbor_hotels == 1:
            # Case 2: absorbed into existing chain
            self.mark_recursive(tile, neighbor_hotels[0])
            return GameEvent.JOIN_CHAIN
        else:
            return GameEvent.MERGER
            
    def available_hotels(self) -> List[Hotel]:
        return [hotel for hotel in Hotel if hotel.value < Hotel.NO_HOTEL.value and self.hotel_sizes[hotel.value] == 0]
    
    def check_merger(self, tile: Tile) -> Tuple[bool, List[Hotel], List[Hotel]]:
        neighbor_hotels = self.get_neighbor_hotels(tile)
        sizes = [self.hotel_sizes[nh.value] for nh in neighbor_hotels]
        can_merge = sizes[1] <= MAX_MERGEABLE_SIZE
        majority_options = [h for (h, sz) in zip(neighbor_hotels, sizes) if sz == sizes[0]]
        return can_merge, majority_options, neighbor_hotels


    def execute_merger(self, tile: Tile, hotels: List[Hotel]):
        """
        pre: check_merger has been run and can_merge is True.
        pre: hotels sorted in descending order of size, with tiebreaks
        selected by player.
        """
        self.mark_recursive(tile, hotels[0])
        for i in range(1, len(hotels)):
            self.hotel_sizes[hotels[i].value] = 0 
        
    def mark_recursive(self, tile: Tile, hotel: Hotel):
        """
        Mark the given tile as belonging to the given hotel, and recursively
        map all non-deadzone tiles it is connected to as also belonging to the
        given hotel. 
        """
        self.cell(tile).occupied = True
        q = deque([tile])
        while q:
            curr_tile = q.pop()
            self.mark_hotel(curr_tile, hotel)
            for neighbor_tile in self.get_neighbor_tiles(curr_tile):
                nc = self.cell(neighbor_tile)
                if nc.occupied and nc.hotel != hotel and not nc.dead_zone:
                    q.append(neighbor_tile)

    def mark_hotel(self, tile: Tile, hotel: Hotel):
        """Mark the given tile as belonging to the given hotel."""
        self.cell(tile).hotel = hotel
        self.hotel_sizes[hotel.value] += 1
    
    def mark_dead_tile(self, tile: Tile):
        """Mark the given tile as belonging to a dead zone."""
        cell = self.cell(tile)
        cell.occupied = True
        cell.hotel = Hotel.NO_HOTEL
        cell.dead_zone = True

    def get_neighbor_tiles(self, tile: Tile) -> List[Tile]:
        """Get the tiles neighboring the given tile."""
        dirs = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        r, c = tile.row, tile.col 
        neighbor_tiles = [Tile(r + dr, c + dc) for (dr, dc) in dirs]
        return [nt for nt in neighbor_tiles if nt.is_valid()]
        
    def get_neighbor_cells(self, tile: Tile) -> List[CellState]:
        """Get the cell states for the tiles neighboring the given tile."""
        return [self.cell(nt) for nt in self.get_neighbor_tiles(tile)]
    
    def get_neighbor_hotels(self, tile: Tile) -> List[Hotel]:
        neighbor_cells = self.get_neighbor_cells(tile)
        neighbor_hotels = list(set(c.hotel for c in neighbor_cells if c.hotel != Hotel.NO_HOTEL))
        neighbor_hotels.sort(key=lambda x: -self.hotel_sizes[x.value])
        return neighbor_hotels
       
    def cell(self, tile: Tile):
        """Get the cell state for the given tile."""
        return self.board[tile.row][tile.col]
