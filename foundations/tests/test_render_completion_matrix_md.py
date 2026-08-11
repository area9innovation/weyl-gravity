from __future__ import annotations

from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import tempfile
import unittest

from foundations.render_completion_matrix_md import render, main


class CompletionMatrixMarkdownTests(unittest.TestCase):
    def test_render_is_deterministic(self):
        self.assertEqual(render(), render())

    def test_dimensions_are_visible(self):
        text = render()
        self.assertIn("16 programmes × 6 axes = **96 cells**", text)
        self.assertIn("**9 rows**, **8 certificates**", text)
        self.assertIn("**25 records**", text)

    def test_coverage_legend_is_plain_language(self):
        text = render()
        for label in ("**Direct**", "**Partial**", "**Adjacent**", "**Not addressed**", "**Not yet classified**"):
            self.assertIn(label, text)
        self.assertIn("It does not mean", text)
        self.assertIn("The full words are printed in every cell", text)
        self.assertNotIn("`D` = direct", text)

    def test_axes_are_explained_as_questions(self):
        text = render()
        self.assertIn("What the six columns ask", text)
        self.assertIn("permitted rules of reasoning", text)
        self.assertIn("Choice, comprehension, or constructive existence", text)

    def test_lifecycle_and_pin_terms_are_explained(self):
        text = render()
        self.assertIn("The status terms have deliberately narrow meanings", text)
        self.assertIn("The **Pin** column reports provenance, not scientific quality", text)

    def test_all_opportunities_are_present(self):
        text = render()
        self.assertEqual(text.count("| `OP-"), 9)

    def test_all_literature_ids_are_present(self):
        text = render()
        for source_id in ("solovay-1970", "blackadar-farah-2026", "heunen-landsman-spitters-2009", "brown-simpson-1986", "grinkevich-1996", "haag-kastler-1964"):
            self.assertIn(source_id, text)

    def test_boundaries_are_rendered(self):
        text = render()
        self.assertIn("Dropping Choice alone does not imply", text)
        self.assertIn("finite replacement for continuum dynamics", text)
        self.assertIn("full Lorentzian off-shell BV propagator", text)

    def test_check_mode_detects_stale_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.md"
            output.write_text("stale")
            with redirect_stderr(StringIO()):
                self.assertEqual(main(["--output", str(output), "--check"]), 1)

    def test_check_mode_accepts_rendered_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.md"
            output.write_text(render(output=output))
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["--output", str(output), "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
