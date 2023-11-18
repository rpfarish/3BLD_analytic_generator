import os
import re

import pandas

from Settings.settings import Settings

s = Settings()
all_buffers = s.all_buffers_order
edge_buffers = s.buffer_order['edges']
corner_buffers = s.buffer_order['corners']
print(corner_buffers)
print(len(corner_buffers))
corners = "|".join(corner_buffers)
to_compile = r"^(" + corners + r")"
print(to_compile)
corners_pattern = re.compile(to_compile)

print(edge_buffers)
print(len(edge_buffers))
edges = "|".join(edge_buffers)
to_compile0 = r"^" + edges
to_compile1 = r"^(" + edges + r")$"
to_compile2 = r"^(" + edges + r")s"
print(to_compile)
edges_pattern0 = re.compile(to_compile0)
edges_pattern1 = re.compile(to_compile1)
edges_pattern2 = re.compile(to_compile2)

pattern2 = re.compile(r'^(U|D|R|L|F|B){2,3}')
file_name = 'Max Hilliard 3BLD'
xl_file = pandas.ExcelFile(f'Spreadsheets/{file_name}.xlsx')

dfs = {}

for sheet_name in xl_file.sheet_names:
    if pattern2.search(sheet_name) is None:
        print(sheet_name)
        print('thirds', pattern2.search(sheet_name))
        continue
    if sheet_name == 'UF':
        print(corners_pattern.search(sheet_name))
        print(edges_pattern0.search(sheet_name))
    if corners_pattern.search(sheet_name):
        match = corners_pattern.search(sheet_name)
        data_frame = xl_file.parse(sheet_name)
        dfs[match.group()] = data_frame

    elif edges_pattern1.search(sheet_name) or edges_pattern2.search(sheet_name):
        match = edges_pattern0.search(sheet_name)
        data_frame = xl_file.parse(sheet_name)
        dfs[match.group()] = data_frame

new_path = f'comms/{file_name}'
if not os.path.exists(new_path):
    os.makedirs(new_path)

print(len(dfs), "sheets converted")
print("Full Floating is 16")

for sheet_name, dataframe in dfs.items():
    dataframe.to_csv(f"comms/{file_name}/{sheet_name}.csv", index=False)
#
# for buffer in s.all_buffers_order:
#     with open(f'comms/{file_name}/{buffer}.csv', newline='') as csvfile:
#         top_corner_key, *_ = next(csv.reader(csvfile))
#
#     with open(f'comms/{file_name}/{buffer}.csv', newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#
#         pprint(reader)
#         for num, row in enumerate(reader):
#             row: dict[str] = row
#             second_target = row[top_corner_key]
#             print(buffer, row)
#         break
