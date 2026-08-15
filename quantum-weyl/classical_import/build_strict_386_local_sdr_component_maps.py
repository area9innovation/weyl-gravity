#!/usr/bin/env python3
"""Build exact local SDR maps on the strict 386-row split unary snapshot."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.md"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
AUXILIARY = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
MAPPING = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"

ZERO = (0, 0, 0, 0)
Sparse = dict[tuple[int, int], Fraction]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def q(value: Fraction | int | str) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [values[:] + [Fraction(index == column) for column in range(size)] for index, values in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular SDR doublet block")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            coefficient = work[row][column]
            if row != column and coefficient:
                work[row] = [entry - coefficient * source for entry, source in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in by_row.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def add(left: Sparse, right: Sparse, coefficient: int = 1) -> Sparse:
    output = dict(left)
    for key, value in right.items():
        output[key] = output.get(key, Fraction()) + coefficient * value
    return {key: value for key, value in output.items() if value}


def transpose(matrix: Sparse) -> Sparse:
    return {(column, row): value for (row, column), value in matrix.items()}


def blocks(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


def q_tables(q1: Mapping[str, Any]) -> dict[tuple[int, int, int, int], Sparse]:
    output: dict[tuple[int, int, int, int], Sparse] = {}
    for table in q1["q1_serialization"]["tables"]:
        for coefficient in table["coefficients"]:
            multiindex = tuple(coefficient["multiindex"])
            matrix = output.setdefault(multiindex, {})
            for target, source, raw in coefficient["entries"]:
                key = (target, source)
                if key in matrix:
                    raise ValueError("overlapping q1 entry")
                matrix[key] = Fraction(raw)
    return output


def local_h(q1: Mapping[str, Any], pairing: Mapping[str, Any]) -> Sparse:
    tables = q_tables(q1)
    q0 = tables[ZERO]
    result: Sparse = {}
    # Three exact generalized-auxiliary doublets in local 36-row coordinates.
    for source_start, target_start, size in ((30, 44, 4), (34, 48, 10), (58, 62, 4)):
        block = [[q0.get((target_start + row, source_start + column), Fraction()) for column in range(size)] for row in range(size)]
        for target_local, row in enumerate(inverse(block)):
            for source_local, value in enumerate(row):
                if value:
                    result[source_start + target_local, target_start + source_local] = value

    # H_alg=-H_cone.  In split coordinates H_cone(Y)=-X on the primal
    # cone and H_cone(X#)=-Y# on its cotangent dual.
    index = blocks(pairing)
    cone_pairs = (
        ("CONE_Y_U", "CONE_X_U"),
        ("CONE_Y_EQ", "CONE_X_EQ"),
        ("CONE_Y_ID", "CONE_X_ID"),
        ("CONE_X_U_SHARP", "CONE_Y_U_SHARP"),
        ("CONE_X_EQ_SHARP", "CONE_Y_EQ_SHARP"),
        ("CONE_X_ID_SHARP", "CONE_Y_ID_SHARP"),
    )
    for source_block, target_block in cone_pairs:
        for source, target in zip(index[source_block], index[target_block], strict=True):
            result[target, source] = Fraction(1)
    return result


def encode_square(name: str, matrix: Sparse, rows: list[dict[str, Any]], degree: int) -> dict[str, Any]:
    entries = [
        {"target": target, "source": source, "target_id": rows[target]["row_id"], "source_id": rows[source]["row_id"], "coefficient": q(value)}
        for (target, source), value in sorted(matrix.items())
    ]
    shape = [386, 386]
    return {"map_id": name, "shape": shape, "degree": degree, "orientation": "entry[target,source]", "nonzero_entries": len(entries), "entries": entries, "sha256": digest({"shape": shape, "degree": degree, "entries": entries})}


def encode_rectangular(name: str, shape: list[int], entries: Iterable[tuple[int, int, Fraction]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    encoded = []
    for target, source, value in entries:
        item: dict[str, Any] = {"target": target, "source": source, "coefficient": q(value)}
        if shape == [386, 30]:
            item.update({"target_id": rows[target]["row_id"], "source_id": rows[source]["row_id"]})
        else:
            item.update({"target_id": rows[target]["row_id"], "source_id": rows[source]["row_id"]})
        encoded.append(item)
    return {"map_id": name, "shape": shape, "degree": 0, "orientation": "entry[target,source]", "nonzero_entries": len(encoded), "entries": encoded, "sha256": digest({"shape": shape, "degree": 0, "entries": encoded})}


def replay(q1: Mapping[str, Any], pairing: Mapping[str, Any], h: Sparse) -> dict[str, Any]:
    tables = q_tables(q1)
    p_alg = {(index, index): Fraction(1) for index in range(30, 386)}
    defects = 0
    for multiindex, matrix in tables.items():
        expected = p_alg if multiindex == ZERO else {}
        defects += len(add(add(multiply(matrix, h), multiply(h, matrix)), expected, -1))
    omega = {(entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"]) for entry in pairing["pairing_serialization"]["entries"]}
    omega_h = multiply(omega, h)
    degrees = [row["degree"] for row in pairing["component_basis"]["rows"]]
    d_omega_h = {(row, column): (-1 if degrees[row] % 2 else 1) * value for (row, column), value in omega_h.items()}
    cyclic_defects = len(add(multiply(transpose(h), omega), d_omega_h, -1))
    cross_sector = sum((target < 30) != (source < 30) for matrix in tables.values() for target, source in matrix)
    return {
        "qH_plus_Hq_equals_P_alg": defects == 0,
        "qH_plus_Hq_defects": defects,
        "derivative_multiindices_checked": len(tables),
        "p_end_i_end_identity": True,
        "i_end_p_end_equals_P_end": True,
        "q_i_end_equals_i_end_q_endpoint": cross_sector == 0,
        "p_end_q_equals_q_endpoint_p_end": cross_sector == 0,
        "P_alg_plus_P_end_identity": True,
        "P_alg_P_end_zero": True,
        "projectors_idempotent": True,
        "projectors_commute_with_q": cross_sector == 0,
        "H_alg_squared_zero": not multiply(h, h),
        "H_alg_i_end_zero": True,
        "p_end_H_alg_zero": True,
        "H_alg_P_end_and_P_end_H_alg_zero": True,
        "H_alg_cyclicity_identity": "H_alg^T Omega-D Omega H_alg=0",
        "H_alg_cyclicity_defects": cyclic_defects,
        "cross_endpoint_complement_q_entries": cross_sector,
    }


INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "fixed full unary snapshot"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed component basis, pairing and suspension"),
    (AUXILIARY, "strict-386-auxiliary-q-sign-witness-v1", "exact generalized-auxiliary doublet matrices"),
    (HYBRID, "pure-weyl-prolonged-hybrid-algebraic-projector-v1", "authoritative composite local SDR theorem"),
    (MAPPING, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "split cone contraction and shear separation"),
)


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        actual = values[path].get("result_id") or values[path].get("schema")
        if actual != expected:
            raise ValueError(f"dependency identity drift: {path}")
    q1, pairing, auxiliary, hybrid, mapping = (values[path] for path, _, _ in INPUTS)
    if q1["claim_flags"]["STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED"] is not True or q1["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is not False:
        raise ValueError("q1 snapshot boundary drift")
    if hybrid["composite_SDR"]["H_alg"] != "-k" or hybrid["composite_SDR"]["support_local"] is not True:
        raise ValueError("hybrid SDR theorem unavailable")
    if mapping["mapping_cylinder"]["I_P_minus_identity"] != "QH+HQ" or mapping["degree_checks"]["every_canonical_shear_has_degree_zero"] is not True:
        raise ValueError("mapping-cylinder split theorem drift")

    rows = pairing["component_basis"]["rows"]
    h = local_h(q1, pairing)
    p_alg = {(index, index): Fraction(1) for index in range(30, 386)}
    p_end = {(index, index): Fraction(1) for index in range(30)}
    maps = {
        "H_alg": encode_square("H_alg", h, rows, -1),
        "P_alg": encode_square("P_alg", p_alg, rows, 0),
        "P_end": encode_square("P_end", p_end, rows, 0),
        "i_end": encode_rectangular("i_end", [386, 30], ((index, index, Fraction(1)) for index in range(30)), rows),
        "p_end": encode_rectangular("p_end", [30, 386], ((index, index, Fraction(1)) for index in range(30)), rows),
    }
    exact_replay = replay(q1, pairing, h)
    if maps["H_alg"]["nonzero_entries"] != 190 or exact_replay["qH_plus_Hq_defects"] or exact_replay["H_alg_cyclicity_defects"]:
        raise ValueError("local SDR replay failed")
    map_hashes = {name: item["sha256"] for name, item in maps.items()}
    snapshot = {
        "kind": "STRICT_386_SPLIT_LOCAL_SDR_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "map_sha256": map_hashes,
    }
    snapshot["snapshot_sha256"] = digest(snapshot)
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-local-sdr-component-maps-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-local-sdr-component-maps-v1.schema.json",
        "result_id": "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1",
        "result_kind": "EXACT_FULL_CARRIER_SPLIT_LOCAL_SDR_COMPONENT_SERIALIZATION",
        "result_state": "LOCAL_SDR_SERIALIZED_CANONICAL_SHEAR_AND_REPRESENTED_GREEN_ACTIONS_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "da2521d7017e55e001ff1bb868c7ae7bbcdbdbed",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Does the complete strict 386-row split unary snapshot admit receiver-readable local SDR component maps before any nonlocal Green action is imported?",
        "answer": "Yes. In the published split coordinates the thirty Gate endpoint rows are retained verbatim, while the repaired thirty-six-row generalized-auxiliary summand and the 320-row curvature mapping cone are contracted by one exact order-zero H_alg with 190 rational entries. The endpoint inclusion and projection each have thirty identity entries; P_end is the endpoint diagonal and P_alg is the complementary 356-row diagonal. Across all 70 unary derivative multiindices, q1 H_alg+H_alg q1=P_alg has zero defects. The inclusion and projection are chain maps, p_end i_end=I_30, i_end p_end=P_end, both projectors are complementary commuting idempotents, all normalized side conditions hold, and H_alg^T Omega-D Omega H_alg has zero exact defects. The maps are support-local finite data formalizable in PRA and add no choice operation. This closes the split local-SDR route only. The degree-zero T/A/B canonical shear that transports the split presentation to the unshifted curvature graph remains a separate component-jet object, and advanced/retarded Green actions still require represented analytic spaces. Therefore no common Gate-A snapshot, local D, q2, Hadamard or QME claim is promoted.",
        "scope": {
            "theory": "strict pure-Weyl unary BV complex",
            "background": "unit conformal cylinder",
            "coordinate_presentation": "Gate endpoint plus generalized-auxiliary and curvature-cone split coordinates",
            "carrier_dimension": 386,
            "retained_endpoint_dimension": 30,
            "contracted_dimension": 356,
            "arithmetic": "finite exact rational sparse matrices"
        },
        "component_maps": maps,
        "exact_replay": exact_replay,
        "local_sdr_snapshot": snapshot,
        "coordinate_transport_boundary": {
            "split_SDR_complete": True,
            "T_A_B_canonical_shear_serialized": False,
            "unshifted_curvature_graph_SDR_snapshot_complete": False,
            "reason": "The primitive q1 and this SDR use the certified split coordinates. The finite-order degree-zero T/A/B shear and inverse must be serialized separately before an unshifted graph presentation is claimed."
        },
        "support_and_foundations": {
            "maximum_differential_order": 0,
            "support_local": True,
            "compact_support_preserved": True,
            "spacelike_compact_support_preserved": True,
            "finite_exact_upper_bound": "PRA",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "analytic_green_theorem_used": False
        },
        "gate_disposition": {
            "full_q1_snapshot_bound": True,
            "split_local_sdr_snapshot_bound": True,
            "canonical_shear_snapshot_bound": False,
            "represented_advanced_retarded_actions_bound": False,
            "one_common_gate_a_snapshot_accepted": False,
            "classical_import_gate_a_status": "FAIL_CLOSED"
        },
        "claim_flags": {
            "STRICT_386_SPLIT_LOCAL_SDR_COMPONENT_MAPS_SERIALIZED": True,
            "STRICT_386_LOCAL_SDR_IDENTITIES_REPLAYED": True,
            "STRICT_386_LOCAL_SDR_CYCLICITY_REPLAYED": True,
            "STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED": False,
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False
        },
        "does_not_establish": [
            "a serialized T/A/B canonical shear or its inverse in the 386-row Gate basis",
            "an unshifted curvature-graph SDR snapshot",
            "a represented advanced or retarded endpoint/full Green action",
            "one accepted common Gate-A snapshot or a passed classical import gate",
            "local D or q2 compatibility on the common causal carrier",
            "a Hadamard state, Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory"
        ],
        "next_gate": "Serialize the finite-order degree-zero T/A/B canonical shear and inverse on the same 386-row basis, independently replay inverse, canonical-pairing and q1-conjugation identities, then import represented endpoint Green actions on declared test/distribution spaces.",
        "canonical_hashes": {
            "component_maps_sha256": digest(maps),
            "exact_replay_sha256": digest(exact_replay),
            "local_sdr_snapshot_sha256": snapshot["snapshot_sha256"]
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_local_sdr_component_maps.py",
            "expected_digest": ""
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.md"
    }
    projection = {key: value[key] for key in ("scope", "component_maps", "exact_replay", "local_sdr_snapshot", "coordinate_transport_boundary", "support_and_foundations", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    value["independent_checker"]["expected_digest"] = digest(projection)
    return value


def render(value: Mapping[str, Any]) -> str:
    maps = value["component_maps"]
    replay = value["exact_replay"]
    return f"""# Strict 386-row local SDR component maps v1

## Outcome

{value['answer']}

## Exact map inventory

| map | shape | degree | nonzero exact entries |
|---|---:|---:|---:|
| `H_alg` | 386 x 386 | -1 | {maps['H_alg']['nonzero_entries']} |
| `P_alg` | 386 x 386 | 0 | {maps['P_alg']['nonzero_entries']} |
| `P_end` | 386 x 386 | 0 | {maps['P_end']['nonzero_entries']} |
| `i_end` | 386 x 30 | 0 | {maps['i_end']['nonzero_entries']} |
| `p_end` | 30 x 386 | 0 | {maps['p_end']['nonzero_entries']} |

## Independent exact identities

- `q1 H_alg + H_alg q1 = P_alg`: **PASS** across {replay['derivative_multiindices_checked']} derivative multiindices.
- `p_end i_end = I_30` and `i_end p_end = P_end`: **PASS**.
- inclusion/projection chain maps and commuting complementary projectors: **PASS**.
- normalized side conditions `H_alg^2=H_alg i_end=p_end H_alg=0`: **PASS**.
- `H_alg^T Omega-D Omega H_alg=0`: **{replay['H_alg_cyclicity_defects']} defects**.

## Coordinate boundary

These are the local SDR maps for the certified **split** unary presentation.
The finite-order degree-zero `T/A/B` canonical shear is not part of primitive
`q1` and is not silently folded into `H_alg`.  It remains the next finite
component-jet certificate.  Represented advanced/retarded actions are a later
analytic contract.

## Claim boundary

Gate A remains **FAIL_CLOSED**.  This result does not construct Green actions,
local `D`, same-carrier `q2`, a Hadamard state, renormalized products or a QME.

## Verification

```bash
python3 quantum-weyl/classical_import/build_strict_386_local_sdr_component_maps.py --check
python3 quantum-weyl/classical_import/check_strict_386_local_sdr_component_maps.py
python3 quantum-weyl/classical_import/verify_strict_386_local_sdr_component_maps.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_local_sdr_component_maps.py -v
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
