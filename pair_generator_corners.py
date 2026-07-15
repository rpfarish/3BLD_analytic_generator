#!/usr/bin/env python3
"""
Letter Pair Drill Generator
----------------------------
Drills letter pairs from a corner-piece letter scheme (Speffz-style, for
blindfolded cubing memo practice), buffer = UFR.

Instead of picking pairs randomly each time (which can repeat/cluster),
this builds the full permutation of every valid ordered pair once, shuffles
it, and drills through that shuffled deck so every pair is seen exactly
once per cycle. Progress persists across reboots.

Controls:
  Enter       -> mark current pair done, show next
  s + Enter   -> show stats
  q + Enter   -> quit (progress saved)
"""

import json
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Corner sticker -> letter mapping (as given)
# ---------------------------------------------------------------------------
STICKER_TO_LETTER = {
    "UBL": "A",
    "UBR": "B",
    "UFR": "U",
    "UFL": "D",
    "LUB": "J",
    "LUF": "F",
    "LDF": "G",
    "LDB": "H",
    "FUL": "E",
    "FUR": "I",
    "FDR": "K",
    "FDL": "L",
    "RUF": "X",
    "RUB": "N",
    "RDB": "O",
    "RDF": "P",
    "BUR": "R",
    "BUL": "M",
    "BDL": "S",
    "BDR": "T",
    "DFL": "C",
    "DFR": "V",
    "DBR": "W",
    "DBL": "Z",
}


# ---------------------------------------------------------------------------
# 2. Group letters that belong to the same physical corner piece.
#    Two sticker codes refer to the same corner iff they contain the same
#    SET of face letters (order = which face/sticker of that corner).
#    e.g. "UBL","LUB","BUL" are all the same corner -> A, J, M must never
#    be paired with each other.
# ---------------------------------------------------------------------------
def build_piece_groups(mapping: dict[str, str]) -> dict[str, int]:
    groups: dict[frozenset, list[str]] = {}
    for sticker, letter in mapping.items():
        key = frozenset(sticker)
        groups.setdefault(key, []).append(letter)

    letter_to_group: dict[str, int] = {}
    for group_id, letters in enumerate(groups.values()):
        for letter in letters:
            letter_to_group[letter] = group_id
    return letter_to_group


LETTER_TO_GROUP = build_piece_groups(STICKER_TO_LETTER)

# ---------------------------------------------------------------------------
# 2b. Buffer piece = UFR. Exclude every letter on the buffer piece (all
#     stickers of that corner: UFR/RUF/FUR) from the drill pool entirely.
# ---------------------------------------------------------------------------
BUFFER_STICKER = "UFR"
BUFFER_GROUP = LETTER_TO_GROUP[STICKER_TO_LETTER[BUFFER_STICKER]]
BUFFER_LETTERS = {ltr for ltr, grp in LETTER_TO_GROUP.items() if grp == BUFFER_GROUP}

ALL_LETTERS = [ltr for ltr in LETTER_TO_GROUP if ltr not in BUFFER_LETTERS]

# ---------------------------------------------------------------------------
# 3. Persistent state (survives reboots)
# ---------------------------------------------------------------------------
STATE_DIR = Path.home() / ".local" / "state" / "letter_pair_drill"
STATE_FILE = STATE_DIR / "state.json"


def load_state() -> dict | None:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            if data:  # non-empty dict
                return data
        except json.JSONDecodeError, OSError:
            pass
    return None


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# 4. Full valid-permutation deck
# ---------------------------------------------------------------------------
def is_valid_pair(a: str, b: str) -> bool:
    if a == b:  # no doubles (AA)
        return False
    if LETTER_TO_GROUP[a] == LETTER_TO_GROUP[b]:  # no same-piece pairs (BN, GC...)
        return False
    return True


def build_shuffled_deck() -> list[str]:
    deck = [a + b for a in ALL_LETTERS for b in ALL_LETTERS if is_valid_pair(a, b)]
    random.shuffle(deck)
    return deck


def new_session(total_drilled: int = 0) -> dict:
    """Fresh shuffled deck; 'done' resets per cycle, 'total_drilled' is cumulative."""
    deck = build_shuffled_deck()
    current = deck.pop(0)
    return {
        "queue": deck,
        "current": current,
        "done": [],
        "total_drilled": total_drilled,
    }


# ---------------------------------------------------------------------------
# 5. Display (dark-terminal friendly ANSI styling)
# ---------------------------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[97m"
DIM = "\033[2m"


def show_pair(pair: str) -> None:
    # No screen clear -> pairs stack/scroll in the terminal.
    print(f"{BOLD}{WHITE}{pair}{RESET}")


# ---------------------------------------------------------------------------
# 6. Main loop
# ---------------------------------------------------------------------------
def main() -> None:
    saved = load_state()
    has_progress = bool(saved and (saved.get("done") or saved.get("current")))

    if has_progress:
        print(
            f"{DIM}Previous session found — {len(saved['done'])} pair(s) done this cycle "
            f"({saved.get('total_drilled', 0)} total).{RESET}"
        )
        if saved["done"]:
            print(f"{DIM}Done so far: {' '.join(saved['done'])}{RESET}")
        choice = (
            input(f"{BOLD}[R]esume or [N]ew session? [R/n]: {RESET}").strip().lower()
        )
        if choice.startswith("n"):
            state = new_session(total_drilled=saved.get("total_drilled", 0))
            save_state(state)
        else:
            state = saved
    else:
        state = new_session()
        save_state(state)

    current = state["current"]
    show_pair(current)

    while True:
        try:
            cmd = input().strip().lower()
        except EOFError, KeyboardInterrupt:
            save_state(state)
            print(f"\n{DIM}Progress saved. Bye!{RESET}")
            sys.exit(0)

        if cmd == "q":
            save_state(state)
            print(f"{DIM}Progress saved. Bye!{RESET}")
            break
        elif cmd == "s":
            print(
                f"{DIM}This cycle: {len(state['done'])}/{len(state['done']) + len(state['queue']) + 1}"
                f"   Total drilled: {state['total_drilled']}{RESET}"
            )
            continue
        else:
            state["done"].append(current)
            state["total_drilled"] += 1

            if state["queue"]:
                current = state["queue"].pop(0)
            else:
                print(f"{DIM}Cycle complete! Reshuffling a fresh deck...{RESET}")
                fresh = new_session(total_drilled=state["total_drilled"])
                state["queue"] = fresh["queue"]
                state["done"] = []
                current = fresh["current"]

            state["current"] = current
            save_state(state)
            show_pair(current)


if __name__ == "__main__":
    main()
