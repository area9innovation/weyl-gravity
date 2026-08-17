#!/usr/bin/env python3
"""Independent verifier for the BT torus phase-pullback obstruction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_PHASE_PULLBACK_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-phase-pullback-obstruction-v1.schema.json",
)
PRODUCER_PATH = os.path.join(
    ROOT, "reverse_physics/bt_euclidean_torus_phase_pullback_obstruction.py"
)
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "POLYNOMIAL_CONTRAST_HIERARCHY_OBSTRUCTION_V1.json"
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def producer_not_imported() -> bool:
    with open(__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    forbidden = "bt_euclidean_torus_phase_pullback_obstruction"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(forbidden in alias.name for alias in node.names):
                return False
        if isinstance(node, ast.ImportFrom) and node.module and forbidden in node.module:
            return False
    return True


def cycle_rebuild(m: int) -> dict[str, object]:
    ramp = m**4
    slope = Fraction(m - 1, ramp)
    side = [
        Fraction(1) + slope * min(index, 2 * ramp - index)
        for index in range(2 * ramp + 1)
    ]
    ratios = side + [1 / side[2 * ramp - index] for index in range(2 * ramp + 1)]
    length = len(ratios)
    residual = [
        ratios[site] + 1 / ratios[(site - 1) % length] - 2
        for site in range(length)
    ]
    current = [
        residual[site] * ratios[site]
        - residual[(site + 1) % length] / ratios[site]
        for site in range(length)
    ]
    gradient = [
        current[(site - 1) % length] - current[site]
        for site in range(length)
    ]
    residual_norm = sum((value**2 for value in residual), Fraction(0))
    gradient_norm = sum((value**2 for value in gradient), Fraction(0))
    return {
        "length": length,
        "contrast": max(max(value, 1 / value) for value in ratios),
        "peak": current[ramp],
        "opposite": current[3 * ramp + 1],
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "quotient": gradient_norm / residual_norm,
    }


def direct_torus_rebuild(active: int) -> dict[str, Fraction]:
    length = 4
    values = [Fraction(1), Fraction(2), Fraction(4), Fraction(2)]
    sites = list(itertools.product(range(length), repeat=4))
    field = {
        site: values[sum(site[:active]) % length]
        for site in sites
    }
    residual: dict[tuple[int, ...], Fraction] = {}
    for site in sites:
        value = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                other = list(site)
                other[axis] = (other[axis] + step) % length
                value += field[tuple(other)] / field[site]
        residual[site] = value
    gradient: dict[tuple[int, ...], Fraction] = {}
    for site in sites:
        value = -residual[site] * (residual[site] + 8)
        for axis in range(4):
            for step in (-1, 1):
                source = list(site)
                source[axis] = (source[axis] - step) % length
                source_site = tuple(source)
                value += residual[source_site] * field[site] / field[source_site]
        gradient[site] = value
    residual_norm = sum((value**2 for value in residual.values()), Fraction(0))
    gradient_norm = sum((value**2 for value in gradient.values()), Fraction(0))
    return {
        "residual_norm": residual_norm,
        "gradient_norm": gradient_norm,
        "quotient": gradient_norm / residual_norm,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["producer_not_imported"] = producer_not_imported()
    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["predecessor_hash_current"] = (
        len(inputs) == 1
        and inputs[0].get("path") == INPUT_REL
        and inputs[0].get("sha256") == file_hash(INPUT_REL)
    )

    stored_rows = certificate.get("exact_hierarchy_fixtures", [])
    hierarchy_ok = len(stored_rows) == 3
    for stored, m in zip(stored_rows, (2, 3, 4)):
        rebuilt = cycle_rebuild(m)
        hierarchy_ok = hierarchy_ok and (
            stored.get("member") == m
            and stored.get("length") == rebuilt["length"]
            and decode(stored["maximum_edge_ratio"]) == rebuilt["contrast"]
            and decode(stored["peak_current"]) == rebuilt["peak"]
            and decode(stored["opposite_current"]) == rebuilt["opposite"]
            and decode(stored["residual_norm_squared"]) == rebuilt["residual_norm"]
            and decode(stored["gradient_norm_squared"]) == rebuilt["gradient_norm"]
            and decode(stored["cycle_quotient"]) == rebuilt["quotient"]
            and decode(stored["cycle_quotient_scaled_by_m6"])
            == rebuilt["quotient"] * m**6
            and decode(stored["two_active_coordinate_torus_quotient"])
            == 4 * rebuilt["quotient"]
            and all(stored.get("checks", {}).values())
        )
    checks["hierarchy_exactly_reconstructed"] = hierarchy_ok

    direct = certificate.get("exact_direct_torus_fixture", {})
    cycle_q = decode(direct["cycle_quotient"])
    torus_ok = len(direct.get("torus_rows", [])) == 4
    for row, active in zip(direct.get("torus_rows", []), range(1, 5)):
        rebuilt = direct_torus_rebuild(active)
        torus_ok = torus_ok and (
            row.get("active_coordinates") == active
            and decode(row["torus_residual_norm_squared"]) == rebuilt["residual_norm"]
            and decode(row["torus_gradient_norm_squared"]) == rebuilt["gradient_norm"]
            and decode(row["torus_quotient"]) == rebuilt["quotient"]
            and rebuilt["quotient"] == active**2 * cycle_q
            and decode(row["quotient_over_cycle"]) == active**2
        )
    checks["direct_4d_torus_enumeration"] = torus_ok

    theorem = certificate.get("phase_pullback_theorem", {})
    lower = certificate.get("hierarchy_lower_bound", {})
    corollary = certificate.get("four_torus_corollary", {})
    checks["theorem_formulas_pinned"] = (
        theorem.get("pointwise_identity")
        == "r_T(x)=k*rho_(chi_k(x)) and g_T(x)=k^2*h_(chi_k(x))"
        and theorem.get("quotient_identity") == "Q_T=k^2*Q_C"
        and lower.get("cycle_lower") == "Q_C>=1/(144m^6) for m>=4"
        and lower.get("cycle_upper")
        == "Q_C<=1960/m^6 for m>=8, imported from the predecessor"
        and corollary.get("normalized_bound")
        == "Q_T/omega_L^2>=k^2*m^10/(9*pi^4) for m>=4"
    )

    # Recheck the elementary inequalities at the first theorem value and the
    # monotone polynomial implications used thereafter.
    m = 4
    rebuilt = cycle_rebuild(m)
    checks["lower_bound_chain"] = (
        rebuilt["peak"] >= Fraction(m**2, 4)
        and rebuilt["opposite"] == -rebuilt["peak"]
        and rebuilt["gradient_norm"] >= Fraction(1, 6)
        and rebuilt["residual_norm"] <= 24 * m**6
        and rebuilt["quotient"] >= Fraction(1, 144 * m**6)
        and 3 * m**2 - 8 * m - 4 >= 0
        and 2 * m**4 + 1 <= 3 * m**4
        and 4 * m**4 + 2 >= 4 * m**4
    )

    disposition = certificate.get("research_disposition", {})
    checks["claim_boundary"] = (
        disposition.get("diagonal_or_helical_single_phase_lift") == "RULED_OUT"
        and disposition.get("genuinely_transverse_multiphase_corrector") == "OPEN"
        and disposition.get("all_field_torus_scaled_PL") == "OPEN"
        and disposition.get("full_witten_coercivity") == "OPEN"
        and disposition.get("lorentzian_transfer") == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate.get("dependency_tags") == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    nonclaims = set(certificate.get("does_not_establish", []))
    checks["required_nonclaims"] = {
        "a lower bound for arbitrary positive fields on T_L^4",
        "exclusion of genuinely multiphase or transverse corrector families",
        "boundedness or divergence of the interacting H^-1 moment",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(nonclaims)
    summary = certificate.get("checks", {})
    checks["certificate_checks_closed"] = (
        summary.get("ok") is True
        and summary.get("passed") == summary.get("total") == 10
        and not summary.get("failures")
        and all(summary.get("details", {}).values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} ({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=CERT_PATH)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
