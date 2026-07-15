import random

"""
The problem is that remaining permutation is 7 long but
remaining target len is even and too big!?

"""


def random_bld_permutation(pieces, first_min):
    """
    pieces: list of piece labels (e.g. list(range(11)) for 11 corners/edges,
            with pieces[0] treated as the buffer).
    first_min: minimum length for the buffer's cycle.

    Returns: mapping (dict) piece -> piece, i.e. the full permutation.
    """
    n = len(pieces)
    buffer = pieces[0]
    rest = pieces[1:]

    # 1. Choose first cycle length uniformly on [first_min, n]
    first_len = random.randint(first_min, n)

    # 2. Pick (first_len - 1) other pieces to join the buffer's cycle
    random.shuffle(rest)
    cycle_members = [buffer] + rest[: first_len - 1]
    leftover = rest[first_len - 1 :]

    # 3. Build the forced first cycle (uniform k-cycle)
    mapping = random_k_cycle(cycle_members)

    # 4. Shuffle the leftover pieces into a uniform random permutation
    #    (this permutation's cycle decomposition gives the remaining cycles)
    if leftover:
        shuffled = leftover[:]
        random.shuffle(shuffled)
        for orig, new in zip(leftover, shuffled):
            mapping[orig] = new

    return mapping


def random_k_cycle(elements):
    elems = list(elements)
    random.shuffle(elems)
    k = len(elems)
    return {elems[i]: elems[(i + 1) % k] for i in range(k)}


def cycle_lengths_from_mapping(mapping, pieces):
    visited = set()
    lengths = []
    for p in pieces:
        if p in visited:
            continue
        length = 0
        j = p
        while j not in visited:
            visited.add(j)
            j = mapping[j]
            length += 1
        lengths.append(length)
    return lengths


# Example
pieces = list(range(11))  # 0 = buffer
perm = random_bld_permutation(pieces, first_min=4)
print(perm)
print(cycle_lengths_from_mapping(perm, pieces))
