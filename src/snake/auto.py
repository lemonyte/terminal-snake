import sys

from snake import Event, Game

DIRECTIONS = {
    Event.UP: (0, -1),
    Event.DOWN: (0, 1),
    Event.LEFT: (-1, 0),
    Event.RIGHT: (1, 0),
}


class AutoSnake(Game):
    def pause(self) -> None:
        while True:
            event = super().get_event()
            if event in (Event.EXIT, Event.QUIT):
                self.exit()
            if event is Event.PAUSE:
                self.stage.update_size()
                break

    def check_move(self, event: Event, /) -> float:
        if event not in DIRECTIONS:
            return sys.maxsize
        direction = DIRECTIONS[event]
        next_pos = self.snake.head
        steps = 0
        while True:
            next_pos = (next_pos[0] + direction[0], next_pos[1] + direction[1])
            if next_pos == self.stage.food_pos:
                return sys.maxsize
            if (
                not (0 <= next_pos[0] < self.stage.width)
                or not (0 <= next_pos[1] < self.stage.height)
                or next_pos in self.snake.points
            ):
                return steps
            steps += 1

    def get_event(self) -> "Event | None":
        if event := super().get_event():
            return event
        head = self.snake.head
        direction = self.snake.direction
        if self.stage.food_pos[0] > head[0] and direction is not Event.RIGHT:
            event = Event.RIGHT
        if self.stage.food_pos[0] < head[0] and direction is not Event.LEFT:
            event = Event.LEFT
        if self.stage.food_pos[1] > head[1] and direction is not Event.DOWN:
            event = Event.DOWN
        if self.stage.food_pos[1] < head[1] and direction is not Event.UP:
            event = Event.UP
        event = event or direction
        if self.check_move(event) < 1:
            return max(DIRECTIONS, key=self.check_move)
        return event


if __name__ == "__main__":
    game = AutoSnake()
    game.play()
