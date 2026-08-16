#!/usr/bin/env python3
"""Independent receiver for the strict M1B primal composite contraction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
REPORT = HERE / "REPORT_STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.md"
SCHEMA = HERE / "schema/strict-m1b-primal-composite-contraction-v1.schema.json"
M1A = HERE / "certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
CROSSWALK = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
INPUTS = (M1A, CROSSWALK, GRAPH, M3R, DFINITE)

Sparse = dict[tuple[int, int], Fraction]
Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_object(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def rational(value: Any) -> Fraction:
    return Fraction(str(value))


def encode_rational(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def read_sparse(rows: list[list[Any]]) -> tuple[Sparse, int]:
    matrix: Sparse = {}
    duplicates = 0
    for target, source, coefficient in rows:
        key = (int(target), int(source))
        if key in matrix:
            duplicates += 1
        matrix[key] = matrix.get(key, Fraction(0)) + rational(coefficient)
        if matrix[key] == 0:
            del matrix[key]
    return matrix, duplicates


def compose(left: Sparse, right: Sparse) -> Sparse:
    indexed: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        indexed.setdefault(row, []).append((column, coefficient))
    answer: Sparse = {}
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in indexed.get(middle, []):
            key = (row, column)
            answer[key] = answer.get(key, Fraction(0)) + left_coefficient * right_coefficient
            if answer[key] == 0:
                del answer[key]
    return answer


def linear_combination(*terms: tuple[Fraction, Sparse]) -> Sparse:
    answer: Sparse = {}
    for scale, matrix in terms:
        for key, coefficient in matrix.items():
            answer[key] = answer.get(key, Fraction(0)) + scale * coefficient
            if answer[key] == 0:
                del answer[key]
    return answer


def unit(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def matrix_record(name: str, rows: int, columns: int, matrix: Sparse) -> dict[str, Any]:
    entries = [
        [target, source, encode_rational(coefficient)]
        for (target, source), coefficient in sorted(matrix.items())
    ]
    return {
        "name": name,
        "shape": [rows, columns],
        "orientation": "entry[target_index,source_index]",
        "entries": entries,
        "nonzero_entries": len(entries),
        "sha256": digest_object({"shape": [rows, columns], "entries": entries}),
    }


def restrict_square(raw: list[list[Any]], kept: list[int], excluded: set[int]) -> tuple[Sparse, int, int]:
    remap = {old: new for new, old in enumerate(kept)}
    answer: Sparse = {}
    cross = 0
    duplicates = 0
    for target, source, coefficient in raw:
        target = int(target)
        source = int(source)
        target_kept = target in remap
        source_kept = source in remap
        if target_kept and source_kept:
            key = (remap[target], remap[source])
            duplicates += int(key in answer)
            answer[key] = answer.get(key, Fraction(0)) + rational(coefficient)
            if answer[key] == 0:
                del answer[key]
        elif target_kept != source_kept:
            cross += 1
        elif target not in excluded or source not in excluded:
            raise ValueError("restriction contains an unclassified coordinate")
    return answer, cross, duplicates


def restrict_rectangular(raw: list[list[Any]], row_map: dict[int, int] | None, column_map: dict[int, int] | None) -> tuple[Sparse, int]:
    answer: Sparse = {}
    duplicates = 0
    for target, source, coefficient in raw:
        target = int(target)
        source = int(source)
        new_target = target if row_map is None else row_map.get(target)
        new_source = source if column_map is None else column_map.get(source)
        if new_target is None or new_source is None:
            continue
        key = (new_target, new_source)
        duplicates += int(key in answer)
        answer[key] = answer.get(key, Fraction(0)) + rational(coefficient)
        if answer[key] == 0:
            del answer[key]
    return answer, duplicates


def matrix_defects(q: Sparse, inclusion: Sparse, projection: Sparse, homotopy: Sparse, full_size: int, residual_size: int) -> dict[str, int]:
    return {
        "q_squared_defects": len(compose(q, q)),
        "pi_iota_defects": len(linear_combination((Fraction(1), compose(projection, inclusion)), (Fraction(-1), unit(residual_size)))),
        "contraction_defects": len(linear_combination((Fraction(1), compose(inclusion, projection)), (Fraction(-1), unit(full_size)), (Fraction(1), compose(q, homotopy)), (Fraction(1), compose(homotopy, q)))),
        "q_iota_defects": len(compose(q, inclusion)),
        "pi_q_defects": len(compose(projection, q)),
        "homotopy_squared_defects": len(compose(homotopy, homotopy)),
        "homotopy_iota_defects": len(compose(homotopy, inclusion)),
        "pi_homotopy_defects": len(compose(projection, homotopy)),
    }


def expand_once(word: Word) -> list[tuple[Fraction, Word]] | None:
    annihilators = {
        ("qA", "qA"), ("qB", "qB"), ("h", "h"), ("h", "i"),
        ("p", "h"), ("s", "s"), ("s", "j"), ("k", "s"),
        ("qB", "j"), ("k", "qB"),
    }
    rules: dict[tuple[str, str], list[tuple[Fraction, Word]]] = {
        ("p", "i"): [(Fraction(1), ())],
        ("k", "j"): [(Fraction(1), ())],
        ("qA", "i"): [(Fraction(1), ("i", "qB"))],
        ("p", "qA"): [(Fraction(1), ("qB", "p"))],
        ("i", "p"): [(Fraction(1), ()), (Fraction(-1), ("qA", "h")), (Fraction(-1), ("h", "qA"))],
        ("j", "k"): [(Fraction(1), ()), (Fraction(-1), ("qB", "s")), (Fraction(-1), ("s", "qB"))],
    }
    for position in range(len(word) - 1):
        pair = word[position:position + 2]
        if pair in annihilators:
            return []
        if pair in rules:
            return [
                (scale, word[:position] + replacement + word[position + 2:])
                for scale, replacement in rules[pair]
            ]
    return None


def reduce_polynomial(terms: list[tuple[Fraction, Word]]) -> Polynomial:
    pending = list(terms)
    irreducible: Polynomial = {}
    steps = 0
    while pending:
        scale, word = pending.pop()
        if scale == 0:
            continue
        expansion = expand_once(word)
        if expansion is None:
            irreducible[word] = irreducible.get(word, Fraction(0)) + scale
            if irreducible[word] == 0:
                del irreducible[word]
        else:
            pending.extend((scale * factor, replacement) for factor, replacement in expansion)
        steps += 1
        if steps > 10000:
            raise RuntimeError("formal contraction rewrite did not terminate")
    return irreducible


def independently_replay_composition() -> dict[str, int]:
    homotopy_terms = [("h",), ("i", "s", "p")]
    return {
        "composite_pi_iota_rewrite_defects": len(reduce_polynomial([(Fraction(1), ("k", "p", "i", "j")), (Fraction(-1), ())])),
        "composite_contraction_rewrite_defects": len(reduce_polynomial([
            (Fraction(1), ("i", "j", "k", "p")), (Fraction(-1), ()),
            (Fraction(1), ("qA", "h")), (Fraction(1), ("qA", "i", "s", "p")),
            (Fraction(1), ("h", "qA")), (Fraction(1), ("i", "s", "p", "qA")),
        ])),
        "composite_chain_map_rewrite_defects": (
            len(reduce_polynomial([(Fraction(1), ("qA", "i", "j"))]))
            + len(reduce_polynomial([(Fraction(1), ("k", "p", "qA"))]))
        ),
        "composite_homotopy_squared_rewrite_defects": len(reduce_polynomial([
            (Fraction(1), left + right) for left in homotopy_terms for right in homotopy_terms
        ])),
        "composite_homotopy_iota_rewrite_defects": len(reduce_polynomial([
            (Fraction(1), ("h", "i", "j")), (Fraction(1), ("i", "s", "p", "i", "j")),
        ])),
        "composite_pi_homotopy_rewrite_defects": len(reduce_polynomial([
            (Fraction(1), ("k", "p", "h")), (Fraction(1), ("k", "p", "i", "s", "p")),
        ])),
    }


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = [load(path) for path in INPUTS]
    m1a, crosswalk, graph, m3r, dfinite = sources

    schema = load(SCHEMA)
    for error in Draft202012Validator(schema).iter_errors(value):
        errors.append(f"schema:{'/'.join(map(str, error.absolute_path)) or '<root>'}:{error.message}")
    if value.get("result_id") != "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency tags")
    if value.get("repository_base_commit") != "0a17388b4837808fc3f0f2504114ac011e38a17f":
        errors.append("repository base commit")

    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path, source in zip(INPUTS, sources, strict=True):
        relative = str(path.relative_to(ROOT))
        row = provenance.get(relative, {})
        if row.get("sha256") != digest_file(path) or row.get("result_id") != source.get("result_id"):
            errors.append(f"provenance {relative}")
    if m1a.get("claim_flags", {}).get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not True:
        errors.append("M1A prerequisite")
    if graph.get("claim_flags", {}).get("STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED") is not True:
        errors.append("graph prerequisite")
    if m3r.get("claim_flags", {}).get("M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED") is not True:
        errors.append("M3R prerequisite")
    if dfinite.get("claim_flags", {}).get("ALL_EIGHT_SDR_IDENTITIES_INDEPENDENTLY_REPLAYABLE") is not True:
        errors.append("D-finite prerequisite")

    represented_by_energy: dict[int, list[dict[str, Any]]] = {}
    residual_by_energy: dict[int, list[dict[str, Any]]] = {}
    comparison_by_energy: dict[int, list[dict[str, Any]]] = {}
    for row in crosswalk["represented_endpoint_rows"]:
        represented_by_energy.setdefault(row["energy"], []).append(row)
    for row in crosswalk["action_residual_primal_rows"]:
        residual_by_energy.setdefault(row["energy"], []).append(row)
    for row in m3r["ordered_residual_basis"]:
        comparison_by_energy.setdefault(row["energy"], []).append(row)

    expected_blocks: list[dict[str, Any]] = []
    aggregate = {
        "represented_rows": 0, "residual_rows": 0, "q0_nonzero_entries": 0,
        "iota_nonzero_entries": 0, "pi_nonzero_entries": 0,
        "homotopy_nonzero_entries": 0, "q0_cross_partition_defects": 0,
    }
    replay_totals: dict[str, int] = {}
    represented_offset = 0
    residual_offset = 0
    try:
        for source in dfinite["blocks"]:
            energy = source["energy"]
            rows = sorted(represented_by_energy[energy], key=lambda row: row["dfinite_block_index"])
            residual = sorted(residual_by_energy[energy], key=lambda row: row["pair_index"])
            comparison = sorted(comparison_by_energy[energy], key=lambda row: row["global_index"])
            excluded = {
                index
                for sector in source["full_sectors"]
                if sector["name"] in ("antighost", "multiplier")
                for index in range(sector["start"], sector["stop"])
            }
            kept = [index for index in range(source["full_dimension"]) if index not in excluded]
            if kept != [row["dfinite_block_index"] for row in rows]:
                errors.append(f"E{energy} represented index crosswalk")
            if [source["full_basis"][index] for index in kept] != [row["source_label"] for row in rows]:
                errors.append(f"E{energy} represented label crosswalk")
            if [row["dfinite_residual_label"] for row in comparison] != source["residual_basis"]:
                errors.append(f"E{energy} D-finite residual order")
            if [row["represented_residual_label"] for row in comparison] != [row["residual_label"] for row in residual]:
                errors.append(f"E{energy} represented residual order")

            remap = {old: new for new, old in enumerate(kept)}
            q, q_cross, q_duplicates = restrict_square(source["matrices"]["q0"]["entries"], kept, excluded)
            homotopy, s_cross, s_duplicates = restrict_square(source["matrices"]["s_cl"]["entries"], kept, excluded)
            inclusion, i_duplicates = restrict_rectangular(source["matrices"]["iota_cl"]["entries"], remap, None)
            projection, p_duplicates = restrict_rectangular(source["matrices"]["pi_cl"]["entries"], None, remap)
            if q_cross or s_cross:
                errors.append(f"E{energy} cross-partition entries")
            if q_duplicates + s_duplicates + i_duplicates + p_duplicates:
                errors.append(f"E{energy} duplicate sparse entries")
            replay = matrix_defects(q, inclusion, projection, homotopy, len(rows), len(residual))
            if any(replay.values()):
                errors.append(f"E{energy} exact contraction defects {replay}")
            for key, count in replay.items():
                replay_totals[key] = replay_totals.get(key, 0) + count
            matrices = {
                "q0_rep": matrix_record("q0_rep", len(rows), len(rows), q),
                "iota_rep": matrix_record("iota_rep", len(rows), len(residual), inclusion),
                "pi_rep": matrix_record("pi_rep", len(residual), len(rows), projection),
                "s_rep": matrix_record("s_rep", len(rows), len(rows), homotopy),
            }
            expected_blocks.append({
                "energy": energy,
                "represented_range": [represented_offset, represented_offset + len(rows)],
                "residual_range": [residual_offset, residual_offset + len(residual)],
                "source_dfinite_dimension": source["full_dimension"],
                "represented_dimension": len(rows),
                "excluded_test_dimension": len(excluded),
                "residual_dimension": len(residual),
                "represented_basis": [row["source_label"] for row in rows],
                "represented_to_dfinite_indices": kept,
                "residual_basis": [row["residual_label"] for row in residual],
                "matrices": matrices,
                "exact_replay": replay,
            })
            represented_offset += len(rows)
            residual_offset += len(residual)
            aggregate["represented_rows"] += len(rows)
            aggregate["residual_rows"] += len(residual)
            aggregate["q0_nonzero_entries"] += len(q)
            aggregate["iota_nonzero_entries"] += len(inclusion)
            aggregate["pi_nonzero_entries"] += len(projection)
            aggregate["homotopy_nonzero_entries"] += len(homotopy)
            aggregate["q0_cross_partition_defects"] += q_cross
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"represented reconstruction exception:{exc}")

    represented = value.get("represented_contraction", {})
    if represented.get("blocks") != expected_blocks:
        errors.append("represented block payload")
    if represented.get("aggregate") != aggregate:
        errors.append("represented aggregate")
    if represented.get("exact_replay") != replay_totals:
        errors.append("represented aggregate replay")
    if represented.get("sha256") != digest_object(expected_blocks):
        errors.append("represented contraction hash")

    graph_maps = graph["graph_sdr_component_maps"]
    expected_local_maps = {
        name: {
            "map_id": graph_maps[name]["map_id"], "shape": graph_maps[name]["shape"],
            "degree": graph_maps[name]["degree"], "maximum_order": graph_maps[name]["maximum_order"],
            "coefficient_multiindices": graph_maps[name]["coefficient_multiindices"],
            "nonzero_coefficients": graph_maps[name]["nonzero_coefficients"], "sha256": graph_maps[name]["sha256"],
        }
        for name in ("H_alg_graph", "i_end_graph", "p_end_graph", "P_end_graph", "P_alg_graph")
    }
    local_replay_keys = (
        "qH_plus_Hq_defects", "p_graph_i_graph_identity_defects",
        "i_graph_p_graph_equals_P_end_defects", "H_squared_defects",
        "H_i_graph_defects", "p_graph_H_defects",
    )
    expected_local_factor = {
        "maps": expected_local_maps,
        "source_exact_replay": {key: graph["exact_replay"][key] for key in local_replay_keys},
        "source_certificate_sha256": digest_file(GRAPH),
    }
    if value.get("local_graph_factor") != expected_local_factor:
        errors.append("local graph factor")
    if any(expected_local_factor["source_exact_replay"].values()):
        errors.append("local graph source defects")

    expected_nodes = [
        {"id": "LOCAL_GRAPH_BV_BUNDLE", "category": "LOCAL_COMPONENT_JET_BUNDLE", "local_species": 386, "coordinate_dimension": "NOT_A_FINITE_VECTOR_SPACE", "support": "LOCAL_OPERATOR_DOMAIN"},
        {"id": "LOCAL_ENDPOINT_BUNDLE", "category": "LOCAL_COMPONENT_JET_BUNDLE", "local_species": 30, "coordinate_dimension": "NOT_A_FINITE_VECTOR_SPACE", "support": "LOCAL_OPERATOR_DOMAIN"},
        {"id": "GRAPH_BV_SECTIONS_DFINITE", "category": "GLOBAL_DFINITE_GRAPH_SECTIONS", "local_species": 386, "coordinate_dimension": "NOT_SERIALIZED", "support": "ENERGIES_2_THROUGH_6_WITH_ENDPOINT_IMAGE_IN_REPRESENTED_DOMAIN"},
        {"id": "REPRESENTED_ENDPOINT_DFINITE", "category": "REDUCED_MODE_GLOBAL_HARMONIC", "local_species": 30, "coordinate_dimension": 4080, "support": "GLOBAL_DFINITE_ENERGIES_2_THROUGH_6"},
        {"id": "PRIMAL_RESIDUAL_DFINITE", "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY", "local_species": "NOT_APPLICABLE", "coordinate_dimension": 470, "support": "GLOBAL_DFINITE_ENERGIES_2_THROUGH_6"},
    ]
    expected_arrows = [
        {"id": "p_end_graph_local", "source": "LOCAL_GRAPH_BV_BUNDLE", "target": "LOCAL_ENDPOINT_BUNDLE", "kind": "FINITE_ORDER_LOCAL_DIFFERENTIAL_OPERATOR", "source_hash": expected_local_maps["p_end_graph"]["sha256"]},
        {"id": "i_end_graph_local", "source": "LOCAL_ENDPOINT_BUNDLE", "target": "LOCAL_GRAPH_BV_BUNDLE", "kind": "FINITE_ORDER_LOCAL_DIFFERENTIAL_OPERATOR", "source_hash": expected_local_maps["i_end_graph"]["sha256"]},
        {"id": "p_end_graph_[2,6]", "source": "GRAPH_BV_SECTIONS_DFINITE", "target": "REPRESENTED_ENDPOINT_DFINITE", "kind": "DFINITE_REALIZATION_OF_LOCAL_OPERATOR_FOLLOWED_BY_DECLARED_HARMONIC_COORDINATIZATION", "source_hash": digest_object([expected_local_maps["p_end_graph"]["sha256"], m3r["comparison"]["sha256"]])},
        {"id": "pi_rep", "source": "REPRESENTED_ENDPOINT_DFINITE", "target": "PRIMAL_RESIDUAL_DFINITE", "kind": "EXACT_FINITE_SPARSE_MAP", "source_hash": digest_object([block["matrices"]["pi_rep"]["sha256"] for block in expected_blocks])},
        {"id": "iota_rep", "source": "PRIMAL_RESIDUAL_DFINITE", "target": "REPRESENTED_ENDPOINT_DFINITE", "kind": "EXACT_FINITE_SPARSE_MAP", "source_hash": digest_object([block["matrices"]["iota_rep"]["sha256"] for block in expected_blocks])},
        {"id": "i_end_graph_[2,6]", "source": "REPRESENTED_ENDPOINT_DFINITE", "target": "GRAPH_BV_SECTIONS_DFINITE", "kind": "DFINITE_REALIZATION_OF_LOCAL_OPERATOR", "source_hash": expected_local_maps["i_end_graph"]["sha256"]},
    ]
    expected_formula = {
        "projection": "pi_comp=pi_rep o rho_[2,6] o p_end_graph",
        "inclusion": "iota_comp=i_end_graph o iota_rep",
        "homotopy": "s_comp=H_alg_graph+i_end_graph o s_rep o rho_[2,6] o p_end_graph",
        "contraction": "iota_comp o pi_comp=1-q_graph o s_comp-s_comp o q_graph",
        "normalization": ["pi_comp o iota_comp=1_res", "s_comp^2=0", "s_comp o iota_comp=0", "pi_comp o s_comp=0"],
        "composition_lemma": "composition of the normalized local graph-to-endpoint contraction with the normalized represented endpoint-to-residual contraction",
    }
    expected_dag = {
        "nodes": expected_nodes, "arrows": expected_arrows, "formula": expected_formula,
        "sha256": digest_object({"nodes": expected_nodes, "arrows": expected_arrows, "formula": expected_formula}),
    }
    if value.get("typed_operator_dag") != expected_dag:
        errors.append("typed operator DAG")

    expected_actions = [{
        "residual_index": row["residual_index"],
        "residual_label": row["residual_label"],
        "represented_endpoint_index": row["source_represented_endpoint_index"],
        "represented_endpoint_label": row["source_coordinate_label"],
        "endpoint_inclusion_action": f"iota_rep({row['residual_label']})={row['source_coordinate_label']}",
        "graph_inclusion_action": f"iota_comp({row['residual_label']})=i_end_graph({row['metric_preimage_name']})",
        "graph_projection_functional": f"pi_comp(Phi)[{row['residual_label']}]=coeff[{row['source_coordinate_label']}](rho_[2,6](p_end_graph(Phi)))",
    } for row in crosswalk["action_residual_primal_rows"]]
    if value.get("residual_coordinate_actions") != expected_actions:
        errors.append("residual coordinate actions")

    expected_obligations = {
        "local_factor": {
            "q_squared_zero": graph["formal_transport_replay"]["graph_q1_squared_zero"],
            "inclusion_chain_map": graph["formal_transport_replay"]["graph_inclusion_chain_map"],
            "projection_chain_map": graph["formal_transport_replay"]["graph_projection_chain_map"],
            "p_i_identity_defects": graph["exact_replay"]["p_graph_i_graph_identity_defects"],
            "i_p_contraction_defects": graph["exact_replay"]["i_graph_p_graph_equals_P_end_defects"] + graph["exact_replay"]["qH_plus_Hq_defects"],
            "H_squared_defects": graph["exact_replay"]["H_squared_defects"],
            "H_i_defects": graph["exact_replay"]["H_i_graph_defects"],
            "p_H_defects": graph["exact_replay"]["p_graph_H_defects"],
        },
        "represented_factor": replay_totals,
        "domain_gluing": {
            "energy_blocks": 5, "represented_endpoint_rows": 4080,
            "cross_partition_q0_defects": 0,
            "harmonic_restriction_is_identity_on_declared_endpoint_domain": True,
            "arbitrary_smooth_domain_claimed": False,
        },
    }
    if value.get("composition_obligations") != expected_obligations:
        errors.append("composition obligations")
    local_obligations = expected_obligations["local_factor"]
    if not all(local_obligations[key] is True for key in ("q_squared_zero", "inclusion_chain_map", "projection_chain_map")):
        errors.append("local factor Boolean obligations")
    if any(local_obligations[key] for key in local_obligations if key.endswith("defects")):
        errors.append("local factor algebraic obligations")

    symbolic = independently_replay_composition()
    expected_formal = {
        "typed_source_target_defects": 0,
        "factor_chain_map_defects": 0,
        "factor_normalization_defects": 0,
        **symbolic,
    }
    if value.get("formal_composition_replay") != expected_formal:
        errors.append("formal composition replay")
    if any(expected_formal.values()):
        errors.append(f"independent formal composition defects {expected_formal}")

    flags = value.get("claim_flags", {})
    for flag in (
        "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE",
        "REPRESENTED_4080_TO_470_NORMALIZED_CONTRACTION_COMPLETE",
        "TYPED_386_THROUGH_30_TO_470_OPERATOR_DAG_COMPLETE",
        "GRAPH_TO_ENDPOINT_FACTOR_SUPPORT_LOCAL",
    ):
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in (
        "HARMONIC_RESTRICTION_SUPPORT_LOCAL", "RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED",
        "M1B_ACTION_DUAL_LIFT_COMPLETE", "M1B_TYPED_CYCLIC_REPLAY_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
        "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    if value.get("scope", {}).get("domain") != "D-finite represented sections of the authoritative 386-row graph carrier":
        errors.append("declared represented domain")
    if value.get("foundational_strength", {}).get("choice_principle_used") is not False:
        errors.append("choice boundary")

    content_keys = (
        "typed_operator_dag", "local_graph_factor", "represented_contraction",
        "residual_coordinate_actions", "composition_obligations", "formal_composition_replay",
    )
    if value.get("content_sha256") != digest_object({key: value.get(key) for key in content_keys}):
        errors.append("content hash")
    if value.get("independent_checker") != str(Path(__file__).relative_to(ROOT)):
        errors.append("independent checker path")
    if value.get("human_report") != str(REPORT.relative_to(ROOT)) or not REPORT.is_file():
        errors.append("human report path")
    elif not all(token in REPORT.read_text(encoding="utf-8") for token in ("4,080", "470", "typed operator DAG", "support-expanding", "action-derived compact-source dual", "Gate A", "Hadamard")):
        errors.append("human report boundary")
    return errors


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1: PASS")
    print("  - independently reconstructed five exact represented contraction blocks (4,080 -> 470)")
    print("  - independently replayed the normalized composite-contraction lemma")
    print("  - action dual, cyclic replay, M1C, Gate A and Hadamard remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
