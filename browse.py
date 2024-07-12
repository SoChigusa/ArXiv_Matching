from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse, quote
import json
import requests
import time


# Function to check if a URL is relative
def is_relative(url):
    return not bool(urlparse(url).netloc)


# Function to display HTML content in Chrome
def display_html_in_browser(html_content, driver):
    driver.get("data:text/html;charset=utf-8," + html_content)


# Function to wait for user interaction
def wait_for_response():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.server.response = self.path[1:]

    server = HTTPServer(('localhost', 8000), RequestHandler)
    server.handle_request()
    return server.response


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

# Disable dock icon creation (for macOS)
# chrome_options.add_argument("--no-startup-window")

# Optionally use headless mode
# chrome_options.add_argument("--headless")

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

# Load the HTML and CSS template from the external file
with open("components/template.html", "r", encoding="utf-8") as template_file:
    html_template = template_file.read()
with open("components/styles.css", "r", encoding="utf-8") as template_file:
    styles_css = template_file.read()


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


# List to store extracted information
extracted_info = []

# Generate individual files for each paper and display in Chrome
for i in range(0, len(papers), 2):
    paper_dt = papers[i]
    paper_dd = papers[i + 1]

    # Extract information from the paper
    paper_info = extract_paper_info(paper_dt, paper_dd)

    # Extracting serial number from 'name' attribute
    serial_number = paper_dt.a['name'][4:]
    html_content = f"<html><body>{str(paper_dt)}{str(paper_dd)}</body></html>"
    full_html_content = quote(html_template.format(
        styles=styles_css, content=html_content))

    # Display the HTML content in Chrome by refreshing the existing tab
    display_html_in_browser(full_html_content, driver)

    # Wait for user response before proceeding
    paper_info["evaluation"] = wait_for_response()
    extracted_info.append(paper_info)
    continue  # Continue to the next paper

# Close the driver
driver.quit()

# Save extracted information to a JSON file
with open("data/matching_info_raw.json", "w", encoding="utf-8") as json_file:
    json.dump(extracted_info, json_file, ensure_ascii=False, indent=4)
