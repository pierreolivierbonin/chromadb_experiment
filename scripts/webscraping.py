from io import StringIO

import bs4
import csv
import pandas as pd
import re
import requests

from utils.IPGs import GenericIPG


with open("./data/LS_IPGs.txt", "r", encoding="utf-8") as tsv_file:
    reader = csv.reader(tsv_file, delimiter="\t")
    IPGs = list(reader)

preprocessed_IPGs = [GenericIPG(id=i[1], title=i[0], text="<placeholder>") for i in IPGs]
print([i.title for i in preprocessed_IPGs])

IPGs_main_page = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html#st")

LS_IPG_hours_of_work = requests.get("https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies/hours-work.html")

print(LS_IPG_hours_of_work.text)

LS_IPG_hours_of_work = bs4.BeautifulSoup(LS_IPG_hours_of_work.text)
print(LS_IPG_hours_of_work)

ls_ipgs_table = bs4.BeautifulSoup(IPGs_main_page.text)
print(ls_ipgs_table)
ls_ipgs_table_hrefs = ls_ipgs_table.find_all(href=True)
print(ls_ipgs_table_hrefs)
with open("dump.txt", "w") as f:
   f.write(str(ls_ipgs_table_hrefs))
# print([link.get('href') for link in LS_IPG_hours_of_work.find_all('a')])

# sometimes we can directly read from the website
url = "https://www.canada.ca/en/employment-social-development/programs/laws-regulations/labour/interpretations-policies.html"
r = requests.get(url)
df_list = pd.read_html(StringIO(r.text))
df = df_list[0]
print(df)

# for i in range(len(df_list)[]):
#    print(f"Table {i}:{df_list[i].head()}")
# # print(df_list[1].head())




CLEANR = re.compile('<.*?>') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

LS_IPG_hours_of_work_clean = cleanhtml(LS_IPG_hours_of_work.text)
print(LS_IPG_hours_of_work)
