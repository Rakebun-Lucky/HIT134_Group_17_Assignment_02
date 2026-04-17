import os
import sys

# Import the cipher file
from cipher import encrypt_text, decrypt_text


# File handling
def read_file(filepath):  # Read the entire contents of a text file and return it as a string.
    try:
        with open(filepath, 'r', encoding='utf-8') as file_handle:
            return file_handle.read()
    except OSError as error:
        print(f"  [ERROR] Cannot read '{filepath}': {error}")
        sys.exit(1)

def write_file(filepath, content):   # Write content to a text file, creating or overwriting it as needed.
    try:
        with open(filepath, 'w', encoding='utf-8') as file_handle:
            file_handle.write(content)
    except OSError as error:
        print(f"  [ERROR] Cannot write '{filepath}': {error}")
        sys.exit(1)


# Functions 
def encryption_function(raw_path, encrypted_path, shift1, shift2): # Read the plaintext file, encrypt it, and write the result to disk.
    raw_text = read_file(raw_path)
    encrypted_text = encrypt_text(raw_text, shift1, shift2)
    write_file(encrypted_path, encrypted_text)
    print(f"  Encrypted Successfully →  {encrypted_path}")


def decryption_function(encrypted_path, decrypted_path, shift1, shift2): # Read the encrypted file, decrypt it, and write the result to disk.
    encrypted_text = read_file(encrypted_path)
    decrypted_text = decrypt_text(encrypted_text, shift1, shift2)
    write_file(decrypted_path, decrypted_text)
    print(f"  Decrypted Successfully  →  {decrypted_path}")


def verification_function(original_path, decrypted_path): # Compare the original plaintext with the decrypted output.
    original_text  = read_file(original_path)
    decrypted_text = read_file(decrypted_path)

    if original_text == decrypted_text:
        print("  Verification PASSED — decrypted text matches the original exactly.")
        return True
    
    
    # Useful diagnostics 
    print("  Verification FAILED — decrypted text does NOT match the original.")

    # First character that differs
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

#clean blank-input handling
def get_positive_integer(label):
    while True:
        raw_input = input(f"  Enter {label} (positive integer): ").strip()

        # Handle blank input explicitly
        if raw_input == "":
            print("  [!] Input cannot be blank. Please enter a positive integer.")
            continue

        try:
            value = int(raw_input)
            if value > 0:
                return value
            print(f"  [!] '{raw_input}' is not a positive integer. Please try again.")
        except ValueError:
            print(f"  [!] '{raw_input}' is not a valid integer. Please try again.")

# Main
def main():

    """
    Orchestrate the full encrypt → decrypt → verify pipeline.
 
    Steps:
        1. Resolve all file paths relative to this script's location.
        2. Confirm 'raw_text.txt' exists before proceeding.
        3. Collect shift1 and shift2 from the user (with validation).
        4. Run encryption_function, decryption_function, verification_function
           in sequence.
    """    
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
