import sys
from unidecode import unidecode

def find_and_replace_non_utf8_characters(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    fixed_content = bytearray()
    i = 0
    while i < len(content):
        try:
            # Try to decode the next byte as UTF-8
            content[i:i+1].decode('utf-8')
            fixed_content.append(content[i])
            i += 1
        except UnicodeDecodeError:
            problematic_byte = content[i]
            print(f"Problematic byte at position {i}: {problematic_byte} (character: {chr(problematic_byte)})")
            # Replace the problematic byte with its UTF-8 counterpart using unidecode
            replacement = unidecode(chr(problematic_byte))
            fixed_content.extend(replacement.encode('utf-8'))
            i += 1
    
    # Save the fixed content back to the file
    with open(file_path, 'wb') as f:
        f.write(fixed_content)
    
    print(f"All problematic bytes in {file_path} replaced and file saved.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_encoding.py <file_path>")
    else:
        find_and_replace_non_utf8_characters(sys.argv[1])