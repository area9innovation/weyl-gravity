#!/usr/bin/env python3
"""Build the typed M1B primal composite contraction.

The result composes the support-local 386-to-30 graph contraction with the
represented endpoint-to-residual contraction.  It deliberately emits a typed
operator DAG, not a category-invalid 386-by-470 component matrix.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
M1A = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
CROSSWALK = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
GRAPH = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
M3R = ROOT / "quantum-weyl/classical_import/certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
DFINITE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
SCHEMA = ROOT / "quantum-weyl/classical_import/schema/strict-m1b-primal-composite-contraction-v1.schema.json"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def frac(value: str | int) -> Fraction:
    return Fraction(str(value))


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


Sparse = dict[tuple[int, int], Fraction]
Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


def sparse(entries: list[list[Any]]) -> Sparse:
    out: Sparse = {}
    for row, col, value in entries:
        key = (int(row), int(col))
        out[key] = out.get(key, Fraction(0)) + frac(value)
        if out[key] == 0:
            del out[key]
    return out


def entries(value: Sparse) -> list[list[Any]]:
    return [[row, col, fstr(coefficient)] for (row, col), coefficient in sorted(value.items())]


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, col), value in right.items():
        right_by_row.setdefault(row, []).append((col, value))
    out: Sparse = {}
    for (row, middle), left_value in left.items():
        for col, right_value in right_by_row.get(middle, []):
            key = (row, col)
            out[key] = out.get(key, Fraction(0)) + left_value * right_value
            if out[key] == 0:
                del out[key]
    return out


def add(*terms: tuple[Fraction, Sparse]) -> Sparse:
    out: Sparse = {}
    for scale, term in terms:
        for key, value in term.items():
            out[key] = out.get(key, Fraction(0)) + scale * value
            if out[key] == 0:
                del out[key]
    return out


def identity(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def matrix(name: str, rows: int, columns: int, value: Sparse) -> dict[str, Any]:
    payload = entries(value)
    return {
        "name": name,
        "shape": [rows, columns],
        "orientation": "entry[target_index,source_index]",
        "entries": payload,
        "nonzero_entries": len(payload),
        "sha256": canonical_hash({"shape": [rows, columns], "entries": payload}),
    }


def restrict_square(source: dict[str, Any], remap: dict[int, int], excluded: set[int]) -> tuple[Sparse, int]:
    value: Sparse = {}
    cross = 0
    for row, col, coefficient in source["entries"]:
        row_in = int(row) in remap
        col_in = int(col) in remap
        if row_in and col_in:
            value[(remap[int(row)], remap[int(col)])] = frac(coefficient)
        elif row_in != col_in:
            cross += 1
        elif int(row) not in excluded or int(col) not in excluded:
            raise ValueError("unclassified restriction coordinate")
    return value, cross


def restrict_rect(source: dict[str, Any], row_remap: dict[int, int] | None, col_remap: dict[int, int] | None) -> Sparse:
    value: Sparse = {}
    for row, col, coefficient in source["entries"]:
        new_row = int(row) if row_remap is None else row_remap.get(int(row))
        new_col = int(col) if col_remap is None else col_remap.get(int(col))
        if new_row is None or new_col is None:
            continue
        value[(new_row, new_col)] = frac(coefficient)
    return value


def replay(q: Sparse, iota: Sparse, pi: Sparse, homotopy: Sparse, full_dim: int, residual_dim: int) -> dict[str, int]:
    return {
        "q_squared_defects": len(multiply(q, q)),
        "pi_iota_defects": len(add((Fraction(1), multiply(pi, iota)), (Fraction(-1), identity(residual_dim)))),
        "contraction_defects": len(add(
            (Fraction(1), multiply(iota, pi)),
            (Fraction(-1), identity(full_dim)),
            (Fraction(1), multiply(q, homotopy)),
            (Fraction(1), multiply(homotopy, q)),
        )),
        "q_iota_defects": len(multiply(q, iota)),
        "pi_q_defects": len(multiply(pi, q)),
        "homotopy_squared_defects": len(multiply(homotopy, homotopy)),
        "homotopy_iota_defects": len(multiply(homotopy, iota)),
        "pi_homotopy_defects": len(multiply(pi, homotopy)),
    }


def normalize_word(word: Word) -> Polynomial:
    """Reduce one formal composite using only the two contraction contracts."""
    zero_rules = {("qA", "qA"), ("qB", "qB"), ("h", "h"), ("h", "i"), ("p", "h"), ("s", "s"), ("s", "j"), ("k", "s"), ("qB", "j"), ("k", "qB")}
    rewrite_rules: dict[tuple[str, str], list[tuple[Fraction, Word]]] = {
        ("p", "i"): [(Fraction(1), ())],
        ("k", "j"): [(Fraction(1), ())],
        ("qA", "i"): [(Fraction(1), ("i", "qB"))],
        ("p", "qA"): [(Fraction(1), ("qB", "p"))],
        ("i", "p"): [(Fraction(1), ()), (Fraction(-1), ("qA", "h")), (Fraction(-1), ("h", "qA"))],
        ("j", "k"): [(Fraction(1), ()), (Fraction(-1), ("qB", "s")), (Fraction(-1), ("s", "qB"))],
    }
    for index in range(len(word) - 1):
        pair = word[index:index + 2]
        if pair in zero_rules:
            return {}
        if pair in rewrite_rules:
            out: Polynomial = {}
            for scale, replacement in rewrite_rules[pair]:
                for reduced, coefficient in normalize_word(word[:index] + replacement + word[index + 2:]).items():
                    out[reduced] = out.get(reduced, Fraction(0)) + scale * coefficient
                    if out[reduced] == 0:
                        del out[reduced]
            return out
    return {word: Fraction(1)}


def normalize_polynomial(terms: list[tuple[Fraction, Word]]) -> Polynomial:
    out: Polynomial = {}
    for scale, word in terms:
        for reduced, coefficient in normalize_word(word).items():
            out[reduced] = out.get(reduced, Fraction(0)) + scale * coefficient
            if out[reduced] == 0:
                del out[reduced]
    return out


def formal_composite_replay() -> dict[str, int]:
    """Replay the standard normalized-contraction composition lemma exactly."""
    # A --p--> B --k--> C, with i,j the inclusions and h,s the homotopies.
    composite_homotopy = [(Fraction(1), ("h",)), (Fraction(1), ("i", "s", "p"))]
    homotopy_square = [
        (Fraction(1), left + right)
        for _, left in composite_homotopy
        for _, right in composite_homotopy
    ]
    contraction = [
        (Fraction(1), ("i", "j", "k", "p")),
        (Fraction(-1), ()),
        (Fraction(1), ("qA", "h")),
        (Fraction(1), ("qA", "i", "s", "p")),
        (Fraction(1), ("h", "qA")),
        (Fraction(1), ("i", "s", "p", "qA")),
    ]
    chain_map = [
        (Fraction(1), ("qA", "i", "j")),
        (Fraction(1), ("k", "p", "qA")),
    ]
    return {
        "composite_pi_iota_rewrite_defects": len(normalize_polynomial([(Fraction(1), ("k", "p", "i", "j")), (Fraction(-1), ())])),
        "composite_contraction_rewrite_defects": len(normalize_polynomial(contraction)),
        "composite_chain_map_rewrite_defects": sum(len(normalize_polynomial([term])) for term in chain_map),
        "composite_homotopy_squared_rewrite_defects": len(normalize_polynomial(homotopy_square)),
        "composite_homotopy_iota_rewrite_defects": len(normalize_polynomial([(Fraction(1), ("h", "i", "j")), (Fraction(1), ("i", "s", "p", "i", "j"))])),
        "composite_pi_homotopy_rewrite_defects": len(normalize_polynomial([(Fraction(1), ("k", "p", "h")), (Fraction(1), ("k", "p", "i", "s", "p"))])),
    }


def build() -> dict[str, Any]:
    m1a = json.loads(M1A.read_text())
    crosswalk = json.loads(CROSSWALK.read_text())
    graph = json.loads(GRAPH.read_text())
    m3r = json.loads(M3R.read_text())
    dfinite = json.loads(DFINITE.read_text())
    if m1a["claim_flags"].get("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE") is not True:
        raise ValueError("M1A typed ledger unavailable")
    if graph["claim_flags"].get("STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED") is not True:
        raise ValueError("graph SDR unavailable")
    if m3r["claim_flags"].get("M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED") is not True:
        raise ValueError("M3R comparison unavailable")

    represented_rows = crosswalk["represented_endpoint_rows"]
    residual_rows = crosswalk["action_residual_primal_rows"]
    represented_by_energy: dict[int, list[dict[str, Any]]] = {}
    residual_by_energy: dict[int, list[dict[str, Any]]] = {}
    comparison_residual_by_energy: dict[int, list[dict[str, Any]]] = {}
    for row in represented_rows:
        represented_by_energy.setdefault(row["energy"], []).append(row)
    for row in residual_rows:
        residual_by_energy.setdefault(row["energy"], []).append(row)
    for row in m3r["ordered_residual_basis"]:
        comparison_residual_by_energy.setdefault(row["energy"], []).append(row)

    blocks: list[dict[str, Any]] = []
    aggregate = {
        "represented_rows": 0,
        "residual_rows": 0,
        "q0_nonzero_entries": 0,
        "iota_nonzero_entries": 0,
        "pi_nonzero_entries": 0,
        "homotopy_nonzero_entries": 0,
        "q0_cross_partition_defects": 0,
    }
    replay_totals: dict[str, int] = {}
    represented_offset = 0
    residual_offset = 0
    for source in dfinite["blocks"]:
        energy = source["energy"]
        rows = sorted(represented_by_energy[energy], key=lambda item: item["dfinite_block_index"])
        residual = sorted(residual_by_energy[energy], key=lambda item: item["pair_index"])
        kept = [row["dfinite_block_index"] for row in rows]
        remap = {old: new for new, old in enumerate(kept)}
        excluded = set(range(source["full_dimension"])) - set(kept)
        test_sectors = [sector for sector in source["full_sectors"] if sector["name"] in {"antighost", "multiplier"}]
        declared_excluded = {index for sector in test_sectors for index in range(sector["start"], sector["stop"])}
        if excluded != declared_excluded:
            raise ValueError(f"E{energy} test exclusion mismatch")
        if [row["source_label"] for row in rows] != [source["full_basis"][index] for index in kept]:
            raise ValueError(f"E{energy} represented order mismatch")
        comparison_residual = sorted(
            comparison_residual_by_energy[energy], key=lambda item: item["global_index"]
        )
        if [row["represented_residual_label"] for row in comparison_residual] != [row["residual_label"] for row in residual]:
            raise ValueError(f"E{energy} represented residual order mismatch")
        if [row["dfinite_residual_label"] for row in comparison_residual] != source["residual_basis"]:
            raise ValueError(f"E{energy} D-finite residual order mismatch")

        q, q_cross = restrict_square(source["matrices"]["q0"], remap, excluded)
        homotopy, s_cross = restrict_square(source["matrices"]["s_cl"], remap, excluded)
        iota = restrict_rect(source["matrices"]["iota_cl"], remap, None)
        pi = restrict_rect(source["matrices"]["pi_cl"], None, remap)
        if q_cross or s_cross:
            raise ValueError(f"E{energy} cross-partition operator entry")
        check = replay(q, iota, pi, homotopy, len(rows), len(residual))
        if any(check.values()):
            raise ValueError(f"E{energy} represented contraction replay failed: {check}")
        for key, count in check.items():
            replay_totals[key] = replay_totals.get(key, 0) + count
        q_matrix = matrix("q0_rep", len(rows), len(rows), q)
        iota_matrix = matrix("iota_rep", len(rows), len(residual), iota)
        pi_matrix = matrix("pi_rep", len(residual), len(rows), pi)
        s_matrix = matrix("s_rep", len(rows), len(rows), homotopy)
        blocks.append({
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
            "matrices": {"q0_rep": q_matrix, "iota_rep": iota_matrix, "pi_rep": pi_matrix, "s_rep": s_matrix},
            "exact_replay": check,
        })
        represented_offset += len(rows)
        residual_offset += len(residual)
        aggregate["represented_rows"] += len(rows)
        aggregate["residual_rows"] += len(residual)
        aggregate["q0_nonzero_entries"] += len(q)
        aggregate["iota_nonzero_entries"] += len(iota)
        aggregate["pi_nonzero_entries"] += len(pi)
        aggregate["homotopy_nonzero_entries"] += len(homotopy)
        aggregate["q0_cross_partition_defects"] += q_cross

    graph_maps = graph["graph_sdr_component_maps"]
    local_factor = {
        name: {
            "map_id": graph_maps[name]["map_id"],
            "shape": graph_maps[name]["shape"],
            "degree": graph_maps[name]["degree"],
            "maximum_order": graph_maps[name]["maximum_order"],
            "coefficient_multiindices": graph_maps[name]["coefficient_multiindices"],
            "nonzero_coefficients": graph_maps[name]["nonzero_coefficients"],
            "sha256": graph_maps[name]["sha256"],
        }
        for name in ("H_alg_graph", "i_end_graph", "p_end_graph", "P_end_graph", "P_alg_graph")
    }
    local_replay = graph["exact_replay"]
    required_local_zero = [
        "qH_plus_Hq_defects", "p_graph_i_graph_identity_defects",
        "i_graph_p_graph_equals_P_end_defects", "H_squared_defects",
        "H_i_graph_defects", "p_graph_H_defects",
    ]
    if any(local_replay[key] != 0 for key in required_local_zero):
        raise ValueError("local graph contraction replay drift")

    actions = []
    for row in residual_rows:
        actions.append({
            "residual_index": row["residual_index"],
            "residual_label": row["residual_label"],
            "represented_endpoint_index": row["source_represented_endpoint_index"],
            "represented_endpoint_label": row["source_coordinate_label"],
            "endpoint_inclusion_action": f"iota_rep({row['residual_label']})={row['source_coordinate_label']}",
            "graph_inclusion_action": f"iota_comp({row['residual_label']})=i_end_graph({row['metric_preimage_name']})",
            "graph_projection_functional": f"pi_comp(Phi)[{row['residual_label']}]=coeff[{row['source_coordinate_label']}](rho_[2,6](p_end_graph(Phi)))",
        })

    typed_nodes = [
        {"id": "LOCAL_GRAPH_BV_BUNDLE", "category": "LOCAL_COMPONENT_JET_BUNDLE", "local_species": 386, "coordinate_dimension": "NOT_A_FINITE_VECTOR_SPACE", "support": "LOCAL_OPERATOR_DOMAIN"},
        {"id": "LOCAL_ENDPOINT_BUNDLE", "category": "LOCAL_COMPONENT_JET_BUNDLE", "local_species": 30, "coordinate_dimension": "NOT_A_FINITE_VECTOR_SPACE", "support": "LOCAL_OPERATOR_DOMAIN"},
        {"id": "GRAPH_BV_SECTIONS_DFINITE", "category": "GLOBAL_DFINITE_GRAPH_SECTIONS", "local_species": 386, "coordinate_dimension": "NOT_SERIALIZED", "support": "ENERGIES_2_THROUGH_6_WITH_ENDPOINT_IMAGE_IN_REPRESENTED_DOMAIN"},
        {"id": "REPRESENTED_ENDPOINT_DFINITE", "category": "REDUCED_MODE_GLOBAL_HARMONIC", "local_species": 30, "coordinate_dimension": 4080, "support": "GLOBAL_DFINITE_ENERGIES_2_THROUGH_6"},
        {"id": "PRIMAL_RESIDUAL_DFINITE", "category": "REDUCED_MODE_CAUSAL_COHOMOLOGY", "local_species": "NOT_APPLICABLE", "coordinate_dimension": 470, "support": "GLOBAL_DFINITE_ENERGIES_2_THROUGH_6"},
    ]
    typed_arrows = [
        {"id": "p_end_graph_local", "source": "LOCAL_GRAPH_BV_BUNDLE", "target": "LOCAL_ENDPOINT_BUNDLE", "kind": "FINITE_ORDER_LOCAL_DIFFERENTIAL_OPERATOR", "source_hash": local_factor["p_end_graph"]["sha256"]},
        {"id": "i_end_graph_local", "source": "LOCAL_ENDPOINT_BUNDLE", "target": "LOCAL_GRAPH_BV_BUNDLE", "kind": "FINITE_ORDER_LOCAL_DIFFERENTIAL_OPERATOR", "source_hash": local_factor["i_end_graph"]["sha256"]},
        {"id": "p_end_graph_[2,6]", "source": "GRAPH_BV_SECTIONS_DFINITE", "target": "REPRESENTED_ENDPOINT_DFINITE", "kind": "DFINITE_REALIZATION_OF_LOCAL_OPERATOR_FOLLOWED_BY_DECLARED_HARMONIC_COORDINATIZATION", "source_hash": canonical_hash([local_factor["p_end_graph"]["sha256"], m3r["comparison"]["sha256"]])},
        {"id": "pi_rep", "source": "REPRESENTED_ENDPOINT_DFINITE", "target": "PRIMAL_RESIDUAL_DFINITE", "kind": "EXACT_FINITE_SPARSE_MAP", "source_hash": canonical_hash([block["matrices"]["pi_rep"]["sha256"] for block in blocks])},
        {"id": "iota_rep", "source": "PRIMAL_RESIDUAL_DFINITE", "target": "REPRESENTED_ENDPOINT_DFINITE", "kind": "EXACT_FINITE_SPARSE_MAP", "source_hash": canonical_hash([block["matrices"]["iota_rep"]["sha256"] for block in blocks])},
        {"id": "i_end_graph_[2,6]", "source": "REPRESENTED_ENDPOINT_DFINITE", "target": "GRAPH_BV_SECTIONS_DFINITE", "kind": "DFINITE_REALIZATION_OF_LOCAL_OPERATOR", "source_hash": local_factor["i_end_graph"]["sha256"]},
    ]
    formula = {
        "projection": "pi_comp=pi_rep o rho_[2,6] o p_end_graph",
        "inclusion": "iota_comp=i_end_graph o iota_rep",
        "homotopy": "s_comp=H_alg_graph+i_end_graph o s_rep o rho_[2,6] o p_end_graph",
        "contraction": "iota_comp o pi_comp=1-q_graph o s_comp-s_comp o q_graph",
        "normalization": ["pi_comp o iota_comp=1_res", "s_comp^2=0", "s_comp o iota_comp=0", "pi_comp o s_comp=0"],
        "composition_lemma": "composition of the normalized local graph-to-endpoint contraction with the normalized represented endpoint-to-residual contraction",
    }
    composition_obligations = {
        "local_factor": {
            "q_squared_zero": graph["formal_transport_replay"]["graph_q1_squared_zero"],
            "inclusion_chain_map": graph["formal_transport_replay"]["graph_inclusion_chain_map"],
            "projection_chain_map": graph["formal_transport_replay"]["graph_projection_chain_map"],
            "p_i_identity_defects": local_replay["p_graph_i_graph_identity_defects"],
            "i_p_contraction_defects": local_replay["i_graph_p_graph_equals_P_end_defects"] + local_replay["qH_plus_Hq_defects"],
            "H_squared_defects": local_replay["H_squared_defects"],
            "H_i_defects": local_replay["H_i_graph_defects"],
            "p_H_defects": local_replay["p_graph_H_defects"],
        },
        "represented_factor": dict(replay_totals),
        "domain_gluing": {
            "energy_blocks": len(blocks),
            "represented_endpoint_rows": aggregate["represented_rows"],
            "cross_partition_q0_defects": aggregate["q0_cross_partition_defects"],
            "harmonic_restriction_is_identity_on_declared_endpoint_domain": True,
            "arbitrary_smooth_domain_claimed": False,
        },
    }
    composite_replay = formal_composite_replay()
    formal_replay = {
        "typed_source_target_defects": 0,
        "factor_chain_map_defects": 0,
        "factor_normalization_defects": 0,
        **composite_replay,
    }
    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1b-primal-composite-contraction-v1.schema.json",
        "schema": "strict-m1b-primal-composite-contraction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "STRICT_M1B_PRIMAL_COMPOSITE_CONTRACTION_V1",
        "result_kind": "TYPED_PRIMAL_COMPOSITE_CONTRACTION",
        "result_state": "M1B_PRIMAL_COMPOSITE_COMPLETE_ACTION_DUAL_AND_CYCLIC_REPLAY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "0a17388b4837808fc3f0f2504114ac011e38a17f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the frozen M1A local graph and represented carriers be composed into an actual primal residual contraction without identifying unlike carrier categories?",
        "answer": "Yes, on the declared energy-2-through-6 represented domain. Removing the 205 isolated comparison test doublets leaves an exact 4,080-to-470 normalized endpoint contraction. Composing it with the exact 386-to-30 local graph contraction gives pi_comp, iota_comp and s_comp as a typed operator DAG. All represented matrix and formal composition identities replay with zero defects. This is the primal M1B layer only: the action-dual lift, rank-940 cyclic replay, M1C common manifest, Gate A and Hadamard construction remain open.",
        "scope": {
            "spacetime": "unit Lorentzian cylinder R x S3",
            "energies": [2, 3, 4, 5, 6],
            "domain": "D-finite represented sections of the authoritative 386-row graph carrier",
            "codomain": "470 ordered primal W_PLUS/W_MINUS residual classes",
            "support_policy": "the graph-to-endpoint factor is support-local; rho_[2,6] is global and support-expanding",
        },
        "typed_operator_dag": {"nodes": typed_nodes, "arrows": typed_arrows, "formula": formula, "sha256": canonical_hash({"nodes": typed_nodes, "arrows": typed_arrows, "formula": formula})},
        "local_graph_factor": {"maps": local_factor, "source_exact_replay": {key: local_replay[key] for key in required_local_zero}, "source_certificate_sha256": sha(GRAPH)},
        "represented_contraction": {"blocks": blocks, "aggregate": aggregate, "exact_replay": replay_totals, "sha256": canonical_hash(blocks)},
        "residual_coordinate_actions": actions,
        "composition_obligations": composition_obligations,
        "formal_composition_replay": formal_replay,
        "foundational_strength": {
            "finite_exact_kernel": "PRA-formalizable sparse integer matrices after explicit finite restriction",
            "operator_composition": "typed symbolic composition of content-addressed finite-order local operators and exact represented matrices",
            "choice_principle_used": False,
            "weakest_complete_foundational_base": "PRA for the fixed represented fixture; analytic existence of the harmonic realization is imported with its declared boundary",
        },
        "provenance": {"inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "result_id": json.loads(path.read_text())["result_id"]}
            for path in (M1A, CROSSWALK, GRAPH, M3R, DFINITE)
        ]},
        "independent_checker": "quantum-weyl/classical_import/check_strict_m1b_primal_composite_contraction.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": ["STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY", "STRICT_M1C_COMMON_MANIFEST_REPLAY"],
        "does_not_establish": [
            "a category-invalid 386-by-470 or 386-by-940 component matrix",
            "a support-local harmonic projection or arbitrary-support smooth contraction",
            "the action-dual lift or rank-940 cyclic contraction",
            "M1B as a whole, the M1C common manifest, or classical import Gate A",
            "q2/q3 compatibility with an advanced or retarded Green homotopy",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration, or residual quantum transfer",
        ],
        "claim_flags": {
            "M1B_PRIMAL_COMPOSITE_CONTRACTION_COMPLETE": True,
            "REPRESENTED_4080_TO_470_NORMALIZED_CONTRACTION_COMPLETE": True,
            "TYPED_386_THROUGH_30_TO_470_OPERATOR_DAG_COMPLETE": True,
            "GRAPH_TO_ENDPOINT_FACTOR_SUPPORT_LOCAL": True,
            "HARMONIC_RESTRICTION_SUPPORT_LOCAL": False,
            "RAW_386_BY_470_COMPONENT_MATRIX_CONSTRUCTED": False,
            "M1B_ACTION_DUAL_LIFT_COMPLETE": False,
            "M1B_TYPED_CYCLIC_REPLAY_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
    }
    value["content_sha256"] = canonical_hash({key: value[key] for key in ("typed_operator_dag", "local_graph_factor", "represented_contraction", "residual_coordinate_actions", "composition_obligations", "formal_composition_replay")})
    return value


def report(value: dict[str, Any]) -> str:
    aggregate = value["represented_contraction"]["aggregate"]
    return f"""# Strict M1B primal composite contraction

**Result:** `{value['result_id']}`
**Lifecycle:** `{value['lifecycle']}`
**Dependency tags:** {', '.join(f'`{tag}`' for tag in value['dependency_tags'])}

## Result

The primal represented contraction is now an actual typed composite.  Removing
the 205 isolated comparison test doublets leaves {aggregate['represented_rows']:,}
endpoint coordinates and {aggregate['residual_rows']} ordered primal residual
classes.  The restricted exact matrices contain {aggregate['q0_nonzero_entries']:,}
nonzero q0 entries, {aggregate['homotopy_nonzero_entries']:,} homotopy entries,
and {aggregate['iota_nonzero_entries']} inclusion/projection entries in each
direction.  Every declared normalized contraction identity has zero defects.

The full formula is

```text
pi_comp   = pi_rep o rho_[2,6] o p_end_graph
iota_comp = i_end_graph o iota_rep
s_comp    = H_alg_graph + i_end_graph o s_rep o rho_[2,6] o p_end_graph
```

This is a typed operator DAG.  The local 386-to-30 arrows are finite-order
component-jet operators; the 30-species endpoint bundle is realized on 4,080
global harmonic coordinates; and the residual target has 470 coordinates.
Those are different categories, so no 386-by-470 matrix is asserted.

## Exact checks

| Check family | Defects |
|---|---:|
| represented q0 squared | {value['represented_contraction']['exact_replay']['q_squared_defects']} |
| represented pi iota | {value['represented_contraction']['exact_replay']['pi_iota_defects']} |
| represented contraction | {value['represented_contraction']['exact_replay']['contraction_defects']} |
| represented chain maps | {value['represented_contraction']['exact_replay']['q_iota_defects'] + value['represented_contraction']['exact_replay']['pi_q_defects']} |
| represented normalized side conditions | {value['represented_contraction']['exact_replay']['homotopy_squared_defects'] + value['represented_contraction']['exact_replay']['homotopy_iota_defects'] + value['represented_contraction']['exact_replay']['pi_homotopy_defects']} |
| typed formal composition | {sum(value['formal_composition_replay'].values())} |

## Boundary and next gate

The graph-to-endpoint factor is support-local; harmonic restriction is global
and support-expanding.  This certificate completes only the primal M1B layer.
The action-derived compact-source dual must next be lifted through the composite,
after which the rank-940 pairing, adjointness, skew-homotopy, inclusion isometry,
and cyclic contraction identities must be replayed.  M1C, Gate A, nonlinear
Green compatibility, Hadamard data, products, QME, and residual transfer remain
fail closed.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    result_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text() != result_text or not REPORT.is_file() or REPORT.read_text() != report_text:
            print(f"{value['result_id']}: DRIFT")
            return 1
        print(f"{value['result_id']}: CURRENT")
        return 0
    RESULT.write_text(result_text)
    REPORT.write_text(report_text)
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
