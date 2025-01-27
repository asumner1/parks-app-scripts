import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_wikipedia_tables():
    # URLs of the Wikipedia pages
    urls = [
        'https://en.wikipedia.org/wiki/List_of_airports_in_the_United_States',
        'https://en.wikipedia.org/wiki/List_of_airports_in_American_Samoa'
    ]
    
    all_tables = []
    first_table_columns = None
    
    for url in urls:
        try:
            # Send GET request to the URL
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables in the page
            tables = pd.read_html(response.text)
            
            # Process each table
            for i, table in enumerate(tables):
                # Check if any of the column names exactly match Airport, FAA, or IATA
                if any(col for col in table.columns if col in ['Airport', 'FAA', 'IATA']):
                    if first_table_columns is None:
                        # Store column names from first valid table (US airports)
                        first_table_columns = table.columns
                        all_tables.append(table)
                    else:
                        # Rename columns to match first table
                        table.columns = first_table_columns[:len(table.columns)]
                        all_tables.append(table)
    
        except requests.RequestException as e:
            print(f"Error fetching the webpage {url}: {e}")
        except Exception as e:
            print(f"An error occurred with {url}: {e}")
    
    if all_tables:
        # Concatenate all tables
        combined_table = pd.concat(all_tables, ignore_index=True)
        
        # Save to CSV
        combined_table.to_csv('airports_1.csv', index=False)
        print(f"Saved combined table to airports_1.csv")

if __name__ == "__main__":
    scrape_wikipedia_tables()
