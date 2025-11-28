import json
from pathlib import Path

from Commutator.convert_list_to_comms import update_comm_list


def load_comms(file_name):
    json_path = Path(f"comms/{file_name}/{file_name}.json")
    try:
        with open(json_path) as f:
            file_comms = json.load(f)
    except FileNotFoundError:
        # Get all buffers from CSV files in the directory
        directory = Path(f"comms/{file_name}")
        buffers = [csv_file.stem for csv_file in directory.glob("*.csv")]
        print(f"Found {len(buffers)} buffers: {buffers}")

        update_comm_list(buffers=buffers, file=file_name)
        return load_comms(file_name)
    return file_comms
