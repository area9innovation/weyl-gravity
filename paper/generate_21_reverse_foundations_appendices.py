#!/usr/bin/env python3
"""Generate the static atlas appendices for paper 21 from the website dataset."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/site/data.json"
ASSEMBLY_SOURCE = ROOT / "foundations/site/assemblies.json"
OUTPUT = ROOT / "paper/21-reverse-foundations-of-physics-appendices.tex"

STATUS_ORDER = [
    "LOCAL_RESULT",
    "LITERATURE_RESULT",
    "PIECES_ONLY",
    "PRIORITY_GAP",
    "REVIEWED_GAP",
    "NOT_MAPPED",
]
STATUS_SHORT = {
    "LOCAL_RESULT": "Local",
    "LITERATURE_RESULT": "Literature",
    "PIECES_ONLY": "Pieces",
    "PRIORITY_GAP": "Priority gap",
    "REVIEWED_GAP": "Reviewed gap",
    "NOT_MAPPED": "Not mapped",
}
RELATION_LABEL = {
    "SUFFICIENT": "Enough for this step",
    "CONDITIONAL_SUFFICIENT": "Enough with conditions",
    "REPRESENTATION_DEPENDENT": "Depends on the coding",
    "COUNTEREXAMPLE_TO_METHOD": "This method fails",
    "LITERATURE_CONTRAST": "Literature contrast",
    "OPEN_IMPLICATION": "Unproved bridge",
    "NOT_SUFFICIENT": "Not enough by itself",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tex(value: object) -> str:
    text = str(value)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("×", r"\(\times\)"),
        ("→", r"\(\rightarrow\)"),
        ("—", "---"),
        ("–", "--"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def scientific_tex(value: object) -> str:
    """Escape prose while typesetting the small certified formula vocabulary."""
    text = tex(value)
    for plain, formula in [
        (r"G\_mu\_nu=0", r"\(G_{\mu\nu}=0\)"),
        ("f(r)=1-2m/r", r"\(f(r)=1-2m/r\)"),
        ("beta=gamma=1", r"\(\beta=\gamma=1\)"),
        ("gamma-1=0", r"\(\gamma-1=0\)"),
        ("1+gamma=2", r"\(1+\gamma=2\)"),
        ("gamma+1", r"\(\gamma+1\)"),
    ]:
        text = text.replace(plain, formula)
    return text


def joined(values: list[str] | None) -> str:
    return tex("; ".join(values or []) if values else "---")


def cert(value: str) -> str:
    return rf"\cert{{{value}}}"


def evidence_boundary(entry: dict) -> str:
    if entry.get("boundary"):
        return entry["boundary"]
    return "Does not establish: " + "; ".join(entry.get("does_not_establish", [])) + "."


def evidence_support(entry: dict) -> str:
    if entry["kind"] == "LITERATURE":
        return "; ".join(entry["supported_statements"])
    positive_flags = [name for name, enabled in entry.get("claim_flags", {}).items() if enabled]
    return "Certified positive flags: " + "; ".join(
        name.replace("_", " ") for name in positive_flags
    ) + "."


def axis_lookup(data: dict) -> dict[str, dict]:
    return {entry["id"]: entry for axis in data["axes"] for entry in axis["keys"]}


def emit_axis_table(lines: list[str], axis: dict) -> None:
    lines.extend(
        [
            rf"\subsubsection{{{tex(axis['question'])}}}",
            r"\begingroup",
            r"\small",
            r"\begin{longtable}{@{}p{0.29\textwidth}p{0.65\textwidth}@{}}",
            r"\toprule",
            r"Option & Plain-language purpose \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Option & Plain-language purpose \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for option in axis["keys"]:
        lines.append(rf"{tex(option['label'])} & {tex(option.get('plain_meaning', option['meaning']))} \\")
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])


def coverage_counts(cells: list[dict], field: str, value: str) -> collections.Counter:
    return collections.Counter(cell["status"] for cell in cells if cell[field] == value)


def build(data: dict, assemblies: dict) -> str:
    axes = {axis["id"]: axis for axis in data["axes"]}
    completion = data["completion_atlas"]
    endpoint_sdr_binding = data["completion_common_endpoint_sdr_binding"]
    residual_comparison = data["completion_endpoint_to_residual_comparison"]
    residual_cyclic_obstruction = data["completion_residual_cyclic_carrier_obstruction"]
    dfinite_cotangent_dual = data["completion_dfinite_cotangent_dual_comparison"]
    local_cyclic_pairing = data["completion_local_cyclic_pairing"]
    residual_zero_modes = data["completion_residual_zero_modes"]
    centered = data["completion_centered_cohomology"]
    residual_sdr_type_audit = data["completion_residual_sdr_type_audit"]
    labels = axis_lookup(data)
    cells = data["cells"]
    evidence = data["evidence"]
    nodes = {node["id"]: node for node in data["graph"]["nodes"]}
    direct_evidence_ids: list[str] = []
    for edge in data["graph"]["edges"]:
        direct_evidence_ids.extend(edge.get("evidence", []))
    for step in data["ladder"]:
        if step.get("source"):
            direct_evidence_ids.append(step["source"])
    direct_evidence_ids = list(dict.fromkeys(direct_evidence_ids))
    evidence_usage = {
        evidence_id: {"cells": [], "graph": [], "ladder": []}
        for evidence_id in evidence
    }
    for cell in cells:
        for evidence_id in cell.get("evidence", []):
            evidence_usage[evidence_id]["cells"].append(cell)
    for edge_number, edge in enumerate(data["graph"]["edges"], start=1):
        for evidence_id in edge.get("evidence", []):
            evidence_usage[evidence_id]["graph"].append(edge_number)
    for step in data["ladder"]:
        if step.get("source"):
            evidence_usage[step["source"]]["ladder"].append(step["level"])
    evidence_anchor = {
        evidence_id: f"atlas-evidence-{number}"
        for number, evidence_id in enumerate(sorted(evidence), start=1)
    }

    lines = [
        "% Generated by paper/generate_21_reverse_foundations_appendices.py.",
        f"% Source SHA256: {sha256(SOURCE)}",
        r"\section{Static companion to the evidence atlas}",
        r"\label{app:atlas-companion}",
        "",
        "The interactive atlas exposes seven views of the same normalized evidence and derived assessments: matrix, dimensions guide, theory profiles, assemblies, typed implications, strength ladder, and evidence catalogue.  This appendix preserves their key research content in a citable static form.  It is a snapshot, not a replacement for cell inspection, filtering, neighboring-cell comparison, or the complete downloadable dataset.",
        "",
        r"\begin{center}",
        r"\small",
        r"\begin{tabularx}{\textwidth}{@{}p{0.20\textwidth}Y@{}}",
        r"\toprule",
        r"Website view & Static counterpart \\",
        r"\midrule",
        r"Matrix & Overall counts, a \(6\times6\) three-way coverage roll-up, and status counts for every obligation. \\",
        r"Dimensions guide & All 28 axis options with their non-specialist descriptions. \\",
        r"Theory profiles & Coverage-envelope and Pareto navigation; these are not composed theories. \\",
        r"Assemblies & Nine cube-selected prototypes, two model-scoped chains with independent maturity rails, typed joins, and an external standard-GR calibration control. \\",
        r"Implications & The complete typed relation ledger: ten directed edges with their exact assertion and evidence. \\",
        r"Strength ladder & All six cylinder-wave gates, including what each adds, establishes, and leaves open. \\",
        rf"Evidence & The complete literature register, local-certificate register, and usage crosswalk for all {len(evidence)} records. \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{center}",
        "",
        r"\subsection{Dimensions guide}",
        r"\label{app:dimensions-guide}",
        "Every coordinate combines one foundational regime, one carrier, and one theorem-level obligation.  The tables below reproduce the website's plain-language guide rather than assuming the reader already knows the programme vocabulary.",
        "",
    ]
    for axis_id in ["FOUNDATION", "CARRIER", "REFINED_OBLIGATION"]:
        emit_axis_table(lines, axes[axis_id])

    lines.extend(
        [
            r"\subsection{Matrix overview}",
            r"\label{app:matrix-overview}",
            r"The full atlas has 576 coordinates.  The website exposes sixteen \(6\times6\) slices, one for each obligation.  For print, Table~\ref{tab:aggregate-matrix} aggregates those slices without implying that the statuses are truth values.  Each entry is \emph{direct / seeded / reviewed / unmapped}: direct combines local and reviewed literature results; seeded combines pieces-only and priority-gap cells; reviewed means a formulated open question with a typed missing certificate but no direct result; unmapped means that no coverage classification is made.",
            "",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{2pt}",
            r"\begin{tabular}{@{}p{0.20\textwidth}rrrrrr@{}}",
            r"\toprule",
            r"Regime \(\downarrow\) / carrier \(\rightarrow\) & Finite exact & Hilbert & Krein & Algebraic & PDE & Localic \\",
            r"\midrule",
        ]
    )
    carriers = axes["CARRIER"]["keys"]
    obligations = axes["REFINED_OBLIGATION"]["keys"]
    for foundation in axes["FOUNDATION"]["keys"]:
        row = [tex(foundation["label"])]
        for carrier in carriers:
            subset = [
                c for c in cells
                if c["foundation"] == foundation["id"] and c["carrier"] == carrier["id"]
            ]
            counts = collections.Counter(c["status"] for c in subset)
            direct = counts["LOCAL_RESULT"] + counts["LITERATURE_RESULT"]
            seeded = counts["PIECES_ONLY"] + counts["PRIORITY_GAP"]
            row.append(f"{direct}/{seeded}/{counts['REVIEWED_GAP']}/{counts['NOT_MAPPED']}")
        lines.append(" & ".join(row) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Aggregate coverage matrix.  Each cell reports direct results / open cells with a starting point / reviewed open gaps / not mapped, across all sixteen obligations.}",
            r"\label{tab:aggregate-matrix}",
            r"\end{table}",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.27\textwidth}rrrrrrr@{}}",
            r"\caption{Coverage status by physical obligation.  Every row sums to 36.}\label{tab:obligation-coverage}\\",
            r"\toprule",
            r"Obligation & Local & Literature & Pieces & \shortstack{Priority\\gap} & \shortstack{Reviewed\\gap} & \shortstack{Not\\mapped} & Total \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Obligation & Local & Literature & Pieces & \shortstack{Priority\\gap} & \shortstack{Reviewed\\gap} & \shortstack{Not\\mapped} & Total \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for obligation in obligations:
        counts = coverage_counts(cells, "obligation", obligation["id"])
        values = [counts[s] for s in STATUS_ORDER]
        lines.append(
            f"{tex(obligation['label'])} & " + " & ".join(str(v) for v in values) + f" & {sum(values)}" + r" \\"
        )
    total = collections.Counter(c["status"] for c in cells)
    values = [total[s] for s in STATUS_ORDER]
    lines.extend(
        [
            r"\midrule",
            "All obligations & " + " & ".join(str(v) for v in values) + f" & {sum(values)}" + r" \\",
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            f"A local or literature result remains bounded by its attached claim boundary.  Pieces-only means relevant ingredients do not yet compose the target.  Priority gap marks a selected current-programme gap.  Reviewed gap marks an explicitly formulated open question with a typed missing certificate, not a result or literature-absence claim.  The atlas has {total['REVIEWED_GAP']} reviewed gaps and {total['NOT_MAPPED']} not-mapped coordinates; all {len(cells)} coordinates are emitted by the authoritative cube.",
            "",
            r"\subsection{Typed implication ledger}",
            r"\label{app:implication-ledger}",
            r"The implication view is directional.  Table~\ref{tab:implication-ledger} is the authoritative print reading of its arrows: the relation column says how the edge may be used, and the assertion column says exactly what has and has not crossed that edge.",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.15\textwidth}p{0.16\textwidth}p{0.15\textwidth}p{0.36\textwidth}p{0.12\textwidth}@{}}",
            r"\caption{Complete typed relation ledger from the implications tab.}\label{tab:implication-ledger}\\",
            r"\toprule",
            r"From & Relation & To & Exact assertion & Evidence \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"From & Relation & To & Exact assertion & Evidence \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for edge in data["graph"]["edges"]:
        evidence_text = "; ".join(cert(item) for item in edge.get("evidence", [])) or "Open bridge---no direct certificate"
        lines.append(
            f"{tex(nodes[edge['from']]['label'])} & {tex(RELATION_LABEL[edge['relation']])} & "
            f"{tex(nodes[edge['to']]['label'])} & {tex(edge['meaning'])} & {evidence_text}" + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            r"\subsection{Cylinder-wave strength ladder}",
            r"\label{app:strength-ladder}",
            "The ladder prevents a certified lower level from being read as a theorem at a stronger level.  ``Adds'' names the new mathematical data at the gate; ``establishes'' records the result available there; and ``still open or excluded'' blocks silent promotion.",
            "",
            r"\begingroup",
            r"\footnotesize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.29\textwidth}p{0.20\textwidth}p{0.20\textwidth}p{0.23\textwidth}@{}}",
            r"\caption{All six gates in the cylinder-wave strength ladder.}\label{tab:strength-ladder}\\",
            r"\toprule",
            r"Gate, object, and sufficient base & Adds & Establishes & Still open or excluded \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Gate, object, and sufficient base & Adds & Establishes & Still open or excluded \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for step in data["ladder"]:
        base = step.get("sufficient_base", step.get("candidate_upper_bound", "Not classified"))
        established = step.get("establishes", step.get("establishes_if_formalized", []))
        open_items = step.get("open", step.get("does_not_establish", []))
        if not open_items and step.get("boundary"):
            open_items = [step["boundary"]]
        if step.get("source_boundary"):
            open_items = list(open_items) + [step["source_boundary"]]
        object_and_base = f"{step['object']}. Base: {base}."
        if step.get("separation"):
            object_and_base += " " + step["separation"]
        lines.append(
            f"{cert(step['level'])} / {cert(step['status'])}. {tex(object_and_base)} & "
            f"{joined(step.get('adds'))} & {joined(established)} & {joined(open_items)}" + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            r"\subsection{Lorentzian Weyl BV completion routes}",
            r"\label{app:lorentzian-weyl-completion}",
            rf"The completion atlas keeps eleven lifecycle stages separate on seven candidate architectures.  None of the branches is a completed Lorentzian quantum theory.  The strict 386-row branch now has an exact graph-coordinate unary differential, a common-bound local endpoint SDR, transported suspension, represented advanced/retarded Green names, the local cylinder-flow action, linked common source q2/q3 snapshots, and a complete local cyclic pairing.  The M3L manifest pins {len(endpoint_sdr_binding['common_manifest']['artifact_pins'])} artifacts and {len(endpoint_sdr_binding['common_manifest']['object_hashes'])} canonical object hashes; all {endpoint_sdr_binding['exact_replay']['compatibility_links_checked']} compatibility links agree and every projected defect is zero.  M4L has exact pairing rank {local_cyclic_pairing['pairing_replay']['exact_rational_rank']} on {local_cyclic_pairing['pairing_replay']['carrier_rows']} local rows with {local_cyclic_pairing['pairing_replay']['nonzero_ordered_pairing_entries']} ordered entries, and all declared q1/SDR/D/q2/q3 local cyclicity defects vanish.  M3R compares {residual_comparison['comparison']['source']['total_dimension']:,} represented endpoint-complex coefficients with {residual_comparison['comparison']['target']['dimension']} W+/W- residual coordinates at energies two through six; its E/A/L magnetic crosswalk, retraction, and q0 chain identities have zero defects.  Direct M4R on that one-sided degree-zero target is nevertheless obstructed: the induced degree-minus-one odd form has exact rank {residual_cyclic_obstruction['obstruction_replay']['pulled_back_odd_pairing_rank']} and nullity {residual_cyclic_obstruction['obstruction_replay']['pulled_back_odd_pairing_nullity']}.  M3RC-A is now exact: the unchanged {dfinite_cotangent_dual['same_source_impossibility']['original_source_full_dimension']:,}-coordinate source has H0={dfinite_cotangent_dual['same_source_impossibility']['original_source_degree_zero_cohomology_dimension']} and H1={dfinite_cotangent_dual['same_source_impossibility']['original_source_degree_one_cohomology_dimension']}, so it cannot retract onto the doubled residual carrier; the declared {dfinite_cotangent_dual['formal_cotangent_completion']['full_dimension']:,}-coordinate shifted cotangent complex instead retracts exactly onto {dfinite_cotangent_dual['formal_cotangent_completion']['residual_dimension']} coordinates with full/residual pairing ranks {dfinite_cotangent_dual['formal_cotangent_completion']['full_pairing_rank']:,}/{dfinite_cotangent_dual['formal_cotangent_completion']['residual_pairing_rank']} and zero declared defects.  M3RC-B remains open because no selected support/topology dual or harmonic integration theorem identifies that formal algebraic dual with the action-derived BV dual.  Harmonic restriction remains global rather than support-local, and Gate A and q2/q3 Green compatibility remain fail closed.",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}rp{0.25\textwidth}p{0.12\textwidth}p{0.12\textwidth}p{0.39\textwidth}@{}}",
            rf"\caption{{Ranked next certificates in Lorentzian Weyl BV completion atlas V{completion['result_id'].rsplit('_V', 1)[1]}.}}\label{{tab:lorentzian-weyl-completion-routes}}\\",
            r"\toprule",
            r"Rank & Route & Leverage & Tractability & Decisive deliverable \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Rank & Route & Leverage & Tractability & Decisive deliverable \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for route in completion["route_selection"]:
        lines.append(
            f"{route['rank']} & {cert(route['route'])} & {tex(route['scientific_leverage'])} & "
            f"{tex(route['tractability'])} & {tex(route['recommendation'])}" + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            rf"The graph-coordinate unary object contains {completion['strict_graph_q1_sdr_component_jets']['operator_tables']} operator tables and {completion['strict_graph_q1_sdr_component_jets']['nonzero_rational_coefficients']:,} exact nonzero coefficients.  Its SDR contains {completion['strict_graph_q1_sdr_component_jets']['H_alg_nonzero_entries']} homotopy entries and replays all {completion['strict_graph_q1_sdr_component_jets']['combined_derivative_multiindices']} unary multiindices with zero direct retract defects.  The transported suspension has {completion['strict_graph_q1_sdr_component_jets']['transported_suspension_entries']} entries; the obsolete diagonal form has {completion['strict_graph_q1_sdr_component_jets']['old_diagonal_suspension_cyclicity_defects']} graph-cyclicity defects.",
            "",
            rf"The represented Green result uses {completion['strict_graph_green_action_name']['spatial_spectral_branches']} canonical Hodge spectral branches and a rank-{completion['strict_graph_green_action_name']['tractor_rank']} parent action, with the zero mode explicit.  Its distinct retarded and advanced names act on the endpoint and full graph, but are neither effective numerical solvers nor serialized distribution kernels.  The original unary-causal snapshot binds {completion['strict_unary_causal_common_snapshot']['accepted_hashes']} hashes on {completion['strict_unary_causal_common_snapshot']['carrier_rows']} rows; the exact real cylinder flow \(T=\partial_t\) extends this to {completion['strict_full_d_action']['scoped_snapshot_hashes']} hashes.  Its {completion['strict_full_d_action']['D_coefficients']} local entries commute with all {completion['strict_full_d_action']['q1_coefficients_checked']:,} checked q1 coefficients and are formally skew on {completion['strict_full_d_action']['pairing_entries_checked']} pairing entries, with zero defects in both replays.  The accepted source q2 has {completion['strict_source_q2_common_assembly']['source_q2_families']} families, {completion['strict_source_q2_common_assembly']['minimal_ordered_symbolic_components']} minimal symbolic operations, and {completion['strict_source_q2_common_assembly']['auxiliary_ordered_component_coefficients']:,} auxiliary coefficients.  Its q1/q2, cyclicity, and D/q2 defect counts are {completion['strict_source_q2_common_assembly']['q1_q2_defects']}, {completion['strict_source_q2_common_assembly']['q2_cyclicity_defects']}, and {completion['strict_source_q2_common_assembly']['D_q2_defects']}.  The historical c-star convention left {completion['strict_source_q2_common_assembly']['rejected_v1_q1_q2_defects']} exact defects; the accepted translation leaves {completion['strict_source_q2_common_assembly']['accepted_v2_q1_q2_defects']}.  The accepted source q3 has {completion['strict_source_q3_common_assembly']['source_q3_families']} exhaustive families and {completion['strict_source_q3_common_assembly']['auxiliary_ordered_q3_coefficients']:,} auxiliary coefficients.  It closes {completion['strict_source_q3_common_assembly']['cyclic_equalities_checked']:,} pointwise cyclic equalities and {completion['strict_source_q3_common_assembly']['Weyl_Ward_checks']} conformal Ward checks.  Gate V23 accepts {completion['strict_gate_v23_reconciliation']['accepted_top_level_hashes']} top-level common hash and leaves {completion['strict_gate_v23_reconciliation']['remaining_top_level_hashes']} hashes open.  The first three successors are \cert{{{completion['route_selection'][0]['route']}}}, \cert{{{completion['route_selection'][1]['route']}}}, and \cert{{{completion['route_selection'][2]['route']}}}; action/support identification M3RC-B, induced residual cyclicity M4R, final freeze, Green compatibility, Hadamard and QME work remain open.",
            "",
            rf"Atlas V41 records the complete arity-two and arity-three source assemblies, the portable residual zero-mode coefficients, the exact centered cohomology payload, the residual-SDR type repair, M3L and M4L, the represented finite M3R comparison, the exact obstruction to applying M4R directly to its one-sided target, and the exact formal M3RC-A cotangent comparison.  The quartic shifted mass contains {completion['strict_source_q3_common_assembly']['classical_independent_monomials']} independent monomials and {completion['strict_source_q3_common_assembly']['classical_ordered_fourth_variations']} ordered fourth variations.  Pairing lift gives {completion['strict_source_q3_common_assembly']['auxiliary_ordered_q3_coefficients']:,} auxiliary q3 coefficients on {completion['strict_source_q3_common_assembly']['graph_block_quadruples']} graph block quadruples.  The common arity-three, cyclicity modulo d, and D/q3 defect counts are {completion['strict_source_q3_common_assembly']['arity_three_defects']}, {completion['strict_source_q3_common_assembly']['q3_cyclicity_defects_mod_d']}, and {completion['strict_source_q3_common_assembly']['D_q3_defects']}.  The residual package contains {len(residual_zero_modes['zero_mode_basis']['canonical_generator_order'])} primal and {len(residual_zero_modes['zero_mode_basis']['canonical_dual_order'])} dual modes, {residual_zero_modes['so42_structure_constants']['nonzero_entries']} nonzero structure coefficients, {len(residual_zero_modes['residual_representation']['matrices'])} representation matrices, and zero defects in every declared exact replay.  The centered C3/C4/C5 bases have dimensions {centered['ordered_centered_cochain_basis']['degrees']['3']['dimension']:,}, {centered['ordered_centered_cochain_basis']['degrees']['4']['dimension']:,}, and {centered['ordered_centered_cochain_basis']['degrees']['5']['dimension']:,}; the receiver reconstructs {centered['centered_differential_summary']['aggregate_nonzero_coefficients']:,} coefficients, proves \(\dim H^4={centered['centered_differential_summary']['cohomology_dimension_H4']}\), and verifies the normalized chiral Gram matrix and parity exchange.  C3 and C5 are cochain carriers, not asserted H3/H5 computations.  The type audit separates {len(residual_sdr_type_audit['type_census']['endpoint_row_ids'])} local endpoint species, {residual_sdr_type_audit['type_census']['dfinite_total_residual_coordinates']} harmonic residual coefficients, and {residual_sdr_type_audit['type_census']['zero_mode_generator_coordinates']}+{residual_sdr_type_audit['type_census']['zero_mode_dual_coordinates']} global symmetry-cotangent coefficients; its exact constant and harmonic projector witnesses expand support.  The older symmetric cross-energy form covers {residual_cyclic_obstruction['older_even_form_control']['dimension']} coordinates at energies two through five and remains a valid even representation-theoretic control, not the field-theoretic BV antibracket.  Gate V23 remains fail closed until the six unaccepted hashes and the three typed packages M3RC-B, M4R, and M1 are supplied.",
            "",
            rf"The authoritative minimal cubic successor exports one nonzero q3 component on the six-generator carrier and classifies the other five output rows as zero.  Its exact receiver replays {completion['strict_minimal_q3_completion']['S3_input_permutations_replayed']} input permutations and the prior {completion['strict_minimal_q3_completion']['diagonal_witness_terms_reproduced']}-term witness.  The full minimal arity-three identity closes all {completion['strict_minimal_q3_completion']['arity_three_channels']} typed channels and {completion['strict_minimal_q3_completion']['arity_three_paths']} composable paths, while the quartic metric form is {completion['strict_minimal_q3_completion']['quartic_permutation_group']}-symmetric modulo horizontal boundary terms.  That minimal result alone does not establish the authoritative 386-row nonminimal theory identity, close the general lambda-squared source, pass Gate A, or reach Hadamard/QME stages.",
            "",
            r"\subsection{Complete evidence and literature registers}",
            r"\label{app:evidence-catalogue}",
        ]
    )
    kind_counts = collections.Counter(entry["kind"] for entry in evidence.values())
    quality_counts = collections.Counter(
        entry.get("artifact_status", entry.get("lifecycle", "UNCLASSIFIED"))
        for entry in evidence.values()
    )
    lines.extend(
        [
            rf"The normalized catalogue contains {len(evidence)} evidence records: {kind_counts['LOCAL_RESULT']} local result records and {kind_counts['LITERATURE']} literature records.  Tables~\ref{{tab:complete-literature-register}}--\ref{{tab:evidence-usage-crosswalk}} print the complete catalogue rather than only the records highlighted by the graph and ladder.  Literature entries preserve their artifact status: metadata-only records are bibliographic leads, not content-pinned evidence.  A catalogue entry supports only its stated role and never silently crosses its recorded boundary.",
            "",
            r"\begin{center}",
            r"\small",
            r"\begin{tabular}{@{}lr@{}}",
            r"\toprule",
            r"Catalogue lifecycle or artifact status & Records \\",
            r"\midrule",
        ]
    )
    for status, count in sorted(quality_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"{cert(status)} & {count}" + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            "",
            r"\subsubsection{Complete literature reference list}",
            r"The stable link is the catalogue's preferred public locator.  \cert{CONTENT_PINNED} means that the reviewed artifact is content-addressed in the evidence ledger; \cert{METADATA_ONLY} means that the bibliographic identity is resolved but the source content is not pinned.  The latter is a research lead, not equivalent evidential weight.",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.36\textwidth}p{0.58\textwidth}@{}}",
            rf"\caption{{Complete literature reference and evidence register ({kind_counts['LITERATURE']} records).}}\label{{tab:complete-literature-register}}\\",
            r"\toprule",
            r"Reference and provenance & Recorded evidential role and boundary \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Reference and provenance & Recorded evidential role and boundary \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for evidence_id, entry in sorted(evidence.items()):
        if entry["kind"] != "LITERATURE":
            continue
        provenance = (
            rf"\hypertarget{{{evidence_anchor[evidence_id]}}}{{{cert(evidence_id)}}}. "
            f"{tex(entry['citation'])} "
            f"{cert(entry['source_kind'])} / {cert(entry['artifact_status'])}. "
            rf"\url{{{entry['stable_url']}}}"
        )
        role = (
            r"\emph{Supports:} " + tex(evidence_support(entry))
            + r" \emph{Boundary:} " + tex(evidence_boundary(entry))
        )
        lines.append(f"{provenance} & {role}" + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            r"\subsubsection{Complete local result and certificate list}",
            "Local records are repository results, not external publications.  Their positive flags state what the registered certificate establishes; the complete negative list prevents a bounded result from being promoted to a stronger mathematical or physical claim.",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.36\textwidth}p{0.58\textwidth}@{}}",
            rf"\caption{{Complete local result and certificate register ({kind_counts['LOCAL_RESULT']} records).}}\label{{tab:complete-local-register}}\\",
            r"\toprule",
            r"Record and repository locator & Certified scope and complete boundary \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Record and repository locator & Certified scope and complete boundary \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for evidence_id, entry in sorted(evidence.items()):
        if entry["kind"] != "LOCAL_RESULT":
            continue
        tags = ", ".join(entry.get("dependency_tags", [])) or "none recorded"
        provenance = (
            rf"\hypertarget{{{evidence_anchor[evidence_id]}}}{{{cert(evidence_id)}}}. "
            f"{cert(entry['result_kind'])} / {cert(entry['lifecycle'])}. "
            f"Dependency tags: {tex(tags)}. "
            f"Result: {cert(entry['result_path'])}. Report: {cert(entry['report_path'])}."
        )
        scope = (
            r"\emph{Establishes:} " + tex(evidence_support(entry))
            + r" \emph{Does not establish:} "
            + tex("; ".join(entry.get("does_not_establish", [])))
            + "."
        )
        lines.append(f"{provenance} & {scope}" + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            r"\subsubsection{Evidence usage crosswalk}",
            r"Every evidence record is used by at least one matrix coordinate.  The matrix column reports the number of coordinates carrying the record and their coverage-status composition.  Graph entries use edge numbers from Table~\ref{tab:implication-ledger}; ladder entries use the gate identifiers from Table~\ref{tab:strength-ladder}.  Clicking a record identifier returns to its full literature or local-certificate entry above.",
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{longtable}{@{}p{0.36\textwidth}p{0.29\textwidth}p{0.29\textwidth}@{}}",
            rf"\caption{{Complete crosswalk from the atlas views to all {len(evidence)} evidence records.}}\label{{tab:evidence-usage-crosswalk}}\\",
            r"\toprule",
            r"Evidence record & Matrix use & Graph and ladder use \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Evidence record & Matrix use & Graph and ladder use \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for evidence_id, entry in sorted(evidence.items()):
        usage = evidence_usage[evidence_id]
        status_counts = collections.Counter(cell["status"] for cell in usage["cells"])
        status_summary = ", ".join(
            f"{STATUS_SHORT[status]} {status_counts[status]}"
            for status in STATUS_ORDER
            if status_counts[status]
        )
        matrix_use = f"{len(usage['cells'])} coordinates ({status_summary})."
        view_uses: list[str] = []
        if usage["graph"]:
            view_uses.append("graph edges " + ", ".join(str(n) for n in usage["graph"]))
        if usage["ladder"]:
            view_uses.append("ladder " + ", ".join(usage["ladder"]))
        graph_ladder_use = "; ".join(view_uses) + "." if view_uses else "No graph or ladder use."
        target = rf"\hyperlink{{{evidence_anchor[evidence_id]}}}{{{cert(evidence_id)}}}"
        target += " (literature)" if entry["kind"] == "LITERATURE" else " (local)"
        lines.append(f"{target} & {tex(matrix_use)} & {tex(graph_ladder_use)}" + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            r"\subsection{Model-scoped assembly, prototype envelopes, and empirical calibration}",
            r"\label{app:assembly-calibration}",
            "The assembly view no longer treats missing downstream work as a failed test.  Its model-specific maturity rails are reported independently: direct obligation coverage may be complete while composition is partial and numerical, prediction, or empirical records remain separately typed.  Red is reserved for an explicit incompatibility, obstruction, or failed comparison.",
            "",
        ]
    )
    model = next(item for item in assemblies["model_scoped_assemblies"] if item["result_id"] == "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1")
    mannheim = next(item for item in assemblies["model_scoped_assemblies"] if item["result_id"] == "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1")
    common_fit = assemblies["model_comparisons"][0]
    lines.extend(
        [
            r"\paragraph{First bounded end-to-end assembly.}",
            tex(model["title"]) + ".  This is one model identity and one declared observational sector, not a maximum assembled from unrelated cells.  Its applicability mask requires "
            + str(model["applicability_summary"]["required"])
            + " of the atlas's sixteen obligations, touches "
            + str(model["applicability_summary"]["touched_not_required"])
            + " others without requiring them, and explicitly places "
            + str(model["applicability_summary"]["out_of_scope"])
            + " outside this prediction.",
            "",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{@{}p{0.22\textwidth}p{0.20\textwidth}Y@{}}",
            r"\toprule",
            r"Stage & Status & What is established \\",
            r"\midrule",
        ]
    )
    for stage in model["stages"]:
        lines.append(
            f"{tex(stage['label'])} & {tex(stage['status'].replace('_', ' ').lower())} & {scientific_tex(stage['establishes'])}" + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\caption{The six typed stages of the standard-GR solar-exterior assembly.  The first four are exact local derivations; the last two are explicitly literature-scoped bridges.}",
            r"\label{tab:gr-cassini-assembly}",
            r"\end{table}",
            "",
            r"The exact rail derives \(g_{tt}=-1+2U-2\beta U^2+O(U^3)\) and \(g_{ij}=(1+2\gamma U+O(U^2))\delta_{ij}\), obtains \(\beta=\gamma=1\), and therefore fixes the first-order null-delay coefficient \(1+\gamma=2\).  The separately typed empirical rail imports the publisher's displayed Cassini estimate \(\gamma=1+(2.1\mathbin{\pm}2.3)\times10^{-5}\).  Exact rational comparison puts the prediction \(\gamma-1=0\) inside that displayed band, at absolute standardized distance \(21/23\) from its centre.",
            "",
            "All three required obligations are satisfied and all five stage interfaces are registered (three exact and two literature-scoped).  The resulting disposition is "
            + tex(model["assembly_disposition"]["status"].replace("_", " ").lower())
            + ".  It does not reproduce the Cassini raw-data reduction or likelihood, assess an independent held-out test, establish a complete theory, or transfer empirical support to Weyl gravity.",
            "",
            r"\paragraph{Second bounded assembly: mixed result.}",
            tex(mannheim["title"]) + ".  This chain retains one declared Mannheim--Kazanas phenomenological model from the Weyl action through certified local static-vacuum and orbit-law predecessors, the published thin-disk formula and NGC 3198 parameter row, an independently evaluated endpoint, and a no-refit comparison with a later SPARC rotation curve.",
            "",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{@{}p{0.22\textwidth}p{0.20\textwidth}Y@{}}",
            r"\toprule",
            r"Stage & Status & What is established \\",
            r"\midrule",
        ]
    )
    for stage in mannheim["stages"]:
        lines.append(
            f"{tex(stage['label'])} & {tex(stage['status'].replace('_', ' ').lower())} & {scientific_tex(stage['establishes'])}" + r" \\"
        )
    numeric = mannheim["numerical_reproduction_rail"]
    comparison = mannheim["empirical_comparison_rail"]
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\caption{The seven typed stages of the Mannheim conformal-gravity NGC 3198 assembly.  A failed uncertainty-sensitive comparison remains visible rather than being averaged with the coarser passing checks.}",
            r"\label{tab:mannheim-ngc3198-assembly}",
            r"\end{table}",
            "",
            "Independent evaluation predicts "
            + format(numeric["predicted_endpoint"]["velocity_km_s"], ".1f")
            + r" km/s at the paper's endpoint, compared with "
            + format(numeric["observed_endpoint_velocity_reconstructed_km_s"], ".1f")
            + r" km/s reconstructed from its displayed endpoint acceleration.  The relative residual is "
            + format(100 * numeric["endpoint_relative_velocity_residual"], ".3f")
            + r"\%, which passes the declared 5\% coarse audit gate.  Across "
            + str(comparison["points_inside_published_radius"])
            + " later SPARC points inside that radius, the no-refit RMS residual is "
            + format(comparison["unweighted_rms_residual_km_s"], ".3f")
            + r" km/s and passes the declared 5 km/s coarse shape gate, while the reduced $\chi^2$ from SPARC random errors alone is "
            + format(comparison["reduced_chi_squared_no_refit"], ".3f")
            + r" and fails the declared gate $\chi^2_\nu\leq2$.",
            "",
            "No parameter is refitted.  SPARC is a later 3.6-micrometre photometric reduction, not the original heterogeneous blue-band dataset, and its random-error column omits inclination and other systematics.  The result is therefore a no-refit external stress test with a mixed disposition, not a reproduction of the original likelihood and not evidence sufficient to promote the model to empirical support.  The massive-tracer matter-coupling assumption is recorded but not resolved.",
            "",
            r"\paragraph{Common-protocol NGC 3198 control.}",
            "The same 39 velocities, random-error-only objective, distance rescaling, and analytic stellar/gas geometry are used for all three families.  The stellar scale is fitted in every family; the NFW family additionally fits halo speed and concentration.",
            "",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{@{}Yp{0.25\textwidth}rrrr@{}}",
            r"\toprule",
            r"Family & Fitted parameters & RMS (km/s) & Reduced $\chi^2$ & AICc & Gate \\",
            r"\midrule",
        ]
    )
    fit_labels = {
        "NEWTONIAN_BARYONS_ONLY": "Newtonian baryons only",
        "GR_NFW_DARK_HALO": "GR plus NFW dark halo",
        "MANNHEIM_CONFORMAL_GRAVITY": "Mannheim conformal gravity",
    }
    for fitted in common_fit["models"]:
        parameters = fitted["fitted_parameters"]
        parameter_text = "q*=" + format(parameters["q_star"], ".4f")
        if "V200_km_s" in parameters:
            parameter_text += ", V200=" + format(parameters["V200_km_s"], ".2f") + ", c200=" + format(parameters["concentration_c200"], ".3f")
        metrics = fitted["metrics"]
        lines.append(
            f"{tex(fit_labels[fitted['model_id']])} & {tex(parameter_text)} & {metrics['unweighted_rms_residual_km_s']:.3f} & {metrics['reduced_chi_squared']:.3f} & {metrics['AICc']:.2f} & {'PASS' if fitted['random_error_gate']['passed'] else 'FAIL'}" + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\caption{Common-protocol NGC 3198 fit.  AICc penalizes the two extra NFW parameters.  The ranking is scoped to this one-galaxy, random-error-only analytic-disk comparison.}",
            r"\label{tab:ngc3198-common-fit}",
            r"\end{table}",
            "",
            "Mannheim has a lower unweighted RMS than NFW, while NFW has the lower uncertainty-weighted chi-squared and AICc.  NFW is the only family passing the declared reduced-chi-squared gate.  This does not include distance, inclination, photometric, gas-profile, or other systematic marginalization; use the full SPARC numerical mass model; impose a halo concentration--mass prior; generalize beyond NGC 3198; or select a complete physical theory.",
            "",
            r"\paragraph{Cube-selected prototype envelopes.}",
            r"\begin{table}[htbp]",
            r"\centering",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{@{}Yrrrr@{}}",
            r"\toprule",
            r"Prototype & Direct obligations & Certified joins & Coverage rail & Composition rail \\",
            r"\midrule",
        ]
    )
    for assembly in assemblies["assemblies"]:
        rails = {rail["id"]: rail["status"] for rail in assembly["maturity_rails"]}
        certified_joins = sum(item["certification_status"] == "CERTIFIED" for item in assembly["interfaces"])
        lines.append(
            f"{tex(assembly['label'])} & {assembly['coverage']['direct']}/{assembly['coverage']['total']} & "
            f"{certified_joins}/{len(assembly['interfaces'])} & {tex(rails['OBLIGATION_COVERAGE'])} & "
            f"{tex(rails['CROSS_CELL_COMPOSITION'])}" + r" \\"
        )
    control = assemblies["calibration_controls"][0]
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\caption{Cube-selected coverage and composition maturity.  The classical-standard mixed-carrier reference has complete direct coverage; this does not certify the unregistered joins.}",
            r"\label{tab:assembly-maturity}",
            r"\end{table}",
            "",
            "The BT positive Euclidean lattice programme is the only prototype with a numerical-reproducibility record.  Its status is COARSE REPRODUCTION ONLY: two independent algorithms pass the declared four-standard-error gate but not the two-standard-error precision gate.  The empirical and out-of-sample rails remain empty.  The separate Euclidean-to-Krein carrier record is incompatible only with identification as the same full nonperturbative measure; it does not refute every conditional bridge.",
            "",
            r"\paragraph{External positive control.}",
            tex(control["label"]) + ". " + tex(control["scope"]),
            "",
            r"\begingroup",
            r"\scriptsize",
            r"\begin{longtable}{@{}p{0.19\textwidth}p{0.27\textwidth}p{0.46\textwidth}@{}}",
            r"\caption{Registered standard-GR control comparisons.}\label{tab:gr-positive-control}\\",
            r"\toprule",
            r"Benchmark & Primary source & Registered finding and boundary \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Benchmark & Primary source & Registered finding and boundary \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    benchmark_labels = {item["id"]: item["label"] for item in assemblies["empirical_ledger"]["benchmarks"]}
    for record in control["records"]:
        source = tex(record["citation"]) + rf" \url{{{record['stable_url']}}}"
        finding = f"{record['finding']} Boundary: {record['boundary']}"
        lines.append(f"{tex(benchmark_labels[record['benchmark']])} & {source} & {tex(finding)}" + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\endgroup",
            "",
            "The control populates three of six benchmark families with four records.  It is outside the cube, does not make GR complete, and transfers no observational support to a Weyl-gravity prototype.",
            "",
            rf"The complete normalized dataset is \cert{{foundations/site/data.json}} (SHA-256 \cert{{{sha256(SOURCE)}}}; canonical digest \cert{{{data['canonical_digest']}}}).  These tables are generated from that file and contain no hand-copied coverage counts, relation edges, evidence roles, boundaries, or citations.",
            rf"The assembly and calibration tables are generated from \cert{{foundations/site/assemblies.json}} (SHA-256 \cert{{{sha256(ASSEMBLY_SOURCE)}}}; canonical digest \cert{{{assemblies['canonical_digest']}}}).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text())
    assemblies = json.loads(ASSEMBLY_SOURCE.read_text())
    expected = build(data, assemblies)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != expected:
            raise SystemExit(f"stale generated appendix: {OUTPUT.relative_to(ROOT)}")
        print(f"PASS {OUTPUT.relative_to(ROOT)} is current")
        return 0
    OUTPUT.write_text(expected)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
