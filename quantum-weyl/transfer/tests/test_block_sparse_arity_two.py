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


ENGINE = _load("arity_two_for_block_sparse_test", TRANSFER_ROOT / "arity_two_cartan.py")
BLOCK = _load("block_sparse_arity_two_test_module", TRANSFER_ROOT / "block_sparse_arity_two.py")


class BlockSparseArityTwoTests(unittest.TestCase):
    def test_block_solver_matches_ambient_exact_correction(self) -> None:
        data = ENGINE.build_exact_correction_fixture()
        weights = tuple((data.lie_D.entries[index][index],) for index in range(data.complex.dimension))
        block = BLOCK.BlockSparseArityTwoComplex(data.complex, ("D_weight",), weights)
        ambient = data.classify()
        blocked = ENGINE.classify_cartan_source(block, data.cartan_source())
        self.assertEqual(blocked.status, "EXACT_CORRECTION")
        self.assertIsNotNone(ambient.correction)
        self.assertIsNotNone(blocked.correction)
        assert ambient.correction is not None and blocked.correction is not None
        self.assertEqual(
            data.complex.differential(blocked.correction, name="delta_blocked").entries,
            data.complex.differential(ambient.correction, name="delta_ambient").entries,
        )
        metrics = block.metrics(0)
        self.assertGreater(metrics["block_count"], 1)
        self.assertLess(metrics["largest_source_block"], metrics["source_coordinate_count"])

    def test_block_solver_retains_normalized_dual_witness(self) -> None:
        q1 = ENGINE.LinearOperator.zero("q1", 1, 1)
        ambient = ENGINE.ArityTwoComplex((0,), (0,), q1)
        block = BLOCK.BlockSparseArityTwoComplex(ambient, ("D_weight",), ((Fraction(0),),))
        source = ambient.operator_from_coordinates(0, (1,), name="obstruction")
        result = ENGINE.classify_cartan_source(block, source)
        self.assertEqual(result.status, "NONTRIVIAL_OBSTRUCTION")
        self.assertEqual(result.dual_witness, (Fraction(1),))

    def test_nonconserved_label_is_rejected(self) -> None:
        q1 = ENGINE.LinearOperator.from_rows("q1", 1, ((0, 0), (1, 0)))
        ambient = ENGINE.ArityTwoComplex((0, 1), (0, 1), q1)
        with self.assertRaisesRegex(ValueError, "q1 does not preserve"):
            BLOCK.BlockSparseArityTwoComplex(
                ambient,
                ("bad_weight",),
                ((Fraction(0),), (Fraction(1),)),
            )

    def test_sparse_solver_handles_inconsistent_and_underdetermined_systems(self) -> None:
        self.assertIsNone(
            BLOCK.sparse_rref_solve(({},), (Fraction(1),), 2)
        )
        solution = BLOCK.sparse_rref_solve(
            ({0: Fraction(2), 1: Fraction(1)},),
            (Fraction(4),),
            2,
        )
        self.assertEqual(solution, (Fraction(2), Fraction(0)))


if __name__ == "__main__":
    unittest.main()
