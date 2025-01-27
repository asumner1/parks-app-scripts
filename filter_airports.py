import pandas as pd
from geopy.distance import geodesic

# Read the CSV files
airports_df = pd.read_csv('airports_1.csv')
iata_icao_df = pd.read_csv('iata-icao.csv')
gpt_suggested_df = pd.read_csv('GPT_Suggested_National_Parks_Airports.csv')

print("After initial load:")
print("HNL in airports_df IATA:", 'HNL' in airports_df['IATA'].values)
print("HNL in iata_icao_df iata:", 'HNL' in iata_icao_df['iata'].values)

# Read national parks data and get coordinates
parks_df = pd.read_csv('national_parks.csv')
park_coordinates = parks_df[['Latitude', 'Longitude']].values

# Get list of suggested airport codes
suggested_codes = gpt_suggested_df['Code'].dropna().unique()

# Filter airports_df to include rows where:
# 1. Role contains L, M, or S OR
# 2. IATA matches a suggested airport code OR
# 3. Airport name contains "International"
airports_filtered = airports_df[
    (airports_df['Role'].str.contains('L|M|S', na=False)) |
    (airports_df['IATA'].isin(suggested_codes)) |
    (airports_df['Airport'].str.contains('International', case=False, na=False))
]



print("\nAfter airports_filtered:")
print("HNL in airports_filtered IATA:", 'HNL' in airports_filtered['IATA'].values)

# Get list of IATA codes from filtered airports
valid_iata_codes = airports_filtered['IATA'].dropna().unique()

# Filter iata_icao_df to only include rows where iata matches valid codes
iata_icao_filtered = iata_icao_df[
    iata_icao_df['iata'].isin(valid_iata_codes)
]

print("\nAfter iata_icao_filtered:")
print("HNL in iata_icao_filtered iata:", 'HNL' in iata_icao_filtered['iata'].values)

# Merge the filtered dataframes
merged_airports = airports_filtered.merge(
    iata_icao_filtered,
    left_on='IATA',
    right_on='iata',
    how='left'
)

print("\nAfter merge:")
print("HNL in merged_airports iata:", 'HNL' in merged_airports['iata'].values)

# For rows where 'Airport' contains 'International' but 'airport' doesn't,
# set 'airport' equal to 'Airport'
international_mask = (
    merged_airports['Airport'].str.contains('International', case=False, na=False) &
    ~merged_airports['airport'].str.contains('International', case=False, na=False)
)
merged_airports.loc[international_mask, 'airport'] = merged_airports.loc[international_mask, 'Airport']

# Drop specified columns and rename 'airport' to 'airport_name'
columns_to_drop = ['Airport', 'ICAO', 'icao', 'FAA', 'iata']
merged_airports = merged_airports.drop(columns=columns_to_drop, errors='ignore')
merged_airports = merged_airports.rename(columns={'airport': 'airport_name'})

# Convert all column names to lowercase
merged_airports.columns = merged_airports.columns.str.lower()

# Cast enplanements to int, replacing any non-numeric values with NaN first
merged_airports['enplanements'] = pd.to_numeric(merged_airports['enplanements'], errors='coerce').astype('Int64')

# Create df of airports not in suggested_codes
non_suggested_airports = merged_airports[~merged_airports['iata'].isin(suggested_codes)].copy()

# Initialize list to store IATA codes of airports to exclude
iatas_to_exclude = []

# For each airport not in suggested_codes
for idx, airport in non_suggested_airports.iterrows():
    airport_point = (airport['latitude'], airport['longitude'])
    
    # Calculate minimum distance to any park
    min_distance = float('inf')
    for park_point in park_coordinates:
        distance = geodesic(airport_point, park_point).miles
        min_distance = min(min_distance, distance)
    
    # If no park is within 500 miles, add to exclusion list
    if min_distance > 500:
        iatas_to_exclude.append(airport['iata'])

# Filter out airports that are too far from any park
merged_airports = merged_airports[~merged_airports['iata'].isin(iatas_to_exclude)]

print("\nAfter distance filtering:")
print("HNL in merged_airports iata:", 'HNL' in merged_airports['iata'].values)

# Create set to store closest airport codes
closest_airports = set()

# For each park, find 3 closest airports
for park_point in park_coordinates:
    # Create list to store (distance, iata) tuples
    distances = []
    
    # Calculate distance to each airport
    for idx, airport in merged_airports.iterrows():
        airport_point = (airport['latitude'], airport['longitude'])
        distance = geodesic(park_point, airport_point).miles
        distances.append((distance, airport['iata']))
    
    # Sort by distance and get 3 closest
    distances.sort()
    closest_three = distances[:4]
    
    # Add IATA codes to set
    for _, iata in closest_three:
        if pd.notna(iata):  # Only add if IATA code is not NaN
            closest_airports.add(iata)

# Keep only airports that are either closest to a park or in suggested_codes
merged_airports = merged_airports[
    merged_airports['iata'].isin(closest_airports) |
    merged_airports['iata'].isin(suggested_codes)
]

print("\nAfter closest airports filtering:")
if 'HNL' in closest_airports:
    print("HNL is in closest_airports set")
print("HNL in final merged_airports iata:", 'HNL' in merged_airports['iata'].values)

# Save merged dataframe to CSV
merged_airports.to_csv('filtered_airports.csv', index=False)
iata_icao_filtered.to_csv('filtered_iata_icao.csv', index=False)
