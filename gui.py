import PySimpleGUI as sg
import sectorscouter as ss

# All the stuff inside your window.
sg.theme('DarkTeal11')
# ================== save import ====================

save_import_frame_data = [
    [sg.Input(size=(133, 5), k='k_path'), sg.FileBrowse(), sg.Button('Import selected', k='k_import')] 
    ]

save_import_frame = sg.Frame('Import save (campaign.xml file)', save_import_frame_data)

# =================== system reqs ======================

planet_num_slider = [[sg.Slider(range=(0,15),default_value=0,orientation='horizontal',size=(59, 15),border_width=3,k='k_planet_num')]]

dist_slider = [[sg.Slider(range=(0,100000),default_value=100000,orientation='horizontal',size=(59, 15), resolution=5000,border_width=3,k='k_dist')]]

system_req_frame_data = [
    [sg.Frame('Minimum number of planets', planet_num_slider)],
    [sg.Frame('Maximum distance from map center', dist_slider)]
    ]

system_req_frame = sg.Frame('System requirements', system_req_frame_data)
# ================== planet types ===============================

planet_types = ['US_acid', 'US_acidRain', 'US_acidWind', 'US_alkali', 'US_arid', 'US_artificial', 'US_auric', 'US_auricCloudy', 'US_azure', 'US_barrenA', 'US_barrenB', 'US_barrenC', 'US_barrenD', 'US_barrenE', 'US_barrenF', 'US_blue', 'US_burnt', 'US_continent', 'US_crimson', 'US_desertA', 'US_desertB', 'US_desertC', 'US_dust', 'US_gas_giant', 'US_gas_giantB', 'US_green', 'US_iceA', 'US_iceB', 'US_jungle', 'US_lava', 'US_lifeless', 'US_lifelessArid', 'US_magnetic', 'US_purple', 'US_red', 'US_redWind', 'US_storm', 'US_volcanic', 'US_water', 'US_waterB', 'arid', 'barren', 'barren-bombarded', 'barren-desert', 'barren2', 'barren3', 'barren_castiron', 'barren_iron', 'barren_venuslike', 'br_lodestone', 'br_nanoplanet', 'cryovolcanic', 'desert', 'desert1', 'frozen', 'frozen1', 'frozen2', 'frozen3', 'gas_giant', 'ice_giant', 'ii_cobalt', 'ii_cydonia', 'ii_irradiated-bombarded', 'irradiated', 'istl_dysonshell', 'jungle', 'lava', 'lava_minor', 'rad_planet', 'rocky_ice', 'rocky_metallic', 'rocky_unstable', 'sen_gas_giant', 'staalo_type', 'terran', 'terran-eccentric', 'toxic', 'toxic_cold', 'tundra', 'water']

planet_type_frame_data = [
    [sg.Listbox(values=planet_types, size=(30, 22), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k='k_types')],
    [sg.Button('Deselect all types', size=(15,1), k='k_deselect')]
    ]

planet_type_frame = sg.Frame('Planet Type', planet_type_frame_data)

# ================== resources ============================

ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
rare_ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
farmland_level_labels = ['-', 'poor', 'adequate', 'rich', 'bountiful']
organics_level_labels = ['-', 'trace', 'common', 'abundant', 'plentiful']
volatiles_level_labels = ['-', 'trace', 'diffuse', 'abundant', 'plentiful']
ruins_level_labels = ['-', 'scattered', 'widespread', 'extensive', 'vast']

ore_level_label_id_map = dict(zip(ore_level_labels, [None] + ss.ore_levels))
rare_ore_level_label_id_map = dict(zip(rare_ore_level_labels, [None] + ss.rare_ore_levels))
farmland_level_label_id_map = dict(zip(farmland_level_labels, [None] + ss.farmland_levels))
organics_level_label_id_map = dict(zip(organics_level_labels, [None] + ss.organics_levels))
volatiles_level_label_id_map = dict(zip(volatiles_level_labels, [None] + ss.volatiles_levels))
ruins_level_label_id_map = dict(zip(ruins_level_labels, [None] + ss.ruins_levels))

res_label_col = [
    [sg.T('Farmland: ')],
    [sg.T('Ore: ')],
    [sg.T('Rare ore: ')],
    [sg.T('Organics: ')],
    [sg.T('Volatiles: ')],
    [sg.T('Ruins: ')]
    ]

res_dropdown_col = [
    [sg.Combo(ore_level_labels, size=(21, 5), default_value=ore_level_labels[0], k='k_ore_level', readonly=True)],
    [sg.Combo(rare_ore_level_labels, size=(21, 5), default_value=rare_ore_level_labels[0], k='k_rare_ore_level', readonly=True)],
    [sg.Combo(farmland_level_labels, size=(21, 5), default_value=farmland_level_labels[0], k='k_farmland_level', readonly=True)],
    [sg.Combo(organics_level_labels, size=(21, 5), default_value=organics_level_labels[0], k='k_organics_level', readonly=True)],
    [sg.Combo(volatiles_level_labels, size=(21, 5), default_value=volatiles_level_labels[0], k='k_volatiles_level', readonly=True)],
    [sg.Combo(ruins_level_labels, size=(21, 5), default_value=ruins_level_labels[0], k='k_ruins_level', readonly=True)]
    ]

res_frame_data = [
                [sg.Column(res_label_col), sg.Column(res_dropdown_col)]
            ]

resources_frame = sg.Frame('Resources', res_frame_data)

# ============== hazard ==========================

hazard_frame_data = [
    [sg.T(''), sg.Slider(range=(50,300),default_value=300,orientation='horizontal',size=(26, 20), resolution=25, border_width=4, k='k_hazard')]
    ]

hazard_frame = sg.Frame('Maximum hazard', hazard_frame_data)

# ============== misc ==========================

misc_frame_data = [
    [sg.Checkbox('Exclude selected planet types in search', default=False, tooltip='Instead of searching for the selected types, search for all types except for the ones selected.')],
    [sg.Checkbox('Require Low-Gravity', default=False)],
    [sg.Checkbox('Exclude High-Gravity', default=False)]
    ]

misc_frame = sg.Frame('Miscellaneous', misc_frame_data)

# ===================== planet req lis ================

added_req_list = sg.Listbox(values=[], size=(74,5), pad=(9,9), enable_events=False, k='k_reqs')
# ===================== planet req panel ====================

planet_req_col_1 = sg.Column([
    [planet_type_frame]
    ])

planet_req_col_2 = sg.Column([
    [resources_frame],
    [hazard_frame],
    [misc_frame],
    [sg.T('                      '), sg.Button('Search for systems', size=(20,2), button_color=('white','#CA3433'), k='k_search')]
    ])

planet_req_frame_data = [
    [added_req_list],
    [sg.Button('New requirement', pad=(9,0), size=(30,1), k='k_new_req'), sg.Button('Remove selected', pad=(9,0), size=(30,1), k='k_remove_req')],
    [planet_req_col_1, planet_req_col_2]
    ]

planet_req_frame = sg.Frame('Planet requirements', planet_req_frame_data)


# ============== search results ============================

system_list_frame_data = [
    [sg.Listbox(values=[], size=(70,10), enable_events=True, k='k_systems')]
    #[sg.Output(size=(70,15))]
    ]

system_list_frame = sg.Frame('Search results', system_list_frame_data,)

system_details_frame_data = [
    [sg.Text(size=(63,34), k='k_details')]
    ]

system_details_frame = sg.Frame('System Details', system_details_frame_data)


results_col = sg.Column([
    [system_list_frame],
    [system_details_frame]
    ])

# ============== layout ===========================

req_col = sg.Column([
    [system_req_frame],
    [planet_req_frame]
    ])

layout = [
            [save_import_frame],
            [req_col, sg.VerticalSeparator(), results_col]
         ]

root = None
system_list = []
unique_planet_list = []
selected_last = None


# Create the Window
window = sg.Window('Sector scouter', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'k_import':
        print('importing')
        path = window['k_path'].get()
        root = ss.get_campaign_xml_root(path)
        print('root imported')
        system_list, unique_planet_list = ss.get_system_list_from_xml(root)
        sg.popup('Save data imported')

    elif event == 'k_remove_req':
        curr_reqs = window['k_reqs'].GetListValues()
        try:
            selected_val = window['k_reqs'].get()[0]
            curr_reqs.remove(selected_val)
            window['k_reqs'].Update(values=curr_reqs)
        except IndexError:
            pass

    elif event == 'k_deselect':
        window['k_types'].SetValue([None])

    elif event == 'k_new_req':
        new_types = window['k_types'].get()

        new_resources = []
        if (ore_level := ore_level_label_id_map[window['k_ore_level'].get()]) is not None:
            new_resources.append(ore_level)
        if (rare_ore_level := rare_ore_level_label_id_map[window['k_rare_ore_level'].get()]) is not None:
            new_resources.append(rare_ore_level)
        if (farmland_level := farmland_level_label_id_map[window['k_farmland_level'].get()]) is not None:
            new_resources.append(farmland_level)
        if (organics_level := organics_level_label_id_map[window['k_organics_level'].get()]) is not None:
            new_resources.append(organics_level)
        if (volatiles_level := volatiles_level_label_id_map[window['k_volatiles_level'].get()]) is not None:
            new_resources.append(volatiles_level)
        if (ruins_level := ruins_level_label_id_map[window['k_ruins_level'].get()]) is not None:
            new_resources.append(ruins_level)

        new_hazard = values['k_hazard']/100
        #print(new_types, new_resources, new_hazard)
        curr_reqs = window['k_reqs'].GetListValues()
        window['k_reqs'].Update(values=curr_reqs + [ss.PlanetReq(desired_types=new_types, desired_resources=new_resources, desired_hazard=new_hazard)])

        window['k_types'].SetValue([None])
        window['k_dist'].Update(value=window['k_dist'].DefaultValue)
        window['k_planet_num'].Update(value=window['k_planet_num'].DefaultValue)
        window['k_ore_level'].Update(set_to_index=0)
        window['k_rare_ore_level'].Update(set_to_index=0)
        window['k_farmland_level'].Update(set_to_index=0)
        window['k_organics_level'].Update(set_to_index=0)
        window['k_volatiles_level'].Update(set_to_index=0)
        window['k_ruins_level'].Update(set_to_index=0)


    elif event == 'k_search':
        sys_req = ss.StarSystemReq(max_distance=values['k_dist'], min_planet_num=values['k_planet_num'], planet_reqs=window['k_reqs'].GetListValues())
        found_systems = []
        for s in system_list:
            if sys_req.check(s):
                '''
                print(s)
                for p in s.planets:
                    print('\t', p, p.conditions)
                '''
                found_systems.append(s)
        window['k_systems'].Update(values=found_systems)

    elif event == 'k_systems':
        sys = values['k_systems'][0]
        detail_string = f'System location: {sys.loc[0]}, {sys.loc[1]}\n\n'
        for i, planet in enumerate(sys.planets):
            detail_string += f'{i+1}. {planet}\n'
            for cond in planet.conditions:
                detail_string += f'\t{cond}\n'
        window['k_details'].Update(value=detail_string)



window.close()


'''
Rest of gui greyed out before importing
Importing has a loading bar


'''