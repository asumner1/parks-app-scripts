import json
import openai
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('GPT_API_KEY')

def get_new_description(original_description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that rewrites national park descriptions in an engaging and informative way."
                },
                {
                    "role": "user", 
                    "content": f"Please rewrite this national park description in an engaging way while maintaining the key information: {original_description}"
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting new description: {e}")
        return None

def main():
    # Read the JSON file
    with open('national_parks.json', 'r') as file:
        parks_data = json.load(file)
    
    # Create a new list to store updated parks
    updated_parks = []
    
    # Process each park
    for park in parks_data:
        print(f"\nProcessing: {park['Name']}")
        
        # Get new description from ChatGPT
        new_description = get_new_description(park['Description'])
        
        if new_description:
            # Create updated park object
            updated_park = park.copy()
            updated_park['Description'] = new_description
            updated_parks.append(updated_park)
            
            # Print original and new descriptions
            print("\nOriginal Description:")
            print(park['Description'])
            print("\nNew Description:")
            print(new_description)
            
            # Add delay to respect API rate limits
            time.sleep(1)
        else:
            # If API call fails, keep original description
            updated_parks.append(park)
    
    # Save updated data to new file
    with open('updated_national_parks.json', 'w') as file:
        json.dump(updated_parks, file, indent=2)

if __name__ == "__main__":
    main()