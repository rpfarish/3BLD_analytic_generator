def get_help():
    """Provides helpful information about commands"""
    # print(f"Just enter '{args}' with no addtional arguments or parameters to see the help file")
    print("Type 'name' to find out more about the function 'name'.")
    docs = """
h | help: Display help information for commands.
m | memo: Memo the cube and handle options.
ls | letterscheme: Manage letter scheme options.
b | buff | buffer: Drill buffer and handle options.
a | algs: Generate algorithm drills.
s | sticker: Drill stickers from default buffers.
q | quit | exit: Exit the program.
c | comm: Retrieve and display commutators.
reload: Reload settings and letter scheme.
timeup | time: Display the elapsed time.
alger: Generate a scramble with a specified number of algs.
f | float: Provide scrambles with flips and cycle breaks.
t: Drill twists: 2f, 3, or 3f.
rb: Pick a random buffer from settings.json
    """
    print(docs)
    return
