import os
from constants_mapping import *
from collections import OrderedDict


class Hero:
    def __init__(self, hero_id):
        self.hero_id = hero_id
        self.hero_name = hero_id_name_mapping[self.hero_id]
        self.hero_localized_name = name_lname_mapping[self.hero_name]
        self.location = (0, 0)
        self.level = 1
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        # self.gold = 0
        self.net_worth = 0
        self.last_hits = 0
        self.denies = 0
        self.wards_placed = 0
        # self.health = 0
        self.alive = True
        # self.respawn_seconds = 0
        # self.mana = 0
        # self.items = []
        # self.abilties = []

    def interval_update(self, update):
        self.location = (update['x'], update['y'])
        self.level = update['level']
        self.kills = update['kills']
        self.deaths = update['deaths']
        self.assists = update['assists']
        # self.gold = update['gold']
        self.net_worth = update['networth']
        self.last_hits = update['lh']
        self.denies = update['denies']
        self.wards_placed = update['obs_placed'] + update['sen_placed']
        self.alive = update['life_state'] == 0

    def __repr__(self):
        return f'{self.hero_localized_name} ({self.hero_name}) at {self.location}'

    def __str__(self):
        return f'Hero:{self.hero_localized_name}, Location:{self.location}, Level:{self.level}, Kills:{self.kills}, Deaths:{self.deaths}, Assists:{self.assists}, Net Worth:{self.net_worth}, Last Hits:{self.last_hits}, Denies:{self.denies}, Wards Placed:{self.wards_placed}, Alive:{self.alive}'


def time_converter(time):
    if time < 0:
        sign = "-"
        time = abs(time)
    else:
        sign = ""
    mins = time // 60
    secs = time % 60
    return f'{sign}{mins}:{secs:02d}'


def simplifier(league_id, match_id, chunk_size=10):
    if not os.path.exists(f'{league_id}/parsed/{match_id}.json'):
        print(f'Parsed {match_id} does not exist')

    with open(f'{league_id}/parsed/{match_id}.json') as f:
        updates = list(map(json.loads, f.read().splitlines()))
        simplified = {}
        heroes = OrderedDict()

        prev_chunk_time = -91
        FB_FLAG = False
        chunk = []
        for update in updates:
            # Chunking logic
            if update['time'] > prev_chunk_time and update['time'] % chunk_size == 0:
                if len(chunk) > 0:
                    simplified[prev_chunk_time] = "\n".join(chunk)
                chunk = []
                prev_chunk_time = update['time']

            # Demo prase logic
            # Skip draft updates
            if update['time'] < -90:
                continue
            # Skip actions updates
            if update['type'] == 'actions':
                continue

            # Game initialization
            if prev_chunk_time == -91 and update['time'] == -90:
                chunk.append(f'{time_converter(update["time"])}: Game started')
            if update['time'] == -89 and update['type'] == 'interval' and update.get('unit', '').startswith('CDOTA_Unit_Hero'):
                heroes[update['hero_id']] = Hero(update['hero_id'])

            # Interval updates
            if update['time'] > -89 and update['type'] == 'interval' and update.get('unit', '').startswith('CDOTA_Unit_Hero'):
                if update['hero_id'] not in heroes:  # Workaround when initial intervals do not have unit info in them
                    heroes[update['hero_id']] = Hero(update['hero_id'])
                heroes[update['hero_id']].interval_update(update)
                if update['time'] % chunk_size == 0:
                    chunk.append(f'{time_converter(update["time"])}: {heroes[update["hero_id"]].__str__()}')

            # Kills
            if update['type'] == 'DOTA_COMBATLOG_DEATH' and update['attackername'] != 'dota_unknown' and update['targetname'] not in ['npc_dota_centaur_cart', 'npc_dota_ember_spirit_remnant']:
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["targetname"]]} was killed by {name_lname_mapping[update["attackername"]]}'
                if FB_FLAG is False and update['targethero'] is True:
                    update_str += ' (First Blood)'
                    FB_FLAG = True
                chunk.append(update_str)

            # Abilities
            if update['type'] == 'DOTA_COMBATLOG_ABILITY' and update['inflictor'].startswith('plus_') is False and update['inflictor'].startswith('seasonal_') is False and update['inflictor'] not in ['ability_lamp_use']:
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["attackername"]]} used {name_lname_mapping[update["inflictor"]]}'
                if update['targetname'] != 'dota_unknown':
                    update_str += f' on {name_lname_mapping[update["targetname"]]}'
                chunk.append(update_str)

            # Damage
            if update['type'] == 'DOTA_COMBATLOG_DAMAGE':
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["attackername"]]} dealt {update["value"]} damage to {name_lname_mapping[update["targetname"]]}'
                if update['inflictor'] != 'dota_unknown':
                    update_str += f' with {name_lname_mapping[update["inflictor"]]}'
                chunk.append(update_str)

            # Healing
            if update['type'] == 'DOTA_COMBATLOG_HEAL' and 'rax' not in update['targetname'] and 'fort' not in update['targetname']:
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["attackername"]]} healed {name_lname_mapping[update["targetname"]]} for {update["value"]} hp'
                if update['inflictor'] != 'dota_unknown':
                    update_str += f' with {name_lname_mapping[update["inflictor"]]}'
                chunk.append(update_str)

            # Items
            if update['type'] == 'DOTA_COMBATLOG_ITEM':
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["attackername"]]} used {name_lname_mapping[update["inflictor"]]}'
                if update['targetname'] != 'dota_unknown':
                    update_str += f' on {name_lname_mapping[update["targetname"]]}'
                chunk.append(update_str)

            # XP
            if update['type'] == 'DOTA_COMBATLOG_XP':
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["targetname"]]} gained {update["value"]} XP'
                chunk.append(update_str)

            # Level
            if update['type'] == 'DOTA_ABILITY_LEVEL':
                if update["abilitylevel"] > 0 and update["valuename"] not in ['plus_high_five', 'plus_guild_banner', 'ability_capture', 'abyssal_underlord_portal_warp', 'twin_gate_portal_warp', 'ability_lamp_use', 'ability_pluck_famango']:
                    update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["targetname"]]} leveled {name_lname_mapping[update["valuename"]]} to level {update["abilitylevel"]}'
                    chunk.append(update_str)

            # Gold
            if update['type'] == 'DOTA_COMBATLOG_GOLD':
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["targetname"]]} gained {update["value"]} gold'
                chunk.append(update_str)

            # Purchases
            if update['type'] == 'DOTA_COMBATLOG_PURCHASE':
                update_str = f'{time_converter(update["time"])}: {name_lname_mapping[update["targetname"]]} purchased {name_lname_mapping[update["valuename"]]}'
                chunk.append(update_str)

            # Scan
            if update['type'] == 'CHAT_MESSAGE_SCAN_USED':
                if update['value'] == 2:
                    update_str = f'{time_converter(update["time"])}: Radiant used Scan'
                elif update['value'] == 3:
                    update_str = f'{time_converter(update["time"])}: Dire used Scan'
                chunk.append(update_str)

            # Glyph
            if update['type'] == 'CHAT_MESSAGE_GLYPH_USED':
                if update['player1'] == 2:
                    update_str = f'{time_converter(update["time"])}: Radiant used Glyph'
                elif update['player1'] == 3:
                    update_str = f'{time_converter(update["time"])}: Dire used Glyph'
                chunk.append(update_str)

            # Runes
            if update['type'] == 'CHAT_MESSAGE_RUNE_BOTTLE':
                update_str = f'{time_converter(update["time"])}: {list(heroes.values())[int(update["player1"])].hero_localized_name} bottled {rune_id_lname_mapping[update["value"]]}'
                chunk.append(update_str)
            if update['type'] == 'CHAT_MESSAGE_RUNE_PICKUP':
                update_str = f'{time_converter(update["time"])}: {list(heroes.values())[int(update["player1"])].hero_localized_name} activated {rune_id_lname_mapping[update["value"]]}'
                chunk.append(update_str)

            # Aegis
            if update['type'] == 'CHAT_MESSAGE_AEGIS':
                update_str = f'{time_converter(update["time"])}: {list(heroes.values())[int(update["player1"])].hero_localized_name} picked up Aegis'
                chunk.append(update_str)

            # Buyback
            if update['type'] == 'CHAT_MESSAGE_BUYBACK':
                update_str = f'{time_converter(update["time"])}: {list(heroes.values())[int(update["player1"])].hero_localized_name} bought back'
                chunk.append(update_str)

            # Game End
            if update['type'] == 'chatwheel' and update['key'] in ["75", "76"]:
                update_str = f'{time_converter(update["time"])}: {list(heroes.values())[int(update["slot"])].hero_localized_name} called GG (forfeit)'
                chunk.append(update_str)
            if update['type'] == 'DOTA_COMBATLOG_DEATH' and update['attackername'] == 'dota_unknown':
                if update['targetname'].startswith('npc_dota_goodguys'):
                    chunk.append(f'{time_converter(update["time"])}: Radiant Ancient Destroyed')
                elif update['targetname'].startswith('npc_dota_badguys'):
                    chunk.append(f'{time_converter(update["time"])}: Dire Ancient Destroyed')
                simplified[prev_chunk_time] = "\n".join(chunk)
                break

    return simplified

# TODO list
# 1. Hero creeps and other special units
# 2. Add Interval hp, mana, respawn_seconds, items, abilities
# 3. Deal with spam/groupings (heal, dmg?, invoker spells)
# 4. Value in purchases?
