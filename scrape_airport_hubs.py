import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_wikipedia_tables():
    # URL of the Wikipedia page
    url = 'https://en.wikipedia.org/wiki/List_of_airports_in_the_United_States'
    
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables in the page
        tables = pd.read_html(response.text)
        
        # Process each table
        for i, table in enumerate(tables):
            # Check if any of the column names exactly match Airport, FAA, or IATA
            if any(col for col in table.columns if col in ['Airport', 'FAA', 'IATA']):
                # Clean the table data (remove reference numbers and brackets)
                #table = table.apply(lambda x: x.str.replace(r'\[\d+\]', '') if x.dtype == "object" else x)
                
                # Generate filename based on content
                filename = f'airports_{i}.csv'
                
                # Save to CSV
                table.to_csv(filename, index=False)
                print(f"Saved table to {filename}")
            
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_wikipedia_tables()
