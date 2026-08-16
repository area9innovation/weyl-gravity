#!/usr/bin/env python3
"""Independent structural audit of the migration-reviewed explorer v2."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "foundations/site"
DATA = SITE / "data.json"
MANIFEST = SITE / "manifest.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
VIABILITY = ROOT / "foundations/site/viability.json"
ASSEMBLIES = ROOT / "foundations/site/assemblies.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json"
LADDER = ROOT / "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json"
COMPLETION_ATLAS = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36.json"
COMPLETION_RESIDUAL_ZERO_MODES = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
COMPLETION_CENTERED_COHOMOLOGY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
COMPLETION_RESIDUAL_SDR_TYPE_AUDIT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
COMPLETION_GREEN_ACTION_NAME = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
COMPLETION_UNARY_CAUSAL_SNAPSHOT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
COMPLETION_FULL_D = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_D_ACTION_V1.json"
COMPLETION_Q2_PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
COMPLETION_Q2_GREEN = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
COMPLETION_RECURSIVE_TREES = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
COMPLETION_FORMAL_COEFFICIENTS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
COMPLETION_QUADRATIC_OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
COMPLETION_Q3_WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
COMPLETION_GATE_V8 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"
COMPLETION_GATE_V9 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
COMPLETION_GATE_V10 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V10_RECONCILIATION.json"
COMPLETION_CUBIC_INVENTORY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
COMPLETION_HH_HV_LIFT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
COMPLETION_GATE_V11 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V11_RECONCILIATION.json"
COMPLETION_DIFF_AUXILIARY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
COMPLETION_GATE_V12 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V12_RECONCILIATION.json"
COMPLETION_GHOST_MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
COMPLETION_GATE_V13 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"
COMPLETION_SHIFTED_MASS_Q2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
COMPLETION_DIFF_AUXILIARY_V2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
COMPLETION_SOURCE_Q2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
COMPLETION_CLASSICAL_QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
COMPLETION_SHIFTED_MASS_Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
COMPLETION_SOURCE_Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
COMPLETION_GATE_V18 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
STATUSES = {"LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"}
MIGRATIONS = {"EXACT_PARENT_TRANSFER", "CAPABILITY_QUALIFIED", "REVIEWED_OVERLAY", "REVIEWED_NO_TRANSFER", "REVIEWED_CHILD_GAP", "DIRECT_COORDINATE_REVIEW", "NOT_REVIEWED"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data: dict[str, Any]) -> str:
    projection = {key: data[key] for key in ("axes", "cells", "evidence", "ladder", "graph", "completion_atlas", "completion_residual_zero_modes", "completion_centered_cohomology", "completion_residual_sdr_type_audit", "cross_cell_interfaces", "carrier_interfaces", "numerical_reproducibility_records")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    data = load(DATA) if data is None else data
    cube, ladder, completion_source, residual_zero_mode_source, centered_cohomology_source, residual_sdr_type_audit_source, result, manifest, viability, assemblies = load(CUBE), load(LADDER), load(COMPLETION_ATLAS), load(COMPLETION_RESIDUAL_ZERO_MODES), load(COMPLETION_CENTERED_COHOMOLOGY), load(COMPLETION_RESIDUAL_SDR_TYPE_AUDIT), load(RESULT), load(MANIFEST), load(VIABILITY), load(ASSEMBLIES)
    green_source, unary_causal_source = load(COMPLETION_GREEN_ACTION_NAME), load(COMPLETION_UNARY_CAUSAL_SNAPSHOT)
    full_d_source, q2_preflight_source, q2_green_source, recursive_tree_source, formal_source, typed_inverse_source, quadratic_source, q3_witness_source, gate_v8_source, gate_v9_source, gate_v10_source, cubic_inventory_source, hh_hv_lift_source, gate_v11_source, diff_auxiliary_source, gate_v12_source, ghost_manifest_source, gate_v13_source, shifted_mass_source, diff_v2_source, source_q2_source, classical_quartic_source, shifted_mass_q3_source, source_q3_source, gate_v18_source = load(COMPLETION_FULL_D), load(COMPLETION_Q2_PREFLIGHT), load(COMPLETION_Q2_GREEN), load(COMPLETION_RECURSIVE_TREES), load(COMPLETION_FORMAL_COEFFICIENTS), load(COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE), load(COMPLETION_QUADRATIC_OBSTRUCTION), load(COMPLETION_Q3_WITNESS), load(COMPLETION_GATE_V8), load(COMPLETION_GATE_V9), load(COMPLETION_GATE_V10), load(COMPLETION_CUBIC_INVENTORY), load(COMPLETION_HH_HV_LIFT), load(COMPLETION_GATE_V11), load(COMPLETION_DIFF_AUXILIARY), load(COMPLETION_GATE_V12), load(COMPLETION_GHOST_MANIFEST), load(COMPLETION_GATE_V13), load(COMPLETION_SHIFTED_MASS_Q2), load(COMPLETION_DIFF_AUXILIARY_V2), load(COMPLETION_SOURCE_Q2), load(COMPLETION_CLASSICAL_QUARTIC), load(COMPLETION_SHIFTED_MASS_Q3), load(COMPLETION_SOURCE_Q3), load(COMPLETION_GATE_V18)
    errors: list[str] = []
    axes = {x.get("id"): x for x in data.get("axes", [])}
    keys = {axis_id: [x.get("id") for x in axes.get(axis_id, {}).get("keys", [])] for axis_id in ("FOUNDATION", "CARRIER", "REFINED_OBLIGATION")}
    if [len(keys[x]) for x in keys] != [6, 6, 16]:
        errors.append("axis sizes")
    if any(not axis.get("plain_name") or not axis.get("guide_question") or any(not key.get("plain_meaning") for key in axis.get("keys", [])) for axis in axes.values()):
        errors.append("plain-language dimension guide closure")
    expected = {(f, c, o) for f in keys["FOUNDATION"] for c in keys["CARRIER"] for o in keys["REFINED_OBLIGATION"]}
    cells = data.get("cells", [])
    coordinates = [(x.get("foundation"), x.get("carrier"), x.get("obligation")) for x in cells]
    if len(cells) != 576 or len(set(coordinates)) != 576 or set(coordinates) != expected:
        errors.append("Cartesian closure")
    if any(x.get("status") not in STATUSES for x in cells) or any(x.get("migration_status") not in MIGRATIONS for x in cells):
        errors.append("coverage/migration status closure")

    emitted = [x for x in cells if x.get("emitted")]
    synthetic = [x for x in cells if not x.get("emitted")]
    if len(emitted) != 576 or len(synthetic) != 0:
        errors.append("emitted/complement partition")
    if any(x.get("status") != "NOT_MAPPED" or x.get("migration_status") != "NOT_REVIEWED" for x in synthetic):
        errors.append("synthetic fail-closed states")
    if any("not a literature-absence claim" not in x.get("boundary", "") for x in synthetic):
        errors.append("synthetic NOT_MAPPED boundary")

    original = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    for cell in emitted:
        source = original.get((cell["foundation"], cell["carrier"], cell["obligation"]))
        if source is None or {key: value for key, value in cell.items() if key != "emitted"} != source:
            errors.append("authoritative emitted-cell copy")
            break
    migration_counts = Counter(x.get("migration_status") for x in emitted)
    if migration_counts.get("REVIEWED_NO_TRANSFER") != 88 or migration_counts.get("REVIEWED_CHILD_GAP") != 24 or migration_counts.get("DIRECT_COORDINATE_REVIEW") != 124 or "NOT_REVIEWED" in migration_counts:
        errors.append("emitted migration review closure")
    no_transfer = [x for x in emitted if x.get("migration_status") == "REVIEWED_NO_TRANSFER"]
    still_unmapped = [x for x in no_transfer if x.get("status") == "NOT_MAPPED"]
    newly_covered = [x for x in no_transfer if x.get("status") != "NOT_MAPPED"]
    if len(still_unmapped) != 0 or len(newly_covered) != 88 or any(not x.get("evidence") or not x.get("migration_evidence") for x in newly_covered):
        errors.append("reviewed no-transfer separation")

    evidence = data.get("evidence", {})

    # Evidence roles: closure, and agreement between the declared role kind and
    # the kind the evidence registry independently resolved for that record.
    vocabulary = {x.get("id") for x in data.get("evidence_role_vocabulary", [])}
    if vocabulary != {"DIRECT_LOCAL", "DIRECT_LITERATURE", "SUPPORTING", "UNREVIEWED"} or not data.get("evidence_role_rule"):
        errors.append("evidence-role vocabulary")
    role_kind = {"DIRECT_LOCAL": "LOCAL_RESULT", "DIRECT_LITERATURE": "LITERATURE"}
    dual = 0
    for cell in cells:
        roles = cell.get("evidence_roles")
        if not isinstance(roles, dict) or sorted(roles) != sorted(cell.get("evidence") or []):
            errors.append("evidence-role closure")
            break
        if set(roles.values()) - vocabulary:
            errors.append("evidence-role vocabulary closure")
            break
        if any(role in role_kind and evidence.get(item, {}).get("kind") != role_kind[role] for item, role in roles.items()):
            errors.append("evidence-role kind disagrees with the resolved evidence record")
            break
        if {"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(roles.values()):
            dual += 1
    if any(x.get("evidence_roles") for x in synthetic):
        errors.append("synthetic cells carry evidence roles")
    if dual != cube["dimensions"]["dual_direct_cells"] or data.get("counts", {}).get("dual_direct") != dual:
        errors.append("dual-direct cell count")

    # Recompute the displayed mark independently of the generator: upper case is a
    # certified direct grade, lower case a supporting ingredient of that kind, and
    # a lower-case letter is suppressed when its kind already shows as a grade.
    status_mark = {"LOCAL_RESULT": "L", "LITERATURE_RESULT": "R", "PIECES_ONLY": "P", "PRIORITY_GAP": "G", "REVIEWED_GAP": "O", "NOT_MAPPED": "\u00b7"}
    upper_of = {"DIRECT_LOCAL": "L", "DIRECT_LITERATURE": "R"}
    lower_of = {"LOCAL_RESULT": "l", "LITERATURE": "r"}
    marks: Counter = Counter()
    cell_marks: list[str] = []
    for cell in cells:
        roles = cell.get("evidence_roles") or {}
        direct = {upper_of[role] for role in roles.values() if role in upper_of}
        upper = "".join(x for x in "LR" if x in direct) or status_mark[cell["status"]]
        support = {lower_of[evidence[item]["kind"]] for item, role in roles.items() if role == "SUPPORTING"}
        cell_marks.append(upper + "".join(x for x in "lr" if x in support and x.upper() not in upper))
        marks[cell_marks[-1]] += 1
    if data.get("counts", {}).get("mark_counts") != dict(sorted(marks.items())):
        errors.append("declared mark counts")
    # A lower-case letter must never move a cell out of its status family: the
    # upper-case part of every mark has to agree with the cell's scalar status.
    family_status = {"L": "LOCAL_RESULT", "LR": "LOCAL_RESULT", "R": "LITERATURE_RESULT",
                     "P": "PIECES_ONLY", "G": "PRIORITY_GAP", "O": "REVIEWED_GAP", "\u00b7": "NOT_MAPPED"}
    for cell, mark in zip(cells, cell_marks):
        family = mark.rstrip("lr")
        if family_status.get(family) != cell.get("status"):
            errors.append("mark family disagrees with status")
            break

    used = {item for cell in emitted for field in ("evidence", "migration_evidence") for item in cell.get(field, [])}
    if set(evidence) != used or len(evidence) != 83:
        errors.append("coverage and migration evidence resolution")
    for item in evidence.values():
        for field in ("result_link", "report_link", "ledger_link"):
            link = item.get(field)
            if link and not (SITE / link).is_file():
                errors.append("bundled evidence link " + link)
    for link in data.get("source_links", {}).values():
        if not (SITE / link).is_file():
            errors.append("bundled source link " + str(link))

    graph = data.get("graph", {})
    nodes = {x.get("id") for x in graph.get("nodes", [])}
    vocabulary = set(graph.get("relation_vocabulary", []))
    if len(nodes) != 12 or len(graph.get("edges", [])) != 10 or any(edge.get("from") not in nodes or edge.get("to") not in nodes or edge.get("relation") not in vocabulary for edge in graph.get("edges", [])):
        errors.append("typed implication graph")
    if data.get("ladder") != ladder.get("ladder") or len(data.get("ladder", [])) != 6:
        errors.append("strength ladder projection")
    completion = data.get("completion_atlas", {})
    if completion != completion_source:
        errors.append("Lorentzian completion atlas projection")
    residual_zero_modes = data.get("completion_residual_zero_modes", {})
    if residual_zero_modes != residual_zero_mode_source:
        errors.append("residual zero-mode payload projection")
    centered_cohomology = data.get("completion_centered_cohomology", {})
    if centered_cohomology != centered_cohomology_source:
        errors.append("centered cohomology payload projection")
    residual_sdr_type_audit = data.get("completion_residual_sdr_type_audit", {})
    if residual_sdr_type_audit != residual_sdr_type_audit_source:
        errors.append("residual SDR type-and-locality audit projection")
    if len(completion.get("branches", [])) != 7 or len(completion.get("stages", [])) != 11 or sum(len(item.get("stages", [])) for item in completion.get("branches", [])) != 77:
        errors.append("Lorentzian completion branch/stage closure")
    if len(completion.get("route_selection", [])) != 10 or len(completion.get("berger_h26_c26_decision_chain", [])) != 11:
        errors.append("Lorentzian completion route/decision closure")
    completion_flags = completion.get("claim_flags", {})
    if completion_flags.get("general_noncone_104_row_no_go") is not False or completion_flags.get("lorentzian_full_theory_certified") is not False:
        errors.append("Lorentzian completion fail-closed boundary")
    if completion.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36":
        errors.append("Lorentzian completion atlas version")
    transport = completion.get("strict_causal_sign_transport", {})
    if transport.get("full_dimension") != 386 or transport.get("positive_signs") != 381 or transport.get("negative_signs") != 5 or transport.get("causal_stage_preserved") is not True:
        errors.append("strict causal sign transport projection")
    if transport.get("common_bytes_identified") is not False or transport.get("nonlinear_stage_preserved") is not False or completion_flags.get("strict_386_common_bytes_identified") is not False:
        errors.append("strict causal transport promotion firewall")
    endpoint = completion.get("strict_endpoint_q1_content_bridge", {})
    if endpoint.get("arrow_tables_matching") != 80 or endpoint.get("bach_columns_matching") != 700 or endpoint.get("common_nonzero_coefficients") != 619:
        errors.append("strict endpoint q1 projection")
    if endpoint.get("transported_ghost_pairing_canonical") is not False or endpoint.get("transported_ghost_pairing_negative_canonical") is not True:
        errors.append("strict endpoint ordinary pairing-sign disposition")
    if completion_flags.get("strict_386_pairing_suspension_bridge_certified") is not True:
        errors.append("strict endpoint suspension resolution")
    suspension = completion.get("strict_suspended_adjoint_bridge", {})
    # The immutable V1 bridge records 54 entries in the pre-pullback
    # DeWitt/ghost coordinates.  The V8 component projection below supplies
    # the unambiguous 54 pre-pullback / 30 Gate-coordinate reconciliation.
    if suspension.get("endpoint_pairing_entries") != 54 or suspension.get("full_R_positive") != 376 or suspension.get("full_R_negative") != 10 or suspension.get("full_suspended_green_adjoint_replayed") is not True:
        errors.append("strict suspension bridge projection")
    component_pairing = completion.get("strict_component_pairing_serialization", {})
    if component_pairing.get("full_rows") != 386 or component_pairing.get("algebraic_complement_rows") != 356 or component_pairing.get("algebraic_complement_split") != "356=36+320" or component_pairing.get("pairing_entries") != 410 or component_pairing.get("pairing_rank") != 386:
        errors.append("strict component-pairing projection")
    if component_pairing.get("endpoint_pairing_entries_gate_coordinates") != 30 or component_pairing.get("endpoint_pairing_entries_pre_pullback") != 54 or component_pairing.get("componentwise_T_adjoint_replayed") is not True or component_pairing.get("all_operator_component_adjoints_replayed") is not False:
        errors.append("strict component-pairing replay boundary")
    if completion_flags.get("strict_386_component_pairing_serialized") is not True or completion_flags.get("strict_386_all_operator_component_adjoints_replayed") is not False:
        errors.append("strict component-pairing flags")
    portability = completion.get("strict_operator_portability", {})
    if portability.get("contracts") != ["FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION"] or portability.get("operator_families_classified") != 6:
        errors.append("strict operator-portability types")
    if (portability.get("endpoint_q1_arrow_tables"), portability.get("endpoint_q1_nonzero_coefficients"), portability.get("endpoint_q1_bach_columns")) != (80, 619, 700):
        errors.append("strict endpoint portability counts")
    if portability.get("full_q1_portable") is not False or portability.get("local_sdr_portable") is not False or portability.get("endpoint_green_action_portable") is not False or portability.get("full_green_action_portable") is not False or portability.get("causal_green_theorem_preserved") is not True:
        errors.append("strict operator-portability boundary")
    sign_gate = completion.get("strict_full_q1_split_sign_gate", {})
    if (sign_gate.get("carrier_rows"), sign_gate.get("auxiliary_rows"), sign_gate.get("executable_sign"), sign_gate.get("declared_sign")) != (386, 36, "+I_4", "-I_4"):
        errors.append("strict split-q1 sign-gate projection")
    if sign_gate.get("executable_cyclicity_defects") != 0 or sign_gate.get("declared_cyclicity_defects") != 8 or sign_gate.get("both_nilpotent") is not True or sign_gate.get("both_contractible") is not True:
        errors.append("strict split-q1 exact replay")
    repair = completion.get("strict_auxiliary_q_sign_repair", {})
    if sign_gate.get("repair_applied") is not False:
        errors.append("historical strict split-q1 diagnosis mutated")
    if (repair.get("repair_applied"), repair.get("source_and_ledgers_consistent"), repair.get("affected_chain_regenerated"), repair.get("plus_cyclicity_defects"), repair.get("minus_regression_cyclicity_defects"), repair.get("tier_3_status"), repair.get("terminal_overclaim_guards")) != (True, True, True, 0, 8, "PASS", 82):
        errors.append("strict split-q1 repair projection")
    if completion_flags.get("strict_386_auxiliary_q_sign_repair_applied") is not True or repair.get("full_q1_serialized") is not False or repair.get("classical_import_gate_passed") is not False:
        errors.append("strict split-q1 repair/full-q1 firewall")
    full_q1 = completion.get("strict_full_q1_component_jet_table", {})
    if (full_q1.get("carrier_dimension"), full_q1.get("operator_tables"), full_q1.get("coefficient_multiindex_tables"), full_q1.get("nonzero_rational_coefficients"), full_q1.get("maximum_order")) != (386, 18, 127, 2193, 4):
        errors.append("strict full-q1 component projection")
    if full_q1.get("q1_squared_zero") is not True or full_q1.get("suspended_cyclicity_defects") != 0 or full_q1.get("derivative_multiindices_checked") != 70:
        errors.append("strict full-q1 exact replay")
    if completion_flags.get("strict_full_386_q1_portable_component_bytes") is not True or completion_flags.get("strict_386_full_q1_squared_zero_replayed") is not True or completion_flags.get("strict_386_full_q1_suspended_cyclicity_replayed") is not True:
        errors.append("strict full-q1 flags")
    if full_q1.get("full_sdr_tables_serialized") is not False or full_q1.get("classical_import_gate_passed") is not False or completion_flags.get("strict_pure_weyl_classical_gate_passed") is not False:
        errors.append("strict full-q1 Gate-A firewall")
    local_sdr = completion.get("strict_local_sdr_component_maps", {})
    expected_local_sdr_counts = (386, 30, 356, 5, 190, 356, 30, 30, 30, 0, 70)
    actual_local_sdr_counts = (
        local_sdr.get("carrier_dimension"), local_sdr.get("retained_endpoint_dimension"),
        local_sdr.get("contracted_dimension"), local_sdr.get("map_count"),
        local_sdr.get("H_alg_nonzero_entries"), local_sdr.get("P_alg_nonzero_entries"),
        local_sdr.get("P_end_nonzero_entries"), local_sdr.get("i_end_nonzero_entries"),
        local_sdr.get("p_end_nonzero_entries"), local_sdr.get("maximum_order"),
        local_sdr.get("derivative_multiindices_checked"),
    )
    if actual_local_sdr_counts != expected_local_sdr_counts:
        errors.append("strict split local-SDR component projection")
    if local_sdr.get("homotopy_identity_defects") != 0 or local_sdr.get("cyclicity_defects") != 0 or local_sdr.get("split_SDR_complete") is not True:
        errors.append("strict split local-SDR exact replay")
    if local_sdr.get("canonical_shear_serialized") is not False or local_sdr.get("represented_green_actions_serialized") is not False or local_sdr.get("classical_import_gate_passed") is not False:
        errors.append("strict split local-SDR coordinate/Green firewall")
    if completion_flags.get("strict_386_split_local_sdr_component_maps_serialized") is not True or completion_flags.get("strict_386_split_local_sdr_identities_replayed") is not True or completion_flags.get("strict_386_split_local_sdr_cyclicity_replayed") is not True:
        errors.append("strict split local-SDR flags")
    if completion_flags.get("strict_386_canonical_shear_component_jets_serialized") is not True or completion_flags.get("strict_386_canonical_shear_inverse_replayed") is not True or completion_flags.get("strict_386_canonical_shear_bv_canonicality_replayed") is not True:
        errors.append("strict canonical-shear successor flags")
    if completion_flags.get("strict_386_unshifted_graph_q1_snapshot_complete") is not True or completion_flags.get("strict_386_unshifted_graph_sdr_snapshot_complete") is not True or completion_flags.get("strict_386_graph_suspension_transported") is not True or completion_flags.get("strict_386_represented_green_actions_serialized") is not True:
        errors.append("strict split local-SDR successor firewall")
    canonical_shear = completion.get("strict_canonical_shear_component_jets", {})
    canonical_counts = (
        canonical_shear.get("carrier_dimension"), canonical_shear.get("forward_table_count"),
        canonical_shear.get("inverse_table_count"), canonical_shear.get("forward_nonzero_off_diagonal_coefficients"),
        canonical_shear.get("inverse_nonzero_off_diagonal_coefficients"), canonical_shear.get("maximum_order"),
        canonical_shear.get("forward_cross_terms"), canonical_shear.get("inverse_cross_terms"),
    )
    if canonical_counts != (386, 7, 7, 1321, 1321, 3, 1, 1):
        errors.append("strict canonical-shear component projection")
    if any(canonical_shear.get(key) != 0 for key in ("raw_T_A_B_hash_defects", "generalized_auxiliary_attachment_nonzero_coefficients", "elementary_BV_canonicality_defects", "left_inverse_defects", "right_inverse_defects", "forbidden_derivative_derivative_products")):
        errors.append("strict canonical-shear exact replay")
    if canonical_shear.get("graph_q1_replay_complete") is not False or canonical_shear.get("graph_sdr_replay_complete") is not False or canonical_shear.get("represented_green_actions_serialized") is not False or canonical_shear.get("classical_import_gate_passed") is not False:
        errors.append("strict canonical-shear graph/Green firewall")
    graph_sdr = completion.get("strict_graph_q1_sdr_component_jets", {})
    graph_counts = (
        graph_sdr.get("carrier_dimension"), graph_sdr.get("operator_tables"),
        graph_sdr.get("split_operator_tables"), graph_sdr.get("graph_attachment_tables"),
        graph_sdr.get("combined_derivative_multiindices"), graph_sdr.get("nonzero_rational_coefficients"),
        graph_sdr.get("maximum_order"), graph_sdr.get("H_alg_nonzero_entries"),
        graph_sdr.get("inclusion_nonzero_entries"), graph_sdr.get("projection_nonzero_entries"),
        graph_sdr.get("transported_suspension_entries"), graph_sdr.get("transported_suspension_off_diagonal_entries"),
    )
    if graph_counts != (386, 27, 18, 9, 70, 4374, 4, 190, 488, 488, 394, 8):
        errors.append("strict graph q1/SDR component projection")
    if any(graph_sdr.get(key) != 0 for key in ("homotopy_defects", "retract_defects", "side_condition_defects", "H_cyclicity_defects", "transported_suspension_involution_defects", "PBW_reduced_cyclicity_defects")):
        errors.append("strict graph q1/SDR exact replay")
    if graph_sdr.get("old_diagonal_suspension_cyclicity_defects") != 8 or graph_sdr.get("raw_graph_suspension_cyclicity_residuals") != 32 or graph_sdr.get("raw_second_chain_relation_residuals") != 16:
        errors.append("strict graph suspension/PBW boundary")
    if graph_sdr.get("represented_green_actions_serialized") is not False or graph_sdr.get("classical_import_gate_passed") is not False:
        errors.append("historical strict graph analytic-Green frontier mutated")
    green_name = completion.get("strict_graph_green_action_name", {})
    if (green_name.get("result_id"), green_name.get("spatial_spectral_branches"), green_name.get("tractor_rank")) != (green_source.get("result_id"), 3, 15):
        errors.append("strict represented Green-name projection")
    if green_name.get("zero_mode_explicit") is not True or green_name.get("endpoint_name_serialized") is not True or green_name.get("full_graph_name_serialized") is not True:
        errors.append("strict represented Green-name closure")
    if green_name.get("plus_name_sha256") != green_source.get("canonical_hashes", {}).get("plus_action_name_sha256") or green_name.get("minus_name_sha256") != green_source.get("canonical_hashes", {}).get("minus_action_name_sha256") or green_name.get("plus_name_sha256") == green_name.get("minus_name_sha256"):
        errors.append("strict represented Green-name hash binding")
    if green_name.get("effective_solver") is not False or green_name.get("kernel_bytes") is not False or green_name.get("weakest_base") != "NOT_ESTABLISHED":
        errors.append("strict represented Green-name boundary")
    unary_causal = completion.get("strict_unary_causal_common_snapshot", {})
    gate_v5 = unary_causal_source.get("gate_v5_reconciliation", {})
    missing_ids = [item.get("id") for item in gate_v5.get("missing_bundle", [])]
    if (unary_causal.get("result_id"), unary_causal.get("carrier_rows"), unary_causal.get("accepted_hashes"), unary_causal.get("receiver_status")) != (unary_causal_source.get("result_id"), 386, 13, "ACCEPTED_SCOPED"):
        errors.append("strict unary-causal common-snapshot projection")
    if unary_causal.get("snapshot_sha256") != unary_causal_source.get("common_snapshot", {}).get("sha256") or unary_causal.get("represented_green_actions_serialized") is not True or unary_causal.get("classical_gate_a_passed") is not False:
        errors.append("strict unary-causal common-snapshot binding")
    if (unary_causal.get("gate_a_exports_required"), unary_causal.get("gate_a_hashes_required"), unary_causal.get("gate_a_freeze_checks_required"), unary_causal.get("gate_a_hashes_accepted_by_scoped_result")) != (20, 7, 10, 0):
        errors.append("strict unary-causal Gate-A boundary")
    if unary_causal.get("missing_bundle_ids") != missing_ids or missing_ids != ["M1_COMMON_STRICT_SNAPSHOT", "M2_STRICT_Q2_D", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES"]:
        errors.append("strict unary-causal missing-bundle ledger")
    if completion_flags.get("strict_386_unary_causal_common_snapshot_accepted") is not True or completion_flags.get("strict_386_effective_numeric_green_solver") is not False or completion_flags.get("strict_386_distribution_kernel_bytes_serialized") is not False:
        errors.append("strict V15 inherited flags")
    full_d = completion.get("strict_full_d_action", {})
    if (full_d.get("result_id"), full_d.get("carrier_rows"), full_d.get("component_blocks"), full_d.get("D_coefficients"), tuple(full_d.get("temporal_multiindex", []))) != (full_d_source.get("result_id"), 386, 22, 386, (1, 0, 0, 0)):
        errors.append("strict full-D projection")
    if (full_d.get("q1_tables_checked"), full_d.get("q1_multiindices_checked"), full_d.get("q1_coefficients_checked"), full_d.get("D_q1_commutator_defects"), full_d.get("pairing_entries_checked"), full_d.get("formal_skew_adjoint_defects"), full_d.get("scoped_snapshot_hashes")) != (27, 70, 4374, 0, 410, 0, 14):
        errors.append("strict full-D exact replay")
    if full_d.get("D_action_sha256") != full_d_source.get("canonical_hashes", {}).get("D_action_sha256") or full_d.get("full_q2_common_snapshot") is not False or full_d.get("D_q2_derivation") is not False or full_d.get("D_gauge_or_charge_decided") is not False:
        errors.append("strict full-D binding/boundary")
    q2_candidate = completion.get("strict_stabilized_q2_lift_preflight", {})
    if (q2_candidate.get("result_id"), q2_candidate.get("carrier_rows"), q2_candidate.get("expanded_component_channels"), q2_candidate.get("unique_block_triples"), q2_candidate.get("input_row_envelope"), q2_candidate.get("output_row_envelope"), q2_candidate.get("interaction_inert_rows")) != (q2_preflight_source.get("result_id"), 386, 140, 68, 110, 110, 196):
        errors.append("strict stabilized-q2 projection")
    if any(q2_candidate.get(key) != 0 for key in ("q1_q2_defects", "koszul_defects", "cyclicity_defects", "D_q2_defects")) or q2_candidate.get("authoritative_full_q2_imported") is not False or q2_candidate.get("candidate_theory_identity_certified") is not False:
        errors.append("strict stabilized-q2 candidate/authority boundary")
    if q2_candidate.get("candidate_q2_sha256") != q2_preflight_source.get("canonical_hashes", {}).get("graph_transport_dag_sha256"):
        errors.append("strict stabilized-q2 hash binding")
    gate_v8 = completion.get("strict_gate_v8_reconciliation", {})
    if (gate_v8.get("result_id"), gate_v8.get("exports_total"), gate_v8.get("exports_receiver_verified_scoped"), gate_v8.get("freeze_checks_total"), gate_v8.get("freeze_checks_receiver_verified_scoped"), gate_v8.get("freeze_checks_supporting_evidence_only"), gate_v8.get("freeze_checks_blocked"), gate_v8.get("accepted_top_level_hashes"), gate_v8.get("gate_a_status")) != (gate_v8_source.get("result_id"), 20, 11, 10, 8, 1, 1, 0, "FAIL_CLOSED"):
        errors.append("strict Gate-V8 projection")
    if (gate_v8.get("source_value"), gate_v8.get("candidate_value"), gate_v8.get("defect"), gate_v8.get("candidate_q2_hash_accepted")) != ("-1", "0", "-1", False):
        errors.append("strict Gate-V8 identity/hash boundary")
    if gate_v8.get("literal_and_linear_identity_refuted") is not True or gate_v8.get("nonlinear_equivalence_may_exist") is not True or gate_v8.get("nonlinear_equivalence_constructed") is not False or gate_v8.get("nonlinear_equivalence_obstructed") is not False:
        errors.append("strict Gate-V8 nonlinear-equivalence firewall")
    q2_green = completion.get("strict_q2_green_composition_preflight", {})
    if (q2_green.get("result_id"), q2_green.get("carrier_rows"), q2_green.get("basis_match"), q2_green.get("pairing_match"), q2_green.get("graph_q1_match"), q2_green.get("causal_orientations_composed")) != (q2_green_source.get("result_id"), 386, True, True, True, 2):
        errors.append("strict candidate q2/Green carrier projection")
    if (q2_green.get("response_identity_defects"), q2_green.get("causal_difference_identity_defects"), q2_green.get("per_input_derivative_order_bound"), q2_green.get("total_derivative_order_bound")) != (0, 0, 10, 13):
        errors.append("strict candidate q2/Green response replay")
    if q2_green.get("plus_response_name_sha256") != q2_green_source.get("canonical_hashes", {}).get("plus_response_name_sha256") or q2_green.get("minus_response_name_sha256") != q2_green_source.get("canonical_hashes", {}).get("minus_response_name_sha256"):
        errors.append("strict candidate q2/Green name binding")
    if q2_green.get("completed_infinite_spaces_required") is not True or q2_green.get("new_choice_beyond_green_theorem") is not False or q2_green.get("weakest_complete_foundational_base") != "NOT_ESTABLISHED":
        errors.append("strict candidate q2/Green foundations boundary")
    if q2_green.get("candidate_only") is not True or q2_green.get("authoritative_q2_green_compatibility") is not False or q2_green.get("recursive_nonlinear_green_trees") is not False:
        errors.append("strict candidate q2/Green authority/recursion firewall")
    recursive_trees = completion.get("strict_recursive_causal_tree_domains", {})
    if (recursive_trees.get("result_id"), recursive_trees.get("retarded_all_finite_trees"), recursive_trees.get("advanced_all_finite_trees"), recursive_trees.get("support_domain_defects"), recursive_trees.get("nodewise_homotopy_domain_defects")) != (recursive_tree_source.get("result_id"), True, True, 0, 0):
        errors.append("strict recursive polarized-tree projection")
    if (recursive_trees.get("first_mixed_failure_leaves"), recursive_trees.get("four_leaf_all_sign_decorations"), recursive_trees.get("four_leaf_admissible"), recursive_trees.get("four_leaf_not_uniformly_defined")) != (4, 40, 38, 2):
        errors.append("strict recursive mixed-sign census")
    if recursive_trees.get("unrestricted_mixed_sign_trees") is not False or recursive_trees.get("arbitrary_causal_difference_trees") is not False or recursive_trees.get("infinite_tree_series_convergence") is not False or recursive_trees.get("authoritative_q2") is not False:
        errors.append("strict recursive tree promotion firewall")
    formal = completion.get("strict_polarized_formal_coefficients", {})
    if (formal.get("result_id"), formal.get("orientations"), formal.get("checked_through_leaves"), formal.get("largest_checked_tree_count")) != (formal_source.get("result_id"), 2, 9, 1430):
        errors.append("strict formal coefficient projection")
    if formal.get("coefficientwise_fixed_point") is not True or formal.get("catalan_formula") is not True or formal.get("formal_inverse") is not True or formal.get("lambda_adic_stabilization") is not True:
        errors.append("strict formal coefficient closure")
    if formal.get("order_lambda_squared_bv_residual") != formal_source.get("bv_equation_diagnostic", {}).get("order_lambda_squared_residual") or formal.get("order_lambda_squared_bv_residual_zero_certified") is not False:
        errors.append("strict lambda-squared BV diagnostic")
    if formal.get("analytic_convergence") is not False or formal.get("nonperturbative_inverse") is not False or formal.get("weyl_bv_maurer_cartan_series") is not False or formal.get("authoritative_weyl_bv_moller_map") is not False or formal.get("typed_field_equation_green_inverse") is not False:
        errors.append("strict formal Moller promotion firewall")
    typed_inverse = completion.get("strict_field_equation_green_quotient_inverse", {})
    typed_complex = typed_inverse_source.get("typed_complex", {})
    typed_obstruction = typed_inverse_source.get("full_inverse_obstruction", {})
    if (typed_inverse.get("result_id"), typed_inverse.get("field_rows"), typed_inverse.get("equation_rows"), typed_inverse.get("gauge_nonzero_coefficients"), typed_inverse.get("field_equation_nonzero_coefficients"), typed_inverse.get("noether_nonzero_coefficients")) != (typed_inverse_source.get("result_id"), 116, 116, 425, 3264, 425):
        errors.append("strict typed field-equation projection")
    if typed_inverse.get("source_identity") != typed_inverse_source.get("restricted_homotopy_identities", {}).get("source_identity") or typed_inverse.get("field_identity") != typed_inverse_source.get("restricted_homotopy_identities", {}).get("field_identity"):
        errors.append("strict typed field-equation identity binding")
    if typed_inverse.get("green_component_typed") is not True or typed_inverse.get("constrained_right_inverse") is not True or typed_inverse.get("quotient_left_inverse") is not True:
        errors.append("strict constrained/quotient inverse closure")
    if typed_inverse.get("full_ungauge_fixed_two_sided_inverse") is not False or typed_inverse.get("full_inverse_obstructed") is not True or typed_obstruction.get("status") != "EXACT_GAUGE_COMPLEX_OBSTRUCTION":
        errors.append("strict full inverse obstruction")
    if typed_inverse.get("all_order_nonlinear_source_closure") is not False or typed_inverse.get("quotient_representative_selection_required") is not False or typed_complex.get("q1_degree_step_defects") != 0:
        errors.append("strict source-closure/foundation firewall")
    quadratic = completion.get("strict_quadratic_truncation_lambda2_source_obstruction", {})
    quadratic_disposition = quadratic_source.get("quadratic_truncation_disposition", {})
    if (quadratic.get("fixture_id"), quadratic.get("q2_jacobiator_weyl_identity_value"), quadratic.get("q2_only_lambda2_source_defect"), quadratic.get("required_q3_q1_image")) != ("FLAT_PURE_DIFF_GAUGE_SEED_1", quadratic_disposition.get("witness_jacobiator_weyl_identity"), quadratic_disposition.get("witness_source_closure_defect"), quadratic_disposition.get("required_q3_q1_image_on_witness")):
        errors.append("strict quadratic-truncation obstruction projection")
    if quadratic.get("q2_only_lambda2_source_closed") is not False or quadratic.get("authoritative_q3_required") is not True or quadratic.get("authoritative_q3_imported") is not False or quadratic.get("not_a_full_weyl_no_go") is not True:
        errors.append("strict q3 necessity and full-Weyl boundary")
    q3_witness = completion.get("strict_pure_weyl_q3_witness", {})
    q3_cancellation = q3_witness_source.get("arity_three_cancellation", {})
    if (q3_witness.get("fixture_id"), q3_witness.get("metric_q3_term_count"), q3_witness.get("metric_q3_nonzero_rows"), q3_witness.get("computed_q1_q3_weyl_identity_value"), q3_witness.get("arity_three_witness_defect"), q3_witness.get("lambda2_witness_source_q1_defect")) != ("FLAT_PURE_DIFF_GAUGE_SEED_1", 41, 10, q3_cancellation.get("computed_q1_q3"), "0", "0"):
        errors.append("strict q3 witness projection")
    if q3_witness.get("lambda2_witness_source_closed") is not True or q3_witness.get("general_full_weyl_lambda2_source_closed") is not False or q3_witness.get("authoritative_arbitrary_input_q3_imported") is not False:
        errors.append("strict q3 witness/general closure firewall")
    if q3_witness.get("Berger_q3_direct_import_compatible") is not False or q3_witness.get("Berger_disposition") != "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP":
        errors.append("strict Berger q3 import firewall")
    if completion_flags.get("strict_386_full_local_d_action_certified") is not True or completion_flags.get("strict_386_d_q1_commutator_replayed") is not True or completion_flags.get("strict_386_d_formal_skew_adjoint_replayed") is not True or completion_flags.get("strict_386_unary_causal_d_scoped_snapshot_accepted") is not True:
        errors.append("strict V16 D successor flags")
    if completion_flags.get("strict_386_stabilized_q2_candidate_certified") is not True or completion_flags.get("strict_386_stabilized_d_q2_derivation_verified") is not True:
        errors.append("strict V17 candidate-q2 flags")
    if completion_flags.get("strict_386_candidate_first_nonlinear_causal_response_certified") is not True or completion_flags.get("strict_386_candidate_q2_green_response_identity_verified") is not True or completion_flags.get("strict_386_q2_green_foundations_stratified") is not True:
        errors.append("strict V18 q2/Green successor flags")
    if completion_flags.get("strict_386_authoritative_q2_green_compatibility_certified") is not False or completion_flags.get("strict_386_recursive_nonlinear_green_trees_certified") is not False:
        errors.append("strict V18 q2/Green promotion firewall")
    if completion_flags.get("strict_386_candidate_retarded_all_finite_q2_trees_certified") is not True or completion_flags.get("strict_386_candidate_advanced_all_finite_q2_trees_certified") is not True or completion_flags.get("strict_386_first_mixed_sign_domain_nondefinition_at_four_leaves") is not True:
        errors.append("strict V19 polarized-tree successor flags")
    if completion_flags.get("strict_386_unrestricted_mixed_sign_trees_certified") is not False or completion_flags.get("strict_386_arbitrary_causal_difference_trees_certified") is not False or completion_flags.get("strict_386_infinite_tree_series_convergence_certified") is not False or completion_flags.get("strict_386_authoritative_q2_recursive_trees_certified") is not False:
        errors.append("strict V19 recursive-tree promotion firewall")
    if completion_flags.get("strict_386_candidate_polarized_formal_coefficients_certified") is not True or completion_flags.get("strict_386_candidate_coefficientwise_fixed_point_verified") is not True or completion_flags.get("strict_386_candidate_catalan_formula_verified") is not True or completion_flags.get("strict_386_candidate_lambda_adic_stabilization_verified") is not True:
        errors.append("strict V20 formal-coefficient successor flags")
    if completion_flags.get("strict_386_order_lambda_squared_bv_residual_zero_certified") is not False or completion_flags.get("strict_386_typed_field_equation_green_inverse_certified") is not False or completion_flags.get("strict_386_weyl_bv_maurer_cartan_series_certified") is not False or completion_flags.get("strict_386_authoritative_formal_moller_map_certified") is not False or completion_flags.get("strict_386_analytic_moller_convergence_certified") is not False:
        errors.append("strict V20 Moller/BV promotion firewall")
    if completion_flags.get("strict_386_field_equation_green_component_typed") is not True or completion_flags.get("strict_386_field_equation_constrained_right_inverse_certified") is not True or completion_flags.get("strict_386_field_equation_quotient_left_inverse_certified") is not True or completion_flags.get("strict_386_ungauge_fixed_two_sided_green_inverse_obstructed") is not True:
        errors.append("strict V21 quotient-inverse successor flags")
    if completion_flags.get("strict_386_ungauge_fixed_two_sided_green_inverse_constructed") is not False or completion_flags.get("strict_386_all_order_nonlinear_source_closure_certified") is not False:
        errors.append("strict V21 full-inverse/source-closure firewall")
    if completion_flags.get("strict_386_authoritative_full_q2_imported") is not True or completion_flags.get("strict_386_candidate_theory_identity_certified") is not False or completion_flags.get("strict_386_full_carrier_q2_certified") is not True or completion_flags.get("strict_386_d_q2_derivation_replayed") is not True or completion_flags.get("strict_pure_weyl_classical_gate_passed") is not False:
        errors.append("strict V17 authoritative q2/Gate firewall")
    if (
        completion_flags.get("strict_386_authoritative_full_q3_imported") is not True
        or completion_flags.get("strict_386_full_arity_three_identity_replayed") is not True
        or completion_flags.get("strict_386_full_q3_cyclicity_replayed_mod_d") is not True
        or completion_flags.get("strict_386_full_D_q3_derivation_replayed") is not True
        or completion_flags.get("strict_386_q2_q3_green_compatibility_certified") is not False
        or completion_flags.get("strict_pure_weyl_classical_gate_passed") is not False
    ):
        errors.append("strict V33 authoritative q3/causal-promotion firewall")
    route_names = [item.get("route") for item in completion.get("route_selection", [])]
    if route_names[:4] != ["STRICT_COMMON_ENDPOINT_SDR_BINDING", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]:
        errors.append("strict V36 endpoint/pairing/residual-comparison/freeze route frontier")
    if "STRICT_RESIDUAL_SDR_COMMON_CARRIER" in route_names:
        errors.append("strict V36 retired type-conflated residual route")
    if any(item in {"STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS", "STRICT_386_BV_COTANGENT_LIFT_COMPONENTS", "STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"} for item in route_names):
        errors.append("strict V31 completed component or manifest routes retained")
    if any(item in {"STRICT_TYPED_FIELD_EQUATION_GREEN_INVERSE", "STRICT_Q2_Q3_SOURCE_COCYCLE_CLOSURE", "STRICT_AUTHORITATIVE_Q2_Q3_ARITY_THREE_EXPORT", "STRICT_LAMBDA2_FULL_SOURCE_COCYCLE_CLOSURE"} for item in route_names):
        errors.append("strict V25 retired route frontier")
    if "STRICT_RESIDUAL_EXACT_PAYLOAD" in route_names:
        errors.append("strict V34 completed residual route retained")
    if "STRICT_CENTERED_H3_H4_H5_REPRESENTATIVE_PAYLOAD" in route_names:
        errors.append("strict V35 completed centered route retained")
    minimal_q3 = completion.get("strict_minimal_q3_completion", {})
    if (minimal_q3.get("classical_export_result_id"), minimal_q3.get("quantum_import_result_id"), minimal_q3.get("arity_three_result_id"), minimal_q3.get("cyclicity_result_id")) != ("CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1", "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1", "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1", "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1"):
        errors.append("strict V25 minimal-q3 provenance projection")
    if (minimal_q3.get("arbitrary_three_metric_inputs"), minimal_q3.get("S3_input_permutations_replayed"), minimal_q3.get("arity_three_channels"), minimal_q3.get("arity_three_paths"), minimal_q3.get("quartic_cyclicity_mod_d"), minimal_q3.get("quartic_permutation_group")) != (True, 6, 72, 212, True, "S4"):
        errors.append("strict V25 minimal-q3 identity/cyclicity projection")
    if minimal_q3.get("strict_386_q3_stabilized") is not False or minimal_q3.get("strict_386_authoritative_nonminimal_equivalence") is not False or minimal_q3.get("classical_import_gate_a_passed") is not False:
        errors.append("strict V25 386/Gate-A promotion firewall")
    stabilized_q3 = completion.get("strict_386_stabilized_q3_preflight", {})
    if (
        stabilized_q3.get("carrier_rows"),
        stabilized_q3.get("contractible_rows"),
        stabilized_q3.get("expanded_ternary_block_channels"),
        stabilized_q3.get("arity_three_channels_transported"),
        stabilized_q3.get("arity_three_paths_transported"),
        stabilized_q3.get("arity_three_defects"),
    ) != (386, 356, 16, 72, 212, 0):
        errors.append("strict V25 candidate-q3 stabilization projection")
    if (
        stabilized_q3.get("candidate_q3_stabilized") is not True
        or stabilized_q3.get("authoritative_full_q3_imported") is not False
        or stabilized_q3.get("authoritative_nonminimal_equivalence") is not False
        or stabilized_q3.get("candidate_causal_lambda2_source_closure") is not False
        or stabilized_q3.get("classical_import_gate_a_passed") is not False
    ):
        errors.append("strict V25 candidate/authority firewall")
    identity_obstruction = completion.get("strict_nonminimal_theory_identity_obstruction", {})
    if (identity_obstruction.get("carrier_rows"), identity_obstruction.get("cyclic_form_channel"), identity_obstruction.get("source_value"), identity_obstruction.get("candidate_value"), identity_obstruction.get("source_minus_candidate_defect")) != (386, "Omega(f_hat,q2(v,v))", "-1", "0", "-1"):
        errors.append("strict V26 theory-identity obstruction projection")
    if identity_obstruction.get("literal_identity_refuted") is not True or identity_obstruction.get("linear_shear_only_identity_refuted") is not True or identity_obstruction.get("candidate_internal_identities_preserved") is not True or identity_obstruction.get("nonlinear_equivalence_may_exist") is not True or identity_obstruction.get("nonlinear_equivalence_constructed") is not False or identity_obstruction.get("nonlinear_equivalence_obstructed") is not False or identity_obstruction.get("classical_import_gate_a_passed") is not False:
        errors.append("strict V26 nonlinear-equivalence/Gate-A firewall")
    elimination = completion.get("strict_quadratic_auxiliary_elimination", {})
    if (elimination.get("carrier_rows"), elimination.get("source_before_correction"), elimination.get("inverse_shift_correction"), elimination.get("transformed_source"), elimination.get("candidate"), elimination.get("residual")) != (386, "-1", "1", "0", "0", "0"):
        errors.append("strict V27 quadratic auxiliary-elimination projection")
    if elimination.get("first_nonlinear_component_constructed") is not True or elimination.get("receiver_componentwise_386_cotangent_lift_serialized") is not False or elimination.get("complete_source_q2_pullback_replayed") is not False or elimination.get("complete_source_q3_pullback_replayed") is not False or elimination.get("full_cyclic_L_infinity_equivalence_constructed") is not False:
        errors.append("strict V27 component/full-equivalence firewall")
    gate_v9 = completion.get("strict_gate_v9_reconciliation", {})
    if gate_v9.get("result_id") != gate_v9_source.get("result_id") or gate_v9.get("gate_a_status") != "FAIL_CLOSED" or gate_v9.get("accepted_top_level_hashes") != 0 or gate_v9.get("residual") != "0":
        errors.append("strict Gate V9 projection")
    cubic_inventory = completion.get("strict_shifted_auxiliary_cubic_inventory", {})
    if (
        cubic_inventory.get("result_id") != cubic_inventory_source.get("result_id")
        or (cubic_inventory.get("known_required_cubic_families"), cubic_inventory.get("component_complete_families"), cubic_inventory.get("component_open_families")) != (7, 2, 5)
        or (cubic_inventory.get("h_f_hat_f_hat_source_coefficients"), cubic_inventory.get("h_f_hat_f_hat_candidate_coefficients")) != (72, 0)
        or (cubic_inventory.get("vv_field_map_coefficients"), cubic_inventory.get("vv_cotangent_partner_coefficients"), cubic_inventory.get("vv_canonicality_slices"), cubic_inventory.get("vv_canonicality_defects")) != (22, 16, 4, 0)
        or cubic_inventory.get("vv_BV_cotangent_lift_component_complete") is not True
        or cubic_inventory.get("full_386_BV_cotangent_lift_serialized") is not False
        or cubic_inventory.get("exhaustive_full_nonlinear_BV_family_census") is not False
    ):
        errors.append("strict V28 shifted-cubic inventory projection")
    gate_v10 = completion.get("strict_gate_v10_reconciliation", {})
    if gate_v10.get("result_id") != gate_v10_source.get("result_id") or gate_v10.get("gate_a_status") != "FAIL_CLOSED" or gate_v10.get("accepted_top_level_hashes") != 0 or gate_v10.get("known_required_cubic_families") != 7 or gate_v10.get("vv_BV_lift_canonical") is not True or gate_v10.get("full_bv_cotangent_lift_serialized") is not False:
        errors.append("strict Gate V10 projection")
    hh_hv_lift = completion.get("strict_hh_hv_auxiliary_cotangent_lift", {})
    if (
        hh_hv_lift.get("result_id") != hh_hv_lift_source.get("result_id")
        or (hh_hv_lift.get("carrier_rows"), hh_hv_lift.get("hh_field_coefficients"), hh_hv_lift.get("hv_field_coefficients"), hh_hv_lift.get("vv_field_coefficients")) != (386, 1392, 76, 22)
        or hh_hv_lift.get("combined_cotangent_coefficients") != 3907
        or (hh_hv_lift.get("metric_variation_slices_declared"), hh_hv_lift.get("vector_variation_slices"), hh_hv_lift.get("formal_adjoint_defects")) != (150, 4, 0)
        or (hh_hv_lift.get("known_required_cubic_families"), hh_hv_lift.get("component_complete_families"), hh_hv_lift.get("component_open_families")) != (7, 4, 3)
        or hh_hv_lift.get("full_quadratic_BV_cotangent_lift_serialized") is not True
        or hh_hv_lift.get("diffeomorphism_BV_representation_component_complete") is not False
        or hh_hv_lift.get("exhaustive_full_nonlinear_BV_family_census") is not False
        or hh_hv_lift.get("full_source_q2_q3_pullback_replayed") is not False
    ):
        errors.append("strict V29 curved quadratic cotangent-lift projection")
    gate_v11 = completion.get("strict_gate_v11_reconciliation", {})
    if (
        gate_v11.get("result_id") != gate_v11_source.get("result_id")
        or gate_v11.get("gate_a_status") != "FAIL_CLOSED"
        or gate_v11.get("accepted_top_level_hashes") != 0
        or gate_v11.get("full_quadratic_BV_cotangent_lift_serialized") is not True
        or gate_v11.get("diffeomorphism_representation_component_complete") is not False
        or gate_v11.get("exhaustive_full_nonlinear_BV_family_census") is not False
        or gate_v11.get("complete_source_q2_q3_pullback_replayed") is not False
    ):
        errors.append("strict Gate V11 projection")
    diff_auxiliary = completion.get("strict_diff_auxiliary_bv_representation", {})
    if (
        diff_auxiliary.get("result_id") != diff_auxiliary_source.get("result_id")
        or (diff_auxiliary.get("carrier_rows"), diff_auxiliary.get("completed_families")) != (386, 3)
        or (diff_auxiliary.get("master_density_coefficients"), diff_auxiliary.get("field_output_coefficients"), diff_auxiliary.get("antifield_output_coefficients"), diff_auxiliary.get("c_star_output_coefficients")) != (264, 336, 632, 704)
        or (diff_auxiliary.get("formal_variational_defects"), diff_auxiliary.get("Koszul_symmetry_defects")) != (0, 0)
        or (diff_auxiliary.get("known_required_cubic_families"), diff_auxiliary.get("component_complete_families"), diff_auxiliary.get("component_open_families")) != (7, 7, 0)
        or diff_auxiliary.get("diffeomorphism_BV_representation_component_complete") is not True
        or diff_auxiliary.get("exhaustive_full_nonlinear_BV_family_census") is not False
        or diff_auxiliary.get("full_source_q2_q3_pullback_replayed") is not False
    ):
        errors.append("strict V30 Diff auxiliary BV projection")
    gate_v12 = completion.get("strict_gate_v12_reconciliation", {})
    if (
        gate_v12.get("result_id") != gate_v12_source.get("result_id")
        or gate_v12.get("gate_a_status") != "FAIL_CLOSED"
        or gate_v12.get("accepted_top_level_hashes") != 0
        or gate_v12.get("seven_known_required_cubic_families_component_complete") is not True
        or gate_v12.get("exhaustive_full_nonlinear_BV_family_census") is not False
        or gate_v12.get("complete_source_q2_q3_pullback_replayed") is not False
    ):
        errors.append("strict Gate V12 projection")
    ghost_manifest = completion.get("strict_nonlinear_weyl_boost_ghost_manifest", {})
    if (
        ghost_manifest.get("result_id") != ghost_manifest_source.get("result_id")
        or (ghost_manifest.get("nonzero_ghost_antifield_families"), ghost_manifest.get("minimal_families"), ghost_manifest.get("auxiliary_families")) != (3, 2, 1)
        or ghost_manifest.get("certified_zero_candidate_families") != 4
        or ghost_manifest.get("additional_nonlinear_Weyl_boost_ghost_antifield_families") != 0
        or ghost_manifest.get("off_shell_closure") is not True
        or ghost_manifest.get("field_dependent_structure_functions") is not False
        or ghost_manifest.get("shifted_f_hat_Weyl_invariant") is not True
        or ghost_manifest.get("shifted_f_hat_boost_invariant") is not True
        or ghost_manifest.get("exhaustive_in_declared_scope") is not True
        or ghost_manifest.get("full_386_source_q2_assembled") is not True
    ):
        errors.append("strict V31 nonlinear Weyl/boost ghost-manifest projection")
    source_q2 = completion.get("strict_source_q2_common_assembly", {})
    if (
        source_q2.get("result_id") != source_q2_source.get("result_id")
        or (source_q2.get("minimal_ordered_symbolic_components"), source_q2.get("auxiliary_ordered_component_coefficients"), source_q2.get("source_q2_families")) != (22, 2064, 16)
        or (source_q2.get("q1_q2_defects"), source_q2.get("q2_cyclicity_defects"), source_q2.get("D_q2_defects")) != (0, 0, 0)
        or source_q2.get("full_source_q3_assembled") is not True
        or (source_q2.get("rejected_v1_q1_q2_defects"), source_q2.get("accepted_v2_q1_q2_defects"), source_q2.get("shifted_mass_cyclicity_equalities")) != (336, 0, 3000)
    ):
        errors.append("strict V33 source-q2 predecessor projection")
    source_q3 = completion.get("strict_source_q3_common_assembly", {})
    if (
        source_q3.get("result_id") != source_q3_source.get("result_id")
        or (source_q3.get("source_q3_families"), source_q3.get("classical_independent_monomials"), source_q3.get("classical_ordered_fourth_variations"), source_q3.get("auxiliary_ordered_q3_coefficients")) != (2, 321, 912, 5952)
        or (source_q3.get("cyclic_equalities_checked"), source_q3.get("Weyl_Ward_checks"), source_q3.get("graph_block_quadruples")) != (40000, 605, 40)
        or (source_q3.get("arity_three_defects"), source_q3.get("q3_cyclicity_defects_mod_d"), source_q3.get("D_q3_defects")) != (0, 0, 0)
        or source_q3.get("full_source_q3_assembled") is not True
    ):
        errors.append("strict V33 source-q3 assembly projection")
    residual_projection = completion.get("strict_residual_zero_mode_payload", {})
    if (
        residual_projection.get("result_id") != residual_zero_mode_source.get("result_id")
        or (residual_projection.get("primal_modes"), residual_projection.get("dual_modes"), residual_projection.get("residual_cotangent_dimension")) != (15, 15, 30)
        or (residual_projection.get("structure_nonzero_entries"), residual_projection.get("representation_matrices"), residual_projection.get("identity_defects")) != (120, 15, 0)
        or residual_projection.get("M5_payload_complete") is not True
        or residual_projection.get("common_freeze_bound") is not False
    ):
        errors.append("strict residual zero-mode projection")
    if (
        len(residual_zero_modes.get("zero_mode_basis", {}).get("canonical_generator_order", [])) != 15
        or len(residual_zero_modes.get("zero_mode_basis", {}).get("canonical_dual_order", [])) != 15
        or residual_zero_modes.get("so42_structure_constants", {}).get("nonzero_entries") != 120
        or len(residual_zero_modes.get("residual_representation", {}).get("matrices", [])) != 15
        or residual_zero_modes.get("residual_differential_q_res_0", {}).get("degree_zero_unary_matrix", {}).get("nonzero_entries") != 0
        or any(value != 0 for value in residual_zero_modes.get("exact_replay", {}).values())
        or residual_zero_modes.get("claim_flags", {}).get("COMMON_GATE_A_FREEZE_BOUND") is not False
    ):
        errors.append("strict residual zero-mode exact payload")
    if (
        centered_cohomology.get("scope", {}).get("centered_cochain_dimensions_C3_C4_C5") != [727, 3084, 8532]
        or centered_cohomology.get("centered_differential_summary", {}).get("aggregate_nonzero_coefficients") != 85091
        or centered_cohomology.get("centered_differential_summary", {}).get("aggregate_ranks_d3_d4") != [636, 2446]
        or centered_cohomology.get("scope", {}).get("cohomology_dimension_H4") != 2
        or centered_cohomology.get("normalized_H4_representatives", {}).get("normalized_gram") != [[1, 0], [0, 1]]
        or centered_cohomology.get("claim_flags", {}).get("M6_CENTERED_REPRESENTATIVES_COMPLETE") is not True
        or centered_cohomology.get("claim_flags", {}).get("COMMON_GATE_A_FREEZE_BOUND") is not False
    ):
        errors.append("strict centered cohomology exact payload")
    if (
        residual_sdr_type_audit.get("result_id") != "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1"
        or len(residual_sdr_type_audit.get("type_census", {}).get("endpoint_row_ids", [])) != 30
        or residual_sdr_type_audit.get("type_census", {}).get("dfinite_total_full_coordinates") != 4490
        or residual_sdr_type_audit.get("type_census", {}).get("dfinite_total_residual_coordinates") != 470
        or residual_sdr_type_audit.get("type_census", {}).get("zero_mode_generator_coordinates") != 15
        or residual_sdr_type_audit.get("type_census", {}).get("zero_mode_dual_coordinates") != 15
        or residual_sdr_type_audit.get("claim_flags", {}).get("STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL") is not True
        or residual_sdr_type_audit.get("claim_flags", {}).get("DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL") is not False
        or residual_sdr_type_audit.get("claim_flags", {}).get("M3_TYPED_SPLIT_REQUIRED") is not True
    ):
        errors.append("strict residual SDR type-and-locality audit")
    gate_v18 = completion.get("strict_gate_v18_reconciliation", {})
    if (
        gate_v18.get("result_id") != gate_v18_source.get("result_id")
        or gate_v18.get("gate_a_status") != "FAIL_CLOSED"
        or gate_v18.get("accepted_top_level_hashes") != 1
        or gate_v18.get("remaining_top_level_hashes") != 6
        or gate_v18.get("M3_typed_split_required") is not True
        or gate_v18.get("M3L_common_endpoint_sdr_bound") is not False
        or gate_v18.get("M3R_typed_residual_comparison_constructed") is not False
        or gate_v18.get("minimal_missing_bundle") != ["M1_COMMON_STRICT_SNAPSHOT", "M3L_COMMON_ENDPOINT_SDR_BINDING", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"]
    ):
        errors.append("strict Gate V18 projection")
    if [item.get("route") for item in completion.get("route_selection", [])[:4]] != ["STRICT_COMMON_ENDPOINT_SDR_BINDING", "STRICT_FULL_CYCLIC_PAIRING", "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]:
        errors.append("strict V36 route frontier")
    result_flags = result.get("claim_flags", {})
    if result_flags.get("strict_residual_zero_mode_payload_exposed") is not True or result_flags.get("strict_residual_zero_mode_common_freeze_exposed") is not False:
        errors.append("site residual zero-mode exposure flags")
    if result_flags.get("strict_centered_cohomology_payload_exposed") is not True or result_flags.get("strict_centered_representative_common_freeze_exposed") is not False:
        errors.append("site centered cohomology exposure flags")
    if result_flags.get("strict_residual_sdr_type_audit_exposed") is not True or result_flags.get("strict_graph_endpoint_sdr_support_local_exposed") is not True or result_flags.get("strict_dfinite_residual_projector_support_local_exposed") is not False or result_flags.get("strict_m3_typed_split_exposed") is not True:
        errors.append("site residual SDR type-and-locality exposure flags")
    if result_flags.get("strict_graph_green_names_exposed") is not True or result_flags.get("strict_unary_causal_snapshot_exposed") is not True or result_flags.get("strict_full_d_action_exposed") is not True or result_flags.get("strict_d_q1_replay_exposed") is not True or result_flags.get("strict_stabilized_q2_candidate_exposed") is not True or result_flags.get("strict_stabilized_d_q2_derivation_exposed") is not True or result_flags.get("strict_candidate_q2_green_first_response_exposed") is not True or result_flags.get("strict_candidate_q2_green_foundations_exposed") is not True or result_flags.get("strict_candidate_polarized_finite_trees_exposed") is not True or result_flags.get("strict_first_mixed_sign_domain_nondefinition_exposed") is not True or result_flags.get("strict_candidate_polarized_formal_coefficients_exposed") is not True or result_flags.get("strict_lambda_adic_stabilization_exposed") is not True or result_flags.get("strict_lambda_squared_bv_promotion_gate_exposed") is not True or result_flags.get("strict_field_equation_green_component_exposed") is not True or result_flags.get("strict_field_equation_quotient_inverse_exposed") is not True or result_flags.get("strict_ungauge_fixed_full_inverse_obstruction_exposed") is not True or result_flags.get("strict_all_order_source_closure_exposed") is not False or result_flags.get("strict_authoritative_q2_green_compatibility_exposed") is not False or result_flags.get("strict_recursive_nonlinear_green_trees_exposed") is not False or result_flags.get("strict_unrestricted_mixed_sign_trees_exposed") is not False or result_flags.get("strict_arbitrary_causal_difference_trees_exposed") is not False or result_flags.get("strict_infinite_tree_series_convergence_exposed") is not False or result_flags.get("strict_typed_field_equation_green_inverse_exposed") is not False or result_flags.get("strict_weyl_bv_maurer_cartan_series_exposed") is not False or result_flags.get("strict_authoritative_formal_moller_map_exposed") is not False or result_flags.get("strict_analytic_moller_convergence_exposed") is not False or result_flags.get("strict_nonperturbative_moller_map_exposed") is not False or result_flags.get("strict_authoritative_full_carrier_q2_exposed") is not True or result_flags.get("strict_full_carrier_q2_exposed") is not True or result_flags.get("strict_classical_gate_a_passed") is not False:
        errors.append("site completion exposure flags")
    if result_flags.get("strict_q2_only_lambda2_source_obstruction_exposed") is not True or result_flags.get("strict_authoritative_q3_cancellation_target_exposed") is not True or result_flags.get("strict_pure_weyl_q3_witness_cancellation_exposed") is not True or result_flags.get("strict_lambda2_witness_full_source_closure_exposed") is not True or result_flags.get("strict_authoritative_minimal_q3_imported") is not True or result_flags.get("strict_minimal_arity_three_identity_exposed") is not True or result_flags.get("strict_minimal_q3_cyclicity_exposed") is not True or result_flags.get("strict_386_candidate_q3_stabilized") is not True or result_flags.get("strict_386_candidate_arity_three_identity_exposed") is not True or result_flags.get("strict_386_candidate_q3_cyclicity_exposed") is not True or result_flags.get("strict_386_candidate_D_q3_derivation_exposed") is not True or result_flags.get("strict_386_literal_trivial_stabilization_identity_refuted") is not True or result_flags.get("strict_386_linear_shear_theory_identity_refuted") is not True or result_flags.get("strict_386_candidate_internal_identities_preserved") is not True or result_flags.get("strict_386_nonlinear_equivalence_may_exist") is not True or result_flags.get("strict_386_nonlinear_equivalence_constructed") is not False or result_flags.get("strict_386_nonlinear_equivalence_obstructed") is not False or result_flags.get("strict_386_q3_stabilized") is not False or result_flags.get("strict_authoritative_q3_imported") is not True or result_flags.get("strict_386_authoritative_nonminimal_equivalence_exposed") is not False or result_flags.get("strict_386_candidate_causal_lambda2_source_closure_exposed") is not False or result_flags.get("strict_full_weyl_lambda2_source_closure_exposed") is not False or result_flags.get("strict_Berger_q3_direct_import_compatible") is not False:
        errors.append("site V26 nonlinear q3 frontier flags")
    if result_flags.get("strict_386_first_nonlinear_equivalence_component_constructed") is not True or result_flags.get("strict_386_f_hat_v_v_pullback_channel_closed") is not True or result_flags.get("strict_386_full_source_q2_pullback_replayed") is not True or result_flags.get("strict_386_full_source_q3_pullback_replayed") is not True:
        errors.append("site nonlinear auxiliary-elimination flags")
    if (
        result_flags.get("strict_386_known_required_cubic_families_enumerated") is not True
        or result_flags.get("strict_386_vv_bv_cotangent_lift_canonical") is not True
        or result_flags.get("strict_386_hh_hv_bv_cotangent_lift_component_complete") is not True
        or result_flags.get("strict_386_full_bv_cotangent_lift_serialized") is not True
        or result_flags.get("strict_386_full_quadratic_bv_cotangent_lift_serialized") is not True
        or result_flags.get("strict_386_diff_bv_representation_component_complete") is not True
        or result_flags.get("strict_386_seven_known_required_cubic_families_component_complete") is not True
        or result_flags.get("strict_386_exhaustive_full_nonlinear_bv_family_census") is not True
        or result_flags.get("strict_nonlinear_weyl_boost_ghost_manifest_complete") is not True
        or result_flags.get("strict_386_full_source_q2_assembled") is not True
    ):
        errors.append("site V32 auxiliary-census/source-assembly flags")
    if (
        result_flags.get("strict_386_diff_cstar_v2_repair_exposed") is not True
        or result_flags.get("strict_386_source_q2_common_hash_accepted") is not True
        or result_flags.get("strict_386_full_q1_q2_identity_exposed") is not True
        or result_flags.get("strict_386_full_q2_cyclicity_exposed") is not True
        or result_flags.get("strict_386_full_D_q2_derivation_exposed") is not True
    ):
        errors.append("site V33 q2 identity exposure flags")
    if (
        result_flags.get("strict_386_authoritative_full_q3_imported") is not True
        or result_flags.get("strict_386_full_arity_three_identity_exposed") is not True
        or result_flags.get("strict_386_full_q3_cyclicity_exposed") is not True
        or result_flags.get("strict_386_full_D_q3_derivation_exposed") is not True
        or result_flags.get("strict_authoritative_q3_imported") is not True
        or result_flags.get("strict_386_full_source_q3_pullback_replayed") is not True
        or result_flags.get("strict_classical_gate_a_passed") is not False
    ):
        errors.append("site V33 authoritative q3 exposure/firewall flags")
    if viability.get("source_atlas_digest") != data.get("canonical_digest") or viability.get("canonical_digest") != result.get("independent_checker", {}).get("expected_viability_digest"):
        errors.append("theory viability source/digest pin")
    if len(viability.get("profiles", [])) != 36 or len(viability.get("carrier_envelopes", [])) != 6:
        errors.append("theory viability profile/envelope closure")
    interfaces = data.get("cross_cell_interfaces", [])
    if [item.get("id") for item in interfaces] != ["STATE_TO_PROBABILITY", "SELECTION_TO_DYNAMICS"] or any(item.get("status") != "CERTIFIED" or item.get("relation") != "CONDITIONAL_BRIDGE" for item in interfaces):
        errors.append("certified cross-cell interface projection")
    carrier_interfaces = data.get("carrier_interfaces", [])
    if [item.get("id") for item in carrier_interfaces] != ["EUCLIDEAN_TO_KREIN_CARRIER"] or carrier_interfaces[0].get("relation") != "INCOMPATIBLE" or carrier_interfaces[0].get("status") != "CERTIFIED":
        errors.append("certified carrier interface projection")
    numerical_records = data.get("numerical_reproducibility_records", [])
    if len(numerical_records) != 1 or numerical_records[0].get("status") != "COARSE_REPRODUCTION_ONLY" or numerical_records[0].get("continuum_status") != "NOT_ESTABLISHED":
        errors.append("numerical reproduction boundary")
    if assemblies.get("source_atlas_digest") != data.get("canonical_digest") or assemblies.get("canonical_digest") != result.get("independent_checker", {}).get("expected_assembly_digest"):
        errors.append("theory assembly source/digest pin")
    if len(assemblies.get("assemblies", [])) != 9 or any(len(item.get("selected_cells", [])) != 16 or len(item.get("interfaces", [])) != 7 or len(item.get("maturity_rails", [])) != 7 for item in assemblies.get("assemblies", [])):
        errors.append("theory assembly prototype/cell/interface closure")
    if any(not item.get("camp_summary") or not item.get("central_question") or len(item.get("lineage", [])) != 3 or len(item.get("signature_ideas", [])) != 3 or not item.get("atlas_window") or not item.get("scope_note") for item in assemblies.get("assemblies", [])):
        errors.append("research-camp exposition closure")
    if assemblies.get("certified_carrier_interface_records") != carrier_interfaces or assemblies.get("numerical_reproducibility_ledger", {}).get("records") != numerical_records:
        errors.append("carrier/numerical assembly projection")
    if assemblies.get("empirical_ledger", {}).get("records") != [] or any(item.get("complete_theory") is not False or item.get("empirically_supported") is not False for item in assemblies.get("assemblies", [])):
        errors.append("theory assembly fail-closed boundary")
    controls = assemblies.get("calibration_controls", [])
    if len(controls) != 1 or controls[0].get("kind") != "EXTERNAL_POSITIVE_CONTROL" or len(controls[0].get("records", [])) != 4:
        errors.append("external positive-control closure")
    if any(rail.get("status") in {"BLOCKED", "FAILED"} for item in assemblies.get("assemblies", []) for rail in item.get("maturity_rails", [])):
        errors.append("missing work mislabeled as failure")
    model_assemblies = assemblies.get("model_scoped_assemblies", [])
    model_by_id = {item.get("result_id"): item for item in model_assemblies}
    if len(model_assemblies) != 2 or set(model_by_id) != {"FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1", "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1"}:
        errors.append("model-scoped assembly closure")
    else:
        if model_by_id["FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1"].get("assembly_disposition") != {"status": "BOUNDED_PREDICTION_ASSEMBLY_COMPLETE", "complete_within_declared_scope": True, "empirically_supported_within_declared_scope": True, "complete_theory": False}:
            errors.append("GR model-scoped bounded disposition")
        mannheim_disposition = model_by_id["FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1"].get("assembly_disposition", {})
        if mannheim_disposition.get("status") != "BOUNDED_ASSEMBLY_PARTIAL_MIXED_COMPARISON" or mannheim_disposition.get("formula_endpoint_coarsely_reproduced") is not True or mannheim_disposition.get("cross_dataset_coarse_shape_gate_passed") is not True or mannheim_disposition.get("cross_dataset_random_error_gate_passed") is not False or mannheim_disposition.get("empirically_supported_within_declared_scope") is not False:
            errors.append("Mannheim mixed bounded disposition")
    comparisons = assemblies.get("model_comparisons", [])
    if len(comparisons) != 1 or comparisons[0].get("result_id") != "FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1" or comparisons[0].get("ranking_by_AICc", [None])[0] != "GR_NFW_DARK_HALO" or comparisons[0].get("claim_flags", {}).get("complete_theory_selected") is not False:
        errors.append("common-protocol model comparison closure")

    calculated_digest = digest(data)
    if calculated_digest != data.get("canonical_digest") or calculated_digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical data digest")
    if (SITE / "data.js").read_bytes() != b"window.MATRIX_EXPLORER_DATA = " + DATA.read_bytes().rstrip() + b";\n":
        errors.append("self-contained data assignment")
    for output in manifest.get("outputs", []):
        path = ROOT / output.get("path", "")
        if not path.is_file() or sha(path) != output.get("sha256") or path.stat().st_size != output.get("bytes"):
            errors.append("manifest output " + str(output.get("path")))
    for source in manifest.get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or sha(path) != source.get("sha256"):
            errors.append("manifest input " + str(source.get("path")))

    html = (SITE / "index.html").read_text()
    app = (SITE / "app.js").read_text() + (SITE / "migration-review.js").read_text() + (SITE / "assemblies.js").read_text()
    if "https://" in html or "http://" in html or '<script src="data.js"></script>' not in html or '<script src="viability.js"></script>' not in html or '<script src="assemblies.js"></script>' not in html or '<script src="migration-review.js"></script>' not in html:
        errors.append("offline/no-remote-code shell")
    for token in ("matrixGroups", "viabilityView", "Theory profiles", "Coverage readiness map", "Coverage envelope, not a composed theory", "No complete observationally validated theory is certified", "paretoProfiles", "assembliesView", "Bounded model tests", "Research programmes", "Interfaces & calibration", "assemblyPanel", "Bounded assembly complete", "Field equations to Cassini", "Weyl action to NGC 3198", "random-error gate failed", "No parameter is refitted", "SPARC", "Meet the research programmes", "Bateman–Turok", "Mannheim conformal gravity", "Pure-Weyl BV–BFV", "Central question", "Important boundary", "Applicability mask", "Seven independent maturity rails", "Eight independent maturity rails", "Numerical reproduction is not empirical validation", "Euclidean/Krein carrier boundary", "External positive control", "Typed interface ledger", "Empirical benchmark ledger", "NOT_ASSESSED", "guideView", "dimensionGuide", "Every result answers three different questions", "Rules", "Container", "Job", "Why “general relativity works” is too compressed", "The question changes even when the equation does not", "Small glossary", "Axiom of Choice", "For reviewers: how the evidence letters and migration audit work", "Regime × carrier × obligation", "Reviewed gap versus priority gap", "graphView", "GRAPH_PATHWAYS", "Relation ledger", "graph-edge-hit", "No direct certificate yet", "ladderView", "evidenceView", "compareDialog", "exportJson", "exportCsv", "downloadBrief", "column-label", "Migration review", "migration_evidence", "175-coordinate surface audit", "data-dual", "directKinds", "role-badge", "Local + literature result", "Directness unreviewed", "data-marklen", "supportingKinds", "legend-note"):
        if token not in html + app:
            errors.append("interface token " + token)
    if "No stronger interpretation is licensed" in app:
        errors.append("legacy graph fallback")
    for token in ("NGC 3198 head-to-head control", "Scoped winner: GR + NFW", "Why RMS and χ² disagree", "FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1"):
        if token not in app:
            errors.append("common-fit interface token " + token)
    for token in ("completionView", "Weyl BV routes", "completionExplorer", "77 separately typed cells", "Where effort has the highest expected value", "RANK_ONLY_FEASIBLE", "general non-cone 104-row no-go", "Finite residual control", "Gate A still closed", "Gate V18", "Residual coefficient gap closed", "normalized dual modes are now portable", "Exact is not yet common-bound", "Centered representative gap closed", "ordered C3/C4/C5 basis elements", "85,091", "dim H4=", "C3 and C5 are carriers, not cohomology claims", "A misleading route removed", "Three different carriers were all being called", "M3L", "M3R", "STRICT_COMMON_ENDPOINT_SDR_BINDING", "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", "STRICT_FULL_CYCLIC_PAIRING", "Cubic family census and vv lift", "Curved quadratic canonical lift completed", "Component frontier completed", "Primary-source surprise", "The missing nonlinear ghost manifest adds no new families", "Common source q2 accepted", "Authoritative source q3 completed", "605 Ward checks", "336 → 0", "1392", "3907", "264", "336", "632", "704", "22", "16", "four pairing slices", "Causal convention crosswalk", "Endpoint search completed", "arrow_tables_matching", "bach_columns_matching", "619", "Suspension question resolved", "54", "30", "376", "10", "Full component pairing serialized", "356=36+320", "410", "Three portability contracts", "FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION", "Complete unary snapshot", "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "Exact split local SDR", "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1", "H_alg", "190", "Canonical coordinate bridge certified", "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "1321", "A(-Tsharp)", "T(-Asharp)", "Represented Green action certified", "Hodge eigenspace projectors", "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1", "Scoped common snapshot accepted", "hashes bind one unary-causal carrier", "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1", "Full cylinder flow certified", "STRICT_386_FULL_D_ACTION_V1", "4374", "Fourteen hashes", "Algebraic q2 lift certified", "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "140", "68", "Finite polarized recursion certified", "Every retarded tree", "38", "40", "Two four-leaf terms", "Formal coefficients certified", "Two unique λ-adic series", "The first BV promotion gap is at λ²", "1430", "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION", "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1", "The quadratic-only λ² source is not closed", "Cubic regression witness", "Minimal cubic L∞ package completed", "Full-graph cubic candidate certified", "Valid construction, unproven identity", "STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1", "Theory-identity test decided", "STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1", "source-minus-candidate defect", "First nonlinear correction constructed", "STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1", "72", "212", "S4", "41", "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP", "37880/27", "-75760/9", "graph coordinates"):
        if token not in html + app + json.dumps(data):
            errors.append("completion interface token " + token)

    status_counts = Counter(x.get("status") for x in cells)
    all_migrations = Counter(x.get("migration_status") for x in cells)
    counts = data.get("counts", {})
    normalized_status_counts = {status: status_counts.get(status, 0) for status in sorted(STATUSES)}
    if counts.get("status_counts") != normalized_status_counts or counts.get("migration_status_counts") != dict(sorted(all_migrations.items())):
        errors.append("coverage/migration counts")
    if counts.get("coverage_classified") != 576 or counts.get("migration_reviewed") != 576 or counts.get("migration_pending") != 0 or counts.get("reviewed_gap") != 169 or counts.get("not_mapped") != 0 or counts.get("evidence_records") != 83:
        errors.append("review count summary")
    summary = {
        "digest": calculated_digest,
        "cells": len(cells),
        "emitted": len(emitted),
        "synthetic_not_mapped": len(synthetic),
        "total_not_mapped": status_counts["NOT_MAPPED"],
        "coverage_classified": counts.get("coverage_classified"),
        "migration_reviewed": counts.get("migration_reviewed"),
        "migration_pending": counts.get("migration_pending"),
        "reviewed_no_transfer": migration_counts["REVIEWED_NO_TRANSFER"],
        "evidence_records": len(evidence),
        "graph_edges": len(graph.get("edges", [])),
        "ladder_levels": len(data.get("ladder", [])),
        "completion_branches": len(completion.get("branches", [])),
        "completion_stages": len(completion.get("stages", [])),
        "completion_cells": sum(len(item.get("stages", [])) for item in completion.get("branches", [])),
        "completion_routes": len(completion.get("route_selection", [])),
        "completion_decisions": len(completion.get("berger_h26_c26_decision_chain", [])),
        "theory_profiles": len(viability.get("profiles", [])),
        "carrier_envelopes": len(viability.get("carrier_envelopes", [])),
        "pareto_profiles": sum(item.get("pareto_default") is True for item in viability.get("profiles", [])),
        "prototype_assemblies": len(assemblies.get("assemblies", [])),
        "assembly_interfaces": sum(len(item.get("interfaces", [])) for item in assemblies.get("assemblies", [])),
        "empirical_comparisons": len(assemblies.get("empirical_ledger", {}).get("records", [])),
        "calibration_comparisons": sum(len(item.get("records", [])) for item in assemblies.get("calibration_controls", [])),
        "calibration_benchmark_families": sum(item.get("status") == "SUPPORTED_CONTROL" for control in assemblies.get("calibration_controls", []) for item in control.get("benchmark_coverage", [])),
        "model_scoped_assemblies": len(assemblies.get("model_scoped_assemblies", [])),
        "model_scoped_stages": sum(len(item.get("stages", [])) for item in assemblies.get("model_scoped_assemblies", [])),
        "model_scoped_interfaces": sum(len(item.get("interfaces", [])) for item in assemblies.get("model_scoped_assemblies", [])),
        "bounded_complete_assemblies": sum(item.get("assembly_disposition", {}).get("complete_within_declared_scope") is True for item in assemblies.get("model_scoped_assemblies", [])),
        "certified_cross_cell_interfaces": len(interfaces),
        "certified_carrier_interfaces": len(carrier_interfaces),
        "numerical_reproduction_records": len(numerical_records),
        "certified_assembly_interface_instances": sum(interface.get("certification_status") == "CERTIFIED" for assembly in assemblies.get("assemblies", []) for interface in assembly.get("interfaces", [])),
        "dual_direct_cells": dual,
        "mark_counts": dict(sorted(marks.items())),
    }
    return errors, summary


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
