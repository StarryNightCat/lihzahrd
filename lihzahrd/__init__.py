import math
import struct
import uuid
import enum
import datetime
import typing


class Rect:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def __repr__(self):
        return f"Rect(left={self.left}, right={self.right}, top={self.top}, bottom={self.bottom})"


class FileReader:
    def __init__(self, file):
        self.file = file

    def bool(self) -> bool:
        return struct.unpack("?", self.file.read(1))[0]

    def int1(self) -> int:
        return struct.unpack("B", self.file.read(1))[0]

    def uint1(self) -> int:
        return struct.unpack("B", self.file.read(1))[0]

    def int2(self) -> int:
        return struct.unpack("h", self.file.read(2))[0]

    def uint2(self) -> int:
        return struct.unpack("H", self.file.read(2))[0]

    def int4(self) -> int:
        return struct.unpack("i", self.file.read(4))[0]

    def uint4(self) -> int:
        return struct.unpack("I", self.file.read(4))[0]

    def int8(self) -> int:
        return struct.unpack("q", self.file.read(8))[0]

    def uint8(self) -> int:
        return struct.unpack("Q", self.file.read(8))[0]

    def single(self) -> float:
        return struct.unpack("f", self.file.read(4))[0]

    def double(self) -> float:
        return struct.unpack("d", self.file.read(8))[0]

    def bit(self) -> typing.Tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        data = struct.unpack("B", self.file.read(1))[0]
        return (bool(data & 0b1000_0000),
                bool(data & 0b0100_0000),
                bool(data & 0b0010_0000),
                bool(data & 0b0001_0000),
                bool(data & 0b0000_1000),
                bool(data & 0b0000_0100),
                bool(data & 0b0000_0010),
                bool(data & 0b0000_0001))

    def rect(self) -> Rect:
        left, right, top, bottom = struct.unpack("iiii", self.file.read(16))
        return Rect(left, right, top, bottom)

    def string(self, size=None) -> str:
        if size is None:
            size = self.uint1()
        return str(self.file.read(size), encoding="latin1")

    def uuid(self) -> uuid.UUID:
        # TODO: convert to uuid
        # https://docs.microsoft.com/en-us/dotnet/api/system.guid.tobytearray?view=netframework-4.8
        uuid_bytes = self.file.read(16)
        return uuid_bytes

    def datetime(self) -> datetime.datetime:
        # TODO: convert to datetime
        # https://docs.microsoft.com/it-it/dotnet/api/system.datetime.kind?view=netframework-4.8#System_DateTime_Kind
        datetime_bytes = self.file.read(8)
        return datetime_bytes


class Version:
    """A Terraria version."""

    _version_ids = {
        71: "1.2.0.3.1",
        77: "1.2.2",
        104: "1.2.3",
        140: "1.3.0.1",
        151: "1.3.0.4",
        153: "1.3.0.5",
        154: "1.3.0.6",
        155: "1.3.0.7",
        156: "1.3.0.8",
        170: "1.3.2",
        174: "1.3.3",
        178: "1.3.4",
        194: "1.3.5.3"
    }

    def __init__(self, data: typing.Union[int, str]):
        if isinstance(data, int):
            self.id = data
        else:
            for version in self._version_ids:
                if self._version_ids[version] == data:
                    self.id = version
                    break
            else:
                raise ValueError("No such version")

    @property
    def name(self):
        # TODO: Add all versions
        try:
            return self._version_ids[self.id]
        except KeyError:
            return "Unknown"

    def __repr__(self):
        return f"Version({self.id})"

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other

    def __gt__(self, other):
        return self.id > other

    def __lt__(self, other):
        return self.id < other


class GeneratorInfo:
    """Information about the world generator."""

    def __init__(self, seed, version):
        self.seed = seed
        """The seed this world was generated with."""

        self.version = version
        """The version of the generator that created this world."""


class Coordinates:
    """A pair of coordinates."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Coordinates({self.x}, {self.y})"

    def __str__(self):
        return f"{self.x}, {self.y}"


class MoonStyle(enum.IntEnum):
    """All possible moon styles."""
    WHITE = 0
    ORANGE = 1
    RINGED_GREEN = 2

    def __repr__(self):
        return f"MoonStyle('{self.name}')"


class FourPartSplit:
    """A world property split in four parts, separated by three vertical lines at a certain x coordinate."""
    def __init__(self, separators: typing.List[int], properties: typing.List):
        self.separators: typing.List[int] = separators
        """The three x coordinates of the vertical separators, in increasing order."""

        self.properties: typing.List = properties
        """The four properties, in order:
        
        - The far left property, the one between the left world edge and the first separator.
        - The nearby left property, between the first and the second separator.
        - The nearby right property, between the second and the third separator.
        - The far right property, between the third separator and the right world edge."""

    def __repr__(self):
        return f"FourPartSplit({repr(self.separators)}, {repr(self.properties)})"

    def get_property_at_x(self, x: int):
        if x < self.separators[0]:
            return self.properties[0]
        elif x < self.separators[1]:
            return self.properties[1]
        elif x < self.separators[2]:
            return self.properties[2]
        else:
            return self.properties[3]

    @property
    def far_left(self):
        return self.properties[0]

    @far_left.setter
    def far_left(self, value):
        self.properties[0] = value

    @property
    def nearby_left(self):
        return self.properties[1]

    @nearby_left.setter
    def nearby_left(self, value):
        self.properties[1] = value

    @property
    def nearby_right(self):
        return self.properties[2]

    @nearby_right.setter
    def nearby_right(self, value):
        self.properties[2] = value

    @property
    def far_right(self):
        return self.properties[2]

    @far_right.setter
    def far_right(self, value):
        self.properties[2] = value


class WorldStyles:
    """The styles of various world elements."""
    def __init__(self,
                 moon: MoonStyle,
                 trees: FourPartSplit,
                 moss: FourPartSplit,):
        self.moon: MoonStyle = moon
        self.trees: FourPartSplit = trees
        self.moss: FourPartSplit = moss

    def __repr__(self):
        return f"WorldStyles(moon={repr(self.moon)}, trees={repr(self.trees)}, moss={repr(self.moss)})"


class WorldBackgrounds:
    """The backgrounds of various world biomes."""
    def __init__(self,
                 bg_underground_snow: int,
                 bg_underground_jungle: int,
                 bg_hell: int,
                 bg_forest: int,
                 bg_corruption: int,
                 bg_jungle: int,
                 bg_snow: int,
                 bg_hallow: int,
                 bg_crimson: int,
                 bg_desert: int,
                 bg_ocean: int):
        self.bg_underground_snow: int = bg_underground_snow
        self.bg_underground_jungle: int = bg_underground_jungle
        self.bg_hell: int = bg_hell
        self.bg_forest: int = bg_forest
        self.bg_corruption: int = bg_corruption
        self.bg_jungle: int = bg_jungle
        self.bg_snow: int = bg_snow
        self.bg_hallow: int = bg_hallow
        self.bg_crimson: int = bg_crimson
        self.bg_desert: int = bg_desert
        self.bg_ocean: int = bg_ocean

    def __repr__(self):
        return f"WorldBackgrounds({self.bg_underground_snow}, {self.bg_underground_jungle}, {self.bg_hell}, {self.bg_forest}, {self.bg_corruption}, {self.bg_jungle}, {self.bg_snow}, {self.bg_hallow}, {self.bg_crimson}, {self.bg_desert}, {self.bg_ocean})"


class WorldClouds:
    """Information about... the clouds in the world?"""
    def __init__(self, bg_cloud: int, cloud_number: int, wind_speed: float):
        self.bg_cloud: int = bg_cloud
        self.cloud_number: int = cloud_number
        self.wind_speed: float = wind_speed

    def __repr__(self):
        return f"WorldClouds(bg_cloud={self.bg_cloud}, cloud_number={self.cloud_number}, wind_speed={self.wind_speed})"


class MoonPhases(enum.IntEnum):
    FULL_MOON = 0
    WANING_GIBBOUS = 1
    THIRD_QUARTER = 2
    WANING_CRESCENT = 3
    NEW_MOON = 4
    WAXING_CRESCENT = 5
    FIRST_QUARTER = 6
    WAXING_GIBBOUS = 7

    def __repr__(self):
        return f"MoonPhases('{self.name}')"


class WorldTime:
    """Game time related information."""
    def __init__(self, current: float,
                 is_daytime: bool,
                 moon_phase: int,
                 sundial_cooldown: int,
                 fast_forward_time: bool):
        self.current: float = current
        """The current game time."""

        self.is_daytime: bool = is_daytime
        """If the current time represents a day or a night."""

        self.moon_phase: int = moon_phase
        """The current moon phase."""

        self.sundial_cooldown: int = sundial_cooldown
        """The number of days the Enchanted Sundial can't be used for."""

        self.fast_forward_time: bool = fast_forward_time

    def __repr__(self):
        return f"WorldTime(current={self.current}, is_daytime={self.is_daytime}, moon_phase={self.moon_phase}, sundial_cooldown={self.sundial_cooldown}, fast_forward_time={self.fast_forward_time})"


class InvasionType(enum.IntEnum):
    NONE = 0
    GOBLIN_INVASION = 1
    FROST_LEGION = 2
    PIRATE_INVASION = 3
    MARTIAN_MADNESS = 4

    def __repr__(self):
        return f"InvasionType('{self.name}')"


class WorldInvasion:
    """Invasions (goblin army, pirates, martian madness...) related information."""
    def __init__(self, delay: int, size: int, type_: InvasionType, position: float, size_start: int):
        self.delay: int = delay
        self.size: int = size

        self.type: InvasionType = type_
        """The type of the current invasion (goblin army / pirates / martian madness...).
        
        If InvasionType.NONE, no invasion will be active in the world."""

        self.position: float = position
        self.size_start: int = size_start

    def __repr__(self):
        return f"WorldInvasion(delay={self.delay}, size={self.size}, type_={self.type}, position={self.position}, size_start={self.size_start})"


class WorldRain:
    """Rain related information."""
    def __init__(self, is_active: bool, time_left: int, max_rain: float):
        self.is_active: bool = is_active
        """If it is currently raining in the world."""

        self.time_left: int = time_left
        """How long it will continue to rain for."""

        self.max_rain: float = max_rain

    def __repr__(self):
        return f"WorldRain(is_active={self.is_active}, time_left={self.time_left}, max_rain={self.max_rain})"


class WorldParty:
    """NPC Party related information."""
    def __init__(self,
                 thrown_by_party_center: bool,
                 thrown_by_npcs: bool,
                 cooldown: int,
                 partying_npcs: typing.List[int]):
        self.thrown_by_party_center: bool = thrown_by_party_center
        """If the party was started by right-clicking a Party Center."""

        self.thrown_by_npcs: bool = thrown_by_npcs
        """If the item was spontaneously thrown by NPCs."""

        self.cooldown: int = cooldown
        """How long a party cannot be started for."""

        self.partying_npcs: typing.List[int] = partying_npcs
        """The list of NPC IDs that threw the party."""

    def __repr__(self):
        return f"WorldParty(thrown_by_party_center={self.thrown_by_party_center}, thrown_by_npcs={self.thrown_by_npcs}, cooldown={self.cooldown}, partying_npcs={self.partying_npcs})"

    @property
    def is_active(self):
        return self.thrown_by_party_center or self.thrown_by_npcs


class WorldSandstorm:
    """Sandstorm related information."""
    def __init__(self,
                 is_active: bool,
                 time_left: int,
                 severity: float,
                 intended_severity: float):
        self.is_active: bool = is_active
        """If a sandstorm is currently ongoing in the desert."""

        self.time_left: int = time_left
        """How long the sandstorm will continue for."""

        self.severity: float = severity
        self.intended_severity: float = intended_severity

    def __repr__(self):
        return f"WorldSandstorm(is_active={self.is_active}, time_left={self.time_left}, severity={self.severity}, intended_severity={self.intended_severity})"


class PillarsInfo:
    """A container for information associated with the Lunar Pillars."""
    def __init__(self, solar, vortex, nebula, stardust):
        self.solar = solar
        self.vortex = vortex
        self.nebula = nebula
        self.stardust = stardust

    def __repr__(self):
        return f"PillarsInfo(solar={self.solar}, vortex={self.vortex}, nebula={self.nebula}, stardust={self.stardust})"


class WorldLunarEvents:
    """Lunar Events (Lunar Pillars) related information."""
    def __init__(self,
                 are_active: bool,
                 pillars_present: PillarsInfo):
        self.are_active: bool = are_active
        """If the Lunar Events are active or not."""

        self.pillars_present: PillarsInfo = pillars_present
        """Which pillars are currently present in the world."""

    def __repr__(self):
        return f"WorldLunarEvents(are_active={self.are_active}, pillars_present={repr(self.pillars_present)})"


class WorldEvents:
    """Information about the ongoing world events."""
    def __init__(self,
                 blood_moon: bool,
                 solar_eclipse: bool,
                 invasion: WorldInvasion,
                 slime_rain: float,
                 rain: WorldRain,
                 party: WorldParty,
                 sandstorm: WorldSandstorm,
                 lunar_events: WorldLunarEvents):
        self.blood_moon: bool = blood_moon
        """If the current moon is a Blood Moon."""

        self.solar_eclipse: bool = solar_eclipse
        """If the current day is a Solar Eclipse."""

        self.invasion: WorldInvasion = invasion
        """Information about the currently ongoing invasion."""

        self.slime_rain: float = slime_rain
        """How long the slime rain will go on for."""

        self.rain: WorldRain = rain
        """Information about the currently ongoing rain."""

        self.party: WorldParty = party
        """Information about the currently ongoing party."""

        self.sandstorm: WorldSandstorm = sandstorm
        """Information about the currently ongoing sandstorm."""

        self.lunar_events: WorldLunarEvents = lunar_events
        """Information about the currently ongoing Lunar Events."""

    def __repr__(self):
        return f"<WorldEvents>"


class WorldEvilType(enum.Enum):
    CORRUPTION = False
    CRIMSON = True

    def __repr__(self):
        return f"CorruptionType('{self.name}')"


class OldOnesArmyTiers:
    def __init__(self, tier1, tier2, tier3):
        self.tier1: bool = tier1
        self.tier2: bool = tier2
        self.tier3: bool = tier3

    def __repr__(self):
        return f"OldOneArmyTiers({self.tier1}, {self.tier2}, {self.tier3})"


class Tier1Ore(enum.IntEnum):
    NOT_DETERMINED = -1
    COBALT = 107
    PALLADIUM = 221

    def __repr__(self):
        return f"Tier1Ore('{self.name}')"


class Tier2Ore(enum.IntEnum):
    NOT_DETERMINED = -1
    MYTHRIL = 108
    ORICHALCUM = 222

    def __repr__(self):
        return f"Tier2Ore('{self.name}')"


class Tier3Ore(enum.IntEnum):
    NOT_DETERMINED = -1
    NOT_DETERMINED_TOO = 16785407  # ???
    ADAMANTITE = 111
    TITANIUM = 223

    def __repr__(self):
        return f"Tier3Ore('{self.name}')"


class WorldAltarsSmashed:
    """Information related to the first three hardmode ores."""
    def __init__(self,
                 count: int,
                 ore_tier1: Tier1Ore,
                 ore_tier2: Tier2Ore,
                 ore_tier3: Tier3Ore):
        self.count: int = count
        """The number of altars smashed."""

        self.ore_tier1: Tier1Ore = ore_tier1
        self.ore_tier2: Tier2Ore = ore_tier2
        self.ore_tier3: Tier3Ore = ore_tier3

    def __repr__(self):
        return f"WorldAltars(count={self.count}, ore_tier1={self.ore_tier1}, ore_tier2={self.ore_tier2}, ore_tier3={self.ore_tier3})"


class AnglersQuestFish(enum.IntEnum):
    BATFISH = 0
    BUMBLEBEE_TUNA = 1
    CATFISH = 2
    CLOUDFISH = 3
    CURSEDFISH = 4
    DIRTFISH = 5
    DYNAMITE_FISH = 6
    EATER_OF_PLANKTON = 7
    FALLEN_STARFISH = 8
    THE_FISH_OF_CTHULHU = 9
    FISHOTRON = 10
    HARPYFISH = 11
    HUNGERFISH = 12
    ICHORFISH = 13
    JEWELFISH = 14
    MIRAGE_FISH = 15
    MUTANT_FLINXFIN = 16
    PENGFISH = 17
    PIXIEFISH = 18
    SPIDERFISH = 19
    TUNDRA_TROUT = 20
    UNICORN_FISH = 21
    GUIDE_VOODOO_FISH = 22
    WYVERNTAIL = 23
    ZOMBIE_FISH = 24
    AMANITIA_FUNGIFIN = 25
    ANGELFISH = 26
    BLOODY_MANOWAR = 27
    BONEFISH = 28
    BUNNYFISH = 29
    CAPN_TUNABEARD = 30
    CLOWNFISH = 31
    DEMONIC_HELLFISH = 32
    DERPFISH = 33
    FISHRON = 34
    INFECTED_SCABBARDFISH = 35
    MUDFISH = 36
    SLIMEFISH = 37
    TROPICAL_BARRACUDA = 38

    def __repr__(self):
        return f"AnglersQuestFish('{self.name}')"


class WorldSavedNPCs:
    def __init__(self,
                 goblin_tinkerer: bool,
                 wizard: bool,
                 mechanic: bool,
                 angler: bool,
                 stylist: bool,
                 tax_collector: bool,
                 bartender: bool):
        self.goblin_tinkerer: bool = goblin_tinkerer
        self.wizard: bool = wizard
        self.mechanic: bool = mechanic
        self.angler: bool = angler
        self.stylist: bool = stylist
        self.tax_collector: bool = tax_collector
        self.bartender: bool = bartender

    def __repr__(self):
        return f"SavedNPCs(goblin_tinkerer={self.goblin_tinkerer}, wizard={self.wizard}, mechanic={self.mechanic}, angler={self.angler}, stylist={self.stylist}, tax_collector={self.tax_collector}, bartender={self.bartender})"


class WorldShadowOrbs:
    """Information related to the Shadow Orbs (or the Crimson Hearts) smashed in the world."""
    def __init__(self,
                 smashed_at_least_once: bool,
                 spawn_meteorite: bool,
                 evil_boss_counter: int):
        self.smashed_at_least_once: bool = smashed_at_least_once
        """If a Shadow Orb has ever been smashed in this world."""

        self.spawn_meteorite: bool = spawn_meteorite
        """If a Meteorite should land in the world at midnight.
        
        It is set to True when a Shadow Orb is smashed, then it is set to False when the meteorite actually lands."""

        self.evil_boss_counter: int = evil_boss_counter
        """If it is 2, the Eater of Worlds will spawn when a Shadow Orb is smashed.
        
        It is the number of Shadow Orbs broken, modulo 3."""

    def __repr__(self):
        return f"WorldShadowOrbs(smashed_at_least_once={self.smashed_at_least_once}, spawn_meteorite={self.spawn_meteorite}, evil_boss_counter={self.evil_boss_counter})"


class WorldBossesDefeated:
    def __init__(self,
                 eye_of_cthulhu: bool,
                 eater_of_worlds: bool,
                 skeletron: bool,
                 queen_bee: bool,
                 the_twins: bool,
                 the_destroyer: bool,
                 skeletron_prime: bool,
                 any_mechnical_boss: bool,
                 plantera: bool,
                 golem: bool,
                 king_slime: bool,
                 goblin_army: bool,
                 clown: bool,
                 frost_moon: bool,
                 pirates: bool,
                 duke_fishron: bool,
                 moon_lord: bool,
                 pumpking: bool,
                 mourning_wood: bool,
                 ice_queen: bool,
                 santa_nk1: bool,
                 everscream: bool,
                 lunar_pillars: PillarsInfo,
                 old_ones_army: OldOnesArmyTiers):
        self.eye_of_cthulhu: bool = eye_of_cthulhu
        self.eater_of_worlds: bool = eater_of_worlds
        self.skeletron: bool = skeletron
        self.queen_bee: bool = queen_bee
        self.the_twins: bool = the_twins
        self.the_destroyer: bool = the_destroyer
        self.skeletron_prime: bool = skeletron_prime

        self.any_mechnical_boss: bool = any_mechnical_boss
        """Appearently, there's a different flag for beating any mechanical boss and a specific mechanical boss."""

        self.plantera: bool = plantera
        self.golem: bool = golem
        self.king_slime: bool = king_slime
        self.goblin_army: bool = goblin_army
        self.clown: bool = clown
        self.frost_moon: bool = frost_moon
        self.pirates: bool = pirates
        self.duke_fishron: bool = duke_fishron
        self.moon_lord: bool = moon_lord
        self.pumpking: bool = pumpking
        self.mourning_wood: bool = mourning_wood
        self.ice_queen: bool = ice_queen
        self.santa_nk1: bool = santa_nk1
        self.everscream: bool = everscream
        self.lunar_pillars: PillarsInfo = lunar_pillars
        self.old_ones_army: OldOnesArmyTiers = old_ones_army

    def __repr__(self):
        return f"<WorldBossesDefeated>"


class WorldAnglersQuest:
    """Information about today's Angler's quest."""

    def __init__(self, current_goal: AnglersQuestFish, completed_by: typing.List[str]):
        self.current_goal: AnglersQuestFish = current_goal
        """The fish currently requested by the angler."""

        self.completed_by: typing.List[str] = completed_by
        """A list of player names who completed the angler's quest today."""

    def __repr__(self):
        return f"WorldAnglersQuest(current_goal={self.current_goal}, completed_by={self.completed_by})"


class World:
    """The Python representation of a Terraria world."""
    def __init__(self,
                 version: Version,
                 savefile_type: int,
                 revision: int,
                 is_favorite: bool,
                 name: str,
                 generator: GeneratorInfo,
                 uuid_: uuid.UUID,
                 id_: int,
                 bounds: Rect,
                 size: Coordinates,
                 is_expert: bool,
                 created_on,
                 styles: WorldStyles,
                 backgrounds: WorldBackgrounds,
                 spawn_point: Coordinates,
                 underground_level: float,
                 cavern_level: float,
                 time: WorldTime,
                 events: WorldEvents,
                 dungeon_point: Coordinates,
                 world_evil: WorldEvilType,
                 saved_npcs: WorldSavedNPCs,
                 altars_smashed: WorldAltarsSmashed,
                 is_hardmode: bool,
                 shadow_orbs: WorldShadowOrbs,
                 bosses_defeated: WorldBossesDefeated,
                 anglers_quest: WorldAnglersQuest,
                 clouds: WorldClouds,
                 cultist_delay: int):

        self.version: Version = version
        """The game version when this savefile was last saved."""

        self.savefile_type = savefile_type
        """The format of the save file. Should be 2 for all versions following 1.2."""

        self.revision: int = revision
        """The number of times this world was saved."""

        self.is_favorite: bool = is_favorite
        """If the world is marked as favorite or not."""

        self.name: str = name
        """The name the world was given at creation. Doesn't always match the filename."""

        self.generator: GeneratorInfo = generator
        """Information about the generation of this world."""

        self.uuid: uuid.UUID = uuid_
        """The Universally Unique ID of this world."""

        self.id: int = id_
        """The world id. Used to name the minimap file."""

        self.bounds: Rect = bounds
        """The world size in pixels."""

        self.size: Coordinates = size
        """The world size in tiles."""

        self.is_expert: bool = is_expert
        """If the world is in expert mode or not."""

        self.created_on = created_on
        """The date and time this world was created in."""

        self.styles: WorldStyles = styles
        """The styles of various world elements."""

        self.backgrounds: WorldBackgrounds = backgrounds
        """The backgrounds of the various biomes."""

        self.spawn_point: Coordinates = spawn_point
        """The coordinates of the spawn point."""

        self.underground_level: float = underground_level
        """The depth at which the underground biome starts."""

        self.cavern_level: float = cavern_level
        """The depth at which the cavern biome starts."""

        self.time: WorldTime = time
        """Game time related information."""

        self.events: WorldEvents = events
        """Currently ongoing world events."""

        self.dungeon_point: Coordinates = dungeon_point
        """The Old Man spawn point."""

        self.world_evil: WorldEvilType = world_evil
        """Whether the world has Corruption or Crimson."""

        self.saved_npcs: WorldSavedNPCs = saved_npcs
        """The NPCs that were rescued by the player."""

        self.altars_smashed: WorldAltarsSmashed = altars_smashed
        """Information related to the destruction of Demon Altars with a Pwnhammer."""

        self.is_hardmode: bool = is_hardmode
        """Whether or not the world is in hardmode."""

        self.shadow_orbs: WorldShadowOrbs = shadow_orbs
        """Information related to the Shadow Orbs or Crimson Hearts in the world."""

        self.bosses_defeated: WorldBossesDefeated = bosses_defeated
        """Which bosses have been defeated in the world."""

        self.anglers_quest: WorldAnglersQuest = anglers_quest
        """Information about today's Angler's Quest."""

        self.clouds: WorldClouds = clouds
        self.cultist_delay: int = cultist_delay

    def __repr__(self):
        return f'<World "{self.name}">'

    @property
    def crimson_hearts(self) -> WorldShadowOrbs:
        return self.shadow_orbs

    @crimson_hearts.setter
    def crimson_hearts(self, value):
        self.shadow_orbs = value

    @classmethod
    def create_from_file(cls, file):
        f = FileReader(file)

        version = Version(f.int4())
        relogic = f.string(7)
        savefile_type = f.uint1()
        if version != Version("1.3.5.3") or relogic != "relogic" or savefile_type != 2:
            raise NotImplementedError("This parser can only read Terraria 1.3.5.3 save files.")

        revision = f.uint4()
        is_favorite = f.uint8() != 0

        pointers = [f.int4() for _ in range(f.int2())]
        tileframeimportant_size = math.ceil(f.int2() / 8)
        tileframeimportant = []
        for _ in range(tileframeimportant_size):
            current_bit = f.bit()
            tileframeimportant = [*tileframeimportant, *current_bit]

        name = f.string()

        generator = GeneratorInfo(f.string(), f.int4())

        uuid_ = f.uuid()
        id_ = f.int8()
        bounds = f.rect()
        world_size = Coordinates(y=f.int4(), x=f.int4())
        is_expert = f.bool()
        created_on = f.datetime()

        world_styles = WorldStyles(moon=MoonStyle(f.uint1()),
                                   trees=FourPartSplit(separators=[f.int4(), f.int4(), f.int4()],
                                                       properties=[f.int4(), f.int4(), f.int4(), f.int4()]),
                                   moss=FourPartSplit(separators=[f.int4(), f.int4(), f.int4()],
                                                      properties=[f.int4(), f.int4(), f.int4(), f.int4()]))

        bg_underground_snow = f.int4()
        bg_underground_jungle = f.int4()
        bg_hell = f.int4()

        spawn_point = Coordinates(f.int4(), f.int4())
        underground_level = f.double()
        cavern_level = f.double()

        current_time = f.double()
        is_daytime = f.bool()
        moon_phase = MoonPhases(f.uint4())

        blood_moon = f.bool()
        eclipse = f.bool()

        dungeon_point = Coordinates(f.int4(), f.int4())
        world_evil = WorldEvilType(f.bool())

        defeated_eye_of_cthulhu = f.bool()  # Possibly. I'm not sure.
        defeated_eater_of_worlds = f.bool()  # Possibly. I'm not sure.
        defeated_skeletron = f.bool()  # Possibly. I'm not sure.
        defeated_queen_bee = f.bool()
        defeated_the_twins = f.bool()
        defeated_the_destroyer = f.bool()
        defeated_skeletron_prime = f.bool()
        defeated_any_mechnical_boss = f.bool()
        defeated_plantera = f.bool()
        defeated_golem = f.bool()
        defeated_king_slime = f.bool()

        saved_goblin_tinkerer = f.bool()
        saved_wizard = f.bool()
        saved_mechanic = f.bool()

        defeated_goblin_army = f.bool()
        defeated_clown = f.bool()
        defeated_frost_moon = f.bool()
        defeated_pirates = f.bool()

        shadow_orbs = WorldShadowOrbs(smashed_at_least_once=f.bool(),
                                      spawn_meteorite=f.bool(),
                                      evil_boss_counter=f.int4())

        smashed_altars_count = f.int4()

        is_hardmode = f.bool()

        invasion_delay = f.int4()
        invasion_size = f.int4()
        invasion_type = InvasionType(f.int4())
        invasion_position = f.double()

        time_left_slime_rain = f.double()

        sundial_cooldown = f.uint1()

        rain = WorldRain(is_active=f.bool(), time_left=f.int4(), max_rain=f.single())

        hardmode_ore_1 = Tier1Ore(f.int4())
        hardmode_ore_2 = Tier2Ore(f.int4())
        hardmode_ore_3 = Tier3Ore(f.int4())
        altars_smashed = WorldAltarsSmashed(count=smashed_altars_count,
                                            ore_tier1=hardmode_ore_1,
                                            ore_tier2=hardmode_ore_2,
                                            ore_tier3=hardmode_ore_3)

        bg_forest = f.int1()
        bg_corruption = f.int1()
        bg_jungle = f.int1()
        bg_snow = f.int1()
        bg_hallow = f.int1()
        bg_crimson = f.int1()
        bg_desert = f.int1()
        bg_ocean = f.int1()

        backgrounds = WorldBackgrounds(bg_underground_snow=bg_underground_snow,
                                       bg_underground_jungle=bg_underground_jungle,
                                       bg_hell=bg_hell,
                                       bg_forest=bg_forest,
                                       bg_corruption=bg_corruption,
                                       bg_jungle=bg_jungle,
                                       bg_snow=bg_snow,
                                       bg_hallow=bg_hallow,
                                       bg_crimson=bg_crimson,
                                       bg_desert=bg_desert,
                                       bg_ocean=bg_ocean)

        clouds = WorldClouds(bg_cloud=f.int4(), cloud_number=f.int2(), wind_speed=f.single())

        angler_today_quest_completed_by_count = f.uint1()
        angler_today_quest_completed_by = []
        for _ in range(angler_today_quest_completed_by_count):
            angler_today_quest_completed_by.append(f.string())

        saved_angler = f.bool()

        angler_today_quest_target = AnglersQuestFish(f.int4())
        anglers_quest = WorldAnglersQuest(current_goal=angler_today_quest_target,
                                          completed_by=angler_today_quest_completed_by)

        saved_stylist = f.bool()
        saved_tax_collector = f.bool()

        invasion_size_start = f.int4()  # ???
        invasion = WorldInvasion(delay=invasion_delay,
                                 size=invasion_size,
                                 type_=invasion_type,
                                 position=invasion_position,
                                 size_start=invasion_size_start)

        cultist_delay = f.int4()  # ???
        mob_types_count = f.int2()
        mob_kills = {}
        for mob_id in range(mob_types_count):
            mob_kills[mob_id] = f.int4()

        fast_forward_time = f.bool()
        time = WorldTime(current=current_time,
                         is_daytime=is_daytime,
                         moon_phase=moon_phase,
                         sundial_cooldown=sundial_cooldown,
                         fast_forward_time=fast_forward_time)

        defeated_duke_fishron = f.bool()
        defeated_moon_lord = f.bool()
        defeated_pumpking = f.bool()
        defeated_mourning_wood = f.bool()
        defeated_ice_queen = f.bool()
        defeated_santa_nk1 = f.bool()
        defeated_everscream = f.bool()
        defeated_pillars = PillarsInfo(solar=f.bool(), vortex=f.bool(), nebula=f.bool(), stardust=f.bool())

        lunar_events = WorldLunarEvents(pillars_present=PillarsInfo(solar=f.bool(),
                                                                    vortex=f.bool(),
                                                                    nebula=f.bool(),
                                                                    stardust=f.bool()),
                                        are_active=f.bool())

        party_center_active = f.bool()
        party_natural_active = f.bool()
        party_cooldown = f.int4()
        partying_npcs_count = f.int4()
        partying_npcs = []
        for _ in range(partying_npcs_count):
            partying_npcs.append(f.int4())
        party = WorldParty(thrown_by_party_center=party_center_active,
                           thrown_by_npcs=party_natural_active,
                           cooldown=party_cooldown,
                           partying_npcs=partying_npcs)

        sandstorm = WorldSandstorm(is_active=f.bool(),
                                   time_left=f.int4(),
                                   severity=f.single(),
                                   intended_severity=f.single())

        events = WorldEvents(blood_moon=blood_moon,
                             solar_eclipse=eclipse,
                             invasion=invasion,
                             slime_rain=time_left_slime_rain,
                             rain=rain,
                             party=party,
                             sandstorm=sandstorm,
                             lunar_events=lunar_events)

        saved_bartender = f.bool()
        saved_npcs = WorldSavedNPCs(goblin_tinkerer=saved_goblin_tinkerer,
                                    wizard=saved_wizard,
                                    mechanic=saved_mechanic,
                                    angler=saved_angler,
                                    stylist=saved_stylist,
                                    tax_collector=saved_tax_collector,
                                    bartender=saved_bartender)

        old_ones_army = OldOnesArmyTiers(f.bool(), f.bool(), f.bool())

        bosses_defeated = WorldBossesDefeated(eye_of_cthulhu=defeated_eye_of_cthulhu,
                                              eater_of_worlds=defeated_eater_of_worlds,
                                              skeletron=defeated_skeletron,
                                              queen_bee=defeated_queen_bee,
                                              the_twins=defeated_the_twins,
                                              the_destroyer=defeated_the_destroyer,
                                              skeletron_prime=defeated_skeletron_prime,
                                              any_mechnical_boss=defeated_any_mechnical_boss,
                                              plantera=defeated_plantera,
                                              golem=defeated_golem,
                                              king_slime=defeated_king_slime,
                                              goblin_army=defeated_goblin_army,
                                              clown=defeated_clown,
                                              frost_moon=defeated_frost_moon,
                                              pirates=defeated_pirates,
                                              duke_fishron=defeated_duke_fishron,
                                              moon_lord=defeated_moon_lord,
                                              pumpking=defeated_pumpking,
                                              mourning_wood=defeated_mourning_wood,
                                              ice_queen=defeated_ice_queen,
                                              santa_nk1=defeated_santa_nk1,
                                              everscream=defeated_everscream,
                                              lunar_pillars=defeated_pillars,
                                              old_ones_army=old_ones_army)
        # Tile data starts here
        world = World(version=version, savefile_type=savefile_type, revision=revision, is_favorite=is_favorite,
                      name=name, generator=generator, uuid_=uuid_, id_=id_, bounds=bounds, size=world_size,
                      is_expert=is_expert, created_on=created_on, styles=world_styles, backgrounds=backgrounds,
                      spawn_point=spawn_point, underground_level=underground_level, cavern_level=cavern_level,
                      time=time, events=events, dungeon_point=dungeon_point, world_evil=world_evil,
                      saved_npcs=saved_npcs, altars_smashed=altars_smashed, is_hardmode=is_hardmode,
                      shadow_orbs=shadow_orbs, bosses_defeated=bosses_defeated, anglers_quest=anglers_quest,
                      clouds=clouds, cultist_delay=cultist_delay)
        breakpoint()
        return world


if __name__ == "__main__":
    with open("Small_Example.wld", "rb") as f:
        w = World.create_from_file(f)
