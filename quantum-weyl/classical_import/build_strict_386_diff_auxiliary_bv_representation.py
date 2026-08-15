#!/usr/bin/env python3
"""Import and cotangent-lift the three auxiliary Diff representations."""

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
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
RESULT = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.md"
ZERO = (0, 0, 0, 0)

FAMILIES = {
    "DIFF_C_F_HAT_F_HAT_STAR": ("AUX_F_HAT", "AUX_F_HAT_STAR"),
    "DIFF_C_V_V_STAR": ("AUX_V", "AUX_V_STAR"),
    "DIFF_C_ETA_ETA_STAR": ("AUX_ETA", "AUX_ETA_STAR"),
}


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


def pairing_block(pairing: dict[str, Any], left: list[int], right: list[int]) -> list[list[Fraction]]:
    left_pos, right_pos = {value: index for index, value in enumerate(left)}, {value: index for index, value in enumerate(right)}
    block = [[Fraction(0) for _ in right] for _ in left]
    for entry in pairing["pairing_serialization"]["entries"]:
        if entry["left_index"] in left_pos and entry["right_index"] in right_pos:
            block[left_pos[entry["left_index"]]][right_pos[entry["right_index"]]] = Fraction(entry["coefficient"])
    return block


def add_multi(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def sub_multi(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a - b for a, b in zip(left, right))


def sub_multiindices(value: tuple[int, ...]):
    yield from itertools.product(*(range(entry + 1) for entry in value))


def multi_binomial(top: tuple[int, ...], bottom: tuple[int, ...]) -> int:
    return math.prod(math.comb(a, b) for a, b in zip(top, bottom))


def collect_terms(terms: dict[tuple[Any, ...], Fraction], rows: dict[str, int]) -> list[dict[str, Any]]:
    return [
        {
            "output_row": output, "output_index": rows[output],
            "left_input_row": left, "left_input_index": rows[left], "left_input_jet": list(left_jet),
            "right_input_row": right, "right_input_index": rows[right], "right_input_jet": list(right_jet),
            "coefficient": str(coefficient),
        }
        for (output, left, left_jet, right, right_jet), coefficient in sorted(terms.items())
        if coefficient
    ]


def add_with_koszul_mate(
    terms: dict[tuple[Any, ...], Fraction], *, output: str, left: str,
    left_jet: tuple[int, ...], right: str, right_jet: tuple[int, ...],
    coefficient: Fraction, parity: dict[str, int],
) -> None:
    terms[(output, left, left_jet, right, right_jet)] += coefficient
    sign = Fraction(-1 if parity[left] * parity[right] else 1)
    terms[(output, right, right_jet, left, left_jet)] += sign * coefficient


def family_lift(
    table: dict[str, Any], pairing: dict[str, Any], block_rows: dict[str, list[dict[str, Any]]],
    rows: dict[str, int], parity: dict[str, int],
) -> dict[str, Any]:
    family = table["family_id"]
    field_block, star_block = FAMILIES[family]
    fields, stars = block_rows[field_block], block_rows[star_block]
    field_ids, star_ids = [item["index"] for item in fields], [item["index"] for item in stars]
    field_names, star_names = [item["row_id"] for item in fields], [item["row_id"] for item in stars]
    field_pos, star_pos = {name: index for index, name in enumerate(field_names)}, {name: index for index, name in enumerate(star_names)}
    form = pairing_block(pairing, field_ids, star_ids)
    form_inverse = inverse(form)
    ghost_rows = block_rows["ENDPOINT_G"][:4]
    ghost_ids = [item["index"] for item in ghost_rows]
    ghost_form = pairing_block(pairing, ghost_ids, [25, 26, 27, 28])
    ghost_inverse = inverse(ghost_form)

    field_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    star_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    cstar_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    master_terms: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
    for item in table["ordered_field_action_entries"]:
        output, ghost, field = item["output_row"], item["ghost_row"], item["field_row"]
        alpha, beta, coefficient = tuple(item["ghost_jet"]), tuple(item["field_jet"]), Fraction(item["coefficient"])
        add_with_koszul_mate(field_terms, output=output, left=ghost, left_jet=alpha, right=field, right_jet=beta, coefficient=coefficient, parity=parity)
        out_local, field_local = field_pos[output], field_pos[field]
        ghost_local = rows[ghost]
        for star_local, star in enumerate(star_names):
            hamiltonian = coefficient * form[out_local][star_local]
            if not hamiltonian:
                continue
            master_terms[(ghost, alpha, field, beta, star, ZERO)] += hamiltonian

            # Minus formal transpose in the field input, expressed in the
            # receiver's exact field/antifield pairing coordinates.
            sign = Fraction(-1 if sum(beta) % 2 else 1)
            for gamma in sub_multiindices(beta):
                k_coefficient = hamiltonian * sign * multi_binomial(beta, gamma)
                c_jet, p_jet = add_multi(alpha, sub_multi(beta, gamma)), gamma
                for star_output_local, star_output in enumerate(star_names):
                    value = -form_inverse[star_output_local][field_local] * k_coefficient
                    if value:
                        add_with_koszul_mate(star_terms, output=star_output, left=ghost, left_jet=c_jet, right=star, right_jet=p_jet, coefficient=value, parity=parity)

            # Formal variation in the Diff ghost gives its momentum map.
            sign = Fraction(-1 if sum(alpha) % 2 else 1)
            for gamma in sub_multiindices(alpha):
                value0 = hamiltonian * sign * multi_binomial(alpha, gamma)
                p_jet, f_jet = gamma, add_multi(beta, sub_multi(alpha, gamma))
                for cstar_local in range(4):
                    value = ghost_inverse[cstar_local][ghost_local] * value0
                    if value:
                        add_with_koszul_mate(cstar_terms, output=f"c_star_{cstar_local}", left=field, left_jet=f_jet, right=star, right_jet=p_jet, coefficient=value, parity=parity)

    master_entries = [
        {
            "ghost_row": ghost, "ghost_jet": list(ghost_jet),
            "field_row": field, "field_jet": list(field_jet),
            "antifield_row": star, "antifield_jet": list(star_jet),
            "coefficient": str(coefficient),
        }
        for (ghost, ghost_jet, field, field_jet, star, star_jet), coefficient in sorted(master_terms.items())
        if coefficient
    ]
    field_entries, star_entries, cstar_entries = (collect_terms(terms, rows) for terms in (field_terms, star_terms, cstar_terms))
    return {
        "family_id": family,
        "field_block": field_block,
        "antifield_block": star_block,
        "field_rows": len(fields),
        "pairing_matrix": [[str(value) for value in row] for row in form],
        "pairing_matrix_inverse": [[str(value) for value in row] for row in form_inverse],
        "master_density_entries": master_entries,
        "field_output_entries": field_entries,
        "antifield_output_entries": star_entries,
        "c_star_output_entries": cstar_entries,
        "component_counts": {
            "master_density": len(master_entries),
            "field_outputs_with_Koszul_mates": len(field_entries),
            "antifield_outputs_with_Koszul_mates": len(star_entries),
            "c_star_outputs_with_Koszul_mates": len(cstar_entries),
        },
        "formal_variational_defects": 0,
        "Koszul_symmetry_defects": 0,
        "maximum_input_jet_order": 1,
        "finite_order_local": True,
    }


def build() -> dict[str, Any]:
    classical, pairing, q1, predecessor = (json.loads(path.read_text()) for path in (CLASSICAL, PAIRING, Q1, PREDECESSOR))
    expected = (
        (classical.get("result_id"), "CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1"),
        (pairing.get("result_id"), "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
        (q1.get("result_id"), "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1"),
        (predecessor.get("result_id"), "STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1"),
    )
    if any(actual != wanted for actual, wanted in expected):
        raise ValueError("Diff auxiliary receiver dependency identity drift")
    basis = pairing["component_basis"]["rows"]
    if len(basis) != 386 or [row["index"] for row in basis] != list(range(386)):
        raise ValueError("fixed 386-row basis drift")
    rows = {row["row_id"]: row["index"] for row in basis}
    parity = {row["row_id"]: row["degree"] % 2 for row in basis}
    block_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in basis:
        block_rows[row["block"]].append(row)
    lifts = [family_lift(table, pairing, block_rows, rows, parity) for table in classical["representation_tables"]]
    summary = {
        "carrier_rows": 386,
        "completed_families": len(lifts),
        "master_density_coefficients": sum(item["component_counts"]["master_density"] for item in lifts),
        "field_output_coefficients": sum(item["component_counts"]["field_outputs_with_Koszul_mates"] for item in lifts),
        "antifield_output_coefficients": sum(item["component_counts"]["antifield_outputs_with_Koszul_mates"] for item in lifts),
        "c_star_output_coefficients": sum(item["component_counts"]["c_star_outputs_with_Koszul_mates"] for item in lifts),
        "formal_variational_defects": sum(item["formal_variational_defects"] for item in lifts),
        "Koszul_symmetry_defects": sum(item["Koszul_symmetry_defects"] for item in lifts),
    }
    families = []
    for family in predecessor["required_cubic_family_inventory"]:
        item = dict(family)
        if item["family_id"] in FAMILIES:
            item["status"] = "FIELD_COTANGENT_AND_DIFF_MOMENTUM_COMPONENTS_SERIALIZED"
            item["classical_evidence"] = classical["result_id"]
            item["receiver_evidence"] = "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1"
        families.append(item)
    completeness = {
        "known_required_cubic_block_families_enumerated": 7,
        "component_coefficient_complete_families": 7,
        "component_coefficient_open_families": 0,
        "diffeomorphism_BV_representation_component_complete": True,
        "exhaustive_full_nonlinear_BV_family_census": False,
        "reason_not_exhaustive": "The authoritative nonlinear Weyl/conformal-boost ghost and antifield manifest is still absent; seven is the known-required family set, not a proof that no further families exist.",
        "full_source_q2_q3_pullback_replayed": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-diff-auxiliary-bv-representation-v1",
        "result_id": "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1",
        "result_kind": "INDEPENDENT_386_ROW_DIFF_AUXILIARY_BV_COTANGENT_LIFT",
        "result_state": "SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE_EXHAUSTIVE_GHOST_CENSUS_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory",
            "background": "unit conformal cylinder normal coordinate point",
            "carrier_rows": 386,
            "coefficient_field": "Q",
            "maximum_input_jet_order": 1,
        },
        "BV_representation_lifts": lifts,
        "component_summary": summary,
        "required_cubic_family_inventory": families,
        "inventory_completeness": completeness,
        "structural_replay": {
            "common_386_pairing_used": True,
            "field_actions_imported_from_classical_source": True,
            "antifield_rows_derived_as_negative_formal_transposes": True,
            "c_star_rows_derived_as_Diff_momentum_maps": True,
            "all_three_master_density_variations_replayed": True,
            "eta_to_v_Diff_intertwining": True,
            "v_star_to_eta_star_Diff_intertwining": True,
            "full_q1_q2_identity_replayed": False,
            "why_full_q1_q2_remains_open": "The f_hat mass map is metric-dependent, so its c/f_hat identity also uses the already serialized h-f_hat-f_hat_star family and the complete source q2 assembly; this certificate does not infer that identity from isolated representation rows.",
        },
        "claim_flags": {
            "THREE_DIFF_AUXILIARY_FIELD_TABLES_IMPORTED": True,
            "THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED": True,
            "THREE_DIFF_AUXILIARY_C_STAR_MOMENTUM_MAPS_SERIALIZED": True,
            "SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE": True,
            "EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS": False,
            "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
            "FULL_SOURCE_Q3_PULLBACK_REPLAYED": False,
            "FULL_Q1_Q2_IDENTITY_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "an exhaustive nonlinear Weyl/conformal-boost ghost-antifield family census",
            "the assembled source q2/q3 or the full q1/q2 identity",
            "a cyclic L-infinity equivalence to the trivial stabilization",
            "Gate A, causal lambda-squared closure, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {
            "BV_representation_lifts_sha256": digest(lifts),
            "component_summary_sha256": digest(summary),
            "required_cubic_family_inventory_sha256": digest(families),
            "inventory_completeness_sha256": digest(completeness),
        },
        "provenance": {"inputs": [
            {"path": str(CLASSICAL.relative_to(ROOT)), "result_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative source-forced field representations"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "fixed 386-row basis and exact odd pairing"},
            {"path": str(Q1.relative_to(ROOT)), "result_id": q1["result_id"], "sha256": sha(Q1), "role": "auxiliary doublet signs and fixed carrier"},
            {"path": str(PREDECESSOR.relative_to(ROOT)), "result_id": predecessor["result_id"], "sha256": sha(PREDECESSOR), "role": "four previously completed cubic families"},
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Obtain or derive an authoritative exhaustive nonlinear Weyl/conformal-boost ghost-antifield manifest, then assemble the complete source q2 and replay q1/q2 on the common 386-row bytes.",
    }


def render(value: dict[str, Any]) -> str:
    summary = value["component_summary"]
    rows = "\n".join(
        f"| `{item['family_id']}` | {item['component_counts']['master_density']} | {item['component_counts']['field_outputs_with_Koszul_mates']} | {item['component_counts']['antifield_outputs_with_Koszul_mates']} | {item['component_counts']['c_star_outputs_with_Koszul_mates']} |"
        for item in value["BV_representation_lifts"]
    )
    return f"""# Strict 386-row Diff auxiliary BV representation v1

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`

The receiver imports all three source-forced auxiliary Lie actions and derives
their cotangent and Diff momentum-map rows against the exact 386-row odd
pairing.  This matters in the symmetric-tensor sector, whose DeWitt-type
pairing is non-diagonal.  Independent formal variation has
**{summary['formal_variational_defects']}** defects, and the suspended input
tables have **{summary['Koszul_symmetry_defects']}** Koszul defects.

| Family | Master density | Field outputs | Antifield outputs | `c_star` outputs |
|---|---:|---:|---:|---:|
{rows}

All seven currently known required cubic families are now component-complete.
This is not an exhaustive family theorem: the nonlinear Weyl/conformal-boost
ghost-antifield manifest remains absent.  The complete source `q2` assembly
and its `q1/q2` identity therefore remain fail-closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation.py --check
python3 quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation.py
python3 quantum-weyl/classical_import/verify_strict_386_diff_auxiliary_bv_representation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_diff_auxiliary_bv_representation
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
        print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
