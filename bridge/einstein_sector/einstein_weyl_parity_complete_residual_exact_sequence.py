"""Maximal parity-complete exact sequence and its first absent residual map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-weyl-parity-complete-residual-exact-sequence-maximal-v1.schema.json"
INPUTS = {
    "polar_residual_obstruction": ("bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json", "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1", "48fe90ab737751abc445200740bb54a1f926af722234d6af4db1fb3980aa370f"),
    "axial_direct_current": ("bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json", "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION", "e3d59018c9ae4a1d65b2ca531f24534d553dc7da1e6386c1d4afb577effd05f8"),
    "polar_direct_current": ("bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json", "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1", "f411d2e62c4ffa7436966d11f7d77e4c91b85d4ffbaf220f04f816bd80ec0b71"),
    "relative_triangle": ("bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json", "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1", "e015943d411836ba823c8dceb0f4bd155484abdf981f744a9d9609f86a5cc353"),
    "branch_dictionary": ("bridge/certificates/einstein_weyl_relative_branch_dictionary.json", "EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1", "0489e3a15956b9e397387476cd76974f6083692a85bc840b34d81d7893bae5aa"),
    "exceptional_global_maps": ("bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json", "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1", "3d4b271bac82751c6b50e6da088dfcdf97ebe946a78c96f2dfe052103a060a0e"),
    "stabilizer": ("bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json", "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT", "7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8"),
}


class ParityExactSequenceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ParityExactSequenceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table() -> list[dict[str, Any]]:
    rows = [
        {"id": "generic.axial", "scope": "per (ell>=2,m,k) polynomial fibre", "scalar_field": "K", "dimension_kind": "K", "Einstein_dimension": 4, "Weyl_dimension": 8, "extra_dimension": 4, "Einstein_pairing_rank": 4, "Weyl_pairing_rank": 8, "extra_pairing_rank": 4, "Einstein_inertia_positive_frequency": [1,1], "Weyl_inertia_positive_frequency": [3,1], "extra_inertia_positive_frequency": [2,0], "radical_dimensions": [0,0,0], "branches": "q-primary; q plus p^2; p^2"},
        {"id": "generic.polar", "scope": "per (ell>=2,m,k) polynomial fibre", "scalar_field": "K", "dimension_kind": "K", "Einstein_dimension": 4, "Weyl_dimension": 8, "extra_dimension": 4, "Einstein_pairing_rank": 4, "Weyl_pairing_rank": 8, "extra_pairing_rank": 4, "Einstein_inertia_positive_frequency": [1,1], "Weyl_inertia_positive_frequency": [3,1], "extra_inertia_positive_frequency": [2,0], "radical_dimensions": [0,0,0], "branches": "q-primary; q plus p^2; p^2"},
        {"id": "exceptional.ell1.axial", "scope": "per (m,k), k=0 and k!=0 independently", "scalar_field": "K", "dimension_kind": "K", "Einstein_dimension": 2, "Weyl_dimension": 4, "extra_dimension": 2, "Einstein_pairing_rank": 2, "Weyl_pairing_rank": 4, "extra_pairing_rank": 2, "Einstein_inertia_positive_frequency": [1,0], "Weyl_inertia_positive_frequency": [2,0], "extra_inertia_positive_frequency": [1,0], "radical_dimensions": [0,0,0], "branches": "standard s=4; standard plus extra s=4/3; extra s=4/3"},
        {"id": "exceptional.ell1.polar", "scope": "per (m,k), k=0 and k!=0 independently", "scalar_field": "K", "dimension_kind": "K", "Einstein_dimension": 2, "Weyl_dimension": 4, "extra_dimension": 2, "Einstein_pairing_rank": 2, "Weyl_pairing_rank": 4, "extra_pairing_rank": 2, "Einstein_inertia_positive_frequency": [1,0], "Weyl_inertia_positive_frequency": [2,0], "extra_inertia_positive_frequency": [1,0], "radical_dimensions": [0,0,0], "branches": "standard s=4; standard plus extra s=4/3; extra s=4/3"},
        {"id": "polar.ell0.nonzero_fourier", "scope": "k!=0", "scalar_field": "R", "dimension_kind": "real solution", "Einstein_dimension": 0, "Weyl_dimension": 0, "extra_dimension": 0, "Einstein_pairing_rank": 0, "Weyl_pairing_rank": 0, "extra_pairing_rank": 0, "Einstein_inertia_positive_frequency": "NOT_APPLICABLE", "Weyl_inertia_positive_frequency": "NOT_APPLICABLE", "extra_inertia_positive_frequency": "NOT_APPLICABLE", "radical_dimensions": [0,0,0], "branches": "empty physical quotient"},
        {"id": "homogeneous.ell0.k0", "scope": "complete generalized global block", "scalar_field": "R", "dimension_kind": "real solution", "Einstein_dimension": 6, "Weyl_dimension": 6, "extra_dimension": 0, "Einstein_pairing_rank": 6, "Weyl_pairing_rank": 6, "extra_pairing_rank": 0, "Einstein_inertia_positive_frequency": "NOT_APPLICABLE", "Weyl_inertia_positive_frequency": "NOT_APPLICABLE", "extra_inertia_positive_frequency": "NOT_APPLICABLE", "radical_dimensions": [0,0,0], "branches": "(a,b,c,d,Q_e,W_x); solution cofiber zero"},
        {"id": "twist.ell1.k0", "scope": "per real SO(3) component", "scalar_field": "R", "dimension_kind": "real solution", "Einstein_dimension": 2, "Weyl_dimension": 2, "extra_dimension": 0, "Einstein_pairing_rank": 2, "Weyl_pairing_rank": 2, "extra_pairing_rank": 0, "Einstein_inertia_positive_frequency": "NOT_APPLICABLE", "Weyl_inertia_positive_frequency": "NOT_APPLICABLE", "extra_inertia_positive_frequency": "NOT_APPLICABLE", "radical_dimensions": [0,0,0], "branches": "position/velocity pair; solution cofiber zero"},
    ]
    for row in rows:
        _require(row["Einstein_dimension"] + row["extra_dimension"] == row["Weyl_dimension"], f"dimension exactness failed: {row['id']}")
        _require(row["Einstein_pairing_rank"] + row["extra_pairing_rank"] == row["Weyl_pairing_rank"], f"pairing rank additivity failed: {row['id']}")
    return rows


def build_certificate() -> dict[str, Any]:
    records = {}
    for name, (relative, result_id, digest) in INPUTS.items():
        path = ROOT / relative
        record = json.loads(path.read_text())
        _require(record["result_id"] == result_id, f"{name} result ID changed")
        _require(_sha256(path) == digest, f"{name} hash changed")
        records[name] = record
    _require(records["relative_triangle"]["acceptance_flags"]["SUPPORT_LOCAL_MAPPING_COFIBER"], "mapping cofiber missing")
    _require(records["relative_triangle"]["pairing_disposition"]["triangle_kind"] == "NONCYCLIC_THREE_FORM", "triangle kind changed")
    return {
        "schema": "einstein-weyl-parity-complete-residual-exact-sequence-maximal-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1",
        "result_state": "PRERESIDUAL_H0_SHORT_EXACT_SEQUENCE_CERTIFIED_STRICT_COMPLEX_AND_FINAL_RESIDUAL_SEQUENCES_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {name: {"path": relative, "result_id": result_id, "sha256": digest} for name,(relative,result_id,digest) in INPUTS.items()}},
        "common_conventions": {"background": "compactified magnetically supported Plebanski-Hacyan", "boundaries": "closed S1_L times S2", "charge": "fixed magnetic Chern class; electric tangent and Wilson-line tangent retained", "local_gauge": "Diff x U1 source to Diff x Weyl x U1 target", "harmonics": "generic, exceptional, homogeneous and twist strata never merged"},
        "maximal_preresidual_statement": {
            "chain_level": "E_EM -> E_WM -> Cofib(iota) is a support-local noncyclic mapping-cofiber triangle, not a degreewise short exact sequence",
            "solution_level": "0 -> H0(E_EM) -> H0(E_WM) -> H0_extra -> 0 is exact on every row in the authoritative table",
            "kernel_equals_image": True,
            "cokernel_equals_declared_extra": True,
            "splitting_claim": False,
            "cyclic_claim": False,
        },
        "authoritative_table": _table(),
        "first_absent_maps": {
            "strict_complex_short_exact_inclusion": "OBSTRUCTED: the certified equation and identity maps are not degreewise injective; the target has the additional Weyl identity",
            "strict_cyclic_identity_inclusion": "OBSTRUCTED: generic axial and polar cohomology-form defects are nonradical",
            "after_residual_quotient_functor": "NO_CERTIFIED_MAP: no common moment-map-zero derived carrier authorizes quotient by H,P_x,J_i",
            "after_residual_exact_sequence": "NO_CERTIFIED_MAP",
            "after_residual_dimensions_pairing_radical": "NO_CERTIFIED_MAP",
        },
        "current_compatibility": {
            "triangle_kind": "NONCYCLIC_THREE_FORM",
            "Einstein_form": "Omega_EM",
            "pulled_back_Weyl_form": "iota^*Omega_WM=Omega_EM(.,R .)",
            "extra_form": "direct Weyl-Maxwell cofiber form",
            "generic_axial_and_polar_extra_nonradical": True,
            "generic_axial_and_polar_extra_inertia": [2,0],
            "generic_axial_and_polar_complete_inertia": [3,1],
            "particle_norm_claim": False,
        },
        "endpoint_disposition": {
            "ell1": "independent axial and polar all-row maps and cofibers certified at k=0 and k!=0",
            "ell0_nonzero": "empty physical solution quotient",
            "homogeneous": "solution cofiber zero; Q_e and W_x retained; R=I+N",
            "twist": "solution cofiber zero; three physical holonomy pairs retained; R=-2I",
            "large_U1": "finite periodic identification only; no tangent deletion",
            "boundary": "NO_CERTIFIED_MAP",
        },
        "mutations": {"infer_split_from_exactness": "REJECTED", "promote_mapping_cofiber_to_degreewise_SES": "REJECTED", "promote_three_form_triangle_to_cyclic": "REJECTED", "gauge_delete_charged_stabilizers_or_W_x": "REJECTED"},
        "classification": {"preresidual_H0_short_exact_sequence_certified": True, "preresidual_mapping_cofiber_triangle_certified": True, "degreewise_short_exact_complex_certified": False, "cyclic_exact_sequence_certified": False, "after_residual_exact_sequence_certified": False, "parity_complete_table_certified": True, "causal_particle_or_quantum_claim": False},
        "claim_boundary": "This certificate assembles the maximal parity-complete compact-product result: a noncyclic mapping-cofiber triangle and exact H0 solution sequence before residual reduction. It does not promote this to a degreewise short exact BV sequence, a cyclic morphism, a split sequence, or an after-residual sequence; the latter lacks an authorized common moment-map-zero quotient carrier. No causal, particle, positivity, unitarity or quantum claim is made.",
        "next_gate": "construct the common moment-map-zero derived quotient functor and separately classify corrected cyclic/symplectic extensions",
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_weyl_parity_complete_residual_exact_sequence --verify bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json", "python3 bridge/einstein_sector/verify_einstein_weyl_parity_complete_residual_exact_sequence.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_parity_complete_residual_exact_sequence"]
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text()) == build_certificate(), f"stale certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True)+"\n")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
