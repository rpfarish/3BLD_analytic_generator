from Cube.solution import Solution
from interface import CLIInterface
from Settings.settings import Settings


class Commands:
    def __init__(self, ui: CLIInterface, settings: Settings) -> None:
        self.ui = ui
        self.settings = settings

    def memo(self, args) -> None:
        """Memo: memo [scramble] [-l filename] [-s filename]
        Description:
            Describes memorization for a scramble in the given
            letter scheme and provides analysis like approximate
            alg count, dlin trace, or dlin optimal combination
            (Currently only available for edges).
            For scrambles with parity, UF-UR swap is done
            (or whatever swap is specified in settings).
            Swap must preserve F/B edge orientation.
        Options:
            -l filename loads scrambles from FILENAME text file
            -s filename saves SCRAMBLE to FILENAME text file
        Aliases:
            m
        """

        if not args:
            self.ui.warning("No scramble provided")
            self.ui.info("Usage: memo <scramble>")
            self.ui.info("Example: memo R U R' U' R' F R2 U' R' U' R U R' F'")
            return

        scramble = " ".join(args).replace("3'", "")

        if scramble.startswith("-l"):
            _, file_name = scramble.split()
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            with open(file_name) as f:
                for num, scram in enumerate(f.readlines(), 1):
                    # print("Scramble number:", num)

                    if not scram:
                        continue
                    # TODO:: cleanup memo output
                    s = Solution(scram.strip().strip('"'), self.ui, self.settings)
                    s.display()
            return

        elif "-s" in scramble:
            scramble = scramble.strip('"').split()
            f_index = scramble.index("-s")
            file_name = scramble[f_index + 1]
            scramble = scramble[:f_index]
            file_name = f"{file_name}.txt" if ".txt" not in file_name else file_name
            scramble = " ".join(scramble)

            with open(file_name, "a+") as f:
                f.write(scramble.strip('"'))
                f.write("\n")
                f.close()

        if not scramble:
            self.ui.warning("No input scramble provided")
            return

        # TODO:: cleanup memo output
        s = Solution(scramble.strip().strip('"'), self.ui, self.settings)
        s.display()
