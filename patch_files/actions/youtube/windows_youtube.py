from urllib.parse import quote

import yt_dlp

from actions.browser.windows_browser import WindowsBrowserController


class WindowsYouTubeController:
    def __init__(self):
        self.browser_controller = WindowsBrowserController()

    def open(self) -> str:
        result = self.browser_controller.open("https://www.youtube.com", browser="chrome")
        if result.startswith("Opened "):
            return "Opened YouTube in Google Chrome."
        return result

    def search(self, query: str) -> str:
        query = (query or "").strip()
        if not query:
            return "Please specify what you want to search for on YouTube."

        url = "https://www.youtube.com/results?search_query=" + quote(query)
        result = self.browser_controller.open(url, browser="chrome")
        if result.startswith("Opened "):
            return f"Searching YouTube for {query} in Google Chrome."
        return result

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
            opened = self.browser_controller.open(url, browser="chrome")
            if not opened.startswith("Opened "):
                return opened

            return f"Opened {video.get('title', query)} on YouTube in Google Chrome."

        except Exception as error:
            return f"I couldn't open that YouTube video: {error}"
