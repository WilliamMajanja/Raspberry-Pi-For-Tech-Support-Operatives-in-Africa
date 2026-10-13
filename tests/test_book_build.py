import unittest
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.build_books import (
    PROFILE_PRIORITY_PATHS,
    ROOT,
    SOURCE_EXPLANATIONS,
    prioritize_reading_order,
    reading_order,
    rewrite_line_links,
    build_printables_bundle,
    make_source_appendix,
    source_files,
)


class BookBuildTests(unittest.TestCase):
    def test_profile_reorders_pages_without_omitting_or_duplicating_content(self):
        source_order = reading_order()
        for profile, priorities in PROFILE_PRIORITY_PATHS.items():
            with self.subTest(profile=profile):
                personalized = prioritize_reading_order(source_order, profile)
                expected_start = [ROOT / path for path in priorities]
                self.assertEqual(personalized[: len(expected_start)], expected_start)
                self.assertEqual(set(personalized), set(source_order))
                self.assertEqual(len(personalized), len(source_order))

    def test_unknown_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown edition profile"):
            prioritize_reading_order(reading_order(), "unknown")

    def test_local_svg_images_are_rebased_for_pdf_and_epub_assets(self):
        source = ROOT / "Raspberry Pi Field Support" / "Secure_Baseline_and_Maintenance.md"
        rewritten = rewrite_line_links(
            "![Support loop](../illustrations/field-support-loop.svg)\n",
            source,
            {},
            {},
        )
        self.assertEqual(
            rewritten,
            "![Support loop](illustrations/field-support-loop.svg)\n",
        )

    def test_printables_bundle_contains_native_a4_template_and_worksheets(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = build_printables_bundle(Path(temporary))
            with zipfile.ZipFile(bundle) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                self.assertIn("printables/Coffee_Pot_Snake_Paper_Cryptex.svg", names)
                self.assertIn("printables/Participant_FieldKit_Worksheet.md", names)
                root = ET.fromstring(archive.read("printables/Coffee_Pot_Snake_Paper_Cryptex.svg"))
                self.assertEqual(root.attrib["width"], "210mm")
                self.assertEqual(root.attrib["height"], "297mm")

    def test_every_source_listing_has_a_purpose_and_data_flow_explanation(self):
        relatives = {path.relative_to(ROOT).as_posix() for path in source_files()}
        self.assertEqual(relatives - set(SOURCE_EXPLANATIONS), set())
        with tempfile.TemporaryDirectory() as temporary:
            appendix = make_source_appendix(Path(temporary)).read_text(encoding="utf-8")
        self.assertIn("## Component flow", appendix)
        for relative in relatives:
            with self.subTest(source=relative):
                section = appendix.split(f"## `{relative}`\n\n", 1)[1]
                self.assertIn(SOURCE_EXPLANATIONS[relative], section)
                self.assertLess(section.index(SOURCE_EXPLANATIONS[relative]), section.index("**Source listing:**"))


if __name__ == "__main__":
    unittest.main()
