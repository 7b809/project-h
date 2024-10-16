import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Set the path to chromedriver.exe
chrome_driver_path = r"chromedriver"

# Set up Chrome options
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

# Set up Chrome service
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# URL of the webpage containing the items
url = "https://hentairead.com/hentai/"  # Change this URL to your target

# Load the webpage
browser.get(url)

# Wait for the page to load
# time.sleep(2)

# Get the HTML content of the page
html_content = browser.page_source

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')


total_page = soup.find('a', class_="last").get("href").strip("/").split("/")[-1]
# Find all divs with the class "manga-item loop-item group/manga-item"
manga_items = soup.find_all('div', class_="manga-item loop-item group/manga-item")

# Prepare data for JSON
data = []

# Loop through each div and save its inner HTML
for idx, item in enumerate(manga_items, 1):
    inner_html = item.decode_contents()  # Get the inner HTML of the div
    data.append({"serial_no": idx, "html_data": inner_html})  # Append to the data list

print(data[0:10])
# Close the browser
browser.quit()

print(f"Saved {len(manga_items)} items to d.json.")
