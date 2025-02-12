#!/usr/bin/env python3
"""
This script extracts Interpretations, Policies and Guidelines (IPGs) from the Canada Labour Program website.
For each IPG it:
  - Creates a Page object containing the IPG's metadata and content
  - Extracts content from the linked page
  - Saves all IPG data to a CSV file
"""

import csv
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

from utils.page_utils import Page, extract_main_content

MAX_WORKERS = 10
BASE_URL = "https://www.canada.ca"

def process_ipg_page(url: str, title: str, ipg_id: str, hierarchy: str) -> Optional[Page]:
    try:
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text, linked_pages = extract_main_content(soup)

        print(f"Processed IPG: {title} - {full_url} (Hierarchy: {hierarchy})")
        
        # Create Page object with empty url_hierarchy and the linked_pages from extract_main_content
        return Page(
            title=title,
            url=full_url,
            hierarchy=[hierarchy],  # Pass as list since Page joins it
            url_hierarchy=[],      # Empty list since we don't extract url hierarchy
            linked_pages=linked_pages,
            text=text,
            id=ipg_id
        )
    
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def extract_ipgs_from_table(table) -> List[tuple]:
    ipgs = []
    
    # Find table title (usually in a caption or preceding h2/h3)
    table_title = ""
    caption = table.find('caption')
    if caption:
        table_title = caption.get_text(strip=True)
    else:
        # Look for preceding header
        prev_elem = table.find_previous(['h2', 'h3'])
        if prev_elem:
            table_title = prev_elem.get_text(strip=True)
    
    # Find the header row to determine column positions
    headers = table.find_all('th')
    title_idx = next((i for i, h in enumerate(headers) if 'Title' in h.get_text()), 0)
    number_idx = next((i for i, h in enumerate(headers) if 'Number' in h.get_text() or 'No.' in h.get_text()), 1)
    
    # Process each row
    for row in table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all(['td', 'th'])
        if len(cells) <= max(title_idx, number_idx):
            continue
            
        title_cell = cells[title_idx]
        number_cell = cells[number_idx]
        
        # Extract title and link
        link = title_cell.find('a')
        if not link:
            continue
            
        title = title_cell.get_text(strip=True)
        url = link.get('href')
        ipg_id = number_cell.get_text(strip=True)
        
        if url and title and ipg_id:
            ipgs.append((title, url, ipg_id, table_title))
    
    return ipgs

def save_to_csv(pages: List[Page]):
    os.makedirs("outputs", exist_ok=True)
    csv_path = f"outputs/ipgs.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'hyperlink', 'hierarchy', 'url_hierarchy', 'linked_pages', 'text'])
        for page in pages:
            writer.writerow([page.id, page.title, page.url,page.hierarchy, page.url_hierarchy, page.linked_pages, page.text])

    print(f"Saved {len(pages)} IPGs to {csv_path}")

def main():
    # Fetch main IPG page
    response = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html")
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    
    # Extract IPGs from all tables
    all_ipgs = []
    for table in tables:
        all_ipgs.extend(extract_ipgs_from_table(table))
    
    print(f"Found {len(all_ipgs)} IPGs to process")
    
    # Process IPG pages in parallel
    processed_pages = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_ipg = {
            executor.submit(process_ipg_page, url, title, ipg_id, hierarchy): (title, url, ipg_id, hierarchy) 
            for title, url, ipg_id, hierarchy in all_ipgs
        }
        
        for future in future_to_ipg:
            page = future.result()
            if page:
                processed_pages.append(page)
    
    save_to_csv(processed_pages)

if __name__ == "__main__":
    main()
