import argparse
import json

from drawscaffold.calculate_top_down import top_down_calc
from drawscaffold.calculator.price_calculator import calculate_price
from drawscaffold.drawer_top_down import top_down_drawer

parser = argparse.ArgumentParser(description='Draw scaffolds top-down professionally')
parser.add_argument("--facade", action="append", required=True, help="facade definition: inset/outset (optional),start,length,depth,F(ront)/R(ight)/L(eft)/B(ack)")

parser.add_argument("--image", action="store_true", help="get the drawing and image of it")
parser.add_argument("--svg", action="store_true", help="get the drawing and svg of it")
parser.add_argument("--dxf", action="store_true", help="get the drawing and dxf of it")

parser.add_argument("--height-in-cm", type=float, required=True, help="construct height in centimeter")
parser.add_argument("--surface-slope", type=float, required=True, help="surface slope")
parser.add_argument("--toe-board-text", action="store_true", help="the text on toe board")

pattern_group = parser.add_mutually_exclusive_group()
pattern_group.add_argument("--use-x-pattern", action="store_true", help="force to use X pattern for diagonals")
pattern_group.add_argument("--use-zigzag-pattern", action="store_true", help="force to use ZigZag pattern for diagonals")

parser.add_argument("--calculate", action="store_true", help="calculate the material count for the scaffold")
parser.add_argument("--calculate-price", action="store_true", help="calculate the material rent price for scaffold")

parser.add_argument("--project-name", type=str, default='project', help="The name of project")
parser.add_argument("--output-id", type=str, default=None, help="Optional output id for predictable filenames")
parser.add_argument("--verbose", action="store_true", help="gives outputs for debug")

args = parser.parse_args()
facades = args.facade
image = args.image
svg = args.svg
dxf = args.dxf
h = args.height_in_cm
slope = args.surface_slope
toe_board = args.toe_board_text
x_pattern = args.use_x_pattern
zigzag_pattern = args.use_zigzag_pattern
calculate = args.calculate
arg_calculate_price = args.calculate_price
project_name = args.project_name
output_id = args.output_id
verbose = args.verbose


if not facades or len(facades)==0:
    exit(-1)

facade_dict = {
    'F': [],
    'R': [],
    'L': [],
    'B': []
}

for facade in facades:
    for facade_key in facade_dict.keys():
        if facade_key in facade:
            facade_dict[facade_key].append(facade)

if len(facade_dict['F'])==0 and len(facade_dict['B'])!=0:
    facade_length = facade_dict['B'][-1].split(',')[2]
    default_text = f'inset,0,{facade_length},0,F'
    facade_dict['F'].append(default_text)
if len(facade_dict['B'])==0 and len(facade_dict['F'])!=0:
    facade_length = facade_dict['F'][-1].split(',')[2]
    default_text = f'inset,0,{facade_length},0,B'
    facade_dict['B'].append(default_text)
if len(facade_dict['R'])==0 and len(facade_dict['L'])!=0:
    facade_length = facade_dict['L'][-1].split(',')[2]
    default_text = f'inset,0,{facade_length},0,R'
    facade_dict['R'].append(default_text)
if len(facade_dict['L'])==0 and len(facade_dict['R'])!=0:
    facade_length = facade_dict['R'][-1].split(',')[2]
    default_text = f'inset,0,{facade_length},0,L'
    facade_dict['L'].append(default_text)

if calculate:
    material_dict = top_down_calc(verbose, facade_dict, h, slope, toe_board, x_pattern, zigzag_pattern)
    print(material_dict)

    exit(0)
if arg_calculate_price:
    material_dict = top_down_calc(verbose, facade_dict, h, slope, toe_board, x_pattern, zigzag_pattern)
    price, currency, symbol = calculate_price(material_dict)

    print(f"{price} {symbol}({currency})")
    exit(0)

file_paths = top_down_drawer(verbose, facade_dict, image, dxf, svg, project_name, output_id)
print(json.dumps({"paths": file_paths}))
