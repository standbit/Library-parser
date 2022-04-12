import argparse
import os
import pathlib
import unicodedata
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_html_content(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    html_content = BeautifulSoup(response.text, "lxml")
    return html_content


def get_book_links(content):
    book_names_tags = content.find(class_="flex").find_all(class_="name")
    links = []
    for tag in book_names_tags:
        relative_link = tag.find("a")["href"]
        book_link = urljoin("https://tululu.org/", relative_link)
        links.append(book_link)
    return links


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    fantastic_link = "https://tululu.org/g/27-nauchnaya-fantastika"
    try:
        html_content = get_html_content(fantastic_link)
        links = get_book_links(html_content)
        for link in links:
            print(link)
    except requests.exceptions.HTTPError as err:
        print("General error.\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()