#!/usr/bin/env python3
"""Freeze the fail-closed Berger apparatus Z2 receiver disposition.

The two detector-selected preparation directions exist, but the committed
same-background inputs do not yet place them and the material apparatus in
one K_Berger-equivariant q1/q2 carrier.  This module therefore exports the
strict receiver contract required by the classical work item.  It does not
invent a compact-product carrier or manufacture obstruction polynomials from
the leading detector rank.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
OUTPUT = ROOT / (
    "d_quotient_classical/certificates/"
    "BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1.json"
)
REPORT = ROOT / (
    "d_quotient_classical/reports/"
    "berger-apparatus-z2-integrability-receiver-disposition-v1.md"
)
SCHEMA = ROOT / (
    "d_quotient_classical/schema/"
    "berger-apparatus-z2-integrability-receiver-disposition-v1.schema.json"
)
VERIFIER = HERE / "verify_berger_apparatus_z2_integrability_receiver_disposition.py"
TESTS = (
    HERE
    / "tests/test_berger_apparatus_z2_integrability_receiver_disposition.py"
)

DEPENDENCIES = {
    "apparatus_parent": ROOT
    / "closed_universe_observers/certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "apparatus_parent_payload": ROOT
    / "closed_universe_observers/certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "component_and_pairing_contract": ROOT
    / "closed_universe_observers/certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary_candidate": ROOT
    / "closed_universe_observers/certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_q2_candidate": ROOT
    / "closed_universe_observers/certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "arity_two_obstruction": ROOT
    / "closed_universe_observers/certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json",
    "apparatus_K_gate": ROOT
    / "closed_universe_observers/certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "detector_selected_preparations": ROOT
    / (
        "closed_universe_observers/certificates/"
        "BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json"
    ),
    "combined_q1_contract": ROOT
    / (
        "closed_universe_observers/certificates/"
        "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT.json"
    ),
    "combined_q1_crosswalk_obstruction": ROOT
    / (
        "closed_universe_observers/certificates/"
        "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION.json"
    ),
    "same_background_receiver_contract": ROOT
    / (
        "closed_universe_observers/certificates/"
        "BERGER_APPARATUS_SAME_BACKGROUND_Z2_RECEIVER_CONTRACT.json"
    ),
}

EXPECTED_REQUIRED_OBJECTS = {
    "Noether_reduction",
    "Z2_ideal",
    "carrier_crosswalk",
    "correction_class_operators",
    "finite_output_closure",
    "memory_transport",
    "quadratic_source",
    "resonant_receiver",
    "response_restriction",
    "stabilizer_receiver",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", ""))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _check_inputs(records: dict[str, dict]) -> None:
    if (
        records["apparatus_parent"].get("claim_status")
        != "CERTIFIED_ACTION_DERIVED_DYNAMICAL_APPARATUS_PARENT_THROUGH_ARITY_TWO"
    ):
        raise ValueError("apparatus parent drifted")
    if (
        records["component_and_pairing_contract"]
        .get("flags", {})
        .get("NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED")
        is not True
    ):
        raise ValueError("108-row pairing contract drifted")
    if (
        records["completed_unary_candidate"]
        .get("flags", {})
        .get("COMPLETE_FIRST_BIDEGREE_UNARY_GATE")
        is not True
    ):
        raise ValueError("completed unary candidate drifted")
    if (
        records["complete_q2_candidate"]
        .get("flags", {})
        .get("COMPLETE_SCALAR_108_ROW_Q2_EXPORTED")
        is not True
    ):
        raise ValueError("q2 candidate disappeared")
    if (
        records["complete_q2_candidate"]
        .get("activation_disposition", {})
        .get("arity_replay_certified")
        is not False
    ):
        raise ValueError("q2 candidate lifecycle changed")
    if (
        records["arity_two_obstruction"]
        .get("flags", {})
        .get("COMPLETE_108_ROW_ARITY_TWO_OBSTRUCTED")
        is not True
    ):
        raise ValueError("108-row arity-two obstruction drifted")
    if (
        records["apparatus_K_gate"]
        .get("flags", {})
        .get("K_BERGER_BACKGROUND_PRESERVING_ON_APPARATUS")
        is not False
    ):
        raise ValueError("apparatus K gate changed")
    if (
        records["detector_selected_preparations"]
        .get("flags", {})
        .get("COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED")
        is not True
    ):
        raise ValueError("detector-selected preparations drifted")
    if records["combined_q1_contract"].get("status") != "REQUIRED_NOT_YET_INSTANTIATED":
        raise ValueError("combined-q1 contract changed")
    combined_obstruction = records["combined_q1_crosswalk_obstruction"]
    if (
        combined_obstruction.get("claim_status")
        != "OBSTRUCTED_NO_BACKGROUND_PRESERVING_LINEAR_K_ON_DECLARED_COMBINED_CARRIER"
    ):
        raise ValueError("combined-q1 crosswalk obstruction drifted")
    exact = combined_obstruction.get("exact_obstruction", {})
    rods = exact.get("global_rod_closure", {})
    mixing = exact.get(
        "parent_material_rows_cannot_supply_missing_directions", {}
    )
    if (
        exact.get("base_background_preserving") is not False
        or rods.get("current_real_rod_span_rank") != 6
        or rods.get("time_translation_closure_rank") != 8
        or rods.get("minimal_additional_real_rod_directions") != 2
        or mixing.get("constant_mixing_nullity") != 0
    ):
        raise ValueError("combined-q1 exact obstruction census drifted")
    receiver = records["same_background_receiver_contract"]
    if receiver.get("status") != "REQUIRED_NOT_YET_INSTANTIATED":
        raise ValueError("same-background receiver contract changed")
    if set(receiver.get("required_exact_objects", {})) != EXPECTED_REQUIRED_OBJECTS:
        raise ValueError("same-background receiver interface drifted")
    if receiver.get("input_span", {}).get("required_quadratic_pairs") != [
        "(u_0,u_0)",
        "(u_0,u_1)",
        "(u_1,u_1)",
    ]:
        raise ValueError("symmetric preparation-pair contract drifted")


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _check_inputs(records)
    source_manifest = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-apparatus-z2-integrability-receiver-disposition-v1",
        "result_id": "BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1",
        "result_state": "STRICT_RECEIVER_CONTRACT_EXPORTED_COMBINED_LINEAR_K_CROSSWALK_OBSTRUCTED",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], records[name])
            for name in DEPENDENCIES
        },
        "available_same_background_inputs": {
            "action_derived_56_row_apparatus_parent": "CERTIFIED",
            "detector_selected_preparation_u0": "CERTIFIED",
            "detector_selected_preparation_u1": "CERTIFIED",
            "leading_two_record_response_rank": 2,
            "108_row_component_basis_and_odd_pairing": "CERTIFIED",
            "108_row_unary_first_bidegree_candidate": "CERTIFIED_IN_ITS_DECLARED_BACKGROUND_QUOTIENT",
            "108_row_q2_tensor": "EXPORTED_BUT_NOT_AN_ARITY_TWO_CODERIVATION",
            "84_row_affine_K_through_arity_two": "CERTIFIED_IN_ITS_DECLARED_SCOPE",
        },
        "ordered_gate_disposition": [
            {
                "gate": 1,
                "object": "combined_q1_pairing_real_K_carrier",
                "status": "OBSTRUCTED",
                "reason": (
                    "The declared constant typed-identification class has no "
                    "background-preserving linear K_Berger crosswalk: the "
                    "six global rods have time-translation closure rank "
                    "eight, and the material first-order rows have zero "
                    "constant mixing nullity into the missing directions."
                ),
            },
            {
                "gate": 2,
                "object": "combined_action_quadratic_euler_source",
                "status": "MISSING",
                "reason": (
                    "D2E[u_i,u_j] is undefined until gate 1 fixes one "
                    "combined action carrier; independently, the exported "
                    "108-row q2 candidate has a certified q1-q2 obstruction."
                ),
            },
            {
                "gate": 3,
                "object": "complete_stabilizer_and_resonant_adjoint_cokernel",
                "status": "MISSING",
                "reason": (
                    "Noether reduction, correction-class domains and the "
                    "combined unary operator required to form the adjoint "
                    "cokernel are absent."
                ),
            },
            {
                "gate": 4,
                "object": "Z2_Berger_equations_and_response_restriction",
                "status": "NO_CERTIFIED_MAP",
                "reason": "The source and receiver gates 1-3 are prerequisites.",
            },
        ],
        "first_missing_operator": {
            "name": "combined_q1_pairing_real_K_carrier",
            "kind": "same-background unary BV operator and row-level crosswalk",
            "status": "OBSTRUCTED_IN_DECLARED_LINEAR_K_IDENTIFICATION_CLASS",
            "required_rows": (
                "gravity-clock-Maxwell plus the action-derived material "
                "apparatus, with u0/u1 and detector-record chain maps"
            ),
            "required_identities": [
                "q1^2=0",
                "q1 odd cyclicity",
                "[K_Berger,q1]=0",
                "real-structure commutation",
                "preparation and detector maps are q1 chain maps",
            ],
            "why_first": (
                "The quadratic Euler source and every adjoint-cokernel "
                "projection depend on the domain, codomain, pairing and "
                "background stabilizer fixed by this operator."
            ),
        },
        "combined_q1_crosswalk_obstruction": {
            "status": "OBSTRUCTED",
            "scope": (
                "constant row identifications and pairing-preserving constant "
                "linear mixing that preserve the typed principal-symbol category"
            ),
            "current_global_rod_span_rank": 6,
            "time_translation_closure_rank": 8,
            "minimal_additional_global_rod_directions": 2,
            "material_to_global_constant_mixing_nullity": 0,
            "prospective_repaired_base_rows": 112,
            "prospective_identified_union_rows": 160,
            "minimal_repair": (
                "add two global scalar degree-zero rods and two cyclic "
                "cotangents, then recompute the background, stress, Phi2, "
                "unary, pairing and quotient before retrying the union"
            ),
            "global_no_go": False,
        },
        "independent_interaction_blocker": {
            "status": "OBSTRUCTED",
            "artifact_id": "BERGER_108_ROW_ARITY_TWO_OBSTRUCTION",
            "identity": "q1 q2 + q2(q1,-) + (-1)^|x| q2(-,q1)=0",
            "first_witness": (
                "tau_star on e0 e1 A_0 and undifferentiated K0_01 "
                "has coefficient +g0 h0"
            ),
            "consequence": (
                "The available 108-row q2 export cannot be used as the "
                "certified quadratic Euler source of a Z2 theorem."
            ),
        },
        "strict_receiver_contract": {
            "background": (
                "the same pinned positive Berger gravity-clock-Maxwell-"
                "apparatus background"
            ),
            "input_ring": "exact polynomial ring Q[a_0,a_1] over the declared Berger coefficient field",
            "general_preparation": "u=a_0*u_0+a_1*u_1",
            "quadratic_pairs": [
                "(u_0,u_0)",
                "(u_0,u_1)",
                "(u_1,u_1)",
            ],
            "required_objects": sorted(EXPECTED_REQUIRED_OBJECTS),
            "correction_classes": {
                "bounded_or_quasiperiodic": "NO_CERTIFIED_MAP",
                "smooth_secular": "NO_CERTIFIED_MAP",
                "causal_or_retarded": "NO_CERTIFIED_MAP",
            },
            "required_outputs": {
                "quadratic_source_map": "NO_CERTIFIED_MAP",
                "moment_map_Taub_polynomials": "NO_CERTIFIED_MAP",
                "nonzero_shell_resonant_pairings": "NO_CERTIFIED_MAP",
                "Z2_Berger_ideal": "NO_CERTIFIED_MAP",
                "individual_preparation_membership": "NO_CERTIFIED_MAP",
                "finite_sum_membership": "NO_CERTIFIED_MAP",
                "restricted_response_rank_and_kernel": "NO_CERTIFIED_MAP",
                "persistent_memory_transport": "NO_CERTIFIED_MAP",
            },
            "forbidden_substitutions": [
                "compact-product modes matched to Berger rows by labels",
                "leading detector rank called second-order survival",
                "global-rod quadratic source called the u0/u1 source",
                "formal secular inverse called bounded",
                "stabilizer charges omitted from the adjoint cokernel",
            ],
        },
        "mutation_results": {
            "charge_gate_omitted": "REJECTED",
            "resonance_gate_falsely_completed": "REJECTED",
            "background_relabelled_compact_product": "REJECTED",
            "mixed_pair_u0_u1_deleted": "REJECTED",
            "q2_candidate_promoted_despite_arity_obstruction": "REJECTED",
        },
        "downstream_disposition": {
            "Z2_Berger": "NO_CERTIFIED_MAP",
            "nonlinear_detector_rank": "NO_CERTIFIED_MAP",
            "relational_memory": "NO_CERTIFIED_MAP",
            "redshift": "NO_CERTIFIED_MAP",
            "q3": "NO_CERTIFIED_MAP",
            "particle": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "flags": {
            "STRICT_RECEIVER_CONTRACT_EXPORTED": True,
            "DECLARED_COMBINED_LINEAR_K_CROSSWALK_OBSTRUCTED": True,
            "COMBINED_Q1_CARRIER_CERTIFIED": False,
            "QUADRATIC_SOURCE_CERTIFIED": False,
            "COMPLETE_ADJOINT_COKERNEL_CERTIFIED": False,
            "Z2_BERGER_CERTIFIED": False,
            "NONLINEAR_RANK_TWO_CERTIFIED": False,
            "COMPACT_PRODUCT_MODE_IMPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "ADD_TWO_GLOBAL_RODS_AND_TWO_COTANGENTS_RECOMPUTE_THE_112_ROW_"
            "BASE_THEN_RETRY_THE_160_ROW_IDENTIFIED_UNION"
        ),
        "provenance": {
            "source_manifest": source_manifest,
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.backreacted_clock.berger_apparatus_z2_integrability_receiver_disposition --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.backreacted_clock.verify_berger_apparatus_z2_integrability_receiver_disposition",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_apparatus_z2_integrability_receiver_disposition",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-apparatus-z2-integrability-receiver-disposition-v1.schema.json -d d_quotient_classical/certificates/BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact fail-closed disposition imports the committed "
            "same-background apparatus parent, detector-selected preparations, "
            "component/pairing interface, unary and q2 candidates, affine "
            "K gate, arity-two obstruction and receiver contracts by content "
            "hash. It identifies the first blocked operator, imports the "
            "exact no-crosswalk result for the declared constant typed linear "
            "K identification class, and exports the strict interface required "
            "for a future Berger Z2 receiver. It does not prove that no "
            "combined carrier exists outside that class, compute a "
            "quadratic source, form an adjoint cokernel, classify any "
            "preparation as extendible or obstructed, promote leading rank "
            "two, import compact-product modes, or establish q3, memory, "
            "redshift, particle, stability or quantum claims."
        ),
    }


def validate(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["atlas_status"] != "NO_CERTIFIED_MAP":
        raise ValueError("atlas status overpromoted")
    if value["first_missing_operator"]["status"] != (
        "OBSTRUCTED_IN_DECLARED_LINEAR_K_IDENTIFICATION_CLASS"
    ):
        raise ValueError("first missing operator boundary crossed")
    if value["combined_q1_crosswalk_obstruction"]["global_no_go"] is not False:
        raise ValueError("scoped crosswalk obstruction was globalized")
    if value["strict_receiver_contract"]["quadratic_pairs"] != [
        "(u_0,u_0)",
        "(u_0,u_1)",
        "(u_1,u_1)",
    ]:
        raise ValueError("quadratic pair coverage changed")
    if any(
        status != "NO_CERTIFIED_MAP"
        for status in value["strict_receiver_contract"]["required_outputs"].values()
    ):
        raise ValueError("receiver output overpromoted")
    if any(
        value["flags"][name]
        for name in (
            "COMBINED_Q1_CARRIER_CERTIFIED",
            "QUADRATIC_SOURCE_CERTIFIED",
            "COMPLETE_ADJOINT_COKERNEL_CERTIFIED",
            "Z2_BERGER_CERTIFIED",
            "NONLINEAR_RANK_TWO_CERTIFIED",
            "COMPACT_PRODUCT_MODE_IMPORTED",
            "QUANTUM_CLAIM",
        )
    ):
        raise ValueError("claim boundary crossed")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Berger apparatus Z2 integrability receiver disposition

## Result

The two detector-selected preparations and their leading rank-two response
are certified.  The declared constant typed-identification class cannot
place those preparations, the 56-row material apparatus and the
gravity--clock--Maxwell rows in one background-preserving linear
\(K_{\\rm Berger}\)-equivariant unary BV complex.  The six global rods have
time-translation closure rank eight, while constant mixing from the
first-order material rows has zero nullity.  That combined row-level \(q_1\),
pairing, real structure and chain crosswalk is the first blocked operator.

The exact minimal repair within the diagnosed architecture is two additional
global scalar rods and two cyclic cotangents.  It requires recomputation of
the co-rotating background, stress, \(\Phi_2\), 112-row unary complex and
quotient before the prospective 160-row identified union can be retried.

This is upstream of the requested quadratic source.  Moreover, the available
108-row \(q_2\) tensor is explicitly not a certified coderivation: its
arity-two replay has a nonzero temporal Ward witness.  It therefore cannot be
silently reused as \(D^2E[u_i,u_j]\).

## Strict receiver contract

A future receiver must work on the same pinned Berger background and evaluate
all three symmetric pairs

\[
(u_0,u_0),\\qquad (u_0,u_1),\\qquad (u_1,u_1).
\]

It must export the complete output closure, Noether reduction, stabilizer
moment-map/Taub rows, complementary nonzero-shell adjoint cokernel and exact
pairings.  Bounded/quasiperiodic, smooth secular and causal/retarded
correction classes remain separate.  Only then may the resulting ideal be
called \(\mathcal Z_2^{\\rm Berger}\), and only then may the two-record response
be restricted and its rank recomputed.

Every requested receiver output is therefore `NO_CERTIFIED_MAP`.  This is a
scoped obstruction in the declared constant typed linear-\(K\) class, not a
global nonexistence theorem for a repaired or affine combined carrier.  No
compact-product mode is imported and no nonlinear response,
memory, redshift, q3, particle, stability or quantum claim follows.

EVIDENCE: `d_quotient_classical/certificates/BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1.json`
"""


def _guards(value: dict) -> None:
    mutations = []
    charge = deepcopy(value)
    charge["strict_receiver_contract"]["required_outputs"][
        "moment_map_Taub_polynomials"
    ] = "CERTIFIED"
    mutations.append(charge)
    resonance = deepcopy(value)
    resonance["strict_receiver_contract"]["required_outputs"][
        "nonzero_shell_resonant_pairings"
    ] = "CERTIFIED"
    mutations.append(resonance)
    background = deepcopy(value)
    background["strict_receiver_contract"]["background"] = (
        "compact product relabelled as Berger"
    )
    mutations.append(background)
    mixed = deepcopy(value)
    mixed["strict_receiver_contract"]["quadratic_pairs"].remove("(u_0,u_1)")
    mutations.append(mixed)
    q2 = deepcopy(value)
    q2["flags"]["QUADRATIC_SOURCE_CERTIFIED"] = True
    mutations.append(q2)
    for index, mutant in enumerate(mutations):
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation {index} was accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("Berger apparatus Z2 disposition drifted")
    if args.guards:
        _guards(value)
    print("BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1: PASS")


if __name__ == "__main__":
    main()
