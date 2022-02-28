from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions


if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld

class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.cursor_location = (0, 0)
        self.player = player
        self.screen_width = 80
        self.screen_height= 50

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass # ignore impossible action exceptions from AI

    def update_fov(self) -> None:
        """
        Recompute the visible area based on player's field of view
        """
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8
        )
        # if a tile is "visible" it should be added to "explored"
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        #self.game_map.render(console)

        sidebar_width = 20


        self.message_log.render_in_frame(
            console=console, 
            x=sidebar_width, 
            y=42, 
            width=self.screen_width-sidebar_width, 
            height=self.screen_height-42
        )

        render_functions.render_character_info(
            console=console,
            x=0,
            y=0,
            width=sidebar_width,
            height=self.screen_height,
            engine=self,
        )

        #render_functions.render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

        self.game_map.render_in_frame(
            x=sidebar_width, 
            y=0, 
            f_width=self.screen_width-sidebar_width, 
            f_height=self.screen_height-8, 
            title=f"Dungeon Level {self.game_world.current_floor}", 
            console=console
        )
   
    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file"""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)