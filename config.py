import json
from dataclasses import dataclass


@dataclass
class _ColorsConfig:
    empty: str
    food: str
    snake: str


@dataclass
class _Config:
    snake_speed: float
    loop: bool
    colors: _ColorsConfig


def load_config(config_path: str = 'config.json') -> _Config:
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


config = load_config()
