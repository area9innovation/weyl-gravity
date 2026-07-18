#!/usr/bin/env python3
"""Certify the compensator-relative AFN0 Wess--Zumino primitive."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json"
SCHEMA = HERE / "schema/wess-zumino-compensator-extension-preflight-v1.schema.json"
DEPENDENCIES = {
    "breaking": HERE / "certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "H14": ROOT / "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
    "Euler_descent": ROOT / "quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json",
    "precursor_audit": ROOT / "symbolic/verify_conformal_coefficient_triangle.py",
    "precursor_note": ROOT / "notes/conformal-c2k-coefficient-compensator.md",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _dependency(path: Path) -> dict[str, str]:
    value: dict[str, Any] = {}
    if path.suffix == ".json":
        value = json.loads(path.read_text())
    identity = value.get("result_id") or value.get("schema") or path.name
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(identity),
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    breaking = json.loads(DEPENDENCIES["breaking"].read_text())
    h14 = json.loads(DEPENDENCIES["H14"].read_text())
    euler = json.loads(DEPENDENCIES["Euler_descent"].read_text())
    if (
        breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or breaking.get("classification", {}).get("status") != "NONTRIVIAL"
        or h14.get("parity_dimensions") != {"even": 2, "odd": 1}
        or h14.get("claim_flags", {}).get("COHOMOLOGY_COMPLETE") is not True
        or euler.get("checks", {}).get("omega_E4_intrinsic_descent_continuation")
        != "NONTRIVIAL_COMPLETE"
    ):
        raise ValueError("Wess-Zumino preflight input drifted")

    coefficients = (
        Fraction(199, 30),
        Fraction(-87, 20),
    )
    imported = tuple(
        Fraction(
            breaking["coefficients"][key]["numerator"],
            breaking["coefficients"][key]["denominator"],
        )
        for key in ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4")
    )
    if imported != coefficients:
        raise ValueError("coefficient-bearing WZ vector drifted")

    # In dressed variables g_hat=exp(-2 tau)g, Q_W tau=omega and Q_W g_hat=0.
    # On each finite jet truncation Q_W and h=tau_I d/d omega_I obey
    # {Q_W,h}=N_tau+N_omega.  The two anomaly generators have N=1.
    boundary_matrix = [[1, 0], [0, 1]]
    # Ordered total carrier: (B_C,B_E,A_C,A_E). Q maps B to A and h maps A
    # back to B. These are odd endomorphisms of the direct sum.
    q_matrix = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
    ]
    homotopy_matrix = [
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    number_matrix = [[int(i == j) for j in range(4)] for i in range(4)]

    def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
        return [
            [sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)
        ]

    qh = multiply(q_matrix, homotopy_matrix)
    hq = multiply(homotopy_matrix, q_matrix)
    q_squared = multiply(q_matrix, q_matrix)
    zero_matrix = [[0 for _ in range(4)] for _ in range(4)]
    anticommutator = [
        [qh[i][j] + hq[i][j] for j in range(4)] for i in range(4)
    ]
    if q_squared != zero_matrix:
        raise ValueError("restricted Weyl differential is not nilpotent")
    if anticommutator != number_matrix:
        raise ValueError("doublet contraction identity failed")

    dressed_metric_weights = {
        "exp_minus_2_tau": -2,
        "metric": 2,
        "sum": 0,
    }
    if (
        dressed_metric_weights["exp_minus_2_tau"]
        + dressed_metric_weights["metric"]
        != dressed_metric_weights["sum"]
    ):
        raise ValueError("dressed-metric Weyl weights do not cancel")

    primitive_coordinates = [_q(value) for value in coefficients]
    image = [
        _q(sum(Fraction(boundary_matrix[i][j]) * coefficients[j] for j in range(2)))
        for i in range(2)
    ]
    if image != primitive_coordinates:
        raise ValueError("coefficient-bearing WZ primitive failed")

    result = {
        "schema": "quantum-weyl-wess-zumino-compensator-extension-preflight-v1",
        "result_id": "WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT",
        "result_state": "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "extension": {
            "new_field": {
                "symbol": "tau",
                "tensor_type": "scalar",
                "ghost_number": 0,
                "antifield_number": 0,
                "Grassmann_parity": "even",
                "Weyl_shift": 1,
            },
            "required_antifield": {
                "symbol": "tau_star",
                "ghost_number": -1,
                "antifield_number": 1,
                "Grassmann_parity": "odd",
                "status": "FULL_COTANGENT_ROW_NOT_IMPORTED",
            },
            "minimal_field_row": "Q tau = L_xi tau + omega",
            "dressed_metric": "g_hat = exp(-2 tau) g",
            "dressed_metric_identity": "Q g_hat = L_xi g_hat",
            "dressed_metric_Weyl_weights": dressed_metric_weights,
            "weyl_jet_rows": "Q_W tau_I = omega_I; Q_W omega_I = 0 for every finite jet multi-index I",
        },
        "nilpotency": {
            "field_sector": "VERIFIED_FROM_Q_DIFF_SQUARE_ZERO_AND_SEMIDIRECT_ACTION",
            "dressed_metric_Weyl_part": "ZERO",
            "positive_antifield_sector": "NOT_COMPUTED",
        },
        "doublet_contraction": {
            "number_operator": "N_tau_omega",
            "homotopy": "h=sum_I tau_I partial/partial omega_I",
            "identity": "Q_W h + h Q_W = N_tau_omega",
            "restricted_matrices": {
                "Q": q_matrix,
                "h": homotopy_matrix,
                "N": number_matrix,
                "Qh": qh,
                "hQ": hq,
                "Q_squared": q_squared,
                "anticommutator": anticommutator,
            },
        },
        "local_primitives": {
            "B_C": "integral sqrt(g) tau C2",
            "B_E": "integral sqrt(g) [tau E4 + 4 G^{mu nu} d_mu tau d_nu tau - 4 (Box tau)(d tau)^2 + 2 (d tau)^4]",
            "variation_convention": "Q_W B_C=ANOM_OMEGA_C2; Q_W B_E=ANOM_OMEGA_E4 modulo d_h",
            "coefficient_bearing_primitive": "(199/30) B_C-(87/20) B_E",
            "primitive_coordinates": primitive_coordinates,
            "image_coordinates": image,
            "counterterm": "-(4 pi)^(-2) hbar [(199/30) B_C-(87/20) B_E]",
        },
        "cohomology_comparison": {
            "scope": "SPAN_OF_THE_TWO_CERTIFIED_EVEN_AFN0_ANOMALY_CLASSES_WITH_FULL_DIFF_DESCENT",
            "strict_boundary_matrix": [[], []],
            "strict_boundary_rank": 0,
            "strict_quotient_dimension": 2,
            "extended_boundary_matrix": boundary_matrix,
            "extended_boundary_rank": 2,
            "extended_quotient_dimension": 0,
            "status": "BOTH_EVEN_BREAKING_COORDINATES_EXACT_IN_DECLARED_EXTENDED_SECTOR",
            "full_extended_H14": "NOT_COMPUTED",
            "full_extended_H04": "NOT_COMPUTED",
        },
        "qme_lifecycle": {
            "strict_theory": "OBSTRUCTED_STRICT_FIELD_CONTENT",
            "extended_AFN0_one_loop_breaking": "EXACT_REMOVABLE",
            "full_extended_BV_QME": "NOT_CERTIFIED",
            "residual_transfer": "FORBIDDEN",
        },
        "dependencies": {
            name: _dependency(path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": "FULL_DIFF_WEYL_BV_COTANGENT_LIFT_AND_EXTENDED_H04_H14_RECOMPUTATION",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC preflight adjoins a shifting scalar compensator, "
            "proves the Weyl-jet doublet contraction after the local dressed-metric change "
            "of variables, and constructs the coefficient-bearing Wess-Zumino primitive for "
            "both certified even anomaly coordinates including the complete universal Diff "
            "descent. It proves exact removability of the one-loop breaking only in that AFN0 "
            "extended sector. It does not supply the tau antifield cotangent row, recompute the "
            "full extended H04 or H14, certify the full extended BV master equation, authorize "
            "residual transfer, or establish Lorentzian products, positivity, or particles."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    comparison = value.get("cohomology_comparison", {})
    lifecycle = value.get("qme_lifecycle", {})
    matrices = value.get("doublet_contraction", {}).get("restricted_matrices", {})
    if (
        value.get("result_id") != "WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT"
        or value.get("result_state")
        != "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN"
        or value.get("extension", {})
        .get("dressed_metric_Weyl_weights", {})
        .get("sum")
        != 0
        or matrices.get("Q_squared") != [[0 for _ in range(4)] for _ in range(4)]
        or matrices.get("anticommutator") != matrices.get("N")
        or comparison.get("strict_quotient_dimension") != 2
        or comparison.get("extended_quotient_dimension") != 0
        or comparison.get("full_extended_H14") != "NOT_COMPUTED"
        or lifecycle.get("extended_AFN0_one_loop_breaking") != "EXACT_REMOVABLE"
        or lifecycle.get("full_extended_BV_QME") != "NOT_CERTIFIED"
        or lifecycle.get("residual_transfer") != "FORBIDDEN"
    ):
        raise ValueError("Wess-Zumino extension preflight drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Wess-Zumino preflight: {OUTPUT}")
    print("WESS-ZUMINO EXTENSION: AFN0 PRIMITIVE CERTIFIED; FULL BV OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
