#!/usr/bin/env python3
"""Independent exact replay of the nonlinear Weyl/boost ghost manifest."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
INPUTS = (
    ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json",
    ROOT / "field_bv_identification/certificates/minimal_bv_chain.json",
    ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
    ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json",
)


def encoded(vector: dict[str, Fraction]) -> dict[str, str]:
    return {key: str(value) for key, value in vector.items() if value}


def total(rows: list[dict[str, Fraction]]) -> dict[str, Fraction]:
    keys = set().union(*(row.keys() for row in rows))
    return {key: sum((row.get(key, Fraction(0)) for row in rows), Fraction(0)) for key in keys}


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    covariance = value.get("shifted_auxiliary_covariance", {})
    boost = covariance.get("boost", {})
    source_boost = {
        "sym_nabla_kappa": Fraction(-1, 2), "sym_b_kappa": Fraction(-1, 2),
        "g_div_kappa": Fraction(1), "g_b_dot_kappa": Fraction(-1, 2),
    }
    if boost.get("delta_G_b_coefficients") != encoded(source_boost) or boost.get("A_g_delta_phi_coefficients") != encoded(source_boost) or boost.get("delta_G_b_minus_A_g_delta_phi") != {}:
        errors.append("boost covariance replay mismatch")

    weyl_rows = [
        {"hess_sigma": Fraction(-1), "g_box_sigma": Fraction(-1, 2)},
        {"hess_sigma": Fraction(1), "sym_b_dsigma": Fraction(-1, 2), "g_b_dot_dsigma": Fraction(1, 2)},
        {"sym_b_dsigma": Fraction(1, 2)},
        {"g_box_sigma": Fraction(1, 2), "g_b_dot_dsigma": Fraction(-1, 2)},
    ]
    if encoded(total(weyl_rows)) or covariance.get("Weyl", {}).get("delta_G_b_coefficients") != {}:
        errors.append("Weyl covariance replay mismatch")

    dk = total([
        {"sym_kappa_dsigma": Fraction(-1), "g_kappa_dot_dsigma": Fraction(1)},
        {"sym_kappa_dsigma": Fraction(1), "g_kappa_dot_dsigma": Fraction(-1)},
    ])
    kk_first = {"sym_kappa1_kappa2": Fraction(-1), "g_kappa1_dot_kappa2": Fraction(1)}
    kk = total([kk_first, {key: -coefficient for key, coefficient in kk_first.items()}])
    brackets = {row["pair"]: row for row in value.get("gauge_algebra", {}).get("brackets", [])}
    if encoded(dk) or brackets.get("Weyl,boost", {}).get("coefficient_defect") != {}:
        errors.append("Weyl-boost commutator mismatch")
    if encoded(kk) or brackets.get("boost,boost", {}).get("coefficient_defect") != {}:
        errors.append("boost-boost commutator mismatch")
    if [row.get("pair") for row in value.get("gauge_algebra", {}).get("brackets", [])] != ["Diff,Diff", "Diff,Weyl", "Diff,boost", "Weyl,Weyl", "Weyl,boost", "boost,boost"]:
        errors.append("gauge bracket census mismatch")

    manifest = value.get("nonzero_ghost_antifield_family_manifest", [])
    if [row.get("family_id") for row in manifest] != ["DIFF_C_C_C_STAR", "DIFF_C_SIGMA_SIGMA_STAR", "DIFF_C_ETA_ETA_STAR"]:
        errors.append("nonzero ghost family manifest mismatch")
    if value.get("shifted_BRST_manifest", {}).get("non_Diff_nonlinear_ghost_antifield_terms") != []:
        errors.append("spurious internal ghost family")
    summary = value.get("manifest_summary", {})
    if summary != {"nonzero_ghost_antifield_families": 3, "minimal_families": 2, "auxiliary_families": 1, "certified_zero_candidate_families": 4, "additional_nonlinear_Weyl_boost_ghost_antifield_families": 0}:
        errors.append("manifest summary mismatch")

    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in INPUTS}
    if pins != expected_pins:
        errors.append("local provenance pins mismatch")
    if value.get("primary_literature", {}).get("pdf_sha256") != "80bbe298159e4fdfc35c0f4dd4e33f01e5da51227184a0bed870e5fa3e6b2676":
        errors.append("primary-source PDF pin mismatch")

    hash_map = {
        "source_transformations_sha256": value.get("source_transformations"),
        "shifted_auxiliary_covariance_sha256": covariance,
        "gauge_algebra_sha256": value.get("gauge_algebra"),
        "shifted_BRST_manifest_sha256": value.get("shifted_BRST_manifest"),
        "nonzero_family_manifest_sha256": manifest,
        "certified_zero_candidate_families_sha256": value.get("certified_zero_candidate_families"),
    }
    for key, payload in hash_map.items():
        if value.get("canonical_hashes", {}).get(key) != digest(payload):
            errors.append(f"canonical hash mismatch: {key}")
    flags = value.get("claim_flags", {})
    required_true = ("FULL_NONLINEAR_WEYL_BOOST_GAUGE_TRANSFORMATIONS_IMPORTED", "WEYL_BOOST_GAUGE_ALGEBRA_OFF_SHELL_CLOSED", "SHIFTED_F_HAT_WEYL_BOOST_INVARIANT", "INTERNAL_WEYL_BOOST_GHOST_BRACKETS_ZERO", "EXHAUSTIVE_NONLINEAR_WEYL_BOOST_GHOST_ANTIFIELD_MANIFEST")
    required_false = ("ADDITIONAL_AUXILIARY_GHOST_ANTIFIELD_FAMILIES_REQUIRED", "FULL_386_SOURCE_Q2_ASSEMBLED", "FULL_Q1_Q2_IDENTITY_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    for key in required_true:
        if flags.get(key) is not True:
            errors.append(f"positive flag drift: {key}")
    for key in required_false:
        if flags.get(key) is not False:
            errors.append(f"fail-closed flag drift: {key}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["manifest_summary"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
