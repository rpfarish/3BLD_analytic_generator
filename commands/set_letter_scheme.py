import json

from Cube.letterscheme import LetterScheme


def set_letter_scheme(args, letter_scheme: LetterScheme) -> LetterScheme:
    """Letter Scheme: ls [-d] [-l] [-c]
Options:
    -d dumps the current loaded letter scheme for the standard Singmaster notation
    -l loads the letter scheme from settings.json
    -c prints the current letter scheme
Aliases:
    letterscheme"""
    # todo add current
    if '-cur' in args or '-c' in args:
        print("Current:", letter_scheme.get_all_dict())
        return letter_scheme
    elif '-dump' in args or '-d' in args:
        print("Previous:", letter_scheme.get_all_dict())
        print("Current: ", LetterScheme(use_default=True).get_all_dict())
        return LetterScheme(use_default=True)
    elif '-load' in args or '-l' in args:
        print("Previous:", letter_scheme.get_all_dict())
        with open("settings.json") as f:
            settings = json.loads(f.read())
            print("Current: ", LetterScheme(ltr_scheme=settings['letter_scheme']).get_all_dict())
            return LetterScheme(ltr_scheme=settings['letter_scheme'])
    else:
        print("Warning action not performed")
        print("Reloading letterscheme")
        return set_letter_scheme(["-load"], letter_scheme)
