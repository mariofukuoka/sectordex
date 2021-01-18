import PySimpleGUI as sg
import sectorscouter as ss
from time import sleep
import starmapdrawer

# Color scheme
sg.theme('BrownBlue')

# Secondary windows
def get_import_progress_window():
    layout = [
        [sg.Frame('Status', [[sg.Output(size=(40,9), echo_stdout_stderr=True)]])]
    ]
    return sg.Window('Import in progress', layout, finalize=True)

def get_starmap_window(graph_bottom_left, graph_top_right):
    starmap = sg.Graph(
        canvas_size=(800, 800), 
        graph_bottom_left=graph_bottom_left, 
        graph_top_right=graph_top_right, 
        background_color='#111144',
        k='starmap_graph',
        float_values=True,
        enable_events=True,
        drag_submits=True
    )
    layout = [
        [sg.Button('Close', k='close_starmap_button')],
        [starmap]
    ]
    return sg.Window('Starmap', layout, finalize=True, element_justification='right')

'''
============================================================== Import panel ==============================================================
'''
# PATH INPUT AND IMPORT BUTTON
save_import_frame_data = [
    [sg.Input(size=(133, 5), k='path_input'), sg.FileBrowse(), sg.Button('Import selected', k='import_selected_button')]
    #[sg.Input(size=(146, 5), k='import_selected_button_path', readonly=True, enable_events=True), sg.FileBrowse(button_text='Import save')]
]
save_import_frame = sg.Frame('Import save (campaign.xml file)', save_import_frame_data)

'''
======================================================== System requirements panel ========================================================
'''
# MINIMUM PLANET NUMBER AND MAXIMUM SYSTEM DISTANCE SLIDERS
planet_num_slider = [[sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(59, 15),border_width=3,k='min_planet_num_slider')]]
dist_slider = [[sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(59, 15), resolution=5,border_width=3,k='max_dist_slider')]]
system_req_frame_data = [
    [sg.Frame('Minimum number of planets', planet_num_slider)],
    [sg.Frame('Maximum distance from map center in ly', dist_slider)]
]
system_req_frame = sg.Frame('System requirements', system_req_frame_data)

# ADDED PLANET REQUIREMENTS LIST
added_req_list = sg.Listbox(values=[], size=(74,5), pad=(9,9), enable_events=False, k='planet_req_listbox')

# PLANET TYPE LIST
planet_type_frame_data = [
    [sg.Listbox(values=[], size=(30, 19), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k='planet_types_listbox')],
    [sg.Button('Deselect all types', size=(15,1), k='deselect_all_types_button')]
]
planet_type_frame = sg.Frame('Planet Type', planet_type_frame_data)

# RESOURCE DROPDOWNS
ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
rare_ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
farmland_level_labels = ['-', 'poor', 'adequate', 'rich', 'bountiful']
organics_level_labels = ['-', 'trace', 'common', 'abundant', 'plentiful']
volatiles_level_labels = ['-', 'trace', 'diffuse', 'abundant', 'plentiful']
ruins_level_labels = ['-', 'scattered', 'widespread', 'extensive', 'vast']
ore_level_label_id_map = dict(zip(ore_level_labels, [None] + ss.ORE_LEVELS))
rare_ore_level_label_id_map = dict(zip(rare_ore_level_labels, [None] + ss.RARE_ORE_LEVELS))
farmland_level_label_id_map = dict(zip(farmland_level_labels, [None] + ss.FARMLAND_LEVELS))
organics_level_label_id_map = dict(zip(organics_level_labels, [None] + ss.ORGANICS_LEVELS))
volatiles_level_label_id_map = dict(zip(volatiles_level_labels, [None] + ss.VOLATILES_LEVELS))
ruins_level_label_id_map = dict(zip(ruins_level_labels, [None] + ss.RUINS_LEVELS))
res_label_col = [
    [sg.T('Ore: ')],
    [sg.T('Rare ore: ')],
    [sg.T('Farmland: ')],
    [sg.T('Organics: ')],
    [sg.T('Volatiles: ')],
    [sg.T('Ruins: ')]
]
res_dropdown_col = [
    [sg.Combo(ore_level_labels, size=(21, 5), default_value=ore_level_labels[0], k='ore_dropdown', readonly=True)],
    [sg.Combo(rare_ore_level_labels, size=(21, 5), default_value=rare_ore_level_labels[0], k='rare_ore_dropdown', readonly=True)],
    [sg.Combo(farmland_level_labels, size=(21, 5), default_value=farmland_level_labels[0], k='farmland_dropdown', readonly=True)],
    [sg.Combo(organics_level_labels, size=(21, 5), default_value=organics_level_labels[0], k='organics_dropdown', readonly=True)],
    [sg.Combo(volatiles_level_labels, size=(21, 5), default_value=volatiles_level_labels[0], k='volatiles_dropdown', readonly=True)],
    [sg.Combo(ruins_level_labels, size=(21, 5), default_value=ruins_level_labels[0], k='ruins_dropdown', readonly=True)]
]
res_frame_data = [
                [sg.Column(res_label_col), sg.Column(res_dropdown_col)]
            ]
resources_frame = sg.Frame('Resources', res_frame_data)

# HAZARD SLIDER
hazard_frame_data = [
    [sg.T(''), sg.Slider(range=(50,300),default_value=300,orientation='horizontal',size=(26, 20), resolution=25, border_width=4, k='hazard_slider')]
]
hazard_frame = sg.Frame('Maximum hazard', hazard_frame_data)

# MISC CHECKBOXES
misc_frame_data = [
    [sg.Checkbox('Exclude selected planet types in search', default=False, k='exclusive_types_checkbox',tooltip='Instead of searching for the selected types, search for all types except for the ones selected.')],
    [sg.Checkbox('Require Low-Gravity', default=False, k='require_low_grav_checkbox', enable_events=True)],
    [sg.Checkbox('Exclude High-Gravity', default=False, k='exclude_high_grav_checkbox', enable_events=True)]
]
misc_frame = sg.Frame('Miscellaneous', misc_frame_data)

# REQUIREMENTS PANEL LAYOUT (left half of main window)
planet_req_col_1 = sg.Column([
    [planet_type_frame]
])
planet_req_col_2 = sg.Column([
    [resources_frame],
    [hazard_frame],
    [misc_frame]
])
planet_req_frame_data = [
    [added_req_list],
    [sg.Button('Add requirement', pad=(9,0), size=(30,1), k='add_planet_req_button'), sg.Button('Remove selected', pad=(9,0), size=(30,1), k='remove_planet_req_button')],
    [planet_req_col_1, planet_req_col_2]
]
planet_req_frame = sg.Frame('Planet requirements', planet_req_frame_data)


'''
======================================================== Search results panel ========================================================
'''
# FOUND SYSTEMS LIST
system_list_frame_data = [
    [sg.Listbox(values=[], size=(70,10), enable_events=True, k='systems_listbox', right_click_menu=['', ['Show on sector map']])],
    [sg.Button('Show on map', k='show_on_map_button')]
]
system_list_frame = sg.Frame('Search results', system_list_frame_data, element_justification='right')

# SYSTEM DETAIL DESCRIPTION
system_details_frame_data = [
    [sg.Column([[sg.Text(size=(50,100), k='system_details_text')]], size=(492,500), scrollable=True)], #540
]
system_details_frame = sg.Frame('System Details', system_details_frame_data)

'''
========================================================= Main layout setup =========================================================
'''
req_col = sg.Column([
    [system_req_frame],
    [planet_req_frame],
    [sg.Button('Search for systems', size=(69,2), button_color=('white','#8B423F'), k='search_systems_button')]
])
results_col = sg.Column([
    [system_list_frame],
    [system_details_frame]
])
layout = [
    [save_import_frame],
    [req_col, sg.VerticalSeparator(), results_col]
]
main_win = sg.Window('Sector scouter', layout, finalize=True)
import_progress_win = None
starmap_win = None

'''
============================================================= Global vars ============================================================
'''
sector = ss.Sector()
drag_start_x, drag_start_y = 0, 0
drag_offset_x, drag_offset_y = 0, 0
is_dragging = False

'''
=========================================================== GUI event loop ===========================================================
'''
while True:
    win, event, values = sg.read_all_windows()

    if event == sg.WIN_CLOSED:
        if win is import_progress_win:
            pass
        elif win is not main_win:
            win.close()
        else:
            break

    # show on map handler
    elif event == 'show_on_map_button' or event == 'Show on sector map':
        if values['systems_listbox']:
            selected_system = values['systems_listbox'][0]
            if starmap_win is not None:
                starmap_win.close()
            canvas_lower_left, canvas_top_right, canvas_size, canvas_center = starmapdrawer.get_viewport_params(selected_system)
            starmap_win = get_starmap_window(canvas_lower_left, canvas_top_right)
            starmapdrawer.draw_polar_axes(starmap_win['starmap_graph'], radius=sector.max_system_dist, canvas_size=canvas_size)
            starmapdrawer.draw_stars(starmap_win['starmap_graph'], sector.systems, canvas_size)
            starmapdrawer.draw_labels(starmap_win['starmap_graph'], sector.systems, selected_system, canvas_size)

    elif event == 'close_starmap_button':
        starmap_win.close()

    # importing save file handler
    elif event == 'import_selected_button':
        path = main_win['path_input'].get()
        import_progress_win = get_import_progress_window()
        try:
            sector.load_from_xml(path)
            main_win['planet_types_listbox'].Update(values=sorted(list(sector.planet_types), key=lambda planet_type: planet_type.removeprefix('US_')))
            main_win['max_dist_slider'].Update(range=(0, sector.max_system_dist))
            main_win['max_dist_slider'].Update(value=sector.max_system_dist)
            main_win['min_planet_num_slider'].Update(range=(0, sector.max_system_planet_num))
            main_win['min_planet_num_slider'].Update(value=0)
            print('Import complete')
            sleep(0.5)
        except FileNotFoundError:
            sg.popup('Invalid path')
        import_progress_win.close()
    
    elif event == 'require_low_grav_checkbox':
        if values['require_low_grav_checkbox']:
            # deselect the high-grav checkbox cause it doesn't make sense to be able to select both, and vice versa in the event below
            main_win['exclude_high_grav_checkbox'].Update(value=False)

    elif event == 'exclude_high_grav_checkbox':
        if values['exclude_high_grav_checkbox']:
            main_win['require_low_grav_checkbox'].Update(value=False)

    elif event == 'remove_planet_req_button':
        curr_reqs = main_win['planet_req_listbox'].GetListValues()
        try:
            selected_val = main_win['planet_req_listbox'].get()[0]
            curr_reqs.remove(selected_val)
            main_win['planet_req_listbox'].Update(values=curr_reqs)
        except IndexError:
            pass

    elif event == 'deselect_all_types_button':
        main_win['planet_types_listbox'].SetValue([None])

    # pressing add new planet req handler
    elif event == 'add_planet_req_button':
        # get types from ui
        new_types = values['planet_types_listbox']
        # get resource reqs from ui
        new_resources = []
        if (ore_level := ore_level_label_id_map[main_win['ore_dropdown'].get()]) is not None:
            new_resources.append(ore_level)
        if (rare_ore_level := rare_ore_level_label_id_map[main_win['rare_ore_dropdown'].get()]) is not None:
            new_resources.append(rare_ore_level)
        if (farmland_level := farmland_level_label_id_map[main_win['farmland_dropdown'].get()]) is not None:
            new_resources.append(farmland_level)
        if (organics_level := organics_level_label_id_map[main_win['organics_dropdown'].get()]) is not None:
            new_resources.append(organics_level)
        if (volatiles_level := volatiles_level_label_id_map[main_win['volatiles_dropdown'].get()]) is not None:
            new_resources.append(volatiles_level)
        if (ruins_level := ruins_level_label_id_map[main_win['ruins_dropdown'].get()]) is not None:
            new_resources.append(ruins_level)
        # get hazard from ui
        new_hazard = values['hazard_slider']/100
        # create planet req object
        new_planet_req = ss.PlanetReq(
            desired_types=new_types, 
            desired_resources=new_resources, 
            desired_hazard=new_hazard,
            exclusive_type_mode=values['exclusive_types_checkbox'],
            require_low_gravity=values['require_low_grav_checkbox'],
            exclude_high_gravity=values['exclude_high_grav_checkbox']
        )
        # add planet req to listbox list
        curr_reqs = main_win['planet_req_listbox'].GetListValues()
        main_win['planet_req_listbox'].Update(values=curr_reqs + [new_planet_req])
        # reset planet req panel slider/dropdown/selection values to default
        main_win['planet_types_listbox'].SetValue([None])
        main_win['hazard_slider'].Update(value=main_win['hazard_slider'].DefaultValue)
        main_win['ore_dropdown'].Update(set_to_index=0)
        main_win['rare_ore_dropdown'].Update(set_to_index=0)
        main_win['farmland_dropdown'].Update(set_to_index=0)
        main_win['organics_dropdown'].Update(set_to_index=0)
        main_win['volatiles_dropdown'].Update(set_to_index=0)
        main_win['ruins_dropdown'].Update(set_to_index=0)
        main_win['exclusive_types_checkbox'].Update(value=False)
        main_win['require_low_grav_checkbox'].Update(value=False)
        main_win['exclude_high_grav_checkbox'].Update(value=False)

    # pressing search button handler
    elif event == 'search_systems_button':
        system_requirement = ss.StarSystemReq(
            max_distance=values['max_dist_slider'], 
            min_planet_num=values['min_planet_num_slider'], 
            planet_reqs=main_win['planet_req_listbox'].GetListValues()
            )

        matching_systems = sector.get_matching_systems(system_requirement)
        main_win['systems_listbox'].Update(values=sorted(matching_systems, key=lambda system: system.dist))
        main_win['system_details_text'].Update(value='')

    # selecting a system in the results handler
    elif event == 'systems_listbox':
        try:
            sys = values['systems_listbox'][0]
        except IndexError:
            sys = None
        if sys:
            detail_string = f'System coordinates: [{sys.loc[0]:0.1f}, {sys.loc[1]:0.1f}]\n' 
            detail_string += f'Distance from center: {sys.dist:0.1f}ly\n'
            detail_string += f'Stars: {", ".join(sys.stars)}\n\n'
            detail_string += f'Contains {len(sys.planets)} planets:\n'
            for i, planet in enumerate(sys.planets):
                detail_string += f'\n{i+1}. {planet}\n'
                for cond in planet.conditions:
                    detail_string += f'\t- {cond}\n'
        else:
            detail_string = ''
        main_win['system_details_text'].Update(value=detail_string)

    # mouse panning in the starmap handlers
    elif event == 'starmap_graph+UP':
        drag_offset_x, drag_offset_y = 0, 0
        is_dragging = False
        
    elif event == 'starmap_graph':
        if not is_dragging:
            drag_start_x, drag_start_y = values['starmap_graph']
            is_dragging = True
        else:
            starmap_win['starmap_graph'].move(-drag_offset_x, -drag_offset_y)
            drag_curr_x, drag_curr_y = values['starmap_graph']
            drag_offset_x = drag_curr_x - drag_start_x
            drag_offset_y = drag_curr_y - drag_start_y
            starmap_win['starmap_graph'].move(drag_offset_x, drag_offset_y)
    else:
        print(event)

main_win.close()


'''
Rest of gui greyed out before importing
Importing has a loading bar

Stable locs/Comm relays/Nav buoys/Sensor arrays slider

Only unclaimed systems checkbox

Edit requirements (with grayout)
'''