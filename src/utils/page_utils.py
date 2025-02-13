from typing import Tuple, List
import os
import csv
from dataclasses import dataclass

@dataclass
class Page:
    id: str
    title: str
    url: str
    hierarchy: List[str]
    url_hierarchy: List[str]
    linked_pages: List[str]
    text: str

    def get_csv_row(self):
        return [self.id, self.title, self.url, " / ".join(self.hierarchy), " / ".join(self.url_hierarchy), "|".join(self.linked_pages) if self.linked_pages else "", self.text]
        
def extract_main_content(soup) -> Tuple[str, List[str]]:
    main_content = soup.find('main')
    if not main_content:
        return "", []
    
    linked_pages = []

    text_content = main_content.get_text().replace("\n", " ").replace("\r", " ")
        
    # Extract links from the element
    for link in main_content.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/') and href not in linked_pages:
            linked_pages.append(href)
    
    return text_content, list(linked_pages)

def save_to_csv(pages: List[Page], filename: str):
    os.makedirs("outputs", exist_ok=True)
    csv_path = f"outputs/{filename}"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'hyperlink', 'hierarchy', 'url_hierarchy', 'linked_pages', 'text'])
        for page in pages:
            writer.writerow(page.get_csv_row())

    print(f"Saved {len(pages)} pages to {csv_path}")