import csv
from pprint import pprint

# for i in a.split('\n'):
# print(i.split(','), "\n\n")
from expand_comm import expand_comm


def convert(comms, buffer):
    comms[buffer] = {}

    with open(f'comms/max_comms/{buffer}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            second_target = row["1st Target:"]
            for first_target in row:
                if row == '' or second_target == first_target or first_target == "1st Target:":
                    continue
                comm = expand_comm(row[first_target])
                if comms[buffer].get(first_target, None) is None:
                    comms[buffer][first_target] = {second_target: comm}
                else:
                    comms[buffer][first_target][second_target] = comm


comms = {}

# buffers = ['UFR', 'UBR', 'UBL']
buffers = [
    'UF', 'UB', 'UR', 'UL', 'DF', 'DB', 'FR', 'FL', 'DR', 'DL',
    'UFR', 'UBR', 'UBL', 'UFL', 'RDF', 'RDB'
]
for buffer in buffers:
    convert(comms, buffer)

pprint(comms, sort_dicts=False)
with open(f"max_comms.py", "w+") as f:
    f.write("MAX_COMMS = ")
    pprint(comms, f, sort_dicts=False)
