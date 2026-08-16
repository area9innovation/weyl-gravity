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
CUBE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json"
PREVIOUS_CUBES = [
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V5.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V6.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V7.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V9.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V12.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json",
    FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json",
]
TEN_CELL_CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1.json"
TWENTY_CELL_CLOSURE = FOUNDATIONS / "results/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1.json"
CORNER_BORN_INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
GROUND_STATE_DYNAMICS_INTERFACE = FOUNDATIONS / "results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json"
BT_EUCLIDEAN_IMPORT = FOUNDATIONS / "results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
FULL_SURFACE_AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
LADDER = FOUNDATIONS / "results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json"
COMPLETION_ATLAS = FOUNDATIONS / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V40.json"
COMPLETION_REPORT = FOUNDATIONS / "reports/lorentzian-weyl-bv-completion-atlas-v40.md"
COMPLETION_GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
COMPLETION_GATE_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V22.md"
COMPLETION_RESIDUAL_COMPARISON = ROOT / "quantum-weyl/classical_import/certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
COMPLETION_RESIDUAL_COMPARISON_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.md"
COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.md"
COMPLETION_ENDPOINT_SDR_BINDING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
COMPLETION_ENDPOINT_SDR_BINDING_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.md"
COMPLETION_LOCAL_CYCLIC_PAIRING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
COMPLETION_LOCAL_CYCLIC_PAIRING_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.md"
COMPLETION_RESIDUAL_SDR_TYPE_AUDIT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
COMPLETION_RESIDUAL_SDR_TYPE_AUDIT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.md"
COMPLETION_RESIDUAL_ZERO_MODES = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
COMPLETION_RESIDUAL_ZERO_MODES_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.md"
COMPLETION_CENTERED_COHOMOLOGY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
COMPLETION_CENTERED_COHOMOLOGY_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.md"
COMPLETION_SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
COMPLETION_SDR_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_DFINITE_RESIDUAL_SDR_V1.md"
COMPLETION_CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
COMPLETION_CYCLIC_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md"
COMPLETION_TRANSPORT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
COMPLETION_TRANSPORT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md"
COMPLETION_ENDPOINT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
COMPLETION_ENDPOINT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.md"
COMPLETION_SUSPENSION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
COMPLETION_SUSPENSION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.md"
COMPLETION_COMPONENT_PAIRING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
COMPLETION_COMPONENT_PAIRING_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.md"
COMPLETION_OPERATOR_PORTABILITY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.json"
COMPLETION_OPERATOR_PORTABILITY_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_OPERATOR_PORTABILITY_AUDIT_V1.md"
COMPLETION_Q1_SIGN_GATE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
COMPLETION_Q1_SIGN_GATE_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.md"
COMPLETION_Q1_SIGN_REPAIR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
COMPLETION_Q1_SIGN_REPAIR_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.md"
COMPLETION_FULL_Q1 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
COMPLETION_FULL_Q1_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.md"
COMPLETION_LOCAL_SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
COMPLETION_LOCAL_SDR_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.md"
COMPLETION_CANONICAL_SHEAR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
COMPLETION_CANONICAL_SHEAR_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.md"
COMPLETION_GREEN_ACTION_NAME = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
COMPLETION_GREEN_ACTION_NAME_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.md"
COMPLETION_UNARY_CAUSAL_SNAPSHOT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
COMPLETION_UNARY_CAUSAL_SNAPSHOT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.md"
COMPLETION_FULL_D = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_D_ACTION_V1.json"
COMPLETION_FULL_D_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_D_ACTION_V1.md"
COMPLETION_Q2_PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
COMPLETION_Q2_PREFLIGHT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.md"
COMPLETION_Q2_GREEN = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
COMPLETION_Q2_GREEN_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.md"
COMPLETION_RECURSIVE_TREES = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
COMPLETION_RECURSIVE_TREES_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.md"
COMPLETION_FORMAL_COEFFICIENTS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
COMPLETION_FORMAL_COEFFICIENTS_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.md"
COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.md"
COMPLETION_QUADRATIC_OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
COMPLETION_QUADRATIC_OBSTRUCTION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.md"
COMPLETION_Q3_WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
COMPLETION_Q3_WITNESS_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_PURE_WEYL_Q3_WITNESS_V1.md"
COMPLETION_MINIMAL_Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
COMPLETION_MINIMAL_Q3_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.md"
COMPLETION_ARITY3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
COMPLETION_ARITY3_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.md"
COMPLETION_Q3_CYCLICITY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
COMPLETION_Q3_CYCLICITY_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.md"
COMPLETION_Q3_STABILIZATION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.json"
COMPLETION_Q3_STABILIZATION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1.md"
COMPLETION_IDENTITY_OBSTRUCTION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
COMPLETION_IDENTITY_OBSTRUCTION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.md"
COMPLETION_QUADRATIC_ELIMINATION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
COMPLETION_QUADRATIC_ELIMINATION_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.md"
COMPLETION_CUBIC_INVENTORY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
COMPLETION_CUBIC_INVENTORY_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.md"
COMPLETION_HH_HV_LIFT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
COMPLETION_HH_HV_LIFT_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.md"
COMPLETION_DIFF_AUXILIARY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
COMPLETION_DIFF_AUXILIARY_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.md"
COMPLETION_GHOST_MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
COMPLETION_GHOST_MANIFEST_REPORT = ROOT / "d_quotient_classical/reports/classical-nonlinear-weyl-boost-ghost-manifest-v1.md"
COMPLETION_SHIFTED_MASS_Q2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
COMPLETION_SHIFTED_MASS_Q2_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.md"
COMPLETION_DIFF_AUXILIARY_V2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
COMPLETION_DIFF_AUXILIARY_V2_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.md"
COMPLETION_SOURCE_Q2 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
COMPLETION_SOURCE_Q2_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.md"
COMPLETION_CLASSICAL_QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
COMPLETION_CLASSICAL_QUARTIC_REPORT = ROOT / "d_quotient_classical/reports/classical-shifted-auxiliary-quartic-mass-v1.md"
COMPLETION_SHIFTED_MASS_Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
COMPLETION_SHIFTED_MASS_Q3_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.md"
COMPLETION_SOURCE_Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
COMPLETION_SOURCE_Q3_REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.md"
LEDGERS = v1.LEDGERS
CREATED = "2026-08-15"
BASE_COMMIT = "229fd0f2147e8ed611c5147328459f7678b1f605"

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
        for key in ("axes", "cells", "evidence", "ladder", "graph", "completion_atlas", "completion_common_endpoint_sdr_binding", "completion_endpoint_to_residual_comparison", "completion_residual_cyclic_carrier_obstruction", "completion_local_cyclic_pairing", "completion_residual_zero_modes", "completion_centered_cohomology", "completion_residual_sdr_type_audit", "cross_cell_interfaces", "carrier_interfaces", "numerical_reproducibility_records")
    }
    return v1.sha_bytes(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def build_dataset() -> dict[str, Any]:
    cube, audit, ladder, bt_import = v1.load(CUBE), v1.load(AUDIT), v1.load(LADDER), v1.load(BT_EUCLIDEAN_IMPORT)
    completion_atlas = v1.load(COMPLETION_ATLAS)
    completion_common_endpoint_sdr_binding = v1.load(COMPLETION_ENDPOINT_SDR_BINDING)
    completion_endpoint_to_residual_comparison = v1.load(COMPLETION_RESIDUAL_COMPARISON)
    completion_residual_cyclic_carrier_obstruction = v1.load(COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION)
    completion_local_cyclic_pairing = v1.load(COMPLETION_LOCAL_CYCLIC_PAIRING)
    completion_residual_zero_modes = v1.load(COMPLETION_RESIDUAL_ZERO_MODES)
    completion_centered_cohomology = v1.load(COMPLETION_CENTERED_COHOMOLOGY)
    completion_residual_sdr_type_audit = v1.load(COMPLETION_RESIDUAL_SDR_TYPE_AUDIT)
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
        "completion_atlas": completion_atlas,
        "completion_common_endpoint_sdr_binding": completion_common_endpoint_sdr_binding,
        "completion_endpoint_to_residual_comparison": completion_endpoint_to_residual_comparison,
        "completion_residual_cyclic_carrier_obstruction": completion_residual_cyclic_carrier_obstruction,
        "completion_local_cyclic_pairing": completion_local_cyclic_pairing,
        "completion_residual_zero_modes": completion_residual_zero_modes,
        "completion_centered_cohomology": completion_centered_cohomology,
        "completion_residual_sdr_type_audit": completion_residual_sdr_type_audit,
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
            "cube_report": site_link("foundations/reports/refined-intersection-cube-v14.md"),
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
            "completion_atlas": site_link(rel(COMPLETION_ATLAS)),
            "completion_atlas_report": site_link(rel(COMPLETION_REPORT)),
            "completion_gate": site_link(rel(COMPLETION_GATE)),
            "completion_gate_report": site_link(rel(COMPLETION_GATE_REPORT)),
            "completion_common_endpoint_sdr_binding": site_link(rel(COMPLETION_ENDPOINT_SDR_BINDING)),
            "completion_common_endpoint_sdr_binding_report": site_link(rel(COMPLETION_ENDPOINT_SDR_BINDING_REPORT)),
            "completion_endpoint_to_residual_comparison": site_link(rel(COMPLETION_RESIDUAL_COMPARISON)),
            "completion_endpoint_to_residual_comparison_report": site_link(rel(COMPLETION_RESIDUAL_COMPARISON_REPORT)),
            "completion_residual_cyclic_carrier_obstruction": site_link(rel(COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION)),
            "completion_residual_cyclic_carrier_obstruction_report": site_link(rel(COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION_REPORT)),
            "completion_local_cyclic_pairing": site_link(rel(COMPLETION_LOCAL_CYCLIC_PAIRING)),
            "completion_local_cyclic_pairing_report": site_link(rel(COMPLETION_LOCAL_CYCLIC_PAIRING_REPORT)),
            "completion_residual_zero_modes": site_link(rel(COMPLETION_RESIDUAL_ZERO_MODES)),
            "completion_residual_zero_modes_report": site_link(rel(COMPLETION_RESIDUAL_ZERO_MODES_REPORT)),
            "completion_centered_cohomology": site_link(rel(COMPLETION_CENTERED_COHOMOLOGY)),
            "completion_centered_cohomology_report": site_link(rel(COMPLETION_CENTERED_COHOMOLOGY_REPORT)),
            "completion_residual_sdr_type_audit": site_link(rel(COMPLETION_RESIDUAL_SDR_TYPE_AUDIT)),
            "completion_residual_sdr_type_audit_report": site_link(rel(COMPLETION_RESIDUAL_SDR_TYPE_AUDIT_REPORT)),
            "completion_sdr": site_link(rel(COMPLETION_SDR)),
            "completion_sdr_report": site_link(rel(COMPLETION_SDR_REPORT)),
            "completion_cyclic": site_link(rel(COMPLETION_CYCLIC)),
            "completion_cyclic_report": site_link(rel(COMPLETION_CYCLIC_REPORT)),
            "completion_transport": site_link(rel(COMPLETION_TRANSPORT)),
            "completion_transport_report": site_link(rel(COMPLETION_TRANSPORT_REPORT)),
            "completion_endpoint": site_link(rel(COMPLETION_ENDPOINT)),
            "completion_endpoint_report": site_link(rel(COMPLETION_ENDPOINT_REPORT)),
            "completion_suspension": site_link(rel(COMPLETION_SUSPENSION)),
            "completion_suspension_report": site_link(rel(COMPLETION_SUSPENSION_REPORT)),
            "completion_component_pairing": site_link(rel(COMPLETION_COMPONENT_PAIRING)),
            "completion_component_pairing_report": site_link(rel(COMPLETION_COMPONENT_PAIRING_REPORT)),
            "completion_operator_portability": site_link(rel(COMPLETION_OPERATOR_PORTABILITY)),
            "completion_operator_portability_report": site_link(rel(COMPLETION_OPERATOR_PORTABILITY_REPORT)),
            "completion_q1_sign_gate": site_link(rel(COMPLETION_Q1_SIGN_GATE)),
            "completion_q1_sign_gate_report": site_link(rel(COMPLETION_Q1_SIGN_GATE_REPORT)),
            "completion_q1_sign_repair": site_link(rel(COMPLETION_Q1_SIGN_REPAIR)),
            "completion_q1_sign_repair_report": site_link(rel(COMPLETION_Q1_SIGN_REPAIR_REPORT)),
            "completion_full_q1": site_link(rel(COMPLETION_FULL_Q1)),
            "completion_full_q1_report": site_link(rel(COMPLETION_FULL_Q1_REPORT)),
            "completion_local_sdr": site_link(rel(COMPLETION_LOCAL_SDR)),
            "completion_local_sdr_report": site_link(rel(COMPLETION_LOCAL_SDR_REPORT)),
            "completion_canonical_shear": site_link(rel(COMPLETION_CANONICAL_SHEAR)),
            "completion_canonical_shear_report": site_link(rel(COMPLETION_CANONICAL_SHEAR_REPORT)),
            "completion_green_action_name": site_link(rel(COMPLETION_GREEN_ACTION_NAME)),
            "completion_green_action_name_report": site_link(rel(COMPLETION_GREEN_ACTION_NAME_REPORT)),
            "completion_unary_causal_snapshot": site_link(rel(COMPLETION_UNARY_CAUSAL_SNAPSHOT)),
            "completion_unary_causal_snapshot_report": site_link(rel(COMPLETION_UNARY_CAUSAL_SNAPSHOT_REPORT)),
            "completion_full_d": site_link(rel(COMPLETION_FULL_D)),
            "completion_full_d_report": site_link(rel(COMPLETION_FULL_D_REPORT)),
            "completion_q2_preflight": site_link(rel(COMPLETION_Q2_PREFLIGHT)),
            "completion_q2_preflight_report": site_link(rel(COMPLETION_Q2_PREFLIGHT_REPORT)),
            "completion_q2_green": site_link(rel(COMPLETION_Q2_GREEN)),
            "completion_q2_green_report": site_link(rel(COMPLETION_Q2_GREEN_REPORT)),
            "completion_recursive_trees": site_link(rel(COMPLETION_RECURSIVE_TREES)),
            "completion_recursive_trees_report": site_link(rel(COMPLETION_RECURSIVE_TREES_REPORT)),
            "completion_formal_coefficients": site_link(rel(COMPLETION_FORMAL_COEFFICIENTS)),
            "completion_formal_coefficients_report": site_link(rel(COMPLETION_FORMAL_COEFFICIENTS_REPORT)),
            "completion_field_equation_quotient_inverse": site_link(rel(COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE)),
            "completion_field_equation_quotient_inverse_report": site_link(rel(COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE_REPORT)),
            "completion_quadratic_obstruction": site_link(rel(COMPLETION_QUADRATIC_OBSTRUCTION)),
            "completion_quadratic_obstruction_report": site_link(rel(COMPLETION_QUADRATIC_OBSTRUCTION_REPORT)),
            "completion_q3_witness": site_link(rel(COMPLETION_Q3_WITNESS)),
            "completion_q3_witness_report": site_link(rel(COMPLETION_Q3_WITNESS_REPORT)),
            "completion_minimal_q3": site_link(rel(COMPLETION_MINIMAL_Q3)),
            "completion_minimal_q3_report": site_link(rel(COMPLETION_MINIMAL_Q3_REPORT)),
            "completion_arity3": site_link(rel(COMPLETION_ARITY3)),
            "completion_arity3_report": site_link(rel(COMPLETION_ARITY3_REPORT)),
            "completion_q3_cyclicity": site_link(rel(COMPLETION_Q3_CYCLICITY)),
            "completion_q3_cyclicity_report": site_link(rel(COMPLETION_Q3_CYCLICITY_REPORT)),
            "completion_q3_stabilization": site_link(rel(COMPLETION_Q3_STABILIZATION)),
            "completion_q3_stabilization_report": site_link(rel(COMPLETION_Q3_STABILIZATION_REPORT)),
            "completion_identity_obstruction": site_link(rel(COMPLETION_IDENTITY_OBSTRUCTION)),
            "completion_identity_obstruction_report": site_link(rel(COMPLETION_IDENTITY_OBSTRUCTION_REPORT)),
            "completion_quadratic_elimination": site_link(rel(COMPLETION_QUADRATIC_ELIMINATION)),
            "completion_quadratic_elimination_report": site_link(rel(COMPLETION_QUADRATIC_ELIMINATION_REPORT)),
            "completion_cubic_inventory": site_link(rel(COMPLETION_CUBIC_INVENTORY)),
            "completion_cubic_inventory_report": site_link(rel(COMPLETION_CUBIC_INVENTORY_REPORT)),
            "completion_hh_hv_lift": site_link(rel(COMPLETION_HH_HV_LIFT)),
            "completion_hh_hv_lift_report": site_link(rel(COMPLETION_HH_HV_LIFT_REPORT)),
            "completion_diff_auxiliary": site_link(rel(COMPLETION_DIFF_AUXILIARY)),
            "completion_diff_auxiliary_report": site_link(rel(COMPLETION_DIFF_AUXILIARY_REPORT)),
            "completion_ghost_manifest": site_link(rel(COMPLETION_GHOST_MANIFEST)),
            "completion_ghost_manifest_report": site_link(rel(COMPLETION_GHOST_MANIFEST_REPORT)),
            "completion_shifted_mass_q2": site_link(rel(COMPLETION_SHIFTED_MASS_Q2)),
            "completion_shifted_mass_q2_report": site_link(rel(COMPLETION_SHIFTED_MASS_Q2_REPORT)),
            "completion_diff_auxiliary_v2": site_link(rel(COMPLETION_DIFF_AUXILIARY_V2)),
            "completion_diff_auxiliary_v2_report": site_link(rel(COMPLETION_DIFF_AUXILIARY_V2_REPORT)),
            "completion_source_q2": site_link(rel(COMPLETION_SOURCE_Q2)),
            "completion_source_q2_report": site_link(rel(COMPLETION_SOURCE_Q2_REPORT)),
            "completion_classical_quartic": site_link(rel(COMPLETION_CLASSICAL_QUARTIC)),
            "completion_classical_quartic_report": site_link(rel(COMPLETION_CLASSICAL_QUARTIC_REPORT)),
            "completion_shifted_mass_q3": site_link(rel(COMPLETION_SHIFTED_MASS_Q3)),
            "completion_shifted_mass_q3_report": site_link(rel(COMPLETION_SHIFTED_MASS_Q3_REPORT)),
            "completion_source_q3": site_link(rel(COMPLETION_SOURCE_Q3)),
            "completion_source_q3_report": site_link(rel(COMPLETION_SOURCE_Q3_REPORT)),
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
All **576** are now emitted by cube v15 and have separate coverage and migration
review fields: **{counts['migration_reviewed']} reviewed**, **{counts['migration_pending']} pending**.
The surface has **{counts['reviewed_gap']} `REVIEWED_GAP`** cells and **{counts['not_mapped']}
`NOT_MAPPED`** cells. A reviewed gap is a formulated open question with a typed
missing certificate; it is not a result, a selected priority, or a literature-absence claim.
There are **{counts['synthetic_not_mapped']}** browser-only complements.

The full-surface audit preserves all 401 prior positive, partial, and priority
classifications. It revises 51 emitted blanks and directly assesses the 124
formerly synthetic coordinates without transferring evidence from neighbors.

Cube v14 preserves two certified `CONDITIONAL_BRIDGE` relations. The first maps an
algebraic finite-corner state to a Krein probability rule under five explicit
hypotheses. The second uses the free Fock energy gap to select the unique normal
zero-energy vacuum state and proves that the same state is invariant under the
generated Krein--Fock dynamics. The other assembly interfaces remain open.

Cube v14 also preserves the positive BT Euclidean finite lattice import into five direct
`FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL` cells. Its independent-sampler record
is coarse numerical reproduction, not empirical validation. A separate carrier
interface refuses only identification of the positive Euclidean measure with the
all-real BT/Krein path integral; controlled conditional bridges remain open.

The **Weyl BV routes** view projects the current audited Lorentzian completion atlas as
seven architectures across eleven ordered gates, for 77 separately typed cells.
It exposes the finite residual-SDR repair, nine ranked next constructions and the
eleven-step Berger H26/C26 decision chain.  The ranking is a planning aid, not a theorem; in particular,
the rational non-cone feasibility control prevents the scoped 104-row failures
from being promoted to a general non-cone no-go.

Atlas V40 preserves the field-equation type result.  The degree-one-to-zero
Green component is an exact right inverse on Noether-compatible sources and a
left inverse modulo gauge.  The stronger full ungauge-fixed inverse is impossible:
the exact nonzero gauge and Noether maps obey `K R=0` and `N K=0`.  The retired
inverse route is replaced by the coefficientwise nonlinear-source test `N S_m=0`.
At lambda squared, an exact pure-diffeomorphism fixture now proves that the
quadratic-only source is not closed: its Weyl Noether defect is `37880/27`.
The action-derived cubic Bach receiver realizes that target exactly:
`q1 q3=-75760/9`.  Its authoritative successor now exports the arbitrary-input
minimal q3, replays all 72 typed arity-three channels and 212 composable paths,
and proves S4 quartic cyclicity modulo horizontal boundary terms.  These are
minimal-carrier results.  Exact zero-extension over the 356-row contractible
complement followed by the accepted BV-canonical shear now gives a 386-row
candidate q3 with sixteen potentially nonzero ternary block channels.  Orthogonal
direct sum and exact conjugation transport the 72-channel/212-path arity-three
identity, S3 symmetry, S4 cyclicity modulo boundary terms, and D/q3 derivation
with zero defects.  This is a valid stabilization construction, not an authoritative
nonminimal import.  The theory-identity test now has a decisive exact witness:
the authoritative ordinary-derivative action gives
`Omega(f_hat,q2(v,v))=-1`, while the trivial stabilization gives zero.  Literal
identity and the linear-shear-only route are therefore refuted.  Nonlinear
equivalence is now constructive at first order: the exact quadratic auxiliary
map contributes `+1`, taking the source channel from `-1` to `0`, equal to the
candidate.  This first nonlinear component closes one channel.  The full source
pullback remains open.  The successor census enumerates seven known-required
cubic families.  Two are component-exact: the shifted mass has 72 nonzero
`h-f_hat-f_hat` coefficients, while the vv canonical transformation has 22
field and 16 cotangent-partner coefficients with zero defect in all four
pairing slices.  The 72-to-zero comparison proves that the vv shift alone is
not the full normalization; it does not obstruct a further local canonical or
L-infinity normalization.  The hh/hv, three Diff, and possible nonlinear
Weyl/boost ghost-antifield families remain explicit fronts.  The successor now
closes the curved hh/hv route: 1,392 hh, 76 hv, and 22 vv field coefficients
induce 3,907 collected cotangent coefficients with zero formal-adjoint defect.
Thus the complete quadratic auxiliary canonical lift is serialized and four of
seven known families are component-complete.  The successor closes the three
Diff families as well: 264 master-density coefficients generate 336 field, 632
antifield, and 704 `c_star` coefficients with zero variational or Koszul defect.
All seven known-required families are therefore component-complete.  The
primary-source completion of Metsaev's nonlinear boost law now proves that the
Weyl/boost internal algebra is Abelian and the shifted auxiliary tensor is
invariant.  Thus the seven previously tracked auxiliary families are
exhaustive in the declared source scope and no additional Weyl/boost
ghost-antifield family is required.  In shifted source coordinates, three of
the seven are type-II coordinate-map data rather than source-vector-field
operations.  The actual source q2 has sixteen families: twelve minimal plus
the shifted-mass vertex and three auxiliary Diff representations.  The
shifted-mass lift has 392 ordered q2 coefficients and zero defects in 3,000
cyclic equalities.  A common replay then exposed a receiver convention
mismatch: auxiliary Diff V1 left 336 exact q1/q2 defects.  Applying the already
certified `T(c_star)=-c_star` translation in append-only V2 removes all 336.
The accepted common q2 snapshot now binds 22 minimal operations with 2,064
auxiliary coefficients, extends by zero over the receiver-added split cone,
and transports canonically to graph coordinates.  Its q1/q2, cyclicity and
stationary D/q2 defect counts are all zero.  The exact auxiliary quartic mass
then supplies 321 independent monomials, 912 ordered fourth variations and
5,952 paired q3 coefficients.  Together with minimal Bach q3 these exhaust the
two source families; arity three, cyclicity modulo horizontal boundary and
stationary D/q3 have zero split/graph defects.  The exact residual export now
serializes fifteen primal and fifteen normalized dual zero modes, all 120
nonzero SO(4,2) structure coefficients, fifteen adjoint/coadjoint/cotangent
representation matrices, and the zero 30-by-30 unary residual differential.
Its independent receiver replays the basis, projectors, pairing, Jacobi,
unimodularity, representation, coadjoint and nilpotency identities without a
defect.  The centered successor exports ordered C3, C4 and C5 bases with
dimensions 727, 3,084 and 8,532, reconstructs 85,091 rational differential
coefficients, and proves ranks 636 and 2,446.  Its two sparse chiral H4 vectors
have identity Gram and are exchanged by parity.  Gate V17 therefore closes the
coefficient-level M5 and M6 packages and retains the accepted q2 hash.  It
remains fail closed because neither new candidate hash is bound to the common
snapshot: six of seven top-level hashes, the common support-local residual SDR,
the full cyclic pairing and the final common contraction remain open.
The next audit finds that this last phrase hid three carrier types.  The graph
SDR contracts 386 local component species to 30 local endpoint field species;
the D-finite residual SDR contracts 4,490 harmonic coefficients to 470 W+/W-
coefficients; and M5's separate 30 counts conformal-Killing cotangent
coefficients.  A constant or harmonic projector expands support, so the
reduced-mode receivers cannot be inserted as support-local maps in causal
Green transfer.  Gate V18 replaced the old M3 item by M3L common endpoint-SDR
binding and M3R typed spectral comparison.  Gate V19 closed M3L: ten
artifacts and seventeen canonical object hashes bind the exact 386-to-30 local
endpoint SDR to the common q1/q2/q3/D carrier, with fifteen compatibility links
and zero projected identity defects.  Gate V20 now closes M4L: all 386 local
rows carry a rank-386 odd pairing with 410 ordered rational entries, and the
q1/endpoint-SDR/D/q2/q3 cyclicity defects vanish.  The old M4 requirement is
split because these rows contain no W+/W- harmonic residual coefficients.
Gate V21 now closes M3R on the represented D-finite domain: all 470
positive-energy residual coordinates have explicit E/A/L magnetic labels,
normalized synthesis names, an exact bijective crosswalk, and zero retraction
or q0-chain defects.  The harmonic restriction is global and is not promoted
to a support-local or all-energy map.  Gate V22 then tests the missing cyclic
step rather than assuming it.  All 470 synthesis columns land in degree-zero
metric slots, while the degree-minus-one BV form has no metric--metric block.
Its literal pullback therefore has rank zero and nullity 470.  The older
cross-energy form is symmetric and even, not the field-theoretic BV
antibracket.  A 940-coordinate shifted-cotangent preflight has an exact
rank-940 odd pairing, but its dual endpoint maps and action-pairing
identification remain open.  No new top-level hash is accepted; M3RC, M4R,
and M1 remain in that dependency order.
The complete Berger q3 remains a different-theory Weyl-plus-clock result on a fixed
54-row carrier; no certified same-theory cyclic map authorizes its direct import.

The strict thirty-row endpoint is no longer a type-only match.  The Gate-V5 and
causal-endpoint unary operators agree in all 80 multiindex tables, including all
700 independent Bach four-jet columns.  The five-row transported ghost-pairing
sign is the exact Gate suspension character.  The pre-pullback endpoint pairing
has 54 ordered nonzero entries, while its pullback to the thirty Gate coordinates
has 30.  The full 386-row hybrid basis and rank-386 pairing are now serialized:
the 356-row complement splits as 36 auxiliary plus 320 cone rows and the full
pairing has 410 ordered entries.  The componentwise T adjoint replays exactly.
The four-row auxiliary cotangent sign conflict is repaired in source and
ledgers and propagated through the full covariant suite with 82/82 terminal
overclaim guards. The full q1 is now a content-addressed unary snapshot:
18 operator tables, 127 jet tables and 2,193 rational coefficients on all
386 rows, with exact nilpotency and zero suspended-cyclicity defects. Local
The unary SDR, canonical shear and represented Green actions are serialized.
What remains open at the nonlinear frontier is q2/q3 Green compatibility,
the complete Gate-A freeze, Hadamard and QME.

The new reconstruction import supplies the first explicit weak-arithmetic
finite-approximant theorem for a declared bounded wave observable. Its rational
dyadic interpolants converge uniformly on every rational bounded time interval
with cutoff `N(k)=k+ell(K)+1`. It reconstructs one smeared scalar observable,
not the full field, causal support, or a Weyl-gravity prediction.

The localized weak-wave import adds ten rational characteristic-strip tests.
Their exact rank-10 labelled measurement matrix separates the declared finite
chiral coefficients, and the transport and scalar wave residuals vanish
coefficient by coefficient.  This is a finite coded test span, not a theorem for
every smooth test function, strict causal support, or a Green operator.

The named H2 completion then embeds those tests in a countable rational C1
piecewise-polynomial carrier.  A supplied fast H2 name gives explicit residual
cutoffs and a continuous distributional field-state map on the fixed slab.  The
name is representation data: this does not reconstruct the unrestricted
nonmetrizable LF test topology or prove uniqueness among arbitrary distributions.

The new representation-to-causality slice closes the next three declared gates.
A fixed-support smooth name with explicit derivative and support advice now translates
to the rational H2 carrier with an exact cutoff modulus.  Support tags assemble these
fixed stages into a represented compact-test union, with a firewall against identifying
that union with the full locally convex LF topology.  Finally, canonical retarded and
advanced Green maps for the flat scalar 1+1 wave operator satisfy exact inverse
identities, causal support, and adjoint duality.  That `LORENTZIAN-CAUSAL` result is a
scalar benchmark, not a Weyl/BV propagator or quantum causal construction.

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
    app = (ASSETS / "app.js").read_text().replace(
        '["matrix", "viability", "assemblies", "guide", "graph", "ladder", "evidence"]',
        '["matrix", "viability", "assemblies", "guide", "graph", "ladder", "completion", "evidence"]',
    ).replace(
        '["viability", "assemblies", "guide", "graph", "ladder"].includes(view)',
        '["viability", "assemblies", "guide", "graph", "ladder", "completion"].includes(view)',
    ).encode()
    index = (ASSETS / "index.html").read_text().replace(
        '    <button class="tab" data-view="evidence">Evidence</button>',
        '    <button class="tab" data-view="completion">Weyl BV routes</button>\n    <button class="tab" data-view="evidence">Evidence</button>',
    ).replace(
        '    <section id="evidenceView" class="view">',
        '    <section id="completionView" class="view">\n      <div class="section-head"><div><p class="eyebrow">From survey to causal construction</p><h2>Lorentzian Weyl BV completion routes</h2></div><p>Seven architectures cross eleven gates. A colored cell reports a scoped evidence state—not a probability that the theory is true.</p></div>\n      <div id="completionExplorer"></div>\n    </section>\n\n    <section id="evidenceView" class="view">',
    ).replace(
        '<script src="data.js"></script>',
        '<script src="data.js"></script>\n  <script src="viability.js"></script>\n  <script src="assemblies.js"></script>',
    ).replace(
        '<script src="app.js"></script>',
        '<script src="app.js"></script>\n  <script src="migration-review.js"></script>',
    ).encode()
    outputs: dict[Path, bytes] = {
        SITE / "index.html": index,
        SITE / "styles.css": (ASSETS / "styles.css").read_bytes() + b"\n" + (V2_ASSETS / "styles-v2.css").read_bytes(),
        SITE / "app.js": app,
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
    completion_evidence_paths = [ROOT / item["path"] for item in dataset["completion_atlas"]["provenance"]["inputs"]]
    reports = [
        FOUNDATIONS / "reports/refined-intersection-cube-v14.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v13.md",
        FOUNDATIONS / "reports/refined-intersection-cube-v12.md",
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
        COMPLETION_REPORT,
        COMPLETION_GATE_REPORT,
        COMPLETION_ENDPOINT_SDR_BINDING_REPORT,
        COMPLETION_RESIDUAL_COMPARISON_REPORT,
        COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION_REPORT,
        COMPLETION_LOCAL_CYCLIC_PAIRING_REPORT,
        COMPLETION_RESIDUAL_ZERO_MODES_REPORT,
        COMPLETION_CENTERED_COHOMOLOGY_REPORT,
        COMPLETION_RESIDUAL_SDR_TYPE_AUDIT_REPORT,
        COMPLETION_GREEN_ACTION_NAME_REPORT,
        COMPLETION_UNARY_CAUSAL_SNAPSHOT_REPORT,
        COMPLETION_FULL_D_REPORT,
        COMPLETION_Q2_PREFLIGHT_REPORT,
        COMPLETION_Q2_GREEN_REPORT,
        COMPLETION_RECURSIVE_TREES_REPORT,
        COMPLETION_FORMAL_COEFFICIENTS_REPORT,
        COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE_REPORT,
        COMPLETION_QUADRATIC_OBSTRUCTION_REPORT,
        COMPLETION_Q3_WITNESS_REPORT,
        COMPLETION_MINIMAL_Q3_REPORT,
        COMPLETION_ARITY3_REPORT,
        COMPLETION_Q3_CYCLICITY_REPORT,
        COMPLETION_Q3_STABILIZATION_REPORT,
        COMPLETION_IDENTITY_OBSTRUCTION_REPORT,
        COMPLETION_QUADRATIC_ELIMINATION_REPORT,
        COMPLETION_CUBIC_INVENTORY_REPORT,
        COMPLETION_HH_HV_LIFT_REPORT,
        COMPLETION_DIFF_AUXILIARY_REPORT,
        COMPLETION_GHOST_MANIFEST_REPORT,
        COMPLETION_SHIFTED_MASS_Q2_REPORT,
        COMPLETION_DIFF_AUXILIARY_V2_REPORT,
        COMPLETION_SOURCE_Q2_REPORT,
        COMPLETION_CLASSICAL_QUARTIC_REPORT,
        COMPLETION_SHIFTED_MASS_Q3_REPORT,
        COMPLETION_SOURCE_Q3_REPORT,
    ]
    bundled_sources = sorted(set([CUBE, *PREVIOUS_CUBES, FULL_SURFACE_AUDIT, CORNER_BORN_INTERFACE, GROUND_STATE_DYNAMICS_INTERFACE, BT_EUCLIDEAN_IMPORT, GR_CASSINI_RESULT, GR_CASSINI_SCHEMA, MANNHEIM_NGC3198_RESULT, MANNHEIM_NGC3198_SCHEMA, MANNHEIM_NGC3198_PARAMETERS, MANNHEIM_NGC3198_SPARC, MANNHEIM_NGC3198_CPP, NGC3198_COMMON_FIT_RESULT, NGC3198_COMMON_FIT_SCHEMA, NGC3198_COMMON_FIT_PROTOCOL, NGC3198_COMMON_FIT_CPP, AUDIT, LADDER, COMPLETION_ATLAS, COMPLETION_REPORT, COMPLETION_GATE, COMPLETION_GATE_REPORT, COMPLETION_ENDPOINT_SDR_BINDING, COMPLETION_ENDPOINT_SDR_BINDING_REPORT, COMPLETION_LOCAL_CYCLIC_PAIRING, COMPLETION_LOCAL_CYCLIC_PAIRING_REPORT, COMPLETION_RESIDUAL_ZERO_MODES, COMPLETION_RESIDUAL_ZERO_MODES_REPORT, COMPLETION_CENTERED_COHOMOLOGY, COMPLETION_CENTERED_COHOMOLOGY_REPORT, COMPLETION_RESIDUAL_SDR_TYPE_AUDIT, COMPLETION_RESIDUAL_SDR_TYPE_AUDIT_REPORT, COMPLETION_SDR, COMPLETION_SDR_REPORT, COMPLETION_CYCLIC, COMPLETION_CYCLIC_REPORT, COMPLETION_TRANSPORT, COMPLETION_TRANSPORT_REPORT, COMPLETION_ENDPOINT, COMPLETION_ENDPOINT_REPORT, COMPLETION_SUSPENSION, COMPLETION_SUSPENSION_REPORT, COMPLETION_COMPONENT_PAIRING, COMPLETION_COMPONENT_PAIRING_REPORT, COMPLETION_OPERATOR_PORTABILITY, COMPLETION_OPERATOR_PORTABILITY_REPORT, COMPLETION_Q1_SIGN_GATE, COMPLETION_Q1_SIGN_GATE_REPORT, COMPLETION_Q1_SIGN_REPAIR, COMPLETION_Q1_SIGN_REPAIR_REPORT, COMPLETION_FULL_Q1, COMPLETION_FULL_Q1_REPORT, COMPLETION_LOCAL_SDR, COMPLETION_LOCAL_SDR_REPORT, COMPLETION_CANONICAL_SHEAR, COMPLETION_CANONICAL_SHEAR_REPORT, COMPLETION_GREEN_ACTION_NAME, COMPLETION_GREEN_ACTION_NAME_REPORT, COMPLETION_UNARY_CAUSAL_SNAPSHOT, COMPLETION_UNARY_CAUSAL_SNAPSHOT_REPORT, COMPLETION_FULL_D, COMPLETION_FULL_D_REPORT, COMPLETION_Q2_PREFLIGHT, COMPLETION_Q2_PREFLIGHT_REPORT, COMPLETION_Q2_GREEN, COMPLETION_Q2_GREEN_REPORT, COMPLETION_RECURSIVE_TREES, COMPLETION_RECURSIVE_TREES_REPORT, COMPLETION_FORMAL_COEFFICIENTS, COMPLETION_FORMAL_COEFFICIENTS_REPORT, COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE, COMPLETION_FIELD_EQUATION_QUOTIENT_INVERSE_REPORT, COMPLETION_QUADRATIC_OBSTRUCTION, COMPLETION_QUADRATIC_OBSTRUCTION_REPORT, COMPLETION_Q3_WITNESS, COMPLETION_Q3_WITNESS_REPORT, COMPLETION_MINIMAL_Q3, COMPLETION_MINIMAL_Q3_REPORT, COMPLETION_ARITY3, COMPLETION_ARITY3_REPORT, COMPLETION_Q3_CYCLICITY, COMPLETION_Q3_CYCLICITY_REPORT, COMPLETION_CUBIC_INVENTORY, COMPLETION_CUBIC_INVENTORY_REPORT, COMPLETION_HH_HV_LIFT, COMPLETION_HH_HV_LIFT_REPORT, *LEDGERS, *local_evidence_paths, *local_report_paths, *reports]))
    bundled_sources = sorted(set([*bundled_sources, COMPLETION_DIFF_AUXILIARY, COMPLETION_DIFF_AUXILIARY_REPORT, COMPLETION_GHOST_MANIFEST, COMPLETION_GHOST_MANIFEST_REPORT, COMPLETION_CLASSICAL_QUARTIC, COMPLETION_CLASSICAL_QUARTIC_REPORT, COMPLETION_SHIFTED_MASS_Q3, COMPLETION_SHIFTED_MASS_Q3_REPORT, COMPLETION_SOURCE_Q3, COMPLETION_SOURCE_Q3_REPORT, *completion_evidence_paths]))
    bundled_sources = sorted(set([*bundled_sources, COMPLETION_RESIDUAL_COMPARISON, COMPLETION_RESIDUAL_COMPARISON_REPORT, COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION, COMPLETION_RESIDUAL_CYCLIC_OBSTRUCTION_REPORT]))
    for source in bundled_sources:
        outputs[SITE / "sources" / source.relative_to(ROOT)] = source.read_bytes()
    input_paths = sorted(set([Path(__file__).resolve(), FOUNDATIONS / "theory_viability.py", FOUNDATIONS / "theory_assembly.py", FOUNDATIONS / "build_gr_cassini_assembly.py", FOUNDATIONS / "check_gr_cassini_assembly.py", FOUNDATIONS / "verify_gr_cassini_assembly.py", FOUNDATIONS / "build_mannheim_ngc3198_assembly.py", FOUNDATIONS / "check_mannheim_ngc3198_assembly.py", FOUNDATIONS / "verify_mannheim_ngc3198_assembly.py", FOUNDATIONS / "build_ngc3198_common_fit_comparison.py", FOUNDATIONS / "check_ngc3198_common_fit_comparison.py", FOUNDATIONS / "verify_ngc3198_common_fit_comparison.py", FOUNDATIONS / "standard-gr-observational-control-v1.json", FOUNDATIONS / "schema/standard-gr-observational-control-v1.schema.json", *bundled_sources, ASSETS / "index.html", ASSETS / "styles.css", ASSETS / "app.js", V2_ASSETS / "app-v2.js", V2_ASSETS / "styles-v2.css"]))
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
        "scope": "Deterministic static exploration surface over the migration-reviewed foundations cube, cylinder implication ladder, and Lorentzian Weyl BV completion routes.",
        "counts": dataset["counts"],
        "features": ["sixteen 6x6 heatmaps", "complete 576-coordinate assessment surface", "reviewed-open-gap state distinct from priority and result", "dual local+literature cell marks", "per-evidence directness roles", "general-audience three-question dimensions guide", "grouped five-stage physical-obligation journey", "progressive-disclosure glossary and reviewer mechanics", "plain-language guide for all 28 axis options", "separate coverage and migration-review states", "migration evidence inspector", "multi-select filters", "full-text search", "cell inspector", "one-axis neighbors", "two-cell comparison", "URL permalinks", "filtered JSON and CSV export", "research-brief export", "three-pathway typed argument map with linked relation ledger", "strength ladder", "evidence catalogue", "theory-profile readiness map", "researcher-selectable obligation gates", "multi-carrier coverage-envelope composer", "non-scalar Pareto navigation", "separate composition, numerical-reproduction, and empirical-agreement rails", "three-way assembly subnavigation for bounded models, research programmes, and interface/calibration ledgers", "nine named research-programme lenses with explicit scope cautions", "first model-scoped GR-to-Cassini bounded prediction assembly", "second bounded Mannheim-to-NGC3198 assembly with a no-refit standardized-residual audit and mixed pass/fail gates", "first explicit uniform finite-approximant reconstruction of a declared bounded wave observable", "finite localized rank-10 chiral test class with coefficient-wise weak wave identities", "named H2 test completion with explicit residual modulus and distributional state map", "fixed-support smooth-name to rational H2 translator", "support-indexed represented test-space comparison with LF boundary", "exact flat scalar 1+1 retarded, advanced, and biwave Green benchmarks", "fail-closed sixteen-gate scalar-biwave-to-Weyl-BV dependency delta", "typed strict-operator portability split for local tables and nonlocal Green actions", "historical auxiliary-q sign diagnosis plus certified source/ledger/pairing repair", "complete content-addressed 386-row unary q1 snapshot with nilpotency and suspended-cyclicity replay", "exact 386-row T/A/B canonical shear and inverse with ordered cross terms", "canonical Hodge-projector Duhamel names for both full-graph Green orientations", "thirteen-hash accepted unary-causal common snapshot distinct from Gate A", "exact full-cylinder flow on all 386 graph rows with unary commutator and pairing-adjoint replay", "exact cyclic 386-row stabilized-q2 candidate with a fail-closed authoritative-theory boundary", "candidate first nonlinear retarded/advanced response with causal support and foundational stratification", "all finite polarized candidate q2/Green trees on PC/FC domains with an exact four-leaf mixed-sign boundary", "exact Catalan-weighted polarized formal coefficients with a lambda-squared BV promotion gate", "typed 116-by-116 field-equation Green component with constrained/quotient inverse and a full-inverse no-go", "exact quadratic-truncation source obstruction with an authoritative cubic-bracket cancellation target", "exact 41-term pure-Weyl cubic metric witness realizing the arity-three target with a Berger direct-import firewall", "authoritative arbitrary-input six-row minimal q3 with exhaustive 72-channel/212-path arity-three identity and S4 quartic cyclicity", "Gate V11 reconciliation with a complete curved quadratic auxiliary BV lift", "typed applicability mask", "exact field-equation-to-PPN-to-null-delay chain", "typed cross-cell interface ledger", "two certified scoped cross-cell bridges", "one certified scoped carrier non-identity", "independent maturity rails with missing distinct from failure", "empty fail-closed candidate empirical benchmark ledger", "external standard-GR positive control with four primary-source records", "ten-cell exact finite-operator closure", "twenty-cell exact finite-BRST closure"],
        "provenance": {"manifest": rel(SITE / "manifest.json"), "manifest_sha256": v1.sha_bytes(manifest_bytes), "canonical_data_digest": dataset["canonical_digest"], "viability_digest": viability["canonical_digest"], "assembly_digest": assemblies["canonical_digest"], "completion_atlas_sha256": v1.sha(COMPLETION_ATLAS)},
        "independent_checker": {"path": "foundations/check_matrix_site_v2.py", "expected_cells": 576, "expected_emitted": 576, "expected_synthetic_not_mapped": 0, "expected_total_not_mapped": 0, "expected_reviewed_gaps": 169, "expected_evidence_records": 83, "expected_digest": dataset["canonical_digest"], "expected_viability_digest": viability["canonical_digest"], "expected_assembly_digest": assemblies["canonical_digest"]},
        "claim_flags": {"static_site_generated": True, "all_cartesian_coordinates_visible": True, "all_cartesian_coordinates_assessed": True, "zero_not_mapped": True, "reviewed_gaps_distinguished_from_results": True, "all_emitted_migrations_reviewed": True, "coverage_and_migration_separated": True, "all_used_evidence_resolved": True, "theory_profiles_generated": True, "theory_assembly_atlas_generated": True, "bounded_observable_reconstruction_exposed": True, "localized_coefficient_weak_wave_exposed": True, "named_h2_test_completion_exposed": True, "smooth_to_h2_translator_exposed": True, "support_indexed_test_comparison_exposed": True, "scalar_green_choice_audit_exposed": True, "strict_graph_green_names_exposed": True, "strict_unary_causal_snapshot_exposed": True, "strict_full_d_action_exposed": True, "strict_d_q1_replay_exposed": True, "strict_stabilized_q2_candidate_exposed": True, "strict_stabilized_d_q2_derivation_exposed": True, "strict_candidate_q2_green_first_response_exposed": True, "strict_candidate_q2_green_foundations_exposed": True, "strict_candidate_polarized_finite_trees_exposed": True, "strict_first_mixed_sign_domain_nondefinition_exposed": True, "strict_candidate_polarized_formal_coefficients_exposed": True, "strict_lambda_adic_stabilization_exposed": True, "strict_lambda_squared_bv_promotion_gate_exposed": True, "strict_field_equation_green_component_exposed": True, "strict_field_equation_quotient_inverse_exposed": True, "strict_ungauge_fixed_full_inverse_obstruction_exposed": True, "strict_all_order_source_closure_exposed": False, "strict_authoritative_q2_green_compatibility_exposed": False, "strict_recursive_nonlinear_green_trees_exposed": False, "strict_unrestricted_mixed_sign_trees_exposed": False, "strict_arbitrary_causal_difference_trees_exposed": False, "strict_infinite_tree_series_convergence_exposed": False, "strict_typed_field_equation_green_inverse_exposed": False, "strict_weyl_bv_maurer_cartan_series_exposed": False, "strict_authoritative_formal_moller_map_exposed": False, "strict_analytic_moller_convergence_exposed": False, "strict_nonperturbative_moller_map_exposed": False, "strict_authoritative_full_carrier_q2_exposed": False, "strict_full_carrier_q2_exposed": False, "strict_classical_gate_a_passed": False, "at_least_one_cross_cell_interface_certified": True, "composition_and_observation_rails_separated": True, "scientific_claims_duplicated_by_hand": False, "literature_complete": False, "unmapped_means_absent": False, "reviewed_gap_means_absent": False, "reviewed_no_transfer_means_absent": False, "priority_score_is_theorem": False, "complete_observationally_valid_theory_identified": False, "new_lorentzian_claim": True},
        "does_not_establish": ["literature completeness", "a result for any of the 169 reviewed open gaps", "that REVIEWED_GAP or NOT_MAPPED means no literature exists", "that an UNREVIEWED evidence role is an absence of direct support", "that a dual LR mark composes its two records into a stronger result", "that all 576 coordinates are jointly realizable", "a weakest mathematical base", "full-state, representation-invariant, causal, or Weyl reconstruction from the single coded wave observable", "the unrestricted LF smooth-test topology from the represented support-indexed union", "surjectivity of the smooth-test embedding onto H2", "uniqueness among arbitrary distributional solutions from energy-image uniqueness", "a variable-coefficient, curved-spacetime, Weyl, or metric-BV Green operator from the scalar 1+1 benchmark", "an effective strict 386-row Green solver or serialized distribution-kernel bytes", "a full two-sided inverse on the ungauge-fixed Weyl field/equation spaces", "a selected gauge representative from the quotient inverse", "that the exact stabilized-q2 candidate is the authoritative nonlinear classical Weyl BV extension", "authoritative q2/Green compatibility from candidate first-response compatibility", "unrestricted mixed-sign or arbitrary causal-difference trees from the certified polarized finite recursion", "a Weyl-BV Maurer-Cartan or Moller map from the candidate formal fixed-point coefficients", "analytic convergence, a convergence radius, or a nonperturbative Moller inverse from lambda-adic stabilization", "a 386-row cyclic q3 stabilization or general source closure from the completed minimal q3 package", "a direct strict pure-Weyl import of the complete Berger-plus-clock q3", "a no-go theorem for full Weyl gravity from the quadratic-only obstruction", "all-order nonlinear source-cocycle closure", "q3 or higher causal brackets", "a weakest-base or choice-free proof of the infinite analytic Green layer", "the metric-dependent auxiliary q3, full arity-three source assembly, or q2/Green compatibility", "a D-Cartan homotopy or physical charge classification from the stabilized D/q2 derivation", "the complete twenty-export, seven-hash classical Gate A from the one accepted q2 hash", "a Hadamard state, causal perturbative AQFT construction, or Lorentzian quantum master equation", "continuum renormalized products from finite regulated-product closure", "a Weyl QME or Weyl residual transfer from a finite toy BRST complex", "equivalence of carrier categories from one finite realization", "a theorem ranking from interface order, Pareto membership, or neighbor counts", "composition beyond the two certified scoped cross-cell interfaces", "precision sampler equivalence, continuum reconstruction, or empirical support from the BT finite lattice", "a complete observationally validated theory"],
        "human_report": "foundations/reports/matrix-explorer-site-v2.md",
    }
    result["features"] = [item for item in result["features"] if not item.startswith("Gate V11 reconciliation")]
    result["features"].append("Gate V22 residual cyclic-carrier repair with one accepted common hash and M3RC/M4R/M1 remaining")
    result["features"].append("M3L content-addressed 386-to-30 local endpoint contraction across 10 artifacts, 17 canonical object hashes, 15 compatibility links, and zero projected defects")
    result["features"].append("M4L complete rank-386 local odd pairing with 410 ordered entries and zero q1/SDR/D/q2/q3 cyclicity defects")
    result["features"].append("M3R represented finite endpoint-to-residual comparison with 470 E/A/L magnetic names, exact crosswalk and zero retraction or q0-chain defects")
    result["features"].append("exact rank-zero obstruction to direct odd-pairing pullback on the 470 degree-zero residual modes, plus a canonical rank-940 shifted-cotangent preflight")
    result["features"].append("portable exact residual zero-mode payload with 15 primal and 15 dual modes, 120 SO(4,2) coefficients, 15 representation matrices, and zero replay defects")
    result["features"].append("portable centered C3/C4/C5 payload with 12343 ordered basis elements, 85091 reconstructed differential coefficients, exact H4 dimension two, and normalized chiral vectors")
    result["features"].append("exact carrier-type audit separating the support-local 386-to-30 endpoint SDR, 4490-to-470 finite harmonic residual SDR, and 30-coordinate conformal-Killing cotangent payload")
    result["features"].append("support-expansion obstruction preventing global harmonic and zero-mode projectors from being mislabeled support-local Green-transfer maps")
    result["features"].append("exact 386-row candidate q3 stabilization with 16 ternary block channels and strict authority firewall")
    result["features"].append("exact source-versus-candidate auxiliary cubic witness refuting literal and linear-shear theory identity")
    result["features"].append("exact first nonlinear auxiliary-elimination component closing the f-hat-v-v channel with full BV pullback still open")
    result["features"].append("seven-family exact shifted-cubic inventory with a 22+16 coefficient canonical vv BV lift")
    result["features"].append("complete curved quadratic auxiliary canonical lift with 1392 hh, 76 hv, 22 vv and 3907 cotangent coefficients")
    result["features"].append("three exact auxiliary Diff BV lifts with 264 master-density, 336 field, 632 antifield and 704 c-star coefficients")
    result["features"].append("append-only canonical c-star V2 repair reducing 336 exact q1/q2 defects to zero")
    result["features"].append("accepted 386-row common source-q2 snapshot with 22 minimal operations, 2064 auxiliary coefficients, and zero q1/q2, cyclicity, and D/q2 defects")
    result["features"].append("authoritative common source-q3 snapshot with two exhaustive families, 5952 auxiliary coefficients, and zero arity-three, cyclicity, and D/q3 defects")
    result["does_not_establish"] = [
        item for item in result["does_not_establish"]
        if "metric-dependent auxiliary q3" not in item
        and "386-row cyclic q3 stabilization" not in item
        and "complete twenty-export, seven-hash classical Gate A from the one accepted q2 hash" not in item
    ]
    result["does_not_establish"].append("support-locality or all-energy smooth completion of the represented finite M3R harmonic comparison")
    result["claim_flags"]["strict_M3R_represented_dfinite_comparison_exposed"] = True
    result["claim_flags"]["strict_M4R_residual_cyclicity_exposed"] = False
    result["claim_flags"]["strict_current_470_induced_odd_pairing_rank_zero_exposed"] = True
    result["claim_flags"]["strict_finite_940_cotangent_preflight_exposed"] = True
    result["claim_flags"]["strict_M3RC_dual_comparison_maps_exposed"] = False
    result["does_not_establish"].extend([
        "the complete twenty-export, seven-hash classical Gate A from the linked source-q2/q3 snapshots and the unbound residual and centered payloads",
        "a common-snapshot zero-mode hash from the portable residual coefficient package",
        "a common-snapshot representative hash from the portable centered coefficient package",
        "H3 or H5 cohomology from the adjacent centered C3 and C5 carrier bases",
        "M3RC dual comparison maps, the induced residual pairing/cyclicity M4R, or the final all-object freeze M1",
        "q2/q3 compatibility with an advanced or retarded Green homotopy",
    ])
    result["does_not_establish"].extend([
        "that the exact stabilized-q3 candidate is the authoritative nonminimal pure-Weyl BV interaction",
        "general lambda-squared causal source closure from the candidate q3 stabilization",
    ])
    result["claim_flags"]["completion_atlas_exposed"] = True
    result["claim_flags"]["strict_residual_zero_mode_payload_exposed"] = True
    result["claim_flags"]["strict_residual_zero_mode_common_freeze_exposed"] = False
    result["claim_flags"]["strict_centered_cohomology_payload_exposed"] = True
    result["claim_flags"]["strict_centered_representative_common_freeze_exposed"] = False
    result["claim_flags"]["strict_residual_sdr_type_audit_exposed"] = True
    result["claim_flags"]["strict_graph_endpoint_sdr_support_local_exposed"] = True
    result["claim_flags"]["strict_dfinite_residual_projector_support_local_exposed"] = False
    result["claim_flags"]["strict_m3_typed_split_exposed"] = True
    result["claim_flags"]["strict_m3l_common_endpoint_sdr_binding_exposed"] = True
    result["claim_flags"]["strict_m3r_typed_residual_comparison_exposed"] = True
    result["claim_flags"]["strict_m4l_local_graph_cyclic_pairing_exposed"] = True
    result["claim_flags"]["strict_m4r_typed_residual_cyclicity_exposed"] = False
    result["claim_flags"]["strict_q2_only_lambda2_source_obstruction_exposed"] = True
    result["claim_flags"]["strict_authoritative_q3_cancellation_target_exposed"] = True
    result["claim_flags"]["strict_authoritative_minimal_q3_imported"] = True
    result["claim_flags"]["strict_minimal_arity_three_identity_exposed"] = True
    result["claim_flags"]["strict_minimal_q3_cyclicity_exposed"] = True
    result["claim_flags"]["strict_386_candidate_q3_stabilized"] = True
    result["claim_flags"]["strict_386_candidate_arity_three_identity_exposed"] = True
    result["claim_flags"]["strict_386_candidate_q3_cyclicity_exposed"] = True
    result["claim_flags"]["strict_386_candidate_D_q3_derivation_exposed"] = True
    result["claim_flags"]["strict_386_authoritative_full_q3_imported"] = True
    result["claim_flags"]["strict_386_full_arity_three_identity_exposed"] = True
    result["claim_flags"]["strict_386_full_q3_cyclicity_exposed"] = True
    result["claim_flags"]["strict_386_full_D_q3_derivation_exposed"] = True
    result["claim_flags"]["strict_386_literal_trivial_stabilization_identity_refuted"] = True
    result["claim_flags"]["strict_386_linear_shear_theory_identity_refuted"] = True
    result["claim_flags"]["strict_386_candidate_internal_identities_preserved"] = True
    result["claim_flags"]["strict_386_nonlinear_equivalence_may_exist"] = True
    result["claim_flags"]["strict_386_nonlinear_equivalence_constructed"] = False
    result["claim_flags"]["strict_386_nonlinear_equivalence_obstructed"] = False
    result["claim_flags"]["strict_386_q3_stabilized"] = False
    result["claim_flags"]["strict_386_authoritative_nonminimal_equivalence_exposed"] = False
    result["claim_flags"]["strict_386_candidate_causal_lambda2_source_closure_exposed"] = False
    result["claim_flags"]["strict_authoritative_q3_imported"] = True
    result["claim_flags"]["strict_full_weyl_lambda2_source_closure_exposed"] = False
    result["claim_flags"]["strict_pure_weyl_q3_witness_cancellation_exposed"] = True
    result["claim_flags"]["strict_lambda2_witness_full_source_closure_exposed"] = True
    result["claim_flags"]["strict_Berger_q3_direct_import_compatible"] = False
    result["claim_flags"]["strict_386_first_nonlinear_equivalence_component_constructed"] = True
    result["claim_flags"]["strict_386_f_hat_v_v_pullback_channel_closed"] = True
    result["claim_flags"]["strict_386_known_required_cubic_families_enumerated"] = True
    result["claim_flags"]["strict_386_vv_bv_cotangent_lift_canonical"] = True
    result["claim_flags"]["strict_386_exhaustive_full_nonlinear_bv_family_census"] = True
    result["claim_flags"]["strict_nonlinear_weyl_boost_ghost_manifest_complete"] = True
    result["claim_flags"]["strict_386_full_source_q2_assembled"] = True
    result["claim_flags"]["strict_386_hh_hv_bv_cotangent_lift_component_complete"] = True
    result["claim_flags"]["strict_386_full_bv_cotangent_lift_serialized"] = True
    result["claim_flags"]["strict_386_full_quadratic_bv_cotangent_lift_serialized"] = True
    result["claim_flags"]["strict_386_diff_bv_representation_component_complete"] = True
    result["claim_flags"]["strict_386_seven_known_required_cubic_families_component_complete"] = True
    result["claim_flags"]["strict_386_diff_cstar_v2_repair_exposed"] = True
    result["claim_flags"]["strict_386_source_q2_common_hash_accepted"] = True
    result["claim_flags"]["strict_386_full_q1_q2_identity_exposed"] = True
    result["claim_flags"]["strict_386_full_q2_cyclicity_exposed"] = True
    result["claim_flags"]["strict_386_full_D_q2_derivation_exposed"] = True
    result["claim_flags"]["strict_authoritative_full_carrier_q2_exposed"] = True
    result["claim_flags"]["strict_full_carrier_q2_exposed"] = True
    result["claim_flags"]["strict_386_full_source_q2_pullback_replayed"] = True
    result["claim_flags"]["strict_386_full_source_q3_pullback_replayed"] = True
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
