import itertools
import json
import pathlib
from urllib.parse import urljoin, urlparse

import requests
import urllib3

from main import get_html_content, parse_book_page
from collections import OrderedDict



def find_book_links(content):
    links_selector = ".d_book a[href^='/b']"
    page_links = [el["href"] for el in content.select(links_selector)]
    rel_book_links= list(OrderedDict.fromkeys(page_links))
    return rel_book_links


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    books_folder = pathlib.Path("books/")
    books_folder.mkdir(parents=True, exist_ok=True)
    images_folder = pathlib.Path("images/")
    images_folder.mkdir(parents=True, exist_ok=True)
    try:
        book_links = []
        for num in range(1, 5):
            fantastic_link = f"https://tululu.org/l55/{num}"
            html_content = get_html_content(fantastic_link)
            links = find_book_links(html_content)
            book_links.append(links)
        flat_book_links = list(itertools.chain(*book_links))
        books_description = []
        for book_link in flat_book_links:
            full_link = urljoin("https://tululu.org/", book_link)
            book_id = book_link.split("/")[1].replace("b", '')
            try:
                book_page = get_html_content(full_link)
                book = parse_book_page(book_page, book_id)
                books_description.append(book)
            except requests.exceptions.HTTPError as err:
                print(err)
                continue
        with open("books_description.json", "w") as my_file:
            json.dump(
                books_description,
                my_file,
                indent=4,
                sort_keys=True,
                ensure_ascii=False)
    except requests.exceptions.HTTPError as err:
        print("General error.\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()
