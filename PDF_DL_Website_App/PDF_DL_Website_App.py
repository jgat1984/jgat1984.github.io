import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==========================================================
# Function: download_pdf
# Purpose: Downloads a PDF file from a given URL with retries.
# ==========================================================
def download_pdf(pdf_url: str, save_path: str, retries: int = 3) -> None:
    """
    Downloads a PDF file from the specified URL and saves it locally.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        save_path (str): Local file path where the PDF will be saved.
        retries (int): Number of retry attempts in case of errors.

    Returns:
        None
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }

    try:
        for attempt in range(retries):
            response = requests.get(pdf_url, headers=headers, stream=True)

            if response.status_code == 200:
                with open(save_path, 'wb') as pdf_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            pdf_file.write(chunk)
                print(f"✅ PDF downloaded successfully: {save_path}")
                return
            elif response.status_code == 403:
                print(f"⚠️ 403 Forbidden for {pdf_url}. Attempt {attempt + 1}/{retries}. Retrying...")
                time.sleep(2)
            else:
                print(f"❌ Failed to download PDF. Status code: {response.status_code}")
                break
    except Exception as e:
        print(f"🚨 Error occurred while downloading: {e}")


# ==========================================================
# Function: scrape_pdf_links
# Purpose: Scrapes all valid PDF links from a given webpage using Selenium.
# ==========================================================
def scrape_pdf_links(url_to_scrape: str) -> list:
    """
    Uses Selenium WebDriver to scrape all external PDF links from a webpage.

    Args:
        url_to_scrape (str): The target URL to scrape.

    Returns:
        list: A list of PDF URLs found on the page.
    """
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')  # Headless mode to run without UI

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url_to_scrape)

        # Wait for <a> tags to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )

        # Extract links
        pdf_links = []
        for link in driver.find_elements(By.TAG_NAME, 'a'):
            href = link.get_attribute('href')
            if href:
                print(f"🔗 Found href: {href}")  # Debugging
                if '.pdf' in href.lower() and 'consumereports.org' not in href:
                    print(f"✅ Valid PDF link: {href}")
                    pdf_links.append(href)

        print("\n📄 Found PDF links:")
        for pdf in pdf_links:
            print(pdf)

        return pdf_links
    finally:
        driver.quit()


# ==========================================================
# Main Script
# ==========================================================
def main():
    """
    Main entry point. 
    Prompts the user for a URL, scrapes PDF links, and downloads them.
    """
    url_to_scrape = input("Enter the URL to scrape PDF links from: ")

    # Get PDF links
    pdf_links = scrape_pdf_links(url_to_scrape)

    # Download PDFs
    if pdf_links:
        save_dir = r"C:\Users\Cruci\source\repos\PDF_DL_Website_App"
        for pdf_url in pdf_links:
            pdf_name = os.path.join(save_dir, pdf_url.split('/')[-1])
            download_pdf(pdf_url, pdf_name)
    else:
        print("⚠️ No PDF links found on the page.")


# ==========================================================
# Script Entry Point
# ==========================================================
if __name__ == "__main__":
    main()
