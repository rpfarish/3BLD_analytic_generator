from interface import CLIInterface


def get_help(ui: CLIInterface):
    """Provide helpful information about commands."""
    docs = """
Type 'command' to find out more. 
Simple commands with no arguments have no extra info.

h  | help  : Display help information about commands
c  | comm  : Retrieve and display commutators.
m  | memo  : Show memorization and info for the given scramble(s)
ls | ltrscm: Load and display letterscheme 

d  | drill : Drill a list of letterpairs from text file until all pairs are drilled.
b  | buffer: Drill all floating cycles for the input buffer with edge or corner only scrambles
rb | rndbfr: Like Buffer but random with cycle breaks and flips 

t   : Drill twists: 2f, 3, or 3f.

alger : Generate a scramble with a specified number of algs. (Needs fine tuning)
arb   : Pick a random buffer from settings.json
clear : Clears the screen.
reload: Reload settings and letter scheme.
timeup | time: Display the elapsed time since startup.
exit   | quit: Exit the program
"""

    broken = """
-- Not available / Broken --
a | algs: Generate algorithm drills.
flip: Drill 2 flips
ltct: Drill LTCT either a full scramble or just algs
    """

    ui.header("3BLD Analytic Generator - Command Reference")
    ui.info(docs)
    ui.error(broken)
    ui.info("Tip: Use '!' or '!r' to repeat the last command")
