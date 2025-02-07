#!/usr/bin/env python3
"""
This script scrapes the Canada Labour Code
It processes the table-of-contents recursively so that only the leaf sections are output.
For each leaf it:
  - Extracts the link URL, title, and (if available) a section number.
  - Constructs a "Hierarchy" string from its parent nodes (skipping the topmost "Canada Labour Code").
  - Downloads the associated page and (if the URL contains an anchor) extracts only the text
    between the start of the corresponding <hX> tag and the next <hX>, if any.
It writes each leaf section's title, section number, hierarchy, URL and text as a row in clb.csv.
"""

import csv
import time
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class TocItem:
    def __init__(self, title: str, section_number: str, link_url: str, hierarchy: str):
        self.title = title
        self.section_number = section_number
        self.link_url = link_url
        self.hierarchy = hierarchy

# Recursively process a TOC element.
def parse_toc_items(ul, current_hierarchy, base_url, root_name) -> list[TocItem]:
    items = []
    for li in ul.find_all("li", recursive=False):
        # Get the first link in this <li>
        a = li.find("a", recursive=False)
        if not a:
            continue
        link_url = a.get("href", "")

        title = a.get_text(strip=True)
        
        # Extract section number if available from a <span class="sectionRange"> within the <li>.
        section_number = ""
        span_tag = li.find("span", class_="sectionRange")

        if span_tag:
            m = re.match(r'\s*(\d+)', span_tag.get_text(strip=True))
            if m:
                section_number = m.group(1)
        
        # Check if this <li> has children
        child_ul = li.find("ul", recursive=False)
        if child_ul:
            # Build new hierarchy; skip adding the topmost node "Canada Labour Code"
            new_hierarchy = list(current_hierarchy)
            if title != root_name:
                new_hierarchy.append(title)
            child_items = parse_toc_items(child_ul, new_hierarchy, base_url, root_name)
            items.extend(child_items)
        else:
            hierarchy_str = " / ".join(current_hierarchy)

            # Extract everything after the first #
            link_url = "#" + link_url.split("#")[1] if "#" in link_url else link_url

            items.append(TocItem(title, section_number, link_url, hierarchy_str))
    return items

# Fetch the main Labour Code page and parse the table-of-contents recursively.
def get_main_toc_links(base_url: str, root_name: str) -> list[TocItem]:
    response = requests.get(base_url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    toc = soup.find('ul', class_='TocIndent')
    toc_items = parse_toc_items(toc, [], base_url, root_name)
    return toc_items

# Given a candidate section URL, download and extract the text content for that specific section.
def extract_page_text(soup, url):
    parsed_url = urlparse(url)
    if parsed_url.fragment:
        header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]

        # Look for the section header with the matching fragment id
        section_header = soup.find(header_tags, id=parsed_url.fragment)
        if not section_header:
            print(f"Section with ID '{parsed_url.fragment}' not found in {url}.")
            return ""
        
        # Check if the header is within a <header> tag
        parent_header = section_header.find_parent('header')
        if parent_header:
            section_header = parent_header
        
        # Start with the header's text
        extracted_text = section_header.get_text(separator="\n", strip=True)

        # Grab subsequent siblings up to the next <hX>
        for sibling in section_header.find_next_siblings():
            # Include all siblings if in a <header> tag section (Ex : Schedule I)
            if sibling.name in header_tags and parent_header is None:
                break
            extracted_text += "\n" + sibling.get_text(separator="\n", strip=True)

        # Replace newlines with spaces
        extracted_text = extracted_text.replace("\n", " ").replace("\r", " ")

        return extracted_text.strip()
    else:
        return None

def process_toc_page(toc_url, full_page_url, file_name, root_name, empty_section_number_prefix = ""):
    print("Fetching table of contents links...")
    toc_items = get_main_toc_links(toc_url, root_name)
    print(f"Found {len(toc_items)} leaf links.")
    soup = None

    try:
        response = requests.get(full_page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
    except Exception as e:
        print(f"Error extracting text from {full_page_url}: {e}")
        return ""
    
    # Open the CSV file for writing.
    with open(f"outputs/{file_name}.csv", "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["ID", "Title", "Section Number", "Hierarchy", "Hyperlink", "Text"])
        empty_section_nb = 1
        
        for toc_item in toc_items:
            url = requests.compat.urljoin(full_page_url, toc_item.link_url)
            print(f"Processing: {toc_item.title} - {url} (Section Number: {toc_item.section_number}, Hierarchy: {toc_item.hierarchy})")
            text = extract_page_text(soup, url)

            if not text:
                print(f"No text found for {url}")
                continue

            id_prefix = file_name.upper() + "-"
            if toc_item.section_number:
                id_text = f"{id_prefix}{toc_item.section_number}"
            else:
                id_text = f"{id_prefix}{empty_section_number_prefix}_{empty_section_nb}"
                empty_section_nb += 1

            csv_writer.writerow([id_text, toc_item.title, toc_item.section_number, toc_item.hierarchy, url, text])

if __name__ == "__main__":
    documents = [
        (
            "https://laws-lois.justice.gc.ca/eng/acts/l-2/",
            "https://laws-lois.justice.gc.ca/eng/acts/l-2/FullText.html",
            "clc",
            "Canada Labour Code",
            ""
        ),
        (
            "https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.,_c._986",
            "https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.,_c._986/FullText.html", 
            "clsr",
            "Canada Labour Standards Regulations",
            "SCHEDULE"
        )
    ]

    for toc_url, full_page_url, file_name, root_name, empty_section_number_prefix in documents:
        process_toc_page(toc_url, full_page_url, file_name, root_name, empty_section_number_prefix)