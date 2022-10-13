#!/usr/bin/env python3
import json
import logging
from collections import OrderedDict
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
import urllib3

from parse_tululu_main import (create_arg_parser, download_image, download_txt,
                               get_book_img_link, get_book_name_author,
                               get_html_content, parse_book_page)

logger = logging.getLogger(__file__)


def find_book_links(content):
    selector = ".d_book a[href^='/b']"
    page_links = [el["href"] for el in content.select(selector)]
    relative_book_links = list(OrderedDict.fromkeys(page_links))
    return relative_book_links


def main():
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d",)
    logger.setLevel(logging.INFO)

    args = create_arg_parser().parse_args()
    start_page = args.start_id
    end_page = args.end_id
    dest_folder = args.dest_folder
    skip_txt = args.skip_txt
    skip_img = args.skip_img
    json_folder = args.json_path
    book_folder = Path(dest_folder, "books")
    img_folder = Path(dest_folder, "images")
    img_src = None
    book_path = None

    if not end_page:
        end_page = start_page + 1
    if not skip_img:
        img_folder.mkdir(parents=True, exist_ok=True)
    if not skip_txt:
        book_folder.mkdir(parents=True, exist_ok=True)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    relative_book_links = []
    for num in range(start_page, end_page):
        fantastic_link = f"https://tululu.org/l55/{num}"
        try:
            html_content = get_html_content(fantastic_link)
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error - {str(err)}")
            continue
        except requests.ConnectionError as err:
            logger.error(f"ConnectionError, check Internet connect-{str(err)}")
            sleep(10)
            continue
        links = find_book_links(html_content)
        relative_book_links.extend(links)
    books_description = []

    for link in relative_book_links:
        book_link = urljoin("https://tululu.org/", link)
        book_id = "".join(num for num in link if num.isdigit())
        try:
            book_page = get_html_content(book_link)

            if not skip_img:
                img_link = get_book_img_link(
                    base_link=book_link,
                    content=book_page)
                img_src = download_image(
                   download_url=img_link,
                   folder=img_folder)
            
            if not skip_txt:
                book_download_link = "http://tululu.org/txt.php"
                payload = {"id": book_id}
                book_name = get_book_name_author(
                    content=book_page,
                    flag=True)
                book_path = download_txt(
                    download_url=book_download_link,
                    payload=payload,
                    filename=book_name,
                    folder=book_folder)
    
            book = parse_book_page(
                html_content=book_page,
                book_path=book_path,
                img_src=img_src)
            books_description.append(book)
            logger.info(f"{book_link} is parsed - OK")
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error - {str(err)}")
            continue
        except requests.exceptions.TooManyRedirects:
                logger.warning(f"Redirect! {book_link} don't allow to download txt/img")
                continue
        except requests.ConnectionError as err:
            logger.error(f"ConnectionError, check Internet connect-{str(err)}")
            sleep(10)
            continue

    json_path = Path(json_folder, "books_description.json")
    with open(json_path, "w", encoding="utf-8") as output_file:
        json.dump(
            books_description,
            output_file,
            indent=4,
            sort_keys=True,
            ensure_ascii=False)


if __name__ == "__main__":
    main()
