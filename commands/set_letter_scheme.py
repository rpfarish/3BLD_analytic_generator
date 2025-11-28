import json

from Cube.letterscheme import LetterScheme


def display_letter_scheme(letter_scheme: LetterScheme):
    cur_ls = letter_scheme.get_all_dict()
    t = tuple(cur_ls.items())
    print("Edges:\tCorners:")
    for i in range(24):
        a, b = t[i]
        c, d = t[i + 24]
        print(f"{a}: {b}\t{c}: {d}")

    print()


def set_letter_scheme(args, letter_scheme: LetterScheme) -> LetterScheme:
    """Letter Scheme: ls [-l] [-c]
    Options:
        -l loads the letter scheme from settings.json
        -c prints the current letter scheme
    Aliases:
        ltrscm
    """
    if "-cur" in args or "-c" in args:
        print("Current Letter Scheme:")
        display_letter_scheme(letter_scheme)
        return letter_scheme

    elif "-dump" in args or "-d" in args:
        print("Previous Letter Scheme:")
        display_letter_scheme(letter_scheme)
        new_ls = LetterScheme(use_default=True)
        print("Current Letter Scheme:")
        display_letter_scheme(new_ls)
        return new_ls

    elif "-load" in args or "-l" in args:
        print("Previous Letter Scheme:")
        display_letter_scheme(letter_scheme)
        with open("settings.json") as f:
            settings = json.loads(f.read())
            new_ls = LetterScheme(ltr_scheme=settings["letter_scheme"])
            print("Current Letter Scheme:")
            display_letter_scheme(new_ls)
            return new_ls

    else:
        print("Warning action not performed")
        print("Reloading letterscheme")
        return set_letter_scheme(["-load"], letter_scheme)
