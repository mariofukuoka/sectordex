from lxml import etree
from numpy.linalg import norm
from time import time
import sys
from os import path

'''# set up condition map
cond_map = {}
# fMs is the tag of the node storing the hazard values, idk what it stands for
for fMs in root.findall(f".//hazard/fMs"):
    cond_id = '_'.join(fMs.get('s').split('_')[:-1])
    cond_hazard_val = fMs.get('v')
    cond_map[cond_id] = cond_hazard_val
del cond_map['haz']
'''

def get_campaign_xml_root(path):
    with open(path, 'r') as xml_file:
        tree = etree.parse(xml_file)
    root = tree.getroot()
    print(f'Loaded XML file structure from {xml_file.name.split("/")[-1]}')
    return root

cond_map = {
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
    def __init__(self, id, name, type, cond):
        self.id = id
        self.name = name
        self.type = type
        self.conditions = cond
        self.hazard = 1 + sum([float(cond_map[c]) for c in cond if c in cond_map])

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

    def __repr__(self):
        return f'{self.name} ({len(self.planets)} planets {self.dist:0.1f}ly from center)'

    def add_planet(self, planet):
        self.planets.append(planet)
    
    def add_star(self, star):
        self.stars.append(star)

    def get_planet_num(self):
        return len(self.planets)

def get_initial_id_system_map(campaign_xml_root):
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
    max_system_dist = 0
    iter_count, total_count = 0, len(system_nodes)

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
        max_system_dist = max(max_system_dist, norm(loc_ly))
        id_system_map[sys_id] = StarSystem(sys_id, name, loc_ly)
    print(f"Mapped ID's to systems")
    return id_system_map, max_system_dist

def assign_planets_to_systems(campaign_xml_root, id_system_map):
    # create set to check all of the unique planet types along the way
    unique_types = set()

    # find all <Plnt> tags with an id 'z' attrib (the ones with definitions)
    hyperspace_node = campaign_xml_root.find('starSystems')
    planet_nodes = hyperspace_node.xpath('//Plnt[@z]')
    print(f'Found {len(planet_nodes)} planets')

    max_system_planet_num = 0

    try:
        for planet_node in planet_nodes:
            system_id = planet_node.find('cL').get('ref')

            # tag showing if it's a planet or star
            tag = planet_node.find('tags').find('st').text
            if tag == 'planet':
                id = planet_node.get('z')
                market_node = planet_node.find('market')
                type = planet_node.find('type').text
                unique_types.add(type)
                if market_node is not None and (name_node := market_node.find('name')) is not None:
                    name = name_node.text
                    # if it's uninhabited, it stores the planet conditions in tags inside a <cond> tag
                    if (cond_node := market_node.find('cond')) is not None:
                        cond = {node.text for node in cond_node}
                    # otherwise it stores conditions in the 'i' attrib of tags inside a <conditions> tag
                    else:
                        cond = {node.get('i') for node in market_node.find('conditions')}

                    new_planet = Planet(id, name, type, cond)
                    id_system_map[system_id].add_planet(new_planet)
                    max_system_planet_num = max(max_system_planet_num, id_system_map[system_id].get_planet_num())

            elif tag == 'star':
                id_system_map[system_id].add_star(planet_node.find('type').text)
    except KeyError as e:
        key = int(str(e).strip("'"))
        print(f'ERROR: system z="{key}" not parsed from XML')
    print(f'Assigned {len(planet_nodes)} planets to {len(id_system_map)} systems')
    return id_system_map, unique_types, max_system_planet_num

#def assign_stable_locations_to_systems(campaign_xml_root, id_system_map):


def get_system_list_from_xml(campaign_xml_root):
    id_system_map, max_system_dist = get_initial_id_system_map(campaign_xml_root)
    id_system_map, unique_planet_types, max_system_planet_num = assign_planets_to_systems(campaign_xml_root, id_system_map)
    return list(id_system_map.values()), unique_planet_types, max_system_dist, max_system_planet_num

ore_levels = ['ore_sparse', 'ore_moderate', 'ore_abundant', 'ore_rich', 'ore_ultrarich']
rare_ore_levels = ['rare_ore_sparse', 'rare_ore_moderate', 'rare_ore_abundant', 'rare_ore_rich', 'rare_ore_ultrarich']
farmland_levels = ['farmland_poor', 'farmland_adequate', 'farmland_rich', 'farmland_bountiful']
organics_levels = ['organics_trace', 'organics_common', 'organics_abundant', 'organics_plentiful']
volatiles_levels = ['volatiles_trace', 'volatiles_diffuse', 'volatiles_abundant', 'volatiles_plentiful']
ruins_levels = ['ruins_scattered', 'ruins_widespread', 'ruins_extensive', 'ruins_vast']

def get_resource_levels(desired_resource):
    if desired_resource in ore_levels:
        return ore_levels[ore_levels.index(desired_resource):]
    elif desired_resource in rare_ore_levels:
        return rare_ore_levels[rare_ore_levels.index(desired_resource):]
    elif desired_resource in farmland_levels:
        return farmland_levels[farmland_levels.index(desired_resource):]
    elif desired_resource in organics_levels:
        return organics_levels[organics_levels.index(desired_resource):]
    elif desired_resource in volatiles_levels:
        return volatiles_levels[volatiles_levels.index(desired_resource):]
    elif desired_resource in ruins_levels:
        return ruins_levels[ruins_levels.index(desired_resource):]
    else:
        raise KeyError('Invalid resource string')

class PlanetReq:
    def __init__(self, desired_types=[], desired_resources=[], desired_hazard=None, exclusive_type_mode=False, require_low_gravity=False, exclude_high_gravity=False):
        self.desired_types = desired_types
        self.desired_resources = desired_resources
        if desired_resources:
            self.desired_resources_levels = [get_resource_levels(desired_resource) for desired_resource in desired_resources]
        self.desired_hazard = desired_hazard
        self.exclusive_type_mode = exclusive_type_mode
        self.require_low_gravity = require_low_gravity
        self.exclude_high_gravity = exclude_high_gravity

    def check(self, planet):
        if self.desired_types:
            if not self.exclusive_type_mode and planet.type not in self.desired_types:
                return False
            elif self.exclusive_type_mode and planet.type in self.desired_types:
                return False
        if self.desired_hazard is not None and planet.hazard > self.desired_hazard:
            return False
        if self.require_low_gravity and 'low_gravity' not in planet.conditions:
            return False
        if self.exclude_high_gravity and 'high_gravity' in planet.conditions:
            return False
        if self.desired_resources:
            if not all([any([level in planet.conditions for level in resource_levels]) for resource_levels in self.desired_resources_levels]):
                return False
        return True

    def __repr__(self):
        repr_str = ''
        if self.desired_types and self.exclusive_type_mode:
            repr_str += 'not '
        repr_str += f'{"/".join(self.desired_types)}'
        if self.desired_resources:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'at least {"/".join(self.desired_resources)}'
        if self.desired_hazard:
            if repr_str != '':
                repr_str += ', '
            repr_str += f'hazard below {self.desired_hazard*100:0.0f}%'
        if self.require_low_gravity:
            if repr_str != '':
                repr_str += ', '
            repr_str += 'lo-grav'
        if self.exclude_high_gravity:
            if repr_str != '':
                repr_str += ', '
            repr_str += 'non hi-grav'
        repr_str = '- planet: ' + repr_str
        return repr_str

class StarSystemReq:
    def __init__(self, max_distance=None, min_planet_num=None, planet_reqs=None):
        self.max_distance = max_distance
        self.planet_reqs = planet_reqs
        self.min_planet_num = min_planet_num

    def check(self, sys):
        if self.max_distance is not None and sys.dist > self.max_distance:
            #print('max dist check failed')
            return False

        if self.min_planet_num is not None and len(sys.planets) < self.min_planet_num:
            #print('planet num check failed')
            return False

        all_reqs_fulfilled = True
        for p_req in self.planet_reqs:
            req_fulfilled = False
            for p in sys.planets:
                if p_req.check(p):
                    req_fulfilled = True
                    break
            if req_fulfilled == False:
                #print(f'check failed for: {p_req}')
                all_reqs_fulfilled = False
                break
        if not all_reqs_fulfilled:
            return False

        return True
    
    def __repr__(self):
        return f'<sys req: at least {self.min_planet_num} planets at least {self.max_distance} from center with {self.planet_reqs}>'

# desired theme
# stable locs

'''x = []
y = []
txt = []
for s in systems.values():
    if len(s['loc']) == 2:
        x.append(float(s['loc'][0]))
        y.append(float(s['loc'][1]))
        txt.append(s['name'].removesuffix(' Star System'))

fig, ax = plt.subplots()

ax.scatter(x, y)
for i, annotation in enumerate(txt):
    ax.annotate(annotation, (x[i], y[i]))
print(time.time() - start)
plt.show()'''

