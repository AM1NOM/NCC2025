# four_square_cards_static.py

import random
import math
import copy
import os

# ===============================
# STATIC CARD GRIDS
# ===============================

# 6x6 card square (Clubs, Diamonds, Hearts A..X)
UL = [
    ["AC","2C","3C","4C","5C","6C"],
    ["7C","8C","9C","XC","JC","QC"],
    ["KC","AD","2D","3D","4D","5D"],
    ["6D","7D","8D","9D","XD","JD"],
    ["QD","KD","AH","2H","3H","4H"],
    ["5H","6H","7H","8H","9H","XH"],
]

# 4x4 card square (Spades + face hearts)
LR = [
    ["JH","QH","KH","AS"],
    ["2S","3S","4S","5S"],
    ["6S","7S","8S","9S"],
    ["XS","JS","QS","KS"],
]

# ===============================
# CARD TOKEN PARSER
# ===============================

# Simple check for valid card tokens
def is_valid_card(token):
    if len(token) != 2:
        return False
    rank = token[0]
    suit = token[1]
    return rank in "A23456789XJQK" and suit in "CDHS"

def read_cipher_cards(filename: str):
    raw = None

    # Try current working directory first
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            raw = f.read()
    else:
        # Fall back to script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, filename)
        if os.path.isfile(alt_path):
            with open(alt_path, 'r', encoding='utf-8') as f:
                raw = f.read()
        else:
            raise FileNotFoundError(f"ciphertext file not found: {filename}")

    text = raw.strip().upper()
    if not text:
        raise ValueError(f"{filename} is empty")

    cards = []

    # If separators exist, split on them
    if any(c in text for c in " ,;\n\t"):
        parts = text.replace(",", " ").replace(";", " ").split()
        for p in parts:
            if is_valid_card(p):
                cards.append(p)
    else:
        # Otherwise assume concatenated format
        i = 0
        while i + 1 < len(text):
            token = text[i:i+2]
            if is_valid_card(token):
                cards.append(token)
                i += 2
            else:
                i += 1  # slide forward if something odd shows up

    if not cards:
        raise ValueError(f"No valid card tokens found in {filename}")

    # Drop the last token if count is odd
    if len(cards) % 2 != 0:
        print(f"Warning: odd number of card tokens ({len(cards)}); dropping final token")
        cards = cards[:-1]

    return cards

# ===============================
# FOUR-SQUARE DECRYPTION
# ===============================

def find_position(grid, target):
    # Basic lookup, grids are small so this is fast enough
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == target:
                return r, c
    return None

def decrypt(cards, LL, UR):
    plaintext = []

    # Process cards as digraphs
    for i in range(0, len(cards), 2):
        c1 = cards[i]
        c2 = cards[i + 1]

        pos1 = find_position(UL, c1)
        pos2 = find_position(LR, c2)

        if pos1 is None or pos2 is None:
            raise ValueError(f"Invalid card in ciphertext: {c1} or {c2}")

        r1, c1 = pos1
        r2, c2 = pos2

        # Four-square swap
        p1 = UR[r1][c2]
        p2 = LL[r2][c1]

        plaintext.append(p2 + p1)

    return ''.join(plaintext)

# ===============================
# HILL-CLIMBING FUNCTIONS
# ===============================

def load_quadgrams(filename='english_quadgrams.txt'):
    quadgrams = {}

    if not os.path.isfile(filename):
        raise FileNotFoundError(
            f"Quadgram file '{filename}' not found. "
            "Download from practicalcryptography.com"
        )

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            quad, count_str = parts
            if len(quad) != 4:
                continue
            try:
                count = int(count_str)
                if count > 0:
                    quadgrams[quad] = count
            except ValueError:
                pass

    if not quadgrams:
        raise ValueError("No quadgrams loaded from file.")

    return quadgrams

def fitness(text, log_probs, floor):
    # Average quadgram log score
    if len(text) < 4:
        return 0.0

    score = 0.0
    for i in range(len(text) - 3):
        quad = text[i:i+4]
        score += log_probs.get(quad, floor)

    return score / (len(text) - 3)

def random_grid(rows, cols, alphabet):
    # Shuffle letters into a grid
    letters = list(alphabet)
    random.shuffle(letters)
    return [letters[i * cols:(i + 1) * cols] for i in range(rows)]

def swap_in_grid(grid):
    # Swap two random positions
    rows = len(grid)
    cols = len(grid[0])

    a = random.randrange(rows * cols)
    b = random.randrange(rows * cols)
    while a == b:
        b = random.randrange(rows * cols)

    r1, c1 = divmod(a, cols)
    r2, c2 = divmod(b, cols)

    new_grid = copy.deepcopy(grid)
    new_grid[r1][c1], new_grid[r2][c2] = new_grid[r2][c2], new_grid[r1][c1]
    return new_grid

# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    cards = read_cipher_cards("cipher.txt")
    print(f"Loaded {len(cards)} card tokens from ciphertext.")

    quadgrams = load_quadgrams()
    total = sum(quadgrams.values())
    log_probs = {k: math.log(v / total) for k, v in quadgrams.items()}
    floor = math.log(0.01 / total)
    print("Quadgram statistics loaded.")

    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    best_score = float('-inf')
    best_LL = None
    best_UR = None
    best_text = ""

    num_restarts = 5
    iterations_per_restart = 10000

    for restart in range(num_restarts):
        print(f"\nRestart {restart + 1}/{num_restarts}")

        LL_LETTERS = random_grid(4, 6, alphabet)
        UR_LETTERS = random_grid(6, 4, alphabet)

        current_text = decrypt(cards, LL_LETTERS, UR_LETTERS)
        current_score = fitness(current_text, log_probs, floor)

        for i in range(iterations_per_restart):
            if random.random() < 0.5:
                new_LL = swap_in_grid(LL_LETTERS)
                new_UR = UR_LETTERS
            else:
                new_LL = LL_LETTERS
                new_UR = swap_in_grid(UR_LETTERS)

            new_text = decrypt(cards, new_LL, new_UR)
            new_score = fitness(new_text, log_probs, floor)

            if new_score > current_score:
                LL_LETTERS = new_LL
                UR_LETTERS = new_UR
                current_text = new_text
                current_score = new_score

            if (i + 1) % 1000 == 0:
                print(f"  Iter {i + 1}: score {current_score:.4f} | text: {current_text[:50]}...")

        if current_score > best_score:
            best_score = current_score
            best_LL = copy.deepcopy(LL_LETTERS)
            best_UR = copy.deepcopy(UR_LETTERS)
            best_text = current_text
            print(f"New best score: {best_score:.4f}")

    print("\nHill-climbing complete.")
    print("Best plaintext:")
    print(best_text)

    print("\nBest LL_LETTERS grid:")
    for row in best_LL:
        print(row)

    print("\nBest UR_LETTERS grid:")
    for row in best_UR:
        print(row)
