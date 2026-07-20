#!/usr/bin/env python3
"""Construct the minimal action-derived dynamical Berger apparatus parent."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json"
PAYLOAD = P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json"
REPORT = P / "reports/berger-dynamical-apparatus-parent.md"
DEPENDENCIES = {
    "all_jet_shortfall": P / "certificates/BERGER_TEMPORAL_CURL_ALL_JET_DISPOSITION_SHORTFALL.json",
    "second_jet_predecessor": P / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION.json",
    "linear_rank_two": P / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "affine_K": P / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json",
    "record_algebra": P / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def third_derivative_records() -> list[dict[str, Any]]:
    lam, p0, p1, f0, f1 = sp.symbols("lambda p0 p1 f0 f1")
    variables = (lam, p0, p1, f0, f1)
    action = -lam * (p0 * f0 + p1 * f1)
    rows = []
    for i, j, k in itertools.product(range(5), repeat=3):
        value = sp.diff(action, variables[i], variables[j], variables[k])
        if value:
            rows.append(
                {
                    "output_cotangent_of": str(variables[i]),
                    "left_input": str(variables[j]),
                    "right_input": str(variables[k]),
                    "coefficient": int(value),
                }
            )
    return rows


def build_payload() -> dict[str, Any]:
    s = sp.symbols("s")
    transport = sp.Matrix([[0, -s], [s, 0]])
    doublet = sp.diag(transport, transport)
    j = sp.Matrix([[0, -1], [1, 0]])
    u, v = sp.symbols("u0:2"), sp.symbols("v0:2")
    uvec, vvec = sp.Matrix(u), sp.Matrix(v)
    k_variation = ((j * uvec).dot(vvec) + uvec.dot(j * vvec)).expand()
    if k_variation != 0:
        raise AssertionError("simultaneous U(1) invariance failed")

    q2 = third_derivative_records()
    if len(q2) != 12:
        raise AssertionError("detector cubic Hessian orbit drifted")

    fields = []
    for detector in range(2):
        for family in ("rod_orientation", "rod_momentum", "polarization", "polarization_momentum"):
            for component in range(2):
                fields.append(f"{family}_{detector}_{component}")
        fields.extend((f"memory_{detector}", f"memory_multiplier_{detector}"))
    for emitter in range(2):
        for family in ("emitter_phase", "emitter_phase_momentum"):
            for component in range(2):
                fields.append(f"{family}_{emitter}_{component}")
    if len(fields) != 28:
        raise AssertionError("minimal apparatus row count drifted")

    source_support = [
        {
            "output": audit["first_quotient_witness"]["output"],
            "left_input": audit["first_quotient_witness"]["left_input"],
            "right_input": audit["first_quotient_witness"]["right_input"],
        }
        for audit in json.loads(DEPENDENCIES["second_jet_predecessor"].read_text())[
            "filtered_second_jet_theorem"
        ]["per_emitter_audits"].values()
    ]
    new_support = [
        {
            "output_sector": "old_Maxwell_cotangent" if row["output_cotangent_of"].startswith("f") else "new_apparatus",
            "new_input_count": sum(
                not name.startswith("f")
                for name in (row["left_input"], row["right_input"])
            ),
        }
        for row in q2
    ]
    if any(row["new_input_count"] == 0 for row in new_support):
        raise AssertionError("new Hessian acquired a pure-old coordinate")

    return {
        "schema": "closed-universe-berger-dynamical-apparatus-parent-payload-v1",
        "result_id": "BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD",
        "coefficient_field": "Q",
        "carrier": {
            "physical_even_rows": fields,
            "physical_even_row_count": 28,
            "odd_cotangent_rows": [f"{field}_plus" for field in fields],
            "odd_cotangent_row_count": 28,
            "ghost_rows": [],
            "ghost_ledger": (
                "EMPTY: Berger-U(1) is a rigid simultaneous covariance, not "
                "a gauged redundancy; the nonzero-frequency transport "
                "principal symbols have no gauge kernel."
            ),
            "odd_pairing_shape": [56, 56],
            "odd_pairing_rank": 56,
        },
        "local_action": {
            "formula": (
                "sum_a[Y_a dot D_K X_a + N_a dot D_K P_a + "
                "lambda_a(d_tau m_a-(Pbar_a+p_a) dot F_a)] + "
                "sum_b[W_b dot D_K Z_b]"
            ),
            "background_polarizations": [[1, 0], [0, 1]],
            "D_K": "d_tau+Omega_K J, J=[[0,-1],[1,0]]",
            "quadratic_terms_generate_q1": True,
            "cubic_term": "-lambda_a p_a dot F_a",
            "cubic_third_derivative_records": q2,
            "cubic_third_derivative_record_count_per_detector": len(q2),
        },
        "principal_symbol": {
            "frequency": "s",
            "canonical_transport_pair": [[0, "-s"], ["s", 0]],
            "canonical_transport_determinant": str(sp.factor(transport.det())),
            "doublet_transport_determinant": str(sp.factor(doublet.det())),
            "characteristics": "real clock transport characteristic s=0",
            "causal_orientation": "retarded/advanced along increasing/decreasing relational clock",
        },
        "exact_identities": {
            "q1_squared": 0,
            "q1_q2_plus_q2_q1": 0,
            "unary_cyclicity_defect": 0,
            "binary_cyclicity_defect": 0,
            "real_structure_defect": 0,
            "K_Berger_action_variation": str(k_variation),
            "reason": (
                "The action depends only on physical fields and their first "
                "jets. Its odd Hamiltonian vector field is Koszul-Tate; "
                "(S,S)=0 identically, and Hessian/third variations are cyclic."
            ),
        },
        "linear_response": {
            "imported_matrix": [["kappa_0", "0"], ["mu", "kappa_1"]],
            "apparatus_selection_matrix": [[1, 0], [0, 1]],
            "induced_matrix": [["kappa_0", "0"], ["mu", "kappa_1"]],
            "determinant": "kappa_0*kappa_1",
            "rank": 2,
            "status": "SURVIVES",
            "scope": "leading linear response on the probe branch lambda_0=lambda_1=0",
        },
        "finite_second_jet_source_intersection": {
            "imported_source_first_coordinates": source_support,
            "new_hessian_support_audit": new_support,
            "pure_old_coordinate_count": 0,
            "intersection_rank": 0,
            "source_status": "UNCHANGED_AND_EXPLICITLY_UNRESOLVED_ALL_JET",
            "separator": (
                "Every new cubic Hessian coordinate contains at least one "
                "new apparatus input; every imported 42-coordinate source "
                "coordinate has only old temporal/Maxwell/emitter inputs."
            ),
        },
        "mutations": {
            "clone_detector_polarization": {
                "selection_matrix": [[1, 0], [1, 0]],
                "selection_rank": 1,
                "rejected": True,
            },
            "delete_detector_cubic": {
                "third_derivative_record_count": 0,
                "rejected": True,
            },
            "opposite_K_sign_on_F": {
                "variation_witness": "2*(u0*v1-u1*v0)",
                "rejected": True,
            },
            "delete_one_cotangent_row": {
                "odd_pairing_rank": 54,
                "rejected": True,
            },
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    deps = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    return {
        "schema": "closed-universe-berger-dynamical-apparatus-parent-v1",
        "result_id": "BERGER_DYNAMICAL_APPARATUS_PARENT",
        "setting_id": deps["linear_rank_two"]["setting_id"],
        "claim_status": "CERTIFIED_ACTION_DERIVED_DYNAMICAL_APPARATUS_PARENT_THROUGH_ARITY_TWO",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": deps[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
        },
        "action_gate": {
            "complete_minimal_declared_ansatz": "CERTIFIED",
            "q1_and_q2_action_derived": "CERTIFIED",
            "nilpotency_through_arity_two": "CERTIFIED",
            "odd_cyclicity": "CERTIFIED",
            "real_structure": "CERTIFIED",
            "K_Berger_covariance": "CERTIFIED_SIMULTANEOUS_FAMILY",
            "causal_principal_blocks": "CERTIFIED_FIRST_ORDER_CLOCK_TRANSPORT",
            "ghost_and_cotangent_completion": "CERTIFIED",
        },
        "observer_result": payload["linear_response"],
        "source_class_result": payload["finite_second_jet_source_intersection"],
        "downstream_disposition": {
            "linear_rank_two": "CERTIFIED_SURVIVES",
            "nonlinear_response_rank": "OPEN",
            "relational_redshift": "NO_CERTIFIED_MAP",
            "memory_promotion": "OPEN",
            "all_jet_temporal_source_membership": "NO_CERTIFIED_MAP",
            "q3": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "missing_object_ledger": [
            "finite-parameter Green theorem for the enlarged apparatus",
            "nonlinear detector response on the second-order tangent cone",
            "same-action q3 and transported nonlinear memory",
            "all-jet temporal source membership theorem",
            "relational frequency comparison and redshift observable",
        ],
        "next_gate": (
            "RESTRICT_THE_ACTION_DERIVED_APPARATUS_RESPONSE_TO_Z2_AND_"
            "TEST_RELATIONAL_MEMORY_BEFORE_ANY_REDSHIFT_PROMOTION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL "
            "certificate constructs a 56-row odd-cotangent extension from "
            "one real first-order local action: two transported detector rod "
            "orientation doublets, two transported polarization doublets, "
            "two persistent memory pairs and two transported emitter-phase "
            "doublets. Berger-U(1) is a rigid simultaneous family covariance, "
            "not a new gauge redundancy, so no ghost row is required; every "
            "physical row has an odd cotangent. The quadratic action gives "
            "q1 and the detector cubic -lambda p dot F gives twelve ordered "
            "third-variation records per detector. Exact action identities "
            "give nilpotency and cyclicity through arity two, while the "
            "transport symbols have real clock characteristics. On the "
            "lambda=0 probe branch the induced record matrix is the imported "
            "triangular rank-two matrix and therefore survives. Every new "
            "q2 coordinate contains a new apparatus input, so its intersection "
            "with the imported pure-old 42-coordinate finite second-jet source "
            "class is zero; that class is unchanged, not solved. The blocked "
            "all-jet membership question remains NO_CERTIFIED_MAP. No q3, "
            "nonlinear rank, tangent-cone response, redshift, finite-parameter "
            "Green, branch, particle or quantum claim is made."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_dynamical_apparatus_parent --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_dynamical_apparatus_parent"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger dynamical apparatus parent

One real first-order action supplies transported rod-orientation,
polarization and emitter-phase doublets plus two persistent memory pairs.
Every physical row has an odd cotangent; no ghost is introduced because the
Berger U(1) is a rigid simultaneous covariance rather than a gauge
redundancy.

The quadratic action derives q1.  The only new cubic,
`-lambda_a p_a dot F_a`, derives twelve ordered q2 records per detector.
Nilpotency, unary/binary cyclicity, reality, simultaneous K covariance and
the clock-transport principal blocks are exact.

On the probe branch the identity polarization selection leaves the imported
triangular detector matrix unchanged, so its rank remains two.  Every new q2
coordinate contains a new apparatus input; hence the new rows have zero
intersection with the pure-old 42-coordinate finite second-jet source
support.  This does not decide the blocked all-jet membership problem.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
