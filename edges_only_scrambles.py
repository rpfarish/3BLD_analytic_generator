from webbrowser import open_new_tab

from Cube.cube import Cube
from get_scrambles import get_scramble

"""For practicing edges only solves but with full scrambles"""

def url_encode(s):
    """:s scramble"""
    s = s.split(' ')
    encoded_url = []
    for move in s:
        if move.endswith("'"):
            encoded_url.append(move.replace("'", "-") + "_")
        else:
            encoded_url.append(move + "_")
    return ''.join(encoded_url)


number = 1

scramble = get_scramble()
last_scramble = scramble
c = Cube(scramble)

has_parity = c.has_parity
print(number, scramble, "Parity" * has_parity, end='')
number += 1
u = ''

while True:
    last_scramble = scramble
    scramble = get_scramble()
    c = Cube(scramble)

    has_parity = c.has_parity
    if input() == 'y':
        url = "https://alg.cubing.net/?setup=" + url_encode(last_scramble)
        print(url)
        open_new_tab(url)
    print(number, scramble, "Parity" * has_parity, end='')
    number += 1
    if u:
        break
a = """
1-3 major weaknesses 
when analysing leave no stone unturned

if something happens only once it's a mistake, but if something happens repeatedly 
and if there's something that happens everytime you get a bad solve then that's a weakness that kills your solve

learn something new
practice it until your comfortable with it 
fix your weaknesses 
repeat
"""

"""
mistraced cycle break. (first letter) breaking from some random sticker instead of RU (second letter)
forgetting which sticker i broke to.
poor ability to cycle break quickly to a floating 2e2e
"""
