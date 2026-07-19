"""Independent verifier core for both ordered cross-parity L4 matrices."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix import fraction_string, rational_interval


ROOT = Path(__file__).resolve().parents[2]
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_polar_L4_q2_slice.json"
PARITY = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
CALIBRATION = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
ROW_LAYOUT = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json"
ACTION = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/action.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str, **locals_: sp.Expr) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, **locals_})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def branch_mass(branch: str) -> sp.Expr:
    return {"q_minus": 6 - 2 * sp.sqrt(3), "p_extra": sp.Rational(16, 3), "q_plus": 6 + 2 * sp.sqrt(3)}[branch]


def target_mass(branch: str) -> sp.Expr:
    return {"q_minus": 20 - 2 * sp.sqrt(10), "p_extra": sp.Rational(58, 3), "q_plus": 20 + 2 * sp.sqrt(10)}[branch]


def axial_basis(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    mass = branch_mass(branch)
    if branch != "p_extra":
        return [sp.Matrix([2 * momentum, -2 * frequency, momentum * (mass - 6), -frequency * (mass - 6)])]
    return [sp.Matrix([-momentum**2 - 6, momentum * frequency, 6, 0]), sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, 6])]


def polar_basis(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    if branch == "p_extra":
        return [
            sp.Matrix(
                [
                    1,
                    -(3 * momentum**2 + 8) / (3 * momentum * frequency),
                    1,
                    0,
                ]
            ),
            sp.Matrix(
                [
                    sp.Rational(4, 3),
                    -2 * (momentum**2 + 6) / (3 * momentum * frequency),
                    0,
                    1,
                ]
            ),
        ]
    mass = branch_mass(branch)
    maxwell = sp.Integer(6)
    sphere_trace = -12 * maxwell / (mass - 6)
    reconstruction = sphere_trace - 2 * maxwell
    common = -(frequency**2 + momentum**2) * reconstruction / mass
    mixed = 2 * momentum * frequency * reconstruction / mass
    return [
        sp.Matrix(
            [
                common + sphere_trace,
                mixed,
                common - sphere_trace,
                maxwell,
            ]
        ).applyfunc(sp.factor)
    ]


def target_adjoints(branch: str, momentum: sp.Expr, frequency: sp.Expr) -> list[sp.Matrix]:
    if branch == "p_extra":
        return [sp.Matrix([-momentum**2 - 20, momentum * frequency, 20, 0]), sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, 20])]
    mass = target_mass(branch)
    return [sp.Matrix([2 * momentum, -2 * frequency, momentum * (mass - 20), -frequency * (mass - 20)])]


def parsed_source() -> tuple[tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], tuple[sp.Symbol, ...], sp.Matrix]:
    value = json.loads(SLICE.read_text())
    assert value["parent"] == {"q2_sha256": sha(Q2), "row_layout_sha256": sha(ROW_LAYOUT), "action_sha256": sha(ACTION)}
    assert value["pbw_support"]["ordered_term_counts"] == {"axial_then_polar": 832, "polar_then_axial": 832}
    variables = sp.symbols("k_1 omega_1 k_2 omega_2", real=True)
    axial, polar = sp.symbols("a_0:4", real=True), sp.symbols("b_0:4", real=True)
    local = {str(x): x for x in (*variables, *axial, *polar)}
    source = sp.Matrix([parse(row, **local) for row in value["source_action_rows"]])
    return variables, axial, polar, source


def verify_direct_calibration(source: sp.Matrix, variables: tuple[sp.Symbol, ...], axial: tuple[sp.Symbol, ...], polar: tuple[sp.Symbol, ...]) -> None:
    k, w = sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6)), sp.sqrt(sp.Rational(29, 6))
    specialized = source.subs({variables[0]: k, variables[1]: w, variables[2]: -k, variables[3]: w, **dict(zip(axial, axial_basis("q_minus", k, w)[0], strict=True)), **dict(zip(polar, polar_basis("q_minus", -k, w)[0], strict=True))}, simultaneous=True)
    expected = sp.Matrix([parse(row) for row in json.loads(CALIBRATION.read_text())["direct_source_ledger"]["axial_plus_polar_minus"]["source_rows"]])
    assert (specialized - expected).applyfunc(canonical) == sp.zeros(4, 1)


def verify_matrix(mode: str) -> None:
    assert mode in ("axial_polar", "polar_axial")
    cert = ROOT / f"bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_{mode}_L4_matrix.json"
    schema = ROOT / f"bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_{mode}_L4_matrix.schema.json"
    value, schema_value = json.loads(cert.read_text()), json.loads(schema.read_text())
    Draft202012Validator.check_schema(schema_value); Draft202012Validator(schema_value).validate(value)
    assert value["schema_sha256"] == sha(schema)
    for item in value["provenance"]["inputs"].values(): assert sha(ROOT / item["path"]) == item["sha256"]
    assert value["source_slice"]["sha256"] == sha(SLICE)
    variables, axial_symbols, polar_symbols, source = parsed_source()
    verify_direct_calibration(source, variables, axial_symbols, polar_symbols)
    workload = {row["candidate_index"]: row for row in json.loads(PARITY.read_text())["source_workload"]["rows"] if row["output_ell"] == 4}
    assert [row["candidate_index"] for row in value["candidate_rows"]] == sorted(workload)
    fixtures = coefficients = zeros = obstructed = 0
    for row in value["candidate_rows"]:
        expected_row = workload[row["candidate_index"]]
        rho = parse(row["rho"]); momenta = [sign * sp.sqrt(rho) for sign in row["signed_momenta"]]
        frequencies = [sp.sqrt(momenta[0]**2 + branch_mass(row["first_branch"])), sp.sqrt(momenta[1]**2 + branch_mass(row["second_branch"]))]
        K, Omega = sum(momenta), sum(frequencies)
        assert canonical(Omega**2 - K**2 - target_mass(row["target_branch"])) == 0
        if mode == "axial_polar":
            first_basis, second_basis = axial_basis(row["first_branch"], momenta[0], frequencies[0]), polar_basis(row["second_branch"], momenta[1], frequencies[1])
            role_values = (momenta[0], frequencies[0], momenta[1], frequencies[1])
        else:
            first_basis, second_basis = polar_basis(row["first_branch"], momenta[0], frequencies[0]), axial_basis(row["second_branch"], momenta[1], frequencies[1])
            role_values = (momenta[1], frequencies[1], momenta[0], frequencies[0])
        assert (row["first_branch"], row["second_branch"], row["target_branch"]) == (expected_row["first_branch"], expected_row["second_branch"], expected_row["target_branch"])
        stored_fixtures = row["basis_fixtures"]
        index = 0
        for first_vector in first_basis:
            for second_vector in second_basis:
                fixture = stored_fixtures[index]; index += 1; fixtures += 1
                axial_vector, polar_vector = (first_vector, second_vector) if mode == "axial_polar" else (second_vector, first_vector)
                specialized = source.subs({variables[0]: role_values[0], variables[1]: role_values[1], variables[2]: role_values[2], variables[3]: role_values[3], **dict(zip(axial_symbols, axial_vector, strict=True)), **dict(zip(polar_symbols, polar_vector, strict=True))}, simultaneous=True)
                expected_pairings = [canonical((adjoint.T * specialized)[0]) for adjoint in target_adjoints(row["target_branch"], K, Omega)]
                stored_pairings = [parse(item) for item in fixture["pairings"]]
                assert len(expected_pairings) == len(stored_pairings)
                assert all(canonical(left - right) == 0 for left, right in zip(expected_pairings, stored_pairings, strict=True))
                coefficients += len(stored_pairings); has_witness = False
                for pairing, interval_value in zip(stored_pairings, fixture["pairing_intervals"], strict=True):
                    if pairing == 0: zeros += 1; assert interval_value is None
                    else:
                        assert interval_value is not None; interval = rational_interval(pairing, int(interval_value["decimal_digits"])); assert [fraction_string(x) for x in interval] == [interval_value["lower"], interval_value["upper"]]; assert interval[0] > 0 or interval[1] < 0; has_witness = True
                assert fixture["bounded_status"] == ("OBSTRUCTED" if has_witness else "OPEN"); obstructed += has_witness
    summary = value["matrix_summary"]
    assert (fixtures, coefficients, zeros, obstructed) == (summary["ordered_input_basis_fixtures"], summary["target_adjoint_coefficients"], summary["zero_target_adjoint_coefficients"], summary["basis_fixtures_with_nonzero_cokernel_vector"])
    assert (fixtures, coefficients, zeros, obstructed) == (20, 27, 0, 20)
    assert summary["nonzero_target_adjoint_coefficients"] == 27
    classification = value["classification"]
    progress = value["workload_progress"]
    assert classification["all_twenty_basis_fixtures_bounded_obstructed"]
    assert not classification["arbitrary_cross_parity_linear_combinations_classified"]
    assert not classification["causal_or_quantum_claim"]
    assert progress["remaining_nonaxisymmetric_L1_L3_coefficients"] == 56
    if mode == "axial_polar":
        assert classification["complete_ordered_axial_polar_L4_basis_matrix_classified"]
        assert not classification["reverse_input_order_matrix_classified"]
        assert not classification["all_axisymmetric_L4_coefficients_classified"]
        assert progress["resolved_axisymmetric_L4_coefficients"] == 81
        assert progress["remaining_axisymmetric_L4_coefficients"] == 27
    else:
        assert classification["complete_ordered_polar_axial_L4_basis_matrix_classified"]
        assert classification["all_axisymmetric_L4_basis_coefficients_classified"]
        assert not classification["complete_two_fibre_tangent_cone_classified"]
        assert progress["resolved_axisymmetric_L4_coefficients"] == 108
        assert progress["remaining_axisymmetric_L4_coefficients"] == 0
        assert value["graded_symmetry_audit"] == {
            "axial_then_polar_PBW_terms": 832,
            "both_orders_in_shared_slice": True,
            "name_based_mode_identification_used": False,
            "polar_then_axial_PBW_terms": 832,
            "reverse_matrix_obtained_by_explicit_role_substitution": True,
        }
