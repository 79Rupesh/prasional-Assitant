class AppTaskParser:

    def parse(self, text: str) -> dict:

        text = text.strip()
        text_lower = text.lower()

        if not text:
            return {
                "operation": "unknown",
                "target": ""
            }

        open_prefixes = [
            "open ",
            "launch ",
            "start "
        ]

        for prefix in open_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                return {
                    "operation": "open",
                    "target": self.clean_target(target)
                }

        close_prefixes = [
            "close ",
            "quit ",
            "exit "
        ]

        for prefix in close_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                return {
                    "operation": "close",
                    "target": self.clean_target(target)
                }

        return {
            "operation": "unknown",
            "target": ""
        }

    def clean_target(self, target: str) -> str:

        target = target.strip()
        target = target.rstrip(".!?")

        words = target.split()

        removable_words = {
            "my",
            "the",
            "a",
            "an"
        }

        while words and words[0].lower() in removable_words:
            words.pop(0)

        target = " ".join(words)

        return target