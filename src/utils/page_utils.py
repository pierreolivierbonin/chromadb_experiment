from typing import Tuple, List

class Page:
    def __init__(self, title: str, url: str, hierarchy: List[str], url_hierarchy: List[str], linked_pages: List[str], text: str, id: str = None):
        self.id = id # will be set later if not provided
        self.title = title
        self.url = url
        self.hierarchy = " / ".join(hierarchy)
        self.url_hierarchy = " / ".join(url_hierarchy)
        self.linked_pages = "|".join(linked_pages) if linked_pages else ""
        self.text = text
        
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