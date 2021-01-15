import PySimpleGUI as sg
import sectorscouter as ss
from time import sleep
from math import ceil

# All the stuff inside your window.
sg.theme('BrownBlue')
# ================== save import ====================

save_import_frame_data = [
    [sg.Input(size=(133, 5), k='k_path_input'), sg.FileBrowse(), sg.Button('Import selected', k='k_import_selected_button')]
    #[sg.Input(size=(146, 5), k='k_import_selected_button_path', readonly=True, enable_events=True), sg.FileBrowse(button_text='Import save')]
    ]
save_import_frame = sg.Frame('Import save (campaign.xml file)', save_import_frame_data)

# =================== system reqs ======================

planet_num_slider = [[sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(59, 15),border_width=3,k='k_min_planet_num_slider')]]

dist_slider = [[sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(59, 15), resolution=5,border_width=3,k='k_max_dist_slider')]]

system_req_frame_data = [
    [sg.Frame('Minimum number of planets', planet_num_slider)],
    [sg.Frame('Maximum distance from map center in ly', dist_slider)]
    ]

system_req_frame = sg.Frame('System requirements', system_req_frame_data)
# ================== planet types ===============================

planet_type_frame_data = [
    [sg.Listbox(values=[], size=(30, 19), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k='k_planet_types_listbox')],
    [sg.Button('Deselect all types', size=(15,1), k='k_deselect_all_types_button')]
    ]

planet_type_frame = sg.Frame('Planet Type', planet_type_frame_data)

# ================== resources ============================

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
    [sg.Checkbox('Exclude selected planet types in search', default=False, k='k_exclusive_types',tooltip='Instead of searching for the selected types, search for all types except for the ones selected.')],
    [sg.Checkbox('Require Low-Gravity', default=False, k='k_require_low_grav_button', enable_events=True)],
    [sg.Checkbox('Exclude High-Gravity', default=False, k='k_exclude_high_grav_checkbox', enable_events=True)]
    ]

misc_frame = sg.Frame('Miscellaneous', misc_frame_data)

# ===================== planet req lis ================

added_req_list = sg.Listbox(values=[], size=(74,5), pad=(9,9), enable_events=False, k='k_planet_req_listbox')
# ===================== planet req panel ====================

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
    [sg.Button('Add requirement', pad=(9,0), size=(30,1), k='k_add_planet_req_button'), sg.Button('Remove selected', pad=(9,0), size=(30,1), k='k_remove_planet_req_button')],
    [planet_req_col_1, planet_req_col_2]
    ]

planet_req_frame = sg.Frame('Planet requirements', planet_req_frame_data)


# ============== search results ============================

system_list_frame_data = [
    [sg.Listbox(values=[], size=(70,10), enable_events=True, k='k_systems_listbox', right_click_menu=['', ['Show on sector map']])],
    [sg.Button('Show on map', k='k_show_on_map_button')]
    ]

system_list_frame = sg.Frame('Search results', system_list_frame_data, element_justification='right')

system_details_frame_data = [
    [sg.Column([[sg.Text(size=(50,100), k='k_system_details_text')]], size=(492,500), scrollable=True)], #540
    ]

system_details_frame = sg.Frame('System Details', system_details_frame_data)


results_col = sg.Column([
    [system_list_frame],
    [system_details_frame]
    #[sg.Frame('Status', [[sg.Output(size=(69, 5))]])]
    ])

# ============== layout ===========================

req_col = sg.Column([
    [system_req_frame],
    [planet_req_frame],
    [sg.Button('Search for systems', size=(69,2), button_color=('white','#8B423F'), k='k_search')]
    ])

layout = [
            [save_import_frame],
            [req_col, sg.VerticalSeparator(), results_col]
         ]


sector = ss.Sector()
unique_planet_list = []
selected_last = None

def get_import_progress_window():
    layout = [
        [sg.Frame('Status', [[sg.Output(size=(40,9), echo_stdout_stderr=True)]])],
        [sg.T('')]
    ]
    return sg.Window('Import in progress', layout, finalize=True)

def get_starmap_window(graph_bottom_left, graph_top_right):
    starmap = sg.Graph(
        canvas_size=(800, 800), 
        graph_bottom_left=graph_bottom_left, 
        graph_top_right=graph_top_right, 
        background_color='#000022',
        k='k_starmap_canvas',
        float_values=True,
        enable_events=True,
        drag_submits=True
        )

    layout = [
        [sg.Button('Close', k='k_close')],
        [starmap]
    ]
    return sg.Window('Starmap', layout, finalize=True, element_justification='right')

# Create the Window
window = sg.Window('Sector scouter', layout, finalize=True)
import_progress_win = None
starmap_win = None


size_supergiant = 0.4
size_giant = 0.3
size_normal = 0.2
size_dwarf = 0.1

# color strings
star_brown = 'maroon'
star_red = '#bb0000'
star_orange = 'darkorange'
star_yellow = 'gold'
star_white = 'whitesmoke'
star_blue = 'aqua'

#radius, fill color, line color, line width
star_draw_params = {
    'star_red_supergiant':[size_supergiant, star_red],
    'star_blue_supergiant':[size_supergiant, star_blue], 
    'star_red_giant':[size_giant, star_red], 
    'US_star_red_giant':[size_giant, star_red],
    'star_blue_giant':[size_giant, star_blue], 
    'US_star_blue_giant':[size_giant, star_blue],      
    'star_orange_giant':[size_giant, star_orange], 
    
    'star_yellow':[size_normal, star_yellow], 
    'US_star_yellow':[size_normal, star_yellow], 
    'star_orange':[size_normal, star_orange], 
    'star_neutron':[size_dwarf, 'lightcyan'], 
    'star_white':[size_dwarf, star_white], 
    
    'US_star_white':[size_dwarf, star_white], 
    'star_red_dwarf':[size_dwarf, star_red],
    'star_browndwarf':[size_dwarf, star_brown], 
    'US_star_browndwarf':[size_dwarf, star_brown], 
    'black_hole':[size_normal, 'black', 'white', 1],
    'istl_sigmaworld':[size_normal, 'limegreen'],
    }

drag_start_x, drag_start_y = 0, 0
drag_offset_x, drag_offset_y = 0, 0
is_dragging = False

def round_up_to_multiple_of_n(num, n):
    return ceil(num/n)*n

# Event Loop to process "events" and get the "values" of the inputs
# ====================================================================================================================================
while True:
    win, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED:
        if win != window:
            print(win)
            win.close()
        else:
            break
    elif event == 'k_close':
        starmap_win.close()
    elif event == 'k_show_on_map_button' or event == 'Show on sector map':
        try:
            selected_system = values['k_systems_listbox'][0]
        except IndexError:
            selected_system = None
        if selected_system:
            canvas_padding = 0
            text_padding = 0.2
            canvas_size = max(abs(selected_system.loc[0]), abs(selected_system.loc[1]))
            canvas_center = [coord/2 for coord in selected_system.loc]
            canvas_lower_left = (canvas_center[0] - canvas_size - canvas_padding, canvas_center[1] - canvas_size - canvas_padding)
            canvas_top_right = (canvas_center[0] + canvas_size + canvas_padding, canvas_center[1] + canvas_size + canvas_padding)
            #canvas_lower_left = (min(0, selected_system.loc[0]) - canvas_padding, min(0, selected_system.loc[1]) - canvas_padding)
            #canvas_top_right = (max(0, selected_system.loc[0]) + canvas_padding, max(0, selected_system.loc[1]) + canvas_padding)
            if starmap_win is not None:
                starmap_win.close()
            starmap_win = get_starmap_window(canvas_lower_left, canvas_top_right)
            
            axis_color = 'mediumblue'
            axis_line_width = 1
            axis_tick_interval = 5
            axis_tick_max_dist = round_up_to_multiple_of_n(sector.max_system_dist, axis_tick_interval)
            starmap_win['k_starmap_canvas'].DrawLine((0, axis_tick_max_dist), (0, -axis_tick_max_dist), axis_color, axis_line_width)
            starmap_win['k_starmap_canvas'].DrawLine((axis_tick_max_dist, 0), (-axis_tick_max_dist, 0), axis_color, axis_line_width)
            for dist in range(axis_tick_interval, axis_tick_max_dist, axis_tick_interval):
                starmap_win['k_starmap_canvas'].DrawCircle((0,0), dist, None, axis_color, axis_line_width)
                starmap_win['k_starmap_canvas'].DrawText(f'{dist}LY', (dist+text_padding, 2*text_padding), axis_color, text_location=sg.TEXT_LOCATION_LEFT)
                starmap_win['k_starmap_canvas'].DrawText(f'{dist}LY', (-dist-text_padding, 2*text_padding), axis_color, text_location=sg.TEXT_LOCATION_RIGHT)
                starmap_win['k_starmap_canvas'].DrawText(f'{dist}LY', (text_padding, dist+2*text_padding), axis_color, text_location=sg.TEXT_LOCATION_LEFT)
                starmap_win['k_starmap_canvas'].DrawText(f'{dist}LY', (text_padding, -dist-2*text_padding), axis_color, text_location=sg.TEXT_LOCATION_LEFT)

            for curr_system in sector.systems:
                x, y = curr_system.loc
                # if inhabited: draw text
                if curr_system.name.endswith('Nebula'):
                    starmap_win['k_starmap_canvas'].DrawCircle((x,y), 0.3, None, 'indigo', 80/canvas_size)
                else:
                    try:
                        star = curr_system.stars[0]
                        starmap_win['k_starmap_canvas'].DrawCircle(*([(x,y)] + star_draw_params[star]))
                    except IndexError:
                        starmap_win['k_starmap_canvas'].DrawCircle(*([(x,y)] + star_draw_params['star_yellow']))
                        #starmap_win['k_starmap_canvas'].DrawText(curr_system.name, (x+text_padding, y+text_padding), 'white', text_location=sg.TEXT_LOCATION_LEFT)
                    except KeyError as e:
                        print('key error', e)
                        starmap_win['k_starmap_canvas'].DrawCircle((x,y), size_norm, 'white')
                        starmap_win['k_starmap_canvas'].DrawText('?', (x, y), 'black')
            starmap_win['k_starmap_canvas'].DrawText(selected_system.name, [coord+text_padding for coord in selected_system.loc], 'white', text_location=sg.TEXT_LOCATION_LEFT)
    elif event == 'k_import_selected_button':
        path = window['k_path_input'].get()
        import_progress_win = get_import_progress_window()
        try:
            sector.load_from_xml(path)
            window['k_planet_types_listbox'].Update(values=sorted(list(sector.planet_types), key=lambda planet_type: planet_type.removeprefix('US_')))
            window['k_max_dist_slider'].Update(range=(0, sector.max_system_dist))
            window['k_max_dist_slider'].Update(value=sector.max_system_dist)
            window['k_min_planet_num_slider'].Update(range=(0, sector.max_system_planet_num))
            window['k_min_planet_num_slider'].Update(value=0)
            print('Import complete')
            sleep(0.5)
        except FileNotFoundError:
            sg.popup('Invalid path')
        import_progress_win.close()
    
    elif event == 'k_require_low_grav_button':
        if values['k_require_low_grav_button']:
            window['k_exclude_high_grav_checkbox'].Update(value=False)

    elif event == 'k_exclude_high_grav_checkbox':
        if values['k_exclude_high_grav_checkbox']:
            window['k_require_low_grav_button'].Update(value=False)

    elif event == 'k_remove_planet_req_button':
        curr_reqs = window['k_planet_req_listbox'].GetListValues()
        try:
            selected_val = window['k_planet_req_listbox'].get()[0]
            curr_reqs.remove(selected_val)
            window['k_planet_req_listbox'].Update(values=curr_reqs)
        except IndexError:
            pass

    elif event == 'k_deselect_all_types_button':
        window['k_planet_types_listbox'].SetValue([None])

    elif event == 'k_add_planet_req_button':
        new_types = values['k_planet_types_listbox']

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
        curr_reqs = window['k_planet_req_listbox'].GetListValues()

        new_planet_req = ss.PlanetReq(
            desired_types=new_types, 
            desired_resources=new_resources, 
            desired_hazard=new_hazard,
            exclusive_type_mode=values['k_exclusive_types'],
            require_low_gravity=values['k_require_low_grav_button'],
            exclude_high_gravity=values['k_exclude_high_grav_checkbox']
            )

        window['k_planet_req_listbox'].Update(values=curr_reqs + [new_planet_req])

        window['k_planet_types_listbox'].SetValue([None])
        window['k_hazard'].Update(value=window['k_hazard'].DefaultValue)
        window['k_ore_level'].Update(set_to_index=0)
        window['k_rare_ore_level'].Update(set_to_index=0)
        window['k_farmland_level'].Update(set_to_index=0)
        window['k_organics_level'].Update(set_to_index=0)
        window['k_volatiles_level'].Update(set_to_index=0)
        window['k_ruins_level'].Update(set_to_index=0)
        window['k_exclusive_types'].Update(value=False)
        window['k_require_low_grav_button'].Update(value=False)
        window['k_exclude_high_grav_checkbox'].Update(value=False)

    elif event == 'k_search':
        system_requirement = ss.StarSystemReq(
            max_distance=values['k_max_dist_slider'], 
            min_planet_num=values['k_min_planet_num_slider'], 
            planet_reqs=window['k_planet_req_listbox'].GetListValues()
            )

        matching_systems = sector.get_matching_systems(system_requirement)
        window['k_systems_listbox'].Update(values=sorted(matching_systems, key=lambda system: system.dist))
        window['k_system_details_text'].Update(value='')

    elif event == 'k_systems_listbox':
        try:
            sys = values['k_systems_listbox'][0]
        except IndexError:
            sys = None
        if sys:
            print(f'{sys.name} is claimed: {sys.is_claimed}')
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
        window['k_system_details_text'].Update(value=detail_string)

    elif event == 'k_starmap_canvas+UP':
        drag_offset_x, drag_offset_y = 0, 0
        is_dragging = False

    elif event == 'k_starmap_canvas':
        if not is_dragging:
            drag_start_x, drag_start_y = values['k_starmap_canvas']
            is_dragging = True
        else:
            starmap_win['k_starmap_canvas'].Move(-drag_offset_x, -drag_offset_y)
            drag_curr_x, drag_curr_y = values['k_starmap_canvas']
            drag_offset_x = drag_curr_x - drag_start_x
            drag_offset_y = drag_curr_y - drag_start_y
            starmap_win['k_starmap_canvas'].Move(drag_offset_x, drag_offset_y)
    else:
        print(event)
    

window.close()


'''
Rest of gui greyed out before importing
Importing has a loading bar

Stable locs/Comm relays/Nav buoys/Sensor arrays slider

Only unclaimed systems checkbox

Edit requirements (with grayout)
'''