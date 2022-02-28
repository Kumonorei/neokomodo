from __future__ import annotations
from platform import mac_ver

from typing import Tuple, TYPE_CHECKING

import color
import tcod

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()

def render_bar(
    console: Console,
    current_value: int,
    maximum_value: int,
    x: int,
    y: int,
    total_width: int,
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=1, bg=color.bar_filled)

    console.print(x=x+1, y=y, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text)

def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int. int]
) -> None:
    """
    Render the level the player is currently on, at the given location
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")

def render_character_info(
    console: Console, 
    x: int,
    y: int,
    width: int,
    height: int,
    engine: Engine,
    title: str = "Stats",
) -> None:
    """
    Render the character stats at the given location
    """
    console.draw_frame(
        x=x,
        y=y,
        width=width,
        height=height,
        title=title,
        clear=True,
        fg=(255, 255, 255),
        bg=(0, 0, 0),
    )

    x_center = int(float (x + (width/2)))
    x_left = x+2

    # Print player name
    console.print(x=x_center, y=y+2, string=engine.player.name, alignment=tcod.CENTER)

    # Display HP bar
    render_bar(
        console=console,
        current_value=(engine.player.fighter.hp),
        maximum_value=(engine.player.fighter.max_hp),
        x=x+2,
        y=y+4,
        total_width=width-4
    )

    # Print level info
    console.print(x=x_left, y=y+6, string=f"Level {engine.player.level.current_level}")
    console.print(
        x=x_left, 
        y=y+8, 
        string=f"{engine.player.level.experience_to_next_level - engine.player.level.current_xp} XP to",
    )
    console.print(x=x_left, y=y+9, string="next level")

    # Print some stats
    console.print(x=x_left, y=y+11, string=f"STR: {engine.player.fighter.power}")
    console.print(x=x_left, y=y+12, string=f"DEF: {engine.player.fighter.defense}")

    # Print current target
    render_names_at_cursor_location(
        console=console,
        x=x_left,
        y=y+15,
        engine=engine,
    )

def render_names_at_cursor_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    cursor_x, cursor_y = engine.cursor_location

    names_at_cursor_location = get_names_at_location(
        x=cursor_x, 
        y=cursor_y, 
        game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_cursor_location)