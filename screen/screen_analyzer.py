import json
import subprocess

from screen.screen_analyzer_provider import ScreenAnalyzerProvider






class ScreenAnalyzer(ScreenAnalyzerProvider):

    # Screenshot physical resolution
    SCREEN_WIDTH = 3420
    SCREEN_HEIGHT = 2224

    # Retina scaling: screenshot pixels -> mouse coordinates
    MOUSE_SCALE_X = 0.5
    MOUSE_SCALE_Y = 0.5

    def find_text(self, image_path: str, target: str) -> dict:
        result = self.analyze(image_path)

        if result["status"] != "success":
            return result

        target = target.lower().strip()

        elements = result["elements"]

        # Find all exact matches
        exact_matches = [
            element
            for element in elements
            if element["text"].lower().strip() == target
        ]

        # Find all partial matches if no exact match
        if not exact_matches:
            exact_matches = [
                element
                for element in elements
                if target in element["text"].lower().strip()
            ]

        if not exact_matches:
            return {
                "status": "not_found",
                "text": target
            }

        # If only one match exists, use it
        if len(exact_matches) == 1:
            best = exact_matches[0]

        else:
            # Score each candidate using nearby OCR context
            scored = []

            for candidate in exact_matches:

                cx = (
                    candidate["pixel_x"]
                    + candidate["pixel_width"] // 2
                )

                cy = (
                    candidate["pixel_y"]
                    + candidate["pixel_height"] // 2
                )

                score = 0

                for other in elements:

                    if other is candidate:
                        continue

                    ox = (
                        other["pixel_x"]
                        + other["pixel_width"] // 2
                    )

                    oy = (
                        other["pixel_y"]
                        + other["pixel_height"] // 2
                    )

                    distance_x = abs(cx - ox)
                    distance_y = abs(cy - oy)

                    # Nearby elements are useful context
                    if distance_x < 500 and distance_y < 300:

                        other_text = (
                            other["text"]
                            .lower()
                            .strip()
                        )

                        # URL near a text candidate is strong
                        # evidence that this is a clickable result.
                        if (
                            other_text.startswith("http://")
                            or other_text.startswith("https://")
                        ):
                            # URL directly above the candidate is strong evidence
                            # that the candidate is the clickable result title.

                            url_bottom = other["pixel_y"] + other["pixel_height"]

                            candidate_top = candidate["pixel_y"]

                            # URL is above candidate
                            if 0 <= candidate_top - url_bottom <= 100:
                                score += 15

                            # Horizontal overlap
                            candidate_left = candidate["pixel_x"]
                            candidate_right = (
                                candidate["pixel_x"]
                                + candidate["pixel_width"]
                            )

                            other_left = other["pixel_x"]
                            other_right = (
                                other["pixel_x"]
                                + other["pixel_width"]
                            )

                            if (
                                candidate_left <= other_right
                                and candidate_right >= other_left
                            ):
                                score += 10

                        # Search-result style contextual words
                        if any(word in other_text for word in [
                            "official",
                            "website",
                            "home",
                            "search",
                            "more results"
                        ]):
                            score += 2

                        # Strong penalty for text far below candidate
                        if distance_y > 250:
                            score -= 1

                scored.append((score, candidate))

            # Highest contextual score wins
            scored.sort(
                key=lambda item: item[0],
                reverse=True
            )

            best = scored[0][1]

        center_x = (
            best["pixel_x"]
            + best["pixel_width"] // 2
        )

        center_y = (
            best["pixel_y"]
            + best["pixel_height"] // 2
        )

        mouse_x = int(center_x * self.MOUSE_SCALE_X)
        mouse_y = int(center_y * self.MOUSE_SCALE_Y)

        return {
            "status": "success",
            "text": best["text"],
            "screenshot_x": center_x,
            "screenshot_y": center_y,
            "x": mouse_x,
            "y": mouse_y
    }

    def analyze(self, image_path: str) -> dict:
        # The bundled vision_ocr executable is a macOS/Swift artifact. On Windows,
        # use pytesseract if both the Python package and Tesseract OCR are installed.
        import os
        if os.name == "nt":
            try:
                from PIL import Image
                import pytesseract
                data = pytesseract.image_to_data(Image.open(image_path), output_type=pytesseract.Output.DICT)
                width, height = Image.open(image_path).size
                elements = []
                for i, value in enumerate(data.get("text", [])):
                    value = value.strip()
                    if not value:
                        continue
                    x, y = int(data["left"][i]), int(data["top"][i])
                    w, h = int(data["width"][i]), int(data["height"][i])
                    elements.append({"text": value, "pixel_x": x, "pixel_y": y, "pixel_width": w, "pixel_height": h})
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT = width, height
                self.MOUSE_SCALE_X = self.MOUSE_SCALE_Y = 1.0
                return {"status": "success", "elements": elements}
            except Exception as error:
                return {"status": "error", "message": "Windows screen OCR needs Pillow, pytesseract, and the Tesseract OCR application installed: " + str(error)}
        try:
            result = subprocess.run(
                ["./screen/vision_ocr", image_path],
                capture_output=True,
                text=True,
                check=True
            )

            observations = json.loads(result.stdout)

            for element in observations:
                # Vision normalized coordinates -> screenshot pixels
                element["pixel_x"] = int(
                    element["x"] * self.SCREEN_WIDTH
                )

                element["pixel_y"] = int(
                    (1 - element["y"] - element["height"])
                    * self.SCREEN_HEIGHT
                )

                element["pixel_width"] = int(
                    element["width"] * self.SCREEN_WIDTH
                )

                element["pixel_height"] = int(
                    element["height"] * self.SCREEN_HEIGHT
                )

            return {
                "status": "success",
                "elements": observations
            }

        except subprocess.CalledProcessError as error:
            return {
                "status": "error",
                "message": error.stderr
            }

        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid OCR output."
            }