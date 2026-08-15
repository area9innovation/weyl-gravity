#!/usr/bin/env python3
"""Build the exhaustive universal cylinder Bach-Hessian component export."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any, Mapping

from cylinder_polarized_bach_evaluator import PAIRS as POINT_PAIRS, polarized_bach_euler_density, polarized_diff_noether_identity, sparse_fixture
from cylinder_polarized_bach_universal import (
    PAIRS,
    BilinearOperator,
    NaturalTaylor,
    evaluate_rows,
    symmetry_defects,
    universal_euler_construction,
    universal_euler_rows,
    universal_diff_noether_defects,
    universal_weyl_trace_defects,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.md"
UNIVERSAL_ENGINE = HERE / "cylinder_polarized_bach_universal.py"
POINT_ENGINE = HERE / "cylinder_polarized_bach_evaluator.py"
INPUTS = (
    ("quantum-weyl/classical_import/certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json", "STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1", "target and acceptance contract"),
    ("quantum-weyl/classical_import/certificates/STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.json", "STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1", "independent concrete-jet evaluator prototype"),
    ("d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "metric-antifield output type"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def words_through(order: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(sorted((word for word in product(range(order + 1), repeat=4) if sum(word) <= order), key=lambda word: (sum(word), word)))


def input_basis() -> list[dict[str, object]]:
    return [
        {"index": index, "component": component, "component_pair": list(PAIRS[component]), "word": list(word), "order": sum(word)}
        for index, (component, word) in enumerate((item for component in range(10) for item in ((component, word) for word in words_through(4))))
    ]


def _serialize_output(values: Mapping[tuple[int, int], Fraction]) -> list[str]:
    return [str(values[pair]) for pair in PAIRS]


def fifth_jet_fixture(seed: int) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    words = ((0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 4), (1, 1, 1, 2))
    return {
        pair: {words[(index + seed) % len(words)]: Fraction((2 * index + seed) % 11 - 5, index % 4 + 1)}
        for index, pair in enumerate(POINT_PAIRS)
    }


def compact_table(construction: Mapping[str, object]) -> dict[str, object]:
    rows = universal_euler_rows(construction)
    density_rows = construction["density_rows"]
    assert isinstance(density_rows, Mapping)
    defects = symmetry_defects(rows)
    if defects:
        raise ValueError(f"universal input symmetry failed with {len(defects)} defects")
    basis = input_basis()
    basis_index = {(item["component"], tuple(item["word"])): item["index"] for item in basis}
    coefficients: set[Fraction] = set()
    raw_rows = []
    for output_component, pair in enumerate(PAIRS):
        linear = density_rows[pair].linear
        assert isinstance(linear, object)
        linear_entries = []
        for component, word, coefficient in linear.terms:
            if coefficient.base:
                coefficients.add(coefficient.base)
                linear_entries.append((basis_index[(component, word)], coefficient.base))
        oriented = rows[pair].at_base()
        symmetric_entries = []
        for (left, lw, right, rw), coefficient in sorted(oriented.items()):
            left_index, right_index = basis_index[(left, lw)], basis_index[(right, rw)]
            if left_index <= right_index:
                coefficients.add(coefficient)
                symmetric_entries.append((left_index, right_index, coefficient))
        raw_rows.append((output_component, pair, linear_entries, symmetric_entries, len(oriented)))
    coefficient_dictionary = [str(value) for value in sorted(coefficients)]
    coefficient_index = {Fraction(value): index for index, value in enumerate(coefficient_dictionary)}
    serialized_rows = [
        {
            "output_component": output_component,
            "output_pair": list(pair),
            "linear_entries": [[basis_id, coefficient_index[value]] for basis_id, value in linear_entries],
            "symmetric_bilinear_entries": [[left, right, coefficient_index[value]] for left, right, value in symmetric_entries],
            "ordered_term_count_before_symmetry": ordered_count,
        }
        for output_component, pair, linear_entries, symmetric_entries, ordered_count in raw_rows
    ]
    return {
        "input_basis": basis,
        "coefficient_dictionary": coefficient_dictionary,
        "rows": serialized_rows,
        "counts": {
            "input_basis": len(basis),
            "coefficient_dictionary": len(coefficient_dictionary),
            "linear_terms": sum(len(row["linear_entries"]) for row in serialized_rows),
            "ordered_bilinear_terms": sum(row["ordered_term_count_before_symmetry"] for row in serialized_rows),
            "symmetric_bilinear_terms": sum(len(row["symmetric_bilinear_entries"]) for row in serialized_rows),
        },
    }


def compact_apply(table: Mapping[str, object], left: Mapping, right: Mapping) -> dict[tuple[int, int], Fraction]:
    basis = table["input_basis"]
    coefficients = [Fraction(value) for value in table["coefficient_dictionary"]]

    def value(inputs: Mapping, basis_id: int) -> Fraction:
        item = basis[basis_id]
        return Fraction(inputs.get(tuple(item["component_pair"]), {}).get(tuple(item["word"]), 0))

    output = {}
    for row in table["rows"]:
        total = Fraction(0)
        for left_id, right_id, coefficient_id in row["symmetric_bilinear_entries"]:
            coefficient = coefficients[coefficient_id]
            total += coefficient * value(left, left_id) * value(right, right_id)
            if left_id != right_id:
                total += coefficient * value(left, right_id) * value(right, left_id)
        output[tuple(row["output_pair"])] = total
    return output


def build() -> dict[str, Any]:
    benchmark, evaluator, antifield = (json.loads((ROOT / path).read_text()) for path, _, _ in INPUTS)
    if benchmark.get("result_id") != INPUTS[0][1] or evaluator.get("result_id") != INPUTS[1][1]:
        raise ValueError("benchmark/evaluator provenance drift")
    gstar = next(item for item in antifield["generators"] if item["symbol"] == "g_star")
    if gstar["tensor_type"]["symmetry"] != "symmetric_contravariant_density":
        raise ValueError("metric-antifield output type drift")

    construction = universal_euler_construction(1)
    rows = universal_euler_rows(construction)
    table = compact_table(construction)
    trace = universal_weyl_trace_defects(construction)
    if trace != {"background": "0", "linear_term_count": 0, "bilinear_term_count": 0}:
        raise ValueError(f"universal Weyl trace identity failed: {trace}")
    diff_noether = universal_diff_noether_defects(construction)
    expected_diff_rows = [
        {"covector_index": index, "background": "0", "linear_term_count": 0, "bilinear_term_count": 0}
        for index in range(4)
    ]
    if diff_noether["rows"] != expected_diff_rows or diff_noether["required_metric_jet_order"] != 5:
        raise ValueError(f"universal Diff Noether identity failed: {diff_noether}")
    crosschecks = []
    for left_seed, right_seed in ((1, 2), (3, 4), (5, 6)):
        left, right = sparse_fixture(left_seed), sparse_fixture(right_seed)
        universal_result = evaluate_rows(rows, left, right)
        compact_result = compact_apply(table, left, right)
        point_result = polarized_bach_euler_density(left, right)
        if universal_result != compact_result or universal_result != point_result:
            raise ValueError(f"universal/compact/point disagreement for seeds {left_seed},{right_seed}")
        crosschecks.append({
            "left_seed": left_seed,
            "right_seed": right_seed,
            "output": _serialize_output(point_result),
            "nonzero_output_count": sum(value != 0 for value in point_result.values()),
            "output_sha256": digest(_serialize_output(point_result)),
            "universal_equals_compact_equals_point": True,
        })
    diff_point_crosschecks = []
    for left_seed, right_seed in ((1, 2), (3, 4), (5, 6)):
        defects = polarized_diff_noether_identity(fifth_jet_fixture(left_seed), fifth_jet_fixture(right_seed))
        if any(defects.values()):
            raise ValueError(f"point-evaluator Diff Noether defect for seeds {left_seed},{right_seed}: {defects}")
        serialized = [str(defects[index]) for index in range(4)]
        diff_point_crosschecks.append({
            "left_seed": left_seed,
            "right_seed": right_seed,
            "covector_defects": serialized,
            "output_sha256": digest(serialized),
            "all_four_rows_zero": True,
        })
    all_entries = [entry for row in table["rows"] for entry in row["symmetric_bilinear_entries"]]
    basis = table["input_basis"]
    maximum_total_order = max(basis[left]["order"] + basis[right]["order"] for left, right, _ in all_entries)
    row_hashes = {str(tuple(row["output_pair"])): digest(row) for row in table["rows"]}
    value: dict[str, Any] = {
        "schema": "strict-cylinder-bach-universal-export-v1",
        "result_id": "STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1",
        "result_kind": "EXACT_UNIVERSAL_HOMOGENEOUS_BASEPOINT_COMPONENT_TABLE",
        "result_state": "UNIVERSAL_CYLINDER_TABLE_AND_DIFF_IDENTITY_CERTIFIED_GLOBAL_AST_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "1b4b9350",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl metric equation row before ghost/cotangent completion",
            "background": "unit conformal cylinder R x S3",
            "basepoint_chart": "t=0, chi=pi/2, theta=pi/2, phi=0 with coordinates (t,chi,theta,phi)",
            "inputs": "two arbitrary symmetric covariant metric four-jets with normalized coordinate Taylor coefficients",
            "output": {"component_count": 10, "tensor_type": gstar["tensor_type"], "form_degree": gstar["form_degree"], "Weyl_weight": gstar["Weyl_weight"]},
            "taylor_convention": "coefficient of a*b with no hidden factor of 1/2",
            "action_normalization": "B_action=-2 B_standard",
            "maximum_total_input_derivative_order": maximum_total_order,
            "Diff_identity_validation_metric_jet_order": 5,
            "coefficient_field": "Q",
            "support_locality": "every exported entry is a finite product of input derivatives at one point; no inverse differential operator occurs",
            "globalization_boundary": "the table is exhaustive at one homogeneous cylinder frame, but an explicit SO(4) isotropy-covariant tensor-natural globalization certificate is not yet supplied",
        },
        "construction": {
            "algorithm": benchmark["candidate_program_contract"],
            "coefficient_method": "second-order sparse natural-operator automatic differentiation over exact rational coordinate coefficient jets, retaining one output-coordinate derivative for the Diff identity",
            "input_slots": "ordered during construction and reduced only after exact swap equality",
            "producer_cost_class": "TIER_2_EXHAUSTIVE_NOT_PER_COMMIT",
        },
        "universal_table": table,
        "exact_checks": {
            "all_ten_output_rows_present": len(table["rows"]) == 10,
            "all_700_metric_four_jet_basis_inputs_named": table["counts"]["input_basis"] == 700,
            "maximum_total_derivative_order_four": maximum_total_order == 4,
            "input_swap_symmetry_defect_count": len(symmetry_defects(rows)),
            "universal_weyl_trace_defects": trace,
            "universal_diff_noether_defects": diff_noether,
            "three_independent_point_evaluator_crosschecks": crosschecks,
            "three_independent_fifth_jet_diff_point_crosschecks": diff_point_crosschecks,
            "compact_table_reproduces_unreduced_operator": True,
        },
        "canonical_hashes": {
            "input_basis_sha256": digest(table["input_basis"]),
            "coefficient_dictionary_sha256": digest(table["coefficient_dictionary"]),
            "row_sha256": row_hashes,
            "universal_table_sha256": digest(table),
            "point_crosschecks_sha256": digest(crosschecks),
            "diff_point_crosschecks_sha256": digest(diff_point_crosschecks),
        },
        "implementation": {
            "universal_engine": {"path": str(UNIVERSAL_ENGINE.relative_to(ROOT)), "sha256": sha(UNIVERSAL_ENGINE)},
            "point_engine": {"path": str(POINT_ENGINE.relative_to(ROOT)), "sha256": sha(POINT_ENGINE)},
        },
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "independent_receiver": {
            "path": "quantum-weyl/classical_import/check_strict_cylinder_bach_universal_export.py",
            "cost_class": "TIER_1_FAST_REPLAY",
            "replays": ["compact table hashes and shape", "normalized four-jet basis", "full unary and quadratic Weyl identity", "four-row universal fifth-jet Diff status", "three independent fifth-jet point-evaluator Diff probes", "claim and provenance boundaries"],
        },
        "next_gates": [
            {"gate": "HT1B_MODE_ADAPTERS", "status": "OPEN", "required": "evaluate and integrate the two named nonzero cylinder channels"},
            {"gate": "TENSOR_NATURAL_GLOBALIZATION", "status": "OPEN", "required": "certify SO(4) isotropy covariance and portable coordinate/tensor AST semantics"},
            {"gate": "STRICT_HSTAR_PORTABLE_INTEGRATION", "status": "OPEN", "required": "globalize the metric Hessian, suspend all bilinear rows and replay the complete q2 receiver"},
        ],
        "claim_flags": {
            "UNIVERSAL_BASEPOINT_METRIC_HESSIAN_TABLE_EXPORTED": True,
            "EXHAUSTIVE_INPUT_SWAP_AND_WEYL_TRACE_REPLAYED": True,
            "FAST_INDEPENDENT_TABLE_RECEIVER_IMPLEMENTED": True,
            "PORTABLE_TENSOR_NATURAL_HSTAR_ROW": False,
            "DIFFERENTIATED_DIFF_NOETHER_REPLAYED": True,
            "HT1B_NONZERO_CHANNELS_REPLAYED_BY_TABLE": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "an SO(4)-isotropy-covariant tensor-natural globalization of the basepoint table",
            "a tensor-natural coordinate-change or SO(4)-isotropy globalization theorem beyond the exact Weyl and Diff identities",
            "the two nonzero HT1B mode densities or their exact S3 integrations",
            "an exported universal first-coordinate-derivative table; only the exact zero Noether reduction and independent point probes are retained",
            "a portable complete h-star row or suspended six-row q2, despite the separate exact basepoint cotangent assembly",
            "the q1q2, D-derivation or BV-cyclicity receiver identities",
            "a passed Gate A, causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory",
        ],
        "independent_checker": "quantum-weyl/classical_import/check_strict_cylinder_bach_universal_export.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    counts = value["universal_table"]["counts"]
    rows = "\n".join(
        f"| `{tuple(row['output_pair'])}` | {len(row['linear_entries'])} | {row['ordered_term_count_before_symmetry']} | {len(row['symmetric_bilinear_entries'])} |"
        for row in value["universal_table"]["rows"]
    )
    gates = "\n".join(f"| `{item['gate']}` | `{item['status']}` | {item['required']} |" for item in value["next_gates"])
    return f"""# Strict universal cylinder Bach-Hessian export v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The full second-order geometric pipeline has now been differentiated as a
universal local operator at a homogeneous unit-cylinder frame. The compact
table names all **{counts['input_basis']}** symmetric-metric four-jet basis
inputs, all ten contravariant density outputs, and
**{counts['symmetric_bilinear_terms']:,}** nonzero exact symmetric coefficients.
Input-slot symmetry is checked before compression rather than assumed.

This closes the coefficient-enumeration problem at the chosen frame. The same
natural construction, retained through one output-coordinate derivative,
also cancels all four background, unary and quadratic Diff Noether rows on
arbitrary metric five-jets. Three separate point-evaluator fixtures replay
that cancellation. It does not yet close the portable `h_star` row:
SO(4)-isotropy/coordinate globalization, the HT1B adapters and suspended
six-row interaction identities remain separate gates.

## Row sizes

| Output | Unary terms | Ordered bilinear terms | Symmetric stored terms |
|---|---:|---:|---:|
{rows}

The table uses a shared rational coefficient dictionary and a shared 700-entry
input basis. That basis uses normalized Taylor coordinates
`partial^alpha h / alpha!`; the producer explicitly inserts the factorial
shift when a coordinate derivative raises `alpha`. Each bilinear entry is
`[left_basis, right_basis, coefficient]` with `left_basis <= right_basis`;
evaluation restores the swapped term when the two basis indices differ.

## Exact checks

- zero input-swap defects on the unreduced ordered table;
- zero background, unary and quadratic defects in `g_ab E^ab=0`;
- zero background, unary and quadratic terms in all four fifth-jet coordinate
  identities `E^ab partial_lambda g_ab - 2 partial_a(E^ab g_lambda_b)=0`;
- three independent exact fifth-jet point-evaluator Diff probes;
- maximum total input derivative order four;
- three independent concrete-jet comparisons in which the universal table,
  compact table and earlier point evaluator agree exactly.

## Remaining gates

| Gate | Status | Required evidence |
|---|---|---|
{gates}

## Production and replay

The exhaustive producer is intentionally Tier 2 and takes minutes. The
`fast independent checker` replays the checked-in table in seconds and is the
routine per-commit rail.

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_bach_universal_export.py
python3 quantum-weyl/classical_import/check_strict_cylinder_bach_universal_export.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_bach_universal_export.py
```

## Does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="rerun the exhaustive producer and compare generated bytes")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1: wrote exhaustive certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
