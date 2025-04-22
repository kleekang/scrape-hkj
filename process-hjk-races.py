import os
import pandas as pd
from bs4 import BeautifulSoup
import glob
import re

def extract_data_from_html_files():
    # Initialize empty lists to store data for each DataFrame
    performance_data = []
    dividend_data = []
    incident_data = []
    
    # Walk through the directory structure
    base_dir = 'race_html'
    
    # Find all date directories
    date_dirs = glob.glob(os.path.join(base_dir, '*-*-*'))
    
    for date_dir in date_dirs:
        date = os.path.basename(date_dir)  # Get date from directory name
        
        # Find all race HTML files in this directory
        race_files = glob.glob(os.path.join(date_dir, 'race_*.html'))
        
        for race_file in race_files:
            # Extract race number from filename
            race_num = re.search(r'race_(\d+)\.html', race_file).group(1)
            
            print(f"Processing {date}, Race {race_num}")
            
            try:
                with open(race_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 1. Extract data from "performance" div
                performance_div = soup.find('div', class_='performance')
                if performance_div:
                    # Extract table data
                    perf_data = extract_table_data(performance_div, 'performance')
                    for row in perf_data:
                        row['date'] = date
                        row['race_num'] = race_num
                        performance_data.append(row)
                
                # 2. Extract data from "dividend_tab f_clear" div
                dividend_div = soup.find('div', class_='dividend_tab f_clear')
                if dividend_div:
                    div_data = extract_table_data(dividend_div, 'dividend')
                    for row in div_data:
                        row['date'] = date
                        row['race_num'] = race_num
                        dividend_data.append(row)
                
                # 3. Extract data from "race_incident_report performance" div
                incident_div = soup.find('div', class_='race_incident_report performance')
                if incident_div:
                    # For incident reports, we might want to extract text differently
                    inc_data = extract_incident_data(incident_div)
                    inc_data['date'] = date
                    inc_data['race_num'] = race_num
                    incident_data.append(inc_data)
                    
            except Exception as e:
                print(f"Error processing {race_file}: {e}")
    
    # Convert lists to DataFrames
    performance_df = pd.DataFrame(performance_data) if performance_data else pd.DataFrame()
    dividend_df = pd.DataFrame(dividend_data) if dividend_data else pd.DataFrame()
    incident_df = pd.DataFrame(incident_data) if incident_data else pd.DataFrame()
    
    return performance_df, dividend_df, incident_df

def extract_table_data(div, data_type):
    """Extract data from tables within the div"""
    results = []
    
    # Find all tables in the div
    tables = div.find_all('table')
    
    for table in tables:
        # Get headers
        headers = []
        header_row = table.find('tr', class_='bg_blue color_w')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # If no headers found, try other common header patterns
        if not headers:
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Process data rows
        data_rows = table.find_all('tr')
        if header_row:  # Skip header row if found
            data_rows = data_rows[1:]
        
        for row in data_rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = {}
                
                # If we have headers, use them as keys
                if headers and len(headers) == len(cells):
                    for i, cell in enumerate(cells):
                        row_data[headers[i]] = cell.get_text(strip=True)
                else:
                    # Otherwise use generic column names
                    for i, cell in enumerate(cells):
                        row_data[f'col_{i+1}'] = cell.get_text(strip=True)
                
                # Add table identifier if multiple tables exist
                row_data['table_index'] = tables.index(table)
                results.append(row_data)
    
    return results

def extract_incident_data(div):
    """Extract incident report text"""
    # For incident reports, we might just want the text content
    text = div.get_text(strip=True, separator=' ')
    return {'incident_report': text}

def main():
    print("Starting data extraction...")
    performance_df, dividend_df, incident_df = extract_data_from_html_files()
    
    # Save DataFrames to CSV files
    performance_df.to_csv('performance_data.csv', index=False)
    dividend_df.to_csv('dividend_data.csv', index=False)
    incident_df.to_csv('incident_data.csv', index=False)
    
    print(f"Extraction complete. Created DataFrames with:")
    print(f"- Performance data: {len(performance_df)} rows")
    print(f"- Dividend data: {len(dividend_df)} rows")
    print(f"- Incident data: {len(incident_df)} rows")
    
    print("Data saved to CSV files.")

if __name__ == "__main__":
    main()
