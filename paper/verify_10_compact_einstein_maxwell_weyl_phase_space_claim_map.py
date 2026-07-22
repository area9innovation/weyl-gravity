#!/usr/bin/env python3
"""Independent fail-closed verification for the Paper 10 claim map."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / "paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json"
POLAR = "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json"
PHASE1 = "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json"
MATERIALITY = "planning/paper-coverage/paper10-polar-extra-publication-boundary-repair-2026-07-22.json"
EXPECTED_HASHES = {
    POLAR: "f411d2e62c4ffa7436966d11f7d77e4c91b85d4ffbaf220f04f816bd80ec0b71",
    PHASE1: "7c045d4bde9e3961ad422faa0e6f8ca4d22cde76970e6071ca7a9bff392666d3",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(data: dict[str, object], *, verify_files: bool = True) -> None:
    require(data.get("schema") == "compact-linear-paper-claim-map-v1", "wrong schema")
    require(data.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"], "dependency boundary changed")
    scope = data.get("scope")
    require(isinstance(scope, dict), "scope missing")
    require("classified independently" in str(scope.get("extra_weyl_maxwell_target")), "independent parity classification missing")
    require("before any optional" in str(scope.get("quotient_stage")), "pre-residual stage missing")

    claims = data.get("certified_claims")
    require(isinstance(claims, dict), "certified claims missing")
    require(claims.get("generic_polar_extra_module_classified") is True, "polar classification not certified")
    require(claims.get("generic_polar_extra_positive_frequency_current_inertia") == [2, 0], "wrong polar extra inertia")
    require(claims.get("complete_generic_polar_positive_frequency_current_inertia") == [3, 1], "wrong complete polar inertia")
    require(claims.get("generic_axial_extra_positive_frequency_current_inertia") == [2, 0], "wrong axial extra inertia")
    require(claims.get("complete_generic_axial_positive_frequency_current_inertia") == [3, 1], "wrong complete axial inertia")
    require(claims.get("axial_polar_representatives_identified") is False, "axial and polar representatives were conflated")

    nonclaims = data.get("explicit_nonclaims")
    require(isinstance(nonclaims, dict), "explicit nonclaims missing")
    fail_closed = (
        "final_residual_descent_complete",
        "lorentzian_causal_bv_complex_certified",
        "positive_frequency_hilbert_space_constructed",
        "particle_interpretation_constructed",
        "linear_or_nonlinear_stability_theorem",
        "quantum_ghost_or_unitarity_theorem",
        "asymptotically_flat_scattering_constructed",
    )
    for key in fail_closed:
        require(nonclaims.get(key) is False, f"forbidden promotion: {key}")

    boundary = str(data.get("claim_boundary", ""))
    for phrase in ("before final residual descent", "No axial/polar representative identification", "No moment-map-zero or final residual quotient"):
        require(phrase in boundary, f"claim boundary omits: {phrase}")

    if verify_files:
        inputs = data.get("inputs")
        require(isinstance(inputs, dict), "input hash ledger missing")
        for relative, expected in inputs.items():
            require(sha256(ROOT / relative) == expected, f"input hash drift: {relative}")
        for relative, expected in EXPECTED_HASHES.items():
            actual = sha256(ROOT / relative)
            require(actual == expected, f"frozen source drift: {relative}")
            require(inputs.get(relative) == expected, f"claim map import hash mismatch: {relative}")

        polar = json.loads((ROOT / POLAR).read_text())
        require(polar.get("result_state") == "GENERIC_POLAR_DIRECT_4D_LEE_WALD_COMPLETION_CERTIFIED", "wrong polar source result")
        classification = polar.get("classification", {})
        require(classification.get("extra_polar_inertia_2_0") is True, "polar source does not certify (2,0)")
        require(classification.get("complete_polar_inertia_3_1") is True, "polar source does not certify (3,1)")
        require(classification.get("final_residual_descent_certified") is False, "polar source unexpectedly promotes residual descent")
        require(classification.get("causal_or_particle_claim") is False, "polar source unexpectedly promotes causal/particle claim")

        phase1 = json.loads((ROOT / PHASE1).read_text())
        require(phase1.get("result_state") == "PHASE1_EINSTEIN_EXTRA_STRUCTURAL_CONTRIBUTION_FROZEN", "wrong Phase-1 source result")
        polar_rows = [row for row in phase1.get("rows", []) if row.get("row_id") == "polar_direct_lee_wald"]
        require(len(polar_rows) == 1, "Phase-1 polar row missing or duplicated")
        require(polar_rows[0].get("scope", {}).get("carrier") == "local-gauge-reduced generic solution module", "Phase-1 polar carrier drift")

        manuscript = (ROOT / str(data.get("manuscript"))).read_text()
        required_tex = (
            "generic polar extra block has inertia $(2,0)$",
            "complete generic polar block has inertia $(3,1)$",
            "do not identify axial and polar representatives",
            "before the final residual quotient",
        )
        for phrase in required_tex:
            require(phrase in manuscript, f"manuscript omits: {phrase}")

        materiality = json.loads((ROOT / MATERIALITY).read_text())
        require(materiality.get("result_state") == "SCOPED_CORRECTION_APPLIED_FAIL_CLOSED", "materiality status drift")
        require(materiality.get("imports") == EXPECTED_HASHES, "materiality import ledger drift")
        paper10 = materiality.get("paper10", {})
        require(paper10.get("status") == "SCOPED_CORRECTION_APPLIED", "materiality correction not closed")
        require(paper10.get("claim_map_sha256") == sha256(DEFAULT_MAP), "materiality claim-map hash drift")
        require(paper10.get("manuscript_tex_sha256") == sha256(ROOT / str(data.get("manuscript"))), "materiality TeX hash drift")
        require(paper10.get("manuscript_pdf_sha256") == sha256(ROOT / "paper/10-compact-einstein-maxwell-weyl-phase-space.pdf"), "materiality PDF hash drift")


def mutation_tests(data: dict[str, object]) -> int:
    mutations: list[tuple[str, str, object]] = [
        ("nonclaim", "final_residual_descent_complete", True),
        ("nonclaim", "lorentzian_causal_bv_complex_certified", True),
        ("nonclaim", "positive_frequency_hilbert_space_constructed", True),
        ("nonclaim", "particle_interpretation_constructed", True),
        ("nonclaim", "linear_or_nonlinear_stability_theorem", True),
        ("nonclaim", "quantum_ghost_or_unitarity_theorem", True),
        ("claim", "axial_polar_representatives_identified", True),
    ]
    rejected = 0
    for section, key, value in mutations:
        candidate = copy.deepcopy(data)
        target = candidate["explicit_nonclaims" if section == "nonclaim" else "certified_claims"]
        target[key] = value
        try:
            verify(candidate, verify_files=False)
        except VerificationError:
            rejected += 1
        else:
            raise VerificationError(f"mutation accepted: {key}")
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()
    path = args.claim_map if args.claim_map.is_absolute() else ROOT / args.claim_map
    data = json.loads(path.read_text())
    verify(data)
    rejected = mutation_tests(data)
    print(f"PASS: Paper 10 polar-extra boundary verified; {rejected} adversarial promotions rejected")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        raise SystemExit(f"FAIL: {exc}")
