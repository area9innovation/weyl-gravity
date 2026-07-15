from __future__ import annotations

from fractions import Fraction
import importlib.util
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TRANSFER_ROOT / "arity_two_cartan.py"
SPEC = importlib.util.spec_from_file_location("arity_two_cartan", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ENGINE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ENGINE
SPEC.loader.exec_module(ENGINE)


class ArityTwoCartanTests(unittest.TestCase):
    def test_equivariant_fixture_has_exact_iota_D2_correction(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        self.assertTrue(all(data.checks().values()))
        classification = data.classify()
        self.assertEqual(classification.status, "EXACT_CORRECTION")
        self.assertIsNotNone(classification.correction)
        correction = classification.correction
        assert correction is not None
        target = data.cartan_source().scaled(-1)
        self.assertEqual(
            data.complex.differential(correction, name="delta_iota_D2").entries,
            target.entries,
        )

    def test_non_equivariant_D_mutation_is_rejected_before_solving(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        rows = [list(row) for row in data.lie_D.entries]
        rows[5][5] = 3
        mutated = ENGINE.ArityTwoCartanData(
            data.complex,
            data.q2,
            data.iota_D,
            ENGINE.LinearOperator.from_rows("mutated_L_D", 0, rows),
            data.lie_D2,
        )
        self.assertFalse(mutated.checks()["classical_Cartan_identity"])
        self.assertFalse(mutated.checks()["D_q2_derivation"])
        with self.assertRaisesRegex(ValueError, "consistency checks failed"):
            mutated.classify()

    def test_closed_nonboundary_has_normalized_dual_witness(self) -> None:
        q1 = ENGINE.LinearOperator.zero("q1", 1, 1)
        complex_ = ENGINE.ArityTwoComplex((0,), (0,), q1)
        source = complex_.operator_from_coordinates(0, (1,), name="obstruction")
        classification = ENGINE.classify_cartan_source(complex_, source)
        self.assertEqual(classification.status, "NONTRIVIAL_OBSTRUCTION")
        self.assertIsNone(classification.correction)
        self.assertEqual(classification.dual_witness, (Fraction(1),))

    def test_admissibility_can_exclude_an_ambient_correction(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        source = data.cartan_source()
        ambient = ENGINE.classify_cartan_source(data.complex, source)
        self.assertEqual(ambient.status, "EXACT_CORRECTION")

        source_slots = data.complex.coordinate_slots(-1)
        constraints = tuple(
            ENGINE.BilinearConstraint.from_row(
                f"forbid_iota2_{index}",
                -1,
                [int(column == index) for column in range(len(source_slots))],
            )
            for index in range(len(source_slots))
        )
        admissible = ENGINE.AdmissibleArityTwoComplex(
            data.complex,
            constraints,
            (-1,),
        )
        restricted = ENGINE.classify_cartan_source(admissible, source)
        self.assertEqual(restricted.status, "NONTRIVIAL_OBSTRUCTION")
        self.assertIsNone(restricted.correction)
        self.assertIsNotNone(restricted.dual_witness)

    def test_nonclosed_source_is_rejected(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        slots = data.complex.coordinate_slots(0)
        nonclosed = None
        for index in range(len(slots)):
            coordinates = [0 for _ in slots]
            coordinates[index] = 1
            candidate = data.complex.operator_from_coordinates(0, coordinates, name="candidate")
            if not data.complex.differential(candidate, name="delta_candidate").is_zero():
                nonclosed = candidate
                break
        self.assertIsNotNone(nonclosed)
        with self.assertRaisesRegex(ValueError, "not q1-closed"):
            ENGINE.classify_cartan_source(data.complex, nonclosed)

    def test_sourced_consistency_identity_is_computed_explicitly(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        self.assertTrue(data.sourced_consistency_identity_defect().is_zero())

        nonlinear_lie_D2 = None
        slots = data.complex.coordinate_slots(0)
        for index in range(len(slots)):
            coordinates = [0 for _ in slots]
            coordinates[index] = 1
            candidate = data.complex.operator_from_coordinates(
                0,
                coordinates,
                name="L_D_2_mutation",
            )
            if not data.complex.differential(candidate, name="delta_L_D_2").is_zero():
                nonlinear_lie_D2 = candidate
                break
        self.assertIsNotNone(nonlinear_lie_D2)
        nonlinear_action = ENGINE.ArityTwoCartanData(
            data.complex,
            data.q2,
            data.iota_D,
            data.lie_D,
            nonlinear_lie_D2,
        )
        self.assertTrue(nonlinear_action.checks()["sourced_consistency_identity"])
        self.assertFalse(nonlinear_action.checks()["cartan_source_q1_closed"])


if __name__ == "__main__":
    unittest.main()
