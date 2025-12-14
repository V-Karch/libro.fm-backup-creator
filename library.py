import os
import re
import csv
import zipfile
import requests
from cookie import find_libro_fm_cookies


class Book:
    def __init__(self, csv_row: dict):
        self.title: str = csv_row.get("Title", "")
        self.authors: str = csv_row.get("Author(s)", "")
        self.narrators: str = csv_row.get("Narrator(s)", "")
        self.isbn: int = int(csv_row.get("ISBN", "0"))
        self.publication_date: str = csv_row.get("Publication Date", "")
        self.purchased_date: str = csv_row.get("Date Purchased", "")
        self.url: str = csv_row.get("URL", "")
        self.download_urls: list[str] = []  # Populated externally
        self.downloaded_paths: list[str] = []  # Populated after download

    def __str__(self):
        parts: list[str] = [
            f"Title: {self.title}",
            f"Author(s): {self.authors}",
            f"Narrator(s): {self.narrators}",
            f"ISBN: {self.isbn if self.isbn != 0 else 'N/A'}",
            f"Publication Date: {self.publication_date or 'N/A'}",
            f"Purchased Date: {self.purchased_date or 'N/A'}",
            f"URL: {self.url or 'N/A'}",
        ]
        return "\n".join(parts)

    def download(self, cookies, output_directory="library_out") -> None:
        # Extremely lengthy, depends on network connection
        # and file size and disk storage and etc.

        if self.download_urls == []:
            raise ValueError(
                "You must first populate the book's download_urls through Library().fetch_book_download_urls()"
            )

        for download_url in self.download_urls:
            cleaned_download_name = (
                download_url.split("file=")[1][:-14]
                .replace("%28", "(")
                .replace("%29", ")")
                .replace("+", " ")
                .replace("%27", "'")
            )  # Removing some garbage characters

            download_path = f"{output_directory}/{self.authors}/{self.title}/{cleaned_download_name}"
            directory_path = f"{output_directory}/{self.authors}/{self.title}"
            os.makedirs(directory_path, exist_ok=True)
            self.downloaded_paths.append(download_path)

            with open(download_path, "wb") as f:
                download_response = requests.get(
                    download_url, headers=Library.REQUEST_HEADERS, cookies=cookies
                )
                f.write(download_response.content)


class Library:
    LIBRARY_EXPORT_URL: str = "https://libro.fm/user/library/export.csv"
    REQUEST_HEADERS: dict[str:str] = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
        "Referer": "https://libro.fm/user/library",
    }

    def __init__(self):
        self.cookies = find_libro_fm_cookies()
        self.csv_summary = None
        self.books: list[Book] = []

        if self.cookies is None:
            print(
                "You have not logged into https://www.libro.fm/ on a browser recently"
            )
            print("Please do so in order to proceed")
            raise Exception(
                "You are missing https://libro.fm/ cookies, which are required to run this program"
            )

    def fetch_csv_summary(self) -> dict:
        if self.csv_summary is not None:
            # ^^ If we already have, cache it
            return self.csv_summary

        csv_summary_response = requests.get(
            Library.LIBRARY_EXPORT_URL,
            headers=Library.REQUEST_HEADERS,
            cookies=self.cookies,
        )

        csv_reader = csv.DictReader(csv_summary_response.text.split("\n"))
        self.csv_summary = [row for row in csv_reader]

        return self.csv_summary

    def fetch_books(self) -> list[Book]:
        if self.books != []:
            # If already populated, don't refill
            return self.books

        csv_summary = self.fetch_csv_summary()
        for row in csv_summary:
            self.books.append(Book(row))

        return self.books

    def fetch_book_download_urls(self) -> list[Book]:
        # This can be very lengthy due to the amount of required requests
        # Especially if the library is large
        for book in self.fetch_books():
            page_response = requests.get(
                book.url, headers=Library.REQUEST_HEADERS, cookies=self.cookies
            )
            raw_download_lines = re.findall(
                re.compile("Download \d.*"), page_response.text
            )

            for raw_download_line in raw_download_lines:
                download_url = (
                    "https://libro.fm"
                    + raw_download_line.split('href="')[1].split('">')[0]
                ).replace("amp;", "")
                book.download_urls.append(download_url)

        return self.books

    def extract_downloaded_files(self) -> None:
        books_list = self.fetch_books()

        for book in books_list:  # Preliminary Path
            if book.downloaded_paths == []:
                raise ValueError(
                    "Cannot extract files if they have not all been downloaded"
                )

        book_count = 1
        for book in books_list:
            for zip_file_path in book.downloaded_paths:
                zip_file = zipfile.ZipFile(zip_file_path)
                zip_file.extractall("/".join(zip_file_path.split("/")[:-1]))
                print(
                    f"({book_count} / {len(books_list)}) Extracting {zip_file_path}..."
                )
