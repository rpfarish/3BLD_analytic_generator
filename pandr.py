import os
import re

import pandas

from Settings.settings import Settings

s = Settings()
buffers = s.all_buffers_order
print(buffers)

buffers = "|".join(buffers)
pattern = re.compile(r"^" + buffers)
file_name = 'Max Hilliard 3BLD'
xl_file = pandas.ExcelFile(f'Spreadsheets/{file_name}.xlsx')
# print(xl_file)
dfs = {match.group(): xl_file.parse(sheet_name)
       for sheet_name in xl_file.sheet_names
       if (match := pattern.search(sheet_name))
       }
new_path = f'comms/{file_name}'
if not os.path.exists(new_path):
    os.makedirs(new_path)
for sheet_name, dataframe in dfs.items():
    dataframe.to_csv(f"comms/{file_name}/{sheet_name}.csv", index=False)
