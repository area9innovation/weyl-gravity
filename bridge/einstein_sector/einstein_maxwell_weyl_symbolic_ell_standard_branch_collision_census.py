"""Exact tuned all-ell collision census for q-minus and q-plus inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.schema.json"
INPUTS = {
    "qminus_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json",
    "parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json",
    "exceptional_target": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def symbolic_proof() -> dict[str, sp.Expr]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    shift = ell / 2 + sp.Rational(1, 6)
    k2 = root - shift
    minus2 = lam - shift
    plus2 = minus2 + 2 * root
    product_root = sp.sqrt(minus2 * plus2)
    mixed_sum_k0 = sp.factor(2 * (minus2 + root + product_root))
    mixed_sum_k2 = sp.factor(mixed_sum_k0 - 4 * k2)
    mixed_difference_k0 = sp.factor(2 * (minus2 + root - product_root))
    mixed_difference_k2 = sp.factor(mixed_difference_k0 - 4 * k2)
    top_lam = 2 * ell * (2 * ell + 1)
    top_p = top_lam - sp.Rational(2, 3)
    top_root = sp.sqrt(2 * top_lam)
    top_qplus = top_lam + top_root

    lower_rhs = ell**2 - ell / 2 - sp.Rational(1, 2) + root
    lower_square_gap = sp.factor(minus2 * plus2 - lower_rhs**2)
    expected_lower_gap = sp.Rational(2, 9) * (
        9 * ell * root + 3 * root + 9 * ell**3 - 6 * ell**2 - 12 * ell - 1
    )
    _require(sp.factor(lower_square_gap - expected_lower_gap) == 0, "mixed-sum lower witness changed")
    _require(sp.factor(mixed_sum_k2 - top_p - 2 * (product_root - lower_rhs)) == 0, "mixed-sum lower reduction changed")
    _require(sp.factor(4 * lam - mixed_sum_k2 - 2 * (minus2 + root - product_root)) == 0, "mixed-sum upper reduction changed")

    h = 4 * root - 2 * ell - sp.Rational(4, 3)
    h_positive_square = sp.factor(16 * root**2 - (2 * ell + sp.Rational(4, 3)) ** 2)
    h_top_square = sp.factor(h**2 - top_root**2)
    h_top_norm = sp.factor(
        (63 * ell**2 + 75 * ell + 4) ** 2
        - 2 * lam * (36 * ell + 24) ** 2
    )
    expected_h_norm = 1377 * ell**4 + 3402 * ell**3 + 1521 * ell**2 - 552 * ell + 16
    _require(sp.factor(h_top_norm - expected_h_norm) == 0, "mixed K0 upper norm changed")

    difference_denominator = minus2 + root + product_root
    rationalized_difference = sp.factor(4 * lam / difference_denominator)
    _require(sp.simplify(mixed_difference_k0 - rationalized_difference) == 0, "difference rationalization changed")
    difference_upper_witness = sp.factor(root**2 - (ell + sp.Rational(1, 3)) ** 2)
    difference_lower_witness = sp.factor((lam + 2 * shift) ** 2 - 4 * root**2)
    k_difference_witness = sp.factor(root**2 - (ell / 2 + sp.Rational(2, 3)) ** 2)

    qplus_k0 = sp.factor(4 * plus2)
    qplus_k2 = sp.factor(qplus_k0 - 4 * k2)
    _require(sp.factor(qplus_k0 - top_p - 8 * root) == 0, "qplus K0 reduction changed")
    _require(sp.factor(qplus_k2 - 4 * (lam + root)) == 0, "qplus K2 reduction changed")

    return {
        "ell": ell,
        "lambda": lam,
        "root": root,
        "k2": k2,
        "minus2": minus2,
        "plus2": plus2,
        "mixed_sum_k0": mixed_sum_k0,
        "mixed_sum_k2": mixed_sum_k2,
        "mixed_difference_k0": mixed_difference_k0,
        "mixed_difference_k2": mixed_difference_k2,
        "top_p": top_p,
        "top_qplus": top_qplus,
        "lower_rhs": lower_rhs,
        "lower_square_gap": lower_square_gap,
        "h": h,
        "h_positive_square": h_positive_square,
        "h_top_square": h_top_square,
        "h_top_norm": h_top_norm,
        "difference_upper_witness": difference_upper_witness,
        "difference_lower_witness": difference_lower_witness,
        "k_difference_witness": k_difference_witness,
        "qplus_k0": qplus_k0,
        "qplus_k2": qplus_k2,
    }


def build_certificate() -> dict[str, object]:
    inputs = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(inputs["qminus_census"]["classification"]["unique_nonzero_frequency_collision_is_L_2ell_K0_p_shell"], "qminus census changed")
    _require(inputs["parity_matrix"]["classification"]["complete_resonance_zero_variety_classified"], "parity matrix changed")
    proof = symbolic_proof()
    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-standard-branch-collision-census-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_STANDARD_BRANCH_COLLISION_CENSUS",
        "result_state": "TUNED_ALL_ELL_QPLUS_AND_QMINUS_STANDARD_BRANCH_COLLISION_CENSUS_COMPLETE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_INTEGER_ELL_ONE_TUNED_NONZERO_MOMENTUM_FIBRE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned separately for each ell",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all q-minus/q-plus self and cross products at signed momenta +/-k; no extra-primary inputs",
            "degree": 2,
            "parity": "over-complete shell arithmetic before parity selection",
            "ell": "every integer input ell>=2; target L=0,...,2ell",
            "m": "all angular outputs allowed by the product; no coefficient claim",
            "k": "+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)",
            "omega": "all positive sums and absolute differences of omega_minus and omega_plus",
        },
        "definitions": {
            "k_squared": str(proof["k2"]),
            "omega_minus_squared": str(proof["minus2"]),
            "omega_plus_squared": str(proof["plus2"]),
            "top_p_shell": str(proof["top_p"]),
            "top_qplus_shell": str(proof["top_qplus"]),
        },
        "qplus_self_exclusion": {
            "sum_K0": str(proof["qplus_k0"]),
            "sum_K2k": str(proof["qplus_k2"]),
            "proof": "both positive sums lie strictly above the largest L<=2ell target q-plus shell; same-branch differences have z<=0",
        },
        "mixed_branch_exclusion": {
            "sum_K0": str(proof["mixed_sum_k0"]),
            "sum_K2k": str(proof["mixed_sum_k2"]),
            "K2_ordering": "P(2ell)<z<Q_plus(2ell); every lower target lies below P(2ell)",
            "K2_lower_square_gap": str(proof["lower_square_gap"]),
            "K0_above_top_auxiliary_h": str(proof["h"]),
            "K0_h_positive_square": str(proof["h_positive_square"]),
            "K0_h_vs_top_root_square": str(proof["h_top_square"]),
            "K0_h_norm": str(proof["h_top_norm"]),
            "difference_K0": str(proof["mixed_difference_k0"]),
            "difference_interval": "4/3<z<2",
            "difference_upper_square_witness": str(proof["difference_upper_witness"]),
            "difference_lower_square_witness": str(proof["difference_lower_witness"]),
            "difference_K2k": str(proof["mixed_difference_k2"]),
            "difference_K2_negative_witness": str(proof["k_difference_witness"]),
        },
        "complete_collision_ledger": {
            "qminus_qminus": "one collision: positive sum, K=0, polar p-primary L=2ell",
            "qminus_qplus": "no characteristic collision",
            "qplus_qplus": "no characteristic collision",
            "exceptional_L1": "mixed K=0 difference lies strictly between 4/3 and 2, missing the certified 4/3 and 4 shells",
            "homogeneous_L0": "nonzero-frequency homogeneous quotient is empty; zero-frequency constraint rows remain governed by the declared moment-map gate",
        },
        "classification": {
            "all_standard_qminus_qplus_input_pairs_covered": True,
            "all_sum_difference_and_K0_K2k_channels_covered": True,
            "qplus_involving_characteristic_collisions_excluded": True,
            "unique_nonzero_frequency_standard_branch_collision_is_qminus_L2ell_p": True,
            "dynamical_null_variety_imported": True,
            "complete_bounded_second_order_extension_certified": False,
            "extra_primary_or_multiple_abs_momentum_inputs_classified": False,
            "causal_or_quantum_claim": False,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OPEN", "reason": "the nonzero-frequency shell ledger closes, but a complete zero-frequency and compatible-source join on the symbolic mixed sheets has not yet been certified"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "interpretation": "Adding the positive-energy q-plus balancing branch creates no new nonzero-frequency characteristic collision at the tuned fibre. The sole standard-branch resonance remains the q-minus L=2ell polar p shell already canceled on the two mixed-parity sheets. The remaining bounded gate is now the zero-frequency/source-compatibility join, not further dispersion arithmetic.",
        "next_gate": "join the common-zero moment-map construction, the symbolic mixed-parity sheets, the bounded twist-wave kernel and the zero-frequency compatible-source theorem to construct one all-ell bounded second-order jet",
        "claim_boundary": "This is a complete characteristic-shell census for standard q-minus/q-plus inputs at one separately tuned |k| per ell. It does not include extra-primary inputs, multiple |k| fibres, certify the complete bounded source equation, or make causal, residual, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build_certificate()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        _require(json.loads(OUTPUT.read_text(encoding="utf-8")) == value, "stale standard-branch census")
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_STANDARD_BRANCH_COLLISION_CENSUS: PASS")


if __name__ == "__main__":
    main()
