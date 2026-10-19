import webbrowser
from urllib.parse import quote
import yt_dlp

class WindowsYouTubeController:
    def open(self) -> str:
        webbrowser.open_new_tab("https://www.youtube.com")
        return "Opened YouTube."
    def search(self, query: str) -> str:
        webbrowser.open_new_tab("https://www.youtube.com/results?search_query=" + quote(query))
        return f"Searching YouTube for {query}."
    def play(self, query: str) -> str:
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True}) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)
            entries = result.get("entries", []) if result else []
            if not entries or not entries[0].get("id"):
                return f"I couldn't find a YouTube video for {query}."
            video = entries[0]
            webbrowser.open_new_tab("https://www.youtube.com/watch?v=" + video["id"])
            return f"Opened {video.get('title', query)} on YouTube."
        except Exception as error:
            return f"I couldn't open that YouTube video: {error}"
