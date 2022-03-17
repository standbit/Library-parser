import os
import pathlib
import urllib3

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import unicodedata
from urllib.parse import urljoin
from urllib.parse import urlparse
from pprint import pprint


BOOK_CONTENT ={
    "Заголовок:": "",
    "Автор:": "",
    "Жанр:": "",
    "Комментарии:": "",
}

def get_book_title(content):
    title_tag = content.find("h1")
    title_text = title_tag.text
    clean_text = unicodedata.normalize("NFKD", title_text).partition("::")
    book_name = clean_text[0].strip()
    book_author = clean_text[2].strip()
    return book_name, book_author


def get_book_img_link(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, "lxml")
    book_img_link = soup.find(class_="bookimage").find("img")["src"]
    full_img_link = urljoin("http://tululu.org/", book_img_link)
    return full_img_link


def check_for_redirect(response):
    main_url = ["https://tululu.org/", "http://tululu.org/"]
    if response.url == main_url[0] or response.url == main_url[1]:
        raise requests.HTTPError
    pass


def download_txt(url, filename, folder="books/"):
    book_file = f"{filename}.txt"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, sanitize_filename(book_file))
    with open(filepath, "w") as outfile:
        outfile.write(response.text)


def download_image(url, folder="images/"):
    image_file = urlparse(url).path.rpartition("/")[-1]
    response = requests.get(url, verify=False)
    response.raise_for_status()
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


def get_html_content(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    html_content = BeautifulSoup(response.text, "lxml")
    return html_content


def parse_book_page(html_content):
    book_name, book_author = get_book_title(html_content)
    genres = get_genres(html_content)
    comments = get_comments(html_content)
    BOOK_CONTENT["Заголовок:"] = book_name
    BOOK_CONTENT["Автор:"] = book_author
    BOOK_CONTENT["Жанр:"] = genres
    BOOK_CONTENT["Комментарии:"] = comments
    return BOOK_CONTENT


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # books_folder = pathlib.Path("books/")
    # books_folder.mkdir(parents=True, exist_ok=True)
    # images_folder = pathlib.Path("images/")
    # images_folder.mkdir(parents=True, exist_ok=True)
    try:
        for num in range(1, 11):
            # book_dowload_link = f"http://tululu.org/txt.php?id={num}"
            book_page = f"https://tululu.org/b{num}"
            try:
                # download_txt(book_download_link, book_title, books_folder)
                # book_title = f"{num}. {get_book_title(book_page)}"
                # book_img_link = get_book_img_link(book_page)
                # download_image(book_img_link)
                # download_comments(book_page)
                html_content = get_html_content(book_page)
                book_content = parse_book_page(html_content)
                print(book_content["Заголовок:"], book_content["Жанр:"], sep="\n" )
                print()
            except requests.exceptions.HTTPError:
                continue
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__=="__main__":
    main()