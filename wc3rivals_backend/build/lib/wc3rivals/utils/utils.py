# Used in API

GATEWAY_MAP = {
    "us_west": "Lordaeron",
    "us_east": "Azeroth",
    "europe": "Northrend",
    "Lordaeron": "Lordaeron",
    "Azeroth": "Azeroth",
    "Northrend": "Northrend"
}

HUMAN_RACE = 'human'
ORC_RACE = 'orc'
NIGHTELF_RACE = 'nightelf'
UNDEAD_RACE = 'undead'
RANDOM_RACE = 'random'


def detect_race(race):
    race = race.lower()
    if 'human' in race:
        return HUMAN_RACE
    if 'orc' in race:
        return ORC_RACE
    if 'elf' in race:
        return NIGHTELF_RACE
    if 'undead' in race:
        return UNDEAD_RACE
    return RANDOM_RACE
