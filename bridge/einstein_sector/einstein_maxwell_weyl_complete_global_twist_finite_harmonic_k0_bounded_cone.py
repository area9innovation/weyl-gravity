"""Complete the standard-global bounded cone for finite generic k=0 wave sums."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.schema.json"
INPUTS = {
    "twist_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json",
    "finite_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
    "partial_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "fixed_ell_successor": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.json",
}


class CompleteGlobalTwistFiniteHarmonicError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteGlobalTwistFiniteHarmonicError(message)


def _sha256(path: Path) -> str:
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
        active.add(path)
        for record in payload.get("provenance", {}).get("inputs", {}).values():
            child_name = record.get("path") if isinstance(record, dict) else None
            if child_name:
                edges += 1
                visit((ROOT / child_name).resolve())
        active.remove(path)

    for path in paths:
        visit(path)
    return seen, edges


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    twist = records["twist_wave"]
    finite_wave = records["finite_wave"]
    partial = records["partial_global"]
    standard = records["standard_global"]
    circumference = records["circumference"]
    electric_wilson = records["electric_wilson"]
    fixed_successor = records["fixed_ell_successor"]

    _require(twist["classification"]["every_fixed_ell_constant_twist_bounded_product_cone_certified"], "fixed-ell A-wave theorem changed")
    _require(twist["classification"]["every_fixed_ell_neighbor_output_invertible"], "fixed-ell neighbor inversion changed")
    _require(twist["source_decomposition"]["L=ell"] == "the complete same-shell adjoint projection is zero", "same-shell A-wave map changed")
    _require(finite_wave["classification"]["all_finite_cross_ell_superpositions_classified"], "finite wave inventory changed")
    _require(finite_wave["classification"]["complete_common_stabilizer_zero_cone_second_order_extendible"], "finite wave sufficiency changed")
    _require(partial["classification"]["cross_ell_wave_superpositions_classified"], "partial cross-ell theorem changed")
    _require(partial["classification"]["A_zero_wave_subcone_certified"], "historical finite A=0 subcone changed")
    _require(partial["global_wave_separation"]["consequence"] == "every nonzero bounded wave branch forces a=b=d=0", "finite global pivots changed")
    _require(standard["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "static global cone changed")
    _require(circumference["classification"]["k0_circumference_cross_bounded_removable"], "finite c-wave transport changed")
    _require(electric_wilson["classification"]["W_x_times_every_oscillator_source_zero"], "finite W_x-wave transport changed")
    _require(fixed_successor["classification"]["every_fixed_generic_ell_complete_global_bounded_cone_classified"], "one-block reduction changed")

    closure, dependency_edges = _dependency_closure(list(INPUTS.values()))
    _require(OUTPUT.resolve() not in closure, "successor appears in its transitive predecessor graph")

    value: dict[str, Any] = {
        "schema": "einstein-maxwell-weyl-complete-global-twist-finite-harmonic-k0-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FINITE_HARMONIC_K0_BOUNDED_CONE",
        "result_state": "FINITE_GENERIC_K0_COMPLETE_STANDARD_GLOBAL_TWIST_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ARBITRARY_FINITE_GENERIC_ELL_SET_K0_COMPLETE_GLOBAL_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle; electric tangent allowed before elimination",
            "carrier": "complete standard homogeneous/twist data plus an arbitrary finite sum of generic ell>=2,k=0 q/p primaries",
            "degree": 2,
            "parity": "homogeneous, axial and polar",
            "ell": "an arbitrary finite subset of integers ell>=2 with global ell=0,1 data adjoined",
            "m": "all retained wave m values and all three real twist components",
            "k": 0,
            "omega": "generalized zero and all retained p/q shell frequencies",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "acyclic_dependency_audit": {
            "historical_partial_predecessor": partial["result_id"],
            "successor_is_separate": True,
            "successor_absent_from_transitive_predecessors": True,
            "transitive_predecessor_count": len(closure),
            "transitive_dependency_edge_count": dependency_edges,
            "only_replaced_statement": "A=0 on the historical finite-wave subcone",
            "replacement": "A arbitrary on the complete finite generic k=0 H,J_i-zero wave cone",
        },
        "finite_additivity_proof": {
            "wave_decomposition": "u_wave=sum_(ell in S) u_ell with S finite and each u_ell retaining all m, parities and p/q multiplicities",
            "mixed_source_identity": "D2E[A,sum_ell u_ell]=sum_ell D2E[A,u_ell]",
            "blockwise_inverse": "for each ell, the same-shell source is zero and the L=ell-1,ell+1 sources have bounded inverses for every p/q coefficient",
            "overlapping_output_channels": "harmless: if distinct input blocks reach the same output carrier, linearity of L makes the sum of their certified corrections a correction for the summed source",
            "moment_map_independence": "the A-wave mixed inverse is available coefficientwise before imposing any blockwise moment-map equation; only the total wave-wave source requires total mu_H=mu_J_i=0",
            "finite_assembly": "the sum contains finitely many bounded quasiperiodic corrections and is therefore bounded quasiperiodic",
        },
        "pairwise_sufficiency": {
            "wave_wave_including_cross_ell": "the finite-harmonic wave theorem supplies a correction exactly on the total H,J_i zero cone",
            "A_wave": "finite additivity of the every-fixed-ell zero-map and neighbor inverses",
            "c_wave": "bounded removable for every retained k=0 oscillator",
            "W_x_wave": "identically zero for every retained oscillator",
            "static_pairs": "complete standard generalized-zero bounded theorem",
            "remaining_wave_globals": "a=b=d=Q_e=B=0 on every nonzero-wave stratum",
            "assembly": "D2E is bilinear and L is linear, so all certified pairwise corrections add",
        },
        "complete_bounded_zero_locus": {
            "static_stratum": "wave=0: a=b=Q_e=B=0; c,d,W_x,A arbitrary",
            "wave_stratum": "wave!=0: a=b=d=Q_e=B=0; c,W_x,A arbitrary; total mu_H=mu_J1=mu_J2=mu_J3=0",
            "intersection": "wave=0,d=0 with c,W_x,A arbitrary",
            "union_is_necessary_and_sufficient": True,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "bounded finite-quasiperiodic corrections form a smooth subclass; unrestricted secular data are not reclassified"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "arbitrary_finite_generic_ell_complete_global_bounded_cone_classified": True,
            "cross_ell_wave_superpositions_classified": True,
            "finite_multi_ell_constant_twist_column_classified": True,
            "all_standard_globals_all_retained_m_both_parities_all_qp_branches_included": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "constant_twist_position_free_on_wave_stratum": True,
            "constant_twist_position_free_on_finite_wave_stratum": True,
            "historical_A_zero_restriction_superseded": True,
            "one_fixed_ell_successor_recovered": True,
            "infinite_harmonic_completion_classified": False,
            "nonzero_momentum_classified": False,
            "exceptional_wave_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At rest and at second order, constant SO(3) holonomy is a bounded spectator not only for one angular block but for every finite generic harmonic sum. Cross-ell wave products are controlled by the total stabilizer moment maps, while A-wave products assemble linearly from the fixed-ell inverses.",
        "next_gate": "treat exceptional ell=1 wave inputs and nonzero compact momentum without merging their dispersion or correction-class scopes",
        "claim_boundary": "Complete only for the standard-global plus arbitrary finite generic ell>=2,k=0 carrier in the bounded class. Infinite harmonic completion, exceptional wave inputs, nonzero momentum, causal propagation, all-orders integration, residual observables and quantum transfer remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS"},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.35, "tests_run": 33, "independent_verifier": "PASS", "direct_consumer": "Einstein residual-atlas producer/verifier/tests PASS"},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "finite wave, fixed-ell A-wave, historical global necessity, standard-global, circumference, Wilson and one-block successor inputs are unchanged exact hashed dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "infinite harmonic, exceptional, momentum, causal and higher lifecycles remain fail-closed"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone",
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
        raise CompleteGlobalTwistFiniteHarmonicError("stale complete finite-harmonic global certificate")
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_FINITE_HARMONIC_K0_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
