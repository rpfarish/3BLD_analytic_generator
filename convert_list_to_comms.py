import csv
import json
from pprint import pprint
from typing import Dict

# for i in a.split('\n'):
# print(i.split(','), "\n\n")
from expand_comm import expand_comm


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
                    comms[first_target][second_target] = comm
                    # if comm2 is not None and '[' not in comm2 and comm2 and \
                    #         not {'F', 'L', 'B', 'S', 'M', 'E'}.intersection(set(comm2)) and 'D' in comm2:
                    #     print(f'"{comm2.strip()}",')
    return comms


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

    pprint(comms, sort_dicts=False)
    with open(f"{file}.json", "w+") as f:
        json.dump(comms, f, indent=4)


if __name__ == '__main__':
    update_comm_list()
    # buffers = [
    #     'UF', 'UB', 'UR', 'UL',
    #     'DF', 'DB',
    #     'FR', 'FL',
    #     'DR', 'DL',
    # ]
    # for buffer in buffers:
    #     _convert(buffer, "eli_comms", top_corner_key="")
