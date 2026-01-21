import os
from datetime import datetime

import cairosvg
import ezdxf
from PIL import Image
from ezdxf import units, bbox
from ezdxf.math import Vec3
from ezdxf.addons import MTextExplode, text2path
from ezdxf.addons.drawing import RenderContext, Frontend, layout
from ezdxf.addons.drawing.config import Configuration, ColorPolicy
from ezdxf.addons.drawing.svg import SVGBackend

from drawscaffold.const.top_down_enum import ScaffoldSide
from drawscaffold.shapes.shapes_top_down import DrawerTopView
from drawscaffold.utils.debug_printer import DebugPrinter

def top_down_drawer(verbose:bool, facades: dict, image: bool, dxf: bool, svg: bool, project_name: str, output_id: str = None):
    d = DebugPrinter(verbose)

    doc = ezdxf.new("R2018")
    doc.units = units.CM

    scaff_layer = doc.layers.add("scaff")
    scaff_layer.description = 'by ScaffAI'

    msp = doc.modelspace()

    drawer = DrawerTopView(msp, doc)
    drawer.line_building(facades)

    draw_facades(facades, drawer, d)

    file_paths = []
    if output_id is not None:
        suffix = str(output_id)
    else:
        suffix = str(int(datetime.now().timestamp()))
    project_name_parts = project_name.split(' ')
    project_name = "_".join(project_name_parts)

    if image:
        context = RenderContext(doc)
        backend = SVGBackend()
        Frontend(context, backend).draw_layout(msp, finalize=True)

        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        svg_path = os.path.abspath(f"{project_name}_top_down_{suffix}.svg")
        png_path = os.path.abspath(f"{project_name}_top_down_{suffix}.png")

        with open(svg_path, "wt", encoding="utf-8") as f:
            f.write(backend.get_string(page))

        cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=300)
        os.remove(svg_path)
        file_paths.append(png_path)

    if svg:
        context = RenderContext(doc)
        backend = SVGBackend()
        Frontend(context, backend, Configuration(color_policy=ColorPolicy.COLOR_SWAP_BW)).draw_layout(msp, finalize=True)

        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        svg_path = os.path.abspath(f"{project_name}_top_down_{suffix}.svg")
        with open(svg_path, "wt", encoding="utf-8") as f:
            f.write(backend.get_string(page))
        file_paths.append(svg_path)

    if dxf:
        ext = bbox.extents(msp)
        if ext is not None:
            (xmin, ymin, _), (xmax, ymax, _) = ext.extmin, ext.extmax
            msp.dxf_layout.dxf.extmin = ezdxf.math.Vec3(xmin, ymin, 0)
            msp.dxf_layout.dxf.extmax = ezdxf.math.Vec3(xmax, ymax, 0)
            doc.header["$EXTMIN"] = msp.dxf_layout.dxf.extmin
            doc.header["$EXTMAX"] = msp.dxf_layout.dxf.extmax

        with MTextExplode(msp) as xpl:
            for m in list(msp.query("MTEXT")):
                xpl.explode(m)

        for t in list(msp.query("TEXT")):
            text2path.explode(t, target=msp)

        dxf_path = os.path.abspath(f"{project_name}_{suffix}.dxf")
        doc.saveas(dxf_path)
        file_paths.append(dxf_path)

    # for thumbnail
    if dxf or image or svg:
        context = RenderContext(doc)
        backend = SVGBackend()
        Frontend(context, backend).draw_layout(msp, finalize=True)

        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        svg_path = os.path.abspath(f"{project_name}_temp_{suffix}.svg")
        png_path = os.path.abspath(f"{project_name}_temp_{suffix}.png")
        jpg_path = os.path.abspath(f"{project_name}_{suffix}.jpg")

        with open(svg_path, "wt", encoding="utf-8") as f:
            f.write(backend.get_string(page))

        cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=300)

        png_image = Image.open(png_path)
        rgb_im = png_image.convert("RGB")
        rgb_im.save(jpg_path)

        os.remove(svg_path)
        os.remove(png_path)
        file_paths.append(jpg_path)

    return file_paths

    if dxf:
        ext = bbox.extents(msp)
        if ext is not None:
            (xmin, ymin, _), (xmax, ymax, _) = ext.extmin, ext.extmax

            msp.dxf_layout.dxf.extmin = ezdxf.math.Vec3(xmin, ymin, 0)
            msp.dxf_layout.dxf.extmax = ezdxf.math.Vec3(xmax, ymax, 0)
            doc.header["$EXTMIN"] = msp.dxf_layout.dxf.extmin
            doc.header["$EXTMAX"] = msp.dxf_layout.dxf.extmax

        with MTextExplode(msp) as xpl:
            for m in list(msp.query("MTEXT")):
                xpl.explode(m)

        for t in list(msp.query("TEXT")):
            text2path.explode(t, target=msp)

        dxf_path = os.path.abspath(f"{project_name}_{suffix}.dxf")
        doc.saveas(dxf_path)
        file_paths.append(dxf_path)
    # for thumbnail
    if dxf or image or svg:
        context = RenderContext(doc)
        backend = SVGBackend()
        Frontend(context, backend).draw_layout(msp, finalize=True)

        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        svg_path = os.path.abspath(f"{project_name}_temp_{suffix}.svg")
        png_path = os.path.abspath(f"{project_name}_temp_{suffix}.png")
        jpg_path = os.path.abspath(f"{project_name}_{suffix}.jpg")

        with open(svg_path, "wt", encoding="utf-8") as f:
            f.write(backend.get_string(page))

        cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=300)

        png_image = Image.open(png_path)
        rgb_im = png_image.convert("RGB")
        rgb_im.save(jpg_path)

        os.remove(svg_path)
        os.remove(png_path)
        file_paths.append(jpg_path)

    return file_paths

def draw_facades(facades: dict, drawer: DrawerTopView, d: DebugPrinter, gap: int = 25):
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
            side = str(values[4]).lower()

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

                    big_parts = pos // 250  # count of big part
                    leftover = pos % 250
                    after_gap = 0

                    if leftover <= 180:
                        # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                        # gap da ekliyoruz çünkü köşeden gap boşluğu var
                        big_parts += 1
                        last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])
                    else:
                        after_gap = 1
                        overshoot = 150 - leftover
                        last_pos = (last_pos[0] - (overshoot + 70 + gap) + 70, last_pos[1])

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x + gap
                    last_pos = (start_x_for_depth, last_pos[1])

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0] + console_count * 35 + 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                if key == 'R':
                    last_y = pos
                    pos = abs(pos - last_pos[1] + total_cumulative_outset)

                    big_parts = pos // 250  # count of big part
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

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y + gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1]  + console_count * 35 + 70)
                    last_y = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                if key == 'B':
                    last_pos = (last_pos[0] - 70 - gap, last_pos[1])

                    big_parts = pos // 250  # count of big part
                    leftover = pos % 250
                    after_gap = 0

                    if leftover <= 180:
                        # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                        # gap da ekliyoruz çünkü köşeden gap boşluğu var
                        big_parts += 1
                        last_pos = (last_pos[0] + (leftover + gap), last_pos[1])
                    else:
                        after_gap = 1
                        overshoot = 150 - leftover
                        last_pos = (last_pos[0] + (overshoot + gap), last_pos[1])

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    last_x = last_pos[0] - 35

                    start_x_for_depth = last_x - gap * 2 + 70
                    last_pos = (start_x_for_depth, last_pos[1])

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    last_pos = (last_pos[0] - console_count * 35 - 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0

                if key == 'L':
                    # hedef: L cephesinde -Y yönüne doğru ilerliyoruz
                    last_y = total_length - pos - total_cumulative_outset
                    pos = abs(last_y - last_pos[1])

                    big_parts = pos // 250
                    leftover = pos % 250
                    after_gap = 0

                    if leftover <= 180:
                        # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                        # gap da ekliyoruz çünkü köşeden gap boşluğu var
                        big_parts += 1
                        last_pos = (last_pos[0] , last_pos[1] + leftover, last_pos[1])
                    else:
                        after_gap = 1
                        overshoot = 150 - leftover
                        last_pos = (last_pos[0], last_pos[1] - (overshoot + 70 + gap) + 70)

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count != 0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )
                        last_pos = (last_pos[0], last_pos[1] - 250)

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )
                        last_pos = (last_pos[0], last_pos[1] - 150)

                    depth_big_parts = depth // 250
                    depth_left_over = depth % 250
                    depth_after_gap = 0

                    if depth_left_over > 100:
                        depth_big_parts += 1
                        # TODO BURADAKİ 75 ŞAŞIRABİLİR
                        last_pos = (last_pos[0] - (depth_left_over + gap) + 75, last_pos[1])

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    d.print(f'depth posu: {last_pos}')

                    # inset L'de içeri dönüş +X yönüne olmalı
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )
                        last_pos = (last_pos[0] + 250, last_pos[1])

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )
                        last_pos = (last_pos[0] + 150, last_pos[1])

                    last_pos = (last_pos[0], last_pos[1] + console_count * 35 - 70)
                    last_y = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0
            elif func == 'outset' and pos != 0:
                if key == 'F':
                    last_x = pos
                    pos = abs(pos - last_pos[0])

                    big_parts = pos // 250  # count of big part
                    leftover = pos % 250
                    after_gap = 0

                    d.print(f"Front pos {pos}")
                    d.print(f"Front leftover {leftover}")
                    if (pos - 70 - gap) <= 250:
                        after_gap = 1
                        big_parts = 0
                    elif leftover <= 180:
                        # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                        # gap da ekliyoruz çünkü köşeden gap boşluğu var
                        big_parts += 1
                        last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])
                    else:
                        after_gap = 1
                        overshoot = 150 - leftover
                        last_pos = (last_pos[0] - (overshoot + 70 + gap) + 70, last_pos[1])

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 250, last_pos[1])  # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_left_over = depth % 250
                    depth_after_gap = 0

                    if gap < depth_left_over <= 180:
                        depth_big_parts += 1

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x - gap
                    last_pos = (start_x_for_depth, last_pos[1])

                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    last_pos = (last_pos[0] - (console_count + 1) * 35 + gap, last_pos[1])
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

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 250) # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] + 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.LEFT
                        )

                        last_pos = (last_pos[0], last_pos[1] + 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 250, last_pos[1]) # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1]  + console_count * 35 + 70)

                if key == 'B':
                    last_x = last_pos[0] - pos - 70

                    big_parts = pos // 250  # count of big part
                    leftover = pos % 250
                    after_gap = 0

                    d.print(f"Back pos {pos}")
                    d.print(f"Back leftover {leftover}")
                    if (pos - 70 - gap) <= 250:
                        after_gap = 1
                        big_parts = 0
                    elif leftover <= 180:
                        # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                        # gap da ekliyoruz çünkü köşeden gap boşluğu var
                        big_parts += 1
                        last_pos = (last_pos[0] + (leftover + 70 + gap) - 70, last_pos[1])
                    else:
                        after_gap = 1
                        overshoot = 150 - leftover
                        last_pos = (last_pos[0] + (overshoot + 70 + gap) - 70, last_pos[1])

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] + 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.FRONT
                        )

                        last_pos = (last_pos[0] + 250, last_pos[1])  # length of scaffold

                    new_y = last_pos[1] - (console_count * 35 + gap) if console_count!=0 else last_pos[1]
                    last_pos = (last_pos[0], new_y)

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 250, last_pos[1]) # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_after_gap = (depth % 250) // 150

                    if last_x == 0:
                        last_x = last_pos[0]

                    start_x_for_depth = last_x - gap * 2 + 70
                    last_pos = (start_x_for_depth, last_pos[1])

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 250) # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0] + console_count * 35 - 70, last_pos[1])
                    last_x = 0
                    d.print(f'son kalan nokta: {last_pos}')
                    console_count = 0
                if key == 'L':
                    last_y = total_length - pos - total_cumulative_outset + gap * 2
                    pos = abs(last_y - last_pos[1])

                    big_parts = pos // 250  # count of big part
                    leftover = pos % 250
                    after_gap = 0

                    d.print(f"Left pos {pos}")
                    d.print(f"Left leftover {leftover}")
                    if gap < (pos - 70 - gap):
                        if (pos - 70 - gap) <= 250:
                            after_gap = 1
                            big_parts = 0
                        elif leftover <= 180:
                            # sonda 70 ekliyoruz çünkü döndükten sonraki parça 70 cm ekleyecek
                            # gap da ekliyoruz çünkü köşeden gap boşluğu var
                            big_parts += 1
                            last_pos = (last_pos[0] - (leftover + 70 + gap) + 70, last_pos[1])
                        else:
                            after_gap = 1
                            overshoot = 150 - leftover
                            last_pos = (last_pos[0] - (overshoot + 70 + gap) + 70, last_pos[1])

                    new_x = last_pos[0] - (console_count * 35 + gap) if console_count != 0 else last_pos[0]
                    last_pos = (new_x, last_pos[1])

                    for b_part in range(big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 250),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

                    for s_part in range(after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0], last_pos[1] - 150),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.RIGHT
                        )

                        last_pos = (last_pos[0], last_pos[1] - 150)  # length of scaffold

                    depth_big_parts = depth // 250  # count of big part
                    depth_left_over = depth % 250
                    depth_after_gap = 0

                    if depth_left_over > 100:
                        depth_big_parts += 1

                    if last_y == 0:
                        last_y = last_pos[1]

                    start_y_for_depth = last_y - gap
                    last_pos = (last_pos[0], start_y_for_depth)

                    d.print(f'depth posu: {last_pos}')
                    for b_part in range(depth_big_parts):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 250, last_pos[1]),
                            small=False,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 250, last_pos[1])  # length of scaffold

                    for s_part in range(depth_after_gap):
                        drawer.draw_scaffold(
                            start_point=(last_pos[0] - 150, last_pos[1]),
                            small=True,
                            console_count=console_count,
                            scaffold_side=ScaffoldSide.BACK
                        )

                        last_pos = (last_pos[0] - 150, last_pos[1])  # length of scaffold

                    # kendisi default 70 cm her bir console 35 cm
                    last_pos = (last_pos[0], last_pos[1] + console_count * 35 - 70)
                    d.print(f'L -> Kaldığı {last_pos}')

        if key == 'F':
            pos = abs(total_length - last_pos[0] - total_cumulative_outset)

            big_parts = pos // 250  # count of big part
            leftover = pos % 250

            if leftover > 90:
                big_parts += 1

            for b_part in range(big_parts):
                drawer.draw_scaffold(
                    start_point=(last_pos[0] + 250, last_pos[1]),
                    small=False,
                    console_count=console_count,
                    scaffold_side=ScaffoldSide.FRONT
                )

                last_pos = (last_pos[0] + 250, last_pos[1])  # length of scaffold

            last_x = total_length - total_cumulative_outset
            last_y = last_pos[1] + gap

        if key == 'R':
            pos = total_length - last_pos[1] - total_cumulative_outset

            big_parts = pos // 250  # count of big part
            leftover = pos % 250

            if leftover > 90:
                big_parts += 1

            for b_part in range(big_parts):
                drawer.draw_scaffold(
                    start_point=(last_pos[0], last_pos[1] + 250),
                    small=False,
                    console_count=console_count,
                    scaffold_side=ScaffoldSide.LEFT
                )

                last_pos = (last_pos[0], last_pos[1] + 250)  # length of scaffold

            last_x = last_pos[0] - gap
            last_y = total_length - total_cumulative_outset

        if key == 'B':
            last_pos = (last_pos[0], last_pos[1])
            pos = total_length - (total_length - last_pos[0])

            big_parts = pos // 250  # count of big part
            leftover = pos % 250

            if leftover > 180:
                big_parts += 1

            for b_part in range(big_parts):
                drawer.draw_scaffold(
                    start_point=(last_pos[0] - 250, last_pos[1]),
                    small=False,
                    console_count=console_count,
                    scaffold_side=ScaffoldSide.BACK
                )

                last_pos = (last_pos[0] - 250, last_pos[1])  # length of scaffold

            d.print(f'B SON : {last_pos}')
            last_x = 0
            last_y = last_pos[1] - gap

        if key == 'L':
            last_pos = (last_pos[0], last_pos[1] + 70 + gap)
            pos = total_length - (total_length - last_pos[1])

            big_parts = pos // 250  # count of big part

            for b_part in range(big_parts):
                drawer.draw_scaffold(
                    start_point=(last_pos[0], last_pos[1] - 250),
                    small=False,
                    console_count=console_count,
                    scaffold_side=ScaffoldSide.RIGHT
                )

                last_pos = (last_pos[0], last_pos[1] - 250)  # length of scaffold

            last_x = last_pos[0]
            last_y = total_length - total_cumulative_outset
