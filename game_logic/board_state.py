
from typing import List, Tuple
from collections import deque

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *

class CellState:
    """
    Represents the state of an individual tile on the Board.
    There are 4 basic types of state a cell can be in:
    0. Unoccupied
    1. Occupied, and not a part of any hotel
    2. Occupied, and part of one of the 7 types of hotels
    3. Occupied, and part of a Dead Zone
    """
    def __init__(self, occupied=False, hotel=Hotel.NO_HOTEL, dead_zone=False, tile=None):
        self.occupied = occupied  # True in all cases except Case 0
        self.hotel = hotel  # NO_HOTEL in all cases except Case 2
        self.dead_zone = dead_zone  # False in all cases except Case 3
        self.tile = tile

    def __str__(self):
        if not self.occupied:
            return str(self.tile)
        elif self.dead_zone:
            return "ZZ"
        elif self.hotel != Hotel.NO_HOTEL:
            return self.hotel.name[0:2]
        else:
            return "XX"
        
    def __repr__(self):
        return self.__str__()
        

class BoardState:
    """
    Maintains the state of the Board during the game.
    The state of the Board is defined by a grid of CellStates, plus an 
    auxiliary structure for tracking sizes of hotels on the board.
    """
    def __init__(self):
        self.board = [[CellState(
            tile=Tile(r, c)) for c in range(NUM_COLS)] for r in range(NUM_ROWS)]
        self.hotel_sizes = [0] * (NUM_HOTELS + 1)

    def place_tile(self, tile: Tile) -> GameEvent:
        """
        Core update to board state that occurs once per turn.
        pre: tile must be a valid Tile that hasn't been placed before.
        There are 4 cases:
        0. Isolated tile (all neighbors empty or dead)
        1. Possibly starts a chain
        2. Absorbed into existing chain
        3. Merger
        """
        cell = self.cell(tile)
        neighbor_cells = self.get_neighbor_cells(tile)
        neighbor_hotels = self.get_neighbor_hotels(tile)
        num_neighbor_hotels = len(neighbor_hotels)
        cell.occupied = True
        if num_neighbor_hotels == 0:
            if not any(nc.occupied and not nc.dead_zone for nc in neighbor_cells):
                return GameEvent.NOOP  # Case 0
            else:
                return GameEvent.START_CHAIN  # Case 1
        elif num_neighbor_hotels == 1:
            self.mark_recursive(tile, neighbor_hotels[0])
            return GameEvent.JOIN_CHAIN  # Case 2
        else:
            return GameEvent.MERGER  # Case 3
        
    def hotels_on_board(self) -> List[Hotel]:
        """Returns a list of hotels present on the Board."""
        return [h for h in Hotel if h.value < NUM_HOTELS and self.hotel_sizes[h.value] > 0]
            
    def available_hotels(self) -> List[Hotel]:
        """Returns a list of hotels not present on the Board."""
        return [h for h in Hotel if h.value < NUM_HOTELS and self.hotel_sizes[h.value] == 0]
    
    def check_merger(self, tile: Tile) -> Tuple[bool, List[Hotel], List[Hotel]]:
        """
        Checks if a given Tile causes a merger between two or more hotels.
        Returns:
        can_merge: Whether a merger is caused
        majority_options: Which of the merged hotels is larger (can be multiple
        in case of a tie)
        neighbor_hotels: The Hotels in neighboring Tiles
        """
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
        cell.tile = tile

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
        """
        Returns a list of hotels neighboring the given Tile, in descending 
        order of size.
        """
        neighbor_cells = self.get_neighbor_cells(tile)
        neighbor_hotels = list(set(c.hotel for c in neighbor_cells if c.hotel != Hotel.NO_HOTEL))
        neighbor_hotels.sort(key=lambda x: -self.hotel_sizes[x.value])
        return neighbor_hotels
       
    def cell(self, tile: Tile):
        """Get the cell state for the given tile."""
        return self.board[tile.row][tile.col]
