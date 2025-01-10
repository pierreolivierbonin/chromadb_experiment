from io import StringIO

from bs4 import BeautifulSoup
import pandas as pd
import re
import requests


# sometimes we can directly read from the website
url = "https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html"
r = requests.get(url)
df_list = pd.read_html(StringIO(r.text))
df = df_list[0]
print(df)

LS_IPG_hours_of_work = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies/hours-work.html")

soup = BeautifulSoup(LS_IPG_hours_of_work.text, features="html.parser")

for i in soup(["script", "style"]):
    i.extract()
text = soup.get_text()
text = re.sub(r'(\n\s*)+\n+', '\n\n', text)

start = 'Interpretations, Policies and Guidelines (IPGs)'
end = 'About this site'
cleaned_text = text[text.find(start)+len(start):text.rfind(end)]