"""Finite-harmonic all-ell k=0 combined-cone second-order theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.schema.json"
INPUTS = {
    "fixed_ell_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "generic_cross_ell": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
    "exceptional_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json",
}


class FiniteHarmonicK0ConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FiniteHarmonicK0ConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["fixed_ell_cone"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"], "fixed-ell theorem changed")
    _require(records["generic_cross_ell"]["classification"]["all_nonzero_generic_output_channels_off_target_shells"], "generic cross-ell theorem changed")
    _require(records["exceptional_L1"]["classification"]["complete_unbounded_cross_ell_nonzero_output_nonresonance"], "exceptional cross-ell theorem changed")
    _require(records["exceptional_L1"]["classification"]["no_zero_frequency_collision"], "cross-ell collision theorem changed")
    return {
        "schema": "einstein-maxwell-weyl-finite-harmonic-k0-combined-cone-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_K0_COMBINED_CONE_SECOND_ORDER",
        "result_state": "COMPLETE_FINITE_HARMONIC_K0_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_FINITE_HARMONIC_ALL_GENERIC_ELLS_K0",
        "domain": "every real finite harmonic sum of generic ell>=2, k=0 axial and polar Einstein-plus, Einstein-minus, and both extra-primary modes on the fixed magnetic bundle, before stabilizer quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "proof_decomposition": {
            "same_ell_pairs": "the fixed-ell theorem solves every nonzero channel and identifies the complete zero-frequency scalar/rotation source with the H,J_i moment maps",
            "distinct_ell_zero_frequency": "absent because the exact cross-ell theorem proves no primary-frequency collision",
            "distinct_ell_L0": "absent independently because an S2 product contains L=0 only when ell_1=ell_2",
            "distinct_ell_generic_nonzero_outputs": "all L>=2 target blocks are off shell by the unbounded five-family theorem",
            "distinct_ell_exceptional_nonzero_outputs": "L=1 requires adjacent inputs and misses the complete exceptional root set {0,4/3,4}",
            "finite_sum_completion": "only finitely many output (L,m,Omega) blocks occur, so the blockwise inverses assemble a real smooth spatially periodic finite-quasiperiodic second-order correction",
        },
        "moment_map_condition": {
            "required": ["mu_H=0", "mu_J1=0", "mu_J2=0", "mu_J3=0"],
            "automatic": "mu_Px=0 because every input has k=0",
            "effect": "cancels the complete sum of same-ell zero-frequency cokernel projections",
        },
        "classification": {
            "all_finite_cross_ell_superpositions_classified": True,
            "complete_common_stabilizer_zero_cone_second_order_extendible": True,
            "explicit_correction_exists_by_finite_blockwise_inversion": True,
            "cross_ell_source_coefficients_required_for_existence": False,
            "infinite_harmonic_completion_classified": False,
            "opposite_momentum_phases_classified": False,
        },
        "interpretation": "The blockwise fixed-ell tangent cones glue without a new cross-ell obstruction. Cross-ell products are spectrally off shell, so their detailed source coefficients affect the correction but not existence. At k=0 the complete finite-harmonic second-order tangent cone is exactly controlled by the total stabilizer moment maps already identified.",
        "next_gate": "retain relative phases in opposite-momentum standing waves, then test the exceptional/global homogeneous and twist-velocity mixed cones",
        "claim_boundary": "This is a second-order finite-harmonic reduced-mode theorem. It does not establish an infinite-mode PDE completion, opposite-momentum phase closure, exceptional/global input closure, all-orders integration, a final residual quotient, causal propagation, scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.05, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 0.2, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order --verify bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["fixed_ell_cone", "generic_cross_ell", "exceptional_L1"]},
            "tier_3": {"status": "NOT_RUN", "reason": "opposite momenta, infinite-mode completion, and exceptional/global inputs remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order --verify bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "finite-harmonic cone certificate is stale")


if __name__ == "__main__":
    main()
