import itertools
import json
import pathlib
from urllib.parse import urljoin

import requests
import urllib3

from parse_tululu_main import get_html_content
from parse_tululu_main import parse_book_page
from parse_tululu_main import create_arg_parser
from collections import OrderedDict


def find_book_links(content):
    links_selector = ".d_book a[href^='/b']"
    page_links = [el["href"] for el in content.select(links_selector)]
    rel_book_links = list(OrderedDict.fromkeys(page_links))
    return rel_book_links


def main(args):
    start_page = args.start_id
    end_page = args.end_id
    dest_folder = args.dest_folder
    no_txt = args.skip_txt
    no_img = args.skip_img
    json_folder = args.json_path
    book_folder = pathlib.Path(f"{dest_folder}/books/")
    img_folder = pathlib.Path(f"{dest_folder}/images/")

    if not end_page:
        end_page = start_page + 1
    if no_img:
        pass
    else:
        img_folder.mkdir(parents=True, exist_ok=True)
    if no_txt:
        pass
    else:
        book_folder.mkdir(parents=True, exist_ok=True)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        book_links = []
        for num in range(start_page, end_page):
            fantastic_link = f"https://tululu.org/l55/{num}"
            print(fantastic_link)
            html_content = get_html_content(fantastic_link)
            links = find_book_links(html_content)
            book_links.append(links)
        flat_book_links = list(itertools.chain(*book_links))

        books_description = []
        for book_link in flat_book_links:
            full_link = urljoin("https://tululu.org/", book_link)
            print(full_link)
            book_id = book_link.split("/")[1].replace("b", '')
            try:
                book_page = get_html_content(full_link)
                book = parse_book_page(
                    html_content=book_page,
                    book_id=book_id,
                    img_dir=img_folder,
                    book_dir=book_folder,
                    img_flag=no_img,
                    book_flag=no_txt)
                books_description.append(book)
            except requests.exceptions.HTTPError as err:
                print(err)
                continue

        with open(f"{json_folder}/books_description.json", "w") as my_file:
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
    cli_args = create_arg_parser().parse_args()
    main(args=cli_args)
