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


def find_book_links(content):
    book_tags = content.find_all(class_="d_book")
    links = []
    for tag in book_tags:
        relative_link = tag.find("a")["href"]
        book_link = urljoin("https://tululu.org/", relative_link)
        links.append(book_link)
    return links


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    fantastic_link = "https://tululu.org/l55/"
    try:
        for num in range(1, 11):
            fantastic_link = f"https://tululu.org/l55/{num}"
            html_content = get_html_content(fantastic_link)
            links = find_book_links(html_content)
            for link in links:
                print(link)
    except requests.exceptions.HTTPError as err:
        print("General error.\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()