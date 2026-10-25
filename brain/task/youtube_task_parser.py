
import re


class YouTubeTaskParser:

    def parse(self, text: str) -> dict:
        text_lower = text.lower().strip()
        text_lower = text_lower.rstrip(".!?")

        # Remove common conversational fillers and greetings.
        text_lower = re.sub(
            r"^(?:(?:hello|hi|hey)\s+ela|ela)[,\s:!-]*",
            "",
            text_lower,
        )

        text_lower = re.sub(
            r"^(okay|ok|alright|right|please)[,\s]+",
            "",
            text_lower,
        ).strip()

        operation = "unknown"
        query = None
        selection = None
        index = None

        # Open YouTube.
        if re.fullmatch(
            r"(?:open|launch|start|go to)\s+(?:a\s+)?youtube"
            r"(?:\s*,?\s+(?:ai|assistant|please|for me))?",
            text_lower,
        ):
            operation = "open"

        # Search YouTube.
        elif (
            text_lower.startswith("search for ")
            or text_lower.startswith("search ")
            or text_lower.startswith("find ")
        ):
            operation = "search"

            prefixes = ("search for ", "search ", "find ")
            for prefix in prefixes:
                if text_lower.startswith(prefix):
                    query = text_lower[len(prefix):].strip()
                    break

            for phrase in (
                " on youtube",
                " in youtube",
                " on youtube for",
            ):
                if query and query.endswith(phrase):
                    query = query[:-len(phrase)].strip()

            query = (query or "").rstrip(".!?").strip()

            if not query:
                operation = "unknown"
                query = None

        # Select a numbered video, e.g. "Play first video".
        elif re.search(
            r"\b(\d+)(?:st|nd|rd|th)?\s+video\b",
            text_lower,
        ) or re.search(
            r"\b(first|second|third|fourth|fifth|sixth|"
            r"seventh|eighth|ninth|tenth)\s+video\b",
            text_lower,
        ):
            numeric_match = re.search(
                r"\b(\d+)(?:st|nd|rd|th)?\s+video\b",
                text_lower,
            )

            word_match = re.search(
                r"\b(first|second|third|fourth|fifth|sixth|"
                r"seventh|eighth|ninth|tenth)\s+video\b",
                text_lower,
            )

            operation = "play"
            selection = "ordinal"

            if numeric_match:
                index = int(numeric_match.group(1))
            else:
                ordinal_map = {
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

                index = ordinal_map[word_match.group(1)]

        # Select a video by title.
        elif "video" in text_lower and "wala" in text_lower:
            operation = "play"
            selection = "title"

            query = re.sub(
                r"\bvideo\b|\bplay\b|\bkaro\b|\bkar do\b|"
                r"\bplease\b|\bwala\b",
                "",
                text_lower,
            )

            query = " ".join(query.split()).strip()

        # Play a video by search query.
        elif text_lower.startswith("play "):
            operation = "play"
            query = text_lower[len("play "):].strip()

            for phrase in (" on youtube", " in youtube", " youtube"):
                if query.endswith(phrase):
                    query = query[:-len(phrase)].strip()
                    break

            query = query.rstrip(".!?").strip()

            if not query:
                operation = "unknown"
                query = None

        return {
            "operation": operation,
            "query": query,
            "selection": selection,
            "index": index,
        }
