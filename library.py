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

    def download(self, session: requests.Session, output_directory: str) -> None:
        if not self.download_urls:
            raise ValueError("Download URLs not populated")

        for download_url in self.download_urls:
            filename = download_url.split("file=")[-1]
            filename = filename.split("&")[0]
            filename = filename.replace("+", " ")
            filename = unicode_filename_safe(filename)

            safe_authors = unicode_filename_safe(self.authors)
            safe_title = unicode_filename_safe(self.title)

            directory = f"{output_directory}/{safe_authors}/{safe_title}"
            os.makedirs(directory, exist_ok=True)

            download_path = f"{directory}/{filename}"
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

    def __init__(self, preferred_format: str):
        if preferred_format not in {"mp3", "m4b"}:
            raise ValueError("preferred_format must be 'mp3' or 'm4b'")

        self.preferred_format = preferred_format

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

            links = re.findall(r'href="(/[^"]+download[^"]+)"', r.text)

            for link in links:
                full_url = "https://libro.fm" + link.replace("amp;", "")
                lower = full_url.lower()

                if self.preferred_format == "mp3" and ".zip" in lower:
                    book.download_urls.append(full_url)

                elif self.preferred_format == "m4b" and ".m4b" in lower:
                    book.download_urls.append(full_url)

            if not book.download_urls:
                print(f"⚠️ No {self.preferred_format} download found for: {book.title}")

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

    def backup(self, output_directory: str = "library_out") -> None:
        print("Fetching download URLs…")
        self.fetch_book_download_urls()

        print("Downloading books…")
        for i, book in enumerate(self.books, start=1):
            print(f"({i}/{len(self.books)}) {book.title}")
            book.download(self.session, output_directory)

        if self.preferred_format == "mp3":
            print("Extracting…")
            self.extract_downloaded_files()

            print("Cleaning up…")
            self.cleanup_files()

        print("Library backup complete ✅")
