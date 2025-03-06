# Terminal Snake

The classic Snake game, in your terminal.

![Screenshot](https://user-images.githubusercontent.com/49930425/220823010-501ac047-e6de-40cd-b0ef-8ea8f13a8272.png)

This project was created as a demo for the [Pyco](https://github.com/lemonyte/pyco) library.

## Installation

With uv:

```shell
uv tool install git+https://github.com/lemonyte/terminal-snake
```

With pip:

```shell
pip install git+https://github.com/lemonyte/terminal-snake
```

Requires [Python 3.9](https://www.python.org/downloads/) or higher.

## Usage

### Command line

```shell
snake [--auto] [--speed <int>]
```

The `auto` flag will let the snake control itself.  
The `speed` option controls the starting speed of the snake in updates per second.

### Controls

| Key                            | Description    |
| ------------------------------ | -------------- |
| <kbd>ESC</kbd> or <kbd>q</kbd> | Exit the game  |
| <kbd>SPACE</kbd>               | Pause the game |
| <kbd>w</kbd>                   | Move up        |
| <kbd>a</kbd>                   | Move left      |
| <kbd>s</kbd>                   | Move down      |
| <kbd>d</kbd>                   | Move right     |

When resizing the terminal, pause and unpause the game with <kbd>SPACE</kbd> to update the internal pixel grid accordingly.

## Contributing

Contributions are welcome!

### Challenge

If you have an implementation for the [CPU snake player](src/snake/auto.py) that can achieve a higher score or win the game, please do open an issue or pull request.

## License

[MIT License](license.txt)
