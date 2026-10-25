"""Normalize a small set of clear Hindi desktop commands for task routing."""

import re


TARGETS = {
    "क्रोम": "Chrome",
    "गूगल क्रोम": "Chrome",
    "एज": "Edge",
    "माइक्रोसॉफ्ट एज": "Edge",
    "व्हाट्सएप": "WhatsApp",
    "वॉट्सऐप": "WhatsApp",
    "व्हाट्स ऐप": "WhatsApp",
    "व्हाट्सएप डेस्कटॉप": "WhatsApp",
    "यूट्यूब": "YouTube",
    "कैलकुलेटर": "Calculator",
    "नोटपैड": "Notepad",
    "फाइल एक्सप्लोरर": "File Explorer",
    "डेस्कटॉप": "Desktop",
    "डाउनलोड": "Downloads",
    "डाउनलोड्स": "Downloads",
    "डॉक्यूमेंट्स": "Documents",
}


def normalize_voice_command(text: str) -> str:
    """Translate unambiguous Hindi open/close/search/play phrases to known verbs."""
    value = (text or "").strip()
    if not value:
        return value

    cleaned = re.sub(r"[,.!?।]+$", "", value).strip()
    lowered = cleaned.lower()

    for source, target in sorted(TARGETS.items(), key=lambda item: len(item[0]), reverse=True):
        cleaned = re.sub(re.escape(source), target, cleaned, flags=re.IGNORECASE)
        lowered = cleaned.lower()

    copy_match = re.fullmatch(
        r"(.+?)\s+को\s+(?:desktop|डेस्कटॉप)\s+पर\s+(?:copy|कॉपी)\s+(?:करो|कर\s+दो)",
        lowered,
        flags=re.IGNORECASE,
    )
    if copy_match:
        return f"copy {copy_match.group(1).strip()} to Desktop"

    send_match = re.fullmatch(
        r"(?:whatsapp|whatsapp\s+पर)\s+(.+?)\s+को\s+(.+?)\s+(?:भेजो|भेज\s+दो)",
        lowered,
        flags=re.IGNORECASE,
    )
    if send_match:
        recipient, file_name = send_match.groups()
        return f"send {file_name.strip()} to {recipient.strip()} on WhatsApp"

    patterns = (
        (r"^(?:कृपया\s+)?(.+?)\s+(?:खोलो|खोल\s+दो|ओपन\s+करो)$", "open"),
        (r"^(?:कृपया\s+)?(?:खोलो|खोल\s+दो)\s+(.+)$", "open"),
        (r"^(?:कृपया\s+)?(.+?)\s+(?:बंद\s+करो|बंद\s+कर\s+दो)$", "close"),
        (r"^(?:गूगल\s+में|इंटरनेट\s+पर)\s+(.+?)\s+(?:खोजो|सर्च\s+करो)$", "search"),
        (r"^(?:youtube\s+पर\s+)?(.+?)\s+(?:चलाओ|बजाओ)$", "play"),
    )
    for pattern, verb in patterns:
        match = re.fullmatch(pattern, lowered, flags=re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            if verb == "play" and "youtube" not in target:
                return f"play {target} on YouTube"
            return f"{verb} {target}"

    return cleaned
