#!/usr/bin/env python3
import json
import logging
import pathlib
from collections import OrderedDict
from urllib.parse import urljoin

import requests
import urllib3

from parse_tululu_main import (create_arg_parser, get_html_content,
                               parse_book_page)


def find_book_links(content):
    selector = ".d_book a[href^='/b']"
    page_links = [el["href"] for el in content.select(selector)]
    relative_book_links = list(OrderedDict.fromkeys(page_links))
    return relative_book_links


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("Check links")
    logger.setLevel(logging.INFO)
    args = create_arg_parser().parse_args()
    start_page = args.start_id
    end_page = args.end_id
    dest_folder = args.dest_folder
    skip_txt = args.skip_txt
    skip_img = args.skip_img
    json_folder = args.json_path
    book_folder = pathlib.Path(f"{dest_folder}/books/")
    img_folder = pathlib.Path(f"{dest_folder}/images/")

    if not end_page:
        end_page = start_page + 1
    if not skip_img:
        img_folder.mkdir(parents=True, exist_ok=True)
    if not skip_txt:
        book_folder.mkdir(parents=True, exist_ok=True)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        relative_book_links = []
        for num in range(start_page, end_page):
            fantastic_link = f"https://tululu.org/l55/{num}"
            html_content = get_html_content(fantastic_link)
            links = find_book_links(html_content)
            relative_book_links.extend(links)

        books_description = []
        for link in relative_book_links:
            book_link = urljoin("https://tululu.org/", link)
            book_id = "".join(num for num in link if num.isdigit())
            try:
                book_page = get_html_content(book_link)
                book = parse_book_page(
                    html_content=book_page,
                    book_id=book_id,
                    img_dir=img_folder,
                    book_dir=book_folder,
                    img_flag=skip_img,
                    book_flag=skip_txt)
                books_description.append(book)
                logger.info(f"{book_link} is parsed - OK")
            except requests.exceptions.HTTPError:
                logger.warning(f"{book_link} has no link for downloading txt")
                continue
    except requests.exceptions.HTTPError as err:
        logger.error(f"General error - {str(err)}")
    except requests.ConnectionError as err:
        logger.error(f"Connection Error, check Internet connect - {str(err)}")

    with open(f"{json_folder}/books_description.json", "w") as output_file:
        json.dump(
            books_description,
            output_file,
            indent=4,
            sort_keys=True,
            ensure_ascii=False)


if __name__ == "__main__":
    main()
