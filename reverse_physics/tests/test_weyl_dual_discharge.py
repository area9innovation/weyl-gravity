"""Fast invariant rail for the Weyl dual discharge.

The exact discharge itself takes minutes (sympy over four metric/signature
pairs plus three convention controls), so it is NOT run here -- the repository's
test-tier rule says to split a fast invariant rail from the expensive
exhaustive certificate rather than normalise a slow commit loop.  The exhaustive
rail is

    PYTHONPATH=. python3 -m reverse_physics.weyl_dual_discharge --check

What these tests do instead is guard the EMITTED certificate against the ways
it can quietly stop meaning anything:

  * a row silently flipping to False,
  * a negative control silently starting to pass (which would mean the
    convention checks no longer discriminate),
  * G6 being satisfied only on Ricci-flat metrics, where it is VACUOUS because
    Riem = C identically -- the specific trap the work item flags,
  * the Lorentzian rows quietly adopting the Euclidean form of G8,
  * the pinned curvature engine or hodge conventions drifting underneath the
    certificate without it being regenerated.

The last is why `inputs` carries content hashes: an unchanged, content-addressed
input may be checked by its hash instead of rebuilding the chain.
"""

from __future__ import annotations

import hashlib
import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_WEYL_DUAL_DISCHARGE_V1.json")

VISIBILITY_FLAGS = {"C2_is_nonzero", "P_is_nonzero", "ricci_is_nonzero",
                    "G6_is_non_vacuous_here"}


def load():
    with open(CERT) as fh:
        return json.load(fh)


class TestCertificateIsSound(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_overall_result_and_no_failures(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])

    def test_every_substantive_row_check_is_true(self):
        for r in self.cert["rows"]:
            for k, v in r.items():
                if isinstance(v, bool) and k not in VISIBILITY_FLAGS:
                    self.assertTrue(v, "%s/%s: %s is False"
                                    % (r["metric"], r["signature"], k))

    def test_all_negative_controls_rejected(self):
        controls = self.cert["negative_controls"]
        self.assertTrue(controls)
        for c in controls:
            self.assertTrue(c["rejected"],
                            "control no longer discriminates: %s" % c["control"])

    def test_star_square_sign_matches_hodge_convention(self):
        want = {"EUCLIDEAN": 1, "LORENTZIAN": -1}
        for r in self.cert["rows"]:
            self.assertEqual(r["star_square_sign"], want[r["signature"]])
            self.assertTrue(r["star_square_matches_hodge"])


class TestNonDegeneracy(unittest.TestCase):
    """The checks that stop the discharge from being satisfied by zeros."""

    def setUp(self):
        self.cert = load()

    def test_the_dual_is_visible_somewhere(self):
        self.assertTrue([r for r in self.cert["rows"] if r["P_is_nonzero"]],
                        "P = 0 everywhere: every G8 check would be vacuous")

    def test_g6_is_carried_by_a_non_ricci_flat_metric(self):
        carriers = [r for r in self.cert["rows"]
                    if r["ricci_is_nonzero"]
                    and r["G6_pontryagin_depends_only_on_weyl"]]
        self.assertTrue(carriers,
                        "G6 holds only where Ric = 0, i.e. where Riem = C and "
                        "the identity is vacuous")
        self.assertEqual(
            sorted("%s/%s" % (r["metric"], r["signature"]) for r in carriers),
            sorted(self.cert["non_degeneracy"]
                   ["metrics_where_G6_is_non_vacuous"]))

    def test_vacuum_rows_are_marked_vacuous_rather_than_counted(self):
        """A Ricci-flat row must NOT advertise itself as supporting G6."""
        for r in self.cert["rows"]:
            if not r["ricci_is_nonzero"]:
                self.assertFalse(r["G6_is_non_vacuous_here"])


class TestSignatureBoundary(unittest.TestCase):
    """G8 is two different statements; neither may absorb the other."""

    def setUp(self):
        self.cert = load()

    def test_lorentzian_rows_use_the_complex_form(self):
        rows = [r for r in self.cert["rows"] if r["signature"] == "LORENTZIAN"]
        self.assertTrue(rows)
        for r in rows:
            self.assertTrue(r["G8_lorentzian_Wplus_sq_eq_C2_minus_iP_over_2"])
            self.assertTrue(r["G8_lorentzian_Wminus_sq_eq_C2_plus_iP_over_2"])
            self.assertNotIn("G8_euclidean_Wplus_sq_eq_C2_plus_P_over_2", r)

    def test_the_textbook_form_is_checked_false_in_lorentzian_signature(self):
        for r in self.cert["rows"]:
            if r["signature"] == "LORENTZIAN":
                self.assertTrue(
                    r["G8_euclidean_form_is_false_in_lorentzian_signature"],
                    "the Euclidean form must be actively refuted here, not "
                    "merely omitted")

    def test_euclidean_rows_use_the_real_form(self):
        rows = [r for r in self.cert["rows"] if r["signature"] == "EUCLIDEAN"]
        self.assertTrue(rows)
        for r in rows:
            self.assertTrue(r["G8_euclidean_Wplus_sq_eq_C2_plus_P_over_2"])
            self.assertTrue(r["G8_euclidean_Wminus_sq_eq_C2_minus_P_over_2"])


class TestProvenance(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_pinned_inputs_have_not_drifted(self):
        for rel, want in self.cert["inputs"].items():
            path = os.path.join(REPO_ROOT, rel)
            self.assertTrue(os.path.exists(path), "missing input %s" % rel)
            with open(path, "rb") as fh:
                got = hashlib.sha256(fh.read()).hexdigest()
            self.assertEqual(got, want,
                             "%s changed; regenerate the certificate with "
                             "--emit rather than trusting it" % rel)

    def test_every_citation_resolves_and_states_a_boundary(self):
        for c in self.cert["citations"]:
            self.assertTrue(c["boundary"],
                            "%s cites without a boundary" % c["entry"])
            for s in c["sources"]:
                self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, s)),
                                "%s cites missing %s" % (c["entry"], s))

    def test_claim_boundary_is_declared(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("discharge", joined)
        self.assertIn("global triviality", joined)
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])


if __name__ == "__main__":
    unittest.main()
