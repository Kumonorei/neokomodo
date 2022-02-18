from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

# Player

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200)
)

# Enemies

menace = Actor(
    char="m",
    color=(63, 127, 63),
    name="Menace",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35)
)

droid = Actor(
    char="d",
    color=(0, 127, 0),
    name="Droid",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75)
)

# Items

# Healing

menace_energy = Item(
    char="!",
    color=(0, 127, 0),
    name="Menace Energy",
    consumable=consumable.HealingConsumable(amount=3),
)

large_menace_energy = Item(
    char="!",
    color=(0, 255, 0),
    name="Large Menace Energy",
    consumable=consumable.HealingConsumable(amount=6),
)

# Techs

lightning_gun = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Gun",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

flame_burst = Item(
    char="~",
    color=(255, 0, 0),
    name="Flame Burst",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

cpu_hack = Item(
    char="~",
    color=(207, 63, 255),
    name="CPU Hack",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)

cpu_overload = Item(
    char="~",
    color=(27, 27, 127),
    name="CPU Overload",
    consumable=consumable.DeactivateConsumable(radius=3, number_of_turns=5),
)