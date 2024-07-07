from acquisitions.game_logic.game_orchestrator import *

# To run: python -m acquisitions.game_logic.run from top level dir

def main(player_names: List[str], use_web_ui: bool = False):
    if use_web_ui:
        ui = WebUI()
    else:
        ui = TextUI()
    game = GameOrchestrator(player_names, ui)
    game.play()

if __name__=="__main__":
    main(["Alice", "Bob"], False)