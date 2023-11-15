import csv
import json
from collections import deque
from typing import Dict

from Cube import Cube
# for i in a.split('\n'):
# print(i.split(','), "\n\n")
from .expand_comm import expand_comm


# todo make this take a spreadsheet and csv
def _convert(buffer, file_name="max_comms", top_corner_key="1st Target:"):
    comms = {}

    with open(f'comms/{file_name}/{buffer}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row: Dict[str] = row
            second_target = row[top_corner_key]

            if len(second_target) > 3:
                raise ValueError(buffer, second_target, "second_target is too long")

            for first_target in row:
                if row == '' or second_target == first_target or first_target == top_corner_key or first_target is None:
                    continue
                if len(first_target) > 3:
                    raise ValueError(buffer, first_target, "first_target is too long")
                # comm2 = row[first_target]
                comm = expand_comm(row[first_target])
                if comms.get(first_target, None) is None:
                    comms[first_target] = {second_target: comm}
                else:
                    comms[first_target][second_target] = comm if comm is not None else ""
                    # if comm2 is not None and '[' not in comm2 and comm2 and \
                    #         not {'F', 'L', 'B', 'S', 'M', 'E'}.intersection(set(comm2)) and 'D' in comm2:
                    #     print(f'"{comm2.strip()}",')
    return comms


def rotate_pair(buffer, target1, target2):
    rotated_once = deque([buffer, target1, target2])
    rotated_twice = deque([buffer, target1, target2])
    rotated_once.rotate()
    rotated_twice.rotate(2)
    return rotated_once, rotated_twice


def add_nested(comms, buffer, sticker1, sticker2) -> dict:
    if comms.get(buffer, {}).get(sticker1, {}).get(sticker2, None) is not None:
        return comms
    if comms.get(buffer, None) is None:
        comms[buffer] = {}
        # add comm to comms
    if comms.get(buffer, {}).get(sticker1, None) is None:
        comms[buffer][sticker1] = {}
        # add first sticker to comms
    return comms


def add_pair(comms, buffer, sticker1, sticker2, comm):
    comms |= add_nested(comms, buffer, sticker1, sticker2)
    comms[buffer][sticker1][sticker2] = comm
    print(buffer, sticker1, sticker2, comm)
    return comms


def fill_in_buffers(file_comms):
    cube = Cube()
    buffers = cube.edge_buffer_order + cube.corner_buffer_order
    num = 0
    comms = {}

    for buffer, sticker_comms in file_comms.items():
        for sticker1, comms_dict in sticker_comms.items():
            for sticker2, comm in comms_dict.items():
                if not comm:
                    continue

                print(comm, '-' * 10)
                num += 1
                for buffer, sticker1, sticker2 in rotate_pair(buffer, sticker1, sticker2):
                    comms |= add_pair(comms, buffer, sticker1, sticker2, comm)
                # corner or edge?
                if len(buffer) == 3:
                    for i in range(2):
                        buffer, sticker1, sticker2 = cube.adj_corners[buffer][i], cube.adj_corners[sticker1][i], \
                            cube.adj_corners[
                                sticker2][i]
                        for buffer, sticker1, sticker2 in rotate_pair(buffer, sticker1, sticker2):
                            comms |= add_pair(comms, buffer, sticker1, sticker2, comm)

                elif len(buffer) == 2:
                    buffer, sticker1, sticker2 = cube.adj_edges[buffer], cube.adj_edges[sticker1], cube.adj_edges[
                        sticker2]
                    for buffer, sticker1, sticker2 in rotate_pair(buffer, sticker1, sticker2):
                        if len({buffer, sticker1, sticker2}) != 3:
                            break
                        comms |= add_pair(comms, buffer, sticker1, sticker2, comm)
                else:
                    raise BufferError("Buffer incorrect length")
    print(num)

    # make loop to get through all letterpairs
    # take letterpair rotate it and then insert that into file_comms
    # then rotate / flip the pair and repeat
    file_comms |= comms
    print(len(file_comms))
    print(len(file_comms['UB']))
    print(len(file_comms['UB']['UR']))

    with open(f"testing.json", "w+") as f:
        json.dump(file_comms, f, indent=4)
    return file_comms


def update_comm_list(buffers=None, file="max_comms", top_corner_key=""):
    # todo import from settings
    if buffers is None:
        buffers = [
            'UF', 'UB', 'UR', 'UL',
            'DF', 'DB',
            'FR', 'FL',
            'DR', 'DL',
            'UFR', 'UBR', 'UBL', 'UFL',
            'RDF', 'RDB'
        ]
    elif len(buffers) != 16:
        raise ValueError("Please include all of the buffers in settings.json")
    comms = {}

    for buffer in buffers:
        comms[buffer] = _convert(buffer, file, top_corner_key=top_corner_key)

    with open(f"comms/{file}/{file}.json", "w+") as f:
        json.dump(comms, f, indent=4)


if __name__ == '__main__':
    # print(rotate_pair("UF", "UL", "UR"))
    with open(f"{'max_comms'}.json") as file:
        file_comms = json.load(file)
    # print(add_nested({}, "UF", "UR", "UL"))
    # fill_in_buffers(file_comms)
    update_comm_list(top_corner_key="1st Target:")
    # buffers = [
    #     'UF', 'UB', 'UR', 'UL',
    #     'DF', 'DB',
    #     'FR', 'FL',
    #     'DR', 'DL',
    # ]
    # for buffer in buffers:
    #     _convert(buffer, "eli_comms", top_corner_key="")
    # a = len([378, 270, 180, 108, 54, 18]) * 378
    # b = len([440, 360, 288, 224, 168, 120, 80, 48, 24, 8]) * 440
    # print(a, b)
    # print(a + b)
    # print((a + b) / 2768)
    #
    # # UL FL DR
