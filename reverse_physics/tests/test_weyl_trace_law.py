"""Fast invariant rail for the N2 trace-law discharge.

The exact discharge takes minutes (three metrics, covariant second derivatives
of the Ricci tensor, plus four convention controls), so the exhaustive rail

    PYTHONPATH=. python3 -m reverse_physics.weyl_trace_law --check

is deliberately not run here.  These tests guard the EMITTED certificate against
the ways it can quietly stop meaning anything -- in particular the one that
already bit this stream once, a check that passes because everything in it is
zero.
"""

from __future__ import annotations

import hashlib
import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_WEYL_TRACE_LAW_V1.json")

VISIBILITY = {"box_R_is_nonzero", "weyl_is_nonzero", "bach_is_nonzero",
              "bach_cross_check_is_non_vacuous", "witnesses_nothing"}


def load():
    with open(CERT) as fh:
        return json.load(fh)


class TestCertificateIsSound(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_no_failures(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])
        self.assertEqual(self.cert["checks"]["passed"],
                         self.cert["checks"]["total"])

    def test_every_substantive_check_is_true(self):
        for r in self.cert["rows"]:
            for k, v in r.items():
                if isinstance(v, bool) and k not in VISIBILITY:
                    self.assertTrue(v, "%s: %s is False" % (r["metric"], k))

    def test_all_negative_controls_rejected(self):
        self.assertTrue(self.cert["negative_controls"])
        for c in self.cert["negative_controls"]:
            self.assertTrue(c["rejected"], "control stopped discriminating: %s"
                            % c["control"])

    def test_trace_law_by_probe_holds_everywhere(self):
        for r in self.cert["rows"]:
            for probe, ok in r["trace_law_by_probe"].items():
                self.assertTrue(ok, "%s: probe %s" % (r["metric"], probe))


class TestTheResultIsTheOneClaimed(unittest.TestCase):
    """The numbers N2 turns on, pinned so they cannot drift silently."""

    def setUp(self):
        self.cert = load()

    def test_the_multiple_is_two_and_nonzero(self):
        res = self.cert["result"]
        self.assertEqual(res["multiple"], 2)
        self.assertTrue(res["multiple_is_nonzero"],
                        "a zero multiple would make RP-TRACELESS => RP-WEYL "
                        "vacuous, which is the whole point of N2")

    def test_the_weyl_functional_matches_the_classification(self):
        self.assertEqual(self.cert["result"]["weyl_functional"], "a + b + 3c")
        self.assertEqual(self.cert["result"]["kernel_of_trace_map"],
                         "span{C^2, E4}")

    def test_the_bach_factor_is_four_as_the_nariai_check_says(self):
        self.assertEqual(self.cert["result"]["bach_factor"], 4)
        carriers = [r for r in self.cert["rows"]
                    if r.get("bach_cross_check_is_non_vacuous")]
        self.assertTrue(carriers, "the Bach cross-check is vacuous everywhere")
        for r in carriers:
            self.assertTrue(r["E_C2_equals_4_Bach"])
            self.assertEqual(r["bach_factor_computed"], ["4"],
                             "the factor must be a single constant across all "
                             "nonzero components")

    def test_weyl_invariant_directions_are_traceless(self):
        for r in self.cert["rows"]:
            self.assertTrue(r["C2_direction_is_traceless"])
            self.assertTrue(r["E4_direction_is_traceless"])


class TestNonDegeneracy(unittest.TestCase):
    """A check satisfied by zeros is not a check."""

    def setUp(self):
        self.cert = load()

    def test_the_trace_law_is_carried_by_a_metric_with_box_R_nonzero(self):
        carriers = [r for r in self.cert["rows"] if r["box_R_is_nonzero"]]
        self.assertTrue(carriers,
                        "box R = 0 everywhere: both sides of the trace law "
                        "vanish identically and it says nothing")
        self.assertEqual(
            sorted(r["metric"] for r in carriers),
            sorted(self.cert["non_degeneracy"]["metrics_with_box_R_nonzero"]))

    def test_the_bach_cross_check_is_carried_somewhere(self):
        self.assertTrue(
            self.cert["non_degeneracy"]["metrics_carrying_the_bach_cross_check"])

    def test_a_metric_that_witnesses_nothing_is_present_and_labelled(self):
        """Schwarzschild is in the set precisely because it can witness
        nothing; if it ever stopped being labelled that way, the labelling
        logic would have broken."""
        nothing = self.cert["non_degeneracy"]["metrics_that_witness_nothing"]
        self.assertIn("schwarzschild", nothing)
        for r in self.cert["rows"]:
            if r["metric"] in nothing:
                self.assertFalse(r["box_R_is_nonzero"])
                self.assertFalse(r["bach_is_nonzero"])

    def test_lanczos_free_subspace_is_verified_separately(self):
        for r in self.cert["rows"]:
            self.assertIn("trace_law_holds_without_lanczos_input", r)
            self.assertTrue(r["trace_law_holds_without_lanczos_input"])


class TestProvenanceAndBoundary(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_pinned_engine_has_not_drifted(self):
        for rel, want in self.cert["inputs"].items():
            path = os.path.join(REPO_ROOT, rel)
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), want,
                                 "%s changed; regenerate with --emit" % rel)

    def test_imported_formulas_are_declared_imported(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("imported", joined)
        self.assertIn("lanczos", joined)
        self.assertIn("discharge", joined)

    def test_the_quantum_boundary_is_declared(self):
        """N2 is often phrased as being about the trace ANOMALY.  What is
        established is the classical variational identity, and the certificate
        must keep saying so."""
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("quantum", joined)
        self.assertIn("beta function", joined)
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])


if __name__ == "__main__":
    unittest.main()
