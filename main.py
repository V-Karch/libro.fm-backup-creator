from library import Library


def main():
    # Setup Stage
    print("Running setup stage...")
    library = Library()
    library.fetch_book_download_urls()
    book_count = 1

    print("Running download stage...")
    # Download Stage
    for book in library.fetch_books():
        print(
            f"({book_count} / {len(library.fetch_books())}) Downloading {book.title}..."
        )
        book.download(library.cookies)
        book_count += 1

    print("Running extraction stage...")
    # Extraction Stage
    library.extract_downloaded_files()

    # Cleanup Stage


if __name__ == "__main__":
    main()
