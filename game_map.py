from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
from tcod import heightmap_add # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(
        self, 
        engine: Engine,
        width: int, 
        height: int, 
        entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width,height), fill_value=False, order="F") # Tiles player can see
        self.explored = np.full((width,height), fill_value=False, order="F") # Tiles player has seen before

        self.downstairs_location = (0, 0)

        self.x_offset = 0
        self.y_offset = 0
        
    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors"""
        yield from (
            entity 
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity
            
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
            
        return None


    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map

        If a tile is in the "visible" array, draw with 'light' color
        If it isn't, but it is in the "explored" array, then use 'dark' color
        Otherwise, default is 'SHROUD'
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities in FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )

    def render_in_frame(
        self, 
        x: int, 
        y: int, 
        f_width: int, 
        f_height: int, 
        console: Console,
        title: str = "<no name>"
    ) -> None:
        """
        Render the map inside a frame of specified position and size
        The map will scroll with the player
        """

        v_width=f_width-2
        v_height=f_height-2

        console.draw_frame(
            x=x,
            y=y,
            width=f_width,
            height=f_height,
            title=title,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        x_origin = self.engine.player.x - int(v_width/2)
        if x_origin < 0:
            x_origin = 0
        y_origin = self.engine.player.y - int(v_height/2)
        if y_origin < 0:
            y_origin = 0

        x_end = x_origin + v_width 
        y_end = y_origin + v_height 

        if x_end > self.width:
            x_diff = x_end - self.width
            x_origin -= x_diff
            x_end -= x_diff

        if y_end > self.height:
            y_diff = y_end - self.height
            y_origin -= y_diff
            y_end -= y_diff
        
        self.x_offset = x - x_origin + 1
        self.y_offset = y - y_origin + 1


        print(f"player {self.engine.player.x},{self.engine.player.y}, origin {x_origin},{y_origin}, modifier {int(v_width/2)}, end {x_end}, {y_end}")
       

        slice_x = slice(x_origin, x_end-1)
        slice_y = slice(y_origin, y_end-1)

        viewport_tiles = self.tiles[slice_x, slice_y]
        viewport_visible = self.visible[slice_x, slice_y]
        viewport_explored = self.explored[slice_x, slice_y]
        
        print(f"{len(viewport_tiles)}")

        #for i in range(y_origin, y_origin+height-2):
        #    for j in range(x_origin, x_origin+width-2):
        #        console.print(x=x+j, y=y+i, string=f"{self.tiles[j, i]}")

        console.tiles_rgb[x+1:x+v_width, y+1:y+v_height] = np.select(
            condlist=[viewport_visible, viewport_explored],
            choicelist=[viewport_tiles["light"], viewport_tiles["dark"]],
            default=tile_types.SHROUD,
        )


        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities in FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x + self.x_offset, y=entity.y + self.y_offset, string=entity.char, fg=entity.color
                )
        

class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        max_monsters_per_room: int,
        max_items_per_room: int,
        current_floor: int = 0,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            max_monsters_per_room=self.max_monsters_per_room,
            max_items_per_room=self.max_items_per_room,
            engine=self.engine,
        )