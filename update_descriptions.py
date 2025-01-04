import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
import argparse
import tiktoken

def get_new_description(client, park_name, original_description):
    try:
        completion = client.chat.completions.create(
            model="chatgpt-4o-latest",
            store=True,
            messages=[
                {
                    "role": "user", 
                    "content": f"""
                        Please rewrite this national park description for {park_name} 
                        in an engaging and informative way while maintaining the key information. 
                        You can add any information that would be useful or interesting to an outdoors 
                        enthusiast. Focus on detail rather than dramatic or exaggerated diction. 
                        Do not include a title, just the description. Make sure to output in 
                        a plain text format that can be directly pasted inside of an html div.
                        Do not include any html tags or formatting in the output.
                        Here is the original description: 
                        {original_description}
                    """
                }
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting new description: {e}")
        return None

def split_into_parts(descriptions, num_parts):
    # Calculate the size of each part
    part_size = len(descriptions) // num_parts
    # Create the parts
    parts = []
    for i in range(num_parts):
        start = i * part_size
        # For the last part, include any remaining items
        end = start + part_size if i < num_parts - 1 else len(descriptions)
        parts.append(descriptions[start:end])
    return parts

def optimize_descriptions(client, descriptions, num_parts=10):
    try:
        # Split descriptions into parts
        description_parts = split_into_parts(descriptions, num_parts)
        all_output_descriptions = []

        for idx, part in enumerate(description_parts):
            joined_descriptions = "UNIQUE_SEPARATOR".join(part)
            prompt = f"""
                I have multiple national park descriptions separated by 'UNIQUE_SEPARATOR'.
                Please review all descriptions and make very minor changes in wording to reduce repetitive language 
                across sections while maintaining the unique character and key information of each park.
                Keep the 'UNIQUE_SEPARATOR' separators in exactly the same places.
                Do not include any other text in the output, just the descriptions and separators.
                Do not remove any useful information from the descriptions. Make sure to keep the same number of descriptions.
                Here are the descriptions:

                {joined_descriptions}
            """

            # Load the tokenizer for your model
            tokenizer = tiktoken.encoding_for_model("gpt-4o")

            # Count tokens
            token_count = len(tokenizer.encode(prompt))
            print(f"Input token count for part {idx + 1}: {token_count}")

            # use mini for higher token limit in this case
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_completion_tokens=16384
            )

            # Count tokens
            token_count = len(tokenizer.encode(completion.choices[0].message.content.strip()))
            print(f"Output token count for part {idx + 1}: {token_count}")

            # Split and clean up each description
            split_descriptions = completion.choices[0].message.content.strip().split("UNIQUE_SEPARATOR")
            cleaned_descriptions = [
                desc.strip().strip('\n').strip()
                for desc in split_descriptions
            ]
            all_output_descriptions.extend(cleaned_descriptions)
        return all_output_descriptions
    except Exception as e:
        print(f"Error optimizing descriptions: {e}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Update national park descriptions')
    parser.add_argument('--optimize-only', action='store_true', 
                       help='Only perform optimization on existing updated descriptions')
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()

    # Set up OpenAI API key from environment variable
    api_key = os.getenv('GPT_API_KEY')
    client = OpenAI(api_key=api_key)

    if args.optimize_only:
        print("\nRunning optimization-only mode...")
        # Read the previously updated JSON file
        with open('updated_national_parks.json', 'r') as file:
            parks_data = json.load(file)
        
        # Extract existing descriptions
        descriptions = [park['Description'] for park in parks_data]
        
        # Optimize descriptions
        print("Optimizing all descriptions...")
        optimized_descriptions = optimize_descriptions(client, descriptions)
        
        if optimized_descriptions:
            # Update parks with optimized descriptions
            updated_parks = []
            for park, optimized_description in zip(parks_data, optimized_descriptions):
                updated_park = park.copy()
                updated_park['Description'] = optimized_description
                updated_parks.append(updated_park)
            
            # Save back to the same file
            with open('updated_optimized_national_parks.json', 'w') as file:
                json.dump(updated_parks, file, indent=2)
            print("Optimization complete. File has been updated.")
        else:
            print("Error during optimization. No changes made.")
        return

    # Original mode - full update process
    with open('national_parks.json', 'r') as file:
        parks_data = json.load(file)
    
    # Create a new list to store updated parks
    updated_parks = []
    new_descriptions = []
    
    # First pass: Get new descriptions for each park
    for park in parks_data:
        print(f"\nProcessing: {park['Name']}")
        
        # Get new description from ChatGPT
        new_description = get_new_description(client, park['Name'], park['Description'])
        
        if new_description:
            new_descriptions.append(new_description)
            # Print original and new descriptions
            print("\nOriginal Description:")
            print(park['Description'])
            print("\nNew Description:")
            print(new_description)
            
            # Add delay to respect API rate limits
            time.sleep(1)
        else:
            new_descriptions.append(park['Description'])
    
    # Save the initial updated descriptions before optimization
    initial_updated_parks = []
    for park, new_description in zip(parks_data, new_descriptions):
        updated_park = park.copy()
        updated_park['Description'] = new_description
        initial_updated_parks.append(updated_park)
    
    with open('updated_national_parks.json', 'w') as file:
        json.dump(initial_updated_parks, file, indent=2)
    print("\nSaved initial updates to updated_national_parks.json")
    
    # Second pass: Optimize all descriptions together
    print("\nOptimizing all descriptions...")
    optimized_descriptions = optimize_descriptions(client, new_descriptions)
    
    # Create final updated parks data
    for park, optimized_description in zip(parks_data, optimized_descriptions):
        updated_park = park.copy()
        updated_park['Description'] = optimized_description
        updated_parks.append(updated_park)
    
    # Save optimized data to new file
    with open('updated_optimized_national_parks.json', 'w') as file:
        json.dump(updated_parks, file, indent=2)
    print("Saved optimized version to updated_optimized_national_parks.json")

if __name__ == "__main__":
    main()