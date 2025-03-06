import argparse
import atexit
from typing import NoReturn

from snake import Game
from snake.auto import AutoSnake


def main() -> NoReturn:
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--speed", type=int, default=20)
    args = parser.parse_args()
    game = AutoSnake() if args.auto else Game()
    atexit.register(game.cleanup)
    game.play(speed=args.speed)


if __name__ == "__main__":
    main()
