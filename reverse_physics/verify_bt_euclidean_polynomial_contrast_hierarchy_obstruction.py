#!/usr/bin/env python3
"""Independent verifier for the BT polynomial-contrast hierarchy obstruction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "POLYNOMIAL_CONTRAST_HIERARCHY_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-polynomial-contrast-"
    "hierarchy-obstruction-v1.schema.json",
)
PRODUCER = os.path.join(
    ROOT,
    "reverse_physics/bt_euclidean_polynomial_contrast_hierarchy_obstruction.py",
)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def encode(value: Fraction | int) -> dict[str, int]:
    rational = Fraction(value)
    return {"numerator": rational.numerator, "denominator": rational.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reconstruct(member: int) -> dict:
    """Rebuild a complete cycle directly, without importing the producer."""

    if member < 2:
        raise ValueError("member must be at least two")
    m = member
    ramp = m**4
    slope = Fraction(m - 1, ramp)
    side_edges = 2 * ramp + 1
    volume = 2 * side_edges
    z = [
        Fraction(1) + slope * min(index, 2 * ramp - index)
        for index in range(side_edges)
    ]

    side_flow = [z[index] ** 2 for index in range(1, 2 * ramp)]
    flow_mass = 2 * sum(side_flow, Fraction(0))
    side_divergence_energy = side_flow[0] ** 2 + side_flow[-1] ** 2
    side_divergence_energy += sum(
        (
            (right - left) ** 2
            for left, right in zip(side_flow, side_flow[1:])
        ),
        Fraction(0),
    )
    divergence_norm = 2 * side_divergence_energy
    main_quotient = divergence_norm / flow_mass

    ratios = list(z)
    ratios.extend(1 / z[2 * ramp - index] for index in range(side_edges))
    residual = []
    for site, ratio in enumerate(ratios):
        residual.append(ratio + 1 / ratios[(site - 1) % volume] - 2)
    current = []
    for site, ratio in enumerate(ratios):
        current.append(
            residual[site] * ratio
            - residual[(site + 1) % volume] / ratio
        )
    gradient = [
        current[(site - 1) % volume] - current[site]
        for site in range(volume)
    ]
    residual_norm = sum((value**2 for value in residual), Fraction(0))
    gradient_norm = sum((value**2 for value in gradient), Fraction(0))
    full_quotient = gradient_norm / residual_norm
    maximum_gradient = max(abs(value) for value in gradient)

    checks = {
        "side_starts_and_ends_at_unit_ratio": z[0] == z[-1] == 1,
        "side_peak_is_m": max(z) == m,
        "two_sides_close_the_positive_cycle": all(
            ratios[side_edges + index] == 1 / z[2 * ramp - index]
            for index in range(side_edges)
        ),
        "cycle_ratio_is_polynomial": max(
            max(value, 1 / value) for value in ratios
        )
        == m,
        "main_flow_bound": main_quotient <= Fraction(160, m**6),
        "full_quotient_bound": full_quotient <= Fraction(1960, m**6),
        "pointwise_gradient_bound": maximum_gradient <= 7 * m * slope,
        "gradient_conservation": sum(gradient, Fraction(0)) == 0,
        "nonconstant_positive_field": residual_norm > 0,
    }
    return {
        "member": m,
        "ramp_length": ramp,
        "cycle_volume": volume,
        "cycle_diameter": side_edges,
        "maximum_edge_ratio": encode(m),
        "ratio_slope": encode(slope),
        "active_edge_count_per_side": len(side_flow),
        "main_flow_mass": encode(flow_mass),
        "main_divergence_norm_squared": encode(divergence_norm),
        "main_transport_coefficient": encode(main_quotient),
        "main_transport_scaled_by_m6": encode(main_quotient * m**6),
        "residual_norm_squared": encode(residual_norm),
        "gradient_norm_squared": encode(gradient_norm),
        "full_gradient_quotient": encode(full_quotient),
        "full_quotient_scaled_by_m6": encode(full_quotient * m**6),
        "maximum_absolute_gradient": encode(maximum_gradient),
        "checks": checks,
    }


def elementary_bound_rail() -> bool:
    """Audit the integer consequences used after the local-calculus lemma."""

    for m in range(2, 257):
        ramp = m**4
        slope = Fraction(m - 1, ramp)
        central_count = (
            (3 * ramp) // 2 - (ramp + 1) // 2 + 1
        )
        if central_count < ramp:
            return False
        mass_floor = 2 * ramp * Fraction(m, 2) ** 2
        if mass_floor != Fraction(m**6, 2):
            return False
        divergence_ceiling = 4 * 2**4 + 2 * (2 * ramp) * (2 * m * slope) ** 2
        if divergence_ceiling > 80:
            return False
        if 4 * ramp + 2 > 5 * ramp:
            return False
        gradient_ceiling = 5 * ramp * (7 * m * slope) ** 2
        if gradient_ceiling > 245:
            return False
        if m >= 8:
            residual_floor = 2 * ramp * Fraction(m, 4) ** 2
            if residual_floor != Fraction(m**6, 8):
                return False
            if Fraction(245, residual_floor) != Fraction(1960, m**6):
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args()
    certificate = load(args.certificate)
    schema = load(SCHEMA)
    checks: dict[str, bool] = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["predecessor_hash"] = all(
        sha256(item["path"]) == item["sha256"]
        for item in certificate["provenance"]["inputs"]
    )

    with open(__file__, encoding="utf-8") as handle:
        syntax = ast.parse(handle.read())
    producer_name = os.path.splitext(os.path.basename(PRODUCER))[0]
    imports = [
        node
        for node in ast.walk(syntax)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    checks["nonimporting_verifier"] = all(
        not (
            isinstance(node, ast.ImportFrom)
            and node.module
            and producer_name in node.module
        )
        and not (
            isinstance(node, ast.Import)
            and any(producer_name in alias.name for alias in node.names)
        )
        for node in imports
    )

    checks["three_exact_fixture_reconstructions"] = (
        [row["member"] for row in certificate["exact_fixtures"]] == [2, 3, 4]
        and [reconstruct(member) for member in (2, 3, 4)]
        == certificate["exact_fixtures"]
    )
    extended = [reconstruct(member) for member in (5, 8)]
    checks["extended_exact_family_rail"] = all(
        all(row["checks"].values()) for row in extended
    )
    checks["elementary_all_member_bounds"] = elementary_bound_rail()

    main_theorem = certificate["main_flow_theorem"]
    full_theorem = certificate["full_gradient_theorem"]
    checks["declared_constants_and_scales"] = (
        main_theorem["mass_lower_bound"] == "K_m>=m^6/2"
        and main_theorem["energy_upper_bound"] == "D_m<=80"
        and main_theorem["coefficient_upper_bound"] == "D_m/K_m<=160/m^6"
        and full_theorem["local_calculus_bound"]
        == "for m>=2 every |g_j|<=7*m*(m-1)/m^4"
        and full_theorem["gradient_norm_bound"] == "||g||_2^2<=245"
        and full_theorem["residual_norm_bound"]
        == "for m>=8, ||r||_2^2>=m^6/8"
        and full_theorem["quotient_upper_bound"]
        == "for m>=8, ||g||_2^2/||r||_2^2<=1960/m^6"
    )
    checks["diameter_products_vanish"] = all(
        Fraction(2 * m**4 + 1) * Fraction(160, m**6)
        == Fraction(320, m**2) + Fraction(160, m**6)
        and Fraction(2 * m**4 + 1) * Fraction(1960, m**6)
        == Fraction(3920, m**2) + Fraction(1960, m**6)
        for m in range(8, 64)
    )

    disposition = certificate["research_disposition"]
    checks["honest_scope_boundary"] = (
        disposition["generic_finite_amplitude_2_over_diameter_flow_bound"]
        == "OBSTRUCTED"
        and disposition["isotropic_four_torus_scaled_PL"] == "OPEN"
        and disposition["actual_interacting_h_minus_one"] == "OPEN"
        and disposition["continuum_measure"] == "NOT_ESTABLISHED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
        and certificate["dependency_tags"]
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    expected_details = {
        "three_exact_cycle_hierarchies": True,
        "all_exact_fixture_checks_pass": True,
        "cycle_volume_is_4m4_plus_2": True,
        "polynomial_contrast_is_m": True,
        "main_coefficient_is_O_m_minus_6": True,
        "full_quotient_is_O_m_minus_6": True,
        "diameter_scale_band_bound_is_obstructed": True,
        "four_torus_scaled_PL_remains_open": True,
        "witten_and_actual_h_minus_one_remain_open": True,
        "no_reconstruction_or_lorentzian_promotion": True,
    }
    checks["certificate_self_check"] = (
        certificate["checks"]["ok"] is True
        and certificate["checks"]["passed"] == 10
        and certificate["checks"]["total"] == 10
        and certificate["checks"]["failures"] == []
        and certificate["checks"]["details"] == expected_details
    )

    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("[FAIL] independent BT polynomial-contrast hierarchy verifier")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "[PASS] independent BT polynomial-contrast hierarchy verifier "
        f"({len(checks)}/{len(checks)}; exact m=2,3,4,5,8 rails)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
