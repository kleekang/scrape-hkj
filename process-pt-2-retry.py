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
            }

            # Header
            header_row = race_div.find('tr', class_='bg_blue color_w font_wb')
            if header_row:
                race_data['header'] = header_row.get_text(strip=True)

            # Table rows
            rows = race_div.find_all('tr')
            cleaned_details = {}

            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if not cells or all(cell == "" for cell in cells):
                    continue

                # Match known patterns based on example structure
                if "Griffin Race" in cells[0]:
                    cleaned_details["race_name"] = cells[0]
                    if len(cells) > 2:
                        cleaned_details[cells[1]] = cells[2]
                elif "RACING FOR" in cells[0]:
                    cleaned_details["race_desc"] = cells[0]
                    if len(cells) > 2:
                        cleaned_details[cells[1]] = cells[2]
                elif "HK$" in cells[0]:
                    cleaned_details["prize_money"] = cells[0]
                    if len(cells) > 1:
                        time_values = [c for c in cells[1:] if c.startswith('(')]
                        for idx, val in enumerate(time_values):
                            cleaned_details[f"Time {idx + 1}:"] = val
                elif "Sectional Time" in row.get_text():
                    # Parse sectional time and splits
                    secs = [td.get_text(strip=True) for td in row.find_all('td')]
                    if len(secs) >= 3:
                        try:
                            cleaned_details["Sectional Time 1:"] = float(secs[2])
                        except:
                            pass
                    if len(secs) >= 4:
                        split_2 = secs[3].replace('\xa0', ' ').split()
                        if len(split_2) == 2:
                            try:
                                cleaned_details["Sectional Time 2:"] = float(split_2[0])
                                cleaned_details["Split 2.1:"] = float(split_2[1])
                            except:
                                pass
                    if len(secs) >= 5:
                        split_3 = secs[4].replace('\xa0', ' ').split()
                        if len(split_3) == 2:
                            try:
                                cleaned_details["Sectional Time 3:"] = float(split_3[0])
                                cleaned_details["Split 3.1:"] = float(split_3[1])
                            except:
                                pass

            race_data.update(cleaned_details)

            all_races_data.append(race_data)

# Output to JSON
with open('all_race_data_cleaned.json', 'w', encoding='utf-8') as out_file:
    json.dump(all_races_data, out_file, ensure_ascii=False, indent=2)

print(f"Extracted and cleaned {len(all_races_data)} race entries.")

# Convert to DataFrame
df = pd.json_normalize(all_races_data)

# Save to CSV
df.to_csv('all_race_data_cleaned.csv', index=False, encoding='utf-8')

print("Cleaned data has been saved to all_race_data_cleaned.csv")
