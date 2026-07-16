"""Certify all mixed blocks in the standard Einstein harmonic pullback."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_mixed_block_orthogonality.schema.json"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_twist_physical_mixed_lee_wald_fixture.py"
INPUTS = {
    "direct_fixture": ROOT / "bridge/certificates/weyl_maxwell_twist_physical_mixed_lee_wald_fixture.json",
    "radiative": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "physical_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
}


class MixedBlockOrthogonalityError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MixedBlockOrthogonalityError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    expected = {
        "direct_fixture": "WEYL_MAXWELL_TWIST_PHYSICAL_MIXED_LEE_WALD_FIXTURE",
        "radiative": "EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION",
        "physical_ell1": "EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION",
        "homogeneous": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION",
        "twist": "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION",
    }
    for name, result_id in expected.items():
        _require(records[name]["result_id"] == result_id, f"{name} input changed")
    direct = records["direct_fixture"]["direct_current"]
    _require(direct["on_shell_polynomial_remainder"] == "0", "shared-label mixed current changed")
    _require(direct["includes_twist_Jordan_partner_Bt"] is True, "twist Jordan partner omitted")
    theorem = {
        "direct_shared_label_collision": {
            "sectors": "axial ell=1 twist versus physical axial ell=1 at n=0 and the same real m",
            "integrated_coordinate_current_per_unit_x": direct["integrated_coordinate_current_per_unit_x"],
            "physical_shell": direct["physical_dispersion"],
            "exact_off_shell_factor": direct["exact_factor"],
            "on_shell_value": "0",
            "full_time_identity": direct["full_time_identity"],
            "both_twist_Jordan_coordinates_included": True,
            "all_real_m": True,
        },
        "remaining_mixed_blocks": {
            "different_ell_or_m": "zero by SO(3) invariance and orthogonality in a real harmonic basis",
            "different_periodic_momentum": "zero by S1 Fourier orthogonality; the twist exists only at n=0",
            "axial_vs_polar": "zero by spatial parity invariance",
            "distinct_radiative_master_branches": "zero because the master operator is Omega_EM-self-adjoint, the target relative operator is its polynomial, and the branch eigenvalues are distinct",
            "homogeneous_vs_nonzero_ell": "zero by SO(3) harmonic orthogonality",
            "only_shared_label_case_not_settled_by_these_rules": "the twist/physical axial ell=1,n=0 collision, closed by the direct fixture above",
        },
        "conclusion": {
            "complete_standard_block_diagonal_pullback": True,
            "mixed_matrix_between_four_declared_block_families": "0",
            "basis_independence": "orthogonality is a property of the invariant subspaces; the direct collision calculation is zero for arbitrary A,B,p",
        },
    }
    return {
        "schema": "einstein-maxwell-weyl-mixed-block-orthogonality-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_MIXED_BLOCK_ORTHOGONALITY",
        "result_state": "COMPLETE_STANDARD_BLOCK_MIXED_PULLBACK_ZERO_DIRECT_SHARED_LABEL_COLLISION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_STANDARD_HARMONIC_MIXED_BLOCKS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "direct_fixture_generator": {"path": str(FIXTURE_GENERATOR.relative_to(ROOT)), "sha256": _sha256(FIXTURE_GENERATOR)},
        },
        "domain": "mixed Weyl-Maxwell Lee-Wald pullback blocks among standard ell>=2 radiation, physical ell=1, homogeneous ell=0, and generalized axial ell=1 twist Einstein-Maxwell tangents on the fixed compact bundle, before final residual quotient",
        "theorem": theorem,
        "classification": {
            "direct_twist_physical_same_label_current_computed": True,
            "twist_Jordan_partner_included": True,
            "all_standard_mixed_blocks_zero": True,
            "complete_standard_block_diagonal_pullback_certified": True,
            "extra_fourth_order_target_mixed_pairing_computed": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_quantum_theorem": False,
        },
        "interpretation": "The block diagonal structure used by the complete standard-harmonic inclusion is now explicit. The only collision not settled by harmonic, Fourier, parity, or distinct-branch orthogonality is the axial ell=1 twist versus physical n=0 oscillator. Its literal mixed current contains the exact physical equation factor omega^2-4, including both the constant twist and its time-linear Jordan partner, and therefore vanishes on shell.",
        "next_gate": "freeze and solve the canonical quotient of the full Weyl-Maxwell harmonic solution complex by the certified standard Einstein-Maxwell image",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies only mixed orthogonality inside the standard Einstein-Maxwell image. It does not compute extra fourth-order target representatives or their mixed pairings, final residual descent, causal scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.weyl_maxwell_twist_physical_mixed_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_twist_physical_mixed_lee_wald_fixture.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_mixed_block_orthogonality --verify bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_mixed_block_orthogonality.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_mixed_block_orthogonality",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale mixed-block certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
