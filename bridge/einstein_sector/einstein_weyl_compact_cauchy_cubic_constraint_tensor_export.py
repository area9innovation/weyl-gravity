"""Fail-closed audit of the action-normalized cubic canonical export."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-v1.schema.json"
INPUTS = {
    "third_order_gate": (
        "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json",
        "EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1",
        "8893ddc02d47101d9ffc718c25455f17af81b55e5cfd83d04830d7be8c6beb3b",
    ),
    "selected_action": (
        "bridge/certificates/einstein_maxwell_product_incidence.json",
        "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
        "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
    ),
    "canonical_constraint_ledger": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json",
        "EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1",
        "1a2986f246d156d70f640337368d29d62c60a8ec464153579bf08af4a40ebce2",
    ),
    "balanced_correction": (
        "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
        "EINSTEIN_MAXWELL_WEYL_BALANCED_ELL0_SECOND_ORDER",
        "13fc90b0ef18c6bf6a8f4f1a397c86aa235ed87fa86a3c3bf5ad031bc2304cfe",
    ),
    "polar_field_crosswalk": (
        "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
        "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR",
        "2cd92c4fc638ce5f3c26fc890e54908d8f2c8beec55efb3e90eee7b3affd8368",
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalization_witness() -> dict[str, Any]:
    epsilon, scale = sp.symbols("epsilon scale")
    # Isolate the displayed -(P_ij P^ij)/(2 sqrt(h)) contribution at one slot.
    term = -scale**2 * (1 + epsilon) ** 2 / (2 * sp.sqrt(1 + epsilon))
    cubic = sp.expand(sp.series(term, epsilon, 0, 4).removeO()).coeff(epsilon, 3)
    req(sp.simplify(cubic - scale**2 / 32) == 0, "canonical scale witness")
    one = sp.simplify(cubic.subs(scale, 1))
    two = sp.simplify(cubic.subs(scale, 2))
    req(one == sp.Rational(1, 32) and two == sp.Rational(1, 8), "scale mutation")
    return {
        "isolated_constraint_term": "-(P_ij P^ij)/(2 sqrt(h))",
        "one_slot_jet": "h=1+epsilon, P=scale*(1+epsilon)",
        "epsilon_cubed_coefficient": str(cubic),
        "scale_1": str(one),
        "scale_2": str(two),
        "conclusion": "both nonzero canonical normalizations preserve the imported rank-only symbol theorem but give different action-normalized cubic coefficients",
    }


def build() -> dict[str, Any]:
    imported: dict[str, dict[str, Any]] = {}
    for name, (rel, result_id, digest) in INPUTS.items():
        path = ROOT / rel
        payload = json.loads(path.read_text())
        req(payload["result_id"] == result_id, f"{name} id")
        req(sha(path) == digest, f"{name} hash")
        imported[name] = payload

    action = imported["selected_action"]
    ledger = imported["canonical_constraint_ledger"]
    correction = imported["balanced_correction"]
    polar = imported["polar_field_crosswalk"]
    req("(alpha_B/8)" in action["conventions"]["weyl_maxwell_action"], "selected action")
    req(action["rational_fixture"]["parameters"]["alpha_B"] == "3", "alpha_B fixture")
    boundary = ledger["action_derived_constraint_ledger"]["normalization_boundary"]
    background = ledger["douglis_nirenberg_symbol"]["background_momentum_normalization"]
    req("nonzero canonical rescaling" in boundary, "normalization boundary disappeared")
    req("suppressed nonzero action normalization" in background, "background scale boundary disappeared")
    req(correction["classification"]["complete_second_order_extension_constructed"], "correction incomplete")
    req(polar["target_operator"]["coordinates"] == ["A_t=A+K", "B", "C_t=C-K", "U"], "polar coordinates")
    serialized = json.dumps(ledger, sort_keys=True)
    req("ostrogradsky_crosswalk" not in serialized and "boundary_term_convention" not in serialized, "new canonical crosswalk appeared")

    return {
        "schema": "einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1",
        "result_state": "ACTION_PINNED_CUBIC_CANONICAL_EXPORT_OBSTRUCTED_BY_MISSING_NORMALIZED_OSTROGRADSKY_CROSSWALK",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                key: {"path": rel, "result_id": rid, "sha256": digest}
                for key, (rel, rid, digest) in INPUTS.items()
            },
        },
        "scope": {
            "theory": "Weyl-Maxwell canonical constraint export from the selected alpha_B=3 action",
            "background": "compactified magnetically supported Plebanski-Hacyan",
            "boundaries": "compact Cauchy slice S1_L x S2 before stabilizer reduction",
            "charge_sector": "fixed P_N,N=2 and fixed Q_e; based Maxwell gauge; W_x retained",
            "carrier": "balanced ell=2,m=0,k=0 first-order fixture and stored ell=0,2,4 second-order correction",
            "degree": "cubic constraint/action derivative export preflight",
            "parity": "axial first order, polar second order, axial cubic output",
            "ell": "required output 2,4,6",
            "m": "0",
            "k": "0",
            "omega": "sixteen-point odd frequency lattice imported from the third-order gate",
        },
        "selected_action": {
            "action": action["conventions"]["weyl_maxwell_action"],
            "alpha_B": action["rational_fixture"]["parameters"]["alpha_B"],
            "covariant_equation": action["conventions"]["weyl_maxwell_equations"],
            "status": "PINNED_BY_CONTENT_HASH",
        },
        "representation_audit": {
            "canonical_pairs": ledger["action_derived_constraint_ledger"]["canonical_pairs"],
            "constraint_rows": ["H_perp", "H_1", "H_2", "H_3", "P_trace", "Q_scale", "Gauss"],
            "covariant_correction_coordinates": ["ell>=2: A_t=A+K,B,C_t=C-K,U", "ell=0: C,K,U"],
            "missing_canonical_coordinates": ["delta K_ij", "delta pi^ij", "delta P^ij", "delta E^i"],
            "normalization_boundary": boundary,
            "background_momentum_boundary": background,
            "boundary_term_issue": "the selected covariant C^2 action has no content-addressed boundary-term/canonical-transformation convention fixing pi and P",
            "conclusion": "the stored covariant correction cannot be inserted into the seven-row canonical constraint map in the same action normalization",
        },
        "normalization_witness": normalization_witness(),
        "first_absent_export": {
            "row": "H_perp",
            "term": "-(P_ij P^ij)/(2 sqrt(h))",
            "missing_map": "the exact alpha_B=3 action-to-canonical map giving P^ij and pi^ij, including background magnitude and boundary-term convention",
            "why_first": "D3H_perp already depends on the suppressed P normalization; later harmonic projection cannot repair an undefined local coefficient",
            "required_crosswalk": "for every stored covariant correction channel, export (delta h,delta K,delta pi,delta P,delta a,delta E) with time/conjugation rules in the canonical ledger convention",
            "downstream_unavailable": [
                "D3C_barPhi[u,u,u]",
                "mixed D2C_barPhi[u,v]",
                "five stabilizer projections",
                "resonant ell=2 q_minus/p_extra projections",
                "second action jet and arity-three Noether identity",
            ],
        },
        "mutations": {
            "set_suppressed_scale_to_one": "REJECTED: scale=1 is a new convention, not a consequence of the selected action certificate",
            "set_missing_momenta_to_zero": "REJECTED: the correction is a covariant solution, not a certified zero-momentum canonical representative",
            "use_covariant_Euler_rows_as_constraints": "REJECTED: no typed projection identifies those rows with the seven canonical constraints in the higher-derivative phase space",
            "infer_arity_three_Noether_from_linear_symbol": "REJECTED: rank and first-class counting do not determine the second action jet",
        },
        "classification": {
            "selected_covariant_action_pinned": True,
            "balanced_correction_pinned": True,
            "canonical_constraint_ledger_pinned": True,
            "exact_action_to_canonical_normalization_present": False,
            "background_ostrogradsky_magnitude_present": False,
            "covariant_to_canonical_correction_crosswalk_present": False,
            "action_normalized_Hperp_D3_exported": False,
            "complete_cubic_tensor_exported": False,
            "arity_three_noether_exported": False,
            "absent_coefficient_inserted_as_zero": False,
            "causal_particle_or_quantum_claim": False,
        },
        "claim_boundary": "Pins the selected alpha_B=3 covariant action, canonical constraint ledger and complete covariant second-order correction, and certifies the first exact representation/normalization obstruction to a cubic canonical tensor export. It does not compute any D3 coefficient, choose a boundary term, invent canonical momenta, evaluate the third-order Kuranishi class, or promote bounded, causal, particle, positivity, unitarity or quantum claims.",
        "next_gate": "derive and certify the alpha_B=3 Ostrogradsky canonical transformation, boundary-term convention, exact background P magnitude, and channelwise covariant-to-canonical correction crosswalk before retrying D3C",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_compact_cauchy_cubic_constraint_tensor_export --verify bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json",
            "python3 bridge/einstein_sector/verify_einstein_weyl_compact_cauchy_cubic_constraint_tensor_export.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_compact_cauchy_cubic_constraint_tensor_export",
            "python3 -m bridge.einstein_sector.generate_cubic_constraint_tensor_export_atlas --check",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.verify:
        req(json.loads(args.verify.read_text()) == payload, "stale certificate")
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
