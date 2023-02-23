import json
from dataclasses import dataclass


@dataclass
class _ColorsConfig:
    empty: str = 'black'
    food: str = 'bright_red'
    snake: str = 'bright_green'


@dataclass
class _Config:
    snake_speed: int = 50
    loop: bool = True
    colors: _ColorsConfig = _ColorsConfig()


def load_config(config_path: str = 'config.json') -> _Config:
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)

        return _Config(
            snake_speed=config_data['snake_speed'],
            loop=config_data['loop'],
            colors=_ColorsConfig(
                empty=config_data['colors']['empty'],
                food=config_data['colors']['food'],
                snake=config_data['colors']['snake'],
            ),
        )
    except (FileNotFoundError, KeyError):
        return _Config()


config = load_config()
