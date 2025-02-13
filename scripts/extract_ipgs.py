#!/usr/bin/env python3
"""
This script extracts Interpretations, Policies and Guidelines (IPGs) from the Canada Labour Program website.
For each IPG it:
  - Creates a Page object containing the IPG's metadata and content
  - Extracts content from the linked page
  - Saves all IPG data to a CSV file
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from dataclasses import dataclass

from utils.page_utils import Page, extract_main_content, save_to_csv

MAX_WORKERS = 10
BASE_URL = "https://www.canada.ca"

@dataclass
class IPG:
    title: str
    url: str
    id: str
    table_title: str

def process_ipg_page(ipg: IPG) -> Optional[Page]:
    try:
        full_url = urljoin(BASE_URL, ipg.url)
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text, linked_pages = extract_main_content(soup)

        print(f"Processed IPG: {ipg.title} - {full_url} (Hierarchy: {ipg.table_title})")
        
        return Page(
            title=ipg.title,
            url=full_url,
            hierarchy=[ipg.table_title],
            url_hierarchy=[],
            linked_pages=linked_pages,
            text=text,
            id=ipg.id
        )
    
    except Exception as e:
        print(f"Error processing {ipg.url}: {e}")
        return None

def extract_ipgs_from_table(table) -> List[IPG]:
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
        cells = row.find_all('td')
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
            ipgs.append(IPG(title, url, ipg_id, table_title))
    
    return ipgs

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
            executor.submit(process_ipg_page, ipg): ipg 
            for ipg in all_ipgs
        }
        
        for future in future_to_ipg:
            page = future.result()
            if page:
                processed_pages.append(page)
    
    save_to_csv(processed_pages, "ipgs.csv")

if __name__ == "__main__":
    main()
