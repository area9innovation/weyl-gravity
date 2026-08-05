"""Cross-cutting coherence of the reverse-physics record.

A retraction is not finished when the retracted certificate is labelled.  The
withdrawn claim survives in every OTHER document that asserted it, and those are
the ones nobody re-reads.  After
REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1 was withdrawn, four documents still
stated it as fact -- including the report whose TITLE was the claim, and a
forward pointer inside a STANDING certificate.  None of them were the retracted
certificate itself.

Separately: every certificate quotes the score of the Forge gate it rests on.
Four gates gained checks during the audit, which left eighteen stale quotes.
Some of those live in preserved-verbatim sections where the number was right
when written and must NOT be rewritten -- but a verification block printing a
score you will not reproduce is a defect either way, so those carry a note.

These tests are the rail for both failure modes.
"""

from __future__ import annotations

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
RP = os.path.join(REPO_ROOT, "reverse_physics")
CERTS = os.path.join(RP, "certificates")
REPORTS = os.path.join(RP, "reports")

# The Forge gates this stream cites, and their CURRENT expect values.  Update
# together with the gate, never separately.
GATE_SCORES = {
    "curvature_invariants_parity_gate": "22/22",
    "curvature_invariants_d6_gate": "27/27",
    "curvature_invariants_deriv_gate": "40/40",
    "curvature_euler_gate": "15/15",
    "curvature_coord_scalar_control_gate": "19/19",
    "curvature_parity_enumeration_gate": "12/12",
    "curvature_parity_field_equations_gate": "6/6",
    "curvature_covderiv_gate": "23/23",
    "curvature_general_inverse_gate": "20/20",
    "curvature_invariants_d4_gate": "25/25",
    "curvature_gate": "18/18",
    "jet_mul_gate": "14/14",
}

# Documents that preserve superseded text verbatim.  Their scores are as-issued
# and are deliberately not rewritten; they must instead carry a note saying so.
PRESERVED = {
    "REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1.json",
    "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json",
    "parity-field-equations.md",
    "parity-conformal-count.md",
}

WITHDRAWN = "REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1"


def docs():
    for base in (CERTS, REPORTS):
        for name in sorted(os.listdir(base)):
            if name.endswith((".json", ".md")):
                path = os.path.join(base, name)
                with open(path) as fh:
                    yield name, path, fh.read()


class TestTheWithdrawnClaimIsNotAssertedAnywhere(unittest.TestCase):
    """Every document that mentions the withdrawn certificate must mark it, not
    repeat it."""

    def test_every_mention_is_marked(self):
        unmarked = []
        for name, path, text in docs():
            if WITHDRAWN not in text and "parity-field-equations" not in text:
                continue
            marked = any(w in text for w in
                         ("RETRACTED", "retracted", "withdrawn", "WITHDRAWN"))
            if not marked:
                unmarked.append(name)
        self.assertEqual(unmarked, [],
                         f"these cite the withdrawn result without marking it: {unmarked}")

    def test_the_retracted_report_leads_with_the_retraction(self):
        with open(os.path.join(REPORTS, "parity-field-equations.md")) as fh:
            first = fh.readline()
        self.assertIn("RETRACTED", first)

    def test_the_retracted_certificate_is_flagged_before_its_claims(self):
        with open(os.path.join(CERTS, WITHDRAWN + ".json")) as fh:
            keys = list(json.load(fh).keys())
        self.assertEqual(keys[1], "status")
        self.assertLess(keys.index("retraction"), keys.index("establishes"))

    def test_standing_certificates_do_not_assert_it_as_fact(self):
        """The one that actually happened: a forward pointer added to the Euler
        certificate BEFORE the retraction went on asserting the result inside a
        certificate that still stands."""
        with open(os.path.join(CERTS, "REVERSE_PHYSICS_EULER_OPERATOR_V1.json")) as fh:
            euler = json.load(fh)
        a = euler["answered_since"]
        self.assertEqual(list(a.keys())[0], "CORRECTION",
                         "the correction must come first in the block")
        self.assertIn("RETRACTED", a["CORRECTION"])
        self.assertIn("SUPERSEDED", a["the_question_it_was_built_for"])

    def test_the_euler_operator_is_never_swept_up_in_the_retraction(self):
        """It is the instrument, and it was not at fault.  Every place the
        retraction is explained must say so, or the tool gets thrown away with
        the result."""
        with open(os.path.join(CERTS, WITHDRAWN + ".json")) as fh:
            r = json.load(fh)["retraction"]
        self.assertIn("untouched", r["what_survives"])


class TestQuotedGateScoresAreCurrent(unittest.TestCase):
    PAT = re.compile(r'([a-z0-9_]*gate)[^0-9\n]{0,60}?(\d{1,3}/\d{1,3})')

    def test_no_live_document_quotes_a_stale_score(self):
        stale = []
        for name, path, text in docs():
            if name in PRESERVED:
                continue
            for line in text.splitlines():
                for m in self.PAT.finditer(line):
                    gate, score = m.group(1), m.group(2)
                    want = GATE_SCORES.get(gate)
                    if want and score != want:
                        stale.append(f"{name}: {gate} quoted {score}, current {want}")
        self.assertEqual(stale, [], "stale gate scores:\n" + "\n".join(stale))

    def test_preserved_documents_say_their_scores_are_as_issued(self):
        """Not rewritten -- append-only -- but a verification block printing a
        score you will not reproduce is a defect either way."""
        for name in PRESERVED:
            base = CERTS if name.endswith(".json") else REPORTS
            with open(os.path.join(base, name)) as fh:
                text = fh.read()
            self.assertIn("as issued", text,
                          f"{name} preserves stale scores without saying so")

    def test_the_gate_table_here_is_not_empty_and_covers_the_audit(self):
        """A table that silently lost its entries would make the test above
        pass vacuously -- the failure mode this whole stream keeps hitting."""
        self.assertGreaterEqual(len(GATE_SCORES), 12)
        for g in ("curvature_invariants_parity_gate", "curvature_euler_gate",
                  "curvature_parity_enumeration_gate"):
            self.assertIn(g, GATE_SCORES)


class TestTheParityHalfIsNotStillAdvertisedAsOpen(unittest.TestCase):
    """Two parity-EVEN certificates said the parity result 'remains open'.  True
    when written; it has since been answered and then corrected."""

    def test_both_carry_a_forward_pointer(self):
        for name in ("REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1",
                     "REVERSE_PHYSICS_DERIVATIVE_CONFORMAL_COUNT_V1"):
            with open(os.path.join(CERTS, name + ".json")) as fh:
                d = json.load(fh)
            self.assertIn("parity_half_no_longer_open", d, name)
            fwd = d["parity_half_no_longer_open"]
            self.assertIn("CORRECTED", fwd)
            self.assertIn("unaffected", fwd,
                          "it must also say THIS certificate is not implicated")


class TestTheLedgerRestsOnTheRowThatSurvived(unittest.TestCase):
    """RP-PARITY's witness is the D = 4 weight-4 Pontryagin density, which the
    correction leaves alone.  If that ever changes, WEYL_ACTION_V1 is in scope."""

    def test_the_witness_is_the_d4_one(self):
        with open(os.path.join(REPORTS, "WEYL-CHARACTERIZATION.md")) as fh:
            text = fh.read()
        row = [l for l in text.splitlines() if "`RP-PARITY`" in l]
        self.assertTrue(row, "the ledger has no RP-PARITY row")
        self.assertIn("W₊²", row[0])

    def test_the_correction_marks_that_row_unchanged(self):
        with open(os.path.join(CERTS,
                  "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json")) as fh:
            d = json.load(fh)
        rows = d["correction"]["corrected_counts"]
        self.assertIn("UNCHANGED", rows["D4_weight4_pontryagin"])


if __name__ == "__main__":
    unittest.main()
