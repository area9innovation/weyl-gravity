#!/usr/bin/env python3
"""Construct the anomaly-induced Paneitz/Riegert representative of Gamma_1."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json"
SCHEMA = HERE / "schema/anomaly-induced-nonlocal-gamma1-v1.schema.json"
DEPENDENCIES = {
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "WZ_primitive": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "Q1_disposition": ROOT / "quantum-weyl/transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _solve_diagonal(diagonal: list[Fraction], target: list[Fraction]) -> list[Fraction]:
    if len(diagonal) != len(target) or any(value == 0 for value in diagonal):
        raise ValueError("singular or malformed Weyl-response system")
    return [rhs / lhs for lhs, rhs in zip(diagonal, target)]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    breaking = values["regulated_breaking"]
    primitive = values["WZ_primitive"]
    q1 = values["Q1_disposition"]

    coefficient_names = ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_BOX_R")
    imported = [
        Fraction(
            breaking["coefficients"][name]["numerator"],
            breaking["coefficients"][name]["denominator"],
        )
        for name in coefficient_names
    ]
    c, e4_coefficient, box_r = imported
    a = -e4_coefficient
    if (
        imported != [Fraction(199, 30), Fraction(-87, 20), Fraction()]
        or primitive["local_primitives"]["coefficient_bearing_primitive"]
        != "(199/30) B_C-(87/20) B_E"
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
    ):
        raise ValueError("anomaly-induced Gamma1 inputs drifted")

    # Under delta_sigma g=2 sigma g, with Ecal4=E4-(2/3) Box R,
    # delta(sqrt(g) Ecal4)=4 sqrt(g) Delta4 sigma and
    # delta int sqrt(g) R^2=-12 int sqrt(g) sigma Box R.
    # Self-adjointness of G4=Delta4^{-1} therefore gives response columns
    # (4 C2, 8 Ecal4, -12 BoxR) for the three functional carriers below.
    response_diagonal = [Fraction(4), Fraction(8), Fraction(-12)]
    target_ecal_basis = [c, -a, -Fraction(2, 3) * a]
    solution = _solve_diagonal(response_diagonal, target_ecal_basis)
    expected_solution = [Fraction(199, 120), Fraction(-87, 160), Fraction(29, 120)]
    if solution != expected_solution:
        raise ValueError("Paneitz/Riegert coefficient solve drifted")

    reconstructed_ecal = [response * coefficient for response, coefficient in zip(response_diagonal, solution)]
    reconstructed_repository = [
        reconstructed_ecal[0],
        reconstructed_ecal[1],
        -Fraction(2, 3) * reconstructed_ecal[1] + reconstructed_ecal[2],
    ]
    if reconstructed_repository != imported:
        raise ValueError("repository anomaly vector did not reconstruct")

    result = {
        "schema": "quantum-weyl-anomaly-induced-nonlocal-gamma1-v1",
        "result_id": "ANOMALY_INDUCED_NONLOCAL_GAMMA1",
        "result_state": "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "conventions": {
            "weyl_variation": "delta_sigma g_(mu nu)=2 sigma g_(mu nu)",
            "modified_euler_density": "Ecal4=E4-(2/3) Box R",
            "paneitz_operator": "Delta4=Box^2+2 R^(mu nu) nabla_mu nabla_nu-(2/3) R Box+(1/3)(nabla^mu R)nabla_mu",
            "density_law": "delta_sigma[sqrt(g) Ecal4]=4 sqrt(g) Delta4 sigma",
            "operator_density_law": "sqrt(g) Delta4[g]=sqrt(g_bar) Delta4[g_bar] for g=exp(2 sigma) g_bar",
            "local_R2_law": "delta_sigma integral sqrt(g) R^2=-12 integral sqrt(g) sigma Box R",
            "pairing": "<f,G4 g>=integral_x sqrt(g) f(x) integral_y sqrt(g) G4(x,y) g(y)",
        },
        "exact_coefficient_solve": {
            "source_basis": ["C2", "E4", "BoxR"],
            "source_vector": [_q(value) for value in imported],
            "modified_basis": ["C2", "Ecal4", "BoxR"],
            "modified_target_vector": [_q(value) for value in target_ecal_basis],
            "functional_basis": ["<Ecal4,G4 C2>", "<Ecal4,G4 Ecal4>", "integral R2"],
            "weyl_response_matrix": [
                [_q(Fraction(4)), _q(Fraction()), _q(Fraction())],
                [_q(Fraction()), _q(Fraction(8)), _q(Fraction())],
                [_q(Fraction()), _q(Fraction()), _q(Fraction(-12))],
            ],
            "solution_vector": [_q(value) for value in solution],
            "reconstructed_modified_vector": [_q(value) for value in reconstructed_ecal],
            "reconstructed_source_vector": [_q(value) for value in reconstructed_repository],
            "rank": 3,
        },
        "anomaly_induced_representative": {
            "kappa": "(4 pi)^(-2)",
            "compact_formula": "Gamma1_anom=kappa{(1/8)<Ecal4,G4[2 c C2-a Ecal4]>+(a/18) integral sqrt(g) R^2}",
            "c": _q(c),
            "a": _q(a),
            "expanded_coefficients": {
                "<Ecal4,G4 C2>": _q(solution[0]),
                "<Ecal4,G4 Ecal4>": _q(solution[1]),
                "integral_R2": _q(solution[2]),
            },
            "weyl_variation": "delta_sigma Gamma1_anom=(4 pi)^(-2) integral sqrt(g) sigma[(199/30)C2-(87/20)E4] on the exact inverse or compatible source sector",
            "BoxR_coordinate": _q(Fraction()),
            "R2_role": "converts the canonical Ecal4 representative to the certified repository BoxR=0 scheme",
            "parity_odd_coordinate": _q(Fraction()),
            "status": "COEFFICIENT_BEARING_ANOMALY_INDUCED_REPRESENTATIVE",
        },
        "green_operator_contract": {
            "signature": "Euclidean",
            "operator": "G4 is a self-adjoint generalized inverse of Delta4",
            "inverse_identity": "Delta4 G4=G4 Delta4=1-Pi_ker on the declared source space",
            "exact_variation_scope": "either Pi_ker=0 for the declared boundary problem or every source in the displayed pairing obeys Pi_ker source=0",
            "zero_mode_policy": "project to the orthogonal complement of ker Delta4; no full-anomaly claim is made for omitted kernel components, which remain separate global data",
            "boundary_policy": "closed manifold or compactly supported Weyl variation; boundary transgressions are not discarded outside that scope",
            "conformal_transport": "use the conformally transported generalized inverse on the same background and boundary problem",
            "existence_status": "CONDITIONAL_ON_DECLARED_EUCLIDEAN_GENERALIZED_INVERSE",
        },
        "wess_zumino_crosscheck": {
            "dressed_metric": "g_hat=exp(-2 tau) g",
            "finite_difference": "Gamma1_anom[g]-Gamma1_anom[g_hat]",
            "BRST_image": "(4 pi)^(-2)[(199/30) ANOM_OMEGA_C2-(87/20) ANOM_OMEGA_E4] modulo d_h",
            "relation_to_stored_primitive": "same certified BRST image as (4 pi)^(-2)[(199/30)B_C-(87/20)B_E]",
            "equality_claim": "NO_TERM_BY_TERM_EQUALITY_CLAIM_BEYOND_BRST_IMAGE_AND_DECLARED_BOUNDARY_CONDITIONS",
        },
        "undetermined_remainder": {
            "decomposition": "Gamma1^ren=Gamma1_anom+Gamma1_Weyl_invariant",
            "Weyl_invariant_nonlocal_functional": "NOT_COMPUTED",
            "finite_C2_and_R2_normalizations": "NOT_FIXED",
            "green_kernel_boundary_and_global_data": "NOT_FIXED_GLOBALLY",
            "renormalized_BV_laplacian_or_time_ordered_product": "NOT_SUPPLIED",
            "extended_classical_residual_contraction": "NOT_SUPPLIED",
        },
        "decision": {
            "anomaly_induced_nonlocal_Gamma1": "CERTIFIED_CONDITIONAL_EUCLIDEAN_REPRESENTATIVE",
            "complete_finite_nonlocal_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
            "Bridge_4": "NO_CERTIFIED_MAP",
            "Bridge_5": "NO_CERTIFIED_MAP_BRIDGE_2_ABSENT",
        },
        "claim_flags": {
            "ANOMALY_VECTOR_REPRODUCED": True,
            "BOX_R_ZERO_SCHEME_REPRODUCED": True,
            "ANOMALY_INDUCED_REPRESENTATIVE_SUPPLIED": True,
            "WEYL_INVARIANT_REMAINDER_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "WEYL_INVARIANT_FINITE_GAMMA1_NORMALIZATION_AND_EXTENDED_CLASSICAL_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate constructs one "
            "coefficient-bearing Paneitz/Riegert representative whose Weyl variation is "
            "the repository one-loop anomaly vector (199/30,-87/20,0,0) on an invertible "
            "boundary problem or the explicitly compatible source sector. The "
            "local R^2 term is derived rather than chosen: it converts E4-(2/3)BoxR back "
            "to the certified BoxR=0 convention. The construction is conditional on a "
            "self-adjoint Euclidean generalized inverse with declared kernel, boundary, "
            "source-compatibility, and conformal-transport policies. Kernel components "
            "remain global data rather than being silently discarded. It determines only the anomaly-induced "
            "representative. An arbitrary Weyl-invariant nonlocal functional, finite C2/R2 "
            "normalizations, global Green data, renormalized BV Laplacian or time-ordered "
            "product, and compensator-inclusive classical contraction remain absent. It "
            "therefore does not supply complete Gamma1 or Q1, authorize residual transfer, "
            "establish a Lorentzian QME or Hadamard state, activate Bridge 4 or Bridge 5, "
            "or identify a particle."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value.get("claim_flags", {})
    decision = value.get("decision", {})
    solve = value.get("exact_coefficient_solve", {})
    if (
        solve.get("rank") != 3
        or decision.get("complete_finite_nonlocal_Gamma1") != "NO_CERTIFIED_FUNCTIONAL"
        or decision.get("complete_Q1") != "NO_CERTIFIED_OPERATOR"
        or decision.get("residual_transfer") != "FORBIDDEN"
        or flags.get("ANOMALY_VECTOR_REPRODUCED") is not True
        or flags.get("ANOMALY_INDUCED_REPRESENTATIVE_SUPPLIED") is not True
        or flags.get("WEYL_INVARIANT_REMAINDER_SUPPLIED") is not False
        or flags.get("COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED") is not False
        or flags.get("COMPLETE_RENORMALIZED_Q1_SUPPLIED") is not False
        or flags.get("RESIDUAL_TRANSFER_AUTHORIZED") is not False
    ):
        raise ValueError("anomaly-induced Gamma1 certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale anomaly-induced Gamma1 certificate: {OUTPUT}")
    print("ANOMALY-INDUCED GAMMA1: EUCLIDEAN REPRESENTATIVE CERTIFIED; WEYL-INVARIANT REMAINDER OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
