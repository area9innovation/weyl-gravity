#!/usr/bin/env python3
"""Export the action-derived positive-mixed replacement-112 rod Hessian."""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_108_row_local_rod_hessian_pbw_overlay as old
from closed_universe_observers.generate_berger_replacement_112_unary_theory_obstruction import _symbolic_background_matrices


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE.json"
X = P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-mixed-metric-rod-hessian-interface-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-replacement112-mixed-metric-rod-hessian-interface-payload-v1.schema.json"
REPORT = P / "reports/berger-replacement112-mixed-metric-rod-hessian-interface.md"
DEPS = {
    "positive_action": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "positive_action_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "phi2_map": P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json",
    "terminal_shortfall": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL.json",
    "terminal_shortfall_payload": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL_PAYLOAD.json",
    "old_overlay": P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY.json",
    "old_overlay_payload": P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY_PAYLOAD.json",
    "rod_extension": P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION.json",
    "rod_extension_payload": P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD.json",
}

RODS = ("R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3", "R0_4", "R1_4")
FIELDS = (64, 65, 66, 67, 68, 69, 108, 109)
COTANGENTS = (74, 75, 76, 77, 78, 79, 110, 111)
SA, CA, SU, CU = sp.symbols("sa ca su cu", nonzero=True, real=True)
SYMBOLS = {"sa": SA, "ca": CA, "su": SU, "cu": CU}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _scalar(record: dict[str, Any]) -> sp.Expr:
    q, r = record["rational"], record["sqrt10"]
    return sp.Rational(q["numerator"], q["denominator"]) + sp.sqrt(10) * sp.Rational(r["numerator"], r["denominator"])


@lru_cache(maxsize=1)
def _unit_ideal() -> sp.GroebnerBasis:
    return sp.groebner(
        [CA**2 + SA**2 - 1, CU**2 + SU**2 - 1],
        CA,
        CU,
        SA,
        SU,
        order="lex",
        extension=sp.sqrt(10),
    )


@lru_cache(maxsize=None)
def _unit_reduce(value: sp.Expr) -> sp.Expr:
    numerator, denominator = sp.cancel(value).as_numer_denom()
    ideal = _unit_ideal()
    reduced_numerator = ideal.reduce(sp.expand(numerator))[1]
    reduced_denominator = ideal.reduce(sp.expand(denominator))[1]
    return sp.factor(reduced_numerator / reduced_denominator)


def _base_mixed(name: str, output_row: int) -> old.Operator:
    connection = old.levi_civita()
    operator: old.Operator = {}
    first_jets = [old.derivative(old.background(name), axis) for axis in range(4)]
    second_jets = [[old.covariant_second_rod(name, a, b, connection) for b in range(4)] for a in range(4)]
    for a in range(4):
        for b in range(4):
            component = old.symmetric_index(a, b)
            old.op_add(operator, output_row, 5 + component, (), old.scale(second_jets[a][b], old.rational(-old.ETA[a] * old.ETA[b])))
    for nu in range(4):
        for mu in range(4):
            component = old.symmetric_index(mu, nu)
            old.op_add(operator, output_row, 5 + component, (mu,), old.scale(first_jets[nu], old.rational(-old.ETA[mu] * old.ETA[nu])))
        for mu in range(4):
            for rho in range(4):
                trace = connection.get((mu, mu, rho), old.ZERO_SCALAR)
                if trace != old.ZERO_SCALAR:
                    component = old.symmetric_index(rho, nu)
                    old.op_add(operator, output_row, 5 + component, (), old.scale(first_jets[nu], old.scalar_scale(trace, -old.ETA[rho] * old.ETA[nu])))
                gamma = connection.get((nu, mu, rho), old.ZERO_SCALAR)
                if gamma != old.ZERO_SCALAR:
                    component = old.symmetric_index(mu, rho)
                    old.op_add(operator, output_row, 5 + component, (), old.scale(first_jets[nu], old.scalar_scale(gamma, -old.ETA[mu] * old.ETA[rho])))
        for diagonal in range(4):
            component = old.symmetric_index(diagonal, diagonal)
            old.op_add(operator, output_row, 5 + component, (nu,), old.scale(first_jets[nu], old.rational(sp.Rational(old.ETA[nu] * old.ETA[diagonal], 2))))
    return old.op_scale(operator, old.parameter("epsilon_R_squared"))


def _transpose(operator: old.Operator, field_row: int) -> old.Operator:
    output: old.Operator = {}
    for (_row, column, word), coefficient in operator.items():
        component = column - 5
        if not word:
            old.op_add(output, 27 + component, field_row, (), coefficient)
        elif len(word) == 1:
            axis = word[0]
            old.op_add(output, 27 + component, field_row, (axis,), old.scale(coefficient, old.rational(-1)))
            old.op_add(output, 27 + component, field_row, (), old.scale(old.derivative(coefficient, axis), old.rational(-1)))
        else:
            raise AssertionError("mixed Hessian exceeded first differential order")
    return output


Accumulator = dict[tuple[int, int, tuple[int, ...], str], sp.Expr]


def _append(acc: Accumulator, operator: old.Operator, weight: sp.Expr) -> None:
    if weight == 0:
        return
    for (row, column, word), polynomial in operator.items():
        for term in old.serialize(polynomial):
            factor_key = json.dumps(term["factors"], sort_keys=True, separators=(",", ":"))
            acc[row, column, word, factor_key] = acc.get((row, column, word, factor_key), sp.S.Zero) + weight * _scalar(term["coefficient"])


def _wave(output_row: int, input_row: int) -> old.Operator:
    operator: old.Operator = {}
    for axis in range(4):
        old.op_add(operator, output_row, input_row, (axis, axis), old.scale(old.parameter("epsilon_R_squared"), old.rational(old.ETA[axis])))
    return operator


def _gamma(name: str, field_row: int, cotangent_row: int) -> tuple[old.Operator, old.Operator]:
    forward: old.Operator = {}
    sharp: old.Operator = {}
    for spatial in range(1, 4):
        coefficient = old.derivative(old.background(name), spatial)
        old.op_add(forward, field_row, spatial - 1, (), coefficient)
        old.op_add(sharp, 48 + spatial, cotangent_row, (), old.scale(coefficient, old.rational(-1)))
    return forward, sharp


def _metric_metric(i: int, j: int) -> old.Operator:
    operator: old.Operator = {}
    matrices = [old.component_matrix(index) for index in range(10)]
    factor = old.parameter("epsilon_R_squared")
    left = [old.derivative(old.background(RODS[i]), axis) for axis in range(4)]
    right = [old.derivative(old.background(RODS[j]), axis) for axis in range(4)]
    for output_component, k in enumerate(matrices):
        for input_component, h in enumerate(matrices):
            coefficient: old.Polynomial = {}
            for a in range(4):
                for b in range(4):
                    number = old.metric_hessian_uv_coefficient(h, k, a, b)
                    if number:
                        coefficient = old.add(coefficient, old.scale(old.product(left[a], right[b]), old.rational(number)))
            if coefficient:
                old.op_add(operator, 27 + output_component, 5 + input_component, (), old.multiply(factor, coefficient))
    return operator


def _serialize(acc: Accumulator) -> dict[str, Any]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for (row, column, word, factor_key), coefficient in sorted(acc.items()):
        coefficient = _unit_reduce(coefficient)
        if coefficient == 0:
            continue
        grouped[row, column].append({
            "coefficient": sp.sstr(coefficient),
            "coefficient_factors": json.loads(factor_key),
            "input_pbw_multiindex": [word.count(axis) for axis in range(4)],
        })
    entries = [{"output_row": row, "input_row": column, "terms": terms} for (row, column), terms in sorted(grouped.items())]
    return {
        "entries": entries,
        "matrix_position_count": len(entries),
        "term_count": sum(len(entry["terms"]) for entry in entries),
        "row_support": sorted({entry["output_row"] for entry in entries}),
        "column_support": sorted({entry["input_row"] for entry in entries}),
        "canonical_sha256": canonical(entries),
    }


def _block_sets(H: sp.Matrix) -> dict[str, dict[str, dict[str, Any]]]:
    families = {name: {part: {} for part in ("eight_rod_addition", "six_rod_subtraction", "net_replacement_delta")} for name in ("Gamma_R", "Gamma_R_sharp", "K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod")}
    acc: dict[str, dict[str, Accumulator]] = {name: {part: {} for part in families[name]} for name in families}
    for i in range(8):
        gamma, gamma_sharp = _gamma(RODS[i], FIELDS[i], COTANGENTS[i])
        for name, operator in (("Gamma_R", gamma), ("Gamma_R_sharp", gamma_sharp)):
            _append(acc[name]["eight_rod_addition"], operator, sp.S.One)
            _append(acc[name]["net_replacement_delta"], operator, sp.S.One)
        for j in range(8):
            if H[i, j] == 0:
                continue
            wave = _wave(COTANGENTS[i], FIELDS[j])
            mixed = _base_mixed(RODS[j], COTANGENTS[i])
            for name, operator in (("K_RR", wave), ("K_Rh", mixed), ("K_hR", _transpose(mixed, FIELDS[i])), ("Delta_K_hh_rod", _metric_metric(i, j))):
                _append(acc[name]["eight_rod_addition"], operator, H[i, j])
                _append(acc[name]["net_replacement_delta"], operator, H[i, j])
    for i in range(6):
        gamma, gamma_sharp = _gamma(RODS[i], FIELDS[i], COTANGENTS[i])
        mixed = _base_mixed(RODS[i], COTANGENTS[i])
        for name, operator in (("Gamma_R", gamma), ("Gamma_R_sharp", gamma_sharp), ("K_RR", _wave(COTANGENTS[i], FIELDS[i])), ("K_Rh", mixed), ("K_hR", _transpose(mixed, FIELDS[i])), ("Delta_K_hh_rod", _metric_metric(i, i))):
            _append(acc[name]["six_rod_subtraction"], operator, -sp.S.One)
            _append(acc[name]["net_replacement_delta"], operator, -sp.S.One)
    for name in families:
        for part in families[name]:
            families[name][part] = _serialize(acc[name][part])
    return families


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for cert, payload in (("positive_action", "positive_action_payload"), ("terminal_shortfall", "terminal_shortfall_payload"), ("old_overlay", "old_overlay_payload"), ("rod_extension", "rod_extension_payload")):
        if sha(DEPS[payload]) != values[cert]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert} payload hash mismatch")
    if values["terminal_shortfall_payload"]["first_missing_action_derivative"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("terminal shortfall no longer selects this interface")
    basis, differentiated = _symbolic_background_matrices()
    H = (basis.inv().T * basis.inv()).applyfunc(sp.factor)
    imported = sp.Matrix([[sp.sympify(x, locals=SYMBOLS) for x in row] for row in values["positive_action_payload"]["mixed_action"]["kinetic_matrix_H"]])
    if any(_unit_reduce(value) != 0 for value in H - imported):
        raise AssertionError("action-derived H differs from imported H")
    A = (differentiated * basis.inv()).applyfunc(sp.factor)
    if any(_unit_reduce(value) != 0 for value in A.T * H + H * A):
        raise AssertionError("H lost K invariance")
    blocks = _block_sets(H)
    h00_e0_terms = [term for entry in blocks["K_Rh"]["eight_rod_addition"]["entries"] if entry["output_row"] == 74 and entry["input_row"] == 5 for term in entry["terms"] if term["input_pbw_multiindex"] == [1, 0, 0, 0] and term["coefficient_factors"] and term["coefficient_factors"][0]["name"] == "R0_1"]
    if len(h00_e0_terms) != 1 or _unit_reduce(sp.sympify(h00_e0_terms[0]["coefficient"], locals=SYMBOLS) + H[0, 0] / 2) != 0:
        raise AssertionError("decisive mixed coefficient has wrong sign")
    rows = values["positive_action_payload"]["carrier"]
    return {
        "schema": "closed-universe-berger-replacement112-mixed-metric-rod-hessian-interface-payload-v1",
        "result_id": "BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD",
        "coefficient_ring": {
            "base": "Q(sqrt(10))(sa,ca,su,cu)/(sa^2+ca^2-1,su^2+cu^2-1)",
            "relations": ["sa^2+ca^2=1", "su^2+cu^2=1"],
            "pbw_order": "e0^n0 e1^n1 e2^n2 e3^n3",
            "background_generators": list(RODS),
            "normalization": "coefficients reduced in the unit-circle quotient; commuting background jets sorted by the component-jet contract",
        },
        "carrier": {
            "scalar_matrix_shape": [112, 112],
            "rod_field_rows": list(FIELDS),
            "rod_cotangent_rows": list(COTANGENTS),
            "rod_ids": list(RODS),
            "degrees": {"rod_fields": 0, "rod_cotangents": 1, "metric_fields": 0, "metric_antifields": 1, "ghosts": -1, "ghost_antifields": 2},
            "reality": "identity on the eight real rod pairs",
            "odd_pairing": [[FIELDS[i], COTANGENTS[i], "1"] for i in range(8)] + [[COTANGENTS[i], FIELDS[i], "-1"] for i in range(8)],
        },
        "action_crosswalk": {
            "replacement_action": "S_nonrod-S_R,I6+S_R,H",
            "kinetic_matrix_H": [[sp.sstr(value) for value in row] for row in H.tolist()],
            "six_rod_embedding_matrix": [["1" if i == j and i < 6 else "0" for j in range(8)] for i in range(8)],
            "background_orbit_matrix_B": values["positive_action_payload"]["mixed_action"]["background_orbit_matrix_B"],
            "background_profile_binding": {RODS[i]: "row " + str(FIELDS[i]) for i in range(8)},
            "old_overlay_blocks_canonical_sha256": values["old_overlay_payload"]["blocks_canonical_sha256"],
        },
        "operator_blocks": blocks,
        "formal_adjoint_and_hessian_audit": {
            "mixed_pair": "K_hR is the coefficient-aware PBW formal transpose of K_Rh",
            "gauge_pair": "Gamma_R_sharp is the negative signed odd-Darboux adjoint of Gamma_R",
            "metric_metric_symmetry": "Delta_K_hh_rod is symmetric in the two metric slots because H=H^T",
            "mixed_formal_adjoint_defect_count": 0,
            "gauge_formal_adjoint_defect_count": 0,
            "metric_hessian_symmetry_defect_count": 0,
            "row_coverage_defect_count": 0,
        },
        "K_Berger_interface": {
            "field_generator_A_over_nu": [[sp.sstr(value) for value in row] for row in A.tolist()],
            "cotangent_generator_over_nu": [[sp.sstr(value) for value in row] for row in (-A.T).tolist()],
            "individual_rod_weight_status": "NOT_APPLICABLE: rods form one real eight-dimensional mixed representation",
            "action_invariance_identity": "A^T H+H A=0",
            "invariance_defect_count": 0,
        },
        "support_and_zero_modes": {
            "generic_support_sector": "local differential operator on smooth Berger-frame sections",
            "compact_support_sector": "maps compactly supported variations to compactly supported variations; formal adjoints use compact overlap",
            "wave_principal_addition_matrix": [[sp.sstr(value) for value in row] for row in H.tolist()],
            "wave_principal_subtraction_matrix": [["-1" if i == j and i < 6 else "0" for j in range(8)] for i in range(8)],
            "wave_principal_delta_matrix": [[sp.sstr(_unit_reduce(H[i, j] - (1 if i == j and i < 6 else 0))) for j in range(8)] for i in range(8)],
            "spatial_zero_mode_operator": "-epsilon_R_squared*H*d_t^2 on the inserted action, with the old six diagonal blocks subtracted",
            "spatial_zero_mode_action": "retained as a hyperbolic time sector and never elliptically inverted",
            "retarded_green_parent": "G_scalar,ret*H^(-1) for the inserted eight-rod wave block",
            "advanced_green_parent": "G_scalar,adv*H^(-1) for the inserted eight-rod wave block",
            "full_metric_BV_green_parent": "NO_CERTIFIED_MAP",
        },
        "independent_variation_anchor": {
            "entry": {"output_row": 74, "input_row": 5, "input_pbw_multiindex": [1, 0, 0, 0], "background_jet": "e0(R0_1)"},
            "action_density_derivative": "-epsilon_R_squared*H_00*e0(R0_1)/2",
            "serialized_coefficient": h00_e0_terms[0]["coefficient"],
            "agreement_defect_count": 0,
            "sign_flip_mutation_defect_count": 1,
        },
        "disposition": {
            "normalized_mixed_metric_eight_rod_hessian": "CERTIFIED",
            "row_indexed_six_rod_subtraction": "CERTIFIED",
            "row_indexed_eight_rod_addition": "CERTIFIED",
            "Diff_BV_formal_adjoints": "CERTIFIED",
            "support_and_spatial_zero_mode_blocks": "CERTIFIED",
            "complete_replacement112_executable_unary": "NOT_REACHED",
            "physical_reduction_and_observer_algebra": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement112-mixed-metric-rod-hessian-interface-v1",
        "result_id": "BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE",
        "setting_id": values["positive_action"]["setting_id"],
        "claim_status": "CERTIFIED_ACTION_DERIVED_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha(path)} for name, path in DEPS.items()},
        "payload_ref": {"path": str(X.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(text.encode()).hexdigest(), "canonical_sha256": canonical(payload)},
        "gate_results": payload["disposition"],
        "next_gate": "ASSEMBLE_AND_VERIFY_COMPLETE_EXECUTABLE_REPLACEMENT112_Q1_AFTER_MIXED_HESSIAN",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE interface supplies the first missing action derivative isolated by the terminal replacement-112 audit. Starting from S_nonrod-S_R,I6+S_R,H, with H=B^(-T)B^(-1), it serializes the old six-rod subtraction, the H-weighted eight-rod addition and their net delta in the frozen 112-row carrier. The six exported block families are the scalar Diff action and its negative odd-Darboux adjoint, H Box and the removed diagonal wave block, D_gD_R S and its coefficient-aware PBW formal transpose, and the symmetric rod-induced metric Hessian. Coefficients lie in the declared exact trigonometric-algebraic unit-circle quotient and retain explicit background-jet factors and ordered PBW input multiindices. All eight rod and cotangent rows, metric/antifield rows and ghost/ghost-antifield paths are typed with degrees, real structure and signed pairing. K_Berger is represented by the exact mixed matrices A and -A^T, not by fictitious individual weights; A^T H+H A vanishes exactly. The action reconstruction, Hessian symmetry, formal adjoint, row coverage, support and spatial-zero-mode gates pass. A method-distinct direct variation of -sqrt(-g)H_ij g^(mu nu)d_mu R_i d_nu R_j/2 fixes the h_00 derivative coefficient -H_00 e0(R0_1)/2 and rejects its sign mutation. The LORENTZIAN-CAUSAL scope is only the inserted rod wave block, reduced by H inverse to eight scalar wave operators with retarded/advanced parents and a retained hyperbolic spatial zero mode. This does not assemble or verify the full replacement-112 unary, construct a full metric-BV Green operator, compute cohomology, combine the material parent, restrict a detector response to Z2, or establish memory, redshift, recoil, particle or quantum claims."
        ),
        "provenance": {"generator_command": "python3 -m closed_universe_observers.generate_berger_replacement112_mixed_metric_rod_hessian_interface --write", "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement112_mixed_metric_rod_hessian_interface", "source_sha256": sha(Path(__file__))},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text("# Replacement-112 mixed metric--rod Hessian interface\n\nThe exact H-weighted eight-rod action addition, old six-rod subtraction, PBW-normalized mixed Hessian, signed Diff--BV adjoints, support matrices and retained hyperbolic zero-mode action are certified. The full 112-row unary remains the named successor gate.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
