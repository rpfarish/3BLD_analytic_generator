import json

from Cube.letterscheme import LetterScheme


class Settings:
    def __init__(self, file="settings.json"):
        self.file = file
        self.letter_scheme = None
        self.buffers = None
        self.buffer_order = None
        self.all_buffers_order = None
        self.comm_file_name = None
        self.parity_swap_edges = None
        self.reload()

    def reload(self):
        with open(self.file) as f:
            settings = json.loads(f.read())
            self.letter_scheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
            self.buffers = settings['buffers']
            self.buffer_order = settings['buffer_order']
            self.all_buffers_order = self.buffer_order['edges'] + self.buffer_order['corners']
            self.comm_file_name = settings['comm_file_name']
            self.parity_swap_edges = settings['parity_swap_edges']

        self._validate_settings()

    def _validate_settings(self):
        if len(self.all_buffers_order) != 16:
            raise ValueError("Please include all of the 16 buffers in settings.json")

        if len(self.buffers) != 2:
            raise ValueError("Please include both edge and corner buffers in settings.json")
        edge_buffer = self.buffers['edge_buffer']
        edge_order_first_buffer = self.buffer_order['edges'][0]
        if not edge_buffer == edge_order_first_buffer:
            raise ValueError(
                f"The edge buffer '{edge_buffer}' and the first edge buffer in buffer_order '{edge_order_first_buffer}' are not the same in settings.json",
            )
        corner_buffer = self.buffers['corner_buffer']
        corner_order_first_buffer = self.buffer_order['corners'][0]
        if not corner_buffer == corner_order_first_buffer:
            raise ValueError(
                f"The corner buffer '{corner_buffer}' and the first corner buffer in buffer_order '{corner_order_first_buffer}' are not the same in settings.json",
            )
