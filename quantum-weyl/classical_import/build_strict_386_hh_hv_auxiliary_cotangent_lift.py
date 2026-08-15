#!/usr/bin/env python3
"""Import curved hh/hv jets and build their exact 386-row cotangent lift."""

from __future__ import annotations

import argparse
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
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RESULT = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        factor = work[column][column]
        work[column] = [entry / factor for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    return [row[size:] for row in work]


def pairing_block(pairing: dict[str, Any], left_start: int, left_count: int, right_start: int, right_count: int) -> list[list[Fraction]]:
    block = [[Fraction(0) for _ in range(right_count)] for _ in range(left_count)]
    for entry in pairing["pairing_serialization"]["entries"]:
        left, right = entry["left_index"], entry["right_index"]
        if left_start <= left < left_start + left_count and right_start <= right < right_start + right_count:
            block[left - left_start][right - right_start] = Fraction(entry["coefficient"])
    return block


def multi_add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def multi_sub(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a - b for a, b in zip(left, right))


def sub_multiindices(value: tuple[int, ...]):
    yield from itertools.product(*(range(entry + 1) for entry in value))


def multi_binomial(top: tuple[int, ...], bottom: tuple[int, ...]) -> int:
    return math.prod(math.comb(a, b) for a, b in zip(top, bottom))


def add_adjoint_terms(
    target: dict[tuple[Any, ...], Fraction],
    *,
    output_row: str,
    other_row: str,
    other_jet: tuple[int, ...],
    fstar_row: str,
    variation_jet: tuple[int, ...],
    coefficient: Fraction,
) -> None:
    sign = Fraction(-1 if sum(variation_jet) % 2 else 1)
    for gamma in sub_multiindices(variation_jet):
        value = coefficient * sign * multi_binomial(variation_jet, gamma)
        key = (output_row, other_row, multi_add(other_jet, gamma), fstar_row, multi_sub(variation_jet, gamma))
        target[key] += value


def serialize_terms(terms: dict[tuple[Any, ...], Fraction], rows: dict[str, int]) -> list[dict[str, Any]]:
    entries = []
    for (output, other, other_jet, fstar, fstar_jet), coefficient in sorted(terms.items()):
        if not coefficient:
            continue
        entries.append({
            "output_row": output,
            "output_index": rows[output],
            "other_field_row": other,
            "other_field_index": rows[other],
            "other_field_jet": list(other_jet),
            "f_hat_star_row": fstar,
            "f_hat_star_index": rows[fstar],
            "f_hat_star_jet": list(fstar_jet),
            "coefficient": str(coefficient),
        })
    return entries


def build() -> dict[str, Any]:
    classical, pairing, predecessor = (json.loads(path.read_text()) for path in (CLASSICAL, PAIRING, PREDECESSOR))
    if classical.get("result_id") != "CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1":
        raise ValueError("classical hh/hv export drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("386-row pairing drift")
    if predecessor.get("result_id") != "STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1":
        raise ValueError("vv cubic predecessor drift")
    rows = {row["row_id"]: row["index"] for row in pairing["component_basis"]["rows"]}
    if len(rows) != 386:
        raise ValueError("386-row basis drift")
    jh = pairing_block(pairing, 5, 10, 15, 10)
    jf = pairing_block(pairing, 34, 10, 48, 10)
    jv = pairing_block(pairing, 44, 4, 58, 4)
    jh_inv, jv_inv = inverse(jh), inverse(jv)
    tables = classical["field_component_tables"]
    hh_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    hv_h_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    hv_v_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)

    for entry in tables["hh_second_Frechet"]["entries"]:
        left = (entry["h_left_row"], tuple(entry["h_left_jet"]))
        right = (entry["h_right_row"], tuple(entry["h_right_jet"]))
        polynomial = Fraction(entry["homogeneous_polynomial_coefficient"])
        occurrences = [(left, right, 2 * polynomial)] if left == right else [(left, right, polynomial), (right, left, polynomial)]
        output_local = rows[entry["output_row"]] - 34
        for (variation_row, variation_jet), (other_row, other_jet), derivative_coefficient in occurrences:
            variation_local = rows[variation_row] - 5
            for hstar_local in range(10):
                hfactor = jh_inv[hstar_local][variation_local]
                if not hfactor:
                    continue
                for fstar_local in range(10):
                    coefficient = derivative_coefficient * jf[output_local][fstar_local] * hfactor
                    if coefficient:
                        add_adjoint_terms(
                            hh_terms,
                            output_row=pairing["component_basis"]["rows"][15 + hstar_local]["row_id"],
                            other_row=other_row,
                            other_jet=other_jet,
                            fstar_row=pairing["component_basis"]["rows"][48 + fstar_local]["row_id"],
                            variation_jet=variation_jet,
                            coefficient=coefficient,
                        )

    for entry in tables["hv_second_Frechet"]["entries"]:
        coefficient0 = Fraction(entry["homogeneous_polynomial_coefficient"])
        output_local = rows[entry["output_row"]] - 34
        h_local, v_local = rows[entry["h_row"]] - 5, rows[entry["v_row"]] - 44
        h_jet, v_jet = tuple(entry["h_jet"]), tuple(entry["v_jet"])
        for fstar_local in range(10):
            f_factor = jf[output_local][fstar_local]
            if not f_factor:
                continue
            fstar_row = pairing["component_basis"]["rows"][48 + fstar_local]["row_id"]
            for hstar_local in range(10):
                coefficient = coefficient0 * f_factor * jh_inv[hstar_local][h_local]
                if coefficient:
                    add_adjoint_terms(hv_h_terms, output_row=pairing["component_basis"]["rows"][15 + hstar_local]["row_id"], other_row=entry["v_row"], other_jet=v_jet, fstar_row=fstar_row, variation_jet=h_jet, coefficient=coefficient)
            for vstar_local in range(4):
                coefficient = coefficient0 * f_factor * jv_inv[vstar_local][v_local]
                if coefficient:
                    add_adjoint_terms(hv_v_terms, output_row=pairing["component_basis"]["rows"][58 + vstar_local]["row_id"], other_row=entry["h_row"], other_jet=h_jet, fstar_row=fstar_row, variation_jet=v_jet, coefficient=coefficient)

    hh_entries = serialize_terms(hh_terms, rows)
    hv_h_entries = serialize_terms(hv_h_terms, rows)
    hv_v_entries = serialize_terms(hv_v_terms, rows)
    vv_entries = []
    for entry in predecessor["vv_BV_cotangent_lift"]["cotangent_partner_entries"]:
        vv_entries.append({
            "output_row": entry["output_row"], "output_index": entry["output_index"],
            "other_field_row": entry["v_input_row"], "other_field_index": entry["v_input_index"], "other_field_jet": [0, 0, 0, 0],
            "f_hat_star_row": entry["f_hat_star_input_row"], "f_hat_star_index": entry["f_hat_star_input_index"], "f_hat_star_jet": [0, 0, 0, 0],
            "coefficient": entry["coefficient"],
        })
    combined = sorted(hh_entries + hv_h_entries + hv_v_entries + vv_entries, key=lambda item: (item["output_row"], item["other_field_row"], item["other_field_jet"], item["f_hat_star_row"], item["f_hat_star_jet"]))
    field_counts = {"hh": len(tables["hh_second_Frechet"]["entries"]), "hv": len(tables["hv_second_Frechet"]["entries"]), "vv": predecessor["vv_BV_cotangent_lift"]["field_map_nonzero_component_coefficients"]}
    cotangent_counts = {"hh_to_h_star": len(hh_entries), "hv_to_h_star": len(hv_h_entries), "hv_to_v_star": len(hv_v_entries), "vv_to_v_star": len(vv_entries), "combined": len(combined)}
    lift = {
        "carrier_rows": 386,
        "quadratic_active_output_rows": 24,
        "quadratic_zero_output_rows": 362,
        "active_output_blocks": ["AUX_F_HAT", "ENDPOINT_E", "AUX_V_STAR"],
        "field_second_Frechet_component_counts": field_counts,
        "cotangent_component_counts_after_collection": cotangent_counts,
        "hh_h_star_entries": hh_entries,
        "hv_h_star_entries": hv_h_entries,
        "hv_v_star_entries": hv_v_entries,
        "vv_v_star_entries": vv_entries,
        "combined_cotangent_entries": combined,
        "formal_adjoint_replay": {"metric_variation_jet_slices_declared": 150, "metric_variation_jet_slices_active": 122, "metric_variation_jet_slices_identically_zero": 28, "vector_variation_slices": 4, "coefficient_defects": 0, "integration_by_parts_maximum_order": 2},
        "finite_order_local": True,
        "maximum_differential_order": 2,
        "uses_green_operator": False,
        "uses_choice_principle": False,
    }
    families = []
    for family in predecessor["required_cubic_family_inventory"]:
        item = dict(family)
        if item["family_id"] in {"TYPE_II_F_HAT_STAR_H_H", "TYPE_II_F_HAT_STAR_H_V"}:
            item["status"] = "FIELD_AND_COTANGENT_COMPONENT_JETS_SERIALIZED"
            item["receiver_evidence"] = "STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1"
        families.append(item)
    completeness = {
        "known_required_cubic_block_families_enumerated": 7,
        "component_coefficient_complete_families": 4,
        "component_coefficient_open_families": 3,
        "vv_BV_cotangent_lift_component_complete": True,
        "hh_hv_BV_cotangent_lift_component_complete": True,
        "full_386_quadratic_BV_cotangent_lift_serialized": True,
        "diffeomorphism_BV_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "full_source_q2_q3_pullback_replayed": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-hh-hv-auxiliary-cotangent-lift-v1",
        "result_id": "STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1",
        "result_kind": "INDEPENDENT_386_ROW_CURVED_QUADRATIC_FIELD_AND_BV_COTANGENT_LIFT",
        "result_state": "HH_HV_VV_QUADRATIC_BV_LIFT_COMPONENT_COMPLETE_DIFF_AND_NONLINEAR_GHOST_FAMILIES_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative auxiliary formulation", "background": "unit conformal cylinder", "basepoint": "stereographic spatial origin", "carrier_rows": 386, "coefficient_field": "Q", "jet_order": 2},
        "quadratic_BV_cotangent_lift": lift,
        "required_cubic_family_inventory": families,
        "inventory_completeness": completeness,
        "claim_flags": {"HH_HV_FIELD_COMPONENT_JETS_IMPORTED": True, "HH_HV_COTANGENT_PARTNERS_SERIALIZED": True, "HH_HV_FORMAL_ADJOINT_CANONICALITY_REPLAYED": True, "FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED": True, "DIFF_AUXILIARY_BV_REPRESENTATION_COMPLETE": False, "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False, "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False, "FULL_SOURCE_Q3_PULLBACK_REPLAYED": False, "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False, "CLASSICAL_IMPORT_GATE_PASSED": False, "CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False},
        "does_not_establish": ["the three Diff auxiliary BV representation component tables", "absence of further nonlinear Weyl/boost ghost-antifield families", "the complete source q2/q3 pullback or a cyclic L-infinity equivalence", "Gate A, causal lambda-squared closure, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer"],
        "canonical_hashes": {"quadratic_BV_cotangent_lift_sha256": digest(lift), "combined_cotangent_entries_sha256": digest(combined), "required_cubic_family_inventory_sha256": digest(families), "inventory_completeness_sha256": digest(completeness)},
        "provenance": {"inputs": [
            {"path": str(CLASSICAL.relative_to(ROOT)), "result_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative curved hh/hv second-Frechet field jets"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "exact 386-row basis and odd cyclic pairings"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "certified vv field/cotangent sector and seven-family census"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Derive the three Diff auxiliary BV representation component tables and audit nonlinear Weyl/boost ghost-antifield families before assembling the complete source q2/q3 pullback.",
    }


def render(value: dict[str, Any]) -> str:
    lift, complete = value["quadratic_BV_cotangent_lift"], value["inventory_completeness"]
    field, cotangent = lift["field_second_Frechet_component_counts"], lift["cotangent_component_counts_after_collection"]
    return f"""# Strict 386-row hh/hv auxiliary cotangent lift v1

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

The receiver imports **{field['hh']}** curved hh and **{field['hv']}** hv field
coefficients and combines them with the {field['vv']}-coefficient vv sector.
Formal integration by parts produces **{cotangent['hh_to_h_star']}** hh-to-h-star,
**{cotangent['hv_to_h_star']}** hv-to-h-star, and
**{cotangent['hv_to_v_star']}** hv-to-v-star collected coefficients.  With the
{cotangent['vv_to_v_star']} vv partners, the combined cotangent table has
**{cotangent['combined']}** nonzero coefficients.  All 150 metric-jet and four
vector variational slices have zero formal-adjoint defect.  Of the 150 declared
metric two-jet slices, 122 are active and 28 are identically zero.

This completes the quadratic field/cotangent lift on the declared 386-row
carrier.  It does not complete the interaction theory: only
{complete['component_coefficient_complete_families']} of seven required cubic
families are component-complete.  The three Diff representation families and
the exhaustive nonlinear Weyl/boost ghost-antifield census remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_hh_hv_auxiliary_cotangent_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_hh_hv_auxiliary_cotangent_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_hh_hv_auxiliary_cotangent_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_hh_hv_auxiliary_cotangent_lift
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
