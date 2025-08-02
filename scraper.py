import requests
from bs4 import BeautifulSoup
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the target URL for Palm Jumeirah listings on Property Finder
# This URL is for sales, sorted by newest listings first.
TARGET_URL = "https://www.propertyfinder.ae/en/search?c=2&l=50&ob=nd&ot=d"

# Define headers to mimic a browser visit, which can help avoid being blocked.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
}

def scrape_property_finder():
    """
    Scrapes property listings for Palm Jumeirah from Property Finder.
    """
    logging.info(f"Starting scrape for Property Finder URL: {TARGET_URL}")
    
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(TARGET_URL, headers=HEADERS)
        
        # Raise an exception if the request was unsuccessful (e.g., 404, 500)
        response.raise_for_status()
        
        logging.info("Successfully fetched the webpage.")
        
        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- Placeholder for parsing logic ---
        # Here we will add the code to find and extract data for each property listing.
        # This will involve inspecting the HTML structure of propertyfinder.ae
        # to find the correct tags and classes for details like price, title, bedrooms, etc.
        
        scraped_properties = []
        
        # Find the script tag with id="__NEXT_DATA__" which contains the page's data as JSON
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if not script_tag:
            logging.error("Could not find the __NEXT_DATA__ script tag. The page structure may have changed.")
            return None

        # Extract the JSON content from the script tag
        json_data = json.loads(script_tag.string)
        
        # Navigate through the JSON structure to find the list of properties
        # The exact path might change if the website updates, but as of now, it is:
        # props -> pageProps -> searchResult -> properties
        properties_list = json_data.get('props', {}).get('pageProps', {}).get('searchResult', {}).get('properties', [])
        
        if not properties_list:
            logging.warning("No properties found in the JSON data.")
            return []

        for prop in properties_list:
            scraped_properties.append({
                "title": prop.get('title'),
                "location": prop.get('location'),
                "price": prop.get('price'),
                "bedrooms": prop.get('bedrooms'),
                "bathrooms": prop.get('bathrooms'),
                "size_sqft": prop.get('size'),
                "property_type": prop.get('propertyType'),
                "url": "https://www.propertyfinder.ae" + prop.get('url') if prop.get('url') else None,
                "scraped_date": datetime.now().isoformat()
            })

        logging.info(f"Successfully parsed {len(scraped_properties)} properties.")
        
        # Save the scraped data to a file in the knowledge directory
        output_path = os.path.join('knowledge', 'scraped_property_listings.json')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(scraped_properties, f, indent=4)
            logging.info(f"Scraped data successfully saved to {output_path}")
        except IOError as e:
            logging.error(f"Failed to save scraped data to {output_path}: {e}")

        return scraped_properties

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the HTTP request: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}")
        return None

if __name__ == "__main__":
    logging.info("Running the scraper directly.")
    properties = scrape_property_finder()
    if properties is not None:
        logging.info(f"Scraping complete. Found {len(properties)} properties.")
        # In a direct run, we might just print the results
        # print(json.dumps(properties, indent=2))
