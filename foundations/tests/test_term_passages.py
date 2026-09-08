import unittest
from foundations.term_passages import render
from foundations.reading_site import display_label

class TermPassagesTests(unittest.TestCase):
    def test_markdown_and_highlight(self):
        result=render('A **bold** term and `code`.',4,8)
        self.assertIn('<strong><mark>bold</mark></strong>',result)
        self.assertIn('<code>code</code>',result)
    def test_no_active_markup_or_links(self):
        result=render('<script>alert(1)</script> [bad](javascript:alert(1))')
        self.assertNotIn('<script',result)
        self.assertNotIn('<a',result)
    def test_case_presentation_preserves_acronyms(self):
        self.assertEqual(display_label({'label':'LOCAL-ALGEBRAIC'}),'Local-algebraic')
        self.assertEqual(display_label({'label':'ACA₀'}),'ACA₀')
