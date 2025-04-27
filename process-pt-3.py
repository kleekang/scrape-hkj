import os
import pandas as pd
from bs4 import BeautifulSoup

# Path to your race_html folder
base_folder = 'race_html'

# List to collect data
data = []

# Walk through each date folder
for date_folder in os.listdir(base_folder):
    date_path = os.path.join(base_folder, date_folder)
    if os.path.isdir(date_path):
        # Look for race_*.html files
        for file_name in os.listdir(date_path):
            if file_name.startswith('race_') and file_name.endswith('.html'):
                file_path = os.path.join(date_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    span = soup.find('span', class_='f_fl f_fs13')
                    if span:
                        data.append({
                            'date': date_folder,
                            'file': file_name,
                            'text': span.get_text(strip=True)
                        })

# Create a DataFrame
df = pd.DataFrame(data)

# Split the 'text' field
df['text-date'] = df['text'].str.extract(r'Race Meeting:\s*(\d{2}/\d{2}/\d{4})')
df['track-name'] = df['text'].str.extract(r'\d{2}/\d{2}/\d{4}\s+(.*)')

# Drop the original 'text' column if you don't need it
df = df.drop(columns=['text'])

# Save to CSV if you want
df.to_csv('race_data.csv', index=False)
