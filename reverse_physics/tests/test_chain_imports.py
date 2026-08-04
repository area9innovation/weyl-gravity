"""Falsification tests for the cross-chain import discipline.

The four conditions replace a blanket ban, so the tests have to show that they
actually bite -- a discipline that cannot reject anything is worse than the ban
it replaced, because it looks like a safeguard.
"""

from __future__ import annotations

import json
import os
import unittest

from reverse_physics.chain_imports import (
    CANNOT_SUPPORT,
    CERT_PATH,
    IMPORTS,
    TAGS,
    build,
    check_tags_travel,
)

_CERT = None


def cert():
    global _CERT
    if _CERT is None:
        _CERT = build()
    return _CERT


class TestTheConditionsHold(unittest.TestCase):
    def test_all_checks_pass(self):
        self.assertTrue(cert()["checks"]["ok"])
        self.assertEqual(cert()["checks"]["failures"], [])

    def test_c1_the_scan_actually_ran(self):
        """A scan that silently failed would report zero violations."""
        c = cert()["no_cycles"]
        self.assertTrue(c["ran"])
        self.assertGreater(c["files_scanned_citing_this_stream"], 20,
                           "the scan found almost nothing -- it probably broke")

    def test_c1_the_only_outside_references_are_coordination(self):
        c = cert()["no_cycles"]
        self.assertEqual(c["violations"], [])
        self.assertGreater(c["coordination_references"], 0,
                           "planning/ should reference the stream; if it does "
                           "not, the exclusion is untested")

    def test_c3_every_import_is_pinned(self):
        self.assertEqual(len(cert()["pins"]), len(IMPORTS))

    def test_c4_every_import_is_middle_column_with_a_boundary(self):
        for imp in IMPORTS:
            self.assertEqual(imp["column"], "GEOMETRY", imp["path"])
            self.assertTrue(imp["boundary"], imp["path"])

    def test_tag_vocabulary_is_closed(self):
        for imp in IMPORTS:
            for t in imp["source_tags"]:
                self.assertIn(t, TAGS, imp["path"])


class TestTheDisciplineBites(unittest.TestCase):
    """If none of these reject, the conditions are decoration."""

    def test_c2_rejects_a_lorentzian_claim_on_reduced_mode_inputs(self):
        """The programme's explicit prohibition, exercised."""
        result = check_tags_travel({"LORENTZIAN-CAUSAL"})
        self.assertTrue(result["violations"],
                        "a LORENTZIAN-CAUSAL claim was allowed to rest on "
                        "REDUCED-MODE inputs")

    def test_c2_permits_what_the_stream_actually_claims(self):
        claimed = set(cert()["tags"]["consumer_tags"])
        self.assertTrue(claimed, "the stream claims no tags at all?")
        self.assertNotIn("LORENTZIAN-CAUSAL", claimed,
                         "this stream must not claim LORENTZIAN-CAUSAL")
        self.assertEqual(check_tags_travel(claimed)["violations"], [])

    def test_the_prohibition_table_is_not_empty(self):
        self.assertIn("LORENTZIAN-CAUSAL", CANNOT_SUPPORT)
        self.assertIn("REDUCED-MODE", CANNOT_SUPPORT["LORENTZIAN-CAUSAL"])
        self.assertIn("EUCLIDEAN-SPECTRAL", CANNOT_SUPPORT["LORENTZIAN-CAUSAL"])
        self.assertIn("UNDECLARED", CANNOT_SUPPORT["LORENTZIAN-CAUSAL"])


class TestUndeclaredSourcesAreSurfaced(unittest.TestCase):
    def test_they_are_listed_not_silently_downgraded(self):
        und = cert()["undeclared_sources"]
        self.assertTrue(und, "no UNDECLARED sources -- but two are known")
        for path in und:
            imp = next(i for i in IMPORTS if i["path"] == path)
            self.assertEqual(imp["source_tags"], ["UNDECLARED"])
            self.assertTrue(imp["boundary"])

    def test_nothing_tagged_may_rest_on_them(self):
        self.assertIn("UNDECLARED", CANNOT_SUPPORT["LORENTZIAN-CAUSAL"])


class TestItRecordsWhatItReplaced(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_the_old_rule_and_why_it_was_over_broad_are_recorded(self):
        r = self.disk["replaces"]
        self.assertIn("vice versa", r["old_rule"].lower())
        self.assertIn("cycle", r["why_it_was_over_broad"].lower())

    def test_what_is_preserved_is_stated(self):
        self.assertIn("audits the programme from outside",
                      self.disk["replaces"]["what_is_preserved"])

    def test_it_does_not_claim_the_imports_are_correct(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("not the content", joined)
        self.assertIn("re-run", joined)

    def test_the_readme_states_the_four_conditions(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        with open(os.path.join(root, "reverse_physics", "README.md")) as fh:
            text = fh.read()
        for c in ("**C1**", "**C2**", "**C3**", "**C4**"):
            self.assertIn(c, text)
        self.assertIn("chain_imports", text)


if __name__ == "__main__":
    unittest.main()
