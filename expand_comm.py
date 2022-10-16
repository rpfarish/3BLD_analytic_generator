from get_scrambles import invert_solution


def expand_comm(comm):
    if not comm or ',' not in comm:
        return comm
    comm = "".join([i for i in comm if i not in ["[", "]"]])
    if comm.count(":") == 0:
        c = ""
        try:
            a, b = comm.split(",")
        except ValueError as e:
            print(e, comm)
            quit()
    elif comm.count(":") == 1:
        split_comm = comm.split(":")

        c, ab = split_comm
        a, b = ab.split(",")
    else:
        raise ValueError("comm wierd length", comm)

    exp_comm = c + a + b + " " + invert_solution(a) + " " + invert_solution(b) + " " + invert_solution(c)

    return " ".join(exp_comm.split())


if __name__ == "__main__":
    print(expand_comm("[R U R', D']"))
    print(expand_comm("[R U' D' : [R' U R , D2]]"))
