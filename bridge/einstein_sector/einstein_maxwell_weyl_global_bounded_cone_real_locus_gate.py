"""Fail-closed reduction of the global bounded cone to its first open real gate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_GLOBAL_BOUNDED_CONE_REAL_LOCUS_GATE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-global-bounded-cone-real-locus-gate-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-global-bounded-cone-real-locus-gate-v1.schema.json"
INPUT_COMMIT = "414853ed8"
INPUTS = {
    "structural_freeze": ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "candidate18_complex": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json",
    "candidate18_separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.json",
    "candidate18_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.json",
    "phase_reduced_divisors": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
    "candidate16_gluing": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing.json",
    "candidate17_20_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json",
    "candidate19_21_links": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links.json",
}
EXPECTED_HASHES = {
    "structural_freeze": "935a3c264858c4f425025f2f1adf50886739bb84cdc86331120058c9ce7bd545",
    "fibre_product": "c6b3b928351ad42570fcba0e45ce3ee9df2a377066f6d44d9f0450c12dcd88da",
    "candidate18_complex": "16390b76191d608e3fd6b81db10c0fd9bd34817866033aa9ca26ae8c6d10b971",
    "candidate18_separation": "8a772c453a0c58ec5cb134617d1c93cb844fd889550c5c4a04c5be5741edcb9f",
    "candidate18_bridge": "dbe2504b9ae1bcbdfda09f410ccb7beda5cfc70f9486fe300b73e1a3cc5d6806",
    "phase_reduced_divisors": "d4e6091c079a75a82f16db01e3478d6e6b971df020c48557ffd471137fb80786",
    "candidate16_gluing": "735d834909680ed8b11f7b643a47355e0976c8c08145cae810b7dc6aa5cddd2c",
    "candidate17_20_contraction": "f3fd8c61e4b3608a0aa497d2f0a22b6a13bbf1d1d40df0685915a0f7e9bf9f0f",
    "candidate19_21_links": "3beb1442e6e98792c0922b72a3b5bccb218f03f8e8c5994cee5e136fff25ec53",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _input_records() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        digest = _sha256(path)
        if digest != EXPECTED_HASHES[name]:
            raise AssertionError(f"{name} content hash changed")
        value = _load(path)
        records[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest,
            "result_id": value["result_id"],
            "lifecycle_state": value["lifecycle_state"],
        }
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", INPUT_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if ancestor.returncode:
        raise AssertionError("required input commit is not an ancestor of HEAD")
    return records


def _candidate18_row(fibre_product: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row for row in fibre_product["candidate_rows"]
        if row["candidate_index"] == 18
    ]
    if len(rows) != 1:
        raise AssertionError("candidate 18 fibre-product row is not unique")
    return rows[0]


def _minor_labels(prefix: str) -> list[str]:
    return [
        f"Re({prefix}_{i}0*{prefix}_{j}1-{prefix}_{j}0*{prefix}_{i}1)=0; "
        f"Im({prefix}_{i}0*{prefix}_{j}1-{prefix}_{j}0*{prefix}_{i}1)=0"
        for i, j in itertools.combinations(range(5), 2)
    ]


def build_certificate() -> dict[str, Any]:
    inputs = {name: _load(path) for name, path in INPUTS.items()}
    row = _candidate18_row(inputs["fibre_product"])
    complex_data = inputs["candidate18_complex"]
    if row["resonance_geometry"] != {
        "ambient_dimension_over_C": 30,
        "component_dimensions_over_C": [22],
        "irreducible_components_over_C": 1,
    }:
        raise AssertionError("candidate 18 resonance geometry changed")
    if complex_data["one_factor"]["equation_count"] != 10:
        raise AssertionError("rank-one minor count changed")

    producer_path = Path(__file__).resolve()
    schema_path = SCHEMA.resolve()
    certificate = {
        "schema": "einstein-maxwell-weyl-global-bounded-cone-real-locus-gate-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_BOUNDED_CONE_REAL_LOCUS_GATE_V1",
        "result_state": "GLOBAL_REAL_LOCUS_OPEN_CANDIDATE18_FIXED_OCCUPATION_GATE_EXACT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan candidate 18 only",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "one same-sign two-|k| ell=2 active support at fixed positive exact scalar-cone occupations",
            "degree": 2,
            "parity": "complete axial/polar carrier",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "candidate-18 signed compact n=(1,2), not identified with any other candidate",
            "omega": "positive-frequency p-extra(n=1)+q-minus(n=2) SUM collision with conjugate reality completion",
            "correction_class": "bounded or finite-quasiperiodic",
        },
        "input_gate": {
            "required_commit": INPUT_COMMIT,
            "exact_hashes": EXPECTED_HASHES,
            "structural_statement": "For every fixed finite harmonic carrier, simultaneous vanishing of all five Taub maps and every certified P/R functional is necessary and sufficient for a bounded or finite-quasiperiodic second-order correction.",
        },
        "global_problem_type": {
            "finite_support_space": "direct union over all finite harmonic supports",
            "not_a_single_fixed_affine_ideal": True,
            "classification_strategy": "classify every finite invariant carrier and its incidence/gluing maps; a complex carrier decomposition is not a real Hermitian orbit classification",
            "global_common_zero_locus_classified": False,
        },
        "closed_block_census": {
            "candidate16": "fixed-occupation zero fibres and normalized nonzero occupation gluing certified connected",
            "candidate17_20": "complete fixed-positive-occupation singular rotation-zero unions contract to a connected hub; occupation gluing remains separate",
            "candidate19_21": "six active real linear sheets have nondegenerate restricted currents and connected rotation-zero links componentwise; distinct sheets remain distinct",
            "candidate18": "complex carrier and smooth regular reductions are classified, but the complete real fixed-occupation rotation-zero fibre and orbit quotient are not",
        },
        "selected_invariant_gate": {
            "selection_rule": "Fix the first candidate in the certified candidate order whose complete real fixed-positive-occupation rotation-zero fibre is not classified, after removing the already classified scalar occupation cone and complex resonance equations.",
            "candidate_index": 18,
            "rho": row["rho"],
            "ambient": "C^10_spectator x Mat(5,2;C)_plus x Mat(5,2;C)_minus",
            "ambient_real_dimension": 60,
            "complex_resonance_carrier": "C^10_spectator x Rank_{<=1}(5x2)_plus x Rank_{<=1}(5x2)_minus",
            "complex_dimension": 22,
            "complex_irreducible_components": 1,
            "complex_minor_equations_per_factor": 10,
            "real_minor_equations_total": 40,
            "rank_one_minor_labels_plus": _minor_labels("Zplus"),
            "rank_one_minor_labels_minus": _minor_labels("Zminus"),
            "Hermitian_level_equations": [
                "N_plus(amplitudes)-N_plus_fixed=0 with N_plus_fixed>0",
                "N_minus(amplitudes)-N_minus_fixed=0 with N_minus_fixed>0",
            ],
            "rotation_equations": ["mu_J1=0", "mu_J2=0", "mu_J3=0"],
            "residual_group_at_this_gate": "U(1)_plus x U(1)_minus x lifted SO(3)",
            "semialgebraic_conditions": ["N_plus_fixed>0", "N_minus_fixed>0", "physical conjugate-reality completion"],
            "invariance": "the determinantal ideal, Hermitian norm levels and rotation moment-map ideal are invariant under both node phases and lifted SO(3)",
        },
        "known_exact_geometry": {
            "complex_carrier": complex_data["complete_carrier"],
            "one_factor": complex_data["one_factor"],
            "singular_rotation_quotient": "at least two singular components at every positive occupation",
            "smooth_bridge": "one certified point in each singular component is joined through the smooth rotation-zero carrier at every positive occupation",
            "regular_phase_reduction": "the smooth fixed-occupation node-phase-reduced divisors and local constant-corank leaf descent are classified",
        },
        "remaining_real_gate": {
            "real_radical_of_complete_fixed_occupation_ideal": "OPEN",
            "every_rotation_zero_component_meets_central_bridge": "OPEN",
            "global_node_phase_lifted_rotation_orbit_quotient": "OPEN",
            "occupation_stratum_gluing": "OPEN",
            "required_next_proof": "Give an exact real-radical/component decomposition of the displayed Hermitian determinantal moment ideal and prove, or refute with an invariant separator, that every component meets the certified central bridge.",
        },
        "necessity_sufficiency_transfer": {
            "equational_formula": row["bounded_cone_formula"]["display"],
            "bounded_criterion": row["bounded_cone_formula"]["necessity_and_sufficiency"],
            "same_fibre_gate": row["bounded_cone_formula"]["same_fibre_factor"],
            "conclusion": "Solving this real Hermitian gate classifies bounded second-order extendibility on this fixed candidate-18 carrier; it does not by itself classify other finite supports or glue the direct union.",
        },
        "classification": {
            "complete_finite_harmonic_bounded_ledger_frozen": True,
            "candidate18_complex_carrier_classified": True,
            "candidate18_complete_real_fixed_occupation_fibre_classified": False,
            "candidate18_real_orbit_quotient_classified": False,
            "complex_variety_substituted_for_real_locus": False,
            "relative_phases_and_lifted_rotations_retained": True,
            "smallest_gate_under_declared_candidate_order_exported": True,
            "unrestricted_global_real_common_zero_classified": False,
            "causal_infinite_harmonic_all_orders_observational_or_quantum_claim": False,
        },
        "provenance": {
            "input_commit": INPUT_COMMIT,
            "inputs": _input_records(),
            "producer_path": str(producer_path.relative_to(ROOT)),
            "producer_sha256": _sha256(producer_path),
            "schema_path": str(schema_path.relative_to(ROOT)),
            "schema_sha256": _sha256(schema_path),
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_bounded_cone_real_locus_gate --check",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_global_bounded_cone_real_locus_gate",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_bounded_cone_real_locus_gate",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-global-bounded-cone-real-locus-gate-fragment-v1.json",
        ],
        "next_gate": "classify the candidate-18 fixed-positive-occupation real Hermitian determinantal moment ideal modulo U(1)^2 and lifted SO(3), retaining all ten spectators",
        "claim_boundary": "This is an exact fail-closed reduction to the first unresolved real fixed-occupation gate under the declared candidate order. It does not classify that real radical or orbit quotient, the unrestricted direct-union cone, occupation gluing, causal corrections, final residual descent, all-orders solutions, observables or quantum states.",
    }
    Draft202012Validator(_load(SCHEMA)).validate(certificate)
    return certificate


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    atlas_scope = {
        key: value
        for key, value in certificate["scope"].items()
        if key != "correction_class"
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).resolve().relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__).resolve()),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "einstein.ph.wm.finite_harmonic_cone.candidate18_real_locus_gate",
            "scope": atlas_scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "Candidate-18 collision and shell data are exact."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The active current, its smooth radical divisor and node-phase reduction are exact."},
                "taub_maps": {"status": "CERTIFIED", "statement": "The two fixed norm levels and all three lifted rotation moment maps are retained."},
                "resonance": {"status": "CERTIFIED", "statement": "The complex resonance carrier is C^10 times two rank-at-most-one 5x2 cones."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Necessary-and-sufficient equations are exact; the complete real Hermitian orbit fibre is not classified."},
                    "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "This gate is scoped only to bounded or finite-quasiperiodic corrections."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."},
                },
            },
            "evidence": [{
                "path": str(OUTPUT.relative_to(ROOT)),
                "sha256": _sha256(OUTPUT),
                "result_id": certificate["result_id"],
            }],
            "claim_boundary": certificate["claim_boundary"],
        }],
        "verification_commands": certificate["verification_commands"],
    }


def write_outputs() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ATLAS.write_text(json.dumps(build_atlas(certificate), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_output() -> None:
    expected = build_certificate()
    if _load(OUTPUT) != expected:
        raise AssertionError("certificate is stale")
    if _load(ATLAS) != build_atlas(expected):
        raise AssertionError("atlas fragment is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
    if args.check:
        verify_output()
    if not (args.write or args.check):
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
