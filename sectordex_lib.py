from lxml import etree
from numpy.linalg import norm
import csv
import os
import glob
from pathlib import Path
import commentjson

#from time import time


HAZARD_COND_MAP = {}

def set_hazard_cond_map(starsector_dir_path):
    global HAZARD_COND_MAP
    files = glob.glob(starsector_dir_path + '/starsector-core/data/campaign/procgen/condition_gen_data.csv') + \
            glob.glob(starsector_dir_path + '/mods/*/data/campaign/procgen/condition_gen_data.csv')
    for file in files:
        with open(file, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row['id'] and row['hazard']:
                    HAZARD_COND_MAP[row['id']] = float(row['hazard'])

COND_ID_TO_NAME_MAP = {}

def set_cond_id_name_maps(starsector_dir_path):
    global COND_ID_TO_NAME_MAP
    global COND_NAME_TO_ID_MAP
    csv_files = glob.glob(starsector_dir_path + '/starsector-core/data/campaign/market_conditions.csv') + \
                glob.glob(starsector_dir_path + '/mods/*/data/campaign/market_conditions.csv')
    for csv_file in csv_files:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] and row['name']:
                    # all of population conditions have same name
                    if row['id'].startswith('population'):
                        row['name'] += f" {row['id'].removeprefix('population_')}"
                    COND_ID_TO_NAME_MAP[row['id']] = row['name']

TYPE_ID_TO_NAME_MAP = {}

def set_type_id_name_maps(starsector_dir_path):
    global TYPE_ID_TO_NAME_MAP
    global TYPE_NAME_TO_ID_MAP
    json_files = glob.glob(starsector_dir_path + '/starsector-core/data/config/planets.json') + \
                 glob.glob(starsector_dir_path + '/mods/*/data/config/planets.json')
    for json_file in json_files:
        with open(json_file, 'r') as f:
            json_data = commentjson.load(f)
            for type_id, type_data_dict in json_data.items():
                TYPE_ID_TO_NAME_MAP[type_id] = type_data_dict['name']

class Planet:
    def __init__(self, id, name, type, conditions, system_id, inhabited=False):
        self.id = id
        self.name = name
        self.type = type
        self.system_id = system_id
        self.inhabited = inhabited
        self.resources = [cond for cond in conditions if cond.resource_level is not None]
        self.conditions = [cond for cond in conditions if cond.resource_level is None]
        self.hazard_conditions = [cond for cond in self.conditions if cond.hazard]
        self.other_conditions = [cond for cond in self.conditions if not cond.hazard]
        self.hazard = 1 + sum([float(cond.hazard) for cond in self.hazard_conditions])

    def __repr__(self):
        return f'{self.name} ({self.hazard*100:0.0f}% {self.type})'


class Condition:
    def __init__(self, id, name=None, hazard=None, resource_level=None):
        self.id = id
        self.name = name
        self.hazard = hazard
        self.resource_level = resource_level

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.name < other.name
    
    def __hash__(self):
        return hash(self.id)


class Type:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'

    def __eq__(self, other):
        # compare display names (not ids) since types with same names are likely functionally equivalent
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

class Star:
    def __init__(self, id, type, system_id):
        self.id = id
        self.type = type
        self.system_id = system_id

    def __repr__(self):
        return f'{self.type}'


class StarSystem:
    def __init__(self, id, name, loc, themes, star_list=None, planet_list=None):
        self.id = id
        self.name = name
        self.loc = loc
        self.themes = themes
        if star_list:
            self.stars = star_list
        else: 
            self.stars = []
        if planet_list:
            self.planets = planet_list
        else:
            self.planets = []
        self.dist = norm(loc)
        self.is_claimed = False

    def __repr__(self):
        return f'{self.name} ({len(self.planets)} planets {self.dist:0.1f}ly from center)'

    def add_planet(self, planet):
        self.planets.append(planet)
    
    def add_star(self, star):
        self.stars.append(star)

    def get_planet_num(self):
        return len(self.planets)

    def set_claimed(self):
        self.is_claimed = True


ORE_LEVELS = ['ore_sparse', 'ore_moderate', 'ore_abundant', 'ore_rich', 'ore_ultrarich']
RARE_ORE_LEVELS = ['rare_ore_sparse', 'rare_ore_moderate', 'rare_ore_abundant', 'rare_ore_rich', 'rare_ore_ultrarich']
FARMLAND_LEVELS = ['farmland_poor', 'farmland_adequate', 'farmland_rich', 'farmland_bountiful']
ORGANICS_LEVELS = ['organics_trace', 'organics_common', 'organics_abundant', 'organics_plentiful']
VOLATILES_LEVELS = ['volatiles_trace', 'volatiles_diffuse', 'volatiles_abundant', 'volatiles_plentiful']
RUINS_LEVELS = ['ruins_scattered', 'ruins_widespread', 'ruins_extensive', 'ruins_vast']

COMBINED_RESOURCE_LEVELS = ORE_LEVELS + RARE_ORE_LEVELS + FARMLAND_LEVELS + ORGANICS_LEVELS + VOLATILES_LEVELS + RUINS_LEVELS

res_vals = [-1, 0, 1, 2]
res_vals_ores = res_vals + [3]
RESOURCE_MAP = dict(zip(ORE_LEVELS, res_vals_ores))
RESOURCE_MAP.update(dict(zip(RARE_ORE_LEVELS, res_vals_ores)))
RESOURCE_MAP.update(dict(zip(FARMLAND_LEVELS, res_vals)))
RESOURCE_MAP.update(dict(zip(ORGANICS_LEVELS, res_vals)))
RESOURCE_MAP.update(dict(zip(VOLATILES_LEVELS, res_vals)))
RESOURCE_MAP.update(dict(zip(RUINS_LEVELS, res_vals)))

ORE_LEVELS = [Condition(level) for level in ORE_LEVELS]
RARE_ORE_LEVELS = [Condition(level) for level in RARE_ORE_LEVELS]
FARMLAND_LEVELS = [Condition(level) for level in FARMLAND_LEVELS]
ORGANICS_LEVELS = [Condition(level) for level in ORGANICS_LEVELS]
VOLATILES_LEVELS = [Condition(level) for level in VOLATILES_LEVELS]
RUINS_LEVELS = [Condition(level) for level in RUINS_LEVELS]

# ^^^ refactor how this spaghetti works later

class Sector:
    MIN_HAZARD = 9999
    MAX_HAZARD = 0

    def __init__(self):
        self.systems = None
        self.planet_types = None
        self.star_types = None
        self.max_system_dist = None
        self.max_system_planet = None
        self.name = None
        self.seed = None
        self.modlist = []

    def load_from_xml(self, path):
        # get xml tree root
        campaign_xml_root = self.get_xml_root(path)
        # set global hazard map
        starsector_dir = os.path.dirname(path) + '/../..'
        if not HAZARD_COND_MAP:
            set_hazard_cond_map(starsector_dir)
        if not COND_ID_TO_NAME_MAP:
            set_cond_id_name_maps(starsector_dir)
        if not TYPE_ID_TO_NAME_MAP:
            set_type_id_name_maps(starsector_dir)
        # get systems and planets
        id_system_map = self.get_initial_id_system_map(campaign_xml_root)
        id_system_map = self.assign_planets_to_systems(campaign_xml_root, id_system_map)
        self.systems = list(id_system_map.values())
        # calculate stats
        self.planet_types = set()
        self.star_types = set()
        self.all_conditions = set()
        self.all_themes = set()
        self.max_system_dist = 0
        self.max_system_planet_num = 0
        for system in self.systems:
            self.max_system_dist = max(self.max_system_dist, system.dist)
            self.max_system_planet_num = max(self.max_system_planet_num, system.get_planet_num())
            self.all_themes.update(system.themes)
            for planet in system.planets:
                self.planet_types.add(planet.type)
                self.all_conditions.update(planet.conditions)
                Sector.MIN_HAZARD = min(Sector.MIN_HAZARD, planet.hazard)
                Sector.MAX_HAZARD = max(Sector.MAX_HAZARD, planet.hazard)
            for star in system.stars:
                self.star_types.add(star)
        if None in self.all_conditions:
            self.all_conditions.remove(None)
        self.name = self.get_save_name(campaign_xml_root)
        self.seed = self.get_seed(campaign_xml_root)
        self.modlist = self.get_modlist(campaign_xml_root)

    def get_xml_root(self, path):
        tree = etree.parse(path)
        root = tree.getroot()
        print(f'Loaded XML file structure from {path.split("/")[-1]}')
        return root

    def get_save_name(self, campaign_xml_root):
        return campaign_xml_root.find('characterData').find('name').text

    def get_seed(self, campaign_xml_root):
        return campaign_xml_root.find('seedString').text

    def get_modlist(self, campaign_xml_root):
        mod_nodes = campaign_xml_root.find('modAndPluginData').find('allModsEverEnabled')
        modlist = []
        for mod_node in mod_nodes:
            try:
                mod_id = mod_node.find('spec').find('id').text
                modlist.append(mod_id)
            except AttributeError:
                continue
        return modlist

    def get_initial_id_system_map(self, campaign_xml_root):
        # read the system id's listed at top level in the xml
        system_index = campaign_xml_root.find('starSystems')
        system_ids = [system.get('ref') for system in system_index]
        system_tags = ['s', 'Sstm', 'cL']#, 't']
        system_nodes = self.get_system_nodes(campaign_xml_root, system_tags, system_ids)
        print(f'Found {len(system_nodes)} out of {len(system_index)} systems')
        # create dict mapping system id (int) to each system (StarSystem)
        id_system_map = {}
        for system_node in system_nodes:
            #print([node.tag for node in system_node])
            try:
                print('\t', [node.tag for node in system_node.find('o').find('saved')])
            except:
                print('\texcepted')
            system = self.get_system_from_xml_node(campaign_xml_root, system_node)
            id_system_map[system.id] = system
        if missing_system_ids := [id for id in system_ids if id not in id_system_map]:
            print(f'Looking for {len(missing_system_ids)} missing systems')
            missing_system_nodes = self.get_system_nodes(campaign_xml_root, ['*'], missing_system_ids)
            print(f'Nonstandard system tags: {", ".join([node.tag for node in missing_system_nodes])}')
            for system_node in missing_system_nodes:
                system = self.get_system_from_xml_node(campaign_xml_root, system_node)
                id_system_map[system.id] = system
        print(f"Mapped ID's to systems")
        return id_system_map

    def get_system_nodes(self, campaign_xml_root, system_tags, system_ids):
        # use search string which includes all of the system id's concatenated together
        # to search for each of the tag nodes which define the contents of the listed systems
        hyperspace_node = campaign_xml_root.find('starSystems')
        id_search_str = '|' + '|'.join(system_ids) + '|'
        expr = '|'.join([f"//{system_tag}[contains('{id_search_str}', concat('|', @z, '|'))]" for system_tag in system_tags])
        system_nodes = hyperspace_node.xpath(expr)
        return system_nodes
        
    def get_system_from_xml_node(self, campaign_xml_root, system_node):
        ly_per_px = 1/2000
        sys_id = system_node.get('z')
        name = system_node.get('dN')
        # read location from the <l> tag
        # if <l> is empty, then it references the tag which stores the loc with its ref attrib
        location_node = system_node.find('l')
        if location_node.text:
            loc_px = location_node.text.split('|')
        else:
            loc_px = campaign_xml_root.find(f".//locInHyper[@z='{location_node.get('ref')}']").text.split('|')          
        loc_ly = [ly_per_px*float(coord) for coord in loc_px]
        themes = [tag.text for tag in system_node.find('tags')]
        return StarSystem(sys_id, name, loc_ly, themes)

    def assign_planets_to_systems(self, campaign_xml_root, id_system_map):
        # find all <Plnt> tags with an id 'z' attrib (the ones with definitions)
        hyperspace_node = campaign_xml_root.find('starSystems')
        planet_nodes = hyperspace_node.xpath('//Plnt[@z]')
        print(f'Found {len(planet_nodes)} planets')
        for planet_node in planet_nodes:
            # tag showing if it's a planet or star
            tag = planet_node.find('tags').find('st').text
            if tag == 'planet':
                if new_planet := self.get_planet_from_xml_node(planet_node):
                    id_system_map[new_planet.system_id].add_planet(new_planet)
                    if new_planet.inhabited:
                        id_system_map[new_planet.system_id].set_claimed()
            elif tag == 'star':
                new_star = self.get_star_from_xml_node(planet_node)
                id_system_map[new_star.system_id].add_star(new_star)
        print(f'Assigned {len(planet_nodes)} planets to {len(id_system_map)} systems')
        return id_system_map

    def get_planet_from_xml_node(self, planet_node):
        id = planet_node.get('z')
        system_id = planet_node.find('cL').get('ref')
        market_node = planet_node.find('market')
        type_id = planet_node.find('type').text
        type = Type(type_id, TYPE_ID_TO_NAME_MAP[type_id])
        if market_node is not None and (name_node := market_node.find('name')) is not None:
            name = name_node.text
            conditions = []
            # if it's uninhabited, it stores the planet conditions in tags inside a <cond> tag
            if (cond_list_node := market_node.find('cond')) is not None:
                for node in cond_list_node:
                    cond_id = node.text
                    hazard = None
                    res_level = None
                    if cond_id in HAZARD_COND_MAP:
                        hazard = HAZARD_COND_MAP[cond_id]
                    if cond_id in RESOURCE_MAP:
                        res_level = RESOURCE_MAP[cond_id]
                    conditions.append(Condition(cond_id, COND_ID_TO_NAME_MAP[cond_id], hazard, res_level))
            # otherwise it stores conditions in the 'i' attrib of tags inside a <conditions> tag
            else:
                for node in market_node.find('conditions'):
                    if cond_id := node.get('i'):
                        hazard = None
                        res_level = None
                        if cond_id in HAZARD_COND_MAP:
                            hazard = HAZARD_COND_MAP[cond_id]
                        if cond_id in RESOURCE_MAP:
                            res_level = RESOURCE_MAP[cond_id]
                        conditions.append(Condition(cond_id, COND_ID_TO_NAME_MAP[cond_id], hazard, res_level))
            is_inhabited = any([condition.id.startswith('population') for condition in conditions])
            return Planet(id, name, type, conditions, system_id, is_inhabited)
        else:
            return None

    def get_star_from_xml_node(self, planet_node):
        id = planet_node.get('z')
        system_id = planet_node.find('cL').get('ref')
        type_id = planet_node.find('type').text
        type = Type(type_id, TYPE_ID_TO_NAME_MAP[type_id])
        return Star(id, type, system_id)
                
    def get_matching_systems(self, system_requirement):
        matching_systems = []
        for system in self.systems:
            if system_requirement.check(system):
                matching_systems.append(system)
        return matching_systems

    def get_hazard_range(self):
        return Sector.MIN_HAZARD, Sector.MAX_HAZARD


class PlanetReq:
    next_id = 0
    def __init__(self, desired_types=[], desired_conditions=[], desired_resources=[], desired_hazard=None, exclusive_type_mode=False, exclusive_cond_mode=False):
        self.desired_types = desired_types
        self.desired_conditions = desired_conditions
        self.desired_resources = desired_resources
        if desired_resources:
            # get better resource levels to match the search (e.q. if 'ore_sparse', search should also match 'ore_rich' etc)
            self.desired_resources_levels = [self.get_better_resource_levels(desired_resource_level) for desired_resource_level in desired_resources]
        self.desired_hazard = desired_hazard
        self.exclusive_type_mode = exclusive_type_mode
        self.exclusive_cond_mode = exclusive_cond_mode
        PlanetReq.next_id += 1
        self.id = PlanetReq.next_id 

    def __eq__(self, other):
        return self.id == other.id

    def check(self, planet):
        if self.desired_types:
            if not self.exclusive_type_mode and planet.type not in self.desired_types:
                return False
            elif self.exclusive_type_mode and planet.type in self.desired_types:
                return False
        if self.desired_conditions:
            for cond in self.desired_conditions:
                if not self.exclusive_cond_mode and cond not in planet.conditions:
                    return False
                elif self.exclusive_cond_mode and cond in planet.conditions:
                    return False
        if self.desired_hazard is not None and planet.hazard > self.desired_hazard:
            return False
        if self.desired_resources:
            if not all([any([level in planet.resources for level in resource_levels]) for resource_levels in self.desired_resources_levels]):
                return False
        return True

    def get_better_resource_levels(self, desired_resource_level):
        resource_levels_list = [ORE_LEVELS, RARE_ORE_LEVELS, FARMLAND_LEVELS, ORGANICS_LEVELS, VOLATILES_LEVELS, RUINS_LEVELS]
        index_of_desired_resource_type = [desired_resource_level in resource_levels for resource_levels in resource_levels_list].index(True)
        desired_resource_levels = resource_levels_list[index_of_desired_resource_type]
        index_of_desired_level = desired_resource_levels.index(desired_resource_level)
        return desired_resource_levels[index_of_desired_level:]

    def __repr__(self):
        repr_str = ''
        #repr_str += f'{"/".join(self.desired_types)}'
        if self.desired_types:
            if self.exclusive_type_mode:
                repr_str += 'n'
            repr_str += f'one of {len(self.desired_types)} types'
        if self.desired_conditions:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'{len(self.desired_conditions)} '
            if not self.exclusive_cond_mode:
                repr_str +=  'req. conditions'
            else:
                repr_str += 'excl. conditions'
        if self.desired_hazard and self.desired_hazard != Sector.MAX_HAZARD:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'hazard =< {self.desired_hazard*100:0.0f}%'
        if self.desired_resources:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'{"/".join([cond.id for cond in self.desired_resources])}'
        if not repr_str:
            repr_str = 'no requirements'
        repr_str = '> planet: ' + repr_str
        return repr_str


class StarSystemReq:
    def __init__(self, max_distance=None, min_planet_num=None, planet_reqs=[], must_be_unclaimed=False, desired_theme=None):
        self.max_distance = max_distance
        self.planet_reqs = planet_reqs
        self.min_planet_num = min_planet_num
        self.must_be_unclaimed = must_be_unclaimed
        self.desired_theme = desired_theme

    def check(self, system):
        if self.max_distance is not None and system.dist > self.max_distance:
            return False
        if self.min_planet_num is not None and len(system.planets) < self.min_planet_num:
            return False
        if self.desired_theme is not None and self.desired_theme not in system.themes:
            return False
        all_reqs_fulfilled = True
        for p_req in self.planet_reqs:
            req_fulfilled = False
            for p in system.planets:
                if p_req.check(p):
                    req_fulfilled = True
                    break
            if req_fulfilled == False:
                all_reqs_fulfilled = False
                break
        if not all_reqs_fulfilled:
            return False
        if self.must_be_unclaimed and system.is_claimed:
            return False
        return True
    
    def __repr__(self):
        return f'<sys req: at least {self.min_planet_num} planets at least {self.max_distance} from center with {self.planet_reqs}>'
