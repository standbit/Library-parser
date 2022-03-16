import requests
from bs4 import BeautifulSoup
import unicodedata


def get_book_title(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    title_tag = soup.find("h1")
    title_text = title_tag.text
    clean_text = unicodedata.normalize("NFKD", title_text).partition("::")
    return clean_text[0].strip()
