
# Netflix Watch History Sync

**Netflix Watch History Sync** is an automated script designed to download and archive Netflix viewing history for multiple profiles and import the data into a MariaDB database daily. It runs in a headless Linux environment using Selenium for browser automation and is optimized for use in cron jobs. Error handling, duplicate checking, and file archiving make it reliable for long-term use.

## Features

-   **Automated Netflix Login**: Logs in and downloads watch history without manual interaction.
-   **Multiple Profiles**: Supports handling multiple Netflix profiles in one run.
-   **MariaDB Integration**: Imports viewing history into a MariaDB database with duplicate checking.
-   **File Archiving**: Moves processed CSV files to an archive folder.
-   **Headless Execution**: Runs on a Linux server without a GUI.
-   **Cron Job Friendly**: Suitable for scheduled daily runs to keep the database up-to-date.

## Table of Contents

-   [Requirements](#requirements)
-   [Installation](#installation)
-   [Configuration](#configuration)
-   [Usage](#usage)
-   [Setting up a Cron Job](#setting-up-a-cron-job)
-   [Troubleshooting](#troubleshooting)
-   [License](#license)

## Requirements

-   **Python** 3.8+
-   **Chromium** and **ChromiumDriver** for headless browsing
-   **MariaDB** server
-   **Python Packages**: Selenium, pandas, mysql-connector-python
-   **Linux Server** (tested on Ubuntu/Debian)

## Installation

1.  **Clone the Repository**:
    
    bash
    
    ```
    git clone https://github.com/IVRYSimon/netflix-watch-history-sync.git
    cd netflix-watch-history-sync
    ``` 
    
2.  **Install Required Packages**: Install Python dependencies:
    
    bash
    ```
    pip install -r requirements.txt
    ```
3.  **Install Chromium and ChromiumDriver**:
    
    bash
    
    ```
    sudo apt update
    sudo apt install -y chromium-browser chromium-chromedriver` 
    ```
    
5.  **Set Up MariaDB Database**:
    
    sql
    ```
    CREATE DATABASE netflix_viewed;
    CREATE TABLE netflix_watchlist (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        date_watched DATE,
        profile_name VARCHAR(100),
        UNIQUE(title, date_watched, profile_name)
    );
    ```
    With the UNIQUE function, we assure that entries are unique identified by title, date_watched and profile_name

## Configuration

Edit the script to update the Netflix credentials, profile names, and database configuration:

-   **Netflix Account Details**:
    
    python
    
    ```
    NETFLIX_EMAIL = "your-email@example.com"
    NETFLIX_PASSWORD = "your-password"
    PROFILES = ["Profile1", "Profile2", "Profile3"]` 
    ```
    
-   **MariaDB Configuration**:
    
    python
    ```
    conn = mariadb.connect(
        user="your-db-user",
        password="your-db-password",
        host="localhost",
        database="netflix_viewed"
    )
    ```
    
-   **Download Path**: Set the directory for temporary CSV files and archived files.
    
    python
    
    ```
    DOWNLOAD_PATH = "/path/to/download"
    ```
    

## Usage

Run the script manually to test the setup:

bash

```
python3 import_netflix_viewed.py
```

## Setting up a Cron Job

To automate daily data syncing, set up a cron job. Open the crontab editor:

bash
```
crontab -e
```
Add a line for daily execution at 2:00 AM:

cron
```
0 2 * * * /usr/bin/python3 /path/to/netflix-watch-history-sync/import_netflix_viewed.py >> /path/to/log/netflix_sync.log 2>&1` 
```
## Troubleshooting

### Common Issues and Fixes

#### Issue: "Profile 'ProfileName' could not be found."

-   **Cause**: The profile name in the script doesn’t match the actual profile on Netflix.
-   **Solution**: Double-check the profile names in the script to ensure they match the exact names on Netflix.

#### Issue: "session not created: Chrome not reachable"

-   **Cause**: Chromium or Chromedriver versions may be incompatible.
-   **Solution**:
    -   Ensure both Chromium and Chromedriver are installed with compatible versions.
    -   Check versions:
        
        bash
        
        
        ```
        chromium --version
        chromedriver --version` 
        ```

#### Issue: "DevToolsActivePort file doesn't exist"

-   **Cause**: Chrome sometimes fails to start in headless mode.
-   **Solution**:
    -   Add `--no-sandbox` and `--disable-dev-shm-usage` to Chrome options.
    -   Ensure `/tmp` directory has sufficient space:
        
        bash
        ```
        df -h /tmp
        ``` 
        

#### Issue: "No such file or directory: NetflixViewingHistory.csv"

-   **Cause**: The CSV file may not have downloaded.
-   **Solution**:
    -   Ensure the "Viewing Activity" page is loading correctly in Selenium.
    -   Increase `time.sleep()` delays if needed to allow time for page loads.

#### Issue: "IntegrityError: Duplicate entry"

-   **Cause**: Attempted to insert an existing entry.
-   **Solution**: The script already includes duplicate checking, so this message can safely be ignored. To suppress the error, ensure you’re handling `IntegrityError` in the import function.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
