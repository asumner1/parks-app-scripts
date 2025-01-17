import json
import unicodedata
import sys
import re
from collections import OrderedDict

def generate_id(name):
    # Convert to lowercase
    id_string = name.lower()
    
    # Replace special quotes and similar characters with empty string
    id_string = re.sub(r'[''""″\'\"ʻ]', '', id_string)
    
    # Replace all types of dashes/hyphens with underscore
    id_string = re.sub(r'[\-\–\—]', '_', id_string)
    
    # Replace spaces (including non-breaking space \u00a0) with underscores
    id_string = re.sub(r'[\s\u00a0]+', '_', id_string)
    
    # Remove diacritics/accents
    id_string = ''.join(
        c for c in unicodedata.normalize('NFKD', id_string)
        if not unicodedata.combining(c)
    )
    
    # Remove all remaining punctuation and special characters except underscores
    id_string = re.sub(r'[^\w\s]', '', id_string)
    
    return id_string

def add_ids_to_json(input_file, output_file=None):
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is a list
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of objects")
        
        # Process each object
        for i, item in enumerate(data):
            # Check for 'name' or 'Name' field
            name_field = next((field for field in ['name', 'Name'] 
                             if field in item), None)
            
            if name_field is None:
                raise ValueError("Objects must contain a 'name' or 'Name' field")
            
            # Generate id
            new_id = generate_id(item[name_field])
            
            # Create new ordered dictionary with id first
            ordered_item = OrderedDict()
            ordered_item['id'] = new_id
            # Add all other fields
            ordered_item.update(item)
            
            # Replace original item with ordered version
            data[i] = ordered_item
        
        # Determine output file name
        if output_file is None:
            output_file = input_file.rsplit('.', 1)[0] + '_with_ids.json'
        
        # Write the updated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully added IDs and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{input_file}' is not a valid JSON file")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_ids_to_json.py <input_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_ids_to_json(input_file, output_file)
