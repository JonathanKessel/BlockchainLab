# Python 3.7, use venv

import random
import json
import os
import yaml
import shutil
from base6_conversion import fromDeci
from generate_assets import createVisualCode
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

class Asset:
    """"Asset class"""
    
    def __init__(self, previous, asset_id, asset_number):
        self.previous = previous
        self.asset_id = asset_id
        self.asset_number = asset_number
        self.hash = self.generate_hash() # hash=SELF, Naming jedoch Hash wegen namenskonflikt zu self)
    
    def generate_hash(self):
        """"Generates the Hash of each Asset based on the PREVIOUS and the TOKEN"""
        # jeweils ersten stelle von previous sowie asset nehmen und zusammensetzen --> PROVISORIUM!!
        prev_str = str(self.previous)
        asset_id_str = str(self.asset_id)
        return prev_str[:grid] + asset_id_str[:grid]  # results in a 12-digit-integer in base-6

with open(r'collection-config.yaml') as file:
    collection_config = yaml.load(file, Loader=yaml.FullLoader)

# calculate range based on collection grid
grid = collection_config.get('grid')
section_length = int((grid*grid)/3) #Value must be divisible through 3 without remainder.

digit_range_low = '1' # prefix lower range with 1
digit_range_up = '5'
for i in range(section_length-1):
    digit_range_low += '0'
    digit_range_up += '5'

digit_range_low_dec = int(str(digit_range_low), 6)
digit_range_up_dec = int(str(digit_range_up), 6)

# generate amount n of unique asset identifiers
asset_id_decimal = random.sample(range(digit_range_low_dec, digit_range_up_dec), collection_config.get('amount')+1)     # 2176782335 as it is the highest decimal number equivalent to a 12 digit base6 number (555555555555)

# Create List Object so store generated assets
collection = []

# Create Assets and store them in the collection list object
for i in range(collection_config.get('amount')):
    asset_id = fromDeci("", 6, asset_id_decimal[i+1])

    if i == 0:  # for genesis block use first asset id in list (generated one more as necessary)
        previous = fromDeci("", 6, asset_id_decimal[i])
    else:
        previous = collection.__getitem__(i-1).hash

    a = Asset(previous, asset_id, i+1)   # create new asset object
    
    # print out generated asset for debugging
    print('---- Asset-Number ' + str(a.asset_number) + ' ----')
    print('ASSET_ID: ' + str(a.asset_id))
    print('PREVIOUS: ' + str(a.previous))
    print('SELF/HASH: ' + str(a.hash))

    collection.append(a)   # add asset to collection

# create folder for collection assets
directory_path = './collection-' + collection_config.get('name') + '/'
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
if os.path.exists(directory_path): #remove path if present
    shutil.rmtree(directory_path)
    os.makedirs(directory_path)

collection_dict = {
    'collection_name' : collection_config.get('name'),
    'author': collection_config.get('author')
    }

# export Asset Metadata to JSON for each Asset individually
for Asset in collection:
    asset_dict = {
        'id' : Asset.asset_id,
        'name': collection_config.get('name') + ' No ' +  str(Asset.asset_number),
        'description': collection_config.get('general_description'),
        'image': 'https://raw.githubusercontent.com/pxlfrk/BlockchainLab/main/collection-' + collection_config.get('name') + '/asset_' + str(Asset.asset_number) + '.png',
        'author': collection_config.get('author')
    }

    name = str(Asset.asset_number)
    print('JSON for Asset-Number ' + str(Asset.asset_number) + ' created.')
    filename = 'asset_%s.json' % name
    filename_png = 'asset_%s.png' % name
    filename_png_backup = 'asset_%s_backup.png' % name
    filename_svg = 'asset_%s.svg' % name

    # add asset-ids to collection-json
    collection_dict.update({'asset_' + name : Asset.asset_id})

    collection_path = os.path.join(directory_path, filename)    # set file path to collection directory
    asset_path_png = os.path.join(directory_path, filename_png)
    asset_path_png_backup = os.path.join(directory_path, filename_png_backup)
    asset_path_svg = os.path.join(directory_path, filename_svg)

    with open(collection_path, 'w') as json_file:   # save json file
        json.dump(asset_dict, json_file, indent=4, sort_keys=True)

    # Generate Assets
    createVisualCode(Asset, asset_path_svg, grid)
    print('Visual Decoding added for Asset-Number ' + str(Asset.asset_number))

    # convert generated SVGs to PNG
    tmpconv = svg2rlg(asset_path_svg)
    renderPM.drawToFile(tmpconv, asset_path_png, fmt='PNG')
    renderPM.drawToFile(tmpconv, asset_path_png_backup, fmt='PNG')
    print('Asset-Number ' + str(Asset.asset_number) + ' converted into PNG.')


# export JSON with Metadata for the complete collection as well as all Asset-IDs
with open(os.path.join(directory_path, 'collection_info.json'), 'w') as json_file:   # save json file
    json.dump(collection_dict, json_file, indent=4, sort_keys=False)
