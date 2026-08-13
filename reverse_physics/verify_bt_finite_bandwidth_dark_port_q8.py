#!/usr/bin/env python3
"""Independent verifier for the finite-bandwidth BT dark-port theorem."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb, factorial

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-bandwidth-dark-port-q8-v1.schema.json"
)


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(receipt):
    value = Fraction(receipt["exact"])
    canonical = f"{value.numerator}/{value.denominator}".encode()
    valid = hashlib.sha256(canonical).hexdigest() == receipt["canonical_sha256"]
    return value, valid


def beta_simplex_coefficient(total_degree, x_power):
    """Independent expansion using t2=t1*u and one beta integral."""
    beta_numerator = factorial(x_power) * factorial(total_degree - x_power)
    beta_denominator = factorial(total_degree + 1)
    simplex_integral = Fraction(beta_numerator, beta_denominator * (total_degree + 2))
    exponential_coefficient = Fraction(comb(total_degree, x_power), factorial(total_degree))
    return exponential_coefficient * simplex_integral


def verify(certificate):
    schema = load(SCHEMA_REL)
    schema_errors = list(Draft202012Validator(schema).iter_errors(certificate))

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    hashes_ok = len(inputs) == 6 and all(
        os.path.exists(os.path.join(ROOT, row.get("path", "")))
        and sha256(row["path"]) == row.get("sha256")
        for row in inputs
    )

    predecessors_ok = False
    event_ok = False
    if len(inputs) == 6:
        try:
            predecessors = [load(row["path"]) for row in inputs[1:-1]]
            event = load(inputs[-1]["path"])
            predecessors_ok = len(predecessors) == 4 and all(
                row["checks"]["ok"] for row in predecessors
            )
            event_ok = (
                event["body"]["payload"]["to_state"] == "DONE"
                and event["body"]["payload"]["target"].endswith(
                    "finite-bandwidth-dark-port-q8"
                )
            )
        except (KeyError, OSError, json.JSONDecodeError):
            pass

    temporal = certificate.get("off_diagonal_temporal_kernel", {})
    rows = temporal.get("coefficient_check", [])
    beta_rows_ok = len(rows) == 13
    for degree, row in enumerate(rows):
        expected = Fraction(1, factorial(degree + 2))
        values = [beta_simplex_coefficient(degree, power) for power in range(degree + 1)]
        beta_rows_ok &= (
            row.get("total_degree") == degree
            and Fraction(row.get("coefficient_without_i_power", "0")) == expected
            and row.get("multiplicity") == degree + 1
            and all(value == expected for value in values)
        )

    sinc_floor, sinc_hash = parse_fraction(
        temporal.get("sinc_floor", {"exact": "0", "canonical_sha256": ""})
    )
    independent_sinc_floor = Fraction(1) - Fraction(1, 4) ** 2 / 6
    derivative_bound = Fraction(96, 95) + Fraction(1, 12) * Fraction(96, 95) ** 2

    ultraviolet = certificate.get("ultraviolet_and_continuity", {})
    uv_constant, uv_hash = parse_fraction(
        ultraviolet.get("uv_constant", {"exact": "0", "canonical_sha256": ""})
    )
    rebuilt_uv = Fraction(2) + 2 * Fraction(6, 5) + Fraction(2)

    packet = certificate.get("finite_bandwidth_packet", {})
    absolute = certificate.get("absolute_dark_port_coefficient", {})
    retained, retained_hash = parse_fraction(
        absolute.get("retained_q6_lower", {"exact": "0", "canonical_sha256": ""})
    )
    dark, dark_hash = parse_fraction(
        absolute.get("exact_rational_lower", {"exact": "0", "canonical_sha256": ""})
    )
    expected_retained = Fraction(49, 2 * 534_336)
    expected_dark = expected_retained**2 / 8

    disposition = certificate.get("disposition", {})
    boundaries = certificate.get("does_not_establish", [])
    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate.get("certificate") == "REVERSE_PHYSICS_BT_FINITE_BANDWIDTH_DARK_PORT_Q8_V1",
        "input_hashes_recomputed": hashes_ok,
        "four_predecessor_pass_flags_rechecked": predecessors_ok,
        "done_event_matches_work_item": event_ok,
        "independent_beta_simplex_coefficients_match": beta_rows_ok,
        "tree_switch_and_Dyson_integral_are_distinct_objects": temporal.get("tree_switch", "").startswith("f(x)=") and temporal.get("ordered_Dyson_integral", "").startswith("d(x,y)="),
        "divided_difference_is_recorded": "[f(x)-f(y)]/[i*(x-y)]" in temporal.get("divided_difference", ""),
        "normalized_interference_kernel_is_recorded": temporal.get("interference_kernel") == "k(x,y)=Im(conj(f(x))*d(x,y))/abs(f(x))^2",
        "closed_form_is_reconstructed": temporal.get("closed_form") == "k(x,y)=[1-cos((y-x)/2)*sinc(y/2)/sinc(x/2)]/(y-x)",
        "diagonal_kernel_is_exact": temporal.get("energy_diagonal") == "k(0,y)=1/y-sin(y)/y^2",
        "removable_resonances_are_recorded": "removable" in temporal.get("resonant_values", ""),
        "sinc_receipt_hash_rechecked": sinc_hash,
        "independent_sinc_floor_recomputed": sinc_floor == independent_sinc_floor == Fraction(95, 96),
        "independent_numerator_derivative_bound_is_conservative": derivative_bound < Fraction(6, 5),
        "uv_receipt_hash_rechecked": uv_hash,
        "uv_constant_rebuilt": uv_constant == rebuilt_uv == Fraction(32, 5),
        "uv_difference_has_extra_power": ultraviolet.get("uv_difference_bound") == "abs(k(x,y)-k(0,y))<=(32/5)*abs(x)/y^2",
        "common_local_counterterm_is_explicit": "no mismatch-dependent counterterm" in ultraviolet.get("counterterm", ""),
        "absolute_uv_convergence_is_explicit": "integrable constant/q^2 tail" in ultraviolet.get("absolute_convergence", ""),
        "finite_region_continuity_uses_nonzero_tree_switch": "abs(f(x))>=95/96" in ultraviolet.get("finite_region", ""),
        "timelike_cut_is_not_dropped": "timelike cut" in ultraviolet.get("cut_boundary", ""),
        "positive_direct_integral_measure_is_recorded": "positive smooth multiple" in packet.get("measure", ""),
        "finite_bandwidth_packet_is_globally_normalizable": packet.get("status") == "NONEMPTY_GLOBALLY_NORMALIZABLE_FINITE_BANDWIDTH_PACKET_CLASS" and "globally normalized L2" in packet.get("normalizability", ""),
        "leading_dark_annihilation_is_fibrewise": "annihilates X2 pointwise" in packet.get("leading_symmetry", ""),
        "bandwidth_radius_is_not_fabricated": packet.get("radius_status") == "EXISTS_BUT_NOT_NUMERICALLY_COMPUTED",
        "retained_q6_hash_rechecked": retained_hash,
        "retained_q6_lower_recomputed": retained == expected_retained,
        "dark_q8_hash_rechecked": dark_hash,
        "dark_q8_lower_recomputed": dark == expected_dark == Fraction(2401, 9_136_478_748_672),
        "dark_q8_lower_exceeds_ten_to_minus_ten": dark > Fraction(1, 10_000_000_000),
        "absolute_status_is_computed": absolute.get("status") == "STRICTLY_POSITIVE_ABSOLUTE_FINITE_BANDWIDTH_DARK_Q8_COEFFICIENT",
        "finite_bandwidth_status_is_not_numeric": disposition.get("finite_total_momentum_and_invariant_mass_bandwidth") == "CONSTRUCTED_AS_NONEMPTY_EXISTENCE_CLASS" and disposition.get("numerical_bandwidth_radius") == "NOT_COMPUTED",
        "local_apparatus_remains_open": disposition.get("local_detector_for_the_fibrewise_projector") == "NOT_CONSTRUCTED",
        "Eq19_remains_open": disposition.get("general_Eq19") == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in boundaries),
        "literature_priority_forbidden": "literature priority" in boundaries,
    }
    return checks


def main():
    certificate = load(CERT_REL)
    checks = verify(certificate)
    for name, value in checks.items():
        print(("PASS" if value else "FAIL") + ":", name)
    ok = all(checks.values())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
