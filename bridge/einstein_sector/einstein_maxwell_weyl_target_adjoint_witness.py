"""Extract the compact constant-lapse target adjoint witness as a standalone gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_target_adjoint_witness.schema.json"


class TargetAdjointWitnessError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TargetAdjointWitnessError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, Any]:
    source = json.loads(DOMAIN_CERTIFICATE.read_text(encoding="utf-8"))
    _require(source["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "domain input changed")
    adjoint = source["adjoint_domain"]
    fixed = source["topology_and_charge_fibres"]["fixed_compact_u1_bundle"]
    _require("constraint adjoint cokernel" in adjoint["class"], "target adjoint class changed")
    _require(fixed["allowed_magnetic_lift"] is False, "fixed-bundle lift gate changed")
    _require(source["classification"]["cauchy_slice_independence"], "slice-independence gate changed")
    return {
        "schema": "einstein-maxwell-weyl-target-adjoint-witness-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TARGET_CONSTANT_LAPSE_ADJOINT_WITNESS",
        "result_state": "STANDALONE_FIXED_BUNDLE_TARGET_CONSTRAINT_ADJOINT_WITNESS_EXTRACTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_COMPACT_TARGET_ADJOINT_WITNESS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {str(DOMAIN_CERTIFICATE.relative_to(ROOT)): _sha256(DOMAIN_CERTIFICATE)},
        },
        "target_correction_domain": {
            "operator": "the action-derived coupled Weyl-Maxwell linearization L_WM at the compact product background",
            "fields": "smooth periodic second-order metric and fixed-P_N compact-U(1) connection corrections on R_t x S1 x S2",
            "pairing": adjoint["pairing"],
            "witness": "zeta_H=(K=partial_t,sigma=0,lambda_K=0), the constant-lapse/time-translation reducibility class",
            "annihilation": "<zeta_H,L_WM Phi^(2)>=0 for every correction in the declared target domain",
            "nontriviality_witness": adjoint["nontriviality_witness"],
            "cauchy_slice_independent": True,
            "fixed_bundle_magnetic_lift_allowed": False,
        },
        "temporal_correction_spaces": {
            "smooth_global": "smooth all-time periodic-in-space corrections; generalized/secular time dependence is not excluded",
            "bounded_normal_mode": "bounded separated normal-mode corrections; secular time dependence is excluded",
            "constant_lapse_verdict": "the compact constraint-adjoint annihilation holds on both spaces; temporal resonance only distinguishes other dynamical adjoint tests",
        },
        "classification": {
            "standalone_target_domain_witness": True,
            "independent_of_named_Einstein_fixture": True,
            "fixed_bundle_constraint_cokernel_class": True,
            "complete_spacetime_formal_adjoint_cokernel": False,
            "complete_target_correction_space_classification": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The constant-lapse class is a property of the Weyl-Maxwell target correction problem on the fixed compact bundle, not of a chosen Einstein fixture. Any quadratic source with nonzero pairing against it is non-removable by every declared second-order target correction, whether or not secular time dependence is admitted.",
        "next_gate": "pair each classified quadratic source channel with zeta_H and with the remaining harmonic target-adjoint classes; use temporal resonance only after declaring the bounded or generalized correction space",
        "claim_boundary": adjoint["qualification"] + " No causal, asymptotic, scattering, or quantum conclusion follows.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_target_adjoint_witness --verify bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_target_adjoint_witness",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale target adjoint witness: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
