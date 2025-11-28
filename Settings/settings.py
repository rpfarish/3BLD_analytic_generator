import json
from pathlib import Path
from typing import Dict, List, TypedDict

from Commutator.convert_list_to_comms import update_comm_list
from Cube.letterscheme import LetterScheme


class CommFile(TypedDict):
    name: str
    spreadsheet: Path
    cols_first: bool


class Settings:
    def __init__(self, file: str = "settings.json"):
        self.file: str = file
        self.letter_scheme: LetterScheme = LetterScheme()
        self.buffers: Dict[str, str] = {"edge_buffer": "", "corner_buffer": ""}
        self.buffer_order: Dict[str, List[str]] = {"edges": [""], "corners": [""]}
        self.all_buffers_order: List[str] = [""]
        self.comm_files: dict[str, CommFile] = {}
        self.parity_swap_edges: str = ""
        self.floating_comms_sheet_name: str = ""

        self.valid_edges = [
            "UF",
            "UB",
            "UR",
            "UL",
            "DF",
            "DB",
            "DR",
            "DL",
            "FR",
            "FL",
            "BR",
            "BL",
        ]

        self.reload(True)

    def reload(self, first=False):
        if not first:
            print("Loading Settings...")
        with open(self.file) as f:
            settings = json.loads(f.read())
            self.letter_scheme: LetterScheme = LetterScheme(
                ltr_scheme=settings["letter_scheme"]
            )
            self.buffers: Dict[str, str] = settings["buffers"]
            self.buffer_order: Dict[str, List[str]] = settings["buffer_order"]
            self.all_buffers_order: List[str] = (
                self.buffer_order["edges"] + self.buffer_order["corners"]
            )
            self.comm_files: dict[str, CommFile] = settings["comm_files"]

            self.parity_swap_edges: str = settings["parity_swap_edges"]
            self.floating_comms_sheet_name: str = settings["floating_comms_sheet_name"]
            # update_comm_list(
            #     buffers=self.all_buffers_order, file=self.comm_file_name,
            # )
            # do I need to parse csv again if there's already .json
        self._validate_settings()

    def load_list_of_comms_json(self):
        ...
        # update_comm_list(
        #     buffers=self.all_buffers_order, file=self.comm_file_name,
        # )

    def _validate_settings(self):
        if len(set(self.all_buffers_order)) != 16:
            raise ValueError("Please include all of the 16 buffers in settings.json")

        if len(self.buffers) != 2:
            raise ValueError(
                "Please include both edge and corner buffers in settings.json"
            )
        edge_buffer: str = self.buffers["edge_buffer"]
        edge_order_first_buffer: str = self.buffer_order["edges"][0]
        if not edge_buffer == edge_order_first_buffer:
            raise ValueError(
                f"The edge buffer '{edge_buffer}' and the first edge buffer in buffer_order "
                f"'{edge_order_first_buffer}' are not the same in settings.json",
            )

        corner_buffer: str = self.buffers["corner_buffer"]
        corner_order_first_buffer: str = self.buffer_order["corners"][0]
        if not corner_buffer == corner_order_first_buffer:
            raise ValueError(
                f"The corner buffer '{corner_buffer}' and the first corner buffer in buffer_order "
                f"'{corner_order_first_buffer}' are not the same in settings.json",
            )

        parity_swap = self.parity_swap_edges
        if (
            "-" not in parity_swap
            or parity_swap.startswith("-")
            or parity_swap.endswith("-")
        ):
            raise ValueError(
                "The separator '-' does not properly separate the parity swap edges"
            )

        swap_a, swap_b = parity_swap.split("-")
        if len(swap_a) != 2 or len(swap_b) != 2:
            raise ValueError(
                f"The length of an edge in parity swap edges is not 2: {self.parity_swap_edges}"
            )

        if not self._is_valid_EO_preserving_swap(swap_a, swap_b):
            raise ValueError(
                f"Currently only supports pseudoswaps preserving F/B EO: '{self.parity_swap_edges}'\n"
                f"Psudoswaps must have edges that are a value of: '{"', '".join(self.valid_edges)}'"
            )

        if self.floating_comms_sheet_name not in self.comm_files:
            raise ValueError(
                f"Name: {self.floating_comms_sheet_name} does not exist in comm_files"
            )

        self._validate_comm_files()

    def _is_valid_EO_preserving_swap(self, a, b):
        return a in self.valid_edges and b in self.valid_edges

    def _validate_comm_files(self):
        invalid = []
        excel_extensions = [".xlsx", ".xlsm", ".xls", ".xlsb"]
        # NOTE: isn't this backwards
        # like we should be asking what files are in Spreadsheets
        # and offering to ingest them for the user
        # and detect when a Spreadsheet is present or not to use it?
        # if no spreadsheets are available just default load Elliotts?

        for name, entry in self.comm_files.items():
            is_invalid = False

            file_path = Path("Spreadsheets", entry["spreadsheet"])
            is_cols = entry["cols_first"]

            if file_path.suffix not in excel_extensions:
                print(f"Spreadsheet format '{file_path.suffix}' not supported")
                is_invalid = True

            elif not file_path.exists() or not file_path.is_file():
                print(f"Warning: '{file_path}' does not exist")
                print("Skipping file...")
                is_invalid = True

            if not isinstance(is_cols, bool):
                print(f"In {name}: cols_first must be a boolean")
                is_invalid = True

            if is_invalid:
                invalid.append(name)

        if invalid:
            print(
                f"Warning: Skipped invalid comm file{'s' * (len(invalid) > 1)}: {', '.join(invalid)}"
            )
            for name in invalid:
                self.comm_files.pop(name)


if __name__ == "__main__":
    s = Settings()
    s.load_list_of_comms_json()
