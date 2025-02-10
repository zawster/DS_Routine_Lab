import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Base URL 
URL = "https://asia.money2020.com/program/speakers"

# Set up Selenium WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--no-sandbox")

# Set up Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the webpage
driver.get(URL)

# Wait for dynamic content to load, it canm vary if data is huge.
time.sleep(5)

# Get the full page source after JS execution
page_source = driver.page_source

# Close the browser
driver.quit()

# Parse the rendered HTML with BeautifulSoup
soup = BeautifulSoup(page_source, "lxml")

# Find all profile containers
profiles = soup.find_all("div", class_="css-1v4fgt5")
print(f"------------ {len(profiles)}")
extracted_profiles = []
# Prepare CSV column names
csv_columns = ["Name", "Position", "Company", "Geography", "Speaker_Profile_URL"]
for profile in profiles:
    try:
        name = profile.find("p", {"data-testid": "media-profile-name"}).text.strip()
        position = profile.find("p", {"data-testid": "job-title"}).text.strip()
        company = profile.find("p", {"data-testid": "company-name"}).text.strip()
        country = profile.find("p", {"data-testid": "country"}).text.strip()
        profile_url = "https://asia.money2020.com" + profile.find("a", {"data-testid": "link"})["href"]

        extracted_profiles.append({
            "Name": name,
            "Position": position,
            "Company": company,
            "Country": country,
            "Speaker_Profile_URL": profile_url
        })

    except AttributeError:
        continue  # Skip profiles with missing data

# Save data to CSV
csv_filename = "Asia_Money2020_Speakers.csv"
df = pd.DataFrame(extracted_profiles)
df.to_csv(csv_filename, index=False, encoding="utf-8")
# Print extracted data on conmsole
for idx, profile in enumerate(extracted_profiles, 1):
    print(f"Profile {idx}:")
    print(f"  Name: {profile['Name']}")
    print(f"  Position: {profile['Position']}")
    print(f"  Company: {profile['Company']}")
    print(f"  Country: {profile['Country']}")
    print(f" ProfileL {profile['Speaker_Profile_URL']}")
    print("-" * 40)

