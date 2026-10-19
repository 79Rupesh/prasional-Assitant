class BrowserResolver:

    BROWSERS = {
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "firefox": "Firefox",
        "safari": "Safari",
        "edge": "Microsoft Edge",
        "microsoft edge": "Microsoft Edge",
        "brave": "Brave Browser",
    }

    def resolve(self, browser_name: str) -> str:

        name = browser_name.lower().strip()

        return self.BROWSERS.get(name)