# four_square_cards_static.py

import os

# -----------------------
# STATIC CARD GRIDS
# -----------------------
UL = [
    ["AC","2C","3C","4C","5C","6C"],
    ["7C","8C","9C","XC","JC","QC"],
    ["KC","AD","2D","3D","4D","5D"],
    ["6D","7D","8D","9D","XD","JD"],
    ["QD","KD","AH","2H","3H","4H"],
    ["5H","6H","7H","8H","9H","XH"],
]

LR = [
    ["JH","QH","KH","AS"],
    ["2S","3S","4S","5S"],
    ["6S","7S","8S","9S"],
    ["XS","JS","QS","KS"],
]

# -----------------------
# ALPHABET GRIDS (A–X)
# -----------------------
LL_LETTERS = [
    ['S','H','A','D','O','W'],
    ['B','C','E','F','G','I'],
    ['K','L','M','N','P','Q'],
    ['R','T','U','V','X','Y'],
]

UR_LETTERS = [
    ['F','U','L','H'],
    ['E','A','R','T'],
    ['B','C','D','G'],
    ['I','K','M','N'],
    ['O','P','Q','S'],
    ['V','W','X','Y'],
]

# -----------------------
# TOKENIZER (no pathlib, no re)
# -----------------------
_RANKS = set("A23456789XJQK")
_SUITS = set("CDHS")
def _is_card(t):
    return len(t) == 2 and t[0] in _RANKS and t[1] in _SUITS

def read_cipher_cards(filename: str):
    """
    Open filename (or file with same name beside script), return list of 2-char card tokens.
    Will raise FileNotFoundError / ValueError normally; no try/except here.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alt = os.path.join(script_dir, filename)

    if os.path.isfile(filename):
        path = filename
    elif os.path.isfile(alt):
        path = alt
    else:
        attempted = [os.path.abspath(filename), os.path.abspath(alt)]
        raise FileNotFoundError(f"ciphertext file not found; tried: {attempted}")

    with open(path, "r", encoding="utf-8") as fh:
        s = fh.read().strip().upper()

    if not s:
        raise ValueError(f"{filename} is empty")

    # split on whitespace/commas/semicolons if present
    if any(c in s for c in " \t\n,;"):
        s = s.replace(",", " ").replace(";", " ")
        tokens = [p for p in s.split() if _is_card(p)]
    else:
        # concatenated stream: scan with a 2-char window
        tokens = []
        i = 0
        n = len(s)
        while i <= n - 2:
            cand = s[i:i+2]
            if _is_card(cand):
                tokens.append(cand)
                i += 2
            else:
                i += 1

    if not tokens:
        raise ValueError(f"No valid card tokens found in {filename}")

    if len(tokens) % 2:
        print(f"Warning: odd number of card tokens ({len(tokens)}); dropping final token")
        tokens = tokens[:-1]

    return tokens

# -----------------------
# FOUR-SQUARE DECRYPTION
# -----------------------
def find_position(grid, target):
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == target:
                return r, c
    return None

def decrypt(cards):
    out = []
    for i in range(0, len(cards), 2):
        a, b = cards[i], cards[i+1]
        p1 = find_position(UL, a)
        p2 = find_position(LR, b)
        if p1 is None or p2 is None:
            raise ValueError(f"Unknown card token: {a} or {b}")
        r1, c1 = p1
        r2, c2 = p2
        out.append( LL_LETTERS[r2][c1] + UR_LETTERS[r1][c2] )
    return "".join(out)

# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    cards = read_cipher_cards("cipher.txt")
    print(decrypt(cards))
