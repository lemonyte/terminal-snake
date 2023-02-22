import json
import time
from dataclasses import dataclass
from enum import Enum
from random import choice

from pyco import cursor, terminal
from pyco.color import RESET, Back, Fore
from pyco.constants import ESC
from pyco.utils import getch, kbhit


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


@dataclass
class XYPair:
    x: int
    y: int

    def copy(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def __iter__(self):
        for attr in [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]:
            yield getattr(self, attr)


class Point(XYPair):
    pass


class Dimensions(XYPair):
    pass


class Field:
    def __init__(self, game: "Game", config: dict):
        self.game = game
        self.config = config
        self.snake = Snake(game, self, config)
        self.size = Dimensions(self.config['field']['width'], self.config['field']['height'])
        self.real_size = Dimensions(self.size.x * 2, self.size.y)
        self.snake_coords: list[Point] = []
        self.field = [[{} for y in range(self.size.y)] for x in range(self.size.x)]
        self.create_food()
        self.clear()
        print(f'{ESC}[8;{self.real_size.y};{self.real_size.x}t', end='')
        terminal.set_window_title("Terminal Snake Game")
        terminal.clear_screen()
        cursor.hide()

    def clear(self):
        for y in range(self.size.y):
            for x in range(self.size.x):
                self.field[x][y] = self.config['field']['empty']

    def update(self):
        self.clear()
        for x, y in self.snake_coords:
            self.field[x][y] = self.config['snake']['body']
        head = self.snake_coords[-1]
        self.field[head.x][head.y] = self.config['snake']['head']
        tail = self.snake_coords[0]
        self.field[tail.x][tail.y] = self.config['snake']['tail']
        self.field[self.food_pos.x][self.food_pos.y] = self.config['field']['food']
        rows = []
        for y in range(self.size.y):
            row = ''
            for x in range(self.size.x):
                row += (
                    (
                        getattr(Fore, self.field[x][y]['fore_color'].upper())
                        + getattr(Back, self.field[x][y]['back_color'].upper())
                        + self.field[x][y]['char']
                        + RESET
                    )
                    * 2
                )
            rows.append(row)
        self.game.add_string((0, 0), '\n'.join(rows))
        terminal.set_window_title(f"Terminal Snake Game - Score: {self.snake.length}")

    def create_food(self):
        xr = list(range(self.size.x))
        yr = list(range(self.size.y))
        while xr and yr:
            point = Point(choice(xr), choice(yr))
            if point not in self.snake_coords:
                self.food_pos = point
                return
            xr.remove(point.x)
            yr.remove(point.y)


class Snake:
    def __init__(self, game: "Game", field: Field, config: dict):
        self.game = game
        self.field = field
        self.config = config['snake']
        self.coords: list[Point] = []
        self.length = self.config['start_length']
        self.direction = Direction(self.config['start_direction'])
        self.speed = 1 / self.config['speed']
        self.is_alive = True
        self.last_move_time = -self.speed
        self.last_direction_time = 0

        start_pos = Point(self.config['start_pos']['x'], self.config['start_pos']['y'])
        if self.direction in (Direction.LEFT, Direction.RIGHT):
            self.coords = [
                Point(start_pos.x + i if self.direction == Direction.RIGHT else -i, start_pos.y)
                for i in range(self.length)
            ]
        elif self.direction in (Direction.UP, Direction.DOWN):
            self.coords = [
                Point(start_pos.x, start_pos.y + i if self.direction == Direction.DOWN else -i)
                for i in range(self.length)
            ]

    def change_direction(self, direction: Direction):
        if direction == Direction.RIGHT and self.direction == Direction.LEFT:
            return
        if direction == Direction.LEFT and self.direction == Direction.RIGHT:
            return
        if direction == Direction.UP and self.direction == Direction.DOWN:
            return
        if direction == Direction.DOWN and self.direction == Direction.UP:
            return
        if self.last_direction_time > self.last_move_time:
            return
        self.last_direction_time = time.perf_counter()
        self.direction = direction

    def loop(self, point: Point):
        looped = True
        if point.x > self.field.size.x - 1:
            point.x = 0
        elif point.x < 0:
            point.x = self.field.size.x - 1
        elif point.y > self.field.size.y - 1:
            point.y = 0
        elif point.y < 0:
            point.y = self.field.size.y - 1
        else:
            looped = False
        if looped and self.config['walls_kill']:
            self.is_alive = False
        return point

    def grow(self):
        self.length += 1
        a = self.coords[0]
        b = self.coords[1]
        tail = a.copy()
        if a.x < b.x:
            tail.x -= 1
        elif a.y < b.y:
            tail.y -= 1
        elif a.x > b.x:
            tail.x += 1
        elif a.y > b.y:
            tail.y += 1
        tail = self.loop(tail)
        self.coords.insert(0, tail)

    def move(self):
        if time.perf_counter() - self.last_move_time >= self.speed:
            head = self.coords[-1].copy()
            if self.direction == Direction.RIGHT:
                head.x += 1
            elif self.direction == Direction.LEFT:
                head.x -= 1
            elif self.direction == Direction.UP:
                head.y -= 1
            elif self.direction == Direction.DOWN:
                head.y += 1
            body = self.coords[:-1]
            self.is_alive = head not in body
            self.coords.append(self.loop(head))
            self.coords.pop(0)
            self.field.snake_coords = self.coords
            if not self.is_alive:
                self.game.end(
                    Fore.BRIGHT_RED + "GAME OVER", Fore.WHITE + "PRESS 'ESC' TO EXIT OR ANY OTHER KEY TO PLAY AGAIN"
                )
            if self.field.food_pos in self.coords:
                self.grow()
                self.field.create_food()
            if self.length >= self.field.size.x * self.field.size.y:
                self.game.end(
                    Fore.BRIGHT_GREEN + "YOU WIN", Fore.WHITE + "PRESS 'ESC' TO EXIT OR ANY OTHER KEY TO PLAY AGAIN"
                )
            self.last_move_time = time.perf_counter()


class Game:
    def __init__(self, config_path: str = 'config.json'):
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)
        self.keybinds = self.config['keybinds']
        self.running = True
        self.field = Field(self, self.config)

    def play(self):
        self.running = True
        while self.running:
            while self.field.snake.is_alive and self.running:
                key = self.get_key()
                if key:
                    key = key.lower()
                    if key in self.keybinds:
                        action = self.keybinds.get(key)
                        if action == 'exit':
                            self.exit()
                        elif action == 'pause':
                            getch()
                        else:
                            self.field.snake.change_direction(Direction(action))
                self.field.snake.move()
                self.field.update()

    def end(self, *messages: str):
        # terminal.bell()
        for i, message in enumerate(messages):
            self.add_string(
                ((self.field.real_size.x - len(message)) // 2, ((self.field.real_size.y - len(messages)) // 2) + i),
                message + RESET,
            )
        key = getch().upper()
        if key == '\x1b':
            self.exit()
        else:
            self.play()

    def exit(self):
        terminal.clear_screen()
        self.running = False

    def add_string(self, pos: tuple[int, int], string: str):
        cursor.set_position(*pos)
        print(string, end='')

    def get_key(self) -> str:
        if kbhit():
            key = getch()
            if key in ['\000', '\x00', '\xe0']:
                key = getch()
            return key


if __name__ == '__main__':
    game = Game()
    try:
        game.play()
    except KeyboardInterrupt:
        raise SystemExit
