#!/usr/bin/env python3
"""Build the M1A3 represented-carrier and action-residual crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.md"

GRADING = HERE / "certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
LOCAL_EXTENSION = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPRESENTED = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
RESIDUAL_CYCLICITY = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"

INPUTS = (
    (GRADING, "STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1", "M1A namespaced grading contract and typed local endpoint rows"),
    (LOCAL_EXTENSION, "STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1", "completed semantics for the other 356 local rows"),
    (DFINITE, "STRICT_DFINITE_RESIDUAL_SDR_V1", "ordered 4,490-coordinate finite harmonic comparison"),
    (REPRESENTED, "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1", "ordered 470-mode analysis/synthesis crosswalk"),
    (ACTION_DUAL, "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1", "compact-source action-dual dictionary"),
    (RESIDUAL_CYCLICITY, "STRICT_TYPED_RESIDUAL_CYCLICITY_V1", "rank-940 shifted-cotangent residual typing"),
)

SECTOR_TO_SPECIES = {
    "diff_ghost": "xi",
    "weyl_ghost": "omega",
    "metric_trace": "g",
    "metric_tf": "g",
    "metric_antifield": "g_star",
    "diff_ghost_antifield": "xi_star",
    "trace_antifield": "g_star",
    "weyl_ghost_antifield": "omega_star",
}
TEST_SECTORS = {"antighost", "multiplier"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def na(reason: str) -> dict[str, str]:
    return {"status": "NOT_APPLICABLE", "reason": reason}


def local_species_rows(grading: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in grading["local_endpoint_typed_rows"]:
        species = row["authority"]["generator"].rsplit("/", 1)[-1]
        grouped.setdefault(species, []).append(row)
    expected = {"xi": 4, "omega": 1, "g": 10, "g_star": 10, "xi_star": 4, "omega_star": 1}
    if {key: len(value) for key, value in grouped.items()} != expected:
        raise ValueError("local endpoint species partition drift")
    return grouped


def uniform_species_semantics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fields = (
        "role", "bv_ghost_number", "chain_degree", "antifield_number", "form_degree",
        "Grassmann_parity", "mass_dimension", "Weyl_weight", "intrinsic_jet_order_bound",
    )
    result = {field: rows[0][field] for field in fields}
    if any(any(row[field] != result[field] for field in fields) for row in rows):
        raise ValueError(f"nonuniform local species semantics: {rows[0]['row_id']}")
    return result


def build() -> dict[str, Any]:
    source = {path: load(path) for path, _, _ in INPUTS}
    for path, expected_id, _ in INPUTS:
        if source[path].get("result_id") != expected_id:
            raise ValueError(f"dependency identity drift: {path}")

    grading = source[GRADING]
    local_extension = source[LOCAL_EXTENSION]
    dfinite = source[DFINITE]
    represented = source[REPRESENTED]
    action = source[ACTION_DUAL]
    residual_cyclicity = source[RESIDUAL_CYCLICITY]
    if local_extension["counts"]["local_386_rows_fully_namespaced_after_this_result"] != 386:
        raise ValueError("M1A2 local completion drift")

    species_rows = local_species_rows(grading)
    species_semantics = {key: uniform_species_semantics(rows) for key, rows in species_rows.items()}

    represented_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []
    dfinite_partition: dict[int, str] = {}
    represented_label_to_index: dict[str, int] = {}
    source_sector_counts: dict[str, int] = {}
    represented_level_counts: list[dict[str, int]] = []
    test_level_counts: list[dict[str, int]] = []

    for block in dfinite["blocks"]:
        energy = block["energy"]
        represented_before = len(represented_rows)
        test_before = len(test_rows)
        for sector in block["full_sectors"]:
            source_sector_counts[sector["name"]] = source_sector_counts.get(sector["name"], 0) + sector["dimension"]
            for sector_index in range(sector["dimension"]):
                block_index = sector["start"] + sector_index
                global_index = block["full_offset"] + block_index
                label = block["full_basis"][block_index]
                common = {
                    "source_label": label,
                    "energy": energy,
                    "dfinite_global_index": global_index,
                    "dfinite_block_index": block_index,
                    "dfinite_sector": sector["name"],
                    "sector_index": sector_index,
                    "chain_degree": sector["ghost_number"],
                    "conformal_compact_weight": energy,
                    "ce_ghost_number": na("finite harmonic chain coordinate, not a residual CE cochain"),
                    "authority": {
                        "dfinite_row": f"{DFINITE.relative_to(ROOT)}#/blocks/{energy - 2}/full_basis/{block_index}",
                        "dfinite_sector": f"{DFINITE.relative_to(ROOT)}#/blocks/{energy - 2}/full_sectors/{[s['name'] for s in block['full_sectors']].index(sector['name'])}",
                    },
                }
                if sector["name"] in TEST_SECTORS:
                    dfinite_partition[global_index] = "TEST_NONMINIMAL_EXCLUDED"
                    partner_sector = "multiplier" if sector["name"] == "antighost" else "antighost"
                    partner = next(row for row in block["full_sectors"] if row["name"] == partner_sector)
                    partner_index = partner["start"] + sector_index
                    row = {
                        "comparison_index": len(test_rows),
                        **common,
                        "role": sector["role"],
                        "comparison_antifield_number": sector["antifield_number"],
                        "chain_parity": sector["ghost_number"] % 2,
                        "bv_ghost_number": na("no authoritative local BV generator dictionary exists for this comparison-only test doublet"),
                        "antifield_number": na("the source supplies only comparison-sector filtration metadata, not an authoritative local BV species"),
                        "form_degree": na("comparison-only harmonic test coordinate, not a local differential-form generator"),
                        "Grassmann_parity": na("local BV parity cannot be inferred from the historical antighost label"),
                        "mass_dimension": na("no action-derived local source dictionary exists for this test fixture"),
                        "Weyl_weight": na("no action-derived local source dictionary exists for this test fixture"),
                        "intrinsic_jet_order_bound": na("global harmonic comparison coordinate, not a local jet row"),
                        "doublet_partner_label": block["full_basis"][partner_index],
                        "doublet_partner_global_index": block["full_offset"] + partner_index,
                        "q0_doublet_role": "SOURCE" if sector["name"] == "antighost" else "TARGET",
                        "source_disposition": "EXCLUDED_FROM_AUTHORITATIVE_LOCAL_GRAPH_BV_386",
                        "exclusion_reason": "the scalar test doublet is absent from the thirty local endpoint species and has no authoritative local action dictionary",
                        "semantic_state": "FULLY_CLASSIFIED_COMPARISON_FIXTURE_EXCLUDED_FROM_AUTHORITATIVE_SOURCE",
                    }
                    test_rows.append(row)
                    continue

                dfinite_partition[global_index] = "AUTHORITATIVE_REPRESENTED_ENDPOINT"
                species = SECTOR_TO_SPECIES[sector["name"]]
                local_rows = species_rows[species]
                semantics = species_semantics[species]
                if sector["ghost_number"] != semantics["chain_degree"] or sector["antifield_number"] != semantics["antifield_number"]:
                    raise ValueError(f"D-finite/local grading mismatch: E{energy}:{sector['name']}")
                row = {
                    "represented_index": len(represented_rows),
                    **common,
                    "role": sector["role"],
                    "local_species_id": species,
                    "local_endpoint_row_ids": [item["row_id"] for item in local_rows],
                    "local_endpoint_row_indices": [item["index"] for item in local_rows],
                    "local_component_resolution": "SPECIES_LEVEL_EXACT; a global tensor harmonic is not one fixed position-space component row",
                    "bv_ghost_number": semantics["bv_ghost_number"],
                    "antifield_number": semantics["antifield_number"],
                    "form_degree": semantics["form_degree"],
                    "Grassmann_parity": semantics["Grassmann_parity"],
                    "mass_dimension": semantics["mass_dimension"],
                    "Weyl_weight": semantics["Weyl_weight"],
                    "intrinsic_jet_order_bound": semantics["intrinsic_jet_order_bound"],
                    "semantic_state": "FULLY_NAMESPACED_REPRESENTED_ENDPOINT_COORDINATE",
                }
                row["authority"]["local_species_rows"] = [item["authority"]["chain_row"] for item in local_rows]
                represented_label_to_index[label] = row["represented_index"]
                represented_rows.append(row)
        represented_level_counts.append({"energy": energy, "coordinates": len(represented_rows) - represented_before})
        test_level_counts.append({"energy": energy, "coordinates": len(test_rows) - test_before})

    all_full_indices = set(range(dfinite["global_direct_sum"]["full_dimension"]))
    if set(dfinite_partition) != all_full_indices:
        raise ValueError("D-finite partition is not exhaustive")

    q_partition_defects = 0
    q_degree_defects = 0
    chain_degree_by_global = {
        row["dfinite_global_index"]: row["chain_degree"] for row in represented_rows + test_rows
    }
    for block in dfinite["blocks"]:
        for target, source_index, coefficient in block["matrices"]["q0"]["entries"]:
            if coefficient != "1":
                raise ValueError("non-unit q0 coefficient drift")
            target_global = block["full_offset"] + target
            source_global = block["full_offset"] + source_index
            q_partition_defects += int(dfinite_partition[target_global] != dfinite_partition[source_global])
            q_degree_defects += int(chain_degree_by_global[target_global] != chain_degree_by_global[source_global] + 1)

    comparison_source = represented["comparison"]["source"]
    if [row["coordinates"] for row in represented_level_counts] != [row["represented_endpoint_complex_dimension"] for row in comparison_source["level_dimensions"]]:
        raise ValueError("represented level census drift")
    if [row["coordinates"] for row in test_level_counts] != [row["test_nonminimal_dimension_excluded"] for row in comparison_source["level_dimensions"]]:
        raise ValueError("test level census drift")

    represented_basis = represented["ordered_residual_basis"]
    dual_dictionary = action["action_pairing_identification"]["dual_dictionary"]
    physical_offsets = {row["energy"]: row for row in represented["comparison"]["physical_offsets"]}
    blocks = {row["energy"]: row for row in dfinite["blocks"]}
    primal_rows: list[dict[str, Any]] = []
    dual_rows: list[dict[str, Any]] = []
    residual_crosswalk_defects = 0
    support_defects = 0
    metric_semantics = species_semantics["g"]
    metric_dual_semantics = species_semantics["g_star"]

    for basis_row, dual in zip(represented_basis, dual_dictionary, strict=True):
        energy = basis_row["energy"]
        block = blocks[energy]
        chirality_size = block["dimensions"]["chirality"]
        physical_index = basis_row["chirality_index"] + (0 if basis_row["chirality"] == "W_PLUS" else chirality_size)
        block_index = physical_offsets[energy]["metric_tf_physical_start"] + physical_index
        source_label = block["full_basis"][block_index]
        represented_index = represented_label_to_index.get(source_label)
        residual_crosswalk_defects += int(
            dual["pair_index"] != basis_row["global_index"]
            or dual["primal_label"] != basis_row["represented_residual_label"]
            or dual["energy"] != energy
            or dual["chirality"] != basis_row["chirality"]
            or dual["family"] != basis_row["family"]
            or dual["two_m_left"] != basis_row["two_m_left"]
            or dual["two_m_right"] != basis_row["two_m_right"]
            or represented_index is None
        )
        support_defects += int(dual["compact_source_support"] is not True)
        common = {
            "pair_index": basis_row["global_index"],
            "energy": energy,
            "chirality": basis_row["chirality"],
            "family": basis_row["family"],
            "two_j_left": basis_row["two_j_left"],
            "two_j_right": basis_row["two_j_right"],
            "two_m_left": basis_row["two_m_left"],
            "two_m_right": basis_row["two_m_right"],
            "source_represented_endpoint_index": represented_index,
            "source_coordinate_label": source_label,
            "source_dfinite_global_index": block["full_offset"] + block_index,
            "local_component_resolution": "SPECIES_LEVEL_EXACT; residual harmonic representatives are not fixed position-space components",
            "ce_ghost_number": na("residual chain coordinate, not a centered CE cochain"),
            "intrinsic_jet_order_bound": na("global cohomology coordinate, not a local jet row"),
        }
        primal_rows.append({
            "residual_index": basis_row["global_index"],
            "residual_label": basis_row["represented_residual_label"],
            "carrier_role": "PRIMAL_POSITIVE_FREQUENCY_RESIDUAL_CLASS",
            **common,
            "chain_degree": 0,
            "bv_ghost_number": metric_semantics["bv_ghost_number"],
            "antifield_number": metric_semantics["antifield_number"],
            "form_degree": metric_semantics["form_degree"],
            "Grassmann_parity": metric_semantics["Grassmann_parity"],
            "mass_dimension": metric_semantics["mass_dimension"],
            "Weyl_weight": metric_semantics["Weyl_weight"],
            "conformal_compact_weight": energy,
            "local_species_id": "g",
            "local_endpoint_row_ids": [row["row_id"] for row in species_rows["g"]],
            "metric_preimage_name": basis_row["metric_preimage_name"],
            "curvature_basis_name": basis_row["curvature_basis_name"],
            "semantic_state": "FULLY_NAMESPACED_REPRESENTED_PRIMAL_RESIDUAL",
            "authority": {
                "residual_basis": f"{REPRESENTED.relative_to(ROOT)}#/ordered_residual_basis/{basis_row['global_index']}",
                "source_coordinate": f"{DFINITE.relative_to(ROOT)}#/blocks/{energy - 2}/full_basis/{block_index}",
            },
        })
        dual_rows.append({
            "residual_index": 470 + basis_row["global_index"],
            "residual_label": dual["formal_dual_label"],
            "carrier_role": "COMPACT_SOURCE_ACTION_DUAL_RESIDUAL_CLASS",
            **common,
            "chain_degree": 1,
            "bv_ghost_number": metric_dual_semantics["bv_ghost_number"],
            "antifield_number": metric_dual_semantics["antifield_number"],
            "form_degree": metric_dual_semantics["form_degree"],
            "Grassmann_parity": metric_dual_semantics["Grassmann_parity"],
            "mass_dimension": metric_dual_semantics["mass_dimension"],
            "Weyl_weight": metric_dual_semantics["Weyl_weight"],
            "conformal_compact_weight": -energy,
            "local_species_id": "g_star",
            "local_endpoint_row_ids": [row["row_id"] for row in species_rows["g_star"]],
            "action_dual_solution_label": dual["action_dual_solution_label"],
            "compact_source_representative": dual["compact_source_representative"],
            "compact_source_support": dual["compact_source_support"],
            "action_krein_sign": dual["action_krein_sign"],
            "phase_normalization": dual["phase_normalization"],
            "action_pairing_on_primal": dual["action_pairing_on_primal"],
            "semantic_state": "FULLY_NAMESPACED_REPRESENTED_COMPACT_SOURCE_ACTION_DUAL",
            "authority": {
                "action_dual": f"{ACTION_DUAL.relative_to(ROOT)}#/action_pairing_identification/dual_dictionary/{basis_row['global_index']}",
                "residual_cyclicity": str(RESIDUAL_CYCLICITY.relative_to(ROOT)),
            },
        })

    typed = residual_cyclicity["typed_carrier"]
    if (
        len(represented_rows) != 4080
        or len(test_rows) != 410
        or len(primal_rows) != typed["primal_residual_coordinates"] != 470
        or len(dual_rows) != typed["compact_source_dual_coordinates"] != 470
        or typed["total_residual_coordinates"] != 940
    ):
        raise ValueError("M1A3 carrier census drift")
    if q_partition_defects or q_degree_defects or residual_crosswalk_defects or support_defects:
        raise ValueError("M1A3 exact crosswalk defect")

    counts = {
        "represented_endpoint_coordinates": len(represented_rows),
        "represented_endpoint_sectors": len(SECTOR_TO_SPECIES),
        "local_endpoint_species_crosswalked": len(species_rows),
        "test_nonminimal_coordinates_excluded": len(test_rows),
        "test_nonminimal_doublets": len(test_rows) // 2,
        "action_residual_primal_coordinates": len(primal_rows),
        "action_residual_dual_coordinates": len(dual_rows),
        "action_residual_total_coordinates": len(primal_rows) + len(dual_rows),
        "dfinite_partition_coordinates": len(dfinite_partition),
        "q0_cross_partition_defects": q_partition_defects,
        "q0_chain_degree_defects": q_degree_defects,
        "residual_crosswalk_defects": residual_crosswalk_defects,
        "compact_source_support_defects": support_defects,
        "rows_with_unresolved_disposition": 0,
    }

    value: dict[str, Any] = {
        "$schema": "../schema/strict-m1a-represented-carrier-crosswalk-v1.schema.json",
        "schema": "strict-m1a-represented-carrier-crosswalk-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m1a-represented-carrier-crosswalk-v1.schema.json",
        "result_id": "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1",
        "result_kind": "M1A3_REPRESENTED_ENDPOINT_TEST_EXCLUSION_AND_ACTION_RESIDUAL_CROSSWALK",
        "result_state": "REPRESENTED_4080_TYPED_TEST_410_EXCLUDED_ACTION_RESIDUAL_940_TYPED",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "a03539c2d82920e945cb776186531b95e993a105",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can every represented positive-energy endpoint and action-residual coordinate be typed against the authoritative local species while resolving the 410-coordinate scalar test doublet without promoting the formal 8,980-coordinate comparison source?",
        "answer": "Yes, on the declared energy-2-through-6 represented domain. All 4,080 minimal D-finite coordinates crosswalk exactly from eight harmonic sectors to six typed local endpoint species. The remaining 410 coordinates are 205 exact comparison-only scalar test doublets; because they are absent from the thirty local endpoint species and have no action-derived local dictionary, they are explicitly excluded from the authoritative source rather than assigned inferred BV semantics. All 470 primal residual rows and 470 compact-source action-dual rows are fully namespaced and source-matched. This completes M1A3, not the M1A4 immutable ledger freeze or Gate A.",
        "scope": {
            "theory": "strict pure-Weyl classical BV import",
            "background": "unit conformal cylinder",
            "energies": [2, 3, 4, 5, 6],
            "represented_domain": "finite D x SO(4)-finite BGG-adapted harmonic sum",
            "action_dual_domain": "the represented 470-dimensional compact-source cohomology subquotient",
            "arithmetic": "finite exact integer labels, gradings, sparse q0 entries and content hashes",
        },
        "crosswalk_contract": {
            "local_to_harmonic_resolution": "A tensor harmonic is crosswalked to one local generator species and its complete component-row family, not falsely to one position-space component.",
            "chain_bv_sign_rule": "chain_degree=-bv_ghost_number on every authoritative represented endpoint and action-residual row",
            "compact_weight_rule": "positive-frequency primal rows have compact weight +energy; conjugate action-dual rows have compact weight -energy",
            "test_fixture_rule": "comparison-only rows without an action-derived local dictionary receive explicit NOT_APPLICABLE local BV fields and are excluded from the authoritative source",
            "formal_source_rule": "the 8,980-coordinate formal cotangent completion is a comparison object and is not imported as the local BV source",
        },
        "sector_to_local_species": [
            {
                "dfinite_sector": sector,
                "local_species_id": species,
                "local_endpoint_row_ids": [row["row_id"] for row in species_rows[species]],
                "coordinate_count": source_sector_counts[sector],
            }
            for sector, species in SECTOR_TO_SPECIES.items()
        ],
        "represented_level_counts": represented_level_counts,
        "test_nonminimal_level_counts": test_level_counts,
        "test_nonminimal_disposition": {
            "status": "EXCLUDED_COMPARISON_FIXTURE",
            "coordinate_count": len(test_rows),
            "doublet_count": len(test_rows) // 2,
            "source_dictionary_found": False,
            "authoritative_local_source_member": False,
            "reason": "the D-finite producer added a scalar test doublet after the eight minimal sectors; it is not a harmonic realization of any of the thirty endpoint species",
            "effect": "the authoritative represented endpoint has dimension 4,080; the wider 4,490-coordinate fixture remains available only as a scoped SDR control",
        },
        "exact_partition_replay": {
            "dfinite_total": len(dfinite_partition),
            "authoritative_represented": len(represented_rows),
            "excluded_test_fixture": len(test_rows),
            "partition_exhaustive": True,
            "partition_disjoint": True,
            "q0_cross_partition_defects": q_partition_defects,
            "q0_chain_degree_defects": q_degree_defects,
        },
        "counts": counts,
        "represented_endpoint_rows": represented_rows,
        "test_nonminimal_rows": test_rows,
        "action_residual_primal_rows": primal_rows,
        "action_residual_dual_rows": dual_rows,
        "row_payload_hashes": {
            "represented_endpoint_rows_sha256": digest(represented_rows),
            "test_nonminimal_rows_sha256": digest(test_rows),
            "action_residual_primal_rows_sha256": digest(primal_rows),
            "action_residual_dual_rows_sha256": digest(dual_rows),
            "combined_typed_crosswalk_sha256": digest([represented_rows, test_rows, primal_rows, dual_rows]),
        },
        "foundational_strength": {
            "finite_crosswalk": "Primitive-recursive finite scans and decidable integer/string equality suffice for the row partition and grading checks.",
            "choice_used_by_crosswalk": False,
            "completion_used_by_crosswalk": False,
            "imported_analytic_dependency": "The compact-source meaning of the 470 action duals is imported from the separately certified LORENTZIAN-CAUSAL M3RC-B theorem.",
            "full_continuous_dual_claimed": False,
        },
        "claim_flags": {
            "M1A3_REPRESENTED_ENDPOINT_4080_FULLY_NAMESPACED": True,
            "M1A3_TEST_NONMINIMAL_410_DISPOSITION_COMPLETE": True,
            "M1A3_ACTION_RESIDUAL_940_FULLY_NAMESPACED": True,
            "M1A3_REPRESENTED_CROSSWALK_COMPLETE": True,
            "M1A4_IMMUTABLE_LEDGER_FREEZE_COMPLETE": False,
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE": False,
            "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE": False,
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE": False,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "FULL_CONTINUOUS_ALL_ENERGY_DUAL_IDENTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "a one-to-one identification between a global tensor harmonic and a fixed position-space component",
            "that the 410 comparison-only test coordinates are fields of the authoritative strict local BV theory",
            "that the finite compact-source action dual is the full continuous dual of all smooth or distributional solutions",
            "that the formal 8,980-coordinate cotangent comparison is the authoritative original BV complex",
            "the M1A4 immutable full-ledger freeze, M1B composite contraction or M1C common replay",
            "a passed classical import gate",
            "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Freeze M1A4 by content-addressing the completed 386 local rows, this represented crosswalk, the zero-mode payload and centered cochain dictionaries as one immutable typed diagram; then construct M1B on those exact carriers.",
        "human_report": str(REPORT.relative_to(ROOT)),
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": file_hash(path), "role": role}
                for path, result_id, role in INPUTS
            ],
            "producer": str(Path(__file__).resolve().relative_to(ROOT)),
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m1a_represented_carrier_crosswalk.py",
            "method": "reconstruct the 4,490 partition, sector/species gradings, q0 separation, residual source locations and 470 action-dual matches directly from pinned inputs",
            "expected_digest": "",
        },
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    sector_rows = "\n".join(
        f"| `{row['dfinite_sector']}` | `{row['local_species_id']}` | {row['coordinate_count']:,} | {', '.join(f'`{item}`' for item in row['local_endpoint_row_ids'])} |"
        for row in value["sector_to_local_species"]
    )
    levels = "\n".join(
        f"| {represented['energy']} | {represented['coordinates']:,} | {test['coordinates']:,} |"
        for represented, test in zip(value["represented_level_counts"], value["test_nonminimal_level_counts"], strict=True)
    )
    return f"""# Strict M1A3 represented-carrier crosswalk v1

**Result:** `{value['result_id']}`
**Lifecycle:** `{value['lifecycle']}`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Outcome

M1A3 is complete on the declared energy-2-through-6 represented domain.  The
4,490-coordinate D-finite comparison source splits exactly and exhaustively
into **4,080 authoritative represented endpoint coordinates** and **410
comparison-only test coordinates**.  No unary differential arrow crosses that
partition and every arrow raises the namespaced chain degree by one.

The 4,080 rows crosswalk from eight harmonic sectors to the six typed local
endpoint species.  This is an exact species-level correspondence: a tensor
harmonic generally mixes position-space components, so it is not assigned to
one arbitrary component row.

| D-finite sector | Local species | Coordinates | Local component family |
|---|---:|---:|---|
{sector_rows}

## The 410-coordinate question

The extra rows are **205 exact scalar test doublets**:

| Energy | Authoritative represented endpoint | Excluded test fixture |
|---:|---:|---:|
{levels}

The historical labels are `antighost` and `multiplier`, but there is no
action-derived local generator dictionary for them and neither occurs among
the thirty endpoint species.  Assigning standard BV ghost number, parity,
dimension or Weyl weight from those names would therefore manufacture theory
data.  Each row instead carries the known comparison-chain metadata, explicit
`NOT_APPLICABLE` local fields, its exact q0 doublet partner, and the disposition
`EXCLUDED_FROM_AUTHORITATIVE_LOCAL_GRAPH_BV_386`.  The full 4,490 fixture
remains a useful finite SDR control; it is not silently promoted to the strict
source.

## Action residual

All **470 positive-frequency primal residual rows** are matched to their exact
metric-sector coordinates and all **470 compact-source action duals** are
matched to the M3RC-B dictionary.  The primal rows have chain degree zero and
compact weight `+E`; the shifted action duals have chain degree one and compact
weight `-E`.  Every compact-source flag is true, and the residual crosswalk,
q0-degree and partition defect counts are all zero.  This is the represented
rank-940 action carrier, not the full continuous dual of an all-energy smooth
space.

## Foundational strength

The partition and crosswalk are finite exact data: primitive-recursive scans
and decidable equality suffice, with no Choice or completion principle.  The
physical compact-source interpretation is not re-proved here; it is imported
under `LORENTZIAN-CAUSAL` from the separately pinned M3RC-B certificate.

## Boundary and next gate

This completes M1A3 only.  M1A4 must freeze the local, represented, zero-mode
and centered dictionaries into one immutable typed diagram.  M1B must then
materialize the composite contraction, and M1C must replay all Gate-A checks
on the same bytes.  Gate A remains fail closed.  No full-complex Hadamard
state, renormalized Lorentzian product, QME restoration or residual quantum
transfer follows.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        ok = RESULT.exists() and REPORT.exists() and RESULT.read_text() == rendered and REPORT.read_text() == report_text
        print("STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1: CURRENT" if ok else "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1: DRIFT")
        return 0 if ok else 1
    RESULT.write_text(rendered, encoding="utf-8")
    REPORT.write_text(report_text, encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
