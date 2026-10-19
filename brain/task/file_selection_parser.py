import re
from typing import Optional


class FileSelectionParser:

    def parse(self, text: str) -> Optional[int]:

        text = text.lower().strip()

        if not text:
            return None

        # Direct number: "1", "2", "10"
        if text.isdigit():
            return int(text)

        # Number words
        number_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        if text in number_words:
            return number_words[text]

        # "number 1", "number 2"
        match = re.fullmatch(r"number\s+(\d+)", text)

        if match:
            return int(match.group(1))

        # "number one", "number two"
        match = re.fullmatch(
            r"number\s+([a-z]+)",
            text
        )

        if match and match.group(1) in number_words:
            return number_words[match.group(1)]

        # "option 1", "option 2"
        match = re.fullmatch(r"option\s+(\d+)", text)

        if match:
            return int(match.group(1))

        # "option one", "option two"
        match = re.fullmatch(
            r"option\s+([a-z]+)",
            text
        )

        if match and match.group(1) in number_words:
            return number_words[match.group(1)]

        # Ordinal words
        ordinal_words = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "tenth": 10,
        }

        for word, number in ordinal_words.items():

            if text == word or text == f"{word} one":
                return number

        # "1st one", "2nd one", "3rd one", etc.
        match = re.fullmatch(
            r"(\d+)(st|nd|rd|th)(?:\s+one)?",
            text
        )

        if match:
            return int(match.group(1))

        return None