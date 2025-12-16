import unicodedata

UNICODE_FILENAME_MAP = str.maketrans(
    {
        ":": "꞉",
        "/": "／",
        "\\": "＼",
        "?": "？",
        "*": "∗",
        '"': "＂",
        "<": "‹",
        ">": "›",
        "|": "￨",
    }  # This should allow storing the books in any filesystem
    # If they have weird chartacters in the title like
    # "Ranger's Apprentice Book 10: The Emperor of Nihon-Ja"
)


def unicode_filename_safe(text: str) -> str:
    if not text:
        return ""

    # Normalize Unicode (prevents weird combining chars)
    text = unicodedata.normalize("NFKC", text)

    # Replace forbidden characters with lookalikes
    text = text.translate(UNICODE_FILENAME_MAP)

    # Strip trailing spaces/dots (Windows limitation)
    return text.rstrip(" .")
