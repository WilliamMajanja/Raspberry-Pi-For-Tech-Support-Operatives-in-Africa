import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from fieldkit.coffee_snake import edition_id, generate, make_seed, render_ascii, render_svg


class CoffeeSnakeTests(unittest.TestCase):
    def test_seeded_art_is_reproducible_and_changes_between_seeds(self):
        seed_a = make_seed("01" * 32)
        seed_b = make_seed("02" * 32)
        self.assertEqual(render_ascii(seed_a), render_ascii(seed_a))
        self.assertEqual(render_svg(seed_a), render_svg(seed_a))
        self.assertNotEqual(edition_id(seed_a), edition_id(seed_b))
        self.assertNotEqual(render_svg(seed_a), render_svg(seed_b))

    def test_svg_is_well_formed_and_art_names_snake_and_pot(self):
        seed = make_seed("03" * 32)
        svg = render_svg(seed)
        ElementTree.fromstring(svg)
        art = render_ascii(seed)
        self.assertIn("COFFEE", art)
        self.assertIn("POT", art)
        self.assertIn("Edition fingerprint:", art)

    def test_generation_creates_a_complete_variant_directory(self):
        seed = make_seed("04" * 32)
        with tempfile.TemporaryDirectory() as temporary:
            paths = generate(Path(temporary), seed)
            self.assertTrue(all(path.is_file() for path in paths))
            manifest = json.loads(paths[2].read_text(encoding="utf-8"))
            self.assertEqual(manifest["edition_id"], edition_id(seed))
            self.assertEqual(
                manifest["cover_sha256"],
                __import__("hashlib").sha256(paths[1].read_bytes()).hexdigest(),
            )
            with self.assertRaises(FileExistsError):
                generate(Path(temporary), seed)

    def test_seed_must_have_sufficient_entropy_length(self):
        with self.assertRaises(ValueError):
            make_seed("not-hex")
        with self.assertRaises(ValueError):
            make_seed("01")


if __name__ == "__main__":
    unittest.main()
