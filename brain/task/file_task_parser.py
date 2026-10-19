class FileTaskParser:

    def parse(self, text: str) -> dict:

        text = text.strip()
        text_lower = text.lower()

        # FIND
        if text_lower.startswith("find "):
            target = text[5:].strip()

            return {
                "operation": "find",
                "target": self.clean_target(target)
            }

        # OPEN
        if text_lower.startswith("open "):
            target = text[5:].strip()

            return {
                "operation": "open",
                "target": self.clean_target(target)
            }

        # LIST / SHOW
        list_prefixes = [
            "list ",
            "show ",
            "what is in ",
            "what's in "
        ]

        for prefix in list_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                return {
                    "operation": "list",
                    "target": self.clean_target(target)
                }

        # INFO
        info_prefixes = [
            "info ",
            "information about ",
            "details about "
        ]

        for prefix in info_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                return {
                    "operation": "info",
                    "target": self.clean_target(target)
                }

        # CREATE
        create_prefixes = [
            "create file ",
            "create folder ",
            "make file ",
            "make folder "
        ]

        for prefix in create_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                if "folder" in prefix:
                    operation = "create_folder"
                else:
                    operation = "create_file"

                return {
                    "operation": operation,
                    "target": self.clean_target(target)
                }

        # RENAME
                # RENAME
        if text_lower.startswith("rename "):

            command = text[7:].strip()

            parts = command.split(" to ", 1)

            if len(parts) != 2:
                return {
                    "operation": "unknown",
                    "target": ""
                }

            source = self.clean_target(parts[0])
            destination = self.clean_target(parts[1])

            return {
                "operation": "rename",
                "target": source,
                "destination": destination
            }

        # MOVE
                # MOVE
        if text_lower.startswith("move "):

            command = text[5:].strip()

            parts = command.split(" to ", 1)

            if len(parts) != 2:
                return {
                    "operation": "unknown",
                    "target": ""
                }

            source = self.clean_target(parts[0])
            destination = self.clean_target(parts[1])

            return {
                "operation": "move",
                "target": source,
                "destination": destination
            }

        # DELETE
        delete_prefixes = [
            "delete ",
            "remove "
        ]

        for prefix in delete_prefixes:

            if text_lower.startswith(prefix):

                target = text[len(prefix):].strip()

                return {
                    "operation": "delete",
                    "target": self.clean_target(target)
                }

        return {
            "operation": "unknown",
            "target": ""
        }

    def clean_target(self, target: str) -> str:

        target = target.strip()
        target = target.rstrip(".!?")

        prefixes = [
            "my ",
            "the ",
            "a ",
            "an "
        ]

        target_lower = target.lower()

        for prefix in prefixes:

            if target_lower.startswith(prefix):
                target = target[len(prefix):].strip()
                break

        suffixes = [
            " folder",
            " directory",
            " file"
        ]

        target_lower = target.lower()

        for suffix in suffixes:

            if target_lower.endswith(suffix):
                target = target[:-len(suffix)].strip()
                break

        return target