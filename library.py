import os
import re
import csv
import zipfile
import requests
from cookie import find_libro_fm_cookies
from filename_sanitizer import unicode_filename_safe


class Book:
    def __init__(self, csv_row: dict):
        self.title: str = csv_row.get("Title", "")
        self.authors: str = csv_row.get("Author(s)", "")
        self.narrators: str = csv_row.get("Narrator(s)", "")
        self.isbn: int = int(csv_row.get("ISBN", "0"))
        self.publication_date: str = csv_row.get("Publication Date", "")
        self.purchased_date: str = csv_row.get("Date Purchased", "")
        self.url: str = csv_row.get("URL", "")
        self.download_urls: list[str] = []
        self.downloaded_paths: list[str] = []

    def download(
        self, session: requests.Session, output_directory="library_out"
    ) -> None:
        if not self.download_urls:
            raise ValueError("Download URLs not populated")

        for download_url in self.download_urls:
            cleaned_name = (
                download_url.split("file=")[1][:-14]
                .replace("%28", "(")
                .replace("%29", ")")
                .replace("+", " ")
                .replace("%27", "'")
            )

            safe_authors = unicode_filename_safe(self.authors)
            safe_title = unicode_filename_safe(self.title)
            cleaned_name = unicode_filename_safe(cleaned_name)

            directory = f"{output_directory}/{safe_authors}/{safe_title}"
            os.makedirs(directory, exist_ok=True)

            download_path = f"{directory}/{cleaned_name}"
            self.downloaded_paths.append(download_path)

            with session.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(download_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)


class Library:
    LIBRARY_EXPORT_URL = "https://libro.fm/user/library/export.csv"

    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://libro.fm/user/library",
    }

    def __init__(self):
        cookies = find_libro_fm_cookies()
        if cookies is None:
            raise RuntimeError("No libro.fm cookies found. Please log in via browser.")

        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
        self.session.cookies.update(cookies)

        self.csv_summary = None
        self.books: list[Book] = []

    def fetch_csv_summary(self) -> list[dict]:
        if self.csv_summary is not None:
            return self.csv_summary

        r = self.session.get(self.LIBRARY_EXPORT_URL)
        r.raise_for_status()

        reader = csv.DictReader(r.text.splitlines())
        self.csv_summary = list(reader)
        return self.csv_summary

    def fetch_books(self) -> list[Book]:
        if self.books:
            return self.books

        for row in self.fetch_csv_summary():
            self.books.append(Book(row))

        return self.books

    def fetch_book_download_urls(self) -> list[Book]:
        for book in self.fetch_books():
            r = self.session.get(book.url)
            r.raise_for_status()

            raw_links = re.findall(r'href="(/[^"]+download[^"]+)"', r.text)
            for link in raw_links:
                book.download_urls.append("https://libro.fm" + link.replace("amp;", ""))

        return self.books

    def extract_downloaded_files(self) -> None:
        for book in self.books:
            for zip_path in book.downloaded_paths:
                with zipfile.ZipFile(zip_path) as z:
                    z.extractall(os.path.dirname(zip_path))

    def cleanup_files(self) -> None:
        for book in self.books:
            for zip_path in book.downloaded_paths:
                os.remove(zip_path)

            directory = os.path.dirname(book.downloaded_paths[0])
            for f in os.listdir(directory):
                if " - " in f:
                    os.rename(
                        f"{directory}/{f}",
                        f"{directory}/{f.split(' - ', 1)[1]}",
                    )

    def backup(self, output_directory="library_out") -> None:
        print("Fetching download URLs…")
        self.fetch_book_download_urls()

        print("Downloading books…")
        for i, book in enumerate(self.books, start=1):
            print(f"({i}/{len(self.books)}) {book.title}")
            book.download(self.session, output_directory)

        print("Extracting…")
        self.extract_downloaded_files()

        print("Cleaning up…")
        self.cleanup_files()

        print("Library backup complete ✅")
