import csv
from pprint import pprint

# for i in a.split('\n'):
# print(i.split(','), "\n\n")
from Cube import Cube
from expand_comm import expand_comm


def convert(comms, buffer):
    comms[buffer] = {}

    with open(f'{buffer}.csv', newline='') as csvfile:
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

buffers = ['UFR', 'UBR', 'UBL']

for buffer in buffers:
    convert(comms, buffer)

pprint(comms)
