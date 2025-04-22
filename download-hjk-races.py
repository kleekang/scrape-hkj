import requests
import csv
import os
from datetime import datetime
import time

def download_race_html(date_str, race_numbers=range(1, 11)):
    """
    Download HTML content for racing pages for a specific date and race numbers
    
    Args:
        date_str (str): Date in DD/MM/YYYY format
        race_numbers (iterable): Race numbers to download (default: 1-10)
    """
    # Convert date from DD/MM/YYYY to YYYY/MM/DD format for URL
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    url_date = date_obj.strftime('%Y/%m/%d')
    
    # Create directory for saving files if it doesn't exist
    save_dir = os.path.join('race_html', date_obj.strftime('%Y-%m-%d'))
    os.makedirs(save_dir, exist_ok=True)
    
    for race_num in race_numbers:
        # Construct the URL
        url = f"https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate={url_date}&RaceNo={race_num}"
        
        # Construct filename for saving
        filename = os.path.join(save_dir, f"race_{race_num}.html")
        
        try:
            # Download the content
            print(f"Downloading {url}")
            response = requests.get(url)
            
            # Check if request was successful
            if response.status_code == 200:
                # Save the HTML content
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Successfully saved to {filename}")
            else:
                print(f"Failed to download: HTTP status code {response.status_code}")
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error downloading {url}: {e}")

def main():
    # Path to your CSV file with dates
    csv_file = 'example-dates.csv'  # Update this to your actual CSV path
    
    try:
        with open(csv_file, 'r') as f:
            csv_reader = csv.reader(f)
            
            # Assuming the date is in the first column
            # Skip header if your CSV has one
            next(csv_reader)  # Skip the header row if your CSV has one
            
            for row in csv_reader:
                if row:  # Check if row is not empty
                    date_str = row[0].strip()  # Get date from first column
                    print(f"\nProcessing date: {date_str}")
                    try:
                        # Validate date format
                        datetime.strptime(date_str, '%d/%m/%Y')
                        download_race_html(date_str)
                    except ValueError:
                        print(f"Invalid date format in row: {row}")
    
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    main()
