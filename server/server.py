import asyncio
import logging
import os
import threading
import uuid

from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room

from acquisitions.game_logic.game_orchestrator import GameOrchestrator
from acquisitions.ui.web_ui import WebUI

logging.basicConfig(level=logging.DEBUG)

class GameServer:
    def __init__(self):
        template_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'ui', 'templates'))
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.config['SECRET_KEY'] = 'your-secret-key'  # TODO - change this
        self.socketio = SocketIO(self.app, async_mode='threading')
        self.games = {}  # in-memory table to store active games
        self.loop = asyncio.new_event_loop()
        self.setup_routes()

        # Start the event loop in a separate thread
        self.loop_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.loop_thread.start()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('lobby.html')

        @self.app.route('/create_game')
        def create_game():
            game_id = str(uuid.uuid4())[:8]  # Use first 8 characters for brevity
            self.games[game_id] = GameOrchestrator(
                [WebUI(game_id, self.socketio, self.loop) for _ in range(2)]
            )
            join_url = f"{request.host_url}join_game/{game_id}"
            return render_template(
                'game_created.html', game_id=game_id, join_url=join_url)

        @self.app.route('/join_game/<game_id>')
        def join_game(game_id):
            if game_id not in self.games:
                return "error", 404  # TODO
            game_orchestrator = self.games[game_id]
            player_name = f"Player{len(game_orchestrator.players)}"
            return render_template('game.html', game_id=game_id, player_name=player_name)


        @self.socketio.on('join')
        def on_join(data):
            logging.debug(f"Join event received: {data}")
            game_id = data['game_id']
            player = data['player']
            join_room(game_id)
            game_orchestrator = self.games[game_id]
            logging.debug(f"Adding {player} to game {game_id} ...")
            game_orchestrator.add_player(player)
            logging.debug(f"Added player {player} to game {game_id}!")
            if game_orchestrator.is_ready():
                logging.debug(f"Game {game_id} is ready to start")
                logging.debug(f"Starting game orchestrator for game {game_id}")
                asyncio.run_coroutine_threadsafe(self.run_game(game_orchestrator), self.loop)

        @self.socketio.on('make_move')
        def on_move(data):
            game_id = data['game_id']
            move = data['move']
            game_orchestrator = self.games[game_id]
            game_orchestrator.receive_input(move)

    async def run_game(self, game_orchestrator):
        logging.debug(f"Running game orchestrator for game {game_orchestrator}")
        logging.debug("Starting play coroutine")
        await game_orchestrator.play()
        logging.debug("Finished play coroutine")

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self):
        logging.info("Starting server")
        self.socketio.run(self.app, debug=True, use_reloader=False)

def create_app():
    server = GameServer()
    return server.app, server.socketio

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app)
