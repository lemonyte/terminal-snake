import random
import sys
import time
from collections import defaultdict
from enum import Enum
from typing import NoReturn

from pyco import cursor, terminal
from pyco.color import RESET, Back, Fore
from pyco.utils import getch, kbhit

Point = tuple[int, int]


class Event(Enum):
    EXIT = "\x1b"
    QUIT = "q"
    PAUSE = " "
    UP = "w"
    DOWN = "s"
    LEFT = "a"
    RIGHT = "d"


class Color(Enum):
    EMPTY = "black"
    SNAKE = "bright_green"
    FOOD = "bright_red"


class Snake:
    def __init__(self, *, length: int = 3, speed: int = 20) -> None:
        self.speed = speed
        self.length = length
        self.direction = Event.RIGHT
        self.is_alive = True
        self.points = []
        self.reset()

    @property
    def head(self) -> Point:
        return self.points[-1]

    @head.setter
    def head(self, point: Point, /) -> None:
        self.points[-1] = point

    @property
    def tail(self) -> Point:
        return self.points[0]

    @tail.setter
    def tail(self, point: Point, /) -> None:
        self.points[0] = point

    def reset(self) -> None:
        self.length = 3
        self.direction = Event.RIGHT
        self.is_alive = True
        self.points = [(x, 0) for x in range(self.length)]

    def change_direction(self, direction: Event, /) -> None:
        if (
            (direction is Event.RIGHT and self.direction is Event.LEFT)
            or (direction is Event.LEFT and self.direction is Event.RIGHT)
            or (direction is Event.UP and self.direction is Event.DOWN)
            or (direction is Event.DOWN and self.direction is Event.UP)
        ):
            return
        self.direction = direction

    def grow(self, point: Point, /) -> None:
        self.length += 1
        self.points.insert(0, point)
        terminal.set_window_title(f"Terminal Snake - Score: {self.length}")

    def move(self) -> None:
        head = self.head
        if self.direction is Event.RIGHT:
            new_head = (head[0] + 1, head[1])
        elif self.direction is Event.LEFT:
            new_head = (head[0] - 1, head[1])
        elif self.direction is Event.UP:
            new_head = (head[0], head[1] - 1)
        else:
            new_head = (head[0], head[1] + 1)
        self.points.append(new_head)
        self.points.pop(0)


class Stage:
    def __init__(self, *, snake: Snake) -> None:
        self.snake = snake
        self.pixels: dict[Point, Color] = defaultdict(lambda: Color.EMPTY)
        self.food_pos: Point = (0, 0)
        self.width = 0
        self.height = 0
        self.update_size()

    def update_size(self) -> None:
        terminal_size = terminal.get_size()
        self.width = terminal_size.columns
        self.height = terminal_size.lines * 2

    def color_code(self, color: Color, point: Point, /) -> str:
        return getattr(Fore if point[1] % 2 == 0 else Back, color.value.upper())

    def render_point(self, point: Point) -> None:
        y1 = point[1] - 1 if point[1] % 2 != 0 else point[1]
        y2 = point[1] if point[1] % 2 != 0 else point[1] + 1
        p1 = (point[0], y1)
        p2 = (point[0], y2)
        fore = self.color_code(self.pixels[p1], p1)
        back = self.color_code(self.pixels[p2], p2)
        x, y = point[0], point[1] // 2
        cursor.set_position(x + 1, y + 1)
        sys.stdout.write(fore + back + "▀")

    def reset(self) -> None:
        cursor.set_position(1, 1)
        sys.stdout.write(self.color_code(Color.EMPTY, (0, 0)) + self.color_code(Color.EMPTY, (0, 1)))
        sys.stdout.write(("▀" * self.width + "\n") * (self.height // 2))
        self.create_food()
        self.snake.reset()

    def create_food(self) -> None:
        x_range = list(range(self.width))
        y_range = list(range(self.height))
        while x_range and y_range:
            point = (random.choice(x_range), random.choice(y_range))
            if point not in self.snake.points:
                self.food_pos = point
                self.pixels[self.food_pos] = Color.FOOD
                self.render_point(self.food_pos)
                return
            x_range.remove(point[0])
            y_range.remove(point[1])

    def update(self) -> None:
        prev_tail = self.snake.tail
        prev_head = self.snake.head
        self.snake.move()
        head = self.snake.head
        if (
            head in self.snake.points[:-1]
            or head[0] < 0
            or head[0] >= self.width
            or head[1] < 0
            or head[1] >= self.height
        ):
            self.snake.is_alive = False
            self.pixels[prev_head] = Color.FOOD
            self.render_point(prev_head)
        else:
            self.pixels[head] = Color.SNAKE
            self.render_point(head)
            if self.food_pos in self.snake.points:
                self.snake.grow(prev_tail)
                self.create_food()
            elif prev_tail not in self.snake.points:
                self.pixels[prev_tail] = Color.EMPTY
                self.render_point(prev_tail)
        sys.stdout.flush()


class Game:
    def __init__(self) -> None:
        self.snake = Snake()
        self.stage = Stage(snake=self.snake)

    def get_event(self) -> "Event | None":
        key = ""
        while kbhit():
            key += getch()
        if key:
            try:
                return Event(key.lower())
            except ValueError:
                return None
        return None

    def handle_event(self, event: "Event | None", /) -> None:
        if event in (Event.EXIT, Event.QUIT):
            self.exit()
        elif event is Event.PAUSE:
            self.pause()
        elif event:
            self.snake.change_direction(event)

    def pause(self) -> None:
        while True:
            event = self.get_event()
            if event in (Event.EXIT, Event.QUIT):
                self.exit()
            if event is Event.PAUSE:
                self.stage.update_size()
                break

    def draw(self, string: str, /, *, x: int = 1, y: int = 1) -> None:
        cursor.set_position(x, y)
        sys.stdout.write(string)
        sys.stdout.flush()

    def reset(self) -> None:
        self.stage.update_size()
        self.stage.reset()
        terminal.set_window_title(f"Terminal Snake - Score: {self.snake.length}")

    def cleanup(self) -> None:
        cursor.show()
        terminal.main_screen_buffer()

    def exit(self) -> NoReturn:
        self.cleanup()
        raise SystemExit

    def end(self, *messages: str) -> None:
        for i, message in enumerate(messages):
            self.draw(
                f"{getattr(Back, Color.EMPTY.value.upper())}{message}{RESET}\n",
                x=(self.stage.width - len(message)) // 2,
                y=((self.stage.height // 2 - len(messages)) // 2) + i,
            )
        self.pause()
        self.reset()

    def play(self, *, speed: int = 20) -> NoReturn:
        terminal.alt_screen_buffer()
        cursor.hide()
        self.snake.speed = speed
        self.reset()
        try:
            while True:
                if self.snake.speed:
                    time.sleep(1 / self.snake.speed)
                self.handle_event(self.get_event())
                self.stage.update()
                if self.snake.length >= self.stage.width * self.stage.height:
                    self.end(
                        f"{Fore.BRIGHT_GREEN}YOU WIN",
                        "PRESS 'ESC' TO EXIT",
                        "OR 'SPACE' TO PLAY AGAIN",
                    )
                if not self.snake.is_alive:
                    self.end(
                        f"{Fore.BRIGHT_RED}GAME OVER",
                        "PRESS 'ESC' TO EXIT",
                        "OR 'SPACE' TO PLAY AGAIN",
                    )
        except KeyboardInterrupt:
            self.exit()
