# Terminal Snake

The classic Snake game, in your terminal.

![Screenshot](https://user-images.githubusercontent.com/49930425/220823010-501ac047-e6de-40cd-b0ef-8ea8f13a8272.png)

## Requirements

### Python File

- [Python 3.9](https://www.python.org/downloads/) or higher
- Packages listed in [`requirements.txt`](requirements.txt)

### Windows Systems

Optional executable file for Windows users. Python and the required packages are included in the executable.

- 6 MB of free space for the executable
- 7 MB of free space for temporary files

## How To Play

Use <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd>, <kbd>D</kbd> to control the direction of the snake.
Press <kbd>ESC</kbd> to exit the game, and <kbd>SPACE</kbd> to pause the game.
Move the snake over the red apples to eat them and grow longer, and avoid hitting the snake's body.

## Configuration

The game can be configured by downloading and editing the [`config.json`](config.json) file.
The file must be in the same directory as the executable or the Python file.

|Option|Description|
|--|--|
|`snake_speed`|The speed of the snake.|
|`loop`|Whether the snake can go through walls.|
|`colors`|The [color](https://duplexes.github.io/pyco/#/ansi?id=_4-bit-colors) of each of the game elements.|

## License

[MIT License](license.txt)
