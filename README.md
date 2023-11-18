# 3BLD Analytic Generator

## Generates 3BLD specific scrambles to drill various algsets

- Memo
- Gen scrambles
- Get comms

The repo allows you to memo and dlin trace a scramble, generate scrambles for various alg sets (defined below) and get and compare comms from different sheets

Alg sets:
- Full floating trainer (both like [Eli's Buffer Trainer](https://elliottkobelansky.github.io/buffer-trainer/) and random state with cycle breaks)
- Specific letter pairs in a random scramble
- Twists
- Flips
- LTCT


This also allows you to specify what cycles you would like to drill and
generates a scramble with those specific letter pairs in it.
These scrambles are random move, but not random state but should be good enough for training.
Please note that the letters on the buffers are not important, but each of them need to be unique.

 It supports intelligent cycle breaking, memoing with alternate pseudoswaps, and the identification of specific cube states like 2-flips, 2-twists, 3-twists, and parity twists. Users can customize the lettering scheme and generate training scrambles based on specified algorithms or letter pairs for both edges and corners. The repository includes commands for memoizing the cube, generating training scrambles, managing letter schemes, drilling buffers, displaying commutators, and more. Note that some features are still a work in progress. The repository emphasizes functionality for blindfolded solving training.

# Features:

## Memo the cube:

WIP

- to memorize the cube with these specific qualities: intelligent cycle breaking, memoing with alternate pseudoswaps,
  identifying: 2-flips, 2-twists, 3-twists, parity + twist, identifying floats, and trying to grade each of these
  solutions with some sort of metric and potentially identify 3-twist/2-twist + parity recommended solutions. Maybe
  using some metric like regrips or total moves
- customizable lettering scheme for people who don't use Speffz

## Generate Training Scrambles
      
- Given a list of algs will generate random scrambles to drill those algs, and will print the alg if you forget it and
  keep track of how many and which ones it was
- Given a list of letter pairs (for either edges or corners) will generate random scrambles that have one or more of
  those letter pairs in a given scramble

- Working on drilling corners and edges and abstracting that logic
- I don't recommend going above 2 else it will take forever
- Given a sticker will let you drill all the cycles containing that sticker (forwards, backwards or both) by generating
  a random scramble that has one those letter pairs in a given scramble
- will let you repeat a certain sticker, letter pair or alg
- Generates a scramble with certain 2-flip, 2-twist, 3-twist, parity + twist
- Given buffer order will generate a scramble with just the cycles with that buffer scrambled

Most of this stuff is still wip.

## Get Comms from sheets
- You can load in comms given some csv files or a spreadsheet and be able to compare side by side multiple peoples lists for full floating.

Note: Please put all piece names in Singmaster notation e.g. UR or RDB except for when specifying args for drill sticker (this may not be necessary anymore).

# CMD Commands List:

### Memo: `memo [scramble] [-l filename] [-s filename]`
------------------------------------------------------------------------------------------------------------------------
- **Description:** This command allows you to memo the cube and provides options for loading and saving scrambles. Note:
  does not support
  wide move scrambles

- **Options:**
    - scramble: The scramble to memo.
    - -l filename: Load scrambles from the FILENAME text file
    - -s filename: Save the SCRAMBLE to the FILENAME text file

- **Usage Examples**:
    - Memo the scramble
      ```
      memo U B2 D L2 B2 D' L2 R2 D' R2 D' B D2 U F' L2 U R' D' L' U2
      ```
    - Memo scramble(s) from text file
      ```
        memo -l saved_scrambles.txt
      ```
    - Memo the scramble and append it to the text file
       ```
       memo U2 M' U2 M -s new_scramble.txt
       ```

### Letter Scheme: `ls [-d] [-l] [-c]`
------------------------------------------------
- **Description:** Manage letter scheme options.

- **Options:**
    - -d: Dumps the current loaded letter scheme for the standard Singmaster notation
    - -l: Loads the letter scheme from settings.json
    - -c: prints the current letter scheme

- **Usage Examples**:
    - Dump the letter scheme

      ```
      ls dump
      ```
    - Load the letter scheme

      ```
      ls -load
      ```
    - Print the current letter scheme

      ```
      ls -cur
      ```

### Sticker:  `s | sticker [sticker] [-t e | c] [[-e] | [-c]] [-ex XY ...]`
---------------------------------------------------------------------------
- **Description**: Drill a sticker from default buffers or load pairs to drill from a text file which can be found in the drill_lists directory. Corner and edge pairs can only be drilled one at a time.

- **Options:**
    - sticker: When a list to drill is not specified, this will load all the sticker + xy letter pairs. This parameter must be put first.
    - -type corner | edge: Specifies the type of the piece to drill. Only needed when piece type is ambiguous. 
    - -edge: Loads letter pairs to drill from drill_list_edges.txt 
    - -corner: Loads letter pairs to drill from drill_list_corners.txt 
    - -exclude: Excludes letterpairs from being drilled and are entered one at a time with a space separating each of then. This parameter must be put last.
    

- **Usage Examples**:
    - Drill the corner sticker N (RUB)

      ```
      sticker N -type corner
      ```
    - Drill the corner sticker RUB

      ```
      sticker RUB
      ```
    - Drill the edges from drill_list_edges.txt 

      ```
      sticker -e
      ```
    - Drill the edge sticker UR but exclude the cycles UR RD, UR LB, and UR LF 

      ```
      sticker UR -ex RD LB LF
      ```
    - Drill the edge sticker B (UR) but exclude the cycles BO, BH, and BF 

      ```
      sticker B -t e -ex O H F
      ```


### HELP: `help`
--------------------------------------------
- **Description:** Provides list of commands

### Buffer: `buffer [buffer name] [-l optional <name=filename>] [-r]`

- **Description**: Drill buffer, specifying the buffer name, and handle options such as loading, random generation, and
  more. Note: all buffers can be saved to the same file

- **Options:**
    - -l <filename>: Load the current buffer drill file from JSON to allow multiple concurrent buffer drill sessions.
      Note
      that if you start a new session without -l, it will erase the existing save file.
    - -r: Randomly generate cycles with no limit on repeating pairs.

- **Example Usages**:

    - Drill the "UF" buffer with random pair generation:

      ```
         buffer UF -r
      ```

    - Load a previously saved buffer drill file named "saved_buffer.json" and continue the session:

      ```
         buffer UR -l saved_buffer.json
      ```

    - Start a new buffer drill session for "UB" without loading a previous file:

      ```
         buffer UB
      ```

    - Load a previously saved default buffer drill file and continue the session

      ```
         buffer UB -l
      ```

These examples demonstrate how to use the buffer command with various options.

### Quit: `quit`
----------------------------------------------------------------------------------
- **Description:** Exits the program when in the main terminal and quits the current operation when running a command

### Comm: `comm [buffer] [pair | pairs...]`
----------------------------------------------------------------------------------
- **Description:** Retrieve and display commutators.
- **Options:**
    - -r: Rapid mode allows you to enter many pairs in and keep the buffer selected for each query
    - -b: Selects a new buffer while in rapid mode

- **Example Usages**:

    - Display commutators for the buffer UF with pairs AB and CD:
        ```
        comm UF AB CD
        ```

    - Enter rapid mode for buffer UR:

       ```
       comm -r UR
       ```

    - Switch buffer to DR while in rapid mode:

      ```
      comm -b DR
      ```

### Reload: `reload`
----------------------------------------------------------------------------------
### Time up: `timeup`
----------------------------------------------------------------------------------
- **Description:** Time since program started.

### Alger: `alger [alg count]`
----------------------------------------------------------------------------------
### Cycle Break Float: `float [buffer]`
----------------------------------------------------------------------------------
### Twists: `twist [twist type]`
----------------------------------------------------------------------------------
- **Options:**
- `[twist type]` 2f: floating 2-twist, 3: 3-twist, or 3f: floating 3-twist

### Random Buffer: `rb`
----------------------------------------------------------------------------------
- **Description:** Pick a random buffer from settings.json

### LTCT: `ltct [ltct type]`
----------------------------------------------------------------------------------
- **Description:** Drills specified LTCT algs

- **Options:**
    - -s: Generates a full scramble with an ltct
    - -u: Adds all UU LTCT to be drilled
    - -ud: Adds some UD LTCT to be drilled
    - -def: Adds default LTCT: UU and some UD

### Flips: `flip`
----------------------------------------------------------------------------------
- **Description:** Drills all 2 flips
