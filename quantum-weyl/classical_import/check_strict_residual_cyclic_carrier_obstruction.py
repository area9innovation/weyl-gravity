#!/usr/bin/env python3
"""Independent receiver for the M4R carrier obstruction and 940-row preflight."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
LOCAL_PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
EVEN_FORM = ROOT / "bridge/certificates/cross_energy_pairing.json"
EVEN_FORM_PRODUCER = ROOT / "symbolic/verify_conformal_cross_energy_pairing.py"
DEPENDENCIES = (M3R, DFINITE, LOCAL_PAIRING, M4L, EVEN_FORM, EVEN_FORM_PRODUCER)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def sector_for(row: int, sectors: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [sector for sector in sectors if sector.get("start", -1) <= row < sector.get("stop", -1)]
    return matches[0] if len(matches) == 1 else None


def expected_pairs(m3r: dict[str, Any]) -> list[dict[str, Any]]:
    dimension = len(m3r.get("ordered_residual_basis", []))
    return [
        {
            "pair_index": item["global_index"],
            "energy": item["energy"],
            "chirality": item["chirality"],
            "family": item["family"],
            "primal_index": item["global_index"],
            "primal_degree": 0,
            "primal_label": item["represented_residual_label"],
            "dual_index": dimension + item["global_index"],
            "dual_degree": 1,
            "dual_label": f"dual[1]({item['represented_residual_label']})",
            "forward_coefficient": "1",
            "reverse_coefficient": "-1",
        }
        for item in m3r.get("ordered_residual_basis", [])
    ]


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text(encoding="utf-8")) if value is None else value
    m3r = json.loads(M3R.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    local_pairing = json.loads(LOCAL_PAIRING.read_text(encoding="utf-8"))
    m4l = json.loads(M4L.read_text(encoding="utf-8"))
    even_form = json.loads(EVEN_FORM.read_text(encoding="utf-8"))
    errors: list[str] = []

    if (
        value.get("result_id") != "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1"
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        errors.append("identity/lifecycle/dependency boundary")
    pins = {
        item.get("path"): item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
    }
    for path in DEPENDENCIES:
        relative = str(path.relative_to(ROOT))
        if pins.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("dependency hash " + relative)
    if (
        m3r.get("result_id") != "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1"
        or dfinite.get("result_id") != "STRICT_DFINITE_RESIDUAL_SDR_V1"
        or local_pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"
        or m4l.get("result_id") != "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1"
        or even_form.get("schema") != "pure-weyl-cross-energy-pairing-v1"
    ):
        errors.append("dependency identity")

    degree_counts: Counter[int] = Counter()
    sector_counts: Counter[str] = Counter()
    coefficient_counts: Counter[str] = Counter()
    columns = 0
    coordinate_defects = 0
    for block in dfinite.get("blocks", []):
        residual = block.get("residual_dimension", 0)
        seen: set[int] = set()
        entries = block.get("matrices", {}).get("iota_cl", {}).get("entries", [])
        columns += len(entries)
        for entry in entries:
            if not isinstance(entry, list) or len(entry) != 3:
                coordinate_defects += 1
                continue
            row, column, raw = entry
            sector = sector_for(row, block.get("full_sectors", []))
            try:
                coefficient = Fraction(raw)
            except (TypeError, ValueError, ZeroDivisionError):
                coordinate_defects += 1
                continue
            if sector is None or column in seen or not 0 <= column < residual or coefficient == 0:
                coordinate_defects += 1
                continue
            seen.add(column)
            degree_counts[sector["ghost_number"]] += 1
            sector_counts[sector["name"]] += 1
            coefficient_counts[str(coefficient)] += 1
        coordinate_defects += residual - len(seen)

    endpoint_rows = {
        row.get("index"): row
        for row in local_pairing.get("component_basis", {}).get("rows", [])
        if row.get("sector") == "CAUSAL_ENDPOINT_30"
    }
    metric = {index for index, row in endpoint_rows.items() if row.get("block") == "ENDPOINT_M"}
    metric_metric = [
        entry
        for entry in local_pairing.get("pairing_serialization", {}).get("entries", [])
        if entry.get("left_index") in metric and entry.get("right_index") in metric
    ]
    expected_obstruction = {
        "m3r_residual_coordinates": 470,
        "m3r_inclusion_nonzero_entries": columns,
        "m3r_inclusion_coordinate_defects": coordinate_defects,
        "m3r_inclusion_degree_counts": {str(key): degree_counts[key] for key in sorted(degree_counts)},
        "m3r_inclusion_sector_counts": dict(sorted(sector_counts.items())),
        "m3r_inclusion_coefficient_counts": dict(sorted(coefficient_counts.items())),
        "authoritative_local_pairing_degree": local_pairing.get("pairing_serialization", {}).get("degree"),
        "endpoint_metric_component_rows": len(metric),
        "endpoint_metric_metric_pairing_nonzeros": len(metric_metric),
        "pulled_back_odd_pairing_nonzeros": 0,
        "pulled_back_odd_pairing_rank": 0,
        "pulled_back_odd_pairing_nullity": 470,
        "required_nondegenerate_rank": 470,
        "nondegeneracy_rank_defect": 470,
        "q_res_cyclicity_defects": 0,
        "reason_q_res_check_is_not_sufficient": "q_res=0 makes the cyclic differential equation vacuous while the induced form remains rank zero",
    }
    if value.get("obstruction_replay") != expected_obstruction:
        errors.append("independent rank-zero obstruction replay")
    if (
        columns != 470
        or coordinate_defects
        or degree_counts != Counter({0: 470})
        or sector_counts != Counter({"metric_tf": 470})
        or coefficient_counts != Counter({"1": 470})
        or len(metric) != 10
        or metric_metric
    ):
        errors.append("obstruction premises")

    control = value.get("older_even_form_control", {})
    if (
        control.get("category") != "raw polynomial D-finite cohomology module"
        or control.get("energies") != [2, 3, 4, 5]
        or control.get("dimension") != 268
        or control.get("symmetric_even_physical_form") is not True
        or control.get("field_theoretic_BV_antibracket_identified") is not False
        or control.get("all_M3R_energies_covered") is not False
        or not any("field-theoretic identification" in item for item in even_form.get("scope", {}).get("not_proved", []))
    ):
        errors.append("even-form category firewall")

    pairs = expected_pairs(m3r)
    preflight = value.get("cotangent_preflight", {})
    if preflight.get("pair_dictionary") != pairs or preflight.get("pair_dictionary_sha256") != digest(pairs):
        errors.append("940-row pair dictionary")
    rows: dict[int, tuple[int, Fraction, int]] = {}
    columns_seen: set[int] = set()
    pairing_defects = 0
    for pair in pairs:
        forward = Fraction(pair["forward_coefficient"])
        reverse = Fraction(pair["reverse_coefficient"])
        left, right = pair["primal_index"], pair["dual_index"]
        if left in rows or right in rows or right in columns_seen or left in columns_seen:
            pairing_defects += 1
        rows[left] = (right, forward, pair["primal_degree"] + pair["dual_degree"])
        rows[right] = (left, reverse, pair["dual_degree"] + pair["primal_degree"])
        columns_seen.update((right, left))
        if reverse != -forward or pair["primal_degree"] + pair["dual_degree"] != 1:
            pairing_defects += 1
    if (
        len(rows) != 940
        or columns_seen != set(range(940))
        or pairing_defects
        or preflight.get("total_dimension") != 940
        or preflight.get("degree_counts") != {"0": 470, "1": 470}
        or preflight.get("nonzero_ordered_pairing_entries") != 940
        or preflight.get("constructive_exact_rank") != 940
        or preflight.get("odd_skew_defects") != 0
        or preflight.get("pairing_degree_defects") != 0
        or preflight.get("action_or_endpoint_pairing_transport") != "NOT_CONSTRUCTED"
    ):
        errors.append("canonical cotangent preflight")

    flags = value.get("claim_flags", {})
    for key in (
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO",
        "FINITE_940_SHIFTED_COTANGENT_CARRIER_CONSTRUCTED",
        "FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_NONDEGENERATE",
        "OLDER_EVEN_COHOMOLOGY_FORM_IS_BV_ANTIBRACKET",
        "FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING",
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    gate = value.get("gate_disposition", {})
    if (
        gate.get("M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION") != "OPEN_AFTER_EXACT_RANK_ZERO_OBSTRUCTION"
        or gate.get("M4R_TYPED_RESIDUAL_CYCLICITY") != "BLOCKED_BY_M3RC"
        or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED"
    ):
        errors.append("gate disposition")
    expected_digest = digest({
        key: value.get(key)
        for key in (
            "scope", "obstruction_replay", "older_even_form_control",
            "cotangent_preflight", "repair_ledger", "foundational_strength",
            "gate_disposition", "claim_flags",
        )
    })
    if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
        errors.append("independent digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - current 470-mode induced odd pairing has exact rank zero")
        print("  - older symmetric cross-energy form is not promoted to a BV antibracket")
        print("  - canonical 940-row cotangent preflight has exact full rank; dual comparison remains open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
