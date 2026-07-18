#!/usr/bin/env python3
"""Project the pure-vector ghost n=1+n=2 slice with exact CPT kernels.

The Hodge-resolvent reduction leaves five n=1/n=2 carriers.  Two are the
pure minimal-vector rows.  On the scalar-flat source complement their sum is
the minimal-operator sign-flip difference with the already known pure-vector
n=3 triangle removed.  CPT-IV then reduces it to structures 1, 3 and 14.

This module evaluates that two-carrier sum in the certified scalar-flat
I10/I24/I25/I28/I29 quotient.  It deliberately leaves the three carriers
containing D_W=delta W d open.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n1-n2-vector-cpt-projection-v1.schema.json"
DEPENDENCIES = {
    "Hodge_resolvent_reduction": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "n3_triangle": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "CPT_universal_kernels": ROOT
    / "quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
    "carrier_manifest": ROOT
    / "quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
}

CHANNELS: tuple[tuple[str, tuple[int, int, int]], ...] = (
    ("I10", (0, 1, 2)),
    ("I24", (0, 1, 2)),
    ("I24", (1, 0, 2)),
    ("I24", (2, 0, 1)),
    ("I25", (0, 1, 2)),
    ("I25", (1, 0, 2)),
    ("I25", (2, 0, 1)),
    ("I28", (0, 1, 2)),
    ("I28", (0, 2, 1)),
    ("I28", (1, 2, 0)),
    ("I29", (0, 1, 2)),
)

MOMENTUM_FIXTURES = (
    ((1, -1, -2, -2), (-2, 1, 0, 2)),
    ((1, 1, -2, 0), (0, 0, 1, 1)),
    ((1, 0, 0, 0), (-2, 1, 1, 0)),
    ((1, -1, 2, -1), (-2, 1, -2, -1)),
    ((-1, 1, 2, 0), (2, 0, 0, 0)),
    ((-1, 0, -1, -2), (-2, 0, 0, -1)),
    ((2, -1, 0, 1), (-1, -1, 2, -2)),
    ((1, 2, -1, -2), (-1, -1, 2, 1)),
    ((2, 0, 0, -1), (1, 1, -2, -1)),
    ((2, 0, -2, 1), (0, -1, 2, -1)),
)

A1, A2, X1, X2, X3 = sp.symbols("alpha1 alpha2 x1 x2 x3", nonzero=True)
A3 = 1 - A1 - A2
DELTA = A2 * A3 * X1 + A1 * A3 * X2 + A1 * A2 * X3
GAMMA1 = sp.Rational(1, 3) / DELTA
GAMMA3 = 2 * A1 * A2 / DELTA
GAMMA14 = -(2 * A3 - 4 * A3**2) / (X3 * DELTA)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _canonical(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(value)))


def _tt_basis(momentum: sp.Matrix) -> list[sp.Matrix]:
    raw = sp.Matrix([list(momentum)]).nullspace()
    orthogonal: list[sp.Matrix] = []
    for vector in raw:
        reduced = vector
        for previous in orthogonal:
            reduced -= previous * (previous.dot(reduced) / previous.dot(previous))
        orthogonal.append(reduced)
    projectors = [vector * vector.T / vector.dot(vector) for vector in orthogonal]
    return [
        projectors[0] - projectors[1],
        projectors[0] - projectors[2],
        orthogonal[0] * orthogonal[1].T + orthogonal[1] * orthogonal[0].T,
        orthogonal[0] * orthogonal[2].T + orthogonal[2] * orthogonal[0].T,
        orthogonal[1] * orthogonal[2].T + orthogonal[2] * orthogonal[1].T,
    ]


def _riemann(momentum: sp.Matrix, ricci: sp.Matrix) -> list[list[sp.Matrix]]:
    """Linearized R_abmn with Ricci contraction equal to ``ricci``."""

    box = (momentum.T * momentum)[0]
    metric_wave = 2 * ricci / box
    result = [[sp.zeros(4) for _ in range(4)] for _ in range(4)]
    for mu, nu in itertools.product(range(4), repeat=2):
        matrix = sp.zeros(4)
        for a, b in itertools.product(range(4), repeat=2):
            matrix[a, b] = sp.Rational(1, 2) * (
                -momentum[mu] * momentum[b] * metric_wave[a, nu]
                - momentum[nu] * momentum[a] * metric_wave[b, mu]
                + momentum[nu] * momentum[b] * metric_wave[a, mu]
                + momentum[mu] * momentum[a] * metric_wave[b, nu]
            )
        result[mu][nu] = matrix
    return result


def _source_values(
    momenta: list[sp.Matrix], tensors: list[sp.Matrix]
) -> tuple[sp.Expr, sp.Expr]:
    r1 = _riemann(momenta[0], tensors[0])
    r2 = _riemann(momenta[1], tensors[1])
    p3 = tensors[2]
    structure3 = sum(
        sp.trace(r1[mu][nu] * r2[mu][nu] * p3)
        for mu, nu in itertools.product(range(4), repeat=2)
    )
    div1 = [sum((momenta[0][mu] * r1[mu][nu] for mu in range(4)), sp.zeros(4)) for nu in range(4)]
    div2 = [sum((momenta[1][mu] * r2[mu][nu] for mu in range(4)), sp.zeros(4)) for nu in range(4)]
    # Two Fourier derivatives contribute i^2=-1.
    structure14 = -sum((sp.trace(div1[nu] * div2[nu] * p3) for nu in range(4)), sp.S.Zero)
    return sp.factor(structure3), sp.factor(structure14)


def _carrier_value(
    carrier: str,
    momenta: list[sp.Matrix],
    tensors: list[sp.Matrix],
    labels: tuple[int, int, int],
) -> sp.Expr:
    k1, k2, k3 = [momenta[index] for index in labels]
    first, second, third = [tensors[index] for index in labels]
    if carrier == "I10":
        return sp.trace(first * second * third)
    if carrier == "I24":
        return -(k2.T * first * k3)[0] * sp.trace(second * third)
    if carrier == "I25":
        return -((second * k3).T * first * (third * k2))[0]
    if carrier == "I28":
        return (k1.T * third * k2)[0] * (k3.T * first * second * k3)[0]
    if carrier == "I29":
        return -(
            (k2.T * first * k2)[0]
            * (k3.T * second * k3)[0]
            * (k1.T * third * k1)[0]
        )
    raise ValueError(carrier)


def _projection_coordinates(boxes: tuple[sp.Expr, sp.Expr, sp.Expr]) -> tuple[list[sp.Expr], list[sp.Expr]]:
    x1, x2, x3 = boxes
    structure3 = [
        -2,
        -1 / x2,
        -1 / x1,
        -(x1 + x2) / (x1 * x2),
        -2 / x1,
        -2 / x2,
        0,
        0,
        0,
        0,
        0,
    ]
    structure14 = [
        -(x1 + x2 - x3) / 2,
        0,
        0,
        -1,
        -1,
        -1,
        0,
        0,
        0,
        0,
        0,
    ]
    return [sp.factor(value) for value in structure3], [sp.factor(value) for value in structure14]


def _verify_projection_fixtures() -> dict[str, Any]:
    residuals = 0
    tensor_rows = 0
    convention_rows = 0
    for first, second in MOMENTUM_FIXTURES:
        momenta = [sp.Matrix(first), sp.Matrix(second)]
        momenta.append(-momenta[0] - momenta[1])
        boxes = tuple((momentum.T * momentum)[0] for momentum in momenta)
        c3, c14 = _projection_coordinates(boxes)
        bases = [_tt_basis(momentum) for momentum in momenta]
        for momentum, basis in zip(momenta, bases):
            for ricci in basis:
                riemann = _riemann(momentum, ricci)
                contraction = sp.Matrix(
                    4,
                    4,
                    lambda a, nu: sum(
                        riemann[mu][nu][mu, a] for mu in range(4)
                    ),
                )
                if sp.simplify(contraction - ricci) != sp.zeros(4):
                    raise ValueError("linearized Riemann/Ricci convention drifted")
                for nu in range(4):
                    divergence = sum(
                        (
                            momentum[mu] * riemann[mu][nu]
                            for mu in range(4)
                        ),
                        sp.zeros(4),
                    )
                    contracted_bianchi = sp.Matrix(
                        4,
                        4,
                        lambda a, b: momentum[a] * ricci[b, nu]
                        - momentum[b] * ricci[a, nu],
                    )
                    if sp.simplify(divergence - contracted_bianchi) != sp.zeros(4):
                        raise ValueError("contracted Bianchi convention drifted")
                convention_rows += 5
        for choice in itertools.product(range(5), repeat=3):
            tensors = [bases[index][choice[index]] for index in range(3)]
            source3, source14 = _source_values(momenta, tensors)
            carrier_values = [
                _carrier_value(carrier, momenta, tensors, labels)
                for carrier, labels in CHANNELS
            ]
            residuals += int(sp.factor(source3 - sum((a * b for a, b in zip(c3, carrier_values)), sp.S.Zero)) != 0)
            residuals += int(sp.factor(source14 - sum((a * b for a, b in zip(c14, carrier_values)), sp.S.Zero)) != 0)
            tensor_rows += 2
    if residuals:
        raise ValueError("CPT P-sector carrier projection failed")
    return {
        "momentum_fixture_count": len(MOMENTUM_FIXTURES),
        "TT_tensor_products_per_fixture": 125,
        "direct_identity_rows": tensor_rows,
        "nonzero_residual_count": residuals,
        "convention_identity_rows": convention_rows,
        "convention_nonzero_residual_count": 0,
        "grading_ansatz": {
            "structure_3_I10": "box degree 0",
            "structure_3_I24_I25": "degree-one numerator over x1*x2",
            "structure_14_I10": "box degree 1",
            "structure_14_I24_I25": "box degree 0",
        },
    }


def _channel_integrands() -> list[dict[str, Any]]:
    p3, p14 = _projection_coordinates((X1, X2, X3))
    result = []
    for index, ((carrier, labels), c3, c14) in enumerate(zip(CHANNELS, p3, p14)):
        value = sp.factor((6 * GAMMA1 if index == 0 else 0) - 2 * GAMMA3 * c3 - 2 * GAMMA14 * c14)
        result.append(
            {
                "carrier_id": carrier,
                "labels": [item + 1 for item in labels],
                "alpha_integrand": _canonical(value),
                "identically_zero": value == 0,
            }
        )
    return result


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    hodge = values["Hodge_resolvent_reduction"]
    triangle = values["n3_triangle"]
    cpt = values["CPT_universal_kernels"]
    manifest = values["carrier_manifest"]
    if (
        hodge.get("log_determinant_expansion", {}).get("carrier_count") != 5
        or triangle.get("projector_sector_expansion", {}).get("sectors", [])[0].get("subset_bits") != "000"
        or triangle.get("master_kernel", {}).get("W_and_Tr_log_multiplier") != {"numerator": -8, "denominator": 3}
        or cpt.get("source_provenance", {}).get("ancillary_file_sha256")
        != "6a9bc97cab8793aeda563513f6d0bf6ad20b387a4f52c9e1d76d7e9c27bdbd5f"
        or manifest.get("quotient_module", {}).get("generic_label_orbit_dimension") != 10
    ):
        raise ValueError("vector CPT projection dependency drifted")

    channels = _channel_integrands()
    digest = hashlib.sha256(
        json.dumps(channels, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-n1-n2-vector-cpt-projection-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION",
        "result_state": "PURE_VECTOR_N1_PLUS_N2_PROJECTED_TO_SCALAR_FLAT_CPT_CARRIER_QUOTIENT",
        "lifecycle_state": "TWO_OF_FIVE_HODGE_CARRIERS_COMBINED_PHYSICAL_SUM_EVALUATED_THREE_LONGITUDINAL_CARRIERS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": hodge["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic nonexceptional-momentum scalar-flat source complement",
            "operator_slice": "N1_VECTOR plus N2_VECTOR_VECTOR through cubic curvature order",
            "loop_prefactor": "common (4*pi)^-2 omitted",
        },
        "source_provenance": {
            "arxiv": "0911.1168",
            "ancillary_file": "anc/ffwa.m",
            "source_archive_sha256": cpt["source_provenance"]["source_archive_sha256"],
            "ancillary_file_sha256": cpt["source_provenance"]["ancillary_file_sha256"],
            "formula_rows": [1, 3, 14],
        },
        "source_CPT_rows": {
            "Gamma1": "< (1/3)/(-Omega) >_3",
            "Gamma3": "< (2 alpha1 alpha2)/(-Omega) >_3",
            "Gamma14": "< ((2 alpha3-4 alpha3^2)/Box3)/(-Omega) >_3",
            "positive_box_convention": "x_i=-Box_i and Delta=-Omega",
            "Delta": _canonical(DELTA),
        },
        "minimal_operator_sign_flip": {
            "source_operator": "H_CPT=Box+P-R/6",
            "positive_vector_base": "F=-Box+Ric corresponds to P_F=-Ric+R/6",
            "positive_vector_shifted": "F+W=-Box-Ric corresponds to P_H=+Ric+R/6",
            "W": "-2 Ric",
            "scalar_flat_specialization": "P_F=-Ric, P_H=+Ric, tr(P)=0",
            "all_P_dependent_rows": [1, 3, 4, 5, 6, 13, 14, 15, 16, 17, 26],
            "even_P_rows_cancel": [6, 13, 17],
            "single_P_scalar_trace_rows_vanish": [4, 5, 15, 16, 26],
            "surviving_rows": [1, 3, 14],
            "positive_determinant_to_source_kernel_sign": -1,
            "n3_pure_vector_calibration": "-8 Gamma1 from the zero-longitudinal projector sector",
            "n1_plus_n2_formula": "6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14",
        },
        "ordered_structure_projection": {
            "source_label_policy": "slots 1,2 are commutator curvatures and slot 3 is P; carrier labels follow the stored CPT order",
            "structure_3_coordinates": [_canonical(value) for value in _projection_coordinates((X1, X2, X3))[0]],
            "structure_14_coordinates": [_canonical(value) for value in _projection_coordinates((X1, X2, X3))[1]],
            "channels": [
                {"carrier_id": carrier, "labels": [item + 1 for item in labels]}
                for carrier, labels in CHANNELS
            ],
            "quotient_gauge": "symmetric I28 coordinate zero",
            "direct_fixture_replay": _verify_projection_fixtures(),
        },
        "vector_n1_plus_n2_channel_integrands": channels,
        "formula_digest": digest,
        "minimal_missing_carrier_theorem": {
            "missing_carriers": [
                "N1_LONGITUDINAL_SCALAR",
                "N2_VECTOR_LONGITUDINAL",
                "N2_LONGITUDINAL_LONGITUDINAL",
            ],
            "irreducible_insertion": "D_W=delta W d",
            "principal_symbol": "sigma_2(D_W)(p)=W^{mu nu} p_mu p_nu",
            "reason": "D_W is a curvature-dependent anisotropic principal-symbol insertion, not a bundle endomorphism P; the mixed row also couples scalar and vector resolvents. The imported minimal-Laplace CPT P rows therefore do not evaluate these three carriers.",
            "smallest_next_input": "covariant scalar/vector kernels with one or two D_W insertions through the required curvature order, or an equivalent direct nonminimal Endo form-factor calculation",
        },
        "claim_flags": {
            "CPT_P_SECTOR_ROWS_1_3_14_IMPORTED": True,
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED": True,
            "MINIMAL_MISSING_LONGITUDINAL_CARRIER_THEOREM_COMPUTED": True,
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED": False,
            "COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "EVALUATE_THREE_DW_LONGITUDINAL_GHOST_CARRIERS_AND_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate imports the exact CPT-IV P-sector rows needed by the pure minimal-vector part of the generic Diff-Weyl ghost determinant. On the scalar-flat source complement the P sign flip and trace identities reduce the vector n=1+n=2 sum to 6 Gamma1 S1-2 Gamma3 S3-2 Gamma14 S14, and an exact TT replay projects it to the certified scalar-flat I10/I24/I25 quotient with I28=I29=0. This evaluates the combined N1_VECTOR plus N2_VECTOR_VECTOR contribution, not the three carriers containing D_W=delta W d. Those carriers require anisotropic principal-symbol and mixed scalar/vector kernels unavailable in the imported minimal-Laplace CPT P sector. The complete generic ghost determinant, physical fourth-order Hessian, repository coefficient sum, Gamma1/Q1, residual transfer, Lorentzian QME, Hadamard, particle, positivity, scattering and unitarity claims remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    true_flags = {
        "CPT_P_SECTOR_ROWS_1_3_14_IMPORTED",
        "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED",
        "MINIMAL_MISSING_LONGITUDINAL_CARRIER_THEOREM_COMPUTED",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("vector CPT projection crossed its claim boundary")
    if len(value["vector_n1_plus_n2_channel_integrands"]) != 11:
        raise ValueError("carrier channel count drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale vector CPT projection: {OUTPUT}")
    print("GENERIC GHOST VECTOR N1+N2: CPT CARRIER PROJECTION EXACT; THREE D_W CARRIERS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
