import string

# Alphabet classification sets
LOWER_FIRST_HALF = "abcdefghijklm"
LOWER_SECOND_HALF = "nopqrstuvwxyz"
UPPER_FIRST_HALF = "ABCDEFGHIJKLM"
UPPER_SECOND_HALF = "NOPQRSTUVWXYZ"

# Low-level group rotation
def _rotate_within_group(char, group, offset):
    index = group.index(char)
    new_index = (index + offset) % len(group)
    return group[new_index]

# Single-character encryption
def encrypt_char(char, shift1, shift2):
    # Lowercase first half: a-m
    if char in LOWER_FIRST_HALF:
        return _rotate_within_group(char, LOWER_FIRST_HALF, shift1 * shift2)

    # Lowercase second half: n-z
    if char in LOWER_SECOND_HALF:
        return _rotate_within_group(char, LOWER_SECOND_HALF, -(shift1 + shift2))

    # Uppercase first half: A-M
    if char in UPPER_FIRST_HALF:
        return _rotate_within_group(char, UPPER_FIRST_HALF, -shift1)

    # Uppercase second half: N-Z
    if char in UPPER_SECOND_HALF:
        return _rotate_within_group(char, UPPER_SECOND_HALF, shift2 ** 2)

    # Non-alphabetic characters unchanged
    return char


# Single-character decryption
def decrypt_char(char, shift1, shift2):
    # lowercase first half
    if char in LOWER_FIRST_HALF:
        return _rotate_within_group(char, LOWER_FIRST_HALF, -(shift1 * shift2))

    # lowercase second half
    if char in LOWER_SECOND_HALF:
        return _rotate_within_group(char, LOWER_SECOND_HALF, shift1 + shift2)

    # uppercase first half
    if char in UPPER_FIRST_HALF:
        return _rotate_within_group(char, UPPER_FIRST_HALF, shift1)

    # uppercase second half
    if char in UPPER_SECOND_HALF:
        return _rotate_within_group(char, UPPER_SECOND_HALF, -(shift2 ** 2))

    return char


# String encryption
def encrypt_text(text, shift1, shift2):
    return "".join(encrypt_char(ch, shift1, shift2) for ch in text)


# String decryption
def decrypt_text(text, shift1, shift2):
    return "".join(decrypt_char(ch, shift1, shift2) for ch in text)
