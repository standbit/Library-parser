import argparse
import json
import os
import pathlib
import unicodedata
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="скачает книги с tululu.org")
    parser.add_argument(
        "--start_id",
        type=int,
        required=True,
        help="номер страницы, с которой начать скачивать")
    parser.add_argument(
        "--end_id",
        required=False,
        type=int,
        help="номер страницы, до которой скачивать")
    parser.add_argument(
        "--dest_folder",
        required=False,
        type=str,
        default=os.getcwd(),
        help="путь к каталогу с результатами парсинга")
    parser.add_argument(
        "--skip_txt",
        required=False,
        action="store_true",
        default=False,
        help="флаг = не скачивать книги")
    parser.add_argument(
        "--skip_img",
        required=False,
        action="store_true",
        default=False,
        help="флаг = не скачивать картинки")
    parser.add_argument(
        "--json_path",
        required=False,
        type=str,
        default=os.getcwd(),
        help="путь к *.json файлу с результатами")
    return parser


def check_for_redirect(response):
    main_urls = ["https://tululu.org/", "http://tululu.org/"]
    if response.url in main_urls:
        raise requests.HTTPError(f"Ups...the page was redirected")


def get_html_content(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    html_content = BeautifulSoup(response.text, "lxml")
    return html_content


def get_book_title(content):
    title_tag = content.select_one("h1")
    title_text = title_tag.text
    divided_text = unicodedata.normalize("NFKD", title_text).partition("::")
    book_name = divided_text[0].strip()
    book_author = divided_text[2].strip()
    return book_name, book_author


def get_book_img_link(content):
    selector = ".bookimage img"
    rel_img_link = content.select_one(selector)["src"]
    full_img_link = urljoin("http://tululu.org/", rel_img_link)
    return full_img_link


def download_txt(
        url,
        payload,
        filename,
        folder):
    response = requests.get(
        url,
        params=payload,
        verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_file = f"{filename}.txt"
    book_path = os.path.join(folder, sanitize_filename(book_file))
    with open(book_path, "w") as outfile:
        outfile.write(response.text)
    return book_path


def download_image(
        url,
        folder):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    image_file = urlparse(url).path.rpartition("/")[-1]
    if image_file == "nopic.gif":
        return "No image"
    img_src = os.path.join(folder, image_file)
    with open(img_src, "wb") as outfile:
        outfile.write(response.content)
    return img_src


def get_comments(content):
    selector = "#content .texts .black"
    comments = [comment.text for comment in content.select(selector)]
    return comments


def get_genres(content):
    selector = "span.d_book a"
    genres = [genre.text for genre in content.select(selector)]
    return genres


def parse_book_page(
    html_content,
    book_id,
    img_dir,
    book_dir,
    img_flag,
    book_flag):
    book_name, book_author = get_book_title(html_content)
    genres = get_genres(html_content)
    comments = get_comments(html_content)
    if img_flag:
        img_src = "-|-Skipped-|-"
        pass
    else:
        img_link = get_book_img_link(html_content)
        img_src = download_image(
            url=img_link,
            folder=img_dir)
    if book_flag:
        book_path = "-|-Skipped-|-"
    else:
        book_download_link = "http://tululu.org/txt.php"
        payload = {"id": book_id}
        book_path = download_txt(
            url=book_download_link,
            payload=payload,
            filename=book_name,
            folder=book_dir)
    book_content = {
        "title:": book_name,
        "author:": book_author,
        "genres:": genres,
        "img_src": img_src,
        "book_path": book_path,
        "comments:": comments,
        }
    return book_content


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    args = create_arg_parser().parse_args()
    start = args.start_id
    end = args.end_id
    books_folder = pathlib.Path("books/")
    books_folder.mkdir(parents=True, exist_ok=True)
    images_folder = pathlib.Path("images/")
    images_folder.mkdir(parents=True, exist_ok=True)
    for num in range(start, end):
        book_download_link = "http://tululu.org/txt.php"
        payload = {"id": num}
        book_page = f"http://tululu.org/b{num}"
        try:
            html_content = get_html_content(book_page)
            book_name = get_book_title(html_content)
            book_title = f"{num}-я книга. {book_name[0]}"
            download_txt(
                book_download_link,
                payload,
                book_title,
                books_folder)
            book_img_link = get_book_img_link(html_content)
            download_image(book_img_link)
            book_content = parse_book_page(
                html_content=html_content,
                book_id=num)
            print(
                book_content["title:"],
                book_content["author:"],
                sep="\n")
            print()
        except requests.exceptions.HTTPError:
            continue
        except requests.ConnectionError as err:
            print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()
