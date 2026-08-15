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
COMPLETION_ATLAS = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12.json"
STATUSES = {"LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"}
MIGRATIONS = {"EXACT_PARENT_TRANSFER", "CAPABILITY_QUALIFIED", "REVIEWED_OVERLAY", "REVIEWED_NO_TRANSFER", "REVIEWED_CHILD_GAP", "DIRECT_COORDINATE_REVIEW", "NOT_REVIEWED"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data: dict[str, Any]) -> str:
    projection = {key: data[key] for key in ("axes", "cells", "evidence", "ladder", "graph", "completion_atlas", "cross_cell_interfaces", "carrier_interfaces", "numerical_reproducibility_records")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(data: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    data = load(DATA) if data is None else data
    cube, ladder, completion_source, result, manifest, viability, assemblies = load(CUBE), load(LADDER), load(COMPLETION_ATLAS), load(RESULT), load(MANIFEST), load(VIABILITY), load(ASSEMBLIES)
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
    if len(completion.get("branches", [])) != 7 or len(completion.get("stages", [])) != 11 or sum(len(item.get("stages", [])) for item in completion.get("branches", [])) != 77:
        errors.append("Lorentzian completion branch/stage closure")
    if len(completion.get("route_selection", [])) != 9 or len(completion.get("berger_h26_c26_decision_chain", [])) != 11:
        errors.append("Lorentzian completion route/decision closure")
    completion_flags = completion.get("claim_flags", {})
    if completion_flags.get("general_noncone_104_row_no_go") is not False or completion_flags.get("lorentzian_full_theory_certified") is not False:
        errors.append("Lorentzian completion fail-closed boundary")
    if completion.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12":
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
    if completion_flags.get("strict_386_canonical_shear_component_jets_serialized") is not False or completion_flags.get("strict_386_unshifted_graph_sdr_snapshot_complete") is not False or completion_flags.get("strict_386_represented_green_actions_serialized") is not False:
        errors.append("strict split local-SDR successor firewall")
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
    for token in ("completionView", "Weyl BV routes", "completionExplorer", "77 separately typed cells", "Where effort has the highest expected value", "RANK_ONLY_FEASIBLE", "general non-cone 104-row no-go", "Finite residual control", "Gate A still closed", "Gate V5", "Causal convention crosswalk", "Endpoint search completed", "arrow_tables_matching", "bach_columns_matching", "619", "Suspension question resolved", "54", "30", "376", "10", "Full component pairing serialized", "356=36+320", "410", "Three portability contracts", "FINITE_COMPONENT_JET_TABLE", "FINITE_SPARSE_COMPONENT_MAP", "ANALYTIC_GREEN_ACTION", "Complete unary snapshot", "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "Exact split local SDR", "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1", "H_alg", "190", "graph coordinates"):
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
