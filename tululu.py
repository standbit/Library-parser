import requests
from bs4 import BeautifulSoup
import unicodedata


url = "https://tululu.org/b1/"
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
title_tag = soup.find("h1")
title_text = title_tag.text
clean_text = unicodedata.normalize("NFKD", title_text).partition("::")
print(f"Заголовок: {clean_text[0].strip()}")
print(f"Автор: {clean_text[2].strip()}")
# author_tah = 
