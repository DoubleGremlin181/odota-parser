import json
from os import getcwd


def json_reader(file_path):
    with open(file_path) as f:
        return json.load(f)


# Mapping Hero ID to Hero Name
hero_id_name_mapping = {int(hero_id): hero_data['name'] for hero_id, hero_data in json_reader("constants/heroes.json").items()}
# Mapping Item ID to Item Name
item_id_name_mapping = {int(item_id): item_name for item_id, item_name in json_reader("constants/item_ids.json").items()}
# Mapping Rune ID to Rune Localized Name
rune_id_lname_mapping = {0: 'Double Damage Rune', 1: 'Haste Rune', 2: 'Illusion Rune', 3: 'Invisibility Rune', 4: 'Regeneration Rune', 5: 'Bounty Rune', 6: 'Arcane Rune', 7: 'Water Rune', 8: 'Wisdom Rune', 9: 'Shield Rune'}

# Mapping Hero Name to Hero Localized Name
name_lname_mapping = {hero_data['name']: hero_data['localized_name'] for hero_id, hero_data in json_reader("constants/heroes.json").items()}
# Mapping Ability Name to Ability Localized Name
name_lname_mapping.update({raw_ability_name: ability_data.get('dname', None) for raw_ability_name, ability_data in json_reader("constants/abilities.json").items()})
# Mapping Non Hero Unit Name to Unit Localized Name
name_lname_mapping.update({name: lname for name, lname in json_reader("constants/non_hero_units.json").items()})
# Mapping Item Name to Item Localized Name
name_lname_mapping.update({f"item_{item_name}": item_data.get('dname', None) for item_name, item_data in json_reader("constants/items.json").items()})
name_lname_mapping.update({f"npc_dota_{item_name}": item_data.get('dname', None) for item_name, item_data in json_reader("constants/items.json").items()})
# Mapping Building Name to Building Localized Name
name_lname_mapping.update({name: lname for name, lname in json_reader("constants/buildings.json").items()})
# Other Mappings
name_lname_mapping.update({name: lname for name, lname in json_reader("constants/other.json").items()})

# Misc
name_lname_mapping['npc_dota_observer_wards'] = 'Observer Ward'
name_lname_mapping['npc_dota_sentry_wards'] = 'Sentry Ward'
name_lname_mapping['npc_dota_enraged_wildkin_tornado'] = 'Tornado'
name_lname_mapping['npc_dota_unit_tidehunter_anchor'] = 'Anchor'
name_lname_mapping['npc_dota_aether_remnant'] = 'Aether Remnant'
name_lname_mapping['npc_dota_unit_twin_gate'] = 'Twin Gate'
name_lname_mapping['twin_gate_portal_warp'] = 'Portal Warp'
name_lname_mapping['#DOTA_OutpostName_North'] = 'Top Outpost'
name_lname_mapping['#DOTA_OutpostName_South'] = 'Bottom Outpost'
name_lname_mapping['#DOTA_OutpostName_Bot_Outer'] = 'Bottom Outpost'
name_lname_mapping['ability_pluck_famango'] = 'Pluck'
name_lname_mapping['npc_dota_treant_eyes'] = 'Eyes In The Forest'


# Additions for name with more than 1 part
temp = {}
for name, lname in name_lname_mapping.items():
    if name.startswith('npc_dota_hero_') and name.count('_') >= 4:
        parts = name.split('_')
        name_fixed = '_'.join(parts[:3]) + '_' + ''.join(parts[3:])
        temp[name_fixed] = lname
name_lname_mapping.update(temp)
