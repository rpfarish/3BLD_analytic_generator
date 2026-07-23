from typing import TypedDict

import numpy as np

import dlin.cube
import dlin.piece


class EdgeTrace(TypedDict):
    type: str
    buffer: str
    targets: list[str]
    orientation: int
    parity: int


class CornerTrace(TypedDict):
    type: str
    buffer: str
    targets: list[str]
    orientation: int
    parity: int


class Tracing(TypedDict):
    edge: list[EdgeTrace]
    corner: list[CornerTrace]
    scramble: str
    rotation: list[str]


def sort_face_precedence(cell):
    name = list(cell)
    face_precedence = {"U": 0, "D": 0, "F": 1, "B": 1, "R": 2, "L": 2, "": 3}
    name[1:] = sorted(name[1:], key=lambda x: face_precedence[x])
    return "".join(name)


def rotate_face_precedence(cell):
    name = list(cell)
    face_precedence = {"U": 0, "D": 0, "F": 1, "B": 1, "R": 2, "L": 2, "": 3}
    name = sorted(name, key=lambda x: face_precedence[x])
    return "".join(name)


def rotate_to_buffer(cell, buffers):
    """
    Cyclically rotate a 3-letter corner sticker name to match the
    canonical buffer name for that physical piece — preserves orientation
    (chirality), unlike a full letter-sort.
    `buffers`: list of canonical buffer corner names, e.g. self.settings.dlin_buffers["corner"]
    """
    if len(cell) != 3:
        return rotate_face_precedence(cell)  # fallback for edges/other lengths

    cell_set = frozenset(cell)
    for buf in buffers:
        if frozenset(buf) == cell_set:
            target = buf[0]
            idx = cell.index(target)
            return sort_face_precedence(cell[idx:] + cell[:idx])

    # no matching buffer piece found — fall back to old behavior
    return sort_face_precedence(rotate_face_precedence(cell))


class Tracer(dlin.cube.Cube):
    def __init__(self, buffers, trace="both"):
        super().__init__()
        self.tracing: Tracing = {
            "edge": [],
            "corner": [],
            "scramble": "",
            "rotation": [],
        }
        self.buffers = buffers
        self.loopcube = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    self.loopcube.append((x, y, z))

        self.trace_corners = True if trace in {"corners", "both"} else False
        self.trace_edges = True if trace in {"edges", "both"} else False

    def find_matching_buffer(self, piece_name, piece_type):
        normalized = rotate_face_precedence(piece_name)
        for buffer in self.buffers[piece_type]:
            if rotate_face_precedence(buffer) == normalized:
                return buffer
        return piece_name

    def find_piece(self, piecename):
        piecename = set(piecename)
        piece = [
            pos for pos in self.loopcube if set(self.cube[pos].get_name()) == piecename
        ][0]
        return piece

    def rotate_into_orientation(self):
        rotations = []
        u_center = self.find_piece("U")
        direction = max(set(u_center) - {1})
        axis = u_center.index(direction)
        rotation = ""
        if axis == 2:
            rotation = "x" if direction == 0 else "x'"
        elif axis == 0:
            rotation = "z" if direction == 0 else "z'"
        elif axis == 1:
            rotation = "z2" if direction == 0 else None

        if rotation:
            self.do_move(rotation)
            rotations.append(rotation)

        f_center = self.find_piece("F")
        direction = max(set(f_center) - {1})
        axis = f_center.index(direction)
        if axis == 2:
            rotation = None if direction == 0 else "y2"
        elif axis == 0:
            rotation = "y" if direction == 2 else "y'"

        if rotation:
            self.do_move(rotation)
            rotations.append(rotation)

        self.tracing["rotation"] = rotations

        return

    def coords_from_name(self, name):
        coords = [1, 1, 1]
        for side in name:
            if side == "F":
                coords[2] = 0
            elif side == "B":
                coords[2] = 2
            elif side == "U":
                coords[1] = 2
            elif side == "D":
                coords[1] = 0
            elif side == "R":
                coords[0] = 2
            elif side == "L":
                coords[0] = 0
        return tuple(coords)

    def where_to(self, a):
        axis = dlin.cube.FACES[a[0]]["axis"]
        piece = self.coords_from_name(a)
        return self.cube[piece].get_name(axis=axis)

    def set_buffer(self, target):
        self.buffer = target
        return

    def trace_from_target(self, target, targets=None):
        targets = targets if targets else []
        to = self.where_to(target)
        if set(list(to)) == set(list(self.buffer)):
            return
        else:
            targets.append(to)
            self.trace_from_target(to, targets)
        return targets

    def absolute_target(self, target):
        return set(list(target))

    def find_flips(self):
        flips = []
        for piece in self.loopcube:
            x, y, z = piece
            name = dlin.piece.Piece(x, y, z).get_name()
            to_name = self.cube[piece].get_name()
            if 1 in piece and set(list(name)) == set(list(to_name)) and name != to_name:
                flips.append(name)
        return flips

    def find_twists(self):
        twists = []
        for piece in self.loopcube:
            x, y, z = piece
            name = dlin.piece.Piece(x, y, z).get_name()
            to_name = self.cube[piece].get_name()
            if (
                1 not in piece
                and set(list(name)) == set(list(to_name))
                and name != to_name
            ):
                abs_target = set(list(name))
                from_sticker = name[0]
                to_sticker = to_name[0]

                if to_sticker in {"R", "L"} and from_sticker in {"U", "D"}:
                    ori = 1
                elif to_sticker in {"F", "B"} and from_sticker in {"U", "D"}:
                    ori = -1
                elif to_sticker in {"U", "D"} and from_sticker in {"F", "B"}:
                    ori = 1
                elif to_sticker in {"R", "L"} and from_sticker in {"F", "B"}:
                    ori = -1
                elif to_sticker in {"U", "D"} and from_sticker in {"R", "L"}:
                    ori = 1
                elif to_sticker in {"F", "B"} and from_sticker in {"R", "L"}:
                    ori = -1

                if abs_target in [
                    {"U", "F", "R"},
                    {"U", "B", "L"},
                    {"D", "B", "R"},
                    {"D", "F", "L"},
                ]:
                    ori = -ori

                twists.append({"location": name, "orientation": ori})
        return twists

    def edge_cycle_ori(self, targets):
        return 0 if self.where_to(targets[-1]) == self.buffer else 1

    def corner_cycle_ori(self, targets):
        last_target = self.where_to(targets[-1])
        abs_target = set(list(last_target))
        last_sticker = last_target[0]
        buffer_sticker = self.buffer[0]
        if last_target == self.buffer:
            return 0
        if last_sticker in {"R", "L"} and buffer_sticker in {"U", "D"}:
            ori = 1
        elif last_sticker in {"F", "B"} and buffer_sticker in {"U", "D"}:
            ori = -1
        elif last_sticker in {"U", "D"} and buffer_sticker in {"F", "B"}:
            ori = 1
        elif last_sticker in {"R", "L"} and buffer_sticker in {"F", "B"}:
            ori = -1
        elif last_sticker in {"U", "D"} and buffer_sticker in {"R", "L"}:
            ori = 1
        elif last_sticker in {"F", "B"} and buffer_sticker in {"R", "L"}:
            ori = -1

        if abs_target in [
            {"U", "F", "R"},
            {"U", "B", "L"},
            {"D", "B", "R"},
            {"D", "F", "L"},
        ]:
            ori = -ori

        return ori

    def cycle_parity(self, targets):
        return 1 if len(targets) % 2 else 0

    def trace_all(self, piecetype, buffers):
        solved = []
        for buffer in buffers:
            if self.absolute_target(buffer) in [
                self.absolute_target(x) for x in solved
            ]:
                continue
            self.set_buffer(buffer)
            targets = self.trace_from_target(buffer)
            if targets:
                [solved.append(target) for target in targets]
                parity = self.cycle_parity(targets)
                ori = (
                    self.edge_cycle_ori(targets)
                    if piecetype == "edge"
                    else self.corner_cycle_ori(targets)
                )
                self.tracing[piecetype].append(
                    {
                        "type": "cycle",
                        "buffer": buffer,
                        "targets": targets,
                        "orientation": ori,
                        "parity": parity,
                    }
                )

        if piecetype == "edge":
            flips = self.find_flips()
            if flips:
                for flip in flips:
                    self.tracing["edge"].append(
                        {
                            "type": "misoriented",
                            "buffer": self.find_matching_buffer(flip, "edge"),
                            "targets": [],
                            "orientation": 1,
                            "parity": 0,
                        }
                    )

        elif piecetype == "corner":
            twists = self.find_twists()
            if twists:
                for twist in twists:
                    self.tracing["corner"].append(
                        {
                            "type": "misoriented",
                            "buffer": self.find_matching_buffer(
                                twist["location"], "corner"
                            ),
                            "targets": [],
                            "orientation": twist["orientation"],
                            "parity": 0,
                        }
                    )

    def modify_buffer_order(self, edgebuffers, cornerbuffers):
        self.buffers["edge"] = edgebuffers
        self.buffers["corner"] = cornerbuffers

    def manual_swap(self, e1, e2):
        # CURRENTLY ONLY SUPPORTS PSEUDOSWAPS PRESERVING F/B EO
        coords1, coords2 = self.coords_from_name(e1), self.coords_from_name(e2)

        # Fix: Use np.where instead of .index()
        slice1 = int(np.where(self.cube[coords1].sides == "")[0][0])
        slice2 = int(np.where(self.cube[coords2].sides == "")[0][0])

        non_slice1, non_slice2 = (
            sorted(list({0, 1, 2} - {slice1})),
            sorted(list({0, 1, 2} - {slice2})),
        )
        piece1, piece2 = (
            [f for f in self.cube[coords1].sides if f],
            [f for f in self.cube[coords2].sides if f],
        )
        # idk why you have to do this but it works
        if sorted([slice1, slice2]) == [0, 1] or sorted([slice1, slice2]) == [0, 2]:
            piece2 = reversed(piece2)
            piece1 = reversed(piece1)

        (
            self.cube[coords1].sides[non_slice1[0]],
            self.cube[coords1].sides[non_slice1[1]],
        ) = piece2
        (
            self.cube[coords2].sides[non_slice2[0]],
            self.cube[coords2].sides[non_slice2[1]],
        ) = piece1

    def sort_tracing(self):
        self.tracing["edge"].sort(key=lambda x: self.buffers["edge"].index(x["buffer"]))
        self.tracing["corner"].sort(
            key=lambda x: self.buffers["corner"].index(x["buffer"])
        )

    def trace_cube(self):
        self.tracing = {
            "edge": [],
            "corner": [],
            "scramble": self.scramble,
            "rotation": [],
        }
        self.rotate_into_orientation()
        if self.trace_corners:
            self.trace_all("corner", self.buffers["corner"])
        if self.trace_edges:
            self.trace_all("edge", self.buffers["edge"])
        self.sort_tracing()
