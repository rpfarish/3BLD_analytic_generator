"""Settings loader and validator for the BLD generator."""

import json
from pathlib import Path
from typing import ClassVar, TypedDict

import dlin
from interface import CLIInterface
from Letterscheme.letterscheme import LetterScheme, sort_face_precedence


class CommFile(TypedDict):
    name: str
    spreadsheet: Path
    cols_first: bool
    enabled: bool


class Buffers(TypedDict):
    edge_buffer: str
    corner_buffer: str


class BufferOrder(TypedDict):
    edges: list[str]
    corners: list[str]


class Settings:
    _TOTAL_BUFFERS: ClassVar[int] = 16
    _REQUIRED_BUFFER_TYPES: ClassVar[int] = 2
    _EDGE_LEN: ClassVar[int] = 2

    _DEFAULT_CORNER_BUFFERS: ClassVar[list[str]] = [
        "UFR",
        "UFL",
        "UBL",
        "UBR",
        "DFR",
        "DFL",
        "DBR",
        "DBL",
    ]
    _DEFAULT_EDGE_BUFFERS: ClassVar[list[str]] = [
        "UF",
        "UB",
        "UR",
        "UL",
        "DF",
        "DB",
        "FR",
        "FL",
        "DR",
        "DL",
        "BR",
        "BL",
    ]
    _VALID_EDGES: ClassVar[list[str]] = [
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
    _EXCEL_EXTENSIONS: ClassVar[list[str]] = [".xlsx", ".xlsm", ".xls", ".xlsb"]

    def __init__(
        self,
        ui: CLIInterface,
        file: str = "settings.json",
    ) -> None:
        self.ui = ui
        self.file: str = file
        self.letter_scheme: LetterScheme = LetterScheme()
        self.buffers: Buffers = {"edge_buffer": "", "corner_buffer": ""}
        self.buffer_order: BufferOrder = {"edges": [""], "corners": [""]}
        self.dlin_buffers: dlin.DefaultBuffers = dlin.DefaultBuffers(edge=[], corner=[])
        self.all_buffers_order: list[str] = []
        self.comm_files: dict[str, CommFile] = {}
        self.parity_swap_edges: str = ""
        self.floating_comms_sheet_name: str = ""
        self.corner_buffer_precedence: list[str] = []
        self.edge_buffer_precedence: list[str] = []
        self.drill_show_comms: bool = True

        self.reload(first=True)

    def reload(self, first: bool = False) -> None:
        if not first:
            self.ui.info("Loading Settings...")
        with Path(self.file).open(encoding="utf-8") as f:
            settings = json.load(f)

        ls = {
            sort_face_precedence(buffer).upper(): name.upper()
            for buffer, name in settings["letter_scheme"].items()
        }
        self.letter_scheme = LetterScheme(ltr_scheme=ls)

        self.buffers = settings["buffers"]
        self.buffers["edge_buffer"] = self.buffers["edge_buffer"].upper()
        self.buffers["corner_buffer"] = sort_face_precedence(
            self.buffers["corner_buffer"].upper(),
        )

        self.buffer_order = settings["buffer_order"]

        self.buffer_order["corners"] = [
            sort_face_precedence(b).upper() for b in self.buffer_order["corners"]
        ]
        self.buffer_order["edges"] = [b.upper() for b in self.buffer_order["edges"]]
        print("BUFFER ORDER IS SET", self.buffer_order)

        self.dlin_buffers = self._get_dlin_default_buffers()
        self.all_buffers_order = (
            self.buffer_order["edges"] + self.buffer_order["corners"]
        )

        for comm_file in settings["comm_files"].values():
            comm_file["spreadsheet"] = Path(comm_file["spreadsheet"])
        self.comm_files = settings["comm_files"]

        self.parity_swap_edges = settings["parity_swap_edges"].upper()
        self.floating_comms_sheet_name = settings["floating_comms_sheet_name"]
        self.drill_show_comms = settings["drill_show_comms"]

        self._validate_settings()

    def _get_dlin_default_buffers(self) -> dlin.DefaultBuffers:
        buffers: dict[str, list[str]] = {
            "corner": list(self._DEFAULT_CORNER_BUFFERS),
            "edge": list(self._DEFAULT_EDGE_BUFFERS),
        }

        corner_buffers = self.buffer_order["corners"]
        edge_buffers = self.buffer_order["edges"]

        if len(corner_buffers) + len(edge_buffers) == self._TOTAL_BUFFERS:
            if sorted(corner_buffers[-1]) == sorted(buffers["corner"][-2]):
                buffers["corner"][-2], buffers["corner"][-3] = (
                    buffers["corner"][-3],
                    buffers["corner"][-2],
                )
            buffers["edge"][: len(edge_buffers)] = edge_buffers
            buffers["corner"][: len(corner_buffers)] = corner_buffers

        print("SETTINGS LOADING DEFAULT DLIN BUFFERS", buffers)
        return dlin.DefaultBuffers(edge=buffers["edge"], corner=buffers["corner"])

    def load_list_of_comms_json(self) -> None: ...

    def _validate_settings(self) -> None:
        if len(set(self.all_buffers_order)) != self._TOTAL_BUFFERS:
            msg = f"Expected {self._TOTAL_BUFFERS} unique buffers in settings.json, got {len(set(self.all_buffers_order))}"
            raise ValueError(msg)

        if len(self.buffers) != self._REQUIRED_BUFFER_TYPES:
            msg = "Please include both edge and corner buffers in settings.json"
            raise ValueError(msg)

        edge_buffer = self.buffers["edge_buffer"]
        edge_order_first = self.buffer_order["edges"][0]
        if edge_buffer != edge_order_first:
            msg = (
                f"Edge buffer '{edge_buffer}' and first buffer_order edge "
                f"'{edge_order_first}' must match in settings.json"
            )
            raise ValueError(msg)

        corner_buffer = self.buffers["corner_buffer"]
        corner_order_first = self.buffer_order["corners"][0]
        if corner_buffer != corner_order_first:
            msg = (
                f"Corner buffer '{corner_buffer}' and first buffer_order corner "
                f"'{corner_order_first}' must match in settings.json"
            )
            raise ValueError(msg)

        parity_swap = self.parity_swap_edges
        if (
            "-" not in parity_swap
            or parity_swap.startswith("-")
            or parity_swap.endswith("-")
        ):
            msg = "The separator '-' does not properly separate the parity swap edges"
            raise ValueError(msg)

        swap_a, swap_b = parity_swap.split("-")
        if len(swap_a) != self._EDGE_LEN or len(swap_b) != self._EDGE_LEN:
            msg = f"Parity swap edge length must be {self._EDGE_LEN}: got '{self.parity_swap_edges}'"
            raise ValueError(msg)

        if not self._is_valid_eo_preserving_swap(swap_a, swap_b):
            valid = "', '".join(self._VALID_EDGES)
            msg = (
                f"Only pseudoswaps preserving F/B EO are supported: '{self.parity_swap_edges}'\n"
                f"Edges must be one of: '{valid}'"
            )
            raise ValueError(msg)

        if self.floating_comms_sheet_name not in self.comm_files:
            msg = f"floating_comms_sheet_name '{self.floating_comms_sheet_name}' not found in comm_files"
            raise ValueError(msg)

        if not isinstance(self.drill_show_comms, bool):
            msg = f"drill_show_comms must be a boolean, got: {self.drill_show_comms!r}"
            raise TypeError(msg)

        self._validate_comm_files()

    def _is_valid_eo_preserving_swap(self, a: str, b: str) -> bool:
        return a in self._VALID_EDGES and b in self._VALID_EDGES

    def _validate_comm_files(self) -> None:
        invalid: list[str] = []

        for name, entry in self.comm_files.items():
            is_invalid = False
            file_path = Path("Spreadsheets", entry["spreadsheet"])

            if file_path.suffix not in self._EXCEL_EXTENSIONS:
                self.ui.warning(
                    f"Spreadsheet format '{file_path.suffix}' not supported in '{name}'",
                )
                is_invalid = True
            elif not file_path.is_file():
                self.ui.warning(f"'{file_path}' does not exist — skipping '{name}'")
                is_invalid = True

            if not isinstance(entry["cols_first"], bool):
                self.ui.warning(f"In '{name}': cols_first must be a boolean")
                is_invalid = True

            if is_invalid:
                invalid.append(name)

        if invalid:
            plural = "s" if len(invalid) > 1 else ""
            self.ui.warning(f"Skipped invalid comm file{plural}: {', '.join(invalid)}")
            for name in invalid:
                self.comm_files.pop(name)


if __name__ == "__main__":
    ui = CLIInterface()
    s = Settings(ui=ui)
    s.load_list_of_comms_json()
