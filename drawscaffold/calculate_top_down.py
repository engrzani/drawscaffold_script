from math import tan, radians

from drawscaffold.calculator.calculator_top_down import CalculatorTopDown
from drawscaffold.const.conts import VERTICAL_PART, HORIZONTAL_PART, FOOT_PART, FOOT_INSIDE_PART, ADJUSTMENT_SHAFT1, \
    ADJUSTMENT_SHAFT2, HALF_FOOT_PART, COMPLETE_FOOT_PART, ADJUSTMENT_SHAFT3, HALF_VERTICAL_PART, DIAGONAL_PART
from drawscaffold.diagonal.diagnoal_drawer import draw_x_diagonal_pattern
from drawscaffold.diagonal.patterns.zigzag_pattern import draw_zigzag_diagonal_pattern
from drawscaffold.utils.debug_printer import DebugPrinter


class MaterialCounterTopDown:
    def __init__(self):
        self.counter_dict = dict()

    def material_add(self, material_name: str):
        if material_name in self.counter_dict.keys():
            self.counter_dict[material_name] += 1
            return

        self.counter_dict[material_name] = 1

def top_down_calc(verbose:bool, facades: dict, h: float, slope: float, toe_board: bool, use_x_pattern, use_zigzag_pattern):
    d = DebugPrinter(verbose)

    material_counter = MaterialCounterTopDown()
    top_down_counter = CalculatorTopDown()

    count_facades(facades, h, slope, toe_board, use_x_pattern, use_zigzag_pattern, material_counter, top_down_counter, d)

    return material_counter.counter_dict

def count_facades(facades: dict, h: float, slope: float, toe_board: bool,
                  use_x_pattern: bool, use_zigzag_pattern: bool,
                  material_counter: MaterialCounterTopDown, top_down_counter: CalculatorTopDown,
                  d: DebugPrinter, gap: int = 25):
    facade_keys = ['F', 'R', 'B', 'L'] # it is the order don't touch

    last_x = 0
    last_y = 0
    for key in facade_keys:
        if len(facades[key]) <= 0:
            continue

        last_pos = (last_x, last_y)

        if key == 'F':
            add_gap_value = (0, -gap)
        elif key == 'R':
            add_gap_value = (gap, 0)
        elif key == 'B':
            add_gap_value = (0, gap)
        else: # key == 'L'
            add_gap_value = (-gap, 0)

        last_pos = (last_pos[0] + add_gap_value[0], last_pos[1] + add_gap_value[1])

        total_length = int(str(facades[key][-1]).split(',')[2])
        console_count = 0
        for item in facades[key]:
            values = str(item).split(',')
            if len(values) < 5:
                continue

            func = str(values[0]).lower()
            pos = int(values[1])
            depth = int(values[3])

            d.print(f'pos: {pos}')
            d.print(f'depth: {depth}')

            calc_key1 = 'R' if key=='F' else 'B' if key == 'R' else 'L' if key == 'B' else 'B' if key == 'L' else ''
            calc_key2 = 'L' if key=='F' else '' if key == 'R' else '' if key == 'B' else 'F' if key == 'L' else ''

            total_cumulative_outset = 0
            if calc_key1:
                for cmd in facades[calc_key1]:
                    split_data = str(cmd).split(',')

                    if split_data[0] == 'outset':
                        total_cumulative_outset += int(split_data[-2])

            if calc_key2:
                for cmd in facades[calc_key2]:
                    split_data = str(cmd).split(',')

                    if split_data[0] == 'outset':
                        total_cumulative_outset += int(split_data[-2])

            if func == 'inset' and pos != 0:
                if key == 'F':
                    last_x = pos
                    pos = abs(pos - last_pos[0])

                    big_parts = pos // 250 # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    if depth <= 80 and overshoot:
                        last_x = pos + last_pos[0]
                        last_pos = (last_pos[0] - overshoot, last_pos[1])

                    else:
                        if leftover <= 80:
                            d.print(f'lastx değeri: {last_x}')

                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] + 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)

                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern, material_counter, top_down_counter, d)
                    scaffs = []

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x + gap
                    last_pos = (start_x_for_depth, last_pos[1])

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0] + console_count * 35 + 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'R':
                    last_y = pos
                    pos = abs(pos - last_pos[1] + total_cumulative_outset)

                    big_parts = pos // 250 # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    if depth <= 80 and overshoot:
                        last_y = pos + last_pos[1]
                        last_pos = (last_pos[0], last_pos[1] - overshoot)

                    else:
                        if leftover <= 80:
                            d.print(f'lasty değeri: {last_y}')

                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            last_pos = (last_pos[0], last_pos[1] - (leftover + 70 + gap) + 70)

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count!=0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y + gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1]  + console_count * 35 + 70)
                    last_y = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'B':
                    last_x = last_pos[0] - pos - 70

                    big_parts = pos // 250 # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    if depth <= 80 and overshoot:
                        last_x = pos + last_pos[0]
                        last_pos = (last_pos[0] + overshoot, last_pos[1])

                    else:
                        if leftover <= 80:
                            d.print(f'lastx değeri: {last_x}')

                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x - gap * 2 + 70
                    last_pos = (start_x_for_depth, last_pos[1])

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] - 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    last_pos = (last_pos[0] - console_count * 35 - 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'L':
                    # hedef: L cephesinde -Y yönüne doğru ilerliyoruz
                    last_y = total_length - pos - total_cumulative_outset
                    pos = abs(last_y - last_pos[1])

                    big_parts = pos // 250
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    # L'de çizim -Y yönünde: overshoot varsa başlangıcı +Y'ye kaydırmalıyız
                    if depth <= 80 and overshoot:
                        last_y = last_pos[1] - pos
                        last_pos = (last_pos[0], last_pos[1] + overshoot)
                    else:
                        if leftover <= 80:
                            d.print(f'lasty değeri: {last_y}')
                            # L'de burada - değil + olmalı (R ile ters)
                            last_pos = (last_pos[0], last_pos[1] + leftover + gap)

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count != 0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] - 250)

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] - 150)

                    depth_big_parts = depth // 250
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')

                    # inset L'de içeri dönüş +X yönüne olmalı
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] + 250, last_pos[1])

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] + 150, last_pos[1])

                    last_pos = (last_pos[0], last_pos[1] + console_count * 35 - 70)
                    last_y = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0
                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

            elif func == 'outset' and pos != 0:
                if key == 'F':
                    last_x = pos
                    pos = abs(pos - last_pos[0])

                    big_parts = pos // 250  # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] + 250, last_pos[1])  # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x - gap
                    last_pos = (start_x_for_depth, last_pos[1])

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    last_pos = (last_pos[0] - (console_count + 1) * 35 + gap, last_pos[1])
                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'R':
                    last_y = pos

                    d.print(f"r pos before: {pos}")
                    pos = abs(pos - last_pos[1] + total_cumulative_outset)

                    d.print(f"r pos after: {pos}")

                    big_parts = pos // 250 # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    if depth <= 80 and overshoot:
                        last_y = pos + last_pos[1]
                        last_pos = (last_pos[0], last_pos[1] - overshoot)

                    else:
                        if leftover <= 80:
                            d.print(f'lasty değeri: {last_y}')

                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            last_pos = (last_pos[0], last_pos[1] - (leftover + 70 + gap) + 70)

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count!=0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] + 250, last_pos[1]) # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1]  + console_count * 35 + 70)
                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'B':
                    last_x = last_pos[0] - pos - 70

                    big_parts = pos // 250 # count of big part
                    after_gap = (pos % 250) // 150
                    leftover = (pos % 250) % 150

                    overshoot = 0
                    if leftover != 0 and leftover <= 80:
                        after_gap += 1
                        overshoot = 150 - leftover

                    if depth <= 80 and overshoot:
                        last_x = pos + last_pos[0]
                        last_pos = (last_pos[0] + overshoot, last_pos[1])

                    else:
                        if leftover <= 80:
                            d.print(f'lastx değeri: {last_x}')

                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x - gap * 2 + 70
                    last_pos = (start_x_for_depth, last_pos[1])

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] - 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0] + console_count * 35 - 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0
                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

                if key == 'L':
                    last_y = total_length - pos - total_cumulative_outset + gap * 2
                    pos = abs(last_y - last_pos[1])

                    big_parts = pos // 250  # count of big part
                    after_gap = (pos % 250) // 150

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count != 0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    scaffs = []

                    for b_part in range(big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

                    for s_part in range(after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)
                    scaffs = []

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        scaffs.append(250)
                        last_pos = (last_pos[0] - 250, last_pos[1])  # length of scaffold

                    for s_part in range(depth_after_gap):
                        scaffs.append(150)
                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1] + console_count * 35 - 70)
                    d.print(f'L -> Kaldığı {last_pos}')

                    frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                         material_counter, top_down_counter, d)

        if key == 'F':
            pos = abs(total_length - last_pos[0] - total_cumulative_outset)

            big_parts = pos // 250  # count of big part
            after_gap = (pos % 250) // 150
            leftover = (pos % 250) % 150

            if 150 >= leftover >= 20:
                after_gap += 1

            scaffs = []

            for b_part in range(big_parts):
                scaffs.append(250)
                last_pos = (last_pos[0] + 250, last_pos[1])  # length of scaffold

            for s_part in range(after_gap):
                scaffs.append(150)
                last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

            last_x = total_length - total_cumulative_outset
            last_y = last_pos[1]

            frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                 material_counter, top_down_counter, d)

        if key == 'R':
            pos = total_length - last_pos[1] - total_cumulative_outset

            big_parts = pos // 250  # count of big part
            after_gap = (pos % 250) // 150
            leftover = (pos % 250) % 150

            if 150 >= leftover >= 20:
                after_gap += 1

            scaffs = []

            for b_part in range(big_parts):
                scaffs.append(250)
                last_pos = (last_pos[0], last_pos[1] + 250)  # length of scaffold

            for s_part in range(after_gap):
                scaffs.append(150)
                last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

            last_x = last_pos[0]
            last_y = total_length - total_cumulative_outset

            frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                 material_counter, top_down_counter, d)

        if key == 'B':
            last_pos = (last_pos[0], last_pos[1])
            pos = total_length - (total_length - last_pos[0])

            big_parts = pos // 250  # count of big part
            after_gap = (pos % 250) // 150
            leftover = (pos % 250) % 150

            if 150 >= leftover >= 20:
                after_gap += 1

            scaffs = []

            for b_part in range(big_parts):
                scaffs.append(250)
                last_pos = (last_pos[0] - 250, last_pos[1])  # length of scaffold

            for s_part in range(after_gap):
                scaffs.append(150)
                last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

            d.print(f'B SON : {last_pos}')
            last_x = 0
            last_y = last_pos[1] - gap
            frontal_calculator2D(scaffs, h, slope, toe_board, use_x_pattern, use_zigzag_pattern,
                                 material_counter, top_down_counter, d)

        if key == 'L':
            last_pos = (last_pos[0], last_pos[1] + 70 + gap)
            pos = total_length - (total_length - last_pos[1])

            big_parts = pos // 250  # count of big part
            after_gap = (pos % 250) // 150

            scaffs = []

            for b_part in range(big_parts):
                scaffs.append(250)
                last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

            for s_part in range(after_gap):
                scaffs.append(150)
                last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

            last_x = last_pos[0]
            last_y = total_length - total_cumulative_outset
            frontal_calculator2D(scaffs, h, 0, toe_board, use_x_pattern, use_zigzag_pattern,
                                 material_counter, top_down_counter, d)

def frontal_calculator2D(length_list: list[int], h: float, slope: float, toe_board: bool,
                         use_x_pattern: bool, use_zigzag_pattern: bool,
                         material_counter: MaterialCounterTopDown, counter: CalculatorTopDown, d: DebugPrinter):
    floor_count = int(h // (VERTICAL_PART - 20))

    def y_on_surface(x, width_cm, base_y, slope_deg):
        x0 = width_cm / 2.0
        m = tan(radians(slope_deg))
        return base_y - m * (x - x0)

    # calculate start points if surface have slope
    start_points = []
    surface_horizontal = 0
    for i in range(len(length_list) + 1):
        surface_point = y_on_surface(surface_horizontal, len(length_list), 0, slope)
        start_points.append(surface_point)

        surface_horizontal += HORIZONTAL_PART

    d.print(start_points)
    biggest_point = max(start_points)

    # make it zero
    start_x_points = 0
    module_idx = 0
    connection_centers = [[] for i in range(len(length_list) + 1)]

    for start_point in start_points:
        difference = biggest_point - start_point

        if difference < 0:
            d.print("mesafe 0'dan küçük geçiyoruz burayı ki bu mümkün olmamalı")
        elif difference == 0:
            foot_start = (start_x_points, start_point)
            lock_center, name = counter.foot(foot_start, lock_start_y=start_point + 0.5)

            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)

        elif difference >= (VERTICAL_PART - 20):
            gap = difference % (VERTICAL_PART - 20)
            vertical_count = int(difference // (VERTICAL_PART - 20))

            if gap <= (FOOT_PART - FOOT_INSIDE_PART):
                foot_start = (start_x_points, start_point)
                lock_center, name = counter.foot(foot_start, lock_start_y=start_point + gap)

                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)

                last_y = foot_start[1] + gap
            elif gap <= (ADJUSTMENT_SHAFT1 * 0.8):
                lock_center, name = counter.adjustment((start_x_points, start_point), ADJUSTMENT_SHAFT1, gap)
                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)

                last_y = start_point + gap
            elif gap <= (ADJUSTMENT_SHAFT2 * 0.8):
                lock_center, name = counter.adjustment((start_x_points, start_point), ADJUSTMENT_SHAFT2, gap)

                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)
                last_y = start_point + gap
            elif gap <= (HALF_FOOT_PART - FOOT_INSIDE_PART):
                foot_start = (start_x_points, start_point)
                lock_center, name = counter.foot(foot_start, half_foot=True, lock_start_y=start_point + gap)

                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)
                last_y = foot_start[1] + gap
            elif gap <= (ADJUSTMENT_SHAFT3 * 0.8):
                lock_center, name = counter.adjustment((start_x_points, start_point), ADJUSTMENT_SHAFT3, gap)

                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)
                last_y = start_point + gap
            elif gap - (HALF_VERTICAL_PART - 20) <= (FOOT_PART - FOOT_INSIDE_PART):
                after_gap = gap - (HALF_VERTICAL_PART - 20)

                lock_y = start_point + after_gap
                lock_center, name = counter.foot(start_point=(start_x_points, start_point), lock_start_y=lock_y)

                last_y = lock_y

                _, name2 = counter.vertical(start_point=(start_x_points, last_y), half_vertical=True)
                connection_centers[module_idx].append(lock_center)

                material_counter.material_add(name)
                material_counter.material_add(name2)

                last_y += (HALF_VERTICAL_PART - 20)

            elif gap - (HALF_VERTICAL_PART - 20) <= (HALF_FOOT_PART - FOOT_INSIDE_PART):
                after_gap = gap - (HALF_VERTICAL_PART - 20)

                lock_y = start_point + after_gap
                lock_center, name = counter.foot(start_point=(start_x_points, start_point), half_foot=True,
                                                    lock_start_y=lock_y)

                last_y = lock_y

                _, name2 = counter.vertical(start_point=(start_x_points, last_y), half_vertical=True)
                connection_centers[module_idx].append(lock_center)

                material_counter.material_add(name)
                material_counter.material_add(name2)

                last_y += (HALF_VERTICAL_PART - 20)
            elif gap <= (COMPLETE_FOOT_PART - FOOT_INSIDE_PART):
                foot_start = (start_x_points, start_point)
                lock_center, name = counter.foot(foot_start, complete_foot=True, lock_start_y=start_point + gap)
                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)

                last_y = foot_start[1] + gap
            else:
                foot_y = COMPLETE_FOOT_PART - FOOT_INSIDE_PART
                slide_cm = gap - foot_y
                foot_start = (start_x_points, start_point + slide_cm)
                lock_center, name = counter.foot(foot_start, complete_foot=True)
                connection_centers[module_idx].append(lock_center)

                last_y = foot_start[1] + foot_y

                lock_center, name2 = counter.vertical((start_x_points, last_y))
                connection_centers[module_idx].append(lock_center)

                material_counter.material_add(name)
                material_counter.material_add(name2)

                last_y += (VERTICAL_PART - 20)

            for vertical in range(vertical_count):
                lock_center, name = counter.vertical((start_x_points, last_y))
                connection_centers[module_idx].append(lock_center)
                material_counter.material_add(name)

                last_y += (VERTICAL_PART - 20)

        elif difference <= (FOOT_PART - FOOT_INSIDE_PART):
            foot_start = (start_x_points, start_point)

            lock_center, name = counter.foot(foot_start, lock_start_y=start_point + difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        elif difference <= (ADJUSTMENT_SHAFT1 * 0.8):
            slide_cm = (ADJUSTMENT_SHAFT1 * 0.8) - difference
            adj_start = (start_x_points, start_point - slide_cm)

            lock_center, name = counter.adjustment(adj_start, ADJUSTMENT_SHAFT1, difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        elif difference <= (ADJUSTMENT_SHAFT2 * 0.8):
            slide_cm = (ADJUSTMENT_SHAFT2 * 0.8) - difference
            adj_start = (start_x_points, start_point - slide_cm)

            lock_center, name = counter.adjustment(adj_start, ADJUSTMENT_SHAFT2, difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        elif difference <= (HALF_FOOT_PART - FOOT_INSIDE_PART):
            foot_start = (start_x_points, start_point)

            lock_center, name = counter.foot(foot_start, half_foot=True, lock_start_y=start_point + difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        elif difference <= (ADJUSTMENT_SHAFT3 * 0.8):
            slide_cm = (ADJUSTMENT_SHAFT3 * 0.8) - difference
            adj_start = (start_x_points, start_point - slide_cm)

            lock_center, name = counter.adjustment(adj_start, ADJUSTMENT_SHAFT3, difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        elif difference <= (COMPLETE_FOOT_PART - FOOT_INSIDE_PART):
            foot_start = (start_x_points, start_point)

            lock_center, name = counter.foot(foot_start, complete_foot=True, lock_start_y=start_point + difference)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)
        else:
            slide_cm = difference - (COMPLETE_FOOT_PART - FOOT_INSIDE_PART)
            foot_start = (start_x_points, start_point + slide_cm)

            lock_center, name = counter.foot(foot_start, complete_foot=True)
            connection_centers[module_idx].append(lock_center)
            material_counter.material_add(name)

        start_x_points += HORIZONTAL_PART
        module_idx += 1

    vertical_point = biggest_point

    tie_every_module = 2 if len(length_list) % 2 == 0 else 3 if len(length_list) % 3 == 0 else 5
    needed_calculate_tie = floor_count >= 4
    for vertical in range(floor_count):
        horizontal_point = 0
        connection_index = 0
        use_l_part = vertical == floor_count - 1
        is_first_floor = vertical == 0
        is_tie_needed = needed_calculate_tie and vertical >= 2
        m = 0
        for module in range(len(length_list)):
            should_calc_tie = is_tie_needed and module % tie_every_module == 0
            if should_calc_tie:
                tie = counter.tie()
                material_counter.material_add(tie)

            if use_l_part:
                l_part_connection_center, name = counter.L_part((horizontal_point, vertical_point))
                connection_centers[connection_index].append(l_part_connection_center)
            else:
                vertical_connection_center, name = counter.vertical((horizontal_point, vertical_point))
                connection_centers[connection_index].append(vertical_connection_center)

            material_counter.material_add(name)

            if toe_board and not is_first_floor:
                _, name2 = counter.sign("")
                material_counter.material_add(name2)

            _, name3 = counter.horizontal(small=length_list[module]==150)

            _, name4 = counter.support(small=length_list[module]==150)
            _, name5 = counter.support(small=length_list[module]==150)

            if not is_first_floor:
                material_counter.material_add(name3)

            material_counter.material_add(name3)
            material_counter.material_add(name4)
            material_counter.material_add(name5)

            horizontal_point += HORIZONTAL_PART

            connection_index += 1
            m = module

        m += 1
        if use_l_part:
            l_part, name = counter.L_part((horizontal_point, vertical_point))
        else:
            vertical_connection_center, name = counter.vertical((horizontal_point, vertical_point))
            connection_centers[connection_index].append(vertical_connection_center)

        should_calc_tie = is_tie_needed and m % tie_every_module == 0
        if should_calc_tie:
            tie = counter.tie()
            material_counter.material_add(tie)

        material_counter.material_add(name)

        vertical_point += (VERTICAL_PART - 20)

    if use_zigzag_pattern:
        diagonal_indexes = draw_zigzag_diagonal_pattern(
            connection_centers, None, len(length_list), DIAGONAL_PART, VERTICAL_PART, True, material_counter
        )
        d.print(diagonal_indexes)
    if use_x_pattern:
        draw_x_diagonal_pattern(connection_centers, None, len(length_list), floor_count, material_counter)

    for counter_key in material_counter.counter_dict.keys():
        material_counter.counter_dict[counter_key] = material_counter.counter_dict[counter_key]
