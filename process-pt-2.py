import os
import json
from bs4 import BeautifulSoup
import pandas as pd

# Set base directory
base_dir = 'race_html'

# Store all extracted data
all_races_data = []

# Walk through all subdirectories
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.startswith('race_') and file.endswith('.html'):
            file_path = os.path.join(root, file)

            # Extract date and race number from path
            date_folder = os.path.basename(root)
            race_number = os.path.splitext(file)[0].split('_')[1]

            # Read HTML
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            race_div = soup.find('div', class_='race_tab')
            if not race_div:
                continue

            race_data = {
                "date": date_folder,
                "race_number": race_number,
                "header": "",
                "details": [],
                "sectional_times": [],
                "videos": []
            }

            # Header
            header_row = race_div.find('tr', class_='bg_blue color_w font_wb')
            if header_row:
                race_data['header'] = header_row.get_text(strip=True)

            # Table rows
            rows = race_div.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if cells:
                    race_data['details'].append(cells)

            # Sectional times (can refine this if needed)
            for row in rows:
                if 'Sectional Time' in row.get_text():
                    race_data['sectional_times'] = [
                        td.get_text(strip=True) for td in row.find_all('td')
                    ]
                    break

            # Videos
            for a in race_div.find_all('a'):
                href = a.get('href')
                label = a.get_text(strip=True)
                race_data['videos'].append({
                    'label': label,
                    'url': href
                })

            all_races_data.append(race_data)

# Output to JSON
with open('all_race_data.json', 'w', encoding='utf-8') as out_file:
    json.dump(all_races_data, out_file, ensure_ascii=False, indent=2)

print(f"Extracted {len(all_races_data)} race entries.")

# Convert to DataFrame
df = pd.json_normalize(all_races_data)

# Save to CSV
df.to_csv('all_race_data.csv', index=False, encoding='utf-8')

print("Data has been saved to all_race_data.csv")
