#!/usr/bin/env python3
"""Classify the M4R obstruction and build the minimal finite cotangent preflight."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
LOCAL_PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
EVEN_FORM = ROOT / "bridge/certificates/cross_energy_pairing.json"
EVEN_FORM_PRODUCER = ROOT / "symbolic/verify_conformal_cross_energy_pairing.py"
RESULT = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def pin(path: Path, artifact_id: str, role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": artifact_id,
        "sha256": sha(path),
        "role": role,
    }


def containing_sector(row: int, sectors: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [sector for sector in sectors if sector["start"] <= row < sector["stop"]]
    if len(matches) != 1:
        raise ValueError(f"full-coordinate row {row} has {len(matches)} sectors")
    return matches[0]


def build() -> dict[str, Any]:
    m3r = load(M3R)
    dfinite = load(DFINITE)
    local_pairing = load(LOCAL_PAIRING)
    m4l = load(M4L)
    even_form = load(EVEN_FORM)
    identities = (
        (m3r.get("result_id"), "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1"),
        (dfinite.get("result_id"), "STRICT_DFINITE_RESIDUAL_SDR_V1"),
        (local_pairing.get("result_id"), "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"),
        (m4l.get("result_id"), "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1"),
        (even_form.get("schema"), "pure-weyl-cross-energy-pairing-v1"),
    )
    if any(actual != expected for actual, expected in identities):
        raise ValueError("residual cyclic-carrier dependency identity drift")
    if m3r["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not True:
        raise ValueError("M3R is unavailable")
    if m4l["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"] is not True:
        raise ValueError("M4L is unavailable")
    if local_pairing["pairing_serialization"]["degree"] != -1:
        raise ValueError("authoritative local pairing degree drift")

    degree_counts: Counter[int] = Counter()
    sector_counts: Counter[str] = Counter()
    coefficient_counts: Counter[str] = Counter()
    energy_counts: dict[str, int] = {}
    inclusion_entries = 0
    inclusion_coordinate_defects = 0
    for block in dfinite["blocks"]:
        residual_dimension = block["residual_dimension"]
        energy_counts[str(block["energy"])] = residual_dimension
        entries = block["matrices"]["iota_cl"]["entries"]
        inclusion_entries += len(entries)
        seen_columns: set[int] = set()
        for row, column, coefficient in entries:
            sector = containing_sector(row, block["full_sectors"])
            sector_counts[sector["name"]] += 1
            degree_counts[sector["ghost_number"]] += 1
            coefficient_counts[coefficient] += 1
            if column in seen_columns or not 0 <= column < residual_dimension:
                inclusion_coordinate_defects += 1
            seen_columns.add(column)
        inclusion_coordinate_defects += residual_dimension - len(seen_columns)

    endpoint_rows = {
        row["index"]: row
        for row in local_pairing["component_basis"]["rows"]
        if row["sector"] == "CAUSAL_ENDPOINT_30"
    }
    metric_indices = {
        index for index, row in endpoint_rows.items() if row["block"] == "ENDPOINT_M"
    }
    endpoint_entries = [
        entry
        for entry in local_pairing["pairing_serialization"]["entries"]
        if entry["left_index"] in endpoint_rows and entry["right_index"] in endpoint_rows
    ]
    metric_metric_entries = [
        entry
        for entry in endpoint_entries
        if entry["left_index"] in metric_indices and entry["right_index"] in metric_indices
    ]

    residual_dimension = len(m3r["ordered_residual_basis"])
    if (
        residual_dimension != 470
        or inclusion_entries != residual_dimension
        or degree_counts != Counter({0: residual_dimension})
        or sector_counts != Counter({"metric_tf": residual_dimension})
        or coefficient_counts != Counter({"1": residual_dimension})
        or inclusion_coordinate_defects
        or metric_metric_entries
    ):
        raise ValueError("degree-concentrated M3R obstruction replay drift")

    pair_dictionary = []
    for item in m3r["ordered_residual_basis"]:
        index = item["global_index"]
        label = item["represented_residual_label"]
        pair_dictionary.append({
            "pair_index": index,
            "energy": item["energy"],
            "chirality": item["chirality"],
            "family": item["family"],
            "primal_index": index,
            "primal_degree": 0,
            "primal_label": label,
            "dual_index": residual_dimension + index,
            "dual_degree": 1,
            "dual_label": f"dual[1]({label})",
            "forward_coefficient": "1",
            "reverse_coefficient": "-1",
        })

    old_even_levels = even_form["levels"]
    old_even_dimension = sum(level["dimension"] for level in old_even_levels)
    old_even_not_proved = even_form["scope"]["not_proved"]
    if (
        [level["energy"] for level in old_even_levels] != [2, 3, 4, 5]
        or old_even_dimension != 268
        or "field-theoretic identification of the constructed cyclic form with a chosen gauge-fixed BV antibracket domain" not in old_even_not_proved
    ):
        raise ValueError("older even-form control drift")

    obstruction_replay = {
        "m3r_residual_coordinates": residual_dimension,
        "m3r_inclusion_nonzero_entries": inclusion_entries,
        "m3r_inclusion_coordinate_defects": inclusion_coordinate_defects,
        "m3r_inclusion_degree_counts": {str(key): degree_counts[key] for key in sorted(degree_counts)},
        "m3r_inclusion_sector_counts": dict(sorted(sector_counts.items())),
        "m3r_inclusion_coefficient_counts": dict(sorted(coefficient_counts.items())),
        "authoritative_local_pairing_degree": -1,
        "endpoint_metric_component_rows": len(metric_indices),
        "endpoint_metric_metric_pairing_nonzeros": len(metric_metric_entries),
        "pulled_back_odd_pairing_nonzeros": 0,
        "pulled_back_odd_pairing_rank": 0,
        "pulled_back_odd_pairing_nullity": residual_dimension,
        "required_nondegenerate_rank": residual_dimension,
        "nondegeneracy_rank_defect": residual_dimension,
        "q_res_cyclicity_defects": 0,
        "reason_q_res_check_is_not_sufficient": "q_res=0 makes the cyclic differential equation vacuous while the induced form remains rank zero",
    }
    cotangent_preflight = {
        "status": "FINITE_ALGEBRAIC_CARRIER_AND_PAIRING_CONSTRUCTED_COMPARISON_MAPS_OPEN",
        "object": "T_star[-1](H_res^[2,6]) represented as H_res degree 0 plus H_res^vee[1] degree 1",
        "primal_dimension": residual_dimension,
        "adjoined_dual_dimension": residual_dimension,
        "total_dimension": 2 * residual_dimension,
        "degree_counts": {"0": residual_dimension, "1": residual_dimension},
        "differential": "zero on both finite halves",
        "pairing_degree": -1,
        "pairing_convention": "Omega(primal_i,dual_j)=delta_ij; Omega(dual_j,primal_i)=-delta_ij",
        "nonzero_ordered_pairing_entries": 2 * residual_dimension,
        "constructive_exact_rank": 2 * residual_dimension,
        "odd_skew_defects": 0,
        "pairing_degree_defects": 0,
        "q_res_cyclicity_defects": 0,
        "pair_dictionary_sha256": digest(pair_dictionary),
        "pair_dictionary": pair_dictionary,
        "minimality_scope": "minimal within the declared full shifted-cotangent completion class because every one of the 470 primal coordinates receives one independent dual",
        "absolute_minimal_cyclic_completion": "NOT_PROVED",
        "action_or_endpoint_pairing_transport": "NOT_CONSTRUCTED",
    }

    artifact_pins = [
        pin(M3R, m3r["result_id"], "fixed 470-mode M3R ordering and metric-only synthesis"),
        pin(DFINITE, dfinite["result_id"], "exact finite inclusion, projection, homotopy and degree-labelled source sectors"),
        pin(LOCAL_PAIRING, local_pairing["result_id"], "authoritative degree-minus-one local BV pairing"),
        pin(M4L, m4l["result_id"], "completed local cyclicity and typed M4R obligation"),
        pin(EVEN_FORM, even_form["schema"], "older symmetric physical cohomology form used only as a category control"),
        pin(EVEN_FORM_PRODUCER, "CONFORMAL_CROSS_ENERGY_PAIRING_PRODUCER", "source-level refusal to promote the even form to a full BV pairing"),
    ]

    result: dict[str, Any] = {
        "$schema": "../schema/strict-residual-cyclic-carrier-obstruction-v1.schema.json",
        "schema": "strict-residual-cyclic-carrier-obstruction-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-residual-cyclic-carrier-obstruction-v1.schema.json",
        "result_id": "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1",
        "result_kind": "CLASSICAL_IMPORT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_AND_COTANGENT_PREFLIGHT",
        "result_state": "CURRENT_470_MODE_M4R_OBSTRUCTED_MINIMAL_940_COTANGENT_PREFLIGHT_CONSTRUCTED_DUAL_COMPARISON_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "6395898920233872342d9f24757d5c7406f5db05",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Does the fixed 470-mode M3R carrier inherit the nondegenerate odd BV pairing required by M4R, and if not what is the smallest explicit finite repair class?",
        "answer": "No. Every M3R residual coordinate has degree zero and its synthesis lands in a trace-free metric slot. The authoritative degree-minus-one local BV form has no metric-metric block, so its literal pullback along the 470-column synthesis is the zero matrix: rank zero, nullity 470. The older cross-energy form is symmetric, even, covers only energies two through five in its committed certificate, and explicitly does not identify itself with the field-theoretic BV antibracket. It cannot discharge M4R. A 940-coordinate shifted-cotangent carrier with one degree-one dual per M3R coordinate has an explicit exact rank-940 odd pairing and zero differential, but its dual inclusion, projection and cyclic homotopy into the authoritative endpoint complex are not constructed. M4R therefore remains fail closed behind a new M3RC cyclic-carrier-completion prerequisite.",
        "scope": {
            "theory": "strict pure-Weyl free classical BV residual comparison",
            "background": "unit Lorentzian conformal cylinder",
            "energies": [2, 3, 4, 5, 6],
            "current_residual_carrier": "470 positive-energy W+/W- metric-mode coefficients",
            "pairing_source": "degree-minus-one local Gate-canonical BV pairing",
            "arithmetic": "finite exact integer sparse incidence",
        },
        "obstruction_replay": obstruction_replay,
        "older_even_form_control": {
            "artifact": even_form["schema"],
            "category": even_form["category"],
            "normalization": even_form["normalization"],
            "energies": [level["energy"] for level in old_even_levels],
            "dimension": old_even_dimension,
            "symmetric_even_physical_form": True,
            "field_theoretic_BV_antibracket_identified": False,
            "all_M3R_energies_covered": False,
            "disposition": "VALID_EVEN_REPRESENTATION_THEORETIC_CONTROL_NOT_M4R_EVIDENCE",
        },
        "cotangent_preflight": cotangent_preflight,
        "repair_ledger": [
            {
                "id": "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION",
                "status": "OPEN",
                "need": "Construct degree-one dual representatives and exact dual inclusion/projection on the same represented endpoint domain, then identify the pulled action pairing with the canonical 940-coordinate cotangent pairing.",
            },
            {
                "id": "M4R_TYPED_RESIDUAL_CYCLICITY",
                "status": "BLOCKED_BY_M3RC",
                "need": "After M3RC, replay nondegeneracy, p=iota-sharp, homotopy skew-adjointness and residual transfer cyclic side conditions exactly.",
            },
            {
                "id": "M1_COMMON_STRICT_SNAPSHOT",
                "status": "BLOCKED_BY_M3RC_AND_M4R",
                "need": "Freeze both primal and dual residual maps with all local exports under one content-addressed manifest.",
            },
        ],
        "foundational_strength": {
            "obstruction_and_940_preflight": "finite exact enumeration and signed-permutation rank, formalizable in PRA",
            "choice_dependency_added": "none at fixed finite cutoff",
            "Hilbert_or_Krein_completion_used": False,
            "all_energy_dual_warning": "an infinite completion must declare algebraic, continuous, Hilbert, Krein or distributional duality; these are inequivalent assumptions",
            "support_warning": "the fixed harmonic restriction remains global and support-expanding",
        },
        "gate_disposition": {
            "M3R_PRIMAL_COMPARISON": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
            "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "OPEN_AFTER_EXACT_RANK_ZERO_OBSTRUCTION",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "provenance": {"inputs": artifact_pins},
        "claim_flags": {
            "CURRENT_470_MODE_INDUCED_ODD_PAIRING_NONDEGENERATE": False,
            "CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO": True,
            "OLDER_EVEN_COHOMOLOGY_FORM_IS_BV_ANTIBRACKET": False,
            "FINITE_940_SHIFTED_COTANGENT_CARRIER_CONSTRUCTED": True,
            "FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE": True,
            "FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING": False,
            "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED": False,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "that no cyclic residual completion exists",
            "absolute minimality of 940 dimensions among all possible mixed or quotient carriers",
            "degree-one dual representatives or their inclusion and projection in the endpoint complex",
            "identification of the canonical cotangent preflight pairing with the action-derived local BV pairing",
            "M4R cyclic contraction or the M1 common freeze",
            "an all-energy topological dual, support-local harmonic projector or analytic completion",
            "a Lorentzian off-shell propagator, Hadamard state, renormalized products, QME restoration or quantum residual transfer",
        ],
        "next_gate": "Construct M3RC by adjoining and source-identifying the 470 degree-one dual residual representatives on the same endpoint domain; only then replay M4R and attempt M1.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_residual_cyclic_carrier_obstruction.py",
            "checks": [
                "all six dependency hashes and identities",
                "all 470 iota columns land once in degree-zero metric slots",
                "the authoritative endpoint pairing has no metric-metric entries",
                "the pulled odd pairing has exact rank zero and nullity 470",
                "the older symmetric even form remains outside the BV-pairing category",
                "the 940-row cotangent signed-permutation pairing has exact full rank and correct degree",
                "M3RC, M4R, Gate A, Hadamard and QME firewalls",
            ],
            "expected_digest": "",
        },
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in (
            "scope", "obstruction_replay", "older_even_form_control",
            "cotangent_preflight", "repair_ledger", "foundational_strength",
            "gate_disposition", "claim_flags",
        )
    })
    return result


def report(value: dict[str, Any]) -> str:
    obstruction = value["obstruction_replay"]
    cotangent = value["cotangent_preflight"]
    return f"""# Residual cyclic-carrier obstruction and cotangent preflight

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M4R:** `BLOCKED_BY_M3RC`
**Gate A:** `FAIL_CLOSED`

## Decisive obstruction

The current M3R target contains {obstruction['m3r_residual_coordinates']} positive-energy
W+/W- coordinates, all in degree zero.  Every synthesis column lands in a
trace-free metric slot.  The authoritative degree-minus-one BV pairing pairs
metric rows with metric-antifield rows and has no metric--metric entries.
Consequently the literal induced form `iota_M3R^T Omega iota_M3R` has
{obstruction['pulled_back_odd_pairing_nonzeros']} entries, rank
{obstruction['pulled_back_odd_pairing_rank']}, and nullity
{obstruction['pulled_back_odd_pairing_nullity']}.  Nondegeneracy requires rank
{obstruction['required_nondegenerate_rank']}.

The equation `q_res^T Omega + Omega q_res=0` is not a rescue: `q_res=0`, so it
is vacuous even for the zero form.

## Why the older cross-energy form does not close M4R

The committed cross-energy certificate is a valid symmetric even form on 268
raw physical coordinates at energies two through five.  It explicitly does
not identify that form with a gauge-fixed field-theoretic BV antibracket, and
it omits energy six.  It remains useful representation-theoretic evidence but
is not evidence for the degree-minus-one M4R pairing.

## Smallest explicit repair class

Adjoining one degree-one dual for each primal coordinate produces the
{cotangent['total_dimension']}-coordinate finite shifted-cotangent carrier.
Its canonical signed-permutation odd pairing has
{cotangent['nonzero_ordered_pairing_entries']} nonzero ordered entries and
exact rank {cotangent['constructive_exact_rank']}.  This is minimal only
within the declared full cotangent-completion class.

The dual inclusion, projection, and homotopy into the authoritative endpoint
complex are not constructed.  Therefore this is an exact carrier preflight,
not M4R.  The next gate is M3RC: construct and identify those dual comparison
maps, then replay cyclicity and only afterward attempt the M1 common freeze.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_cyclic_carrier_obstruction.py --check
python3 quantum-weyl/classical_import/check_strict_residual_cyclic_carrier_obstruction.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_residual_cyclic_carrier_obstruction.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
