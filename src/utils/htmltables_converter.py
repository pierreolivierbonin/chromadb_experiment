from dataclasses import dataclass
from io import StringIO

from pandas import read_html
import requests

@dataclass
class HTMLTablestoDataframes:
    url:str = None

    def __post_init__(self):
        html_content = requests.get(self.url)
        self.df_list = read_html(StringIO(html_content.text))
