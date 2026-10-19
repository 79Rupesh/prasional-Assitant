import os
import difflib
import re


class WindowsFileTargetResolver:

    def __init__(self):

        self.search_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
        ]

        self.exclude_directories = {
            ".venv",
            "node_modules",
            ".git",
            "__pycache__",
            "site-packages",
            "dist",
            "build"
        }

    def resolve(
        self,
        target: str,
        target_type: str = "any"
    ) -> list:

        target = target.strip()

        if not target:
            return []

        expanded_target = os.path.expanduser(target)

        if os.path.exists(expanded_target):

            if target_type == "directory":
                if os.path.isdir(expanded_target):
                    return [expanded_target]
                return []

            if target_type == "file":
                if os.path.isfile(expanded_target):
                    return [expanded_target]
                return []

            return [expanded_target]

        target_normalized = self.normalize(target)

        if not target_normalized:
            return []

        scored_results = []

        for search_path in self.search_paths:

            if not os.path.exists(search_path):
                continue

            for root, directories, files in os.walk(search_path):

                directories[:] = [
                    directory
                    for directory in directories
                    if directory not in self.exclude_directories
                ]

                items = []

                if target_type in ["any", "directory"]:
                    items.extend(
                        (item, True)
                        for item in directories
                    )

                if target_type in ["any", "file"]:
                    items.extend(
                        (item, False)
                        for item in files
                    )

                for item, is_directory in items:

                    item_normalized = self.normalize(item)

                    score = self.match_score(
                        target_normalized,
                        item_normalized
                    )

                    if score >= 0.60:

                        scored_results.append(
                            (
                                score,
                                os.path.join(root, item)
                            )
                        )

        scored_results.sort(
            key=lambda result: result[0],
            reverse=True
        )

        return [
            path
            for score, path in scored_results
        ]

    def match_score(
        self,
        target: str,
        item: str
    ) -> float:

        if target == item:
            return 1.0

        target_words = set(target.split())
        item_words = set(item.split())

        if not target_words or not item_words:
            return 0.0

        common_words = target_words.intersection(item_words)

        if not common_words:
            return 0.0

        if len(target_words) > 1 and len(common_words) < 2:
            return 0.0

        word_score = (
            len(common_words) /
            len(target_words)
        )

        sequence_score = difflib.SequenceMatcher(
            None,
            target,
            item
        ).ratio()

        # Prefer exact word matches over partial matches
        if word_score == 1.0:
            return 0.95

        return max(
            word_score,
            sequence_score
        )

    def normalize(self, text: str) -> str:

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        words = text.split()

        filler_words = {
            "a",
            "an",
            "the",
            "of",
            "to",
            "my",
            "please"
        }

        words = [
            word
            for word in words
            if word not in filler_words
        ]

        return " ".join(words)