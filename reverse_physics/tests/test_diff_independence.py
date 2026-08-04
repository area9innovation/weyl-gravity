"""Falsification tests for the RP-DIFF independence witness.

Unlike the geometry discharges, this computation is pure Fraction arithmetic and
runs in well under a second, so the tests RE-RUN IT rather than only guarding an
emitted certificate.  What they attack is the two ways this result could be
worthless: an invariance computation returning zero because it is broken, and a
"witness" that is not actually moved by the group it is supposed to fail.
"""

from __future__ import annotations

import json
import os
import unittest

from reverse_physics.diff_independence import (
    CERT_PATH,
    CONTROL_BASIS,
    DIM,
    H2_BASIS,
    build,
    d_inverse,
    d_metric,
    invariant_dimension,
    variation_row_control,
    variation_row_h2,
    weyl_weight,
)


class TestTheComputation(unittest.TestCase):
    # Computed once: the control space is 100 basis elements against 1600
    # columns and is ranked twice, so per-method setUp would dominate the
    # scoped suite's runtime for no extra coverage.
    @classmethod
    def setUpClass(cls):
        cls.main = invariant_dimension(H2_BASIS, variation_row_h2)
        cls.control = invariant_dimension(CONTROL_BASIS, variation_row_control)

    def test_lowest_weight_zero_degree_has_55_elements(self):
        """Degree-2 monomials in the 10 independent inverse-metric
        components: C(11,2) = 55."""
        self.assertEqual(len(H2_BASIS), 55)
        self.assertEqual(self.main["basis_dimension"], 55)

    def test_diff_invariant_subspace_is_zero(self):
        self.assertEqual(self.main["invariant_dimension"], 0)

    def test_the_two_rank_rails_agree(self):
        self.assertTrue(self.main["rails_agree"])
        self.assertTrue(self.control["rails_agree"])
        self.assertEqual(self.main["rank_rail_a_gauss_jordan"],
                         self.main["rank_rail_b_bareiss"])

    def test_control_finds_its_known_invariant(self):
        """h^ab g_cd has a one-dimensional GL-invariant subspace, spanned by
        the trace.  WITHOUT THIS the zero above is not evidence of anything --
        a broken invariance computation returns zero too."""
        self.assertEqual(self.control["invariant_dimension"], 1,
                         "the machinery cannot find a known invariant, so its "
                         "zero answers mean nothing")


class TestTheWitness(unittest.TestCase):
    def test_the_witness_is_actually_moved(self):
        """sqrt(-g)(g^00)^2 must not be accidentally GL-invariant."""
        row = variation_row_h2(((0, 0), (0, 0)))
        movers = {gen for (gen, _m), c in row.items() if c}
        self.assertTrue(movers, "the witness is GL-invariant -- not a witness")

    def test_every_basis_element_is_a_witness(self):
        """The invariant subspace is zero, so no element is invariant."""
        for element in H2_BASIS:
            row = variation_row_h2(element)
            self.assertTrue(any(c for c in row.values()),
                            "%s is GL-invariant, contradicting dimension 0"
                            % (element,))

    def test_witness_is_weyl_invariant_and_has_weight_zero(self):
        self.assertEqual(weyl_weight(2, 0), 0)

    def test_only_degree_two_is_weyl_invariant(self):
        """Exactly one inverse-metric degree gives weight zero, so the carrier
        is not being chosen to make the answer come out."""
        invariant = [n for n in range(6) if weyl_weight(n, 0) == 0]
        self.assertEqual(invariant, [2])


class TestGroupActionIsRight(unittest.TestCase):
    """The GL action is written by hand, so check it against facts that do not
    depend on how it was written."""

    def test_inverse_metric_variation_is_symmetric_in_its_indices(self):
        for a in range(DIM):
            for b in range(DIM):
                for m in range(DIM):
                    for n in range(m, DIM):
                        self.assertEqual(d_inverse((m, n), a, b),
                                         d_inverse((n, m), a, b))

    def test_trace_is_the_control_invariant(self):
        """delta( h^ab g_ab ) = 0 for every generator -- computed from the two
        variation rules independently, not asserted."""
        for a in range(DIM):
            for b in range(DIM):
                acc = {}
                for p in [(m, n) for m in range(DIM) for n in range(m, DIM)]:
                    weight = 1 if p[0] == p[1] else 2  # off-diagonal counted twice
                    for r, c in d_inverse(p, a, b).items():
                        acc[(r, p)] = acc.get((r, p), 0) + c * weight
                    for s, c in d_metric(p, a, b).items():
                        acc[(p, s)] = acc.get((p, s), 0) + c * weight
                # collect on the contracted trace: pair the h-index with the
                # g-index and sum
                total = {}
                for (hp, gp), c in acc.items():
                    total[(hp, gp)] = total.get((hp, gp), 0) + c
                contracted = sum(c for (hp, gp), c in total.items() if hp == gp)
                self.assertEqual(contracted, 0,
                                 "generator E^%d_%d moves the trace" % (a, b))


class TestCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fresh = build()
        with open(CERT_PATH) as fh:
            cls.disk = json.load(fh)

    def test_all_checks_pass(self):
        self.assertTrue(self.fresh["checks"]["ok"])
        self.assertEqual(self.fresh["checks"]["failures"], [])

    def test_emitted_certificate_is_current(self):
        self.assertEqual(self.disk["main_space"], self.fresh["main_space"])
        self.assertEqual(self.disk["control_space"]["invariant_dimension"],
                         self.fresh["control_space"]["invariant_dimension"])

    def test_the_conditional_is_stated_not_hidden(self):
        """Independence is GIVEN RP-METRIC; the Stuckelberg escape is blocked,
        not refuted, and the certificate must keep saying so."""
        joined = " ".join(self.fresh["does_not_establish"]).lower()
        self.assertIn("stuckelberg", joined)
        self.assertIn("rp-metric", joined)
        self.assertIn("blocked", joined)

    def test_the_quantum_boundary_is_stated(self):
        joined = " ".join(self.fresh["does_not_establish"]).lower()
        self.assertIn("quantum", joined)
        self.assertIn("not used as evidence", joined)

    def test_the_consequence_is_recorded(self):
        c = self.fresh["consequence"]
        self.assertEqual(c["witness_derivative_order"], 0)
        self.assertEqual(c["derived_order_at_D4"], 4)
        self.assertIn("requires RP-DIFF", c["claim"])

    def test_scope_limit_to_lowest_degree_is_declared(self):
        joined = " ".join(self.fresh["does_not_establish"]).lower()
        self.assertIn("lowest weight-zero degree", joined)


if __name__ == "__main__":
    unittest.main()
