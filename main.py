from library import Library


def main():
    choice = input("Which format would you prefer? (m4b/mp3) $ ").strip().lower()

    if choice not in {"m4b", "mp3"}:
        print("Invalid choice. Please enter 'm4b' or 'mp3'.")
        return

    library = Library(preferred_format=choice)
    library.backup(output_directory="library_out")


if __name__ == "__main__":
    main()
