# Letter Pair Finder

The repo allows you to quickly memorize Rubik's Cubes.
This also allows you to specify what cycles you would like to drill and
generates a scramble with those specific letter pairs in it.
Supports both edge and corner piece types though separately.
Does not account for breaking into twists, flips or parity shifting.
These scrambles are random move, but not random state but should be good enough for training
Please note that the letters on the buffers are not important, but each of them need to be unique.

## Features:

### Memo the cube
Syntax: memo [scramble]

- to memorize the cube with these specific qualities: intelligent cycle breaking, memoing with alternate pseudoswaps,
  identifying: 2-flips, 2-twists, 3-twists, parity + twist, identifying floats, and trying to grade each of these
  solutions with some sort of metric and potentially identify 3-twist/2-twist + parity recommended solutions. Maybe
  using some metric like regrips or total moves
- customizable lettering scheme for people who don't use Speffz

### Generate Training Scrambles

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

# 3BLD_analytic_generator

Note: Please put all piece names in Singmaster notation e.g. UR or RDB exept for when specifying args for drill sticker

## CMD Commands List:

### Memo: `memo [scramble] [-l filename] [-s filename]`

#### Options:

- `-l filename`  loads scrambles from FILENAME text file
- `-s filename` saves SCRAMBLE to FILENAME text file

### HELP: `help [name]`

### Letter Scheme: `ls [-d] [-l]`

#### Options:

- `-d` dumps the current loaded letter scheme for the standard Singmaster notation
- `-l` loads the letter scheme from settings.json

### Buffer: `buffer [buffer name] [-l optional <name=filename>] [-r]`

#### Options:

- `-l <filename>` loads the current buffer drill file from json to allow multiple concurrent buffer drill sessions (
  Note: if you start a new session without -l it will erase the existing save file)
- `-r` randomly generates cycles with no limit on repeating pairs

### Quit: `quit`

### Comm: `comm [buffer] [pair | pairs...]`

#### Options:

- `-r` rapid mode allows you to enter many pairs in and keep the buffer selected for each query
- `-b` selects a new buffer while in rapid mode

### Reload: `reload`

### Time up: `timeup`

### Alger: `alger [alg count]`

### Cycle Break Float: `float [buffer]`
