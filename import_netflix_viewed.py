import os
import time
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import mysql.connector as mariadb
import pandas as pd

# Netflix login credentials and profiles
NETFLIX_EMAIL = "your-email@example.com"
NETFLIX_PASSWORD = "your-password"
PROFILES = ["Profile1", "Profile2", "Profile3"]  # Add all profile names here

# MariaDB database connection
try:
    conn = mariadb.connect(
        user="your-db-user",
        password="your-db-password",
        host="localhost",
        database="netflix_viewed"
    )
    cursor = conn.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    exit(1)

# Directory paths
DOWNLOAD_PATH = "/path/to/download/" # eg. /root/netflix-viewed/ - dont forget trailing slash :)
ARCHIVE_PATH = os.path.join(DOWNLOAD_PATH, "archive")
if not os.path.exists(ARCHIVE_PATH):
    os.makedirs(ARCHIVE_PATH)

# Configure browser for headless operation
def configure_browser():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    service = Service('/usr/local/bin/chromedriver')
    return webdriver.Chrome(service=service, options=options)

# Download watch history for a specific profile
def get_watch_history(profile_name):
    driver = configure_browser()
    driver.get("https://www.netflix.com/login")

    # Login
    driver.find_element(By.ID, ":r0:").send_keys(NETFLIX_EMAIL)
    driver.find_element(By.ID, ":r3:").send_keys(NETFLIX_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'button[data-uia="login-submit-button"]').click()
    time.sleep(5)

    # Select profile
    try:
        profile_element = driver.find_element(By.XPATH, f'//span[text()="{profile_name}"]')
        profile_element.click()
        time.sleep(5)
    except NoSuchElementException:
        print(f"Profile '{profile_name}' could not be found.")
        driver.quit()
        return None

    # Navigate to viewing activity
    driver.get("https://www.netflix.com/viewingactivity")
    time.sleep(3)

    # Download CSV
    download_button = driver.find_element(By.LINK_TEXT, "Alle herunterladen")
    download_button.click()
    time.sleep(10)
    driver.quit()

    # Rename downloaded file
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    new_filename = f"{profile_name}_NetflixViewingHistory_{date_suffix}.csv"
    downloaded_file_path = os.path.join(DOWNLOAD_PATH, "NetflixViewingHistory.csv")
    new_file_path = os.path.join(DOWNLOAD_PATH, new_filename)

    if os.path.exists(downloaded_file_path):
        os.rename(downloaded_file_path, new_file_path)
        return new_file_path
    else:
        print("Download failed or timed out.")
        return None

# Import CSV to MariaDB and archive the file
def import_csv_to_mariadb(file_path, profile_name):
    try:
        df = pd.read_csv(file_path)
        print("CSV columns:", df.columns)  # Debugging: check column names

        for _, row in df.iterrows():
            date_watched = datetime.strptime(row['Date'], "%d.%m.%y").date()

            # Insert entry, skip if duplicate
            try:
                cursor.execute(
                    "INSERT INTO netflix_watchlist (title, date_watched, profile_name) VALUES (%s, %s, %s)",
        
