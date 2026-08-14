#!/usr/bin/env python3
"""Build the migration-reviewed v2 static foundations explorer."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from foundations import build_matrix_site as v1
from foundations.theory_assembly import build_assembly_assessment
from foundations.theory_viability import build_assessment

ROOT = v1.ROOT
FOUNDATIONS = v1.FOUNDATIONS
ASSETS = v1.ASSETS
V2_ASSETS = FOUNDATIONS / "matrix_site_v2_assets"
SITE = FOUNDATIONS / "site"
RESULT = FOUNDATIONS / "results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
REPORT = FOUNDATIONS / "reports/matrix-explorer-site-v2.md"
VIABILITY_RESULT = FOUNDATIONS / "results/FOUNDATIONAL_THEORY_VIABILITY_ASSESSMENT_V1.json"
VIABILITY_REPORT = FOUNDATIONS / "reports/theory-viability-assessment-v1.md"
ASSEMBLY_RESULT = FOUNDATIONS / "results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json"
ASSEMBLY_REPORT = FOUNDATIONS / "reports/theory-assembly-atlas-v1.md"
GR_CASSINI_RESULT = FOUNDATIONS / "results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json"
GR_CASSINI_REPORT = FOUNDATIONS / "reports/gr-cassini-model-assembly-v1.md"
GR_CASSINI_SCHEMA = FOUNDATIONS / "schema/foundational-gr-cassini-model-assembly-v1.schema.json"
MANNHEIM_NGC3198_RESULT = FOUNDATIONS / "results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json"
MANNHEIM_NGC3198_REPORT = FOUNDATIONS / "reports/mannheim-ngc3198-model-assembly-v1.md"
MANNHEIM_NGC3198_SCHEMA = FOUNDATIONS / "schema/foundational-mannheim-ngc3198-model-assembly-v1.schema.json"
MANNHEIM_NGC3198_PARAMETERS = FOUNDATIONS / "data/mannheim-ngc3198-parameters-v1.json"
MANNHEIM_NGC3198_SPARC = FOUNDATIONS / "data/ngc3198-sparc-mass-model-v1.tsv"
MANNHEIM_NGC3198_CPP = FOUNDATIONS / "mannheim_ngc3198_numeric_checker.cpp"
NGC3198_COMMON_FIT_RESULT = FOUNDATIONS / "results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json"
NGC3198_COMMON_FIT_REPORT = FOUNDATIONS / "reports/ngc3198-common-fit-comparison-v1.md"
NGC3198_COMMON_FIT_SCHEMA = FOUNDATIONS / "schema/foundational-ngc3198-common-fit-comparison-v1.schema.json"
NGC3198_COMMON_FIT_PROTOCOL = FOUNDATIONS / "data/ngc3198-common-fit-protocol-v1.json"
NGC3198_COMMON_FIT_CPP = FOUNDATIONS / "ngc3198_common_fit_checker.cpp"
CUBE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json"
PREVIOUS_CUBES = [
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json",
]
TEN_CELL_CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
TWENTY_CELL_CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1.json"
CORNER_BORN_INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
GROUND_STATE_DYNAMICS_INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
BT_EUCLIDEAN_IMPORT = FOUNDATIONS / "results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
FULL_SURFACE_AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
LADDER = FOUNDATIONS / "results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json"
LEDGERS = v1.LEDGERS
CREATED = "2026-08-14"
BASE_COMMIT = "2a211e2931cd391b78f16d8ec374369ec09a4a24"

PLAIN_AXIS_GUIDE = {
    "FOUNDATION": {
        "question": "Which rules of reasoning and mathematical existence are we allowing?",
        "plain_name": "Mathematical regime",
        "CLASSICAL_STANDARD": "Mainstream mathematics: classical logic, completed infinite structures, and ordinary analysis, with Choice available unless a proof explicitly avoids it.",
        "WEAK_ARITHMETIC": "Use a deliberately small formal system and ask exactly how much arithmetic or set existence the proof needs.",
        "WEAK_CHOICE_ZF": "Keep classical set theory but remove or isolate principles that choose objects from infinitely many sets at once.",
        "CONSTRUCTIVE_COMPUTABLE": "An existence claim must provide a witness, construction, or algorithm—not only show that nonexistence would be contradictory.",
        "TOPOS_INTERNAL": "Do the mathematics inside an alternative logical universe, where truth may be local and classical either/or reasoning may fail.",
        "FINITE_DISCRETE": "Replace an infinite or continuous system by finite exact data or finitely many modes. This is not automatically the same as rejecting infinity as a foundation.",
    },
    "CARRIER": {
        "question": "What kind of mathematical object holds the states, fields, and observables?",
        "plain_name": "Mathematical carrier",
        "FINITE_EXACT": "Finite matrices, rational arrays, or other finite algebraic data that can be checked exactly.",
        "HILBERT_OPERATOR": "The positive-norm vector spaces and operators used in standard quantum mechanics and spectral theory.",
        "KREIN_INDEFINITE": "A vector space whose inner product can be positive, negative, or zero, as often occurs before unphysical gauge directions are removed.",
        "ALGEBRAIC_CSTAR": "Start from an algebra of observable quantities; a state is a rule assigning expectation values rather than primarily a wavefunction.",
        "SMOOTH_DISTRIBUTIONAL": "Continuum fields on space or spacetime, including derivatives, PDEs, Sobolev spaces, generalized functions, and Green operators.",
        "LOCALIC_SYNTHETIC": "Describe spaces through regions, logical relations, or internal geometry instead of beginning with a set of individual points.",
    },
    "REFINED_OBLIGATION": {
        "question": "Which physical job must the theory perform?",
        "plain_name": "Physical obligation",
        "KINEMATICS_OBSERVABLES": "Say what the possible configurations and measurable quantities are before specifying how they evolve.",
        "STATE_EXISTENCE": "Show that at least one mathematically valid state actually exists.",
        "STATE_REPRESENTATION": "Explain how an abstract state is encoded—for example by a vector, density matrix, measure, valuation, or GNS construction.",
        "PROBABILITY_RULE": "Turn states and events into normalized probabilities, such as a Born-type prediction rule.",
        "PHYSICAL_STATE_SELECTION": "Explain why a particular vacuum, thermal, Hadamard, or other state should count as physically distinguished.",
        "GENERATOR_SPECTRAL_DYNAMICS": "Construct what generates time evolution and, where relevant, identify its allowed frequencies or energy spectrum.",
        "EVOLUTION_WELLPOSEDNESS": "Show that admissible initial data produce a solution that exists, is unique, and changes stably or computably with the data.",
        "CAUSAL_PROPAGATION_GREEN": "Show that disturbances propagate within the permitted causal region and construct retarded or advanced response maps.",
        "GAUGE_BV_COHOMOLOGY": "Handle redundant gauge descriptions consistently and identify the quantities or states that remain physically meaningful.",
        "INTERACTION_CONSTRUCTION": "Build a genuine coupling or nonlinear theory rather than only a collection of free, noninteracting fields.",
        "COUNTERTERM_CLASSIFICATION": "List every local correction that quantum calculations are allowed to require before attempting to calculate its coefficient.",
        "ANOMALY_CLASSIFICATION": "List the possible ways a classical symmetry or consistency condition could fail after quantization.",
        "RENORMALIZED_PRODUCTS": "Define products and correlation functions that would otherwise be singular when fields meet at the same spacetime point.",
        "QME_RESTORATION": "Repair the quantum master equation, the BV consistency condition that encodes quantum gauge symmetry.",
        "RESIDUAL_QUANTUM_TRANSFER": "After quantum consistency is restored, transfer the correction to the smaller complex that represents the surviving physical content.",
        "RECONSTRUCTION_LIMITS": "Connect the formulation back to operational predictions, a continuum or standard theory, or a demonstrated notion of empirical equivalence.",
    },
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def site_link(path: str) -> str:
    return "sources/" + Path(path).as_posix()


def guided_axes(source_axes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes: list[dict[str, Any]] = []
    for source_axis in source_axes:
        guide = PLAIN_AXIS_GUIDE[source_axis["id"]]
        axes.append({
            **source_axis,
            "plain_name": guide["plain_name"],
            "guide_question": guide["question"],
            "keys": [{**key, "plain_meaning": guide[key["id"]]} for key in source_axis["keys"]],
        })
    return axes


def evidence_registry(cube: dict[str, Any], ladder: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reuse the v1 resolver, but include evidence reviewed only for migration."""
    registry_cube = dict(cube)
    registry_cube["cells"] = [
        {**cell, "evidence": list(dict.fromkeys([*cell["evidence"], *cell.get("migration_evidence", [])]))}
        for cell in cube["cells"]
    ]
    return v1.evidence_registry(registry_cube, ladder)


def complete_surface(cube: dict[str, Any]) -> list[dict[str, Any]]:
    axes = {axis["id"]: axis for axis in cube["axes"]}
    foundations = [x["id"] for x in axes["FOUNDATION"]["keys"]]
    carriers = [x["id"] for x in axes["CARRIER"]["keys"]]
    obligations = [x["id"] for x in axes["REFINED_OBLIGATION"]["keys"]]
    emitted = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    cells: list[dict[str, Any]] = []
    for obligation in obligations:
        for foundation in foundations:
            for carrier in carriers:
                coordinate = (foundation, carrier, obligation)
                if coordinate in emitted:
                    cells.append({**emitted[coordinate], "emitted": True})
                else:
                    cells.append({
                        "foundation": foundation,
                        "carrier": carrier,
                        "obligation": obligation,
                        "status": "NOT_MAPPED",
                        "evidence": [],
                        "evidence_roles": {},
                        "parent_obligation": None,
                        "migration_relation": "NOT_EMITTED",
                        "migration_status": "NOT_REVIEWED",
                        "migration_evidence": [],
                        "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
                        "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
                        "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
                        "emitted": False,
                    })
    return cells


STATUS_MARK = {"LOCAL_RESULT": "L", "LITERATURE_RESULT": "R", "PIECES_ONLY": "P", "PRIORITY_GAP": "G", "REVIEWED_GAP": "O", "NOT_MAPPED": "\u00b7"}
KIND_UPPER = {"DIRECT_LOCAL": "L", "DIRECT_LITERATURE": "R"}
KIND_LOWER = {"LOCAL_RESULT": "l", "LITERATURE": "r"}


def cell_mark(cell: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> str:
    """Upper case names a certified direct grade, lower case a supporting ingredient."""
    roles = cell["evidence_roles"]
    direct = {KIND_UPPER[role] for role in roles.values() if role in KIND_UPPER}
    upper = "".join(x for x in "LR" if x in direct) or STATUS_MARK[cell["status"]]
    support = {KIND_LOWER[evidence[item]["kind"]] for item, role in roles.items() if role == "SUPPORTING"}
    return upper + "".join(x for x in "lr" if x in support and x.upper() not in upper)


def canonical_digest(dataset: dict[str, Any]) -> str:
    projection = {
        key: dataset[key]
        for key in ("axes", "cells", "evidence", "ladder", "graph", "cross_cell_interfaces", "carrier_interfaces", "numerical_reproducibility_records")
    }
    return v1.sha_bytes(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def build_dataset() -> dict[str, Any]:
    cube, audit, ladder, bt_import = v1.load(CUBE), v1.load(AUDIT), v1.load(LADDER), v1.load(BT_EUCLIDEAN_IMPORT)
    interface_results = [v1.load(CORNER_BORN_INTERFACE), v1.load(GROUND_STATE_DYNAMICS_INTERFACE)]
    if cube.get("certified_interfaces") != [item.get("interface") for item in interface_results]:
        raise ValueError("cube/interface projection mismatch")
    if cube.get("certified_carrier_interfaces") != [bt_import.get("carrier_interface")]:
        raise ValueError("cube/carrier-interface projection mismatch")
    cells = complete_surface(cube)
    evidence = evidence_registry(cube, ladder)
    status_counts: dict[str, int] = {}
    migration_counts: dict[str, int] = {}
    for cell in cells:
        status_counts[cell["status"]] = status_counts.get(cell["status"], 0) + 1
        migration_counts[cell["migration_status"]] = migration_counts.get(cell["migration_status"], 0) + 1
    for status in ("LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"):
        status_counts.setdefault(status, 0)
    dataset = {
        "schema_version": "foundational-matrix-explorer-data-v2",
        "title": "Reverse Physics Atlas",
        "created": CREATED,
        "dependency_tags": cube["dependency_tags"],
        "axes": guided_axes(cube["axes"]),
        "groups": v1.GROUPS,
        "statuses": cube["cell_statuses"],
        "evidence_role_vocabulary": cube["evidence_role_vocabulary"],
        "evidence_role_rule": cube["evidence_role_rule"],
        "migration_statuses": cube["migration_statuses"] + [{"id": "NOT_REVIEWED", "meaning": "The coordinate was not emitted by cube v2, so no migration review was required."}],
        "counts": {
            "cartesian_total": cube["dimensions"]["cartesian_total"],
            "emitted": cube["dimensions"]["emitted_cells"],
            "coverage_classified": cube["dimensions"]["coverage_classified_cells"],
            "qualified": cube["dimensions"]["coverage_classified_cells"],
            "migration_reviewed": cube["dimensions"]["migration_reviewed_cells"],
            "migration_pending": cube["dimensions"]["migration_pending_cells"],
            "migration_unresolved": cube["dimensions"]["migration_pending_cells"],
            "reviewed_no_transfer": cube["dimensions"]["reviewed_no_transfer_cells"],
            "reviewed_gap": status_counts["REVIEWED_GAP"],
            "not_mapped": status_counts["NOT_MAPPED"],
            "dual_direct": sum({"DIRECT_LOCAL", "DIRECT_LITERATURE"} <= set(cell["evidence_roles"].values()) for cell in cells),
            "mark_counts": dict(sorted(Counter(cell_mark(cell, evidence) for cell in cells).items())),
            "evidence_role_counts": dict(sorted({role: sum(list(cell["evidence_roles"].values()).count(role) for cell in cells) for role in ("DIRECT_LITERATURE", "DIRECT_LOCAL", "SUPPORTING", "UNREVIEWED")}.items())),
            "synthetic_not_mapped": sum(not cell["emitted"] for cell in cells),
            "status_counts": dict(sorted(status_counts.items())),
            "migration_status_counts": dict(sorted(migration_counts.items())),
            "evidence_records": len(evidence),
        },
        "cells": cells,
        "evidence": evidence,
        "ladder": ladder["ladder"],
        "graph": ladder["typed_relation_graph"],
        "cross_cell_interfaces": cube["certified_interfaces"],
        "carrier_interfaces": cube["certified_carrier_interfaces"],
        "numerical_reproducibility_records": bt_import["numerical_reproducibility_records"],
        "boundaries": {
            "cube": cube["does_not_establish"],
            "migration_audit": audit["does_not_establish"],
            "ladder": ladder["does_not_establish"],
            "navigation": [
                "Coverage status and migration-review status answer different questions.",
                "REVIEWED_NO_TRANSFER, REVIEWED_GAP, and NOT_MAPPED are not literature-absence claims.",
                "All 576 coordinates are emitted and directly assessed; zero browser-only synthetic complements remain.",
                "A REVIEWED_GAP is an explicit open question with a typed missing certificate, not a result or a selected priority.",
                "Neighbor counts and candidate views are navigation aids, not theorem rankings.",
                "An UNREVIEWED evidence role means the record has not been reviewed for directness at that obligation; it is not a finding that the record fails to support the cell.",
                "The LR mark reports two certified direct evidence kinds at one coordinate. It does not merge them into a stronger single result.",
            ],
        },
        "source_links": {
            "cube": site_link(rel(CUBE)),
            "full_surface_audit": site_link(rel(FULL_SURFACE_AUDIT)),
            "migration_audit": site_link(rel(AUDIT)),
            "ladder": site_link(rel(LADDER)),
            "cube_report": site_link("foundations/reports/refined-intersection-cube-v11.md"),
            "bt_euclidean_import": site_link(rel(BT_EUCLIDEAN_IMPORT)),
            "bt_euclidean_import_report": site_link("foundations/reports/bt-euclidean-lattice-foundational-import.md"),
            "full_surface_audit_report": site_link("foundations/reports/full-surface-gap-audit.md"),
            "twenty_cell_closure": site_link(rel(TWENTY_CELL_CLOSURE)),
            "twenty_cell_closure_report": site_link("foundations/reports/finite-brst-twenty-cell-closure.md"),
            "ten_cell_closure": site_link(rel(TEN_CELL_CLOSURE)),
            "ten_cell_closure_report": site_link("foundations/reports/finite-operator-ten-cell-closure.md"),
            "corner_born_interface": site_link(rel(CORNER_BORN_INTERFACE)),
            "corner_born_interface_report": site_link("foundations/reports/bt-corner-born-interface.md"),
            "ground_state_dynamics_interface": site_link(rel(GROUND_STATE_DYNAMICS_INTERFACE)),
            "ground_state_dynamics_interface_report": site_link("foundations/reports/krein-fock-ground-state-dynamics-interface.md"),
            "migration_audit_report": site_link("foundations/reports/intersection-cube-migration-audit-v2.md"),
            "ladder_report": site_link("foundations/reports/cylinder-wave-strength-ladder-v2.md"),
        },
    }
    dataset["canonical_digest"] = canonical_digest(dataset)
    return dataset


def render_report(result: dict[str, Any]) -> str:
    counts = result["counts"]
    return f"""# Migration-reviewed static foundations matrix explorer v2

**Result:** `{result['result_id']}`

**Lifecycle:** `{result['lifecycle']}`

**Dependency tags:** {', '.join(f'`{x}`' for x in result['dependency_tags'])}

## Outcome

`foundations/site/index.html` presents all **576** Cartesian coordinates.
All **576** are now emitted by cube v11 and have separate coverage and migration
review fields: **{counts['migration_reviewed']} reviewed**, **{counts['migration_pending']} pending**.
The surface has **{counts['reviewed_gap']} `REVIEWED_GAP`** cells and **{counts['not_mapped']}
`NOT_MAPPED`** cells. A reviewed gap is a formulated open question with a typed
missing certificate; it is not a result, a selected priority, or a literature-absence claim.
There are **{counts['synthetic_not_mapped']}** browser-only complements.

The full-surface audit preserves all 401 prior positive, partial, and priority
classifications. It revises 51 emitted blanks and directly assesses the 124
formerly synthetic coordinates without transferring evidence from neighbors.

Cube v11 preserves two certified `CONDITIONAL_BRIDGE` relations. The first maps an
algebraic finite-corner state to a Krein probability rule under five explicit
hypotheses. The second uses the free Fock energy gap to select the unique normal
zero-energy vacuum state and proves that the same state is invariant under the
generated Krein--Fock dynamics. The other assembly interfaces remain open.

Cube v11 also preserves the positive BT Euclidean finite lattice import into five direct
`FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL` cells. Its independent-sampler record
is coarse numerical reproduction, not empirical validation. A separate carrier
interface refuses only identification of the positive Euclidean measure with the
all-real BT/Krein path integral; controlled conditional bridges remain open.

The new reconstruction import supplies the first explicit weak-arithmetic
finite-approximant theorem for a declared bounded wave observable. Its rational
dyadic interpolants converge uniformly on every rational bounded time interval
with cutoff `N(k)=k+ell(K)+1`. It reconstructs one smeared scalar observable,
not the full field, causal support, or a Weyl-gravity prediction.

Coverage is assessed for **{counts['coverage_classified']}** emitted cells. The
finite-BRST pass classifies exactly twenty additional empty cells: seventeen
direct local results and three pieces-only regulated-product results. Its exact
lifecycle orders cohomology classification before QME restoration and residual
transfer; none of those toy-model statements is a Weyl-BV promotion.
The cell inspector exposes coverage evidence separately from migration-review
evidence and links to the explicit 112-decision audit ledger.

The **Dimensions guide** explains the 6 mathematical regimes, 6 carriers, and
16 physical obligations in non-specialist language while retaining each
technical definition in an expandable detail block.

The implication view is a three-pathway argument map. Arrowheads terminate at
visible box ports, every edge has an explicit plain-language assertion, and
hover or keyboard focus links the diagram to its relation-ledger row.

## Build and verification

```text
python3 foundations/build_matrix_site_v2.py
python3 foundations/build_matrix_site_v2.py --check
python3 foundations/check_matrix_site_v2.py
python3 foundations/verify_matrix_site_v2.py
python3 -m unittest foundations.tests.test_matrix_site
```

Earlier cubes remain unchanged as historical artifacts. The existing-site build
fails closed on unresolved evidence IDs and projects scientific text from the
cube, migration audit, strength ladder, local results, and literature ledgers.

## Deployment

Serve `foundations/site/` from any static host, or open `index.html` directly.
All source links resolve inside the standalone directory; no remote code is used.

## Boundaries

This site does not establish:

""" + "\n".join(f"- {item}" for item in result["does_not_establish"]) + "\n"


def render_viability_report(assessment: dict[str, Any]) -> str:
    pareto = [item for item in assessment["profiles"] if item["pareto_default"]]
    lines = [
        "# Theory coverage, composition, and observation assessment v1",
        "",
        "**Result:** `FOUNDATIONAL_THEORY_VIABILITY_ASSESSMENT_V1`",
        "",
        "**Lifecycle:** `VERIFIED_NAVIGATION_ARTIFACT`",
        "",
        "## Outcome",
        "",
        "The assessment compares all **36** regime-carrier formulation profiles and computes",
        "six carrier-portfolio coverage envelopes. It deliberately refuses to turn coverage",
        "into an empirical-validity score.",
        "",
        "Under the default predictive-physics gate, no single profile has direct evidence for",
        "every required obligation. The present Pareto navigation set is:",
        "",
        *[
            f"- `{item['foundation']} × {item['carrier']}`: "
            f"{item['default_gate']['direct']}/{item['default_gate']['total']} default-gate obligations direct; "
            f"{item['direct']}/16 total obligations direct."
            for item in pareto
        ],
        "",
        "This does **not** make those profiles complete theories. Evidence across obligations",
        "can come from different scoped models. Combining carriers takes the best recorded cell",
        "status and therefore creates a coverage envelope, not a composition theorem.",
        "",
        "## Three separate rails",
        "",
        "1. **Obligation coverage — computed.** Direct, partial, gap, and unknown statuses are",
        "   projected from the atlas without changing their evidence type.",
        "2. **One coherent integrated theory — partially assessed.** Two scoped joins",
        "   are certified: finite-corner state-to-probability and free ground-state-to-dynamics. The",
        "   remaining interfaces block a composed theory.",
        "3. **Agreement with observations — not in the current schema.** There are no typed",
        "   dataset, likelihood, residual, fit, or out-of-sample prediction records. The",
        "   reconstruction obligation is only a bridge-readiness proxy.",
        "",
        "## Interface",
        "",
        "The **Theory profiles** tab provides a 6×6 readiness map, selectable obligation gates,",
        "a single-carrier ranking table, a multi-carrier coverage-envelope composer, bundle",
        "profiles, exact blockers, and the default Pareto set. No scalar winner is emitted.",
        "",
        "## Boundaries",
        "",
        *[f"- This does not establish {item}." for item in assessment["does_not_establish"]],
        "",
    ]
    return "\n".join(lines)


def render_assembly_report(assessment: dict[str, Any]) -> str:
    certified_instances = sum(
        interface.get("certification_status") == "CERTIFIED"
        for assembly in assessment["assemblies"]
        for interface in assembly["interfaces"]
    )
    model_assembly = next(item for item in assessment["model_scoped_assemblies"] if item["result_id"] == "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1")
    mannheim_assembly = next(item for item in assessment["model_scoped_assemblies"] if item["result_id"] == "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1")
    common_fit = assessment["model_comparisons"][0]
    lines = [
        "# Candidate theory assembly atlas v1",
        "",
        "**Result:** `FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1`",
        "",
        "**Lifecycle:** `VERIFIED_NAVIGATION_ARTIFACT`",
        "",
        "## Outcome",
        "",
        "The atlas generates nine named research-programme lenses. Each is a deterministic",
        "coverage envelope: it selects the strongest recorded cell for every obligation",
        "inside a declared regime/carrier region. It is not a composed theory or a claim",
        "that every researcher in the named tradition endorses every selected cell.",
        "",
        "The lenses make the larger conversations recognizable: mainstream GR/QFT,",
        "algebraic QFT, finite/discrete exact models, Bateman–Turok, reverse mathematics,",
        "Mannheim conformal gravity, this repository's Pure-Weyl BV–BFV programme,",
        "constructive/computable physics, and topos/internal quantum foundations. Each",
        "records a central question, lineage, signature ideas, the narrower atlas window",
        "currently sampled, and an explicit scope caution.",
        "",
        "The crucial new object is the interface ledger. Seven joins in each prototype",
        "must separately record whether the linked objects are identical, exactly",
        "translated, conditionally bridged, approximated with a bound, conjecturally",
        "linked, incompatible, or not assessed. Two scoped relations are now",
        "certified and produce " + str(certified_instances) + " compatible prototype-interface instances; the other",
        "required joins remain `NOT_ASSESSED`, so coverage cannot silently promote them.",
        "",
        "## First model-scoped assembly",
        "",
        "`FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1` is the first bounded",
        "end-to-end assembly. It keeps one model identity from the vacuum Einstein",
        "equations through the Schwarzschild exterior, isotropic PPN reduction,",
        "null-delay coefficient, Cassini fitted parameter, and published comparison.",
        "All " + str(len(model_assembly["interfaces"])) + " stage joins are registered; the first three are exact and",
        "the last two are explicitly literature-scoped. The exact prediction",
        "`gamma-1=0` lies inside the publisher's displayed `(2.1+/-2.3)e-5` band.",
        "The disposition is `BOUNDED_PREDICTION_ASSEMBLY_COMPLETE`, not complete theory.",
        "",
        "## Second model-scoped assembly: a mixed result",
        "",
        "`FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1` follows one declared",
        "Mannheim--Kazanas phenomenological model through seven stages: the Weyl action,",
        "the certified static vacuum family and circular-orbit law, the published thin-disk",
        "formula, the NGC 3198 parameter row, endpoint reproduction, and a no-refit residual audit",
        "with the later SPARC curve. The endpoint relative velocity residual is " + format(100 * mannheim_assembly["numerical_reproduction_rail"]["endpoint_relative_velocity_residual"], ".3f") + " percent,",
        "and the SPARC RMS residual is " + format(mannheim_assembly["empirical_comparison_rail"]["unweighted_rms_residual_km_s"], ".3f") + " km/s. Both pass their declared coarse audit gates.",
        "The reduced chi-squared using SPARC random errors alone is " + format(mannheim_assembly["empirical_comparison_rail"]["reduced_chi_squared_no_refit"], ".3f") + ", which fails the declared gate of 2.",
        "No parameter is refitted, and SPARC is a later non-identical data reduction, so the",
        "mixed disposition remains partial and does not establish empirical support.",
        "",
        "## Common-protocol NGC 3198 control",
        "",
        "`FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1` fits Newtonian baryons-only,",
        "GR plus NFW, and Mannheim to the same 39 velocities and analytic baryonic geometry.",
        "The AICc order is " + " > ".join(common_fit["ranking_by_AICc"]) + ". GR plus NFW is the only family",
        "passing the declared reduced-chi-squared gate. Mannheim nevertheless has the lower",
        "unweighted RMS, so the explorer displays both metrics rather than collapsing them.",
        "This one-galaxy random-error-only ranking is not a complete-theory selection.",
        "",
        "## Independent maturity rails",
        "",
        "Every prototype is displayed against seven separately reported rails: obligation coverage,",
        "cross-cell composition, prediction derivation, observable identification, numerical reproducibility,",
        "empirical comparison, and robustness/out-of-sample performance. A complete",
        "classical coverage envelope is therefore shown as complete even when composition",
        "is only partial. Missing or premature downstream work is `NOT_ASSESSED`,",
        "`NOT_EVALUABLE`, `NOT_REGISTERED`, or `NO_RECORDS`; red failure states are",
        "reserved for an explicit obstruction, incompatibility, or failed comparison.",
        "",
        "The BT Euclidean lattice prototype has one `COARSE_REPRODUCTION_ONLY` numerical",
        "record: HMC and local Metropolis pass the declared four-standard-error gate but",
        "not a two-standard-error precision gate. The empirical and robustness rails stay empty.",
        "",
        "## Empirical ledger",
        "",
        "The ledger declares six benchmark families and the fields a future comparison",
        "must carry. It is intentionally empty. A benchmark name is not observational",
        "evidence, and reconstruction coverage is not an empirical comparison.",
        "",
        "## External positive control",
        "",
        "Standard general relativity is included as an external positive control, not as",
        "a cube-selected prototype. Four primary-source records populate prediction,",
        "observable, and comparison rails in three benchmark families: solar-system",
        "propagation, compact binaries, and gravitational waves. The other benchmark",
        "families remain unregistered. This calibrates the display without transferring",
        "observational support to Weyl gravity or claiming that GR is complete.",
        "",
        "## Interface",
        "",
        "The **Assemblies** tab synchronizes the maturity rails, selected obligation",
        "cells, typed interface ledger, and empirical benchmark ledger for one prototype.",
        "Each selected cell links back to the exact matrix coordinate.",
        "",
        "## Boundaries",
        "",
        *[f"- This does not establish {item}." for item in assessment["does_not_establish"]],
        "",
    ]
    return "\n".join(lines)


def generated() -> dict[Path, bytes]:
    dataset = build_dataset()
    viability = build_assessment(dataset)
    assemblies = build_assembly_assessment(dataset)
    data_json = (json.dumps(dataset, indent=2, ensure_ascii=False) + "\n").encode()
    viability_json = (json.dumps(viability, indent=2, ensure_ascii=False) + "\n").encode()
    assembly_json = (json.dumps(assemblies, indent=2, ensure_ascii=False) + "\n").encode()
    index = (ASSETS / "index.html").read_text().replace(
        '<script src="data.js"></script>',
        '<script src="data.js"></script>\n  <script src="viability.js"></script>\n  <script src="assemblies.js"></script>',
    ).replace(
        '<script src="app.js"></script>',
        '<script src="app.js"></script>\n  <script src="migration-review.js"></script>',
    ).encode()
    outputs: dict[Path, bytes] = {
        SITE / "index.html": index,
        SITE / "styles.css": (ASSETS / "styles.css").read_bytes(),
        SITE / "app.js": (ASSETS / "app.js").read_bytes(),
        SITE / "migration-review.js": (V2_ASSETS / "app-v2.js").read_bytes(),
        SITE / "data.json": data_json,
        SITE / "data.js": b"window.MATRIX_EXPLORER_DATA = " + data_json.rstrip() + b";\n",
        SITE / "viability.json": viability_json,
        SITE / "viability.js": b"window.THEORY_VIABILITY_DATA = " + viability_json.rstrip() + b";\n",
        SITE / "assemblies.json": assembly_json,
        SITE / "assemblies.js": b"window.THEORY_ASSEMBLY_DATA = " + assembly_json.rstrip() + b";\n",
    }
    local_evidence_paths = [ROOT / item["result_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT"]
    local_report_paths = [ROOT / item["report_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT" and item.get("report_path")]
    reports = [
        FOUNDATIONS / "reports/refined-intersection-cube-v11.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v10.md",
        FOUNDATIONS / "reports/bt-euclidean-lattice-foundational-import.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v8.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v7.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v6.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v5.md",
        FOUNDATIONS / "reports/bt-corner-born-interface.md",
        FOUNDATIONS / "reports/krein-fock-ground-state-dynamics-interface.md",
        FOUNDATIONS / "reports/intersection-cube-migration-audit-v2.md",
        FOUNDATIONS / "reports/cylinder-wave-strength-ladder.md",
        FOUNDATIONS / "reports/full-surface-gap-audit.md",
        GR_CASSINI_REPORT,
        MANNHEIM_NGC3198_REPORT,
        NGC3198_COMMON_FIT_REPORT,
    ]
    bundled_sources = sorted(set([CUBE, *PREVIOUS_CUBES, FULL_SURFACE_AUDIT, CORNER_BORN_INTERFACE, GROUND_STATE_DYNAMICS_INTERFACE, BT_EUCLIDEAN_IMPORT, GR_CASSINI_RESULT, GR_CASSINI_SCHEMA, MANNHEIM_NGC3198_RESULT, MANNHEIM_NGC3198_SCHEMA, MANNHEIM_NGC3198_PARAMETERS, MANNHEIM_NGC3198_SPARC, MANNHEIM_NGC3198_CPP, NGC3198_COMMON_FIT_RESULT, NGC3198_COMMON_FIT_SCHEMA, NGC3198_COMMON_FIT_PROTOCOL, NGC3198_COMMON_FIT_CPP, AUDIT, LADDER, *LEDGERS, *local_evidence_paths, *local_report_paths, *reports]))
    for source in bundled_sources:
        outputs[SITE / "sources" / source.relative_to(ROOT)] = source.read_bytes()
    input_paths = sorted(set([Path(__file__).resolve(), FOUNDATIONS / "theory_viability.py", FOUNDATIONS / "theory_assembly.py", FOUNDATIONS / "build_gr_cassini_assembly.py", FOUNDATIONS / "check_gr_cassini_assembly.py", FOUNDATIONS / "verify_gr_cassini_assembly.py", FOUNDATIONS / "build_mannheim_ngc3198_assembly.py", FOUNDATIONS / "check_mannheim_ngc3198_assembly.py", FOUNDATIONS / "verify_mannheim_ngc3198_assembly.py", FOUNDATIONS / "build_ngc3198_common_fit_comparison.py", FOUNDATIONS / "check_ngc3198_common_fit_comparison.py", FOUNDATIONS / "verify_ngc3198_common_fit_comparison.py", FOUNDATIONS / "standard-gr-observational-control-v1.json", FOUNDATIONS / "schema/standard-gr-observational-control-v1.schema.json", *bundled_sources, ASSETS / "index.html", ASSETS / "styles.css", ASSETS / "app.js", V2_ASSETS / "app-v2.js"]))
    manifest = {
        "schema_version": "foundational-matrix-explorer-manifest-v2",
        "created": CREATED,
        "generator": rel(Path(__file__).resolve()),
        "canonical_data_digest": dataset["canonical_digest"],
        "inputs": [{"path": rel(path), "sha256": v1.sha(path)} for path in input_paths],
        "outputs": [{"path": rel(path), "sha256": v1.sha_bytes(content), "bytes": len(content)} for path, content in sorted(outputs.items())],
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    outputs[SITE / "manifest.json"] = manifest_bytes
    result = {
        "schema_version": "foundational-matrix-explorer-site-v2",
        "result_id": "FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2",
        "result_kind": "STATIC_EVIDENCE_EXPLORER",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "created": CREATED,
        "repository_base_commit": BASE_COMMIT,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": "Deterministic static exploration surface over the migration-reviewed foundations cube and cylinder implication ladder.",
        "counts": dataset["counts"],
        "features": ["sixteen 6x6 heatmaps", "complete 576-coordinate assessment surface", "reviewed-open-gap state distinct from priority and result", "dual local+literature cell marks", "per-evidence directness roles", "general-audience three-question dimensions guide", "grouped five-stage physical-obligation journey", "progressive-disclosure glossary and reviewer mechanics", "plain-language guide for all 28 axis options", "separate coverage and migration-review states", "migration evidence inspector", "multi-select filters", "full-text search", "cell inspector", "one-axis neighbors", "two-cell comparison", "URL permalinks", "filtered JSON and CSV export", "research-brief export", "three-pathway typed argument map with linked relation ledger", "strength ladder", "evidence catalogue", "theory-profile readiness map", "researcher-selectable obligation gates", "multi-carrier coverage-envelope composer", "non-scalar Pareto navigation", "separate composition, numerical-reproduction, and empirical-agreement rails", "three-way assembly subnavigation for bounded models, research programmes, and interface/calibration ledgers", "nine named research-programme lenses with explicit scope cautions", "first model-scoped GR-to-Cassini bounded prediction assembly", "second bounded Mannheim-to-NGC3198 assembly with a no-refit standardized-residual audit and mixed pass/fail gates", "first explicit uniform finite-approximant reconstruction of a declared bounded wave observable", "typed applicability mask", "exact field-equation-to-PPN-to-null-delay chain", "typed cross-cell interface ledger", "two certified scoped cross-cell bridges", "one certified scoped carrier non-identity", "independent maturity rails with missing distinct from failure", "empty fail-closed candidate empirical benchmark ledger", "external standard-GR positive control with four primary-source records", "ten-cell exact finite-operator closure", "twenty-cell exact finite-BRST closure"],
        "provenance": {"manifest": rel(SITE / "manifest.json"), "manifest_sha256": v1.sha_bytes(manifest_bytes), "canonical_data_digest": dataset["canonical_digest"], "viability_digest": viability["canonical_digest"], "assembly_digest": assemblies["canonical_digest"]},
        "independent_checker": {"path": "foundations/check_matrix_site_v2.py", "expected_cells": 576, "expected_emitted": 576, "expected_synthetic_not_mapped": 0, "expected_total_not_mapped": 0, "expected_reviewed_gaps": 172, "expected_evidence_records": 76, "expected_digest": dataset["canonical_digest"], "expected_viability_digest": viability["canonical_digest"], "expected_assembly_digest": assemblies["canonical_digest"]},
        "claim_flags": {"static_site_generated": True, "all_cartesian_coordinates_visible": True, "all_cartesian_coordinates_assessed": True, "zero_not_mapped": True, "reviewed_gaps_distinguished_from_results": True, "all_emitted_migrations_reviewed": True, "coverage_and_migration_separated": True, "all_used_evidence_resolved": True, "theory_profiles_generated": True, "theory_assembly_atlas_generated": True, "bounded_observable_reconstruction_exposed": True, "at_least_one_cross_cell_interface_certified": True, "composition_and_observation_rails_separated": True, "scientific_claims_duplicated_by_hand": False, "literature_complete": False, "unmapped_means_absent": False, "reviewed_gap_means_absent": False, "reviewed_no_transfer_means_absent": False, "priority_score_is_theorem": False, "complete_observationally_valid_theory_identified": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "a result for any of the 172 reviewed open gaps", "that REVIEWED_GAP or NOT_MAPPED means no literature exists", "that an UNREVIEWED evidence role is an absence of direct support", "that a dual LR mark composes its two records into a stronger result", "that all 576 coordinates are jointly realizable", "a weakest mathematical base", "full-state, representation-invariant, causal, or Weyl reconstruction from the single coded wave observable", "continuum renormalized products from finite regulated-product closure", "a Weyl QME or Weyl residual transfer from a finite toy BRST complex", "equivalence of carrier categories from one finite realization", "a theorem ranking from interface order, Pareto membership, or neighbor counts", "composition beyond the two certified scoped cross-cell interfaces", "precision sampler equivalence, continuum reconstruction, or empirical support from the BT finite lattice", "a complete observationally validated theory", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/matrix-explorer-site-v2.md",
    }
    outputs[RESULT] = (json.dumps(result, indent=2) + "\n").encode()
    outputs[REPORT] = render_report(result).encode()
    outputs[VIABILITY_RESULT] = viability_json
    outputs[VIABILITY_REPORT] = render_viability_report(viability).encode()
    outputs[ASSEMBLY_RESULT] = assembly_json
    outputs[ASSEMBLY_REPORT] = render_assembly_report(assemblies).encode()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts differ")
    args = parser.parse_args()
    outputs = generated()
    stale = [rel(path) for path, content in outputs.items() if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: wrote {len(outputs)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
