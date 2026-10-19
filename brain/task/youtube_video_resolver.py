from difflib import SequenceMatcher


class YouTubeVideoResolver:

    def __init__(self, screen_analyzer):
        self.screen_analyzer = screen_analyzer

    def _is_video_title(self, item: dict) -> bool:
        text = item.get("text", "").strip()
        text_lower = text.lower()

        x = item.get("pixel_x", 0)
        width = item.get("pixel_width", 0)
        height = item.get("pixel_height", 0)

        if len(text) < 20:
            return False

        # Main YouTube results area only
        if x < 1600:
            return False

        # Ignore metadata / descriptions / UI text
        ignored = [
            "views",
            "ago",
            "chapters",
            "subscribe",
            "share",
            "save",
            "shorts",
            "comments",
            "home",
            "subscriptions",
            "description",
            "summary",
            "youtube.com",
            "recently uploaded",
            "more from youtube",
            "try premium",
            "freecodecamp.org",
        ]

        if any(word in text_lower for word in ignored):
            return False

        # Description-like OCR blocks
        if text_lower.startswith(
            (
                "this course",
                "this video",
                "in this video",
                "learn ",
                "the course",
            )
        ):
            return False

        # YouTube title is generally a wide text element
        if width < 400:
            return False

        # Avoid large OCR blocks
        if height > 60:
            return False

        return True

    def _get_video_titles(self, screenshot_path: str):

        result = self.screen_analyzer.analyze(screenshot_path)

        if result.get("status") != "success":
            return []

        elements = result.get("elements", [])

        candidates = []

        for item in elements:

            if not self._is_video_title(item):
                continue

            text = item.get("text", "").strip()

            x = item.get("pixel_x")
            y = item.get("pixel_y")
            width = item.get("pixel_width", 0)
            height = item.get("pixel_height", 0)

            if x is None or y is None:
                continue

            candidates.append({
                "title": text,
                "x": x,
                "y": y,
                "width": width,
                "height": height
            })

        candidates.sort(key=lambda item: item["y"])

        # Remove description-like OCR blocks.
        # A description usually appears shortly below a real title.
        titles = []

        for item in candidates:

            is_description = False

            for title in titles:

                vertical_gap = item["y"] - (
                    title["y"] + title["height"]
                )

                if 0 <= vertical_gap <= 180:

                    # Description generally starts below the title
                    # and is usually much longer.
                    if (
                        item["width"] > title["width"]
                        or item["height"] <= 25
                    ):
                        is_description = True
                        break

            if not is_description:
                titles.append(item)

        return titles

    def resolve_ordinal(self, screenshot_path: str, index: int):

        titles = self._get_video_titles(screenshot_path)

        if index < 1:
            return None

        if index > len(titles):
            return None

        return titles[index - 1]

    def resolve_title(self, screenshot_path: str, query: str):

        titles = self._get_video_titles(screenshot_path)

        query_lower = query.lower().strip()

        best_match = None
        best_score = 0.0

        for item in titles:

            title_lower = item["title"].lower()

            # Exact phrase contained in title
            if query_lower in title_lower:
                return item

            score = SequenceMatcher(
                None,
                query_lower,
                title_lower
            ).ratio()

            if score > best_score:
                best_score = score
                best_match = item

        if best_score >= 0.35:
            return best_match

        return None