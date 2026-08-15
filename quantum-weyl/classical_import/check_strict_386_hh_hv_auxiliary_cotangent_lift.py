#!/usr/bin/env python3
"""Independent Euler-adjoint replay of the 386-row hh/hv cotangent lift."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def pairing_block(pairing: dict[str, Any], left_start: int, size: int, right_start: int) -> list[list[Fraction]]:
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for item in pairing["pairing_serialization"]["entries"]:
        left, right = item["left_index"], item["right_index"]
        if left_start <= left < left_start + size and right_start <= right < right_start + size:
            result[left - left_start][right - right_start] = Fraction(item["coefficient"])
    return result


def euler_expansion(variation: tuple[int, ...], other: tuple[int, ...]):
    sign = Fraction(-1 if sum(variation) % 2 else 1)
    for gamma in itertools.product(*(range(x + 1) for x in variation)):
        factor = sign * math.prod(math.comb(a, b) for a, b in zip(variation, gamma))
        yield tuple(a + b for a, b in zip(other, gamma)), tuple(a - b for a, b in zip(variation, gamma)), factor


def collect(target: dict[tuple[Any, ...], Fraction], output: str, other: str, other_jet: tuple[int, ...], fstar: str, variation_jet: tuple[int, ...], coefficient: Fraction) -> None:
    for shifted_other, shifted_fstar, factor in euler_expansion(variation_jet, other_jet):
        target[(output, other, shifted_other, fstar, shifted_fstar)] += coefficient * factor


def serialized_map(entries: list[dict[str, Any]]) -> dict[tuple[Any, ...], Fraction]:
    return {
        (item["output_row"], item["other_field_row"], tuple(item["other_field_jet"]), item["f_hat_star_row"], tuple(item["f_hat_star_jet"])): Fraction(item["coefficient"])
        for item in entries
    }


def expected_tables(classical: dict[str, Any], pairing: dict[str, Any], predecessor: dict[str, Any]):
    basis = pairing["component_basis"]["rows"]
    rows = {row["row_id"]: row["index"] for row in basis}
    jh, jf, jv = pairing_block(pairing, 5, 10, 15), pairing_block(pairing, 34, 10, 48), pairing_block(pairing, 44, 4, 58)
    if any(jh[i][j] for i in range(10) for j in range(10) if i != j) or any(jv[i][j] for i in range(4) for j in range(4) if i != j):
        raise ValueError("expected diagonal h/v pairing blocks")
    hh: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    hv_h: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    hv_v: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    tables = classical["field_component_tables"]
    active_h: set[tuple[str, tuple[int, ...]]] = set()
    for item in tables["hh_second_Frechet"]["entries"]:
        left = (item["h_left_row"], tuple(item["h_left_jet"]))
        right = (item["h_right_row"], tuple(item["h_right_jet"]))
        occurrences = [(left, right)] if left == right else [(left, right), (right, left)]
        output = rows[item["output_row"]] - 34
        coefficient0 = Fraction(item["second_Frechet_coefficient"])
        for variation, other in occurrences:
            active_h.add(variation)
            variation_local = rows[variation[0]] - 5
            hstar = f"h_star_{variation[0][2:]}"
            hfactor = Fraction(1, 1) / jh[variation_local][variation_local]
            for fstar_local in range(10):
                coefficient = coefficient0 * jf[output][fstar_local] * hfactor
                if coefficient:
                    collect(hh, hstar, other[0], other[1], basis[48 + fstar_local]["row_id"], variation[1], coefficient)
    for item in tables["hv_second_Frechet"]["entries"]:
        output = rows[item["output_row"]] - 34
        hrow, hjet, vrow, vjet = item["h_row"], tuple(item["h_jet"]), item["v_row"], tuple(item["v_jet"])
        active_h.add((hrow, hjet))
        hlocal, vlocal = rows[hrow] - 5, rows[vrow] - 44
        coefficient0 = Fraction(item["second_Frechet_coefficient"])
        for fstar_local in range(10):
            coefficient = coefficient0 * jf[output][fstar_local]
            if not coefficient:
                continue
            fstar = basis[48 + fstar_local]["row_id"]
            collect(hv_h, f"h_star_{hrow[2:]}", vrow, vjet, fstar, hjet, coefficient / jh[hlocal][hlocal])
            collect(hv_v, f"v_star_{vrow[2:]}", hrow, hjet, fstar, vjet, coefficient / jv[vlocal][vlocal])
    vv = {
        (item["output_row"], item["v_input_row"], (0, 0, 0, 0), item["f_hat_star_input_row"], (0, 0, 0, 0)): Fraction(item["coefficient"])
        for item in predecessor["vv_BV_cotangent_lift"]["cotangent_partner_entries"]
    }
    return ({key: value for key, value in hh.items() if value}, {key: value for key, value in hv_h.items() if value}, {key: value for key, value in hv_v.items() if value}, vv, active_h)


def check(value: dict[str, Any]) -> list[str]:
    classical, pairing, predecessor = (json.loads(path.read_text()) for path in (CLASSICAL, PAIRING, PREDECESSOR))
    expected_hh, expected_hv_h, expected_hv_v, expected_vv, active_h = expected_tables(classical, pairing, predecessor)
    lift = value.get("quadratic_BV_cotangent_lift", {})
    actual_hh = serialized_map(lift.get("hh_h_star_entries", []))
    actual_hv_h = serialized_map(lift.get("hv_h_star_entries", []))
    actual_hv_v = serialized_map(lift.get("hv_v_star_entries", []))
    actual_vv = serialized_map(lift.get("vv_v_star_entries", []))
    actual_combined = serialized_map(lift.get("combined_cotangent_entries", []))
    combined = dict(expected_hh | expected_hv_h | expected_hv_v | expected_vv)
    counts = lift.get("cotangent_component_counts_after_collection", {})
    replay = lift.get("formal_adjoint_replay", {})
    complete = value.get("inventory_completeness", {})
    flags = value.get("claim_flags", {})
    hashes = value.get("canonical_hashes", {})
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (CLASSICAL, PAIRING, PREDECESSOR)}
    families = value.get("required_cubic_family_inventory", [])
    ok = (
        value.get("result_id") == "STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1"
        and value.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and actual_hh == expected_hh and actual_hv_h == expected_hv_h and actual_hv_v == expected_hv_v and actual_vv == expected_vv and actual_combined == combined
        and counts == {"hh_to_h_star": len(expected_hh), "hv_to_h_star": len(expected_hv_h), "hv_to_v_star": len(expected_hv_v), "vv_to_v_star": len(expected_vv), "combined": len(combined)}
        and replay == {"metric_variation_jet_slices_declared": 150, "metric_variation_jet_slices_active": len(active_h), "metric_variation_jet_slices_identically_zero": 150 - len(active_h), "vector_variation_slices": 4, "coefficient_defects": 0, "integration_by_parts_maximum_order": 2}
        and (len(active_h), 150 - len(active_h)) == (122, 28)
        and complete.get("component_coefficient_complete_families") == 4
        and complete.get("component_coefficient_open_families") == 3
        and complete.get("hh_hv_BV_cotangent_lift_component_complete") is True
        and complete.get("full_386_quadratic_BV_cotangent_lift_serialized") is True
        and complete.get("diffeomorphism_BV_representation_component_complete") is False
        and complete.get("exhaustive_full_nonlinear_BV_family_census") is False
        and sum(item.get("status") in {"COMPONENT_COEFFICIENTS_SERIALIZED", "FIELD_AND_COTANGENT_COMPONENT_COEFFICIENTS_SERIALIZED", "FIELD_AND_COTANGENT_COMPONENT_JETS_SERIALIZED"} for item in families) == 4
        and flags.get("HH_HV_COTANGENT_PARTNERS_SERIALIZED") is True
        and flags.get("HH_HV_FORMAL_ADJOINT_CANONICALITY_REPLAYED") is True
        and flags.get("FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED") is True
        and flags.get("DIFF_AUXILIARY_BV_REPRESENTATION_COMPLETE") is False
        and flags.get("EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS") is False
        and flags.get("FULL_SOURCE_Q2_PULLBACK_REPLAYED") is False
        and flags.get("FULL_SOURCE_Q3_PULLBACK_REPLAYED") is False
        and flags.get("CLASSICAL_IMPORT_GATE_PASSED") is False
        and flags.get("HADAMARD_STATE_CONSTRUCTED") is False
        and flags.get("QME_RESTORED") is False
        and hashes.get("quadratic_BV_cotangent_lift_sha256") == digest(lift)
        and hashes.get("combined_cotangent_entries_sha256") == digest(lift.get("combined_cotangent_entries"))
        and hashes.get("required_cubic_family_inventory_sha256") == digest(families)
        and hashes.get("inventory_completeness_sha256") == digest(complete)
        and pins == expected_pins
    )
    return [] if ok else ["independent Euler-adjoint replay, counts, hashes, provenance, or fail-closed boundary mismatch"]


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1_INDEPENDENT_EULER_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["quadratic_BV_cotangent_lift"]["cotangent_component_counts_after_collection"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
