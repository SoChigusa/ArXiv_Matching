import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import random
import string


def generate_user_id():
    return 'user-' + ''.join(random.choices(string.ascii_letters + string.digits, k=9))

# Step 1: Send HTML data to Next.js API


# Generate a user ID
user_id = generate_user_id()

# Replace with your Next.js server URL
url = 'http://localhost:3000/api/upload_html'
html_data = [
    '<h2>Content 1</h2><p>This is the first piece of content.</p>',
    '<h2>Content 2</h2><p>This is the second piece of content.</p>',
    '<h2>Content 3</h2><p>This is the third piece of content.</p>'
]
payload = {'userId': user_id, 'html': html_data}
response = requests.post(url, json=payload)
print(response.json())

# Step 2: Set up Selenium and Chrome driver

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

# Step 3: Open the Next.js page in Chrome
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
print(f'Selections for {user_id}: {selections}')

# Step 5: Close the browser
driver.quit()
