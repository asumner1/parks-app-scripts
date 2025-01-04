from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variable
api_key = os.getenv('GPT_API_KEY')
client = OpenAI(api_key=api_key)

# Define the prompt
prompt = """You are a data api that takes descriptive language input, searches the web across multiple sources, and returns the most accurate data formatted in a plain text data table, with no other extraneous information, titles, context, sources, or responses. Units of measurement can be in the column names, but should not be in the data rows themselves. Prefer official, governmental, and/or well-respected sources.

Return a data table of the average monthly high and low temperatures in Fahrenheit for Kobuk Valley National Park."""

# Make the API call
completion = client.chat.completions.create(
    model="chatgpt-4o-latest",
    store=True,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Get the response
table_text = completion.choices[0].message.content
print(table_text)

# Convert the text table to a pandas DataFrame
df = pd.read_csv(StringIO(table_text), sep='|', engine='python')

# Clean up whitespace in column names and values
df.columns = [col.strip() for col in df.columns]
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Save to CSV
df.to_csv('kobuk_valley_temperatures.csv', index=False)

print("Data has been saved to kobuk_valley_temperatures.csv") 