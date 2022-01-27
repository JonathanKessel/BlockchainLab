# Python 3.7, use venv
# Generate Assets

import os
import svgwrite
from svgutils import transform as st

def createVisualCode(Asset, asset_path_svg, grid):
    """"generates the VisualCode for the given Asset object"""

    dwg = svgwrite.Drawing('asset_x', profile = 'Full', debug=False)
    dwg.viewbox(0, 0, 850.39, 1133.86) # set user coordinate space

    previous_shapes = dwg.add(dwg.g(id='previous'))    # add shapes from prev to group PREV
    token_shapes = dwg.add(dwg.g(id='token'))    # add shapes from prev to group PREV
    hash_shapes = dwg.add(dwg.g(id='hash'))    # add shapes from prev to group PREV

    # set amount of columns and rows of the shape matrix
    row = 1 # start-row
    col = 1 # start-column

    Shape_columns = grid
    Shape_rows = grid

    x_start = 208
    x_end = 605
    x_range = x_end - x_start
    y_start = 376
    y_end = 756 #before 756
    y_range = y_end - y_start

    digits = [int(Asset.previous), int(Asset.asset_id), int(Asset.hash)]
    print(digits)
    section = 0

    for item in digits:
        for digit in map(int, str(item)):

            x = x_start + ((col-1) * (x_range/(Shape_columns-1)))
            y = y_start + ((row-1) * (y_range/(Shape_rows-1)))

            if section == 0:
                previous_shapes.add(get_shape(digit, section, x, y, dwg, grid))

            if section == 1: #if token-section apply colours
                token_shapes.add(get_shape(digit, section, x, y, dwg, grid))

            if section == 2:
                hash_shapes.add(get_shape(digit, section, x, y, dwg, grid))

            col += 1
            
            if col == Shape_columns+1:  # if shape_position reaches the end of a row, jump to a new one and reset column counter

                if row == 4:
                    row +=1 #add blank row after section 1

                row += 1 # change row
                col = 1 #reset column index

        section += 1 #increase index counter
        print('Section: ' + str(section))

    name = str(Asset.asset_number)
    filename = '.temp/asset_%s-shape-only.svg' % name
    dwg.saveas(filename, pretty=True, indent=4)

    template = st.fromfile('base_assets/base_template_v2.svg')
    asset_svg = st.fromfile(filename)

    # if asset_svg file exists remove before saving
    if os.path.exists(asset_path_svg):
        os.remove(asset_path_svg)

    template.append(asset_svg)
    template.save(asset_path_svg)
    os.remove(filename) # remove shape_only file

def get_shape(digit, section, x, y, dwg, grid):

    shape_size = int(200 / grid)
    shapes_base_dir = '../base_assets/shapes/' # define directory for base assets

    shape_dict = {
                '0' : shapes_base_dir + 'shape_triangle_down',
                '1' : shapes_base_dir + 'shape_rect',
                '2' : shapes_base_dir + 'shape_triangle_top',
                '3' : shapes_base_dir + 'shape_triangle_left',
                '4' : shapes_base_dir + 'shape_circle',
                '5' : shapes_base_dir + 'shape_triangle_right',
            }

    colour_dict = {
                '0' : 'green',
                '1' : 'purple',
                '2' : 'red',
                '3' : 'blue',
                '4' : 'yellow',
                '5' : 'turquoise'
            }

    shape_path = shape_dict.get(str(digit))

    if section == 1: #if in token section
        shape_path = f"{shape_path}_{colour_dict.get(str(digit))}"

    if section == 2:
        shape_path = f"{shape_path}_grey"

    elif section == 0: #define standard color for previous and hash
        shape_path = f"{shape_path}_white"
    
    shape_path = f"{shape_path}.svg"

    return dwg.image(shape_path, insert =(x, y), size=(shape_size, shape_size))