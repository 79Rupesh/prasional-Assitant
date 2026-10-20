import subprocess
import webbrowser
import urllib.parse

from core.interfaces.action import Action


class WebSearchAction(Action):

    def execute(self, value: str) -> str:
        query = value.strip()

        if not query:
            return "What should I search for?"

        encoded_query = urllib.parse.quote_plus(query)

        url = f"https://www.google.com/search?q={encoded_query}"

        webbrowser.open_new_tab(url)

        return f"Searching for {query}"