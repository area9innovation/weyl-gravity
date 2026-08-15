#!/usr/bin/env python3
"""Import the shifted cubic census and serialize the exact vv BV cotangent lift."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
CANDIDATE = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.md"
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


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
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    return [row[size:] for row in work]


def pairing_blocks(pairing: dict[str, Any]) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    jf = [[Fraction(0) for _ in range(10)] for _ in range(10)]
    jv = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for entry in pairing["pairing_serialization"]["entries"]:
        left, right, coefficient = entry["left_index"], entry["right_index"], Fraction(entry["coefficient"])
        if 34 <= left < 44 and 48 <= right < 58:
            jf[left - 34][right - 48] = coefficient
        if 44 <= left < 48 and 58 <= right < 62:
            jv[left - 44][right - 58] = coefficient
    return jf, jv


def second_frechet() -> list[list[list[Fraction]]]:
    table = [[[Fraction(0) for _ in range(4)] for _ in range(4)] for _ in range(10)]
    for output, (mu, nu) in enumerate(COORDS):
        for a in range(4):
            for b in range(4):
                table[output][a][b] = Fraction(int(mu == a and nu == b) + int(mu == b and nu == a) - int(mu == nu and a == b) * SIGNS[mu] * SIGNS[a])
    return table


def cotangent_table(jf: list[list[Fraction]], jv: list[list[Fraction]], rows: dict[str, int]) -> list[dict[str, Any]]:
    jv_inverse = inverse(jv)
    d2 = second_frechet()
    entries: list[dict[str, Any]] = []
    for output in range(4):
        for vector_input in range(4):
            for fstar_input, coord in enumerate(COORDS):
                coefficient = sum((jv_inverse[output][a] * d2[frow][a][vector_input] * jf[frow][fstar_input] for a in range(4) for frow in range(10)), Fraction(0))
                if coefficient:
                    entries.append({
                        "output_row": f"v_star_{output}",
                        "output_index": rows[f"v_star_{output}"],
                        "v_input_row": f"v_{vector_input}",
                        "v_input_index": rows[f"v_{vector_input}"],
                        "f_hat_star_input_row": f"f_hat_star_{coord[0]}{coord[1]}",
                        "f_hat_star_input_index": rows[f"f_hat_star_{coord[0]}{coord[1]}"],
                        "coefficient": str(coefficient),
                    })
    return entries


def canonical_defects(jf: list[list[Fraction]], jv: list[list[Fraction]], cotangent: list[dict[str, Any]]) -> list[dict[str, Any]]:
    d2 = second_frechet()
    slices: list[dict[str, Any]] = []
    for vector_input in range(4):
        c = [[Fraction(0) for _ in range(10)] for _ in range(4)]
        for entry in cotangent:
            if entry["v_input_row"] == f"v_{vector_input}":
                c[entry["output_index"] - 58][entry["f_hat_star_input_index"] - 48] = Fraction(entry["coefficient"])
        defect = [[sum((jv[a][r] * c[r][s] for r in range(4)), Fraction(0)) - sum((d2[o][a][vector_input] * jf[o][s] for o in range(10)), Fraction(0)) for s in range(10)] for a in range(4)]
        nonzero = sum(int(value) for row in defect for value in row)
        slices.append({"v_input_row": f"v_{vector_input}", "matrix_shape": [4, 10], "nonzero_canonicality_defects": nonzero, "defect_sha256": digest([[str(value) for value in row] for row in defect])})
    return slices


def build() -> dict[str, Any]:
    classical, pairing, candidate, predecessor = (json.loads(path.read_text()) for path in (CLASSICAL, PAIRING, CANDIDATE, PREDECESSOR))
    if classical.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1":
        raise ValueError("classical cubic inventory drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("component pairing drift")
    if candidate.get("result_id") != "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1":
        raise ValueError("candidate q2 drift")
    if predecessor.get("result_id") != "STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1":
        raise ValueError("quadratic channel predecessor drift")

    basis = pairing["component_basis"]["rows"]
    rows = {row["row_id"]: row["index"] for row in basis}
    if len(rows) != 386:
        raise ValueError("386-row basis drift")
    jf, jv = pairing_blocks(pairing)
    cotangent = cotangent_table(jf, jv, rows)
    slices = canonical_defects(jf, jv, cotangent)
    if len(cotangent) != 16 or any(item["nonzero_canonicality_defects"] for item in slices):
        raise AssertionError("vv cotangent-lift canonicality drift")

    field_entries = []
    for entry in classical["quadratic_vv_field_map"]["entries"]:
        item = dict(entry)
        item["output_index"] = rows[item["output_row"]]
        item["v_left_index"] = rows[item["v_left_row"]]
        item["v_right_index"] = rows[item["v_right_row"]]
        field_entries.append(item)
    lift = {
        "carrier_rows": 386,
        "linear_identity_rows": 386,
        "quadratic_active_output_rows": 14,
        "quadratic_zero_output_rows": 372,
        "active_output_blocks": ["AUX_F_HAT", "AUX_V_STAR"],
        "field_map_formula": "f_hat'=f_hat+F_(2)(v), F_(2)(v)=v tensor v-(1/2)g v^2",
        "cotangent_formula": "v_star_old=v_star_new+J_v^-1 (D_v F_(2))^T J_f f_hat_star_new",
        "field_map_nonzero_component_coefficients": len(field_entries),
        "cotangent_partner_nonzero_component_coefficients": len(cotangent),
        "field_map_entries": field_entries,
        "cotangent_partner_entries": cotangent,
        "canonicality_slices": slices,
        "canonicality_defects": sum(item["nonzero_canonicality_defects"] for item in slices),
        "finite_order_local": True,
        "differential_order": 0,
        "uses_green_operator": False,
        "uses_choice_principle": False,
    }
    families = []
    for family in classical["required_cubic_family_inventory"]:
        item = dict(family)
        if item["family_id"] == "TYPE_II_F_HAT_STAR_V_V":
            item["status"] = "FIELD_AND_COTANGENT_COMPONENT_COEFFICIENTS_SERIALIZED"
            item["receiver_evidence"] = "STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1"
        families.append(item)
    completeness = {
        "known_required_cubic_block_families_enumerated": 7,
        "component_coefficient_complete_families": 2,
        "component_coefficient_open_families": 5,
        "vv_BV_cotangent_lift_component_complete": True,
        "hh_hv_BV_cotangent_lift_component_complete": False,
        "diffeomorphism_BV_representation_component_complete": False,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "full_386_quadratic_BV_cotangent_lift_serialized": False,
        "full_source_q2_q3_pullback_replayed": False,
    }
    comparison = {
        "previous_f_hat_v_v_channel_residual": predecessor["channel_pullback_replay"]["transformed_source_minus_candidate_residual"],
        "shifted_mass_h_f_hat_f_hat_source_nonzero_coefficients": 72,
        "trivial_candidate_h_f_hat_f_hat_nonzero_coefficients": 0,
        "new_exact_source_candidate_component_defect_count": 72,
        "interpretation": "The vv nonlinear shift closes the old channel but does not make the metric-dependent auxiliary mass interaction-inert.",
        "further_metric_dependent_canonical_or_L_infinity_normalization_may_exist": True,
        "full_nonlinear_equivalence_obstructed": False,
    }
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-shifted-auxiliary-cubic-inventory-v1",
        "result_id": "STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1",
        "result_kind": "INDEPENDENT_386_ROW_CUBIC_FAMILY_IMPORT_AND_SCOPED_BV_COTANGENT_LIFT",
        "result_state": "SEVEN_REQUIRED_FAMILIES_ENUMERATED_HFF_AND_VV_COMPONENTS_EXACT_VV_BV_LIFT_CANONICAL_FULL_LIFT_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative auxiliary formulation", "background": "Minkowski normal frame at zero vector", "carrier_rows": 386, "coefficient_field": "Q", "claim_scope": "known required cubic-family census, exact h-f_hat-f_hat import, and componentwise vv field/cotangent sector"},
        "vv_BV_cotangent_lift": lift,
        "required_cubic_family_inventory": families,
        "inventory_completeness": completeness,
        "candidate_comparison": comparison,
        "claim_flags": {"KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED": True, "SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_IMPORTED": True, "VV_FIELD_MAP_COMPONENTS_IMPORTED": True, "VV_COTANGENT_PARTNER_COMPONENTS_SERIALIZED": True, "VV_BV_COTANGENT_LIFT_CANONICAL": True, "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False, "FULL_386_BV_COTANGENT_LIFT_SERIALIZED": False, "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False, "FULL_SOURCE_Q3_PULLBACK_REPLAYED": False, "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False, "FULL_NONLINEAR_EQUIVALENCE_OBSTRUCTED": False, "CLASSICAL_IMPORT_GATE_PASSED": False, "CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False},
        "does_not_establish": ["the hh or hv component sectors of the nonlinear field/cotangent map", "component tables for the Diff auxiliary BV representation", "absence of further nonlinear Weyl/boost ghost-antifield families", "the full source q2/q3 pullback or cyclic L-infinity equivalence", "Gate A, causal lambda-squared closure, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer"],
        "canonical_hashes": {"vv_BV_cotangent_lift_sha256": digest(lift), "required_cubic_family_inventory_sha256": digest(families), "inventory_completeness_sha256": digest(completeness), "candidate_comparison_sha256": digest(comparison)},
        "provenance": {"inputs": [
            {"path": str(CLASSICAL.relative_to(ROOT)), "result_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative shifted cubic coefficients and family audit"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "exact 386-row basis and odd pairing"},
            {"path": str(CANDIDATE.relative_to(ROOT)), "result_id": candidate["result_id"], "sha256": sha(CANDIDATE), "role": "interaction-inert trivial-stabilization comparison"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "closed predecessor vv channel"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Derive and serialize D_g^2(A_g^-1 G^b) and D_g D_b(A_g^-1 G^b), their h-star/v-star cotangent partners, and the three Diff auxiliary representation vertices; then audit the full nonlinear Weyl/boost ghost manifest before assembling a complete 386-row lift.",
    }
    return value


def render(value: dict[str, Any]) -> str:
    lift, comparison = value["vv_BV_cotangent_lift"], value["candidate_comparison"]
    return f"""# Strict 386-row shifted-auxiliary cubic inventory v1

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

The receiver embeds the exact vv nonlinear field map in the published 386-row
basis.  It serializes **{lift['field_map_nonzero_component_coefficients']}**
field-map and **{lift['cotangent_partner_nonzero_component_coefficients']}**
cotangent-partner coefficients.  All four `J_v C_b=(D_bF)^T J_f`
canonicality slices have zero defect.  The quadratic correction acts on 14
output rows and is zero on the other 372.

The imported shifted mass has **72** nonzero `h-f_hat-f_hat` coefficients,
whereas the interaction-inert candidate has {comparison['trivial_candidate_h_f_hat_f_hat_nonzero_coefficients']}.
Thus the vv shift closes the old `-1+1=0` channel but does not by itself
identify the source with the trivial stabilization.

Seven currently required cubic families are enumerated.  Two are now
component-complete; hh, hv and three Diff BV representation families remain
open.  The source manifest is not yet exhaustive for nonlinear Weyl/boost
ghost-antifield channels, so neither a full 386-row lift nor full equivalence is
claimed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_auxiliary_cubic_inventory.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_auxiliary_cubic_inventory.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_auxiliary_cubic_inventory.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_auxiliary_cubic_inventory
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
        print("STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
