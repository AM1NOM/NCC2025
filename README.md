# National Cipher Challenge2025

Open this [pdf|https://github.com/AM1NOM/NCC2025/edit/main/README.md] to learn how we did this challenge.

At the start, we didn’t know how the cards were arranged in the missing squares, and we
also didn’t know the key grids needed to decrypt the message. Since there are far too
many possible arrangements to try by hand, the only practical option was to search for
them programmatically.
The first step was to write a basic decryption routine. This function takes a proposed key
(the two unknown Four-Square grids), reads the ciphertext from cipher.txt, and
applies the Four-Square rules using the fixed card squares. Given a key, it produces a
candidate plaintext. On its own this doesn’t tell us whether the result is meaningful
English, but it lets us test keys quickly.
Next, we built the main solver around this decryption function. The solver uses quadgram
analysis to evaluate how “English-like” a decrypted text is. Quadgrams are sequences of
four letters, and by using frequency data from english_quadgrams.txt, we can
assign a numerical score to any piece of text. Text with common English letter patterns
gets a higher score, while random noise scores poorly. This gives the program an
objective way to compare different keys.
The solving process starts by generating random keys for the unknown grids. For each
key, the ciphertext is decrypted and scored using the quadgram fitness function. The
program then makes small changes to the key, typically by swapping two letters in one
of the grids, and decrypts the text again. If the new key produces a higher score, it is kept;
if not, it is discarded. By repeating this process thousands of times, the key gradually
improves and the plaintext becomes more readable.
To avoid getting stuck in a bad local solution, the program performs multiple restarts.
Each restart begins with a fresh random key and runs the same improvement process. At
the end, the best-scoring result across all restarts is selected as the final output.
For the solver to work correctly, english_quadgrams.txt must be located in the
same directory as four-s.py, since it is loaded at runtime to build the scoring model.
Without this file, the program has no way to judge whether a decrypted message looks
like real English.
