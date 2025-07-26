def get_help():
    """Provides helpful information about commands"""
    docs = """
Type 'command' to find out more. 
Simple commands with no options have no extra info.

h  | help  : Display help information about commands
c  | comm  : Retrieve and display commutators.
m  | memo  : Generates memorization and info for the input scramble
ls | ltrscm: Load and unload letterscheme 

s  | stkr  : Drill sticker from default buffers.
b  | buffer: Drill all floating cycles for the input buffer with edge or corner only scrambles
rb | rndbfr: Like Buffer but random with cycle breaks and flips 

t   : Drill twists: 2f, 3, or 3f.
ltct: Drill LTCT either a full scramble or just algs
flip: Drill 2 flips

alger : Generate a scramble with a specified number of algs. (Needs fine tuning)
arb   : Pick a random buffer from settings.json
reload: Reload settings and letter scheme.
timeup | time: Display the elapsed time.
exit   | quit: Exit the program

-- Broken --
a | algs: Generate algorithm drills.
    """
    print(docs)
    return
