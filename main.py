import argparse
import os
import pathlib
import unicodedata
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_parser():
    parser = argparse.ArgumentParser(
        description="""скачает книги с tululu.org \
        в указанном диапазоне""")
    parser.add_argument(
        "-s",
        "--start_id",
        default="1",
        type=int,
        help="номер страницы, с которой начать скачивание книг")
    parser.add_argument(
        "-e",
        "--end_id",
        default="10",
        type=int,
        help="номер страницы, до которой скачивать книги")
    return parser


def check_for_redirect(response):
    main_urls = ["https://tululu.org/", "http://tululu.org/"]
    if response.url == main_urls[0] or response.url == main_urls[1]:
        raise requests.HTTPError


def get_html_content(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    html_content = BeautifulSoup(response.text, "lxml")
    return html_content


def get_book_title(content):
    title_tag = content.find("h1")
    title_text = title_tag.text
    clean_text = unicodedata.normalize("NFKD", title_text).partition("::")
    book_name = clean_text[0].strip()
    book_author = clean_text[2].strip()
    return book_name, book_author


def get_book_img_link(content):
    book_img_link = content.find(class_="bookimage").find("img")["src"]
    full_img_link = urljoin("http://tululu.org/", book_img_link)
    return full_img_link


def download_txt(url, payload, filename, folder="books/"):
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_file = f"{filename}.txt"
    filepath = os.path.join(folder, sanitize_filename(book_file))
    with open(filepath, "w") as outfile:
        outfile.write(response.text)


def download_image(url, folder="images/"):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    image_file = urlparse(url).path.rpartition("/")[-1]
    filepath = os.path.join(folder, image_file)
    with open(filepath, "wb") as outfile:
        outfile.write(response.content)


def get_comments(content):
    comments = []
    comments_tags = content.find(id="content").find_all(class_="texts")
    if not comments_tags:
        return ""
    for tag in comments_tags:
        comment = tag.find(class_="black").text
        comments.append(comment)
    return comments


def get_genres(content):
    tags = content.find_all(class_="d_book")
    genres = []
    for tag in tags:
        if tag.b:
            if tag.b.text == "Жанр книги:":
                a_tags = tag.find_all("a")
    for genre in a_tags:
        genres.append(genre.text)
    return genres


def parse_book_page(html_content):
    book_name, book_author = get_book_title(html_content)
    genres = get_genres(html_content)
    comments = get_comments(html_content)
    book_content = {
        "Заголовок:": book_name,
        "Автор:": book_author,
        "Жанр:": genres,
        "Комментарии:": comments,
        }
    return book_content


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    args = create_parser().parse_args()
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
            book_title = f"{num}. {book_name[0]}"
            download_txt(
                book_download_link,
                payload,
                book_title,
                books_folder)
            book_img_link = get_book_img_link(html_content)
            download_image(book_img_link)
            book_content = parse_book_page(html_content)
            print(
                book_content["Заголовок:"],
                book_content["Автор:"],
                sep="\n")
            print()
        except requests.exceptions.HTTPError:
            continue
        except requests.ConnectionError as err:
            print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()
