import csv
import os
import re

import pandas

from Settings.settings import Settings


def ingest_spreadsheet(file_name, s: Settings):
    # return if done correct
    # TODO make a list of possible acceptable buffers and parse using that then cross reference against buffers in settings.json
    edge_buffers = s.buffer_order["edges"]
    corner_buffers = s.buffer_order["corners"]
    corners = "|".join(corner_buffers)
    to_compile = r"^(" + corners + r")"
    corners_pattern = re.compile(to_compile)

    edges = "|".join(edge_buffers)
    to_compile0 = r"^" + edges
    to_compile1 = r"^(" + edges + r")$"
    to_compile2 = r"^(" + edges + r")s"
    edges_pattern0 = re.compile(to_compile0)
    edges_pattern1 = re.compile(to_compile1)
    edges_pattern2 = re.compile(to_compile2)

    xl_file = pandas.ExcelFile(f"Spreadsheets/{file_name}")

    dfs = {}

    for sheet_name in xl_file.sheet_names:
        if corners_pattern.search(sheet_name):
            match = corners_pattern.search(sheet_name)
            data_frame = xl_file.parse(sheet_name)
            dfs[match.group()] = data_frame

        elif edges_pattern1.search(sheet_name) or edges_pattern2.search(sheet_name):
            match = edges_pattern0.search(sheet_name)
            data_frame = xl_file.parse(sheet_name)
            dfs[match.group()] = data_frame

    new_path = f"comms/{file_name}"
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    len_dfs = len(dfs)
    print(len(dfs), "sheets converted")
    print("Full Floating is 16")

    for sheet_name, dataframe in dfs.items():
        dataframe.to_csv(f"comms/{file_name}/{sheet_name}.csv", index=False)

    pattern = r"^(U|D|R|L|F|B){2,3}"
    sticker_pattern = re.compile(pattern)

    def filter_buffer(cell) -> str:
        # check if cell is a corner or edge buffer
        print(cell)
        if sticker_pattern.search(cell) is not None:
            print(
                sticker_pattern,
                sticker_pattern.search(cell),
                sticker_pattern.search(cell).group(),
            )
            return sticker_pattern.search(cell).group()
        else:
            print("Cell not parsed", cell)
            return cell

    def parse_header(header):
        return_header = [header[0]]
        for head_index in range(1, len(header)):
            return_header.append((filter_buffer(header[head_index])))
        return return_header

    def parse_row(row):
        row_index, *rest_of_row = row
        row_index = filter_buffer(row_index)
        rest_of_row = [i.strip() for i in rest_of_row]
        return [row_index] + rest_of_row

    for buffer in s.all_buffers_order:
        with open(f"comms/{file_name}/{buffer}.csv", newline="") as csvfile:
            top_corner_key, *_ = next(csv.reader(csvfile))

        with (
            open(f"comms/{file_name}/{buffer}.csv", newline="") as csvfile,
            open(f"comms/{file_name}/temp.csv", newline="", mode="w+") as temp_file,
        ):
            reader = csv.reader(csvfile)
            temp_writer = csv.writer(temp_file)
            print(reader)
            for row_num, row in enumerate(reader):
                if len(buffer) + row_num > 24:
                    break
                if row_num == 0:
                    temp_writer.writerow(parse_header(row))
                else:
                    temp_writer.writerow(parse_row(row))

        os.remove(f"comms/{file_name}/{buffer}.csv")
        os.rename(f"comms/{file_name}/temp.csv", f"comms/{file_name}/{buffer}.csv")
