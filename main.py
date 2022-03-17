import os
import pathlib
import urllib3

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import unicodedata
from urllib.parse import urljoin


def get_book_title(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, "lxml")
    title_tag = soup.find("h1")
    title_text = title_tag.text
    clean_text = unicodedata.normalize("NFKD", title_text).partition("::")
    book_title = clean_text[0].strip()
    return book_title


def get_book_img_link(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, "lxml")
    book_link = soup.find(class_="bookimage").find("img")["src"]
    urljoin("http://tululu.org/", book_link)
    return urljoin("http://tululu.org/", book_link)


def check_for_redirect(response):
    main_url = ["https://tululu.org/", "http://tululu.org/"]
    if response.url == main_url[0] or response.url == main_url[1]:
        raise requests.HTTPError
    pass


def download_txt(url, filename, folder="books/"):
    book_file = f"{filename}.txt"
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, sanitize_filename(book_file))
    with open(filepath, "w") as outfile:
        outfile.write(response.text)

    
def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    books_folder = pathlib.Path("books/")
    books_folder.mkdir(parents=True, exist_ok=True)
    try:
        for num in range(1, 11):
            book_dowload_link = f"http://tululu.org/txt.php?id={num}"
            book_page = f"https://tululu.org/b{num}"
            try:
                #download_txt(book_download_link, book_title, books_folder)
                book_title = f"{num}. {get_book_title(book_page)}"
                book_img_link = get_book_img_link(book_page)
                print(book_title)
                print(book_img_link)
            except requests.exceptions.HTTPError:
                continue
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__=="__main__":
    main()