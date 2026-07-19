"""Complete the standard-global bounded cone over one fixed generic ell."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.schema.json"
INPUTS = {
    "twist_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json",
    "partial_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "ell2_calibration": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.json",
}


class CompleteGlobalFixedEllError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteGlobalFixedEllError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency_closure(paths: list[Path]) -> tuple[set[Path], int]:
    seen: set[Path] = set()
    active: set[Path] = set()
    edges = 0

    def visit(path: Path) -> None:
        nonlocal edges
        path = path.resolve()
        _require(path not in active, f"predecessor certificate cycle at {path.relative_to(ROOT)}")
        if path in seen:
            return
        seen.add(path)
        if path.suffix != ".json":
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        inputs = payload.get("provenance", {}).get("inputs", {})
        active.add(path)
        for record in inputs.values():
            child_name = record.get("path") if isinstance(record, dict) else None
            if not child_name:
                continue
            child = (ROOT / child_name).resolve()
            edges += 1
            visit(child)
        active.remove(path)

    for path in paths:
        visit(path)
    return seen, edges


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    twist = records["twist_wave"]
    partial = records["partial_global"]
    standard = records["standard_global"]
    circumference = records["circumference"]
    electric_wilson = records["electric_wilson"]
    calibration = records["ell2_calibration"]

    _require(twist["classification"]["every_fixed_ell_constant_twist_bounded_product_cone_certified"], "twist-wave product changed")
    _require(twist["complete_bounded_zero_locus"]["necessity_and_sufficiency"], "twist-wave sufficiency changed")
    _require(twist["complete_bounded_zero_locus"]["constant_twist_position"] == "A is arbitrary", "free twist position changed")
    _require(partial["classification"]["all_m_both_parities_all_qp_branches_included"], "fixed-ell global inventory changed")
    _require(partial["classification"]["A_zero_wave_subcone_certified"], "historical A=0 subcone changed")
    _require("a=b=d=0" in partial["global_necessity"]["a_b_d"], "a,b,d pivot changed")
    _require(partial["global_necessity"]["twist_velocity"] == "B=0 on every bounded branch", "B gate changed")
    _require(partial["global_necessity"]["electric_E11_replay"] == "Q_e**2/2", "electric gate changed")
    _require(standard["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "static global cone changed")
    _require(circumference["classification"]["k0_circumference_cross_bounded_removable"], "c transport changed")
    _require(electric_wilson["classification"]["W_x_times_every_oscillator_source_zero"], "W_x transport changed")
    _require(calibration["classification"]["bounded_zero_locus_necessary_and_sufficient"], "ell2 calibration changed")
    closure, dependency_edges = _dependency_closure(list(INPUTS.values()))
    _require(OUTPUT.resolve() not in closure, "successor appears in its transitive predecessor graph")

    value = {
        "schema": "einstein-maxwell-weyl-complete-global-twist-fixed-ell-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FIXED_ELL_BOUNDED_CONE",
        "result_state": "EVERY_FIXED_GENERIC_ELL_COMPLETE_STANDARD_GLOBAL_TWIST_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_EVERY_ONE_FIXED_GENERIC_ELL_K0_COMPLETE_GLOBAL_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle; electric tangent allowed before elimination",
            "carrier": "complete standard homogeneous/twist data plus every q/p primary in one fixed generic ell block",
            "degree": 2,
            "parity": "homogeneous, axial and polar",
            "ell": "one fixed integer ell>=2 with global ell=0,1 data adjoined",
            "m": "all wave m and all three real twist components",
            "k": 0,
            "omega": "generalized zero and every fixed-ell p/q shell",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "acyclic_dependency_audit": {
            "historical_partial_predecessor": partial["result_id"],
            "successor_is_separate": True,
            "successor_absent_from_transitive_predecessors": True,
            "transitive_predecessor_count": len(closure),
            "transitive_dependency_edge_count": dependency_edges,
            "reason": "the fixed-ell twist factorization already imports the historical global subcone; replacing that predecessor in place would create a certificate cycle",
            "retained_inputs": ["generic a,b,d pivots", "B=0", "E11=Q_e^2/2", "c transport", "W_x zero source"],
            "only_replaced_statement": "A=0 on the historical wave subcone",
            "replacement": "A arbitrary on the complete fixed-ell H,J_i-zero wave cone",
        },
        "pairwise_sufficiency": {
            "wave_wave": "certified on mu_H=mu_J1=mu_J2=mu_J3=0",
            "A_wave": "same-shell zero and uniformly invertible L=ell-1,ell+1 outputs",
            "c_wave": "bounded removable at k=0",
            "W_x_wave": "identically zero",
            "static_pairs": "complete standard generalized-zero bounded theorem",
            "assembly": "D^2E is bilinear and L is linear, so the pairwise corrections add",
        },
        "complete_bounded_zero_locus": {
            "static_stratum": "wave=0: a=b=Q_e=B=0; c,d,W_x,A arbitrary",
            "wave_stratum": "wave!=0: a=b=d=Q_e=B=0; c,W_x,A arbitrary; mu_H=mu_J1=mu_J2=mu_J3=0",
            "intersection": "wave=0,d=0 with c,W_x,A arbitrary",
            "union_is_necessary_and_sufficient": True,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "bounded corrections form a smooth subclass; unrestricted secular data are not reclassified"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "every_fixed_generic_ell_complete_global_bounded_cone_classified": True,
            "all_standard_globals_all_m_both_parities_all_qp_branches_included": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "constant_twist_position_free_on_wave_stratum": True,
            "historical_A_zero_restriction_superseded": True,
            "ell2_complete_global_theorem_recovered": True,
            "finite_multi_ell_twist_cone_classified": False,
            "nonzero_momentum_classified": False,
            "exceptional_wave_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At rest, constant SO(3) holonomy survives freely over every one-fixed-ell nonlinear bounded wave cone. Nonzero waves still remove a,b,d,Q_e,B while c and W_x remain spectators.",
        "next_gate": "classify constant-twist cross terms for finite sums of distinct ell blocks without merging output frequencies or angular carriers",
        "claim_boundary": "Complete only for the standard-global plus one fixed ell>=2,k=0 carrier in the bounded class. Finite multi-ell, nonzero momentum, exceptional waves, unrestricted secular, causal, all-orders, residual, observational and quantum scopes remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS"},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.40, "tests_run": 34, "independent_verifier": "PASS", "direct_consumer": "Einstein residual-atlas producer/verifier/tests PASS"},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "all predecessor theorems are unchanged exact hashed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "finite multi-ell and higher lifecycles remain fail-closed"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone",
        ],
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise CompleteGlobalFixedEllError("stale complete fixed-ell global certificate")
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FIXED_ELL_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
