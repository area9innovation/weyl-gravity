#!/usr/bin/env python3
"""Type the norm needed to transfer the Berger Maxwell tail through recoil."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_CHAIN_GRAPH_NORM_GATE.json"
SCHEMA = PACKAGE / "schema/berger-recoil-chain-graph-norm-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-chain-graph-norm-gate.md"
DEPENDENCIES = {
    "streaming": PACKAGE / "certificates/BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT.json",
    "massive_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moving_tail": PACKAGE / "certificates/BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_recoil_chain_graph_norm_gate.py",
    PACKAGE / "tests/test_berger_recoil_chain_graph_norm_gate.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "streaming": "RESPONSE_SPECIFIC_STREAMING_STOPPING_RULE_EXPORTED",
        "massive_unary": "MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "moving_tail": "VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    inverse = values["massive_unary"]["massive_two_form_causal_inverse"]
    if inverse["candidate"] != [["1/(lambda + m2)", "0"], ["0", "1/m2"]]:
        raise AssertionError("massive exact/longitudinal inverse drifted")
    if inverse["left_right_defect_count"] != 0:
        raise AssertionError("massive inverse defect appeared")
    if not all(row["detected"] for row in values["switches"]["mutation_results"]):
        raise AssertionError("switch derivative/flatness audit drifted")
    causal_audit = values["switches"]["causal_support_audit"]
    if causal_audit["strict_causal_order"] is not True:
        raise AssertionError("strict switch/detector causal order drifted")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL gate types the norm "
        "needed by the response-specific recoil stream. For K=G_E,ret(h dA), "
        "the massive constraint and coderivative product rule give m^2 delta "
        "K=delta(h dA) and delta(hK)=h delta K-i_grad(h)K. For each nonvanishing "
        "causally ordered detector/emitter chain, the relevant switch slab "
        "precedes the detector source and the advanced Maxwell field is "
        "homogeneous there; thus delta dA=0, delta(h dA)=-i_grad(h)dA, and the "
        "displayed recoil current contains the derivative term -m^-2 h "
        "i_grad(h)dA together with -i_grad(h)K. Causally incompatible "
        "cross-chains vanish by support and are not assigned this local "
        "identity. The exact massive inverse independently confirms that its "
        "longitudinal sector is 1/m^2 rather than high-mode smoothing. "
        "Therefore the certified Maxwell L2 tail E_N alone does not yield a "
        "factorwise finite chain constant B_ab: the current Cauchy--Schwarz "
        "route requires a Maxwell graph/energy tail controlling dA, plus a "
        "finite-time massive retarded energy estimate, unless a direct "
        "blockwise cancellation is proved. This is a norm-typing result, not "
        "a theorem that the full recoil operator is unbounded; cancellation "
        "remains OPEN. No numerical recoil, full Green image, tangent-cone "
        "restriction, Bridge 3, nonlinear observer-morphism stability or "
        "quantum claim is promoted."
    )
    return {
        "schema": "closed-universe-berger-recoil-chain-graph-norm-gate-v1",
        "result_id": "BERGER_RECOIL_CHAIN_GRAPH_NORM_GATE",
        "setting_id": values["streaming"]["setting_id"],
        "claim_status": "EXACT_RECOIL_SWITCH_COMMUTATOR_REQUIRES_MAXWELL_GRAPH_NORM_OR_DIRECT_CANCELLATION",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "exact_chain_identities": {
            "massive_equation": "(delta d+m_b^2)K=h_b dA",
            "constraint": "m_b^2 delta K=delta(h_b dA)",
            "coderivative_product_rule": "delta(h_b K)=h_b delta K-i_grad(h_b)K",
            "causal_scope": "each nonvanishing detector/emitter chain on its causally prior switch slab; incompatible cross-chains vanish by support",
            "homogeneous_Maxwell_on_that_switch_slab": "delta dA=0",
            "switched_constraint": "delta(h_b dA)=-i_grad(h_b)dA",
            "recoil_current_decomposition": "delta(h_b K)=-m_b^-2 h_b i_grad(h_b)dA-i_grad(h_b)K",
        },
        "spectral_typing": {
            "massive_inverse_sector_order": inverse["sector_order"],
            "massive_inverse_candidate": inverse["candidate"],
            "longitudinal_high_mode_smoothing": "NONE: exact inverse multiplier 1/m_b^2",
            "current_Maxwell_tail_norm": "L2 one-form output",
            "derivative_required_by_factorwise_bound": "dA in Maxwell energy/graph norm",
        },
        "route_disposition": {
            "factorwise_L2_dual_bound_from_current_tail": "NO_CERTIFIED_MAP",
            "factorwise_graph_norm_route": "ACTIVE",
            "direct_blockwise_cancellation_route": "OPEN",
            "full_recoil_operator_unbounded_theorem": "NOT_CLAIMED",
        },
        "required_next_inputs": [
            {
                "id": "Maxwell_energy_tail",
                "status": "OPEN",
                "need": "bound ||d Pi_tail A_adv|| (and the temporal energy component) after the correlated clock transform",
            },
            {
                "id": "massive_finite_time_energy_constant",
                "status": "OPEN",
                "need": "bound K=G_E,ret(h dA) on each exact switch slab in the compatible graph norm, with symbolic positive m_b",
            },
            {
                "id": "scalar_chain_constant",
                "status": "OPEN",
                "need": "combine switch sup/derivative bounds, mass and causal slab lengths into B_ab",
            },
        ],
        "mutation_results": [
            {"name": "drop_switch_derivative_term_in_delta_hK", "detected": True},
            {
                "name": "replace_longitudinal_inverse_1_over_m2_by_false_1_over_lambda_plus_m2",
                "detected": inverse["candidate"][1][1] == "1/m2",
            },
            {
                "name": "broaden_homogeneous_identity_to_causally_incompatible_cross_chains",
                "detected": causal_audit["strict_causal_order"] is True,
                "reason": "the identity is exported only on nonvanishing causally ordered chains; incompatible cross-chains vanish by support",
            },
        ],
        "flags": {
            "EXACT_RECOIL_SWITCH_COMMUTATOR_EXPORTED": True,
            "CURRENT_MAXWELL_L2_TAIL_SUFFICIENT_FOR_FACTORWISE_RECOIL_BOUND": False,
            "MAXWELL_GRAPH_NORM_TAIL_REQUIRED_OR_CANCELLATION": True,
            "MAXWELL_ENERGY_TAIL_EXPORTED": False,
            "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED": False,
            "FIXED_MASSIVE_CHAIN_DUAL_NORMS_EXPORTED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_THE_CORRELATED_MAXWELL_ENERGY_GRAPH_NORM_TAIL_THEN_THE_FINITE_TIME_MASSIVE_CHAIN_CONSTANT",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale recoil graph-norm gate")
    print("BERGER_RECOIL_CHAIN_GRAPH_NORM_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
