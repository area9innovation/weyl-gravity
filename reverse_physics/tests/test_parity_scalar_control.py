"""Falsification tests for the parity-odd scalar defect, its retraction and its
corrections.

A retraction is the easiest record to let rot: the numbers get corrected, the
reason gets forgotten, and the next candidate family is built the same way.  So
what these guard is not the counts.  It is that the retraction stays visible,
that the original claims stay preserved rather than quietly rewritten, that the
reason no existing check caught it survives in the record, and that the
boundaries on the corrected result are no stronger than the ones on the claim it
replaced.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERTS = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
CERT = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1.json")
FIELDEQ = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1.json")
COUNT = os.path.join(CERTS, "REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1.json")
EULER = os.path.join(CERTS, "REVERSE_PHYSICS_EULER_OPERATOR_V1.json")
ACTION = os.path.join(CERTS, "REVERSE_PHYSICS_WEYL_ACTION_V1.json")
REPORT = os.path.join(REPO_ROOT, "reverse_physics", "reports",
                      "parity-scalar-defect.md")


def load(path=CERT):
    with open(path) as fh:
        return json.load(fh)


class TestTheRetractionIsUnmissable(unittest.TestCase):
    """A reader landing on the withdrawn certificate must not be able to take
    its numbers as current."""

    def setUp(self):
        self.fe = load(FIELDEQ)

    def test_the_status_field_says_retracted(self):
        self.assertEqual(self.fe["status"], "RETRACTED")

    def test_status_precedes_the_original_claims(self):
        """Key order is the only thing standing between a reader and the old
        `establishes` string."""
        keys = list(self.fe.keys())
        self.assertLess(keys.index("status"), keys.index("establishes"))
        self.assertLess(keys.index("retraction"), keys.index("establishes"))

    def test_it_names_what_replaces_it(self):
        self.assertEqual(self.fe["retraction"]["by"],
                         "REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1")

    def test_it_says_what_was_actually_wrong(self):
        w = self.fe["retraction"]["what_was_wrong"]
        self.assertIn("NOT A SCALAR", w)
        self.assertIn("SL(6, Z)", w)

    def test_the_withdrawn_claim_is_named_explicitly(self):
        """"Retracted" without naming the sentence lets the sentence survive."""
        w = self.fe["retraction"]["what_is_withdrawn"]
        self.assertIn("NOT redundant on the D = 6 field equations", w)
        self.assertIn("mean nothing", w)

    def test_the_original_text_is_preserved_not_rewritten(self):
        """Append-only: a repair is a new entry, never an edit."""
        self.assertIn("verbatim",
                      " ".join(self.fe["retraction"].keys()) + " " +
                      " ".join(str(v) for v in self.fe["retraction"].values()))
        self.assertIn("CONTRIBUTES TO THE FIELD EQUATIONS",
                      self.fe["establishes"])
        self.assertEqual(len(self.fe["results"]), 3)
        self.assertEqual(self.fe["results"][0]["value"], "-12614421113/320")


class TestTheEulerOperatorIsNotCollateralDamage(unittest.TestCase):
    """The instrument was correct; the Lagrangian it was pointed at was not.
    Retracting the operator too would lose a working tool."""

    def test_the_retraction_says_the_operator_survives(self):
        s = load(FIELDEQ)["retraction"]["what_survives"]
        self.assertIn("untouched", s)
        self.assertIn("n = 6", s)
        self.assertIn("exactly zero", s)

    def test_the_euler_certificate_still_stands(self):
        self.assertTrue(load(EULER)["checks"]["ok"])

    def test_the_new_certificate_does_not_retract_it(self):
        self.assertNotIn("EULER_OPERATOR", load()["retracts"])


class TestTheCorrectionToTheCount(unittest.TestCase):
    def setUp(self):
        self.c = load(COUNT)

    def test_the_status_field_says_corrected(self):
        self.assertEqual(self.c["status"], "CORRECTED")

    def test_status_precedes_the_original_claims(self):
        keys = list(self.c.keys())
        self.assertLess(keys.index("correction"), keys.index("establishes"))

    def test_all_four_rows_are_accounted_for(self):
        rows = self.c["correction"]["corrected_counts"]
        self.assertEqual(len(rows), 4)

    def test_the_two_that_moved_are_stated_as_replacements(self):
        rows = self.c["correction"]["corrected_counts"]
        self.assertIn("not 2", rows["D4_weight6"])
        self.assertIn("not 2", rows["D6_weight6"])

    def test_the_two_that_did_not_move_say_unchanged(self):
        rows = self.c["correction"]["corrected_counts"]
        self.assertIn("UNCHANGED", rows["D4_weight4_pontryagin"])
        self.assertIn("UNCHANGED", rows["odd_D"])

    def test_the_original_counts_are_preserved(self):
        self.assertIn("2", self.c["establishes"])


class TestWhyNothingCaughtIt(unittest.TestCase):
    """The counts are recoverable; the reason is not.  If this drops out of the
    record, the next candidate family gets built exactly the same way."""

    def setUp(self):
        self.w = load()["why_no_existing_check_could_catch_it"]

    def test_the_conformal_test_is_recorded_as_vacuous_here(self):
        v = self.w["the_conformal_test_is_vacuous_on_weyl_built_candidates"]
        self.assertIn("no derivative-of-sigma terms", v.lower())
        self.assertIn("ANY index pattern", v)

    def test_the_gates_own_words_are_quoted_against_it(self):
        """"Conformally invariant by construction" was true and was exactly
        why the test said nothing.  That irony is the lesson."""
        v = self.w["the_conformal_test_is_vacuous_on_weyl_built_candidates"]
        self.assertIn("conformally invariant by construction", v)

    def test_the_weight_cancellation_is_recorded(self):
        self.assertIn("-2", self.w["the_weight_count_cancels"])
        self.assertIn("+2", self.w["the_weight_count_cancels"])

    def test_the_actual_gap_is_named(self):
        g = self.w["the_actual_gap"]
        self.assertIn("never tested covariance", g)

    def test_the_mechanism_is_recorded_not_just_the_symptom(self):
        d = self.w["where_the_defect_lives"]
        self.assertIn("variance is implicit", d.lower())
        self.assertIn("cu012", d)


class TestTheFalsifierIsCalibratedBothWays(unittest.TestCase):
    """A test that only ever passes proves nothing.  The negative control is
    what makes the positive results evidence."""

    def setUp(self):
        self.f = load()["the_falsifier"]

    def test_a_negative_control_is_required_to_move(self):
        c = self.f["calibrated_in_both_directions"]
        self.assertIn("must MOVE", c)
        self.assertIn("blind", c)

    def test_known_scalars_are_required_to_survive(self):
        c = self.f["calibrated_in_both_directions"]
        self.assertIn("PONTRYAGIN", c.upper())

    def test_the_determinant_is_preserved_on_purpose(self):
        w = self.f["why_SL_and_not_GL"]
        self.assertIn("det A = 1", w)
        self.assertIn("SYMBOL", w)

    def test_a_non_triangular_chart_is_used(self):
        t = self.f["three_charts"]
        self.assertIn("triangular in neither direction", t)

    def test_the_witness_ties_back_to_the_retracted_number(self):
        """The chart-dependent value IS the number the withdrawn certificate
        published as its control.  That link is the proof they are the same
        object."""
        self.assertIn("6566972251/160", self.f["the_witness"])
        fe = load(FIELDEQ)
        self.assertIn("6566972251/160", json.dumps(fe))


class TestTheEmptySectorIsTreatedAsAResult(unittest.TestCase):
    def setUp(self):
        self.e = load()["an_empty_sector_is_a_result"]

    def test_the_conflict_is_stated(self):
        p = self.e["the_problem"]
        self.assertIn("PREMISE OF A NONZERO COUNT", p)
        self.assertIn("demanding the wrong answer", p)

    def test_both_ranks_zero_is_required_not_just_the_difference(self):
        f = self.e["the_fix"]
        self.assertIn("both ranks to be zero", f)
        self.assertIn("difference", f)

    def test_a_parity_even_witness_guards_against_a_dead_pipeline(self):
        w = self.e["the_parity_even_witness"]
        self.assertIn("R_{abcd} R^{abcd}", w)
        self.assertIn("indistinguishable", w)

    def test_the_structural_reason_the_D6_zero_is_not_a_weyl_artefact(self):
        """Zero from Weyl alone could be the trace conditions.  Zero from
        Riemann too means the index pattern itself is empty."""
        r = load()["why_the_D6_zero_is_structural"]
        self.assertIn("RIEMANN", r.upper())
        self.assertIn("not traceless", r)


class TestTheDefectLedger(unittest.TestCase):
    def setUp(self):
        self.d = load()["the_eight_defects"]

    def test_every_defect_names_a_dimension_and_a_candidate(self):
        for e in self.d:
            self.assertIn(e["dimension"], (4, 6))
            self.assertIsInstance(e["candidate"], int)
            self.assertTrue(e["defect"])

    def test_the_two_the_published_count_rested_on_are_marked(self):
        marked = [e for e in self.d if "published count" in e["defect"]]
        self.assertEqual(len(marked), 2)
        self.assertTrue(all(e["dimension"] == 6 for e in marked))

    def test_the_zero_as_written_defect_is_called_out(self):
        """It could never have been found from a wrong number.  That is the
        whole argument for auditing construction rather than output."""
        n = load()["the_one_worth_naming"]
        self.assertIn("ZERO AS WRITTEN", n)
        self.assertIn("never by watching output", n)


class TestTheBoundariesAreNoStrongerThanBefore(unittest.TestCase):
    """The failure mode of a correction is over-correcting: replacing one
    unsupported claim with its unsupported opposite."""

    def setUp(self):
        self.dne = " ".join(load()["does_not_establish"])

    def test_the_algebraic_sector_is_a_count_but_the_whole_sector_is_not(self):
        """The upgrade is real and it is bounded: exhaustive over one epsilon
        and three UNDIFFERENTIATED curvature tensors, and silent on the
        derivative patterns.  Letting "exhaustive" travel unqualified would
        overstate it exactly the way the retracted claim did."""
        self.assertIn("undifferentiated", self.dne.lower())
        self.assertIn("NOT swept", self.dne)
        self.assertIn("hand-built list again", self.dne)

    def test_the_vacuous_reading_is_not_claimed(self):
        self.assertIn("Recorded as a reading, not as a result", self.dne)
        self.assertIn("opposite direction", self.dne)

    def test_the_ledger_result_is_explicitly_spared(self):
        self.assertIn("REVERSE_PHYSICS_WEYL_ACTION_V1", self.dne)
        self.assertIn("theta-angle", self.dne)

    def test_the_parity_even_counts_are_explicitly_spared(self):
        self.assertIn("REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1", self.dne)

    def test_the_unexplained_observation_is_kept_as_an_observation(self):
        self.assertIn("four-dimensional identity", self.dne)
        self.assertIn("not a result", self.dne)

    def test_it_carries_the_local_algebraic_tag_only(self):
        self.assertEqual(load()["dependency_tags"], ["LOCAL-ALGEBRAIC"])


class TestTheEnumerationUpgrade(unittest.TestCase):
    """The D = 6 zero started as a lower bound over a hand-built list -- the same
    weakness that admitted the eight defects.  These guard that it is now a count,
    and that the mechanism recorded with it is the one the computation found
    rather than the one that was guessed twice."""

    def setUp(self):
        self.cert = load()
        self.e = self.cert["the_d6_zero_is_now_a_count_not_a_lower_bound"]
        self.m = self.cert["the_mechanism"]

    def test_the_space_is_enumerated_not_hand_built(self):
        self.assertIn("hand-built", self.e["what_changed"].lower())
        self.assertIn("mechanically", self.e["what_changed"])

    def test_the_collapse_from_13860_is_justified_by_a_verified_identity(self):
        """(2,2,2) is what makes the sweep runnable, so it must rest on an
        identity that was checked, not sampled."""
        sp = self.e["the_space"]
        self.assertIn("13860", sp)
        self.assertIn("(2,2,2)", sp)
        self.assertIn("exact componentwise identity rather than sampled", sp)

    def test_all_15_matchings_are_swept_so_tracelessness_is_exercised(self):
        self.assertIn("exercised rather than assumed", self.e["the_space"])

    def test_variance_is_derived_not_hand_written(self):
        v = self.e["variance_is_derived_not_chosen"]
        self.assertIn("Nothing is hand-written", v)

    def test_the_mechanism_is_pair_exchange(self):
        self.assertIn("PAIR-EXCHANGE SYMMETRY", self.m["finding"])
        self.assertIn("C_{abcd} = C_{cdab}", self.m["finding"])

    def test_the_evidence_separates_the_two_halves_of_the_symmetry(self):
        """Antisymmetry alone leaves 2208 alive; adding pair-exchange kills all
        of them.  Without both numbers the mechanism is not pinned."""
        ev = self.m["the_evidence"]
        self.assertEqual(ev["generic_no_symmetry"], "3240 of 3240 nonzero")
        self.assertEqual(ev["antisymmetric_within_pairs_only"], "2208 of 3240 nonzero")
        self.assertEqual(ev["plus_pair_exchange_symmetry"], "0")

    def test_the_generic_sweep_is_what_makes_the_zeros_meaningful(self):
        """3240 of 3240 nonzero is the only thing separating 'the answer is
        zero' from 'the loop never ran'."""
        self.assertIn("3240 of 3240", self.m["the_evidence"]["generic_no_symmetry"])

    def test_bianchi_and_tracelessness_are_explicitly_ruled_out(self):
        n = self.m["what_it_is_not"]
        self.assertIn("NOT the first Bianchi identity", n)
        self.assertIn("NOT tracelessness", n)
        self.assertIn("2208", n)

    def test_the_wrong_hypothesis_is_recorded_rather_than_erased(self):
        """Recording it is what makes the next control get built to fail."""
        w = self.m["a_hypothesis_that_was_wrong_twice"]
        self.assertIn("wrong", w.lower())
        self.assertIn("refute", w)

    def test_the_derivative_sector_is_excluded_from_the_claim(self):
        dne = " ".join(self.cert["does_not_establish"])
        self.assertIn("undifferentiated", dne.lower())
        self.assertIn("NOT swept", dne)

    def test_the_controls_are_flagged_as_less_exhaustive(self):
        """The (2,2,2) cut is justified BY Bianchi, so it is not valid for the
        Bianchi-violating controls.  Letting that read as equally exhaustive
        would overstate them."""
        dne = " ".join(self.cert["does_not_establish"])
        self.assertIn("CONTROL sweeps are as exhaustive as the curvature ones", dne)
        self.assertIn("justified BY the first Bianchi identity", dne)

    def test_the_gate_is_in_the_check_ledger(self):
        self.assertIn("curvature_parity_enumeration_gate",
                      self.cert["checks"]["detail"])


class TestTheReport(unittest.TestCase):
    def setUp(self):
        with open(REPORT) as fh:
            self.text = fh.read()

    def test_the_retraction_is_in_the_opening(self):
        self.assertIn("retracts", self.text[:900].lower())

    def test_it_carries_the_chart_dependent_witness(self):
        self.assertIn("6566972251/160", self.text)
        self.assertIn("-200078513393/160", self.text)

    def test_it_carries_the_corrected_table(self):
        self.assertIn("**0**", self.text)
        self.assertIn("unchanged", self.text.lower())

    def test_it_carries_the_verification_commands(self):
        self.assertIn("curvature_coord_scalar_control_gate", self.text)

    def test_it_declares_exact_arithmetic(self):
        self.assertIn("no floating point", self.text.lower())


if __name__ == "__main__":
    unittest.main()
