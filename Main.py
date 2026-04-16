import os
import sys

# Import the cipher file
from cipher import encrypt_text, decrypt_text


# File handling
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file_handle:
            return file_handle.read()
    except OSError as error:
        print(f"  [ERROR] Cannot read '{filepath}': {error}")
        sys.exit(1)

def write_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as file_handle:
            file_handle.write(content)
    except OSError as error:
        print(f"  [ERROR] Cannot write '{filepath}': {error}")
        sys.exit(1)


# Functions 
def encryption_function(raw_path, encrypted_path, shift1, shift2):
    raw_text = read_file(raw_path)
    encrypted_text = encrypt_text(raw_text, shift1, shift2)
    write_file(encrypted_path, encrypted_text)
    print(f"  Encrypted Successfully →  {encrypted_path}")


def decryption_function(encrypted_path, decrypted_path, shift1, shift2):
    encrypted_text = read_file(encrypted_path)
    decrypted_text = decrypt_text(encrypted_text, shift1, shift2)
    write_file(decrypted_path, decrypted_text)
    print(f"  Decrypted Successfully  →  {decrypted_path}")


def verification_function(original_path, decrypted_path):
    original_text  = read_file(original_path)
    decrypted_text = read_file(decrypted_path)

    if original_text == decrypted_text:
        print("  Verification PASSED — decrypted text matches the original exactly.")
        return True

    print("  Verification FAILED — decrypted text does NOT match the original.")

    # First character
    for position, (orig_char, dec_char) in enumerate(zip(original_text, decrypted_text)):
        if orig_char != dec_char:
            print(f"         First mismatch at index {position}: "
                  f"expected {orig_char!r}, got {dec_char!r}")
            break

    # Length discrepancy
    if len(original_text) != len(decrypted_text):
        print(f"         Length mismatch: "
              f"original = {len(original_text)} chars, "
              f"decrypted = {len(decrypted_text)} chars")

    return False


# User input
def get_positive_integer(label):

    while True:
        raw_input = input(f"  Enter {label} (positive integer): ").strip()
        try:
            value = int(raw_input)
            if value > 0:
                return value
            print(f"  [!] '{raw_input}' is not a positive integer. Please try again.")
        except ValueError:
            print(f"  [!] '{raw_input}' is not a valid integer. Please try again.")


# Main
def main():
    # File paths
    base_directory = os.path.dirname(os.path.abspath(__file__))
    raw_path       = os.path.join(base_directory, "raw_text.txt")
    encrypted_path = os.path.join(base_directory, "encrypted_text.txt")
    decrypted_path = os.path.join(base_directory, "decrypted_text.txt")

    # check
    if not os.path.isfile(raw_path):
        print(f"[ERROR] Source file not found: '{raw_path}'")
        print("        Please ensure 'raw_text.txt' is in the same directory as this script.")
        sys.exit(1)

    separator = "=" * 56

    # user inputs 
    shift1 = get_positive_integer("shift1")
    shift2 = get_positive_integer("shift2")
    print("-" * 56)

    # Executation
    encryption_function(raw_path,       encrypted_path, shift1, shift2)
    decryption_function(encrypted_path, decrypted_path, shift1, shift2)
    verification_function(raw_path,     decrypted_path)

    print(separator)
    print()


# Main
if __name__ == "__main__":
    main()
