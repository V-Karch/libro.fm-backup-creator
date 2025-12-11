import re
import csv
import requests
import browser_cookie3

libro_fm_cookies = {
    cookie.name: cookie.value
    for cookie in browser_cookie3.firefox() # <- Assuming firefox for now
    if cookie.domain.endswith("libro.fm")
}  # Just the stuff from libro.fm
# Promise I don't care about your other cookies

if not libro_fm_cookies:
    print("You have not logged into https://www.libro.fm/ on a browser recently")
    print("Please do so in order to proceed")
    exit(1)

print("Libro.fm cookies found.")

library_export_url = "https://libro.fm/user/library/export.csv"

request_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Referer": "https://libro.fm/user/library",
}

print("Downloading library summary as csv.")

library_csv_summary_response = requests.get(
    library_export_url, headers=request_headers, cookies=libro_fm_cookies
)

print("Library csv downloaded.")

print("Reading csv")


csv_reader = csv.DictReader(library_csv_summary_response.text.split("\n"))
csv_data = [row for row in csv_reader]

for row in csv_data:
    if row["Title"] == "Halt's Peril":
        info_url = row["URL"]
        info_response = requests.get(info_url, headers=request_headers, cookies=libro_fm_cookies)
        raw_download_lines = re.findall(re.compile("Download \d.*"), info_response.text)

        for raw_download_line in raw_download_lines:
            download_url = "https://libro.fm" + raw_download_line.split('href="')[1].split('">')[0]
            print(download_url)
            
        break
