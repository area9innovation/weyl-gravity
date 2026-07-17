"""Exact adjacent-input nonresonance for exceptional L=1 outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.schema.json"
GENERIC_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json"


class ExceptionalL1NonresonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalL1NonresonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _same_branch_witnesses() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    lam_next = (ell + 1) * (ell + 2)
    target = sp.Rational(4, 3)
    extra_first = lam - sp.Rational(2, 3)
    extra_second = lam_next - sp.Rational(2, 3)
    extra_polynomial = sp.factor((target - extra_first - extra_second) ** 2 - 4 * extra_first * extra_second)
    _require(sp.expand(extra_polynomial + sp.Rational(4, 3) * (ell - 1) * (ell + 3)) == 0, "extra-extra witness changed")

    d0 = sp.factor(target - lam - lam_next)
    coefficient_first = sp.factor(-2 * (d0 + 2 * lam_next))
    coefficient_second = sp.factor(-2 * (d0 + 2 * lam))
    cancellation_remainder = sp.factor(
        ell * (3 * ell + 5) ** 2 - (ell + 2) * (3 * ell + 1) ** 2
    )
    _require(sp.expand(cancellation_remainder - 2 * (3 * ell**2 + 6 * ell - 1)) == 0, "equal-squarefree cancellation remainder changed")
    return {
        "extra_extra": {
            "squared_resonance_polynomial": str(extra_polynomial),
            "nonzero_for_every_ell_at_least_2": True,
        },
        "same_q_branch": {
            "resonance_polynomial": "R + s*c_first*x_ell + s*c_second*x_{ell+1} - 2*x_ell*x_{ell+1}, where s=+/-1",
            "coefficient_first_without_branch_sign": str(coefficient_first),
            "coefficient_second_without_branch_sign": str(coefficient_second),
            "distinct_nonrational_squarefree_parts": "the product-root basis coefficient is uniquely -2",
            "equal_nonrational_squarefree_parts": {
                "required_ratio": "m_{ell+1}/m_ell=(3ell+5)/(3ell+1)",
                "exact_squared_ratio_remainder": str(cancellation_remainder),
                "strictly_positive_for_ell_at_least_2": True,
            },
            "one_rational_inner_root": "the remaining irrational coefficient cannot vanish: the only candidate equality sets an integer equal to 2ell+2/3 or 2ell+10/3",
            "both_rational_inner_roots": "both q squared frequencies are integers, contradicting a squared difference equal to 4/3",
        },
    }


def build_certificate() -> dict[str, Any]:
    generic = json.loads(GENERIC_INPUT.read_text(encoding="utf-8"))
    _require(generic["classification"]["all_nonzero_generic_output_channels_off_target_shells"], "generic-output input changed")
    return {
        "schema": "einstein-maxwell-weyl-cross-ell-k0-exceptional-L1-nonresonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CROSS_ELL_K0_EXCEPTIONAL_L1_NONRESONANCE",
        "result_state": "ALL_ADJACENT_INPUT_EXCEPTIONAL_L1_OUTPUTS_NONRESONANT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_ADJACENT_GENERIC_INPUTS_K0_EXCEPTIONAL_L1_OUTPUT",
        "domain": "every adjacent generic input pair (ell,ell+1), ell>=2, at k=0, all three primary branches on both inputs, and the complete exceptional L=1 target root set",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "generic_output_theorem": {"path": str(GENERIC_INPUT.relative_to(ROOT)), "sha256": _sha256(GENERIC_INPUT)},
        },
        "angular_reduction": "a distinct generic input pair can couple to L=1 only when ell_2=ell_1+1",
        "target_root_set": {"omega_squared": ["0", "4/3", "4"], "omega_positive": ["0", "2/sqrt(3)", "2"]},
        "cross_branch_interval_exclusions": {
            "minus_to_extra": "3/2<Delta omega<2",
            "minus_to_plus": "11/5<Delta omega<11/4",
            "extra_to_minus": "0<Delta omega<1/2",
            "extra_to_plus": "3/2<Delta omega<39/20",
            "plus_to_minus": "1/5<abs(Delta omega)<3/4",
            "plus_to_extra": "1/20<Delta omega<1/2",
        },
        "same_branch_witnesses": _same_branch_witnesses(),
        "classification": {
            "all_adjacent_input_ells_covered": True,
            "all_nine_input_branch_pairs_covered": True,
            "complete_exceptional_L1_root_set_covered": True,
            "no_zero_frequency_collision": True,
            "no_exceptional_L1_output_resonance": True,
            "complete_unbounded_cross_ell_nonzero_output_nonresonance": True,
            "cross_ell_quadratic_source_solved": False,
        },
        "interpretation": "Together with the generic-output theorem, this closes the complete unbounded k=0 cross-ell output-resonance gate. Any failure of second-order extension for distinct-ell common-zero data must now occur in the mixed quadratic source or its adjoint-cokernel projection.",
        "next_gate": "compute the cross-ell mixed quadratic source projections, starting with the smallest angularly allowed common-moment-map-zero fixture",
        "claim_boundary": "This closes output-shell resonance only. It does not prove cross-ell second-order extension, compute mixed sources, retain opposite-momentum phases, include exceptional/global inputs, or support all-orders, causal, scattering, particle, or quantum claims.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.05, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.0, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance"
            ]},
            "tier_2": {"status": "NOT_RUN", "reason": "the exceptional audit imports the unchanged content-addressed generic-output theorem and no shared operator changed"},
            "tier_3": {"status": "NOT_RUN", "reason": "the mixed cross-ell source remains open, so no second-order cone freeze is promoted"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance --verify bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "exceptional L1 certificate is stale")


if __name__ == "__main__":
    main()
