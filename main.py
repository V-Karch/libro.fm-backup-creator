from library import Library


def main():
    library = Library()
    library.fetch_book_download_urls()
    book_count = 1
    for book in library.fetch_books():
        print(
            f"({book_count} / {len(library.fetch_books())}) Downloading {book.title}..."
        )
        book.download(library.cookies)
        book_count += 1


if __name__ == "__main__":
    main()
