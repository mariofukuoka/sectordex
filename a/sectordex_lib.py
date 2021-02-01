from lxml import etree
from numpy.linalg import norm
#from time import time

ORE_LEVELS = ['ore_sparse', 'ore_moderate', 'ore_abundant', 'ore_rich', 'ore_ultrarich']
RARE_ORE_LEVELS = ['rare_ore_sparse', 'rare_ore_moderate', 'rare_ore_abundant', 'rare_ore_rich', 'rare_ore_ultrarich']
FARMLAND_LEVELS = ['farmland_poor', 'farmland_adequate', 'farmland_rich', 'farmland_bountiful']
ORGANICS_LEVELS = ['organics_trace', 'organics_common', 'organics_abundant', 'organics_plentiful']
VOLATILES_LEVELS = ['volatiles_trace', 'volatiles_diffuse', 'volatiles_abundant', 'volatiles_plentiful']
RUINS_LEVELS = ['ruins_scattered', 'ruins_widespread', 'ruins_extensive', 'ruins_vast']
COMBINED_RESOURCE_LEVELS = ORE_LEVELS + RARE_ORE_LEVELS + FARMLAND_LEVELS + ORGANICS_LEVELS + VOLATILES_LEVELS + RUINS_LEVELS

HAZARD_COND_MAP = {
    'decivilized': '0.25',
    'hot': '0.25', 
    'habitable': '-0.25', 
    'water_surface': '0.25', 
    'no_atmosphere': '0.5', 
    'cold': '0.25', 
    'extreme_weather': '0.25', 
    'very_hot': '0.5', 
    'tectonic_activity': '0.25', 
    'meteor_impacts': '0.5', 
    'poor_light': '0.25', 
    'low_gravity': '0.25', 
    'very_cold': '0.5', 
    'thin_atmosphere': '0.25', 
    'high_gravity': '0.5', 
    'toxic_atmosphere': '0.5', 
    'dense_atmosphere': '0.5', 
    'extreme_tectonic_activity': '0.5', 
    'pollution': '0.25', 
    'inimical_biosphere': '0.25', 
    'mild_climate': '-0.25',
    'US_magnetic': '0.5',
    'US_artificial': '0.0',
    'US_storm': '0.25',
    #'US_special_no_pick': 'nan', 
    'US_shrooms': '0.0', 
    'US_mind': '0.0', 
    'US_bedrock': '-0.5', 
    #'US_tunnels': 'nan', 
    'US_virus': '0.5', 
    'US_religious': '0.0', 
    'US_base': '0.0', 
    'US_elevator': '0.0', 
    'US_floating': '-0.5', 
    'US_crash': '-0.5'
    }


class Planet:
    def __init__(self, id, name, type, conditions):
        self.id = id
        self.name = name
        self.type = type
        self.resources = [cond for cond in conditions if cond in COMBINED_RESOURCE_LEVELS]
        self.conditions = [cond for cond in conditions if cond not in COMBINED_RESOURCE_LEVELS]
        self.hazard_conditions = [cond for cond in conditions if cond in HAZARD_COND_MAP]
        self.hazard = 1 + sum([float(HAZARD_COND_MAP[cond]) for cond in self.hazard_conditions])

    def __repr__(self):
        return f'{self.name} ({self.hazard*100:0.0f}% {self.type})'


class StarSystem:
    def __init__(self, id, name, loc, star_list=None, planet_list=None):
        self.id = id
        self.name = name
        self.loc = loc
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


class Sector:
    def __init__(self):
        self.systems = None
        self.planet_types = None
        self.star_types = None
        self.max_system_dist = None
        self.max_system_planet = None

    def load_from_xml(self, path):
        # get systems and planets
        campaign_xml_root = self.get_xml_root(path)
        id_system_map = self.get_initial_id_system_map(campaign_xml_root)
        id_system_map = self.assign_planets_to_systems(campaign_xml_root, id_system_map)
        self.systems = list(id_system_map.values())
        # calculate stats
        self.planet_types = set()
        self.star_types = set()
        self.all_conditions = set()
        self.max_system_dist = 0
        self.max_system_planet_num = 0
        for system in self.systems:
            self.max_system_dist = max(self.max_system_dist, system.dist)
            self.max_system_planet_num = max(self.max_system_planet_num, system.get_planet_num())
            for planet in system.planets:
                self.planet_types.add(planet.type)
                self.all_conditions.update(planet.conditions)
            for star in system.stars:
                self.star_types.add(star)
        if None in self.all_conditions:
            self.all_conditions.remove(None)

    def get_xml_root(self, path):
        with open(path, 'r') as xml_file:
            tree = etree.parse(xml_file)
        root = tree.getroot()
        print(f'Loaded XML file structure from {xml_file.name.split("/")[-1]}')
        return root

    def get_initial_id_system_map(self, campaign_xml_root):
        # read the system id's listed at top level in the xml
        system_index = campaign_xml_root.find('starSystems')
        system_ids = [system.get('ref') for system in system_index]
        hyperspace_node = campaign_xml_root.find('starSystems')
        # use search string which includes all of the system id's concatenated together
        # to search for each of the tag nodes which define the contents of the listed systems
        id_search_str = '|' + '|'.join(system_ids) + '|'
        system_tags = ['s', 'Sstm', 'cL', 't']
        expr = '|'.join([f"//{system_tag}[contains('{id_search_str}', concat('|', @z, '|'))]" for system_tag in system_tags])
        system_nodes = hyperspace_node.xpath(expr)
        print(f'Found {len(system_nodes)} systems')
        # create dict mapping system id (int) to each system (StarSystem)
        id_system_map = {}
        for system_node in system_nodes:
            name = system_node.get('dN')
            # read location from the <l> tag
            # if <l> is empty, then it references the tag which stores the loc with its ref attrib
            location_node = system_node.find('l')
            if location_node.text:
                loc_px = location_node.text.split('|')
            else:
                loc_px = campaign_xml_root.find(f".//locInHyper[@z='{location_node.get('ref')}']").text.split('|')
            sys_id = system_node.get('z')
            loc_ly = [float(coord)/2000 for coord in loc_px]
            id_system_map[sys_id] = StarSystem(sys_id, name, loc_ly)
        print(f"Mapped ID's to systems")
        return id_system_map

    def assign_planets_to_systems(self, campaign_xml_root, id_system_map):
        # find all <Plnt> tags with an id 'z' attrib (the ones with definitions)
        hyperspace_node = campaign_xml_root.find('starSystems')
        planet_nodes = hyperspace_node.xpath('//Plnt[@z]')
        print(f'Found {len(planet_nodes)} planets')
       
        error_system_ids = []
        for planet_node in planet_nodes:
            try:
                system_id = planet_node.find('cL').get('ref')
                # tag showing if it's a planet or star
                tag = planet_node.find('tags').find('st').text
                if tag == 'planet':
                    id = planet_node.get('z')
                    market_node = planet_node.find('market')
                    type = planet_node.find('type').text
                    if market_node is not None and (name_node := market_node.find('name')) is not None:
                        name = name_node.text
                        # if it's uninhabited, it stores the planet conditions in tags inside a <cond> tag
                        if (cond_node := market_node.find('cond')) is not None:
                            cond = {node.text for node in cond_node}
                        # otherwise it stores conditions in the 'i' attrib of tags inside a <conditions> tag
                        else:
                            cond = {node.get('i') for node in market_node.find('conditions')}
                            id_system_map[system_id].set_claimed()
                        new_planet = Planet(id, name, type, cond)
                        id_system_map[system_id].add_planet(new_planet)
                        
                elif tag == 'star':
                    id_system_map[system_id].add_star(planet_node.find('type').text)
            except KeyError as e:
                key = str(e).strip("'")
                if key not in error_system_ids:
                    error_system_ids.append(key)
                    print(f'WARNING: system z="{key}" not parsed from XML')
        print(f'Assigned {len(planet_nodes)} planets to {len(id_system_map)} systems')
        return id_system_map

    def get_matching_systems(self, system_requirement):
        matching_systems = []
        for system in self.systems:
            if system_requirement.check(system):
                matching_systems.append(system)
        return matching_systems


class PlanetReq:
    next_id = 0
    def __init__(self, desired_types=[], desired_conditions = [], desired_resources=[], desired_hazard=None, exclusive_type_mode=False, exclusive_cond_mode=False):
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
        if self.desired_resources:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'at least {"/".join(self.desired_resources)}'
        if self.desired_hazard:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'hazard < {self.desired_hazard*100:0.0f}%'
        repr_str = '> planet: ' + repr_str
        return repr_str


class StarSystemReq:
    def __init__(self, max_distance=None, min_planet_num=None, planet_reqs=None):
        self.max_distance = max_distance
        self.planet_reqs = planet_reqs
        self.min_planet_num = min_planet_num

    def check(self, system):
        if self.max_distance is not None and system.dist > self.max_distance:
            return False

        if self.min_planet_num is not None and len(system.planets) < self.min_planet_num:
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

        return True
    
    def __repr__(self):
        return f'<sys req: at least {self.min_planet_num} planets at least {self.max_distance} from center with {self.planet_reqs}>'
