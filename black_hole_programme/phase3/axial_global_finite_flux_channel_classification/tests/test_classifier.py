from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.classifier import (
    classify_exact_cell,
    classify_populated_form,
    complex_hermitian_inertia,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify import (
    verify_document,
)


HERE = Path(__file__).resolve().parents[1]


def connection_from_traces(cminus: sp.Matrix, cplus: sp.Matrix) -> sp.Matrix:
    """Assemble infinity order XI0,XI1,XI2,XI3,EI0,EI2."""
    answer = sp.zeros(6, 3)
    for target, source in zip((0, 1, 4), range(3)):
        answer[target, :] = cminus[source, :]
    for target, source in zip((2, 3, 5), range(3)):
        answer[target, :] = cplus[source, :]
    return answer


class ExactClassifierTest(unittest.TestCase):
    def test_certificate_is_fail_closed(self) -> None:
        verify_document(json.loads((HERE / "certificate.json").read_text()))

    def test_positive_synthetic_cell_and_one_sided_relation(self) -> None:
        identity = sp.eye(3)
        result = classify_exact_cell(
            connection_from_traces(identity, identity),
            identity,
            identity,
            sp.zeros(3),
        )
        self.assertEqual(result.imin["physical_inertia"], (3, 0, 0))
        self.assertEqual(result.iplus["physical_inertia"], (3, 0, 0))
        self.assertEqual(
            result.imin["origins"]["additional"]["physical_quotient_dimension"],
            2,
        )
        self.assertEqual(
            result.imin["origins"]["einstein"]["physical_quotient_dimension"],
            1,
        )
        self.assertEqual(result.joint_kernel_dimension, 0)
        self.assertTrue(result.conservation_certified)
        self.assertTrue(result.one_sided_relation["J_isometry_certified"])
        self.assertFalse(result.one_sided_relation["full_scattering_matrix"])

    def test_indefinite_synthetic_cell(self) -> None:
        gram = sp.diag(1, -1, -1)
        result = classify_exact_cell(
            connection_from_traces(sp.eye(3), sp.eye(3)),
            gram,
            gram,
            sp.zeros(3),
        )
        self.assertEqual(result.imin["physical_inertia"], (1, 2, 0))
        self.assertEqual(result.iplus["physical_inertia"], (1, 2, 0))

    def test_radical_synthetic_cell(self) -> None:
        trace = sp.diag(1, 1, 0)
        gram = sp.diag(1, 0, 1)
        result = classify_populated_form(trace, gram)
        self.assertEqual(result["trace_rank"], 2)
        self.assertEqual(result["trace_kernel_dimension"], 1)
        self.assertEqual(result["pullback_rank"], 1)
        self.assertEqual(result["populated_radical_dimension"], 1)
        self.assertEqual(result["physical_quotient_dimension"], 1)
        self.assertEqual(result["physical_inertia"], (1, 0, 0))

    def test_offdiagonal_exact_inertia(self) -> None:
        self.assertEqual(
            complex_hermitian_inertia(sp.Matrix([[0, 1], [1, 0]])),
            (1, 1, 0),
        )

    def test_wrong_conservation_refused(self) -> None:
        identity = sp.eye(3)
        with self.assertRaisesRegex(ValueError, "current conservation"):
            classify_exact_cell(
                connection_from_traces(identity, identity),
                identity,
                identity,
                identity,
            )


if __name__ == "__main__":
    unittest.main()

