from __future__ import annotations

from fractions import Fraction
import importlib.util
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = _load("arity_three_cartan_test_module", TRANSFER_ROOT / "arity_three_cartan.py")
ARITY2 = _load("arity_two_for_arity_three_test", TRANSFER_ROOT / "arity_two_cartan.py")


class ArityThreeCartanTests(unittest.TestCase):
    def test_direct_q3_fixture_has_exact_iota_D3_correction(self) -> None:
        data = ENGINE.build_direct_q3_correction_fixture()
        self.assertTrue(all(data.checks().values()))
        result = data.classify()
        self.assertEqual(result.status, "EXACT_CORRECTION")
        self.assertIsNotNone(result.correction)
        assert result.correction is not None
        self.assertEqual(
            data.complex.differential(result.correction, name="delta_iota_D3").entries,
            data.cartan_source().scaled(-1).entries,
        )
        self.assertFalse(data.q3.is_zero())
        self.assertFalse(data.cartan_source().is_zero())

    def test_exchange_bracket_is_computed_from_q2_and_iota_D2(self) -> None:
        complex_, q2, iota2, exchange = ENGINE.build_exchange_bracket_fixture()
        complex_.validate_ternary(exchange)
        self.assertFalse(exchange.is_zero())
        reverse = complex_.bilinear_bracket(iota2, q2, name="[iota_D2,q2]")
        self.assertEqual(exchange.entries, reverse.entries)

    def test_odd_q2_self_commutator_has_expected_factor_two(self) -> None:
        complex_, q2, _iota2, _exchange = ENGINE.build_exchange_bracket_fixture()
        bracket = complex_.bilinear_bracket(q2, q2, name="[q2,q2]")
        composition = ENGINE._bilinear_composition(
            q2,
            q2,
            input_parities=complex_.basis_parities,
            name="q2_after_q2",
        )
        self.assertEqual(bracket.entries, composition.scaled(2).entries)

    def test_closed_nonboundary_has_normalized_dual_witness(self) -> None:
        q1 = ARITY2.LinearOperator.zero("q1", 1, 1)
        complex_ = ENGINE.ArityThreeComplex((0,), (0,), q1)
        source = complex_.operator_from_coordinates(0, (1,), name="obstruction")
        result = ENGINE.classify_arity_three_source(complex_, source)
        self.assertEqual(result.status, "NONTRIVIAL_OBSTRUCTION")
        self.assertEqual(result.dual_witness, (Fraction(1),))

    def test_broken_D_weight_is_rejected_before_solving(self) -> None:
        data = ENGINE.build_direct_q3_correction_fixture()
        rows = [list(row) for row in data.lie_D.entries]
        rows[3][3] = 4
        broken = ENGINE.ArityThreeCartanData(
            data.complex,
            data.q2,
            data.q3,
            data.iota_D,
            data.iota_D2,
            ARITY2.LinearOperator.from_rows("broken_L_D", 0, rows),
            data.lie_D2,
            data.lie_D3,
        )
        self.assertFalse(broken.checks()["Cartan_identity_arity_one"])
        self.assertFalse(broken.checks()["D_equivariance_arity_three"])
        with self.assertRaisesRegex(ValueError, "consistency checks failed"):
            broken.classify()

    def test_nonclosed_arity_three_source_is_rejected(self) -> None:
        data = ENGINE.build_direct_q3_correction_fixture()
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
            ENGINE.classify_arity_three_source(data.complex, nonclosed)


if __name__ == "__main__":
    unittest.main()
