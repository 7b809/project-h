import json
import time
import zlib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from pymongo import MongoClient
from manga_extractor import extract_manga_data
import os
chrome_driver_path = r"chromedriver"

chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')

chrome_service = ChromeService(executable_path=chrome_driver_path)

def insert_data_as_binary(json_data, chunk_size=8000):
    # MongoDB connection settings
    mongo_url = os.getenv("MONGO_URL")

    client = MongoClient(mongo_url)

    db = client['project-h']  
    collection = db['api-data']  
    temp_collection = db['api-data-temp'] 
    
    if collection.count_documents({}) > 0:
            # Copy all data from 'api-data' to 'api-data-temp'
            all_documents = collection.find()
            temp_collection.insert_many(all_documents)
            print(f"Copied {temp_collection.count_documents({})} documents to 'api-data-temp'.")

            # Remove all data from the original collection
            collection.delete_many({})
            print("Cleared all data from 'api-data'.")

        
    # Process the data in chunks
    total_snippets = len(json_data)
    for i in range(0, total_snippets, chunk_size):
        chunk = json_data[i:i + chunk_size]

        # Convert the chunk to binary data (compressed)
        binary_data = zlib.compress(json.dumps(chunk).encode('utf-8'))

        # Insert the binary data into MongoDB
        collection.insert_one({"data": binary_data})

        # Print the inserted document size
        print(f"Inserted chunk {i // chunk_size + 1} with {len(chunk)} records into MongoDB.")
        print(f"Inserted document size: {len(binary_data) / (1024 * 1024):.2f} MB")

    client.close()

def get_total_pages(url, browser):
    browser.get(url)
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    last_page_link = soup.find('a', class_="last")
    total_pages = last_page_link.get("href").strip("/").split("/")[-1] if last_page_link else 1000  # Default to 1 if not found

    # Set this to your logic for calculating total pages
    return int(total_pages)

def extract_manga_data_from_page(url, browser):
    browser.get(url)
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    manga_items = soup.find_all('div', class_="manga-item loop-item group/manga-item")
    data = []
    for idx, item in enumerate(manga_items, 1):
        inner_html = item.decode_contents()
        data.append({"serial_no": idx, "html_data": inner_html})
    return data

def main():
    url = "https://hentairead.com/hentai/"
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    total_pages = get_total_pages(url, browser)
    print(f"Total pages: {total_pages}")

    all_data = []
    for page in range(1, total_pages + 1):
        if page%100 == 0:
            print("resting for 10 sec")
            time.sleep(10)
        print(f"Extracting data from page {page}...")
        page_url = f"https://hentairead.com/hentai/page/{page}"
        page_data = extract_manga_data_from_page(page_url, browser)
        all_data.extend(page_data)

    json_data = []
    for entry in all_data:
        if isinstance(entry, dict) and 'html_data' in entry:
            html_content = entry['html_data']
            if html_content:
                temp = extract_manga_data(html_content)
                extracted_data = {
                    'serial_no': entry['serial_no'],
                    'data': json.loads(temp)
                }
                json_data.append(extracted_data)

    # Insert data into MongoDB
    if json_data:
        insert_data_as_binary(json_data)

        print(f"Inserted {len(json_data)} records into MongoDB.")
    else:
        print("No data to insert into MongoDB.")

    browser.quit()

if __name__ == "__main__":
    main()
