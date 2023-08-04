import csv
from pprint import pprint

# for i in a.split('\n'):
# print(i.split(','), "\n\n")
from expand_comm import expand_comm


def _convert(buffer):
    comms = {}

    with open(f'comms/max_comms/{buffer}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            second_target = row['1st Target:']
            if len(second_target) > 3:
                raise ValueError(buffer, second_target, "second_target is too long")

            for first_target in row:
                if row == '' or second_target == first_target or first_target == "1st Target:" or first_target is None:
                    continue
                if len(first_target) > 3:
                    raise ValueError(buffer, first_target, "first_target is too long")

                comm = expand_comm(row[first_target])
                if comms.get(first_target, None) is None:
                    comms[first_target] = {second_target: comm}
                else:
                    comms[first_target][second_target] = comm
    return comms


def update_comm_list(file="max_comms.py", buffers=None):
    if buffers is None:
        buffers = [
            'UF', 'UB', 'UR', 'UL',
            'DF', 'DB',
            'FR', 'FL',
            'DR', 'DL',
            'UFR', 'UBR', 'UBL', 'UFL',
            'RDF', 'RDB'
        ]
    elif len(buffers) != 18:
        raise ValueError("Please include all of the buffers in settings.json")

    comms = {}
    for buffer in buffers:
        comms[buffer] = _convert(buffer)

    pprint(comms, sort_dicts=False)
    with open(f"{file}.py", "w+") as f:
        f.write(f"{file.upper()} = ")
        pprint(comms, f, sort_dicts=False)


if __name__ == '__main__':
    update_comm_list()
