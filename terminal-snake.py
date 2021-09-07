import os
import time
import json
from random import randint
from pyco.color import Fore, Back, RESET
from pyco import terminal, cursor
from pyco.constants import ESC
from pyco.utils import getch, kbhit


class Keys:
    RIGHT = 'M'
    LEFT = 'K'
    UP = 'H'
    DOWN = 'P'
    SPACE = ' '
    ESC = ESC


class Window:
    @staticmethod
    def AddString(pos: tuple[int], string: str):
        cursor.set_position(*pos)
        print(string)

    @staticmethod
    def GetKey() -> str:
        if kbhit():
            key = getch()
            if key in [b'\000', b'\x00', b'\xe0']:
                key = getch()

            return str(key, 'utf-8')


class Field:
    def __init__(self, config: dict):
        self.config = config
        self.size = (config['field']['width'], config['field']['height'])
        self.snakeCoords = []
        self.Generate()
        self.CreateFood()

    def Generate(self):
        self.field = [[self.config['field']['empty'] for x in range(self.size[1])] for y in range(self.size[0])]
        # self.field = [[self.config['field']['border']['corner'] if (x == 0 and y == 0) or (x == 0 and y == self.size[1] - 1) or (x == self.size[0] -1 and y == 0) and (x == self.size[0] -1 and y == self.size[1] - 1) else self.config['field']['empty'] for x in range(self.size[1])] for y in range(self.size[0])]

    def Clear(self):
        self.field = [[x if x != self.config['snake']['head'] and x != self.config['snake']['body'] and x != self.config['snake']['tail'] else self.config['field']['empty'] for x in y] for y in self.field]
        # self.field = [[self.config['field']['empty'] for x in y] for y in self.field]

    def Render(self):
        self.Clear()
        # Window.AddString((0, 1), f"Score: {len(self.snakeCoords)}")
        for x, y in self.snakeCoords:
            self.field[x][y] = self.config['snake']['body']

        head = self.snakeCoords[-1]
        self.field[head[0]][head[1]] = self.config['snake']['head']
        for y in range(self.size[1]):
            row = ''
            for x in range(self.size[0]):
                row += (getattr(Fore, self.field[x][y]['fore_color']) + getattr(Back, self.field[x][y]['back_color']) + self.field[x][y]['char'] + RESET) * 2

            Window.AddString((0, y + 1), row)

    def CreateFood(self):
        while True:
            self.foodPos = [randint(0, self.size[0] - 1), randint(0, self.size[1] - 1)]
            if self.foodPos not in self.snakeCoords:
                self.field[self.foodPos[0]][self.foodPos[1]] = self.config['field']['food']
                break


class Snake:
    def __init__(self, field: Field, config: dict):
        self.field = field
        self.config = config
        self.pos = [config['pos']['x'], config['pos']['y']]
        self.length = config['length']
        self.direction = getattr(Keys, config['direction'])
        self.speed = 1 / config['speed']
        self.isAlive = True
        self.lastMoveTime = -self.speed
        self.lastDirectionTime = 0
        if self.direction == Keys.RIGHT or self.direction == Keys.LEFT:
            self.coords = [[self.pos[0] + i if self.direction == Keys.RIGHT else -i, self.pos[1]] for i in range(self.length)]

        elif self.direction == Keys.UP or self.direction == Keys.DOWN:
            self.coords = [[self.pos[0], self.pos[1] + i if self.direction == Keys.DOWN else -i] for i in range(self.length)]

    def SetDirection(self, direction: Keys):
        if direction == Keys.RIGHT and self.direction == Keys.LEFT: return
        if direction == Keys.LEFT and self.direction == Keys.RIGHT: return
        if direction == Keys.UP and self.direction == Keys.DOWN: return
        if direction == Keys.DOWN and self.direction == Keys.UP: return
        if self.lastDirectionTime > self.lastMoveTime: return
        self.lastDirectionTime = time.perf_counter()

        self.direction = direction

    def Loop(self, point):
        looped = False
        if point[0] > self.field.size[0] - 1:
            looped = True
            point[0] = 0

        elif point[0] < 0:
            looped = True
            point[0] = self.field.size[0] - 1

        elif point[1] > self.field.size[1] - 1:
            looped = True
            point[1] = 0

        elif point[1] < 0:
            looped = True
            point[1] = self.field.size[1] - 1

        if self.config['walls_kill'] and looped:
            self.isAlive = False

        return point

    def IsAlive(self):
        head = self.coords[-1]
        body = self.coords[:-1]
        self.isAlive = head not in body

    def Grow(self):
        self.length += 1
        a = self.coords[0]
        b = self.coords[1]
        tail = a[:]
        if a[0] < b[0]:
            tail[0] -= 1

        elif a[1] < b[1]:
            tail[1] -= 1

        elif a[0] > b[0]:
            tail[0] += 1

        elif a[1] > b[1]:
            tail[1] += 1

        tail = self.Loop(tail)
        self.coords.insert(0, tail)

    def Move(self):
        if time.perf_counter() - self.lastMoveTime >= self.speed:
            head = self.coords[-1][:]
            if self.direction == Keys.RIGHT:
                head[0] += 1

            elif self.direction == Keys.LEFT:
                head[0] -= 1

            elif self.direction == Keys.UP:
                head[1] -= 1

            elif self.direction == Keys.DOWN:
                head[1] += 1

            self.IsAlive()
            head = self.Loop(head)
            del self.coords[0]
            self.coords.append(head)
            self.field.snakeCoords = self.coords
            if not self.isAlive:
                message = "GAME OVER"
                Window.AddString((self.field.size[0] - (len(message) // 2), self.field.size[1] // 2), Fore.BRIGHT_RED + message + RESET)
                getch()
                exit()

            if self.field.foodPos in self.coords:
                # print(BEL, end='')
                self.Grow()
                self.field.CreateFood()

            self.lastMoveTime = time.perf_counter()


def Main():
    # try:
    with open('config.json', 'r') as configFile:
        config = json.load(configFile)

    # except:
    #     pass

    terminal.set_window_title("Terminal Snake Game")
    terminal.clear_screen(2)
    cursor.hide()
    os.system(f"mode con: cols={config['window']['width']} lines={config['window']['height']}")
    field = Field(config)
    snake = Snake(field, config['snake'])
    while True:
        key = Window.GetKey()
        if key in [Keys.RIGHT, Keys.LEFT, Keys.UP, Keys.DOWN]:
            snake.SetDirection(key)

        elif key == Keys.ESC:
            exit()

        elif key == Keys.SPACE:
            getch()

        snake.Move()
        field.Render()
        terminal.set_window_title(f"Terminal Snake Game - Score: {snake.length}")


if __name__ == '__main__':
    Main()
