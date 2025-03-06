import atexit
import sys
from typing import NoReturn

from snake import Game
from snake.auto import AutoSnake


def main() -> NoReturn:
    game = AutoSnake() if "--auto" in sys.argv else Game()
    atexit.register(game.cleanup)
    game.play()


if __name__ == "__main__":
    main()
