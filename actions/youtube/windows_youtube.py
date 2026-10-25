from urllib.parse import quote

import yt_dlp

from actions.browser.windows_browser import WindowsBrowserController


class WindowsYouTubeController:
    def __init__(self):
        self.browser_controller = WindowsBrowserController()

    def _open_url(self, url: str, description: str) -> str:
        result = self.browser_controller.open(url, browser="chrome")
        browser_name = "Google Chrome"
        if result == "Google Chrome was not found in the usual installation folders.":
            result = self.browser_controller.open(url, browser="default")
            browser_name = "the default browser"
        if result.startswith("Requested "):
            return (
                f"Requested {description} in {browser_name}; "
                "page load could not be verified."
            )
        return result

    def open(self) -> str:
        return self._open_url("https://www.youtube.com", "YouTube")

    def search(self, query: str) -> str:
        query = (query or "").strip()
        if not query:
            return "Please specify what you want to search for on YouTube."

        url = "https://www.youtube.com/results?search_query=" + quote(query)
        return self._open_url(url, f"a YouTube search for {query}")

    def play(self, query: str) -> str:
        query = (query or "").strip()
        if not query:
            return "Please specify what you want me to play."

        try:
            options = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)

            entries = result.get("entries", []) if result else []
            if not entries or not entries[0].get("id"):
                return f"I couldn't find a YouTube video for {query}."

            video = entries[0]
            url = "https://www.youtube.com/watch?v=" + video["id"]
            return self._open_url(
                url,
                f"{video.get('title', query)} on YouTube",
            )

        except Exception as error:
            return f"I couldn't open that YouTube video: {error}"
