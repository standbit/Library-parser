import requests


filename = "dvmn.svg"
url = "https://dvmn.org/filer/canonical/1542890876/16/"
response = requests.get(url)
response.raise_for_status()
with open(filename, "wb") as outfile:
    outfile.write(response.content)
