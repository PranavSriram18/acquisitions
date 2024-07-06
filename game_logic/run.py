from acquisitions.game_logic.game_orchestrator import *

# To run: python -m acquisitions.game_logic.run from top level dir

def main():
    game = GameOrchestrator(["Player0", "Player1"], ui=TextUI())
    game.play()

if __name__=="__main__":
    main()