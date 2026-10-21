
import re
from pathlib import Path


class KnowledgeLoader:
    def __init__(self, knowledge_path=None):
        project_root = Path(__file__).resolve().parents[2]

        self.knowledge_path = (
            Path(knowledge_path)
            if knowledge_path
            else project_root / "data" / "ela_knowledge.txt"
        )
        self._knowledge = None
        self._sections = None

    def load(self, force_reload=False):
        if self._knowledge is not None and not force_reload:
            return self._knowledge

        if not self.knowledge_path.is_file():
            raise FileNotFoundError(
                f"Ela knowledge file not found: {self.knowledge_path}"
            )

        content = self.knowledge_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            raise ValueError("Ela knowledge file is empty.")

        self._knowledge = content
        self._sections = self._split_sections(content)
        return self._knowledge

    @staticmethod
    def _split_sections(content):
        sections = []
        current = []

        for line in content.splitlines():
            heading = re.match(
                r"^(?:#{1,3}\s+|\d+\.\s+[A-Z])",
                line.strip()
            )

            if heading and current:
                sections.append("\n".join(current).strip())
                current = []

            current.append(line)

        if current:
            sections.append("\n".join(current).strip())

        return [section for section in sections if section]

    @staticmethod
    def _words(text):
        return set(re.findall(r"[a-zA-Z0-9_'-]+", text.lower()))

    def get_relevant_sections(self, query, max_chars=6000):
        self.load()

        query_words = {
            word for word in self._words(query)
            if len(word) > 2
        }

        if not query_words:
            return ""

        scored = []

        for index, section in enumerate(self._sections):
            lines = section.splitlines()
            heading = lines[0] if lines else ""
            heading_words = self._words(heading)
            section_words = self._words(section)

            score = len(query_words & section_words)
            score += 2 * len(query_words & heading_words)

            if score:
                scored.append((score, index, section))

        scored.sort(key=lambda item: (-item[0], item[1]))

        selected = []
        used_chars = 0

        for _, _, section in scored:
            remaining = max_chars - used_chars

            if remaining <= 0:
                break

            if len(section) > remaining:
                continue

            selected.append(section)
            used_chars += len(section) + 2

        return "\n\n".join(selected)
