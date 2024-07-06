from acquisitions.game_logic.board_state import *

"""
Basic text rendering of board in terminal.
"""
def render_board_text(cell_states: List[List[CellState]]):
    print("Current board: \n\n")
    for r in range(NUM_ROWS):
        for c in range(NUM_COLS):
            cell_state = cell_states[r][c]
            if cell_state.occupied:
                print(cell_state.hotel, end=" ")
            else:
                print(Tile(r, c), end=" ")
        print("\n")
