import requests
from bs4 import BeautifulSoup
import os
import time

# Base Confluence search URL (modify as needed)
BASE_SEARCH_URL = "https://confluence.fkinternal.com/dosearchsite.action?cql=space+%3D+%22TRUS%22+and+type+%3D+%22page%22&startIndex={}"
BASE_PAGE_URL = "https://confluence.fkinternal.com"

# Authentication (Replace with actual credentials or API token)
HEADERS = {
    "Cookie": "JSESSIONID=59BF79A3D90D7900588367E9CDFED374"
}

# Directory to save documents
SAVE_DIR = "confluence_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

# Track visited URLs to avoid duplicates
visited_urls = set()

def fetch_and_save(url):
    """Fetches a Confluence document and saves it as a text file."""
    if url in visited_urls:
        return
    visited_urls.add(url)

    print(f"Fetching document: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Skipping {url} (Status: {response.status_code})")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract page title
        title = soup.find("title").text.strip()
        safe_title = "".join(c if c.isalnum() else "_" for c in title)

        # Extract content (Modify selector based on Confluence structure)
        content_div = soup.find("div", {"id": "main-content"})
        content_text = content_div.get_text("\n", strip=True) if content_div else "No content found"

        # Save content to a text file
        file_path = os.path.join(SAVE_DIR, f"{safe_title}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_text)

        print(f"Saved: {file_path}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

def get_document_links(start_index=10):
    """Fetches document links from Confluence search pagination."""
    while True:
        search_url = BASE_SEARCH_URL.format(start_index)
        print(f"Fetching search page: {search_url}")

        try:
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {search_url} (Status: {response.status_code})")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", class_="search-result-link")

            if not links:
                print("No more documents found. Exiting pagination.")
                break

            for link in links:
                page_url = BASE_PAGE_URL + link["href"]
                fetch_and_save(page_url)

            start_index += 10  # Move to the next page in pagination
            time.sleep(2)  # Avoid overwhelming the server

        except Exception as e:
            print(f"Error processing search page {search_url}: {e}")
            break

# Start fetching documents
get_document_links()
print("Finished fetching all relevant documents.")
