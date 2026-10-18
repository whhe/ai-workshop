"""Regression checks for text extraction and explicit depth truncation."""

import unittest
import warnings

from transformer import extract_text_from_alidocs


class TextExtractionTests(unittest.TestCase):
    @staticmethod
    def nested_text(depth: int) -> dict[str, object]:
        node: dict[str, object] = {"text": "Deep text"}
        for _ in range(depth):
            node = {"children": node}
        return node

    def test_text_order_and_explicit_fields_are_preserved(self) -> None:
        document = {
            "text": "Root text",
            "t": "Secondary text",
            "children": [{"text": "Child text"}, "Bare visible text"],
        }
        self.assertEqual(
            extract_text_from_alidocs(document),
            ["Root text", "Secondary text", "Child text", "Bare visible text"],
        )

    def test_default_depth_boundary_reports_truncation_once(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(
                extract_text_from_alidocs(self.nested_text(25)), ["Deep text"]
            )
            self.assertEqual(caught, [])
            self.assertEqual(
                extract_text_from_alidocs(
                    [self.nested_text(25), self.nested_text(25)]
                ),
                [],
            )
        self.assertEqual(len(caught), 1)
        self.assertIs(caught[0].category, RuntimeWarning)
        self.assertIn("max_depth=25", str(caught[0].message))

    def test_configured_depth_recovers_deep_text_without_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(
                extract_text_from_alidocs(self.nested_text(30), max_depth=30),
                ["Deep text"],
            )
        self.assertEqual(caught, [])

    def test_starting_depth_remains_supported(self) -> None:
        self.assertEqual(
            extract_text_from_alidocs({"text": "Deep text"}, 25), ["Deep text"]
        )
        with self.assertWarns(RuntimeWarning):
            self.assertEqual(
                extract_text_from_alidocs({"text": "Deep text"}, 26), []
            )
        self.assertEqual(
            extract_text_from_alidocs({"text": "Deep text"}, 26, max_depth=26),
            ["Deep text"],
        )

    def test_negative_depth_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            extract_text_from_alidocs({"text": "Deep text"}, max_depth=-1)


if __name__ == "__main__":
    unittest.main()
