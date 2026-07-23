from __future__ import annotations

import json
import hashlib
import struct
import unittest
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.activate import (
    build_classification,
    verify_document as verify_activated_document,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.affine_adapter import (
    AffineScalar,
    ComplexAffine,
    Interval,
    certify_origin_blocks,
    certify_whole_cell_inertia,
    determinant_excludes_zero,
    json_ready,
    matrix_add,
    matrix_from_json,
    matrix_multiply,
    matrix_negate,
    require_hermitian_enclosure,
    validate_channel_handoff_algebra,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.classifier import (
    classify_exact_cell,
    classify_populated_form,
    complex_hermitian_inertia,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify import (
    verify_document,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify_activated import (
    verify_documents as independently_verify_activated_documents,
)


HERE = Path(__file__).resolve().parents[1]


def float_bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def rational(value: int | Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def affine_scalar(
    center: int | Fraction,
    linear: int | Fraction = 0,
    remainder: tuple[float, float] = (0.0, 0.0),
) -> dict:
    return {
        "center": rational(center),
        "linear": rational(linear),
        "remainder": [float_bits(remainder[0]), float_bits(remainder[1])],
    }


def complex_affine(
    real: int | Fraction,
    imag: int | Fraction = 0,
    *,
    real_linear: int | Fraction = 0,
    imag_linear: int | Fraction = 0,
    real_remainder: tuple[float, float] = (0.0, 0.0),
    imag_remainder: tuple[float, float] = (0.0, 0.0),
) -> dict:
    return {
        "re": affine_scalar(real, real_linear, real_remainder),
        "im": affine_scalar(imag, imag_linear, imag_remainder),
    }


def affine_diagonal(values: list[dict]) -> list:
    zero = complex_affine(0)
    return [
        [values[i] if i == j else zero for j in range(len(values))]
        for i in range(len(values))
    ]


def constant_complex_matrix(values: list[list[int | complex]]) -> list:
    return [
        [
            complex_affine(
                Fraction(value.real) if isinstance(value, complex) else value,
                Fraction(value.imag) if isinstance(value, complex) else 0,
            )
            for value in row
        ]
        for row in values
    ]


def synthetic_subdivided_handoff() -> dict:
    identity = constant_complex_matrix(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    )
    twice_identity = constant_complex_matrix(
        [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    )
    zero = constant_complex_matrix(
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    )
    connection = constant_complex_matrix(
        [
            [1, 0, 0],
            [0, 1, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 1],
        ]
    )
    artifact = (
        HERE.parent
        / "axial_global_connection_matrix_v5/chunks/tests/fixtures/"
        "current_identity.json"
    )
    verifier = artifact.with_name("verify_current_identity.py")
    witness = {
        "kind": "verified-action-current-identity",
        "path": str(artifact.relative_to(HERE.parents[2])),
        "result_id": "SYNTHETIC_ACTION_CURRENT_IDENTITY_V1",
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "verifier_path": str(verifier.relative_to(HERE.parents[2])),
        "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest(),
        "replay_command": [
            "python",
            str(verifier.relative_to(HERE.parents[2])),
        ],
        "certified_claim_path": [
            "claim_flags",
            "radial_current_conservation_certified",
        ],
    }
    payload = {
        "connection": {
            "complex_6_by_3": connection,
            "Cminus_3_by_3": identity,
            "Cplus_3_by_3": identity,
        },
        "endpoint_forms": {
            "Gminus": twice_identity,
            "Gplus": identity,
            "GHplus_outward": identity,
            "gminus_pullback": twice_identity,
            "gplus_pullback": identity,
            "conservation": {
                "identity": "GHplus+gplus-gminus=0",
                "defect": zero,
                "zero_contained_entrywise": True,
                "structural_identity_witness": witness,
            },
        },
        "classification_witnesses": {
            "inertia": {
                name: {"positive": 3, "negative": 0, "zero": 0}
                for name in ("GHplus", "gminus", "gplus")
            },
            "multiplier_bounds": {
                "connection_operator_norm_upper": "2.0",
                "Cminus_inverse_norm_upper": "1.0",
                "frequency_derivative_norm_upper": "3.0",
                "whole_cell": True,
            },
        },
        "provenance": {"synthetic_sha256": "a" * 64},
    }
    return {
        "schema": "phase3-axial-global-channel-handoff-v1",
        "status": "CERTIFIED",
        "parent_cell": {
            "ell": 2,
            "mass_normalization": "M=1",
            "omega_parameter": "M*omega",
            "omega_interval": ["1/2", "129/256"],
            "center": "257/512",
            "radius": "1/512",
        },
        "cells": [
            {
                "cell_id": "q0",
                "omega_interval": ["1/2", "129/256"],
                "center": "257/512",
                "radius": "1/512",
                "affine_generator": 7315,
                "disposition": "CERTIFIED",
                "validated_payload": payload,
                "shortfall": None,
            }
        ],
        "parent_classification": {
            "all_cells_resolved": True,
            "parent_rank_inertia_promoted": True,
            "exceptional_or_unresolved_cells": [],
        },
    }


def synthetic_sixteen_cell_handoff() -> dict:
    """Refine the synthetic pilot into the production 16-cell cover."""
    document = synthetic_subdivided_handoff()
    payload = document["cells"][0]["validated_payload"]
    lower = Fraction(1, 2)
    width = Fraction(1, 4096)
    cells = []
    for index in range(16):
        lo = lower + index * width
        hi = lo + width
        cells.append(
            {
                "cell_id": f"q{index}",
                "omega_interval": [rational(lo), rational(hi)],
                "center": rational((lo + hi) / 2),
                "radius": rational(width / 2),
                "affine_generator": 7315,
                "disposition": "CERTIFIED",
                # A JSON round trip gives every cell an independent payload,
                # matching the production handoff's per-cell ownership.
                "validated_payload": json.loads(json.dumps(payload)),
                "shortfall": None,
            }
        )
    document["cells"] = cells
    return document


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
        self.assertEqual(
            result.imin["origins"]["additional"][
                "restricted_pullback_inertia"
            ],
            (1, 1, 0),
        )
        self.assertEqual(
            result.imin["origins"]["einstein"][
                "restricted_pullback_inertia"
            ],
            (0, 1, 0),
        )
        self.assertEqual(result.imin["einstein_additional_mixed_rank"], 0)

    def test_einstein_additional_mixing_is_reported(self) -> None:
        gram = sp.Matrix(
            [
                [2, 0, 1 + sp.I],
                [0, -1, 2],
                [1 - sp.I, 2, 3],
            ]
        )
        result = classify_populated_form(sp.eye(3), gram)
        self.assertEqual(result["einstein_additional_mixed_rank"], 1)
        self.assertEqual(
            result["einstein_additional_mixed_block"],
            sp.Matrix([[1 + sp.I], [2]]),
        )
        self.assertEqual(
            result["origins"]["additional"]["restricted_pullback_inertia"],
            (1, 1, 0),
        )
        self.assertEqual(
            result["origins"]["einstein"]["restricted_pullback_inertia"],
            (1, 0, 0),
        )

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


class AffineCellAdapterTest(unittest.TestCase):
    def test_affine_product_keeps_quadratic_remainder(self) -> None:
        left = AffineScalar(Fraction(1), Fraction(1), Interval.point(0))
        right = AffineScalar(Fraction(1), Fraction(-1), Interval.point(0))
        product = left * right
        self.assertEqual(product.center, 1)
        self.assertEqual(product.linear, 0)
        self.assertEqual(product.remainder.hi, 0)
        self.assertEqual(product.remainder.lo, -1)

    def test_affine_containment_allows_rebased_center_and_linear(self) -> None:
        inner = AffineScalar(
            Fraction(1),
            Fraction(2),
            Interval(Fraction(-1, 100), Fraction(1, 100)),
        )
        outer = AffineScalar(
            Fraction(1001, 1000),
            Fraction(201, 100),
            Interval(Fraction(-3, 100), Fraction(3, 100)),
        )
        self.assertTrue(outer.contains_affine(inner))
        narrow = AffineScalar(
            outer.center,
            outer.linear,
            Interval(Fraction(-1, 1000), Fraction(1, 1000)),
        )
        self.assertFalse(narrow.contains_affine(inner))

    def test_whole_cell_rank_and_inertia(self) -> None:
        matrix = matrix_from_json(
            affine_diagonal(
                [
                    complex_affine(2, real_linear=1),
                    complex_affine(-1, real_linear=Fraction(1, 4)),
                    complex_affine(3),
                ]
            )
        )
        self.assertTrue(determinant_excludes_zero(matrix))
        witness = certify_whole_cell_inertia(matrix)
        self.assertEqual(witness.complex_inertia, (2, 1, 0))
        self.assertLess(witness.inverse_perturbation_bound, 1)

    def test_singular_cell_is_refused(self) -> None:
        matrix = matrix_from_json(
            affine_diagonal(
                [
                    complex_affine(0, real_linear=1),
                    complex_affine(1),
                    complex_affine(1),
                ]
            )
        )
        self.assertFalse(determinant_excludes_zero(matrix))
        with self.assertRaisesRegex(ValueError, "center form is singular"):
            certify_whole_cell_inertia(matrix)

    def test_nonhermitian_affine_coefficient_is_refused(self) -> None:
        matrix = matrix_from_json(
            [
                [complex_affine(1), complex_affine(1, imag=1)],
                [complex_affine(1, imag=1), complex_affine(1)],
            ]
        )
        with self.assertRaisesRegex(ValueError, "imaginary center"):
            require_hermitian_enclosure(matrix, "mutation")

    def test_affine_matrix_product(self) -> None:
        left = matrix_from_json(
            [[complex_affine(1, real_linear=1), complex_affine(0)]]
        )
        right = matrix_from_json(
            [[complex_affine(1, real_linear=-1)], [complex_affine(2)]]
        )
        product = matrix_multiply(left, right)
        self.assertEqual(product[0][0].re.center, 1)
        self.assertEqual(product[0][0].re.linear, 0)
        self.assertEqual(
            product[0][0].re.remainder.lo,
            -1,
        )

    def test_orientation_correct_matrix_defect(self) -> None:
        incoming = matrix_from_json([[complex_affine(3)]])
        outgoing_horizon = matrix_from_json([[complex_affine(1)]])
        outgoing_infinity = matrix_from_json([[complex_affine(2)]])
        defect = matrix_add(
            outgoing_horizon,
            outgoing_infinity,
            matrix_negate(incoming),
        )
        self.assertEqual(defect[0][0].re.value_interval(), Interval.point(0))
        self.assertEqual(defect[0][0].im.value_interval(), Interval.point(0))

    def test_subdivided_handoff_is_independently_classified(self) -> None:
        result = validate_channel_handoff_algebra(
            synthetic_subdivided_handoff()
        )
        self.assertTrue(result["parent_promoted"])
        self.assertEqual(result["unresolved_cells"], [])
        self.assertEqual(
            result["certified_cells"]["q0"]["inertia"]["gminus"].complex_inertia,
            (3, 0, 0),
        )
        encoded = json.dumps(json_ready(result), sort_keys=True)
        self.assertIn('"complex_inertia": [3, 0, 0]', encoded)
        self.assertIn('"normalized_affine_parameter": "e in [-1,1]"', encoded)
        origins = result["certified_cells"]["q0"]["origin_blocks"]["Iminus"]
        self.assertEqual(origins["additional"]["inertia"], (2, 0, 0))
        self.assertEqual(origins["einstein"]["inertia"], (1, 0, 0))
        self.assertEqual(origins["mixed_status"], "EXACT_ZERO")
        self.assertEqual(origins["mixed_rank"], 0)

    def test_wrong_generator_is_refused(self) -> None:
        document = synthetic_subdivided_handoff()
        document["cells"][0]["affine_generator"] = 7316
        with self.assertRaisesRegex(ValueError, "generator"):
            validate_channel_handoff_algebra(document)

    def test_nonzero_conservation_defect_is_refused(self) -> None:
        document = synthetic_subdivided_handoff()
        document["cells"][0]["validated_payload"]["endpoint_forms"][
            "GHplus_outward"
        ] = constant_complex_matrix(
            [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
        )
        with self.assertRaisesRegex(ValueError, "conservation defect"):
            validate_channel_handoff_algebra(document)

    def test_nonzero_origin_mixing_is_certified(self) -> None:
        matrix = matrix_from_json(
            constant_complex_matrix(
                [[2, 0, 1], [0, -1, 0], [1, 0, 3]]
            )
        )
        result = certify_origin_blocks(matrix)
        self.assertEqual(result["additional"]["inertia"], (1, 1, 0))
        self.assertEqual(result["einstein"]["inertia"], (1, 0, 0))
        self.assertEqual(result["mixed_status"], "CERTIFIED_NONZERO")
        self.assertEqual(result["mixed_rank"], 1)

    def test_activated_certificate_from_certified_pilot(self) -> None:
        document = build_classification(
            synthetic_subdivided_handoff(),
            handoff_sha256="a" * 64,
        )
        verify_activated_document(document)
        self.assertEqual(document["lifecycle"], "CERTIFIED")
        self.assertTrue(
            document["parent"]["additional_global_channel_classified"]
        )
        self.assertTrue(document["cells"][0][
            "additional_global_direction_survives"
        ])
        self.assertFalse(
            document["parent"]["full_scattering_matrix_constructed"]
        )
        self.assertTrue(
            document["parent"]["one_sided_J_isometry_constructed"]
        )
        self.assertEqual(
            document["cells"][0]["one_sided_relation"]["input"],
            "Iminus",
        )

    def test_sixteen_cell_cover_activates_without_coarse_hulling(self) -> None:
        handoff = synthetic_sixteen_cell_handoff()
        algebra = validate_channel_handoff_algebra(handoff)
        self.assertEqual(list(algebra["certified_cells"]), [
            f"q{index}" for index in range(16)
        ])
        document = build_classification(handoff, handoff_sha256="b" * 64)
        verify_activated_document(document)
        self.assertEqual(len(document["cells"]), 16)
        self.assertTrue(document["parent"]["all_cells_resolved"])
        self.assertTrue(
            document["parent"]["one_sided_J_isometry_constructed"]
        )

    def test_activated_certificate_refuses_gap_in_cell_cover(self) -> None:
        document = build_classification(
            synthetic_sixteen_cell_handoff(),
            handoff_sha256="c" * 64,
        )
        document["cells"][8]["omega_interval"][0] = "2057/4096"
        with self.assertRaisesRegex(ValueError, "gap, overlap"):
            verify_activated_document(document)

    def test_activated_certificate_refuses_scattering_promotion(self) -> None:
        document = build_classification(
            synthetic_subdivided_handoff(),
            handoff_sha256="a" * 64,
        )
        document["parent"]["full_scattering_matrix_constructed"] = True
        with self.assertRaisesRegex(
            ValueError, "full[_ ]scattering_matrix_constructed"
        ):
            verify_activated_document(document)

    def test_independent_activated_verifier_accepts_sixteen_cells(self) -> None:
        handoff = synthetic_sixteen_cell_handoff()
        document = build_classification(handoff, handoff_sha256="d" * 64)
        independently_verify_activated_documents(
            handoff,
            document,
            handoff_sha256="d" * 64,
        )

    def test_independent_activated_verifier_rejects_claim_drift(self) -> None:
        handoff = synthetic_sixteen_cell_handoff()
        document = build_classification(handoff, handoff_sha256="e" * 64)
        document["cells"][3]["Iplus"]["inertia"] = [2, 1, 0]
        with self.assertRaisesRegex(SystemExit, "Iplus inertia changed"):
            independently_verify_activated_documents(
                handoff,
                document,
                handoff_sha256="e" * 64,
            )

    def test_independent_verifier_rejects_deleted_additional_origin(self) -> None:
        handoff = synthetic_sixteen_cell_handoff()
        document = build_classification(handoff, handoff_sha256="f" * 64)
        document["cells"][7]["additional_origin_dimension"] = 1
        with self.assertRaisesRegex(SystemExit, "horizon-origin dimensions"):
            independently_verify_activated_documents(
                handoff,
                document,
                handoff_sha256="f" * 64,
            )


if __name__ == "__main__":
    unittest.main()
