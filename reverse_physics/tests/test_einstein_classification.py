"""Fast invariant rail for the D = 4 Lovelock classification.

The derivation takes minutes (symbolic divergences over three metrics), so the
exhaustive rail

    PYTHONPATH=. python3 -m reverse_physics.einstein_classification --check

is not run here.  These tests guard the emitted certificate against the ways it
could stop meaning anything -- and in particular against the two that already
bit this module once: a check that fails for the wrong reason, and a result
established only where everything vanishes.
"""

from __future__ import annotations

import hashlib
import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1.json")

LANCZOS = {"RmanbRab": "-4", "RmaRan": "-4", "R_Rmn": "2",
           "g_ric2": "2", "g_R2": "-1/2",
           "boxRmn": "0", "ddR": "0", "g_boxR": "0"}


def load():
    with open(CERT) as fh:
        return json.load(fh)


class TestTheDerivation(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.d = self.cert["derivation"]

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_the_system_is_overdetermined(self):
        """Eight unknowns; fewer than eight equations could not pin anything."""
        self.assertGreaterEqual(self.d["equations_from_identical_vanishing"], 8)
        self.assertEqual(len(self.d["unknown_structures"]), 8)

    def test_divergence_freedom_alone_leaves_exactly_two_parameters(self):
        """Not zero and not more: the residue must be the span of the Ric^2 and
        R^2 variations, which is two-dimensional.  A different number would
        mean the structure basis or the equations are wrong."""
        self.assertEqual(
            self.d["residual_family_dimension_without_second_order"], 2)

    def test_second_order_gives_a_unique_tensor(self):
        self.assertEqual(self.d["solutions_with_second_order"], 1)

    def test_the_derived_tensor_is_lanczos(self):
        self.assertTrue(self.d["matches_lanczos"])
        self.assertEqual(self.d["derived_coefficients"], LANCZOS)

    def test_the_reference_is_only_a_comparison(self):
        """The Lanczos coefficients must be declared as a comparison target,
        not an input -- otherwise the derivation is circular."""
        self.assertIn("never substituted", self.d["note"])


class TestTheVanishing(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_vanishes_on_every_tested_metric(self):
        rows = self.cert["vanishing_in_D4"]
        self.assertTrue(rows)
        for r in rows:
            self.assertTrue(r["vanishes_identically"], r["metric"])

    def test_it_is_tested_somewhere_non_trivial(self):
        """Vanishing on Schwarzschild alone would prove little; a non-Einstein
        and a twisted metric must be in the set."""
        names = {r["metric"] for r in self.cert["vanishing_in_D4"]}
        self.assertIn("non_einstein_static", names)
        self.assertIn("taub_nut", names)


class TestTheDegreeOneSector(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.rows = self.cert["degree_one_sector"]

    def test_both_pieces_are_divergence_free(self):
        for r in self.rows:
            self.assertTrue(r["einstein_tensor_is_divergence_free"], r["metric"])
            self.assertTrue(r["cosmological_term_is_divergence_free"],
                            r["metric"])

    def test_schwarzschild_is_recovered_as_a_vacuum_solution(self):
        """G_mn = 0 on Schwarzschild is a CORRECTNESS check, not a failure --
        it is exactly the vacuum Einstein equation.  An earlier version of this
        module recorded it as a failed check."""
        row = next(r for r in self.rows if r["metric"] == "schwarzschild")
        self.assertTrue(row["is_a_vacuum_solution"])
        self.assertFalse(row["einstein_tensor_is_nonzero"])

    def test_the_einstein_tensor_is_nonzero_somewhere(self):
        """Otherwise the degree-<=1 sector is established only where it
        vanishes, which establishes nothing."""
        self.assertTrue(any(r["einstein_tensor_is_nonzero"] for r in self.rows))

    def test_vacuum_rows_do_not_double_as_nonvanishing_witnesses(self):
        for r in self.rows:
            if r["is_a_vacuum_solution"]:
                self.assertFalse(r["einstein_tensor_is_nonzero"])


class TestBoundaryAndProvenance(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_no_field_equation_formula_is_imported(self):
        assumed = " ".join(self.cert["inputs_assumed"]).lower()
        self.assertIn("forced head", assumed)
        self.assertIn("divergence-freedom", assumed)
        self.assertIn("rp-2nd-order", assumed)
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("degree", joined)

    def test_scope_limits_are_declared(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("d > 4", joined)
        self.assertIn("nonlocal", joined)
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_it_records_what_it_upgrades(self):
        up = self.cert["upgrades"]
        self.assertIn("weyl_trace_law", up["what"])
        self.assertIn("discharged", up["how"])

    def test_it_records_what_it_closes(self):
        self.assertIn("CITED", self.cert["closes"]["what"])

    def test_pinned_engine_has_not_drifted(self):
        for rel, want in self.cert["inputs"].items():
            path = os.path.join(REPO_ROOT, rel)
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), want,
                                 "%s changed; regenerate with --emit" % rel)


if __name__ == "__main__":
    unittest.main()
