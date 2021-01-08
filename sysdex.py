from lxml import etree
import os
import matplotlib.pyplot as plt
import time
import numpy as np

os.chdir('C:/Users/Mario/Desktop/systemfinder')

with open('campaign.xml', 'r') as myFile:
    tree = etree.parse(myFile)


root = tree.getroot()
print(root.tag)

cond_map = {}
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
        self.cond = cond
        self.hazard = 1 + sum([float(cond_map[c]) for c in cond if c in cond_map])

    def __repr__(self):
        return f'{self.name} ({self.get_haz()*100:0.0f}% {self.type})'

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



start = time.time()

system_index = root.find('starSystems')
system_ids = [system.get('ref') for system in system_index]
#systems = {system.get('ref'):{} for system in system_index}
#print(system_ids)
#system_ids = system_ids[:3]
#expr = f".//*[@z={tuple(system_ids)}]"
#expr = f".//*[@z='{system_ids[1]}']"
search_str = '|' + '|'.join(system_ids) + '|'
#print(search_str)
expr = f".//*[contains('{search_str}', concat('|', @z, '|'))]"
#print(expr)
system_elements = root.xpath(expr)

systems = {}



for element in system_elements:
    name = element.get('dN')
    location_tag = element.find('l')
    if location_tag.text:
        loc = location_tag.text.split('|')
    else:
        loc = root.find(f".//*[@z='{location_tag.get('ref')}']").text.split('|')
    #systems[element.get('z')] = {'name':name, 'loc':loc, 'stars':[], 'planets':[]}
    sys_id = element.get('z')
    systems[sys_id] = StarSystem(sys_id, name, loc)

unique_types = set()

planet_elements = root.xpath('.//Plnt[@z]')
for el in planet_elements:
    system_id = el.find('cL').get('ref')
    tag = el.find('tags').find('st').text
    if tag == 'planet':
        id = el.get('z')
        market = el.find('market')
        type = el.find('type').text
        unique_types.add(type)
        if market:
            name = market.find('name').text
            if cond_node := market.find('cond'):
                cond = [node.text for node in cond_node]
            else:
                cond = [node.get('i') for node in market.find('conditions')]
            
            new_planet = Planet(id, name, type, cond)
            #systems[system_id]['planets'].append(new_planet)
            systems[system_id].add_planet(new_planet)
    elif tag == 'star':
        #systems[system_id]['stars'].append(el.find('type').text)
        systems[system_id].add_star(el.find('type').text)
    

#for k,v in systems.items():
#    print(f'{k}: {v}')


#for c in unique_conditions:
#    print(c)

#for k,v in cond_map.items():
#    print(f'{k}: {v}')

#for planet in systems['219015'].planets:
#    print(planet.name, planet.cond, planet.hazard)

#for typ in unique_types:
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

