import sys
import os
import json
from unidecode import unidecode

def find_and_replace_non_utf8_characters(content):
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
    
    return fixed_content

def read_json_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    return content

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), 'initial_data')
    files = ['groups.json', 'members.json', 'posts.json']
    
    combined_content = bytearray()
    file_contents = {}
    
    # Read and combine content from all files
    for file_name in files:
        file_path = os.path.join(base_dir, file_name)
        content = read_json_file(file_path)
        file_contents[file_name] = content
        combined_content.extend(content)
    
    # Process combined content
    fixed_combined_content = find_and_replace_non_utf8_characters(combined_content)
    
    # Split and save fixed content back to original files
    start = 0
    for file_name in files:
        original_content = file_contents[file_name]
        end = start + len(original_content)
        fixed_content = fixed_combined_content[start:end]
        start = end
        
        output_path = os.path.join(base_dir, file_name)
        with open(output_path, 'wb') as output_file:
            output_file.write(fixed_content)
        print(f"Processed {file_name} and saved fixed content to {output_path}")