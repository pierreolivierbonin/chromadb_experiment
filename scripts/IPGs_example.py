from io import StringIO

from dataclasses import dataclass
import requests

from utils.htmltables_converter import HTMLTablestoDataframes

@dataclass
class GenericIPG:
    """A general class to hold data from Interpretations, Policies, and Guidelines (IPGs) 
    found at https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html#st"""

    id:str = "<placeholder>" # this is called "number" on the official webpage
    title:str = "<placeholder>"
    hyperlink:str = "<placeholder>"
    text:str = "<placeholder>"

    def fetch_text_from_hyperlinks(self):
        """Requires having assigned hyperlink beforehand."""
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

    # load only the first HTML table for LS IPGs (Employment standards) as an example
    url = "https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html"
    IPGs_tables = HTMLTablestoDataframes(url=url)
    LS_IPGs = IPGs_tables.df_list[0].values

    # organize and check
    preprocessed_IPGs = [GenericIPG(id=i[1], title=i[0]) for i in LS_IPGs]
    print([(i.id, i.title) for i in preprocessed_IPGs])

    # fetch html objects at given hyperlink
    IPGs_main_page = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html#st")

    # extract the table and hrefs
    ls_ipgs_table = BeautifulSoup(IPGs_main_page.text, features="lxml")
    ls_ipgs_table_hrefs = ls_ipgs_table.find_all(href=True)

    result = re.search('<a href=(.*)</a>', str(ls_ipgs_table_hrefs)) # extracts all the hyperlink HTML objects (hrefs)
    result = [" ".join(i.lower().split()) for i in result.group(0).split("</a>")]      # lowercase + whitespace removal to avoid matching issues

    # add the hyperlinks that were embedded in each LS IPG to the class instance
    for i in result:
        for j in preprocessed_IPGs:
            href = re.search(f'<a href="(.*)">{" ".join(j.title.lower().split())}', i) # lowercase + whitespace removal to avoid matching issues
            if href is not None:
                j.hyperlink = "https://www.canada.ca" + href.group(1)

    # check if everything is looking good
    for i in preprocessed_IPGs:
        print([i.id, i.title, i.hyperlink])

    # final step: add the text found at the embedded hyperlink --> longer operation as it has to request each page in a loop
    for i in preprocessed_IPGs:
        i.fetch_text_from_hyperlinks()
    
    # check if everything is looking good
    for i in preprocessed_IPGs[:5]:
        print([i.id, i.title, i.hyperlink, i.text[:100]])

    # save to dataframe, then save file for reusability (preparing for transfer into ChromaDB)
    cols = ["Number", "Name", "Text"]
    df = pd.DataFrame(preprocessed_IPGs)
    print(df)
    print(df.text)
    # df.to_csv("../../data/IPGs_Labour_standards.csv", index=False)
