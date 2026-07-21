#!/usr/bin/env python3
"""Classify the complete local action-Hessian repair orbit for replacement-112."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator

from closed_universe_observers import berger_replacement112_executable_unary_engine as engine


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO.json"
X = P / "certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-132-defect-minimal-nilpotent-repair-no-go-v1.schema.json"
REPORT = P / "reports/berger-replacement112-132-defect-minimal-nilpotent-repair-no-go.md"
DEPS = {
    "mixed_nilpotency": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION.json",
    "mixed_nilpotency_payload": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION_PAYLOAD.json",
    "mixed_hessian": P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE.json",
    "mixed_hessian_payload": P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD.json",
    "material_parent": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE.json",
    "material_parent_payload": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE_PAYLOAD.json",
    "pushout_nondefinition": P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION.json",
    "pushout_nondefinition_payload": P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION_PAYLOAD.json",
}
FIXTURE = {
    engine.SA: sp.Rational(3, 5),
    engine.CA: sp.Rational(4, 5),
    engine.SU: sp.Rational(5, 13),
    engine.CU: sp.Rational(12, 13),
}
EXPECTED_ACTION_BLOCKS = {"K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"}
EXPECTED_CONTROL_BLOCKS = {"Gamma_R", "Gamma_R_sharp"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def specialize(operator: engine.Operator) -> engine.Operator:
    result: engine.Operator = {}
    for key, polynomial in operator.items():
        value = {monomial: sp.cancel(coefficient.subs(FIXTURE)) for monomial, coefficient in polynomial.items()}
        value = {monomial: coefficient for monomial, coefficient in value.items() if coefficient != 0}
        if value:
            result[key] = value
    return result


def generated_block_partition(interface: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    action_blocks: list[str] = []
    control_blocks: list[str] = []
    for name, block in sorted(interface["operator_blocks"].items()):
        degrees = set()
        for entry in block["net_replacement_delta"]["entries"]:
            for term in entry["terms"]:
                degrees.add(
                    sum(
                        int(factor["kind"] == "parameter" and factor["name"] == "epsilon_R_squared")
                        for factor in term["coefficient_factors"]
                    )
                )
        if degrees == {1}:
            action_blocks.append(name)
        elif degrees == {0}:
            control_blocks.append(name)
        else:
            raise AssertionError(f"block {name} has mixed or unsupported epsilon_R_squared degrees: {sorted(degrees)}")
    if set(action_blocks) != EXPECTED_ACTION_BLOCKS or set(control_blocks) != EXPECTED_CONTROL_BLOCKS:
        raise AssertionError("mechanically generated action/control block partition drifted")
    return tuple(action_blocks), tuple(control_blocks)


def correction_orbit(interface: dict[str, Any], action_blocks: tuple[str, ...]) -> engine.Operator:
    graded: engine.GradedOperator = {}
    for name in action_blocks:
        engine._add_serialized_blocks(
            graded,
            [{"entries": interface["operator_blocks"][name]["net_replacement_delta"]["entries"]}],
            string_coefficients=True,
        )
    if set(graded) != {(1, 0)}:
        raise AssertionError("the generated correction orbit left epsilon_R_squared degree")
    return graded[(1, 0)]


def real_structure_defect_count(interface: dict[str, Any], action_blocks: tuple[str, ...]) -> int:
    local_symbols = {"sa": engine.SA, "ca": engine.CA, "su": engine.SU, "cu": engine.CU}
    defects = 0
    for name in action_blocks:
        for entry in interface["operator_blocks"][name]["net_replacement_delta"]["entries"]:
            for term in entry["terms"]:
                defects += int(sp.sympify(term["coefficient"], locals=local_symbols).has(sp.I))
    return defects


def parsed_inherited_defects(payload: dict[str, Any]) -> dict[tuple[int, int, tuple[int, ...], int], sp.Expr]:
    local_symbols = {"r10": engine.R10, "r58": engine.R58, "j": engine.J}
    local_symbols.update({str(symbol): symbol for symbol in engine.rods.X})
    return {
        (
            record["output_index"],
            record["input_index"],
            tuple(record["input_pbw_word"]),
            record["time_mode"],
        ): sp.sympify(record["coefficient"], locals=local_symbols)
        for record in payload["mixed_nilpotency_obstruction"]["defect_entries"]
    }


def equation_record(
    key: tuple[int, int, tuple[int, ...], int],
    monomial: tuple[int, ...],
    correction: sp.Expr,
    rhs: sp.Expr,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    output, input_, word, mode = key
    variable_names = ("x0", "x1", "x2", "x3", "r10", "r58", "j")
    return {
        "output_index": output,
        "output_row_id": rows[output]["row_id"],
        "input_index": input_,
        "input_row_id": rows[input_]["row_id"],
        "input_pbw_word": list(word),
        "time_mode": mode,
        "basis_monomial": {name: power for name, power in zip(variable_names, monomial)},
        "correction_coefficient": sp.sstr(correction),
        "right_hand_side": sp.sstr(rhs),
    }


def scalar_equations(
    inherited: dict[tuple[int, int, tuple[int, ...], int], sp.Expr],
    correction: dict[tuple[int, int, tuple[int, ...], int], sp.Expr],
    rows: list[dict[str, Any]],
) -> tuple[list[tuple[sp.Expr, sp.Expr]], dict[str, Any], dict[str, Any]]:
    variables = (*engine.rods.X, engine.R10, engine.R58, engine.J)
    equations: list[tuple[tuple[int, int, tuple[int, ...], int], tuple[int, ...], sp.Expr, sp.Expr]] = []
    for key in sorted(set(inherited) | set(correction)):
        target_terms = dict(sp.Poly(sp.expand(inherited.get(key, 0)), *variables, domain=sp.QQ).terms())
        correction_terms = dict(sp.Poly(sp.expand(correction.get(key, 0)), *variables, domain=sp.QQ).terms())
        for monomial in sorted(set(target_terms) | set(correction_terms), reverse=True):
            a = correction_terms.get(monomial, sp.S.Zero)
            b = -target_terms.get(monomial, sp.S.Zero)
            if a != 0 or b != 0:
                equations.append((key, monomial, a, b))
    correction_nonzero = next(item for item in equations if item[2] != 0)
    target_only = next(item for item in equations if item[2] == 0 and item[3] != 0)
    determinant = sp.expand(correction_nonzero[2] * target_only[3])
    if determinant == 0:
        raise AssertionError("canonical augmented-rank separator vanished")
    pairs = [(a, b) for _key, _monomial, a, b in equations]
    return (
        pairs,
        equation_record(*correction_nonzero, rows),
        equation_record(*target_only, rows),
    )


def k_invariance_defect_count(interface: dict[str, Any]) -> int:
    local_symbols = {"sa": engine.SA, "ca": engine.CA, "su": engine.SU, "cu": engine.CU}
    action = sp.Matrix(
        [[sp.sympify(value, locals=local_symbols) for value in row] for row in interface["K_Berger_interface"]["field_generator_A_over_nu"]]
    )
    hessian = sp.Matrix(
        [[sp.sympify(value, locals=local_symbols) for value in row] for row in interface["action_crosswalk"]["kinetic_matrix_H"]]
    )
    return sum(int(engine.reduce_expr(value) != 0) for value in action.T * hessian + hessian * action)


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for certificate_name, payload_name in (
        ("mixed_nilpotency", "mixed_nilpotency_payload"),
        ("mixed_hessian", "mixed_hessian_payload"),
        ("material_parent", "material_parent_payload"),
        ("pushout_nondefinition", "pushout_nondefinition_payload"),
    ):
        if sha(DEPS[payload_name]) != values[certificate_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{certificate_name} payload hash mismatch")

    obstruction_payload = values["mixed_nilpotency_payload"]
    interface = values["mixed_hessian_payload"]
    material = values["material_parent_payload"]
    action_blocks, control_blocks = generated_block_partition(interface)
    action_origin = interface["action_crosswalk"]["replacement_action"]
    if action_origin != "S_nonrod-S_R,I6+S_R,H":
        raise AssertionError("the generated Hessian blocks no longer share the certified single replacement action")
    rows = obstruction_payload["carrier"]["rows"]
    q1, assembly = engine.assemble()
    q00 = specialize(q1[(0, 0)])
    orbit = specialize(correction_orbit(interface, action_blocks))
    orbit_square = engine.add_operators(engine.compose(orbit, q00), engine.compose(q00, orbit))
    orbit_defects, orbit_summary = engine.background_quotient_defect(orbit_square, FIXTURE)
    inherited = parsed_inherited_defects(obstruction_payload)
    equations, correction_equation, target_only_equation = scalar_equations(inherited, orbit_defects, rows)

    raw_constraint_rows = []
    for index in range(1, len(action_blocks)):
        row = [-1] + [0] * (len(action_blocks) - 1)
        row[index] = 1
        raw_constraint_rows.append(row)
    raw_constraint = sp.Matrix(raw_constraint_rows)
    background_anchor = sp.cancel(sp.Rational(-5, 9) / engine.SA**2).subs(FIXTURE)
    coefficient_rank = int(any(a != 0 for a, _b in equations))
    augmented_rank = 2 if correction_equation["correction_coefficient"] != "0" and target_only_equation["right_hand_side"] != "0" else 0
    if (raw_constraint.rank(), len(raw_constraint.nullspace()), background_anchor, coefficient_rank, augmented_rank) != (3, 1, sp.Rational(-125, 81), 1, 2):
        raise AssertionError("complete ansatz or inconsistency ranks drifted")
    if k_invariance_defect_count(interface) != 0:
        raise AssertionError("the unique action orbit ceased to be K_Berger invariant")
    if real_structure_defect_count(interface, action_blocks) != 0:
        raise AssertionError("the mechanically generated action orbit ceased to be real")

    return {
        "schema": "closed-universe-berger-replacement112-132-defect-minimal-nilpotent-repair-no-go-payload-v1",
        "result_id": "BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO_PAYLOAD",
        "carrier": {
            "row_count": len(rows),
            "rows": rows,
            "pairing_rank": obstruction_payload["carrier"]["pairing_rank"],
            "material_parent_row_count": material["carrier"]["row_count"],
            "material_parent_pairing_rank": material["complete_internal_q1"]["pairing_rank"],
            "background": "same pinned positive Berger eight-rod background",
            "support_sector": interface["support_and_zero_modes"],
        },
        "imported_obstruction": {
            "defect_count": len(inherited),
            "matrix_position_count": len({(row, column) for row, column, _word, _mode in inherited}),
            "first_exact_witness": obstruction_payload["mixed_nilpotency_obstruction"]["first_exact_witness"],
            "rod_wave_defect_count": obstruction_payload["mixed_nilpotency_obstruction"]["rod_wave_defect_count"],
            "assembly": assembly,
        },
        "complete_local_action_hessian_ansatz": {
            "derivation": (
                "The epsilon_R_squared degree filter fixes Gamma_R and Gamma_R_sharp as degree-zero gauge/control maps and generates four serialized Hessian correction blocks. "
                "Formal-adjoint pairing, equality of mixed partials and derivation from the single local scalar S_R,H-S_R,I6 impose one common amplitude."
            ),
            "mechanical_degree_partition_rule": "scan every serialized net-replacement block; epsilon_R_squared factor count one is an action-Hessian correction, count zero is a fixed gauge/control map, and every other degree is rejected",
            "single_action_origin": action_origin,
            "fixed_degree_zero_control_blocks": list(control_blocks),
            "raw_block_amplitudes": list(action_blocks),
            "raw_dimension": len(action_blocks),
            "integrability_constraint_matrix": [[int(value) for value in row] for row in raw_constraint.tolist()],
            "integrability_constraint_rank": int(raw_constraint.rank()),
            "canonical_nullspace_basis": [[int(value) for value in vector] for vector in raw_constraint.nullspace()],
            "action_orbit_dimension": len(raw_constraint.nullspace()),
            "action_orbit_vector": [1] * len(action_blocks),
            "block_entry_counts": {
                name: len(interface["operator_blocks"][name]["net_replacement_delta"]["entries"])
                for name in action_blocks
            },
            "formal_adjoint_and_hessian_audit": interface["formal_adjoint_and_hessian_audit"],
            "real_structure_defect_count": real_structure_defect_count(interface, action_blocks),
            "K_Berger_invariance_identity": interface["K_Berger_interface"]["action_invariance_identity"],
            "K_Berger_invariance_defect_count": 0,
            "correction_orbit_operator_summary": engine.summary(orbit),
            "correction_orbit_mixed_square_summary": orbit_summary,
        },
        "background_preservation_gate": {
            "first_variation_anchor": interface["independent_variation_anchor"],
            "specialized_anchor_coefficient": sp.sstr(background_anchor),
            "constraint_matrix": [[sp.sstr(background_anchor)]],
            "constraint_rank": 1,
            "admissible_dimension": 0,
            "conclusion": "Every nonzero multiple of the unique action orbit changes the frozen background equation; the work-item prohibition therefore forces amplitude zero.",
        },
        "nilpotency_equation": {
            "identity": "D_current + mu*[q00,Delta_action]=0 in the exact Berger-background/sphere quotient",
            "scalar_equation_count": len(equations),
            "nonzero_correction_coefficient_count": sum(int(a != 0) for a, _b in equations),
            "nonzero_right_hand_side_count": sum(int(b != 0) for _a, b in equations),
            "coefficient_matrix_shape": [len(equations), 1],
            "coefficient_matrix_rank": coefficient_rank,
            "augmented_matrix_rank": augmented_rank,
            "solution_status": "INCONSISTENT",
            "correction_only_equation": correction_equation,
            "target_only_equation": target_only_equation,
            "canonical_two_equation_augmented_determinant": sp.sstr(
                sp.sympify(correction_equation["correction_coefficient"])
                * sp.sympify(target_only_equation["right_hand_side"])
            ),
            "first_unavoidable_defect": target_only_equation,
        },
        "control_and_consumer_disposition": {
            "healthy_clock_rod_and_Maxwell_control_rows": "UNCHANGED_BECAUSE_THE_COMPLETE_ADMISSIBLE_CORRECTION_SPACE_IS_ZERO_DIMENSIONAL",
            "signed_pairing_rank_112": "CERTIFIED_IMPORTED",
            "complete_repaired_replacement112_q1": "NO_CERTIFIED_MAP",
            "generic_and_zero_mode_rank_cohomology": "NO_CERTIFIED_MAP",
            "material_parent56_internal_q1_and_rank2_detector": "CERTIFIED_SEPARATE_UNCHANGED",
            "apparatus_160_pushout": "NONDEFINED",
            "physical_reduction_detector_memory_redshift_recoil": "NO_CERTIFIED_MAP",
            "q2_q3_and_quantum": "NOT_REACHED",
        },
        "mutation_targets": {
            "split_the_four_integrable_block_amplitudes": "REJECTED_BY_RANK_THREE_HESSIAN_INTEGRABILITY_CONSTRAINT",
            "rescale_the_unique_action_orbit": "REJECTED_BY_RANK_ONE_VERSUS_AUGMENTED_RANK_TWO_NILPOTENCY_SYSTEM",
            "change_the_background_equation": "FORBIDDEN_AND_DETECTED_BY_NONZERO_FIRST_VARIATION_ANCHOR",
            "delete_the_target_only_defect_row": "FORBIDDEN_AND_REJECTED_BY_DEPENDENCY_HASH_AND_TYPED_WITNESS",
            "import_material_readout_blocks_as_internal_56_entries": "REJECTED_BY_CERTIFIED_RELATIVE_INTERFACE_TYPING",
        },
        "does_not_establish": [
            "a no-go outside the declared finite local single-action Hessian sector",
            "a repaired or executable replacement-112 unary",
            "a 160-row apparatus pushout or physical reduction",
            "detector response, memory, redshift, recoil, q2, q3 or quantum observables",
            "a Lorentzian causal metric-BV propagator",
        ],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement112-132-defect-minimal-nilpotent-repair-no-go-v1",
        "result_id": "BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO",
        "setting_id": values["mixed_nilpotency"]["setting_id"],
        "claim_status": "OBSTRUCTED_COMPLETE_LOCAL_ACTION_HESSIAN_ANSATZ_HAS_NO_NILPOTENT_REPAIR",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha(path)}
            for name, path in DEPS.items()
        },
        "payload_ref": {
            "path": str(X.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical(payload),
        },
        "gate_results": payload["control_and_consumer_disposition"],
        "ansatz_result": {
            "raw_dimension": payload["complete_local_action_hessian_ansatz"]["raw_dimension"],
            "integrability_rank": payload["complete_local_action_hessian_ansatz"]["integrability_constraint_rank"],
            "action_orbit_dimension": payload["complete_local_action_hessian_ansatz"]["action_orbit_dimension"],
            "background_preserving_dimension": payload["background_preservation_gate"]["admissible_dimension"],
            "nilpotency_coefficient_rank": payload["nilpotency_equation"]["coefficient_matrix_rank"],
            "nilpotency_augmented_rank": payload["nilpotency_equation"]["augmented_matrix_rank"],
        },
        "first_obstruction": payload["nilpotency_equation"]["first_unavoidable_defect"],
        "next_gate": "NO_REPLACEMENT112_PUSHOUT_UNTIL_THE_ACTION_OR_BACKGROUND_ARCHITECTURE_CHANGES_WITH_A_NEW_CERTIFIED_WORK_ITEM",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE no-go imports the certified 132-entry replacement-112 mixed-square obstruction, the complete six-block mixed metric--rod interface, the executable material-parent-56 relative readout interface and the categorical pushout nondefinition by content hash. The epsilon_R_squared degree filter keeps Gamma_R and Gamma_R_sharp fixed as healthy degree-zero gauge/control maps. A mechanical basis generator therefore starts from the four action-Hessian correction amplitudes K_RR, K_Rh, K_hR and Delta_K_hh_rod. Tensor typing, equality of mixed partials, signed pairing adjointness and derivation from the single local scalar S_R,H-S_R,I6 give a rank-three exact constraint matrix and the unique common-amplitude action orbit. Its real defect is zero and exact reduction of A^T H+H A gives zero simultaneous K_Berger defects. At the certified nondegenerate unit-circle fixture, the full orbit commutator has 444 quotient entries in 60 positions. Coefficientwise comparison with all 132 inherited defects yields 4542 exact scalar equations: the one-column coefficient matrix has rank one while the augmented matrix has rank two. Canonically, the orbit creates a nonzero h_hat_star_00-from-c_spatial_1 coefficient where the target is zero, yet has zero coefficient on the inherited j*x0^2 component of h_hat_star_00-from-sigma, whose right-hand side is nonzero. Thus even an unrestricted rescaling of the complete action orbit cannot repair nilpotency. More strongly, its exact nonzero first-variation anchor shows every nonzero amplitude changes the frozen background equation, so the permitted background-preserving correction class has dimension zero. No row is deleted and healthy clock, rod and Maxwell controls remain unchanged. The standalone material-parent-56 unary and rank-two detector remain certified but separate; the 160-row pushout stays NONDEFINED and rank/cohomology, detector reduction, memory, redshift, recoil, q2, q3 and quantum claims stay fail-closed. The independent verifier checks hashes, reconstructs the four-to-one exact ansatz reduction, independently reduces A^T H+H A, and replays the rank-one/rank-two inconsistency from the serialized canonical coefficient equations without importing this producer; it does not reassemble all 112 PBW rows."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_replacement112_132_defect_minimal_nilpotent_repair --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement112_132_defect_minimal_nilpotent_repair",
            "producer_source_sha256": sha(Path(__file__)),
            "assembly_engine_sha256": sha(P / "berger_replacement112_executable_unary_engine.py"),
        },
    }


def report_text() -> str:
    return """# Replacement-112 132-defect minimal nilpotent repair no-go

The complete declared local action-Hessian correction class has four raw block
amplitudes and three exact integrability/adjoint constraints, hence one common
action orbit.  Its exact Berger-quotient nilpotency system has coefficient rank
one and augmented rank two.  A canonical correction-only coefficient forces
the orbit amplitude, while the inherited `j*x0^2` coefficient of
`h_hat_star_00 <- sigma` is outside that orbit and remains nonzero.  The
nonzero first-variation anchor independently reduces the allowed
background-preserving correction space to dimension zero.

The 112-row unary therefore remains obstructed.  The certified 56-row material
unary and rank-two detector stay separate, and the 160-row pushout remains
nondefined.  No cohomology, detector reduction, memory, redshift, recoil,
interaction or quantum claim is promoted.

CLOSE-OUT: OBSTRUCTED — the complete declared local action-Hessian ansatz has coefficient rank one and augmented nilpotency rank two
EVIDENCE: closed_universe_observers/certificates/BERGER_REPLACEMENT112_132_DEFECT_MINIMAL_NILPOTENT_REPAIR_NO_GO.json
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
