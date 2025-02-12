#!/usr/bin/env python3
"""
This script extracts content from Canada government pages and saves them to a CSV file.
For each page it:
  - Creates a Page object containing the page's metadata and content
  - Extracts the navigation hierarchy from the header
  - Extracts the main content text
  - Saves the page data to a CSV if it doesn't already exist
"""

import csv
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

from utils.page_utils import Page, extract_main_content

MAX_BATCH_SIZE = 10
BASE_URL = "https://www.canada.ca"

PROCESSED_LINKS = set()
BLACKLIST_ROOT_URLS = set()

def extract_hierarchy(soup) -> Tuple[List[str], List[str]]:
    hierarchy = []
    url_hierarchy = []
    breadcrumb = soup.find('ol', class_='breadcrumb')
    if breadcrumb:
        for item in breadcrumb.find_all('li'):
            text = item.get_text(strip=True)
            link = item.find('a')
            if text:
                hierarchy.append(text)
            if link and link.get('href'):
                url_hierarchy.append(link.get('href'))
    return hierarchy, url_hierarchy

# Extract the title from the page
def extract_title(soup) -> str:
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    return ""

# Save the page to CSV
def save_to_csv(pages: List[Page]):
    os.makedirs("outputs", exist_ok=True)
    csv_path = f"outputs/pages.csv" # include timestamp in the filename
    
    # Append the new row
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'hyperlink', 'hierarchy', 'url_hierarchy', 'linked_pages', 'text'])
        for page in pages:
            writer.writerow([page.id, page.title, page.url, page.hierarchy, page.url_hierarchy, page.linked_pages, page.text])

    print(f"Saved {len(pages)} pages to {csv_path}")

# Extract links from table of contents (Steps)
def extract_toc_links(soup) -> List[str]:
    toc = soup.find('ul', class_='toc')
    if not toc:
        return []
    
    links = []
    for link in toc.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/'):
            links.append(f"{BASE_URL}{href}")
    return links

def process_page(url: str, current_depth: int, skip_toc: bool = False):
    current_processed_pages = []
    print(f"Processing {url} at depth {current_depth}")
    
    try:     
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for table of contents if not skipping
        if not skip_toc:
            toc_links = extract_toc_links(soup)
            if toc_links:
                print(f"Found table of contents in {url}, processing sub-pages...")
                for full_url in toc_links:
                    if full_url not in PROCESSED_LINKS:
                        PROCESSED_LINKS.add(full_url) # Mark as processed
                        processed_pages = process_page(full_url, current_depth, skip_toc=True)
                        current_processed_pages.extend(processed_pages)
                return current_processed_pages
        
        # Extract page components
        title = extract_title(soup)
        hierarchy, url_hierarchy = extract_hierarchy(soup)
        text, linked_pages = extract_main_content(soup)

        page = Page(title, url, hierarchy, url_hierarchy, linked_pages, text)
        current_processed_pages.append(page)
        
        # Process linked pages if depth allows
        if current_depth < 1:
            print(f"Processing links from {url} at depth {current_depth}")
            sub_links_to_process = []
                
            # Mark all links as processed before starting
            for link in linked_pages:
                full_url = f"{BASE_URL}{link}"
                if full_url not in PROCESSED_LINKS and not any(link.startswith(root_url) for root_url in BLACKLIST_ROOT_URLS):
                    PROCESSED_LINKS.add(full_url)
                    sub_links_to_process.append(full_url)
            
            # Process in parallel only at depth 0
            if current_depth == 0:
                # Process in batches of 10
                with ThreadPoolExecutor(max_workers=MAX_BATCH_SIZE) as executor:
                    futures = [executor.submit(process_page, url, current_depth + 1) for url in sub_links_to_process]

                    # Wait for batch completion and add results in order
                    # for future in sorted(futures.keys(), key=lambda f: futures[f]):
                    for future in futures:
                        processed_pages = future.result()
                        if processed_pages:
                            current_processed_pages.extend(processed_pages)
            else:
                # Process sequentially for depth > 0
                for link in sub_links_to_process:
                    processed_pages = process_page(link, current_depth + 1)
                    current_processed_pages.extend(processed_pages)
                
    except Exception as e:
        print(f"Error processing {url}: {e}")

    return current_processed_pages

if __name__ == "__main__":
    pages_to_process = [
        ("LABOUR", "https://www.canada.ca/en/employment-social-development/corporate/portfolio/labour.html"),
        ("WORKPLACE", "https://www.canada.ca/en/services/jobs/workplace.html"),
        ("LABOUR-REPORTS", "https://www.canada.ca/en/employment-social-development/corporate/portfolio/labour/programs/labour-standards/reports.html")
    ]
    
    # Initialize PROCESSED_LINKS with starting pages
    PROCESSED_LINKS = set(pages_to_process)

    BLACKLIST_ROOT_URLS = set([
        "/en/news/"
    ])

    all_processed_pages = []
    
    for id_prefix, page_url in pages_to_process:
        processed_pages = process_page(page_url, 0)

        # Set the id for each page (Otherwise, might not be in order due to parallel processing)
        for idx, page in enumerate(processed_pages):
            page.id = f"{id_prefix}-{idx + 1}"

        all_processed_pages.extend(processed_pages)

    save_to_csv(all_processed_pages)
