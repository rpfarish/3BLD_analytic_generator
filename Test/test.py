from Commutator.expand_comm import expand_comm


def test_expand_comm():
    assert expand_comm("[R U R', D']") == "R U R' D' R U' R' D"
    assert expand_comm("[R U' D' : [R' U R , D2]]") == "R U' D' R' U R D2 R' U' R D2 D U R'"
    assert expand_comm("(U M' U M) * 2") == "U M' U M U M' U M"
    assert expand_comm("[M' : (U' M' U' M) * 2]") == "M' U' M' U' M U' M' U' M M"
    assert expand_comm("R D R' U: D/R U R'") == "R D R' U D R U R' D D R U' R' D U' R D' R'"
    assert expand_comm("R : U/R D R'") == "R U R D R' U U R D' R' U R'"
    assert expand_comm("U'/L' E L") == "U' L' E L U' U' L' E' L U'"
    assert expand_comm("(M' U) * 4") == "M' U M' U M' U M' U"


if __name__ == '__main__':
    test_expand_comm()
    print("All test cases passed!")
