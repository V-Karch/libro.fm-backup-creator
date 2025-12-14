from library import Library


def main():
    print("Running setup stage...")
    # Setup Stage
    library = Library()
    library.fetch_book_download_urls()

    print("Running download stage...")
    # Download Stage
    library.download_all_books()

    print("Running extraction stage...")
    # Extraction Stage
    library.extract_downloaded_files()

    # Cleanup Stage


if __name__ == "__main__":
    main()
