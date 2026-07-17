"""Physical coefficient-ring audit for the generic axial Weyl--Maxwell module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
OPERATOR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_physical_ring.schema.json"


class AxialPhysicalRingError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialPhysicalRingError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _audit() -> dict[str, Any]:
    rows, symbols = _generic_rows()
    eigenvalue, momentum, frequency = symbols["lambda"], symbols["k"], symbols["omega"]
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    equations = sp.Matrix([rows["metric_t"], rows["metric_x"], rows["maxwell_t"], rows["maxwell_x"]])
    hessian = (sp.diag(eigenvalue, -eigenvalue, 1, 1) * equations).jacobian(coefficients).applyfunc(sp.factor)

    upper_left = hessian[:2, :2]
    unit_block = hessian[:2, 2:]
    lower_left = hessian[2:, :2]
    lower_right = hessian[2:, 2:]
    _require(unit_block == sp.diag(eigenvalue, -eigenvalue), "unit block changed")
    _require(sp.factor(unit_block.det() + eigenvalue**2) == 0, "unit minor changed")

    schur = (lower_left - lower_right * unit_block.inv() * upper_left).applyfunc(sp.factor)
    extra = sp.factor(frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3))
    einstein = sp.factor((frequency**2 - momentum**2 - eigenvalue) ** 2 - 2 * eigenvalue)
    reduced = (schur / extra).applyfunc(sp.factor)

    a = sp.factor(momentum**4 + 2 * momentum**2 * eigenvalue - momentum**2 * frequency**2 + eigenvalue**2 - 2 * eigenvalue)
    b = sp.factor(momentum * frequency * (momentum**2 + 2 * eigenvalue - frequency**2))
    d = sp.factor(momentum**2 * frequency**2 - eigenvalue**2 + 2 * eigenvalue * frequency**2 + 2 * eigenvalue - frequency**4)
    expected_reduced = -sp.Rational(3, 4) * sp.Matrix([[a, b], [b, d]])
    _require((reduced - expected_reduced).applyfunc(sp.factor) == sp.zeros(2), "Schur factorization changed")
    _require(sp.factor(reduced.det() + sp.Rational(9, 16) * eigenvalue * (eigenvalue - 2) * einstein) == 0, "reduced determinant changed")

    bezout_a = sp.factor(frequency**2 * (momentum**2 + 2 * eigenvalue - frequency**2))
    bezout_b = sp.factor(-momentum * frequency * (momentum**2 + 2 * eigenvalue - frequency**2))
    bezout_d = sp.factor(-eigenvalue * (eigenvalue - 2))
    bezout_target = eigenvalue**2 * (eigenvalue - 2) ** 2
    _require(sp.factor(bezout_a * a + bezout_b * b + bezout_d * d - bezout_target) == 0, "Bezout witness changed")

    zero_momentum_reduced = reduced.subs(momentum, 0).applyfunc(sp.factor)
    expected_zero = -sp.Rational(3, 4) * sp.diag(
        eigenvalue * (eigenvalue - 2),
        -eigenvalue**2 + 2 * eigenvalue * frequency**2 + 2 * eigenvalue - frequency**4,
    )
    _require(
        (zero_momentum_reduced - expected_zero).applyfunc(sp.factor) == sp.zeros(2),
        "k=0 Schur block changed",
    )

    extra_representatives_zero = sp.Matrix(
        [[-eigenvalue, 0], [0, -sp.Rational(2, 3)], [eigenvalue, 0], [0, eigenvalue]]
    )
    _require(extra_representatives_zero[2:, :].det() == eigenvalue**2, "k=0 extra representatives lost independence")

    determinant = sp.factor(hessian.det())
    expected_determinant = sp.factor(
        sp.Rational(9, 16) * eigenvalue**3 * (eigenvalue - 2) * extra**2 * einstein
    )
    _require(sp.factor(determinant - expected_determinant) == 0, "full determinant changed")

    resultant = sp.factor(sp.resultant(extra, einstein, frequency))
    expected_resultant = sp.factor(sp.Rational(4, 81) * (9 * eigenvalue - 2) ** 2)
    _require(sp.factor(resultant - expected_resultant) == 0, "p-q resultant changed")

    return {
        "physical_coefficient_ring": "R_phys=Q[lambda,k,lambda^(-1),(lambda-2)^(-1),(9lambda-2)^(-1)]",
        "polynomial_variable": "omega",
        "not_inverted": ["k", "omega", "p", "q"],
        "unit_two_by_two_minor": "-lambda^2",
        "block_reduction": {
            "unit_block": _matrix_strings(unit_block),
            "Schur_complement": _matrix_strings(schur),
            "factorization": "Schur=p*T",
            "p": str(extra),
            "T": _matrix_strings(reduced),
            "det_T": str(sp.factor(reduced.det())),
            "q": str(einstein),
        },
        "Bezout_unit_ideal_witness": {
            "T_common_factor_removed": "-3/4",
            "entries": {"a": str(a), "b": str(b), "d": str(d)},
            "coefficients": {"A": str(bezout_a), "B": str(bezout_b), "D": str(bezout_d)},
            "identity": "A*a+B*b+D*d=lambda^2*(lambda-2)^2",
            "right_hand_side_is_a_unit_in_R_phys": True,
        },
        "determinantal_ideals_over_R_phys_omega": {
            "I1": "(1)",
            "I2": "(1)",
            "I3": "(p)",
            "I4": "(p^2*q)",
            "no_k_torsion": True,
            "reason": "I2 contains the unit minor -lambda^2 and I3/p is generated by the entries of T, whose displayed Bezout combination is a unit",
        },
        "specialization": {
            "physical_lambda": "lambda=ell*(ell+1), ell>=2",
            "compact_momentum": "k=2*pi*n/L, every n in Z including n=0",
            "fiberwise_Smith_invariants": ["1", "1", "p", "p*q"],
            "p_q_resultant": str(resultant),
            "p_q_coprime_on_every_physical_specialization": True,
            "target_fiber_module": "K[omega]/(p) direct_sum K[omega]/(p*q)",
            "CRT_target_fiber_module": "(K[omega]/(p))^2 direct_sum K[omega]/(q)",
            "extra_quotient_fiber_module": "(K[omega]/(p))^2",
        },
        "zero_momentum_audit": {
            "T_at_k_zero": _matrix_strings(zero_momentum_reduced),
            "extra_representatives_order_Ht_Hx_Qt_Qx": _matrix_strings(extra_representatives_zero),
            "extra_representative_independence_minor": "lambda^2",
            "same_fiberwise_invariant_factors": True,
            "zero_momentum_retained": True,
        },
    }


def build_certificate() -> dict[str, Any]:
    source = json.loads(OPERATOR_CERTIFICATE.read_text(encoding="utf-8"))
    _require(source["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR", "operator input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-physical-ring-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_PHYSICAL_RING",
        "result_state": "PHYSICAL_RING_FITTING_IDEALS_AND_ALL_MOMENTUM_SPECIALIZATION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_PHYSICAL_RING_AND_K_ZERO_AUDIT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {str(OPERATOR_CERTIFICATE.relative_to(ROOT)): _sha256(OPERATOR_CERTIFICATE)},
        },
        "domain": "generic axial ell>=2 Weyl-Maxwell coefficient complex over a physical localization that retains every real compact momentum, including k=0",
        "audit": _audit(),
        "classification": {
            "generic_fraction_field_alone_controls_specialization": False,
            "physical_ring_determinantal_ideals_certified": True,
            "all_physical_lambda_specializations_certified": True,
            "all_compact_momenta_including_zero_certified": True,
            "extra_quotient_two_cyclic_summands_on_every_physical_fiber": True,
            "global_unimodular_Smith_transformations_over_multivariate_ring_claimed": False,
            "quantum_or_causal_claim": False,
        },
        "interpretation": "The earlier fraction-field Smith calculation is only generic. The physical-ring Schur and Bezout audit repairs the specialization theorem without inverting k or omega: the Fitting ideals are (1),(1),(p),(p^2 q), and every physical lambda and compact momentum fiber, including k=0, has Smith factors 1,1,p,pq. The canonical extra quotient on each physical fiber is two copies of K[omega]/(p).",
        "next_gate": "use the physical-ring theorem in the compact linear manuscript and keep the stronger claim of explicit global unimodular Smith transformations over R_phys[omega] fail-closed unless those transformations are constructed",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate proves the physical-ring determinantal ideals and every physical momentum specialization. It does not claim a global Smith normal form over the multivariate ring, final residual descent, nonlinear closure, causal scattering, or quantum interpretation.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_physical_ring --verify bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_physical_ring.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_physical_ring",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"stale physical-ring certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
