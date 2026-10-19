import subprocess
from urllib.parse import quote

import yt_dlp


class MacYouTubeController:

    def open(self) -> str:

        url = "https://www.youtube.com"

        subprocess.run(
            ["open", url],
            check=False
        )

        return "Opened YouTube."

    def search(self, query: str) -> str:

        encoded_query = quote(query)

        url = (
            "https://www.youtube.com/results?search_query="
            + encoded_query
        )

        subprocess.run(
            ["open", url],
            check=False
        )

        return f"Searching YouTube for {query}."

    def play(self, query: str) -> str:

        search_query = f"ytsearch1:{query}"

        options = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        try:

            with yt_dlp.YoutubeDL(options) as ydl:

                result = ydl.extract_info(
                    search_query,
                    download=False
                )

            entries = result.get("entries", [])

            if not entries:
                return f"I couldn't find a YouTube video for {query}."

            video = entries[0]

            video_id = video.get("id")

            if not video_id:
                return f"I couldn't find a playable video for {query}."

            url = f"https://www.youtube.com/watch?v={video_id}"

            subprocess.run(
                ["open", url],
                check=False
            )

            title = video.get("title", query)

            return f"Playing {title}."

        except Exception as error:

            return f"I couldn't play that YouTube video: {error}"