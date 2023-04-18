from get_scrambles import invert_solution


def expand_comm(comm):
    if not comm or "," not in comm and "*" not in comm:
        return comm
    comm = "".join([i for i in comm if i not in ["[", "]"]])
    if comm.count(":") == 0:
        c = ""
        if "," in comm:
            a, b = comm.split(",")

        elif "*" in comm:
            a = "".join([i for i in comm if i not in ["(", ")", "2", "*"]])

    elif comm.count(":") == 1:
        split_comm = comm.split(":")

        c, ab = split_comm
        if "," in comm:
            a, b = ab.split(",")

        elif "*" in comm:
            a = "".join([i for i in ab if i not in ["(", ")", "2", "*"]])
    else:
        raise ValueError("comm wierd length", comm)

    if "," in comm:
        exp_comm = c + a + b + " " + invert_solution(a) + " " + invert_solution(b) + " " + invert_solution(c)
    elif "*" in comm and "," not in comm:
        exp_comm = c + a + a + invert_solution(c)

    return " ".join(exp_comm.split())


if __name__ == "__main__":
    print(expand_comm("[R U R', D']"))
    print(expand_comm("[R U' D' : [R' U R , D2]]"))
    print(expand_comm("(U M' U M) * 2"))
    print(expand_comm("[M' : (U' M' U' M) * 2]"))
