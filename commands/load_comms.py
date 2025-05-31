import json

from Commutator.convert_list_to_comms import update_comm_list


def load_comms(buffer_order, file_name):
    try:
        with open(f"comms/{file_name}/{file_name}.json") as f:
            file_comms = json.load(f)
    except FileNotFoundError:
        update_comm_list(buffers=buffer_order, file=file_name)
        return load_comms(buffer_order, file_name)

    return file_comms
