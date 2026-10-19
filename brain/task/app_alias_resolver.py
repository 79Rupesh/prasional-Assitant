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
        }

    def resolve(self, name: str) -> str:

        name = name.strip()

        if not name:
            return ""

        return self.aliases.get(
            name.lower(),
            name
        )