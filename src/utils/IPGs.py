from dataclasses import dataclass

@dataclass
class GenericIPG():
    """A general class to hold data from Interpretations, Policies, and Guidelines (IPGs) 
    found at https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html#st"""

    id:str = "<placeholder>" # this is called "number" on the official webpage
    title:str = "<placeholder>"
    hyperlink:str = "<placeholder>"
    text:str = "<placeholder>"

    def fetch_text_from_hyperlinks(self):
        specific_IPG = requests.get(self.hyperlink)

        soup = BeautifulSoup(specific_IPG.text, features="html.parser")

        for i in soup(["script", "style"]):
            i.extract()
        text = soup.get_text()
        text = re.sub(r'(\n\s*)+\n+', '\n\n', text)

        start = 'Interpretations, Policies and Guidelines (IPGs)'
        end = 'About this site'
        cleaned_text = text[text.find(start)+len(start):text.rfind(end)]
        self.text = cleaned_text

        return


if __name__ == "__main__":

    from io import StringIO

    from bs4 import BeautifulSoup
    import pandas as pd
    import re
    import requests

    url = "https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html"
    r = requests.get(url)
    df_list = pd.read_html(StringIO(r.text))
    IPGs = df_list[0].values # this is the first dataframed table (i.e. the Labour Standards IPGs (employment standards)

    preprocessed_IPGs = [GenericIPG(id=i[1], title=i[0]) for i in IPGs]
    print([(i.id, i.title) for i in preprocessed_IPGs])

    # fetch html object
    IPGs_main_page = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html#st")

    ls_ipgs_table = BeautifulSoup(IPGs_main_page.text, features="lxml")
    ls_ipgs_table_hrefs = ls_ipgs_table.find_all(href=True)

    result = re.search('<a href=(.*)</a>', str(ls_ipgs_table_hrefs))
    result = [i for i in result.group(0).split("</a>")]

    hrefs = []
    for i in result:
        for j in preprocessed_IPGs:
            href = re.search(f'<a href="(.*)">{j.title}', i)
            if href is not None:
                # print("canada.ca" + href.group(1))
                j.hyperlink = "canada.ca" + href.group(1)

    for i in preprocessed_IPGs:
        print([i.id, i.title, i.hyperlink])