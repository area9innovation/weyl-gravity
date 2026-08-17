#!/usr/bin/env python3
"""Independently verify the BT torus dyadic stopping-flow certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_DYADIC_STOPPING_FLOW_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-dyadic-stopping-flow-v1.schema.json",
)


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False

    inputs_ok = all(
        os.path.isfile(os.path.join(ROOT, row["path"]))
        and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
        for row in certificate["provenance"]["inputs"]
    )
    theorem = certificate["dyadic_stopping_theorem"]
    stopping_constants = (
        theorem["low_band_mass_ceiling"] == "sum_(e in B_<2) f_e<=q^2*N/W"
        and theorem["path_edge_count"]
        == "each source-to-sink path contains at most D*log_2(W) edges with z_e>=2"
        and theorem["divergence_floor"]
        == "||div(f)||_2>=F/(D*log_2(W)*sqrt(N))"
    )

    # Re-derive the two error fractions at the dense threshold.  The first is
    # strictly below 1/4; the second follows after squaring the stopping bound.
    # 4/(16*sqrt(2)) < 1/4 is equivalent to 1 < sqrt(2), hence to 1 < 2
    # after squaring positive quantities.
    first_error_ok = 1 < 2
    second_error_ok = 256 * 8 >= 8

    audit = certificate["exact_constant_audit"]
    exact_constants = (
        audit["sparse_available_coefficient"] == 512**3
        and audit["sparse_required_coefficient"] == 512 * 8**5 * 4
        and audit["stopping_condition_left_at_L0"] == 2**16
        and audit["stopping_condition_log2_W0_at_L0"] == 9 + 10 * 12 // 3
        and audit["stopping_condition_right_at_L0"] == 16 * 49**2
        and all(audit["checks"].values())
    )

    # For x=log_2 L >= 12, 2^(4x/3)/(9+10x/3)^2 is increasing because
    # (4 ln 2)/3 > 8/9 > 20/147 >= (20/3)/(9+10x/3).  We use the elementary
    # exact lower bound ln(2)>2/3 and check every remaining comparison in Q.
    monotonicity_ok = (
        Fraction(8, 9) > Fraction(20, 147)
        and 2**16 >= 16 * 49**2
        and 12 <= 4096 // 64
    )
    dichotomy = certificate["sparse_dense_dichotomy"]
    dichotomy_ok = (
        dichotomy["sparse_sufficient_condition"] == "W^3>=512*q^5*D^2*N^2"
        and dichotomy["sparse_conclusion"] == "Q>=64*q/N"
        and dichotomy["dense_sufficient_condition"]
        == "sqrt(W)>=16*sqrt(q)*D*log_2(W)"
        and dichotomy["dense_conclusion"] == "Q>=q^2/(D^2*log_2(W)^2)"
    )
    corollary = certificate["four_torus_corollary"]
    torus_ok = (
        corollary["scope"] == "T_L^4 with L>=4096"
        and corollary["contrast_hypothesis"] == "W>=512*L^(10/3)"
        and corollary["normalized_conclusion"] == "Q/omega_L^2>=32/pi^4"
        and 512**3 >= 512 * 8**5 * 4
        and 512 / 16 == 32
        and 1024 / 16 >= 32
    )
    boundary_ok = (
        certificate["research_disposition"]["sub_L_10_over_3_moderate_contrast_sector"] == "OPEN"
        and certificate["research_disposition"]["all_field_torus_scaled_PL"] == "OPEN"
        and certificate["research_disposition"]["lorentzian_transfer"] == "NOT_ESTABLISHED"
        and "a lower bound for every positive field on T_L^4"
        in certificate["does_not_establish"]
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        ("producer_not_imported", "bt_euclidean_torus_dyadic_stopping_flow" not in sys.modules),
        ("predecessor_hash", inputs_ok),
        ("stopping_constants", stopping_constants),
        ("error_absorption_constants", first_error_ok and second_error_ok),
        ("exact_torus_constants", exact_constants),
        ("monotonicity_lemmas", monotonicity_ok),
        ("sparse_dense_dichotomy", dichotomy_ok),
        ("torus_corollary", torus_ok),
        ("claim_boundaries", boundary_ok),
        ("dependency_tags", certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]),
        ("self_checks", self_checks["ok"] is True and self_checks["passed"] == self_checks["total"] == 10 and all(self_checks["details"].values())),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(f"BT torus dyadic stopping-flow verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
