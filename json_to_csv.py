import json
import csv
import sys
import json

def json_to_csv(json_file_path):
    # Read JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{json_file_path}' is not a valid JSON file.")
        sys.exit(1)

    if not data or not isinstance(data, list):
        print("Error: JSON file must contain a list of objects.")
        sys.exit(1)

    # Get field names from the first object
    fieldnames = list(data[0].keys())

    # Create CSV filename from JSON filename
    csv_file_path = json_file_path.rsplit('.', 1)[0] + '.csv'

    # Write to CSV
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                # Convert nested objects/lists to strings
                row = {}
                for key, value in item.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)
        
        print(f"Successfully converted {json_file_path} to {csv_file_path}")

    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_to_csv.py <json_file_path>")
        sys.exit(1)
    
    json_to_csv(sys.argv[1])
