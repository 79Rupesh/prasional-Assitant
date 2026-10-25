import difflib

from core.interfaces.app_alias_resolver import AppAliasResolverProvider


class AppAliasResolver(AppAliasResolverProvider):

    def __init__(self):

        self.aliases = {
            # Browser
            "browser": "Safari",
            "web browser": "Safari",
            "internet": "Safari",

            # File manager
            "file manager": "Finder",
            "file explorer": "Finder",

            # Text editor
            "text editor": "TextEdit",
            "text edit": "TextEdit",
            "textedit": "TextEdit",

            # Code editor
            "code editor": "Visual Studio Code",
            "visual studio code": "Visual Studio Code",
            "visual studio": "Visual Studio Code",
            "vs code": "Visual Studio Code",
            "vscode": "Visual Studio Code",
            "chrome": "Google Chrome",
            "google chrome": "Google Chrome",
            "whatsapp": "WhatsApp",
        }

    def resolve(self, name: str) -> str:

        name = name.strip()

        if not name:
            return ""

        normalized = name.lower()
        exact = self.aliases.get(normalized)
        if exact:
            return exact

        # Speech recognition commonly swaps a letter in app names (e.g. "Crome").
        # Correct only close matches to known app names; leave other targets intact.
        candidates = set(self.aliases) | set(self.aliases.values())
        match = difflib.get_close_matches(
            normalized,
            candidates,
            n=1,
            cutoff=0.82,
        )
        if not match:
            return name
        candidate = match[0]
        return self.aliases.get(candidate, candidate)
