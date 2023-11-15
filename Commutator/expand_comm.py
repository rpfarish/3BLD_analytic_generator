import re

from .invert_solution import invert_solution as inv


def expand_comm(comm):
    if not comm or not any(sym in comm for sym in [",", "*", ":", "/"]):
        return comm
    comm = comm.replace("[", "").replace("]", "")
    split_comm = comm.split(":")
    c, ab = split_comm if len(split_comm) == 2 else ("", comm)
    a, b, num = "", "", 0
    if "," in comm:
        a, b = ab.split(",")
        exp_comm = f"{c}{a}{b} {inv(a)} {inv(b)} {inv(c)}"
    elif "/" in comm:
        a, b = ab.split("/")
        exp_comm = f"{c} {a} {b} {a} {a} {inv(b)} {a} {inv(c)}"
    elif "*" in comm:
        a = "".join([i for i in ab if i not in "()*" and not i.isdigit()])
        int_match = re.search(r'\*\s*(\d+)', comm)
        if int_match:
            num = int(int_match.group(1))
        exp_comm = f"{c}{' ' + a * num + ' '}{inv(c)}"
    else:
        exp_comm = f"{c} {ab} {inv(c)}"

    return " ".join(exp_comm.split())


if __name__ == "__main__":
    print(expand_comm("[R U R', D']"))
    print(expand_comm("[R U' D' : [R' U R , D2]]"))
    print(expand_comm("(U M' U M) * 2"))
    print(expand_comm("[M' : (U' M' U' M) * 2]"))
    print(expand_comm("R D R' U: D/R U R'"))
    print(expand_comm("R : U/R D R'"))
    print(expand_comm("U'/L' E L"))
    print(expand_comm("(M' U) * 4"))


    def test_expand_comm():
        assert expand_comm("[R U R', D']") == "R U R' D' R U' R' D"
        assert expand_comm("[R U' D' : [R' U R , D2]]") == "R U' D' R' U R D2 R' U' R D2 D U R'"
        assert expand_comm("(U M' U M) * 2") == "U M' U M U M' U M"
        assert expand_comm("[M' : (U' M' U' M) * 2]") == "M' U' M' U' M U' M' U' M M"
        assert expand_comm("R D R' U: D/R U R'") == "R D R' U D R U R' D D R U' R' D U' R D' R'"
        assert expand_comm("R : U/R D R'") == "R U R D R' U U R D' R' U R'"
        assert expand_comm("U'/L' E L") == "U' L' E L U' U' L' E' L U'"
        assert expand_comm("(M' U) * 4") == "M' U M' U M' U M' U"


    test_expand_comm()
    print("All test cases passed!")
