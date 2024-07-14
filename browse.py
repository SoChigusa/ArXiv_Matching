from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse
import os
import random
import string
import time
import json
import requests


# Function to generate a user ID
def generate_user_id():
    return 'user-' + ''.join(random.choices(string.ascii_letters + string.digits, k=9))


# Function to check if a URL is relative
def is_relative(url):
    return not bool(urlparse(url).netloc)


# Path to your ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--window-size=1024,768")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("user-data-dir=/tmp/chrome_user_data")

# Set binary location to existing Chrome application (adjust path if necessary)
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Initialize the Chrome driver
service = ChromeService(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL to fetch the HTML content from
html_url = "https://arxiv.org/list/hep-ph/new"

# Fetch the HTML content from the URL
response = requests.get(html_url)
html_content = response.text

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Convert relative URLs to absolute URLs
arXiv_home = "https://arxiv.org"
for tag in soup.find_all(['a']):
    if tag.has_attr('href') and is_relative(tag['href']):
        tag['href'] = urljoin(html_url, tag['href'])

# Find the specific <h3> tag and remove it along with subsequent content
replacement_h3 = soup.find(
    "h3", string=lambda text: text and text.startswith("Replacement submissions"))
if replacement_h3:
    # Remove the <h3> tag and all following siblings
    for sibling in list(replacement_h3.next_siblings):
        sibling.extract()
    replacement_h3.extract()
else:
    print("Replacement submissions section was not found.")

# Extract all <dt> and <dd> elements
papers = soup.find_all(['dt', 'dd'])


# Function to extract paper information
def extract_paper_info(paper_dt, paper_dd):
    # Extract the title
    title_div = paper_dd.find('div', class_='list-title mathjax')
    title = title_div.get_text(strip=True).replace(
        title_div.span.get_text(strip=True), '')

    # Extract the authors
    authors_div = paper_dd.find('div', class_='list-authors')
    authors = [a.get_text(strip=True) for a in authors_div.find_all('a')]

    # Extract the abstract
    abstract_p = paper_dd.find('p', class_='mathjax')
    abstract = abstract_p.get_text(strip=True)

    return {'title': title, 'authors': authors, 'abstract': abstract}


# Generate list of paper information
extracted_info = []
html_data = []
for i in range(0, len(papers), 2):
    paper_dt = papers[i]
    paper_dd = papers[i + 1]

    # Extract information from the paper
    paper_info = extract_paper_info(paper_dt, paper_dd)
    extracted_info.append(paper_info)

    # Extracting serial number from 'name' attribute
    serial_number = paper_dt.a['name'][4:]
    html_content = f"{str(paper_dt)}{str(paper_dd)}"

    html_data.append(html_content)
    continue  # Continue to the next paper

# Generate a user ID
user_id = generate_user_id()

# Data upload
url = 'http://localhost:3000/api/upload_html'
payload = {'userId': user_id, 'html': html_data}
response = requests.post(url, json=payload)
print(response.json())

# Open the webpage in Chrome
page_url = f'http://localhost:3000?userId={user_id}'
driver.get(page_url)

# Monitor for completion notification
completed = False
while not completed:
    time.sleep(1)  # Adjust the polling interval as needed
    response = requests.get(
        f'http://localhost:3000/api/notify_completion?userId={user_id}')
    data = response.json()
    if data['status'] == 'completed':
        completed = True

# Retrieve and print selections
response = requests.get(
    f'http://localhost:3000/api/save_selections?userId={user_id}')
selections = response.json()['selections']
for e, s in zip(extracted_info, selections):
    if s == 1:
        e["evaluation"] = "like"
    else:
        e["evaluation"] = "dislike"

# Step 5: Close the browser
driver.quit()

# Load existing data from the JSON file
file_path = "data/matching_info_raw.json"
if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as json_file:
        existing_data = json.load(json_file)
else:
    existing_data = []

# Add new data to the existing data
existing_data.extend(extracted_info)

# Save updated data back to the JSON file
with open(file_path, "w", encoding="utf-8") as json_file:
    json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
