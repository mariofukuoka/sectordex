from lxml import etree
import os
import matplotlib.pyplot as plt
import time
import numpy as np

os.chdir('C:/Users/Mario/Desktop/systemfinder')

with open('campaign.xml', 'r') as myFile:
    tree = etree.parse(myFile)
root = tree.getroot()

# set up condition map
cond_map = {}
# fMs is the tag of the element storing the hazard values, idk what it stands for
for fMs in root.findall(f".//hazard/fMs"):
    cond_id = '_'.join(fMs.get('s').split('_')[:-1])
    cond_hazard_val = fMs.get('v')
    cond_map[cond_id] = cond_hazard_val
del cond_map['haz']


class Planet:
    def __init__(self, id, name, type, cond):
        self.id = id
        self.name = name
        self.type = type
        self.conditions = set(cond)
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
        self.dist = np.linalg.norm(loc)

    def __repr__(self):
        return f'{self.name} ({len(self.planets)} planets {self.dist:0.0f} from center)'

    def add_planet(self, planet):
        self.planets.append(planet)
    
    def add_star(self, star):
        self.stars.append(star)

def get_initial_id_system_map(campaign_xml_root):
    # read the system id's listed at top level in the xml
    system_index = campaign_xml_root.find('starSystems')
    system_ids = [system.get('ref') for system in system_index]

    # use search string which includes all of the system id's concatenated together
    # to search for each of the tag elements which define the contents of the listed systems
    search_str = '|' + '|'.join(system_ids) + '|'
    expr = f".//*[contains('{search_str}', concat('|', @z, '|'))]"
    system_elements = campaign_xml_root.xpath(expr)

    # create dict mapping system id (int) to each system (StarSystem)
    id_system_map = {}

    for element in system_elements:
        name = element.get('dN')

        # read location from the <l> tag
        # if <l> is empty, then it references the tag which stores the loc with its ref attrib
        location_tag = element.find('l')
        if location_tag.text:
            loc = location_tag.text.split('|')
        else:
            loc = campaign_xml_root.find(f".//*[@z='{location_tag.get('ref')}']").text.split('|')

        sys_id = element.get('z')
        id_system_map[sys_id] = StarSystem(sys_id, name, loc)

    return id_system_map

def assign_planets_to_systems(campaign_xml_root, id_system_map):
    # create set to check all of the unique planet types along the way
    unique_types = set()

    # find all <Plnt> tags with an id 'z' attrib (the ones with definitions)
    planet_elements = root.xpath('.//Plnt[@z]')
    for el in planet_elements:
        # parent system id
        system_id = el.find('cL').get('ref')

        # tag showing if it's a planet or star
        tag = el.find('tags').find('st').text
        if tag == 'planet':
            id = el.get('z')
            market = el.find('market')
            type = el.find('type').text
            unique_types.add(type)
            if market:
                name = market.find('name').text
                # if it's uninhabited, it stores the planet conditions in tags inside a <cond> tag
                if cond_node := market.find('cond'):
                    cond = {node.text for node in cond_node}
                # otherwise it stores conditions in the 'i' attrib of tags inside a <conditions> tag
                else:
                    cond = {node.get('i') for node in market.find('conditions')}
                
                new_planet = Planet(id, name, type, cond)
                id_system_map[system_id].add_planet(new_planet)
        elif tag == 'star':
            id_system_map[system_id].add_star(el.find('type').text)
    return id_system_map, unique_types

#def assign_stable_locations_to_systems(campaign_xml_root, id_system_map):


def get_system_list_from_xml(campaign_xml_root):
    id_system_map = get_initial_id_system_map(campaign_xml_root)
    id_system_map, unique_planet_types = assign_planets_to_systems(campaign_xml_root, id_system_map)
    return list(id_system_map.values()), unique_planet_types



def get_resource_levels(desired_resource):
    ore_levels = ['ore_sparse', 'ore_moderate', 'ore_abundant', 'ore_rich', 'ore_ultrarich']
    rare_ore_levels = ['rare_ore_sparse', 'rare_ore_moderate', 'rare_ore_abundant', 'rare_ore_rich', 'rare_ore_ultrarich']
    farmland_levels = ['farmland_poor', 'farmland_adequate', 'farmland_rich', 'farmland_bountiful']
    organics_levels = ['organics_trace', 'organics_common', 'organics_abundant', 'organics_plentiful']
    volatiles_levels = ['volatiles_trace', 'volatiles_diffuse', 'volatiles_abudant', 'volatiles_plentiful']

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

class PlanetReq:
    def __init__(self, desired_types=None, desired_resources=None, desired_hazard=None):
        self.desired_types = desired_types
        self.desired_resources = desired_resources
        self.desired_resources_levels = [get_resource_levels(desired_resource) for desired_resource in desired_resources]
        self.desired_hazard = desired_hazard

    def check(self, planet):
        if self.desired_types is not None and planet.type not in self.desired_types:
            return False
        if self.desired_hazard is not None and planet.hazard > self.desired_hazard:
            return False
        if self.desired_resources_levels is not None:
            if not all([any([level in planet.conditions for level in resource_levels]) for resource_levels in self.desired_resources_levels]):
                return False
        return True
    
    def __repr__(self):
        return f'<planet req: {self.desired_type} with {self.desired_resources} and hazard below {self.desired_hazard}>'

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


# ====================================== main ======================================

system_list, unique_planet_types = get_system_list_from_xml(root)
#for i, s in enumerate(system_list):
#    print(i, s)



p_reqs = {
    PlanetReq(desired_resources={'farmland_poor', 'organics_trace', 'ore_sparse', 'rare_ore_sparse', 'volatiles_trace'}, desired_hazard=1.75)
    }

sys_req = StarSystemReq(planet_reqs=p_reqs)

for s in system_list:
    if sys_req.check(s):
        print(s)
        for p in s.planets:
            print('\t', p, p.conditions)


'''s = system_list[-4]
print(s, s.id)
for p in s.planets:
    print('\t', p, p.conditions)
p_reqs = {PlanetReq(desired_resources={'ore_sparse'})}
sys_req = StarSystemReq(60000, 4, p_reqs)
print(sys_req.check(s))'''


# ORE:
# sparse -1
# moderate 0 
# abundant 1
# rich 2
# ultrarich 3

# FARMLAND:
# poor -1
# adequate 0
# rich 1
# bountiful 2

# ORGANICS:
# trace -1
# common 0
# abundant 1
# plentiful 2

# VOLATILES:
# trace -1
# diffuse 0
# abundant 1
# plentiful 2

# RUINS:
# scattered
# widespread
# extensive
# vast



#for c in unique_conditions:
#    print(c)

#for k,v in cond_map.items():
#    print(f'{k}: {v}')

#for planet in systems['219015'].planets:
#    print(planet.name, planet.cond, planet.hazard)

#for typ in unique_planet_types:
#    print(typ)

#for s in sorted(systems.values(), key=lambda s: len(s.planets), reverse=True)[:5]:
#    print(s)





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

