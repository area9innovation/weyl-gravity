#!/usr/bin/env python3
"""Certify the first input obstruction to a canonical 108-row PBW replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_PBW_INPUT_OBSTRUCTION.json"
SCHEMA = PACKAGE / "schema/berger-108-row-pbw-input-obstruction-v1.schema.json"
REPORT = PACKAGE / "reports/berger-108-row-pbw-input-obstruction.md"

DEPENDENCIES = {
    "master_identity": PACKAGE / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json",
    "apparatus_q2_q3": PACKAGE / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "apparatus_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "emitter_unary": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "base_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "base_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
}
LATER_INPUTS = {
    "detector_smearings": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "emitter_switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_108_row_pbw_input_obstruction.py",
    "tests": PACKAGE / "tests/test_berger_108_row_pbw_input_obstruction.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "master_identity": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED",
        "apparatus_q2_q3": "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "apparatus_handoff": "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE",
        "emitter_unary": "108_ROW_Q1_CERTIFIED",
        "base_q2": "CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"required dependency flag dropped: {name}.{flag}")
    base = values["base_q2"]
    expected = base["classical_binary_q2"]["payload_file_sha256"]
    compact = json.dumps(values["base_q2_payload"], sort_keys=True, separators=(",", ":")) + "\n"
    observed = hashlib.sha256(compact.encode()).hexdigest()
    if observed != expected:
        raise AssertionError("pinned 64-row payload hash drifted")
    return values


def profile_nondetermination_audit(*, identify_widths: bool = False) -> dict[str, Any]:
    """Two normalized radial bump widths satisfy the frozen prose contract."""

    epsilon = sp.symbols("epsilon", positive=True)
    narrow = epsilon if identify_widths else epsilon / 2
    # A normalized radial three-coordinate bump has centre value C/epsilon^3.
    wide_value = epsilon ** -3
    narrow_value = narrow ** -3
    ratio = sp.simplify(narrow_value / wide_value)
    distinct = sp.simplify(ratio - 1) != 0
    return {
        "common_contract": "smooth nonnegative compact radial detector bump with unit rod-coordinate integral",
        "realization_A_width": "epsilon",
        "realization_B_width": "epsilon" if identify_widths else "epsilon/2",
        "both_admissible_if": "0<epsilon<r_chart (then 0<epsilon/2<r_chart)",
        "normalized_centre_value_ratio_B_over_A": sp.sstr(ratio),
        "readout_q2_coefficient_differs": distinct,
        "dependency_closure_declares_width_or_profile_formula": False,
    }


def switch_nondetermination_audit(*, identify_radii: bool = False) -> dict[str, Any]:
    """Two unit-integral flat switches satisfy the frozen emitter handoff."""

    radius = sp.symbols("r", positive=True)
    narrow = radius if identify_radii else radius / 2
    # For h_r(theta)=B((theta-c)/r)/(r C_B), h_r(c)=1/(r C_B).
    wide_value = radius ** -1
    narrow_value = narrow ** -1
    ratio = sp.simplify(narrow_value / wide_value)
    distinct = sp.simplify(ratio - 1) != 0
    return {
        "common_contract": "fixed smooth nonnegative compact relational switch of the dynamical clock",
        "realization_A_radius": "r",
        "realization_B_radius": "r" if identify_radii else "r/2",
        "unit_integral_centre_value_ratio_B_over_A": sp.sstr(ratio),
        "emitter_q2_clock_and_interaction_coefficients_differ": distinct,
        "dependency_closure_declares_switch_formula": False,
    }


def component_interface_audit(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    base = values["base_q2"]
    apparatus = values["apparatus_q2_q3"]["apparatus_action_jets"]
    unary = values["emitter_unary"]["q1_new_blocks"]
    base_payload = values["base_q2_payload"]
    return {
        "pinned_base": {
            "shape": base_payload["shape"],
            "coefficient_field": base_payload["coefficient_field"],
            "pbw_basis": base_payload["pbw_basis"],
            "payload_file_sha256": base["classical_binary_q2"]["payload_file_sha256"],
            "canonical_scalar_terms_available": True,
        },
        "apparatus_extension": {
            "carrier_support": apparatus["carrier_support"],
            "representation": "covariant Frechet-derivative formula strings",
            "scalar_component_rows": False,
            "coefficient_atom_grammar": False,
            "positive_order_profile_jet_serialization": False,
        },
        "emitter_unary_extension": {
            "new_nonzero_block_count": len(unary["new_nonzero_operator_blocks"]),
            "representation": "source/target row ranges plus covariant operator strings",
            "complete_108_by_108_scalar_PBW_matrix": False,
        },
        "required_for_independent_replay": [
            "canonical 108-row scalar component basis and odd-pairing normalization",
            "differential coefficient algebra for f_a, rho_a, J_a, h_b and all requested Berger-frame jets",
            "complete scalar PBW q1 matrix on 108 rows",
            "complete sparse scalar PBW q2 tensor including apparatus and emitter reciprocal cyclic orbits",
        ],
        "component_coefficient_replay_callable_from_dependency_closure": False,
    }


def build() -> dict[str, Any]:
    values = _load()
    profile = profile_nondetermination_audit()
    switch = switch_nondetermination_audit()
    if not profile["readout_q2_coefficient_differs"] or not switch["emitter_q2_clock_and_interaction_coefficients_differ"]:
        raise AssertionError("non-uniqueness witness collapsed")
    profile_mutation = profile_nondetermination_audit(identify_widths=True)
    switch_mutation = switch_nondetermination_audit(identify_radii=True)
    if profile_mutation["readout_q2_coefficient_differs"] or switch_mutation["emitter_q2_clock_and_interaction_coefficients_differ"]:
        raise AssertionError("identity mutation was not detected")
    interface = component_interface_audit(values)
    boundary = (
        "This exact LOCAL-ALGEBRAIC interface audit preserves the certified covariant 108-row q1-q2 master identity "
        "and the pinned scalar 64-row gravity-clock-Maxwell PBW payload, but proves that their certified dependency "
        "closure does not determine a canonical scalar 108-row PBW payload.  The apparatus q2/q3 artifact stores "
        "Frechet-derivative formula strings rather than component rows or a differential coefficient grammar, and "
        "the emitter unary stores covariant block ranges rather than a complete scalar PBW matrix.  More decisively, "
        "two normalized detector bumps of widths epsilon and epsilon/2 satisfy the frozen apparatus profile contract "
        "but change the centre readout coefficient by a factor eight; two unit-integral flat switches of radii r and "
        "r/2 satisfy the frozen emitter handoff but change the centre interaction coefficient by a factor two.  Later "
        "exact detector/switch certificates exist, but they are not dependencies of the q1-q2 theorem and still need "
        "an explicit coefficient-jet/component serializer before a PBW replay.  Therefore the PBW map is fail-closed "
        "as NO_CERTIFIED_MAP.  No component coefficient is inferred from row coverage, and no q3/q4, physical recoil, "
        "backreacted branch, tangent-cone, Bridge 3, finite-parameter, Lorentzian quantum, or quantum claim is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-pbw-input-obstruction-v1",
        "result_id": "BERGER_108_ROW_PBW_INPUT_OBSTRUCTION",
        "setting_id": values["master_identity"]["setting_id"],
        "claim_status": "OBSTRUCTED_CERTIFIED_DEPENDENCY_CLOSURE_DOES_NOT_DETERMINE_COMPONENT_PBW_PAYLOAD",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name].get("result_id", "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD"), "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "pinned_base_and_interface_audit": interface,
        "nonuniqueness_witnesses": {"detector_profile": profile, "emitter_switch": switch},
        "later_inputs_not_in_certified_dependency_closure": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": json.loads(path.read_text())["result_id"], "sha256": _sha256(path), "disposition": "available input to a future serializer; not retroactively imported"}
            for name, path in LATER_INPUTS.items()
        },
        "minimal_activation_contract": {
            "imports": ["exact detector smearings", "exact normalized emitter switches", "pinned 64-row PBW payload"],
            "new_machine_readable_objects": [
                "108-row scalar component/cotangent basis crosswalk",
                "closed differential coefficient-jet grammar with canonical normal form and equality",
                "complete 108-row scalar PBW q1 payload",
                "action-derived apparatus/emitter q2 component expander with cyclic reciprocal outputs",
            ],
            "acceptance": "independent coefficientwise q1 q2 replay plus profile-width, switch-radius, reciprocal-orbit and base-hash mutations",
        },
        "mutation_results": [
            {"name": "identify_detector_profile_widths", "detected": not profile_mutation["readout_q2_coefficient_differs"], "mutated_ratio": profile_mutation["normalized_centre_value_ratio_B_over_A"]},
            {"name": "identify_emitter_switch_radii", "detected": not switch_mutation["emitter_q2_clock_and_interaction_coefficients_differ"], "mutated_ratio": switch_mutation["unit_integral_centre_value_ratio_B_over_A"]},
        ],
        "flags": {
            "PINNED_64_ROW_PBW_PAYLOAD_VERIFIED": True,
            "COVARIANT_108_ROW_Q1_Q2_IDENTITY_PRESERVED": True,
            "DEPENDENCY_CLOSURE_PBW_NONUNIQUENESS_CERTIFIED": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "FULL_NONLINEAR_EMITTER_BACKREACTION_INCLUDED": False,
            "QUANTUM_CLAIM": False,
        },
        "atlas_status": "NO_CERTIFIED_MAP",
        "next_gate": "DECLARE_108_ROW_COMPONENT_AND_DIFFERENTIAL_COEFFICIENT_JET_CONTRACT_THEN_EXPORT_Q1_AND_Q2_PBW_PAYLOADS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 108-row PBW input obstruction certificate")
    print("BERGER_108_ROW_PBW_INPUT_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
