import pathlib

import requests


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
        except requests.HTTPError:
            continue
        with open(filename, "w") as outfile:
            outfile.write(response.text)


def check_for_redirect(response):
    main_url = "http://tululu.org/"
    if response.url == main_url:
        raise requests.HTTPError
    pass


def main():
    try:
        download_books(10)
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__=="__main__":
    main()