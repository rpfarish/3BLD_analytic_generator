import cmd
from pprint import pprint

import dlin

from Cube.letterscheme import letter_scheme


class LetterPairFinder(cmd.Cmd):
    intro = "Welcome to the Letter Pair Finder. Type help or ? to list commands."
    prompt = "(3bld) "

    def do_m(self, scramble):
        """See memo for more info"""
        self.do_memo(scramble)

    def do_memo(self, scramble: str):
        """Syntax: Memo <scramble> <[-f filename] | [-fs filename]>
        -f: displays the memorization for all scrambles in <filename>.txt
        -fs: displays the memorization for the entered scramble and saves it to <filename>.txt
        """
        if not scramble:
            print("Syntax: <scramble> <[-f filename] | [-fs filename]>")
            return
        if scramble.startswith("-f"):
            _, file_name = scramble.split()
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            with open(file_name) as f:
                for num, scram in enumerate(f.readlines(), 1):
                    print("Scramble number:", num)
                    pprint(self.memo(scram.strip("\n").strip()))
        elif "-fs" in scramble:
            scramble = scramble.split()
            f_index = scramble.index("-fs")
            file_name = scramble[f_index + 1]
            scramble = scramble[:f_index]
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            scramble = " ".join(scramble)

            with open(file_name, "a+") as f:
                f.write(scramble)
                f.write("\n")
                f.close()

            pprint(self.memo(scramble))
        else:
            pprint(self.memo(scramble))

    @staticmethod
    def memo(scramble):
        from main import memo_cube

        memo_cube(scramble, letter_scheme)
        return dlin.trace(scramble)

    @staticmethod
    def do_quit(_):
        quit()

    @staticmethod
    def do_ls(args):
        if args:
            pass


# LetterPairFinder().cmdloop()
