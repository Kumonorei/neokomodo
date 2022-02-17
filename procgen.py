from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property 
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def room(self) -> Tuple[slice, slice]:
        """Return the full room including wall space"""
        return slice(self.x1, self.x2), slice(self.y1, self.y2)

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2d array index"""
        return slice(self.x1 + 1, self.x2 -1), slice(self.y1 + 1, self.y2 -1)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps another RectangularRoom"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def place_entities(
    room: RectangularRoom,
    dungeon: GameMap,
    maximum_monsters: int,
    maximum_items: int,
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)
    number_of_items = random.randint(0, maximum_items)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 2)
        y = random.randint(room.y1 + 1, room.y2 - 2)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            monster_chance = random.random()
            if monster_chance < 0.8:
                entity_factories.menace.spawn(dungeon, x, y)
            else:
                entity_factories.droid.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 2)
        y = random.randint(room.y1 + 1, room.y2 - 2)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()
            if item_chance < 0.4:
                entity_factories.menace_energy.spawn(dungeon, x, y)
            elif item_chance < 0.6:
                entity_factories.large_menace_energy.spawn(dungeon, x, y)
            elif item_chance < 0.7: 
                entity_factories.lightning_gun.spawn(dungeon, x, y)
            elif item_chance < 0.8:
                entity_factories.cpu_hack.spawn(dungeon, x, y)
            elif item_chance < 0.9:
                entity_factories.flame_burst.spawn(dungeon, x, y)
            else:
                entity_factories.cpu_overload.spawn(dungeon, x, y)

def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
    ) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between two points"""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5: #50% chance
        # Horizontal first, vertical second
        corner_x, corner_y = x2, y1
    else:
        # Vertical first, horizontal second
        corner_x, corner_y = x1, y2

    # Generate coordinates for the tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    max_monsters_per_room: int,
    max_items_per_room: int,
    engine: Engine,
) -> GameMap:
    """Generate a new Dungeon Map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through other rooms and check if they intersect this one
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # this room intersects, so go to the next attempt
        #if there are no intersections then the room is valid
        # set the room to roomwalls
        dungeon.tiles[new_room.room] = tile_types.roomwall
        # dig out the inner area
        dungeon.tiles[new_room.inner] = tile_types.floor

        # finally append room to list
        rooms.append(new_room)

    # dig tunnels through the roomwall
    for i, room in enumerate(rooms):
        if i == 0:
            # this means this is the first room, where player will start
            player.place(*room.center, dungeon)
        else: #for all other rooms
            # dig out a tunnel between this room and the last
            for x, y in tunnel_between(rooms[i-1].center, room.center):
                dungeon.tiles[x,y] = tile_types.floor

    # place monsters in rooms
    for room in rooms:
        place_entities(room, dungeon, max_monsters_per_room, max_items_per_room)

    # place down stairs in center of last room generated
    center_of_last_room = rooms[(len(rooms)) - 1].center
    dungeon.tiles[center_of_last_room] = tile_types.down_stairs
    dungeon.downstairs_location = center_of_last_room

    return dungeon