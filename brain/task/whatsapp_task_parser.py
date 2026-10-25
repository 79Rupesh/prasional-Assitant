"""Parse an explicit file-to-contact WhatsApp send request."""

import re


class WhatsAppTaskParser:
    PATTERNS = (
        re.compile(
            r"^send\s+(?:the\s+)?(?:file\s+)?(.+?)\s+to\s+(.+?)\s+(?:on|via)\s+whatsapp[.!?]*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^whatsapp\s+send\s+(?:the\s+)?(?:file\s+)?(.+?)\s+to\s+(.+?)[.!?]*$",
            re.IGNORECASE,
        ),
    )

    def parse(self, text: str) -> dict:
        value = (text or "").strip()
        for pattern in self.PATTERNS:
            match = pattern.fullmatch(value)
            if match:
                return {
                    "operation": "send_file",
                    "target": match.group(1).strip(),
                    "recipient": match.group(2).strip(),
                }
        return {"operation": "unknown", "target": "", "recipient": ""}
