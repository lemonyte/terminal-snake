from dataclasses import dataclass
from enum import Enum


class Event(Enum):
    EXIT = '\x1b'
    PAUSE = ' '
    UP = 'w'
    DOWN = 's'
    LEFT = 'a'
    RIGHT = 'd'


@dataclass
class Point:
    x: int
    y: int

    def copy(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def __iter__(self):
        for attr in [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith('__')]:
            yield getattr(self, attr)
