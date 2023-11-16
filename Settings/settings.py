import json

from Cube.letterscheme import LetterScheme


class Settings:
    def __init__(self):
        self.letter_scheme = None
        self.buffers = None
        self.buffer_order = None
        self.all_buffers_order = None
        self.comm_file_name = None
        self.parity_swap_edges = None
        self.reload()

    def reload(self):
        with open("settings.json") as f:
            settings = json.loads(f.read())
            self.letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
            self.buffers = settings['buffers']
            self.buffer_order = settings['buffer_order']
            self.all_buffers_order = self.buffer_order['edges'] + self.buffer_order['corners']

            if len(self.all_buffers_order) != 16:
                raise ValueError("Please include all of the 16 buffers in settings.json")

            self.comm_file_name = settings['comm_file_name']
            self.parity_swap_edges = settings['parity_swap_edges']
