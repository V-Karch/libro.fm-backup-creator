import re
import os
import csv
import zipfile
import requests
import browser_cookie3

libro_fm_cookies = {
    cookie.name: cookie.value
    for cookie in browser_cookie3.firefox()  # <- Assuming firefox for now
    if cookie.domain.endswith("libro.fm")
}  # Just the stuff from libro.fm
# Promise I don't care about your other cookies

if not libro_fm_cookies:
    print("You have not logged into https://www.libro.fm/ on a browser recently")
    print("Please do so in order to proceed")
    exit(1)

print("Libro.fm cookies found.")
print("This may take a while, especially with larger libraries")
print("Retrieving library information...")

library_export_url = "https://libro.fm/user/library/export.csv"

request_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Referer": "https://libro.fm/user/library",
}

library_csv_summary_response = requests.get(
    library_export_url, headers=request_headers, cookies=libro_fm_cookies
)

csv_reader = csv.DictReader(library_csv_summary_response.text.split("\n"))
csv_data = [row for row in csv_reader]

collected_download_urls = {}

# This will be a very lengthy operation for any reasonably sized library
# I will later implement some sort of check for if the files already exist

for row in csv_data:
    info_url = row["URL"]
    info_title = row["Title"]
    info_response = requests.get(
        info_url, headers=request_headers, cookies=libro_fm_cookies
    )
    raw_download_lines = re.findall(re.compile("Download \d.*"), info_response.text)

    for raw_download_line in raw_download_lines:
        download_url = (
            "https://libro.fm" + raw_download_line.split('href="')[1].split('">')[0]
        )
        file_title = (
            raw_download_line.split("file=")[1]
            .split("&")[0]
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("+", " ")
            .replace("%27", "'")
        )

        collected_download_urls[info_title] = []
        collected_download_urls[info_title].append({"zip_file": file_title, "download_url": download_url})

print(collected_download_urls)

# print("Created output directory")
# os.makedirs("library_out", exist_ok=True)

# zip_file_paths = []

# print("Downloading compressed files...")
# for title, url in collected_download_urls.items():
#     title_stripped = title.split(" (")[0]

#     print(f"Downloading {title}...")
#     zip_path =f"library_out/{title_stripped}/{title}"
#     os.makedirs("/".join(zip_path.split("/")[:-1]), exist_ok=True)
#     with open(zip_path, "wb") as f:
#         download_response = requests.get(url, headers=request_headers, cookies=libro_fm_cookies)
#         f.write(download_response.content)

#     zip_file_paths.append(zip_path)

# print("Extracting compressed files")
# for zip_path in zip_file_paths:
#     unzip_directory = os.path.dirname(zip_path)
#     with zipfile.ZipFile(zip_path, "r") as z:
#         z.extractall(unzip_directory)

#     print(f"Removing {zip_path}...")
#     os.remove(zip_path)
#     print("Renaming files...")
#     for i in os.listdir(unzip_directory):
#         os.rename(f"{unzip_directory}/{i}", f"{unzip_directory}/{i.split(' - ')[-1]}")
#         # Should work for every title(?)
#         # We just want track numbers for mp3s

# print("Backup finished.")
# # Proof of concept to download and extract files
# # TODO: Sort files by book author
# # TODO: Organize internal data better to store necessary info, maybe use classes