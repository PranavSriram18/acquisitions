from flask import Flask, render_template, jsonify, request
from typing import List, Tuple 
from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *
from acquisitions.game_logic.board_state import *
from acquisitions.ui.ui_interface import BaseUI

class WebUI(BaseUI):
    def __init__(self):
        self.app = Flask(__name__)
        self.game_orchestrator = None
        self.setup_routes()
        self.user_input = None
        self.messages = []
        self.game_state = {}

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/get_game_state')
        def get_game_state():
            return jsonify(self.game_state)

        @self.app.route('/make_move', methods=['POST'])
        def make_move():
            self.user_input = request.json
            return jsonify({'status': 'received'})

    def run(self):
        self.app.run(debug=True, threaded=True)

    def set_game_orchestrator(self, game_orchestrator):
        self.game_orchestrator = game_orchestrator

    def render_board(self, cell_states: List[List[CellState]]):
        board_data = []
        for r in range(NUM_ROWS):
            row = []
            for c in range(NUM_COLS):
                cell_state = cell_states[r][c]
                cell = {
                    'occupied': cell_state.occupied,
                    'dead_zone': cell_state.dead_zone,
                    'content': cell_state.hotel.name[:2] if cell_state.occupied else ('ZZ' if cell_state.dead_zone else f"{r}-{c}")
                }
                row.append(cell)
            board_data.append(row)
        self.game_state['board'] = board_data

    def display_message(self, msg: str):
        self.messages.append(msg)
        self.game_state['messages'] = self.messages

    def display_property(self, player: PlayerState):
        property_info = {
            'name': player.name,
            'shares': [{'hotel': hotel.name, 'shares': num_shares} for hotel, num_shares in zip(Hotel, player.property) if num_shares > 0],
            'cash': player.money
        }
        self.game_state['property'] = property_info

    def display_event(self, player, tile, game_event):
        # TODO: Implement this method
        pass

    def get_tile_from_user(self, player: PlayerState) -> Tile:
        self.game_state['input_required'] = {
            'type': 'tile',
            'player': player.name,
            'available_tiles': [str(tile) for tile in player.tiles]
        }
        while self.user_input is None:
            pass  # Wait for user input
        tile = Tile.from_str(self.user_input['tile'])
        self.user_input = None
        return tile

    def get_hotel_from_user(self, player: PlayerState, hotels: List[Hotel]) -> Hotel:
        self.game_state['input_required'] = {
            'type': 'hotel',
            'player': player.name,
            'available_hotels': [hotel.name for hotel in hotels]
        }
        while self.user_input is None:
            pass  # Wait for user input
        hotel = Hotel.from_str(self.user_input['hotel'])
        self.user_input = None
        return hotel

    def get_buy_order_from_user(self, player: PlayerState) -> List[int]:
        self.game_state['input_required'] = {
            'type': 'buy_order',
            'player': player.name
        }
        while self.user_input is None:
            pass  # Wait for user input
        buy_order = [0] * NUM_HOTELS
        for purchase in self.user_input['buy_order']:
            hotel = Hotel.from_str(purchase['hotel'])
            quantity = purchase['quantity']
            buy_order[hotel.value] = quantity
        self.user_input = None
        return buy_order

    def get_user_liquidation_option(self, name: str, num_shares: int) -> Tuple[int, int]:
        self.game_state['input_required'] = {
            'type': 'liquidation',
            'player': name,
            'num_shares': num_shares
        }
        while self.user_input is None:
            pass  # Wait for user input
        sell = self.user_input['sell']
        twofer = self.user_input['twofer']
        self.user_input = None
        return sell, twofer

    def display_final_scores(self, players: List[PlayerState]):
        scores = [{'name': p.name, 'money': p.money} for p in players]
        rankings = sorted(scores, key=lambda x: -x['money'])
        self.game_state['final_scores'] = rankings
        self.game_state['winner'] = rankings[0]['name']
        