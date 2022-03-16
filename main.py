import os
import pathlib
import urllib3

import requests
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    main_url = ["https://tululu.org/", "http://tululu.org/"]
    if response.url == main_url[0] or response.url == main_url[1]:
        raise requests.HTTPError
    pass


def download_books(books_num):
    books_folder = pathlib.Path("./books/")
    books_folder.mkdir(parents=True, exist_ok=True)
    for num in range(1, books_num + 1):
        filename = f"{books_folder}//id{num}.txt"
        url = f"http://tululu.org/txt.php?id={num}"
        response = requests.get(url, verify=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            print(response.url)
        except requests.HTTPError:
            continue
        with open(filename, "w") as outfile:
            outfile.write(response.text)


def download_txt(url, filename, folder='books/'):
    books_folder = pathlib.Path(folder)
    book_name = f"{filename}.txt"
    books_folder.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(books_folder, sanitize_filename(book_name))
    with open(filepath, "w") as outfile:
        outfile.write(response.text)
    return filepath


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # try:
    #     download_books(10)
    # except requests.exceptions.HTTPError as err:
    #     print("General Error, incorrect link\n", str(err))
    # except requests.ConnectionError as err:
    #     print("Connection Error. Check Internet connection.\n", str(err))
    url = 'http://tululu.org/txt.php?id=1'

    filepath = download_txt(url, 'Алиби')
    print(filepath)  # Выведется books/Алиби.txt
    
    filepath = download_txt(url, 'Али/би', folder='books/')
    print(filepath)  # Выведется books/Алиби.txt
    
    filepath = download_txt(url, 'Али\\би', folder='txt/')
    print(filepath)  # Выведется txt/Алиби.txt


if __name__=="__main__":
    main()