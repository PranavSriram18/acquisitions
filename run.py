from acquisitions.server.server import GameServer

# To run: python -m acquisitions.run from top level dir

def main():
    server = GameServer()
    print("Starting Acquisitions game server...")
    print("Open http://127.0.0.1:5000 in your web browser to create or join a game.")
    server.run()

if __name__ == "__main__":
    main()