import json
from typing import Dict, List

from Commutator.convert_list_to_comms import update_comm_list
from Cube.letterscheme import LetterScheme


class Settings:
    def __init__(self, file: str = "settings.json"):
        self.file: str = file
        self.letter_scheme: LetterScheme = LetterScheme()
        self.buffers: Dict[str, str] = {'edge_buffer': '', 'corner_buffer': ''}
        self.buffer_order: Dict[str, List[str]] = {'edges': [''], 'corners': ['']}
        self.all_buffers_order: List[str] = ['']
        self.comm_file_name: str = ''
        self.parity_swap_edges: str = ''
        self.reload()

    def reload(self):
        with open(self.file) as f:
            settings = json.loads(f.read())
            self.letter_scheme: LetterScheme = LetterScheme(ltr_scheme=settings['letter_scheme'])
            self.buffers: Dict[str, str] = settings['buffers']
            self.buffer_order: Dict[str, List[str]] = settings['buffer_order']
            self.all_buffers_order: List[str] = self.buffer_order['edges'] + self.buffer_order['corners']
            self.comm_file_name: str = settings['comm_file_name']
            self.parity_swap_edges: str = settings['parity_swap_edges']
            update_comm_list(
                buffers=self.all_buffers_order, file=self.comm_file_name,

            )
        self._validate_settings()

    def _validate_settings(self):
        if len(self.all_buffers_order) != 16:
            raise ValueError("Please include all of the 16 buffers in settings.json")

        if len(self.buffers) != 2:
            raise ValueError("Please include both edge and corner buffers in settings.json")
        edge_buffer: str = self.buffers['edge_buffer']
        edge_order_first_buffer: str = self.buffer_order['edges'][0]
        if not edge_buffer == edge_order_first_buffer:
            raise ValueError(
                f"The edge buffer '{edge_buffer}' and the first edge buffer in buffer_order "
                f"'{edge_order_first_buffer}' are not the same in settings.json",
            )

        corner_buffer: str = self.buffers['corner_buffer']
        corner_order_first_buffer: str = self.buffer_order['corners'][0]
        if not corner_buffer == corner_order_first_buffer:
            raise ValueError(
                f"The corner buffer '{corner_buffer}' and the first corner buffer in buffer_order "
                f"'{corner_order_first_buffer}' are not the same in settings.json",
            )
