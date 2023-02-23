import random
import time
from typing import Optional

from pyco import cursor, terminal
from pyco.color import RESET, Back, Fore
from pyco.utils import getch, kbhit

from classes import Event, Point
from config import config


class Field:
    def __init__(self):
        self.colors: list[list[str]] = []
        self.food_pos = Point(0, 0)
        self.snake = Snake(self)
        self.text = ''
        self.reset()

    @property
    def width(self) -> int:
        return terminal.get_size().columns

    @property
    def height(self) -> int:
        return terminal.get_size().lines * 2

    def reset(self):
        self.clear()
        self.create_food()
        self.snake.reset()

    def clear(self):
        self.colors = [[config.colors.empty for y in range(self.height)] for x in range(self.width)]

    def create_food(self):
        x_range = list(range(self.width))
        y_range = list(range(self.height))
        while x_range and y_range:
            point = Point(random.choice(x_range), random.choice(y_range))
            if point not in self.snake.coords:
                self.food_pos = point
                return
            x_range.remove(point.x)
            y_range.remove(point.y)

    def update(self):
        self.clear()
        for x, y in self.snake.coords:
            self.colors[x][y] = config.colors.snake
        self.colors[self.food_pos.x][self.food_pos.y] = config.colors.food
        rows = []
        for y in range(0, self.height, 2):
            row = ''
            for x in range(self.width):
                row += (
                    getattr(Fore, self.colors[x][y].upper())
                    + (getattr(Back, self.colors[x][y + 1].upper()) if y + 1 < self.height else '')
                    + '▀'
                    + str(RESET)
                )
            rows.append(row)
        self.text = '\n'.join(rows)


class Snake:
    def __init__(self, field: Field):
        self.field = field
        self.speed = config.snake_speed
        self.length = 3
        self.direction = Event.RIGHT
        self._is_alive = True
        self.coords = [Point(x, 0) for x in range(self.length)]
        self.reset()

    @property
    def is_alive(self) -> bool:
        if self.coords[-1] in self.coords[:-1]:
            self._is_alive = False
        return self._is_alive

    def reset(self):
        self.speed = config.snake_speed
        self.length = 3
        self.direction = Event.RIGHT
        self._is_alive = True
        self._last_direction_time = 0
        self.coords = [Point(x, 0) for x in range(self.length)]

    def change_direction(self, direction: Event):
        if direction is Event.RIGHT and self.direction is Event.LEFT:
            return
        if direction is Event.LEFT and self.direction is Event.RIGHT:
            return
        if direction is Event.UP and self.direction is Event.DOWN:
            return
        if direction is Event.DOWN and self.direction is Event.UP:
            return
        self.direction = direction

    def loop(self, point: Point) -> Point:
        looped = True
        if point.x > self.field.width - 1:
            point.x = 0
        elif point.x < 0:
            point.x = self.field.width - 1
        elif point.y > self.field.height - 1:
            point.y = 0
        elif point.y < 0:
            point.y = self.field.height - 1
        else:
            looped = False
        if looped and not config.loop:
            self._is_alive = False
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
        self.speed *= 1.5
        terminal.set_window_title(f"Terminal Snake - Score: {self.field.snake.length}")

    def move(self):
        head = self.coords[-1].copy()
        if self.direction is Event.RIGHT:
            head.x += 1
        elif self.direction is Event.LEFT:
            head.x -= 1
        elif self.direction is Event.UP:
            head.y -= 1
        elif self.direction is Event.DOWN:
            head.y += 1
        self.coords.append(self.loop(head))
        self.coords.pop(0)
        if self.field.food_pos in self.coords:
            self.grow()
            self.field.create_food()
        self.field.update()


class Game:
    def __init__(self):
        self.field = Field()
        self._last_update_time = time.perf_counter()
        self._last_direction_time = time.perf_counter()
        terminal.set_window_title(f"Terminal Snake - Score: {self.field.snake.length}")
        terminal.clear_screen()
        cursor.hide()

    def play(self):
        try:
            while True:
                event = self.get_event()
                if event is Event.EXIT:
                    self.exit()
                elif event is Event.PAUSE:
                    getch()
                elif event is not None and self._last_direction_time < self._last_update_time:
                    self.field.snake.change_direction(event)
                    self._last_direction_time = time.perf_counter()
                if time.perf_counter() - self._last_update_time >= 1 / self.field.snake.speed:
                    self.field.snake.move()
                    self.display_string((0, 0), self.field.text)
                    if self.field.snake.length >= self.field.width * self.field.height:
                        self.end(
                            str(Fore.BRIGHT_GREEN) + "YOU WIN",
                            "PRESS 'ESC' TO EXIT",
                            "OR ANY OTHER KEY TO PLAY AGAIN",
                        )
                    if not self.field.snake.is_alive:
                        self.end(
                            str(Fore.BRIGHT_RED) + "GAME OVER",
                            "PRESS 'ESC' TO EXIT",
                            "OR ANY OTHER KEY TO PLAY AGAIN",
                        )
                    self._last_update_time = time.perf_counter()
        except KeyboardInterrupt:
            self.exit()

    def reset(self):
        self.field.reset()

    def exit(self):
        terminal.clear_screen()
        cursor.set_position(0, 0)
        cursor.show()
        raise SystemExit

    def display_string(self, pos: tuple[int, int], string: str):
        cursor.set_position(*pos)
        for line in string.splitlines(keepends=True):
            print(line, end='', flush=True)

    def get_event(self) -> Optional[Event]:
        key = ''
        while kbhit():
            key += getch()
        if key:
            key = key.lower()
            try:
                return Event(key)
            except ValueError:
                return None

    def end(self, *messages: str):
        for i, message in enumerate(messages):
            self.display_string(
                (((self.field.width - len(message)) // 2), ((self.field.height // 2 - len(messages)) // 2) + i),
                getattr(Back, config.colors.empty.upper()) + message + str(RESET) + '\n',
            )
        key = getch()
        if key == Event.EXIT.value:
            self.exit()
        else:
            self.reset()


if __name__ == '__main__':
    Game().play()
