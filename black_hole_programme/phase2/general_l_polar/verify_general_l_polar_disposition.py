#!/usr/bin/env python3
"""Independent verifier for the generic-ell polar disposition.

The verifier does not import the producer.  It evaluates two explicit
harmonics, ell=3 and ell=4, in the full coordinate Bianchi divergence and
checks them against the serialized symbolic-Lambda rows.  It also derives the
STF tensor harmonic directly from the two-sphere Christoffels and independently
audits every fail-closed promotion flag and imported content hash.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.core.function import AppliedUndef

from black_hole_programme.weyl_geometry import Geometry


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
ATLAS = ROOT / "residual_atlas/phase2-black-hole-general-l-polar-disposition-fragment-v1.json"
EXPECTED_IMPORTS = {
    "black_hole_programme/certificates/BH2_GENERAL_L_STRUCTURAL.json": "1c375331014b1121791e8d6c63d994d84a41a0a94aa94233ecf28222475b6863",
    "black_hole_programme/certificates/BH2B_POLAR_SPLIT.json": "1c84cd014d31e1f97b6489ef083d5e81bcf83ba08eb9aa749c19931e60d5b8d5",
    "black_hole_programme/certificates/BH2B_POLAR_REACH.json": "c2639050b9d735d73daa756aed99c86e6882d354c99e13eb7a806a7a8d3ea977",
    "black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json": "df58e1c00ef75450602009ec07f490fe594d1223a5fd54376d150e563cfe9780",
    "black_hole_programme/certificates/BH2B_COMPOSED_REPAIR.json": "6fd94f8cd137592b6b5471c2bef62ad115c7f5453cb2b44f341e3b25206b94ac",
    "black_hole_programme/certificates/BH2C_POLAR_METRIC_INDICIAL.json": "98c9505228e186a7b3d3c94a52be824aa977cb9b318b370365f0f764e894d23b",
    "black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json": "e547439682a65a689c0c1bb8049a06e99638cbe91056918e3e5ffa39c1080f47",
    "black_hole_programme/certificates/BH2_POLAR_QUANTIFIER_REPAIR.json": "77658bfa250edbc493a9fd1b9f0f3a55da5078ecf36167b48ebbd4afc3207021",
    "black_hole_programme/certificates/BH2B_POLAR_CROSS_FLUX.json": "39530c7ea9173c5491cc082167e5c06f9439ddee1e5b151857235df965caf26d",
}
RECONSTRUCTION_MODULE = HERE / "symbolic_reconstruction.py"
LITERAL_CURRENT_MODULE = HERE / "literal_current.py"
CARRIER_ASYMPTOTICS_MODULE = HERE / "generic_carrier_asymptotics.py"
SOURCED_LIFT_MODULE = HERE / "sourced_lift.py"
SOURCED_LIFT_PILOT = HERE / "sourced_lift_depth2_pilot.json"
SOURCED_LIFT_PILOT_PRODUCER = HERE / "produce_sourced_lift_depth2_pilot.py"


class IndependentPolarVerificationError(RuntimeError):
    """Raised when the independent rail rejects the certificate."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentPolarVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_rows(serialized: list[str]) -> tuple[list[sp.Expr], dict[str, Any]]:
    v, r = sp.symbols("v r")
    local: dict[str, Any] = {
        "v": v,
        "r": r,
        "m": sp.Symbol("m", positive=True),
        "Lambda": sp.Symbol("Lambda"),
        "A": sp.Function("A"),
        "Bc": sp.Function("Bc"),
        "Cc": sp.Function("Cc"),
        "D": sp.Function("D"),
        "Ec": sp.Function("Ec"),
        "F": sp.Function("F"),
        "Gc": sp.Function("Gc"),
        "Derivative": sp.Derivative,
    }
    return [sp.sympify(value, locals=local) for value in serialized], local


def _raw_current_group_audit(serialized: str) -> tuple[int, int, dict[str, int]]:
    r = sp.Symbol("r")
    local: dict[str, Any] = {
        "r": r,
        "Lambda": sp.Symbol("Lambda"),
        "m": sp.Symbol("m"),
        "omega": sp.Symbol("omega"),
        "alpha": sp.Symbol("alpha"),
        "I": sp.I,
        "Derivative": sp.Derivative,
    }
    for component in "ABCK":
        for side in "ab":
            name = f"F{component}{side}_r"
            local[name] = sp.Function(name)
    expression = sp.expand(sp.sympify(serialized, locals=local))
    groups: dict[tuple[str, str], sp.Expr] = {}
    maxima = {component: 0 for component in "ABCK"}
    for term in sp.Add.make_args(expression):
        slots = [factor for factor in sp.Mul.make_args(term) if isinstance(factor, (sp.Derivative, AppliedUndef))]
        _require(len(slots) == 2, "literal current lost bilinearity")
        signature = tuple(sorted(sp.sstr(slot) for slot in slots))
        coefficient = term / slots[0] / slots[1]
        groups[signature] = groups.get(signature, 0) + coefficient
        for slot in slots:
            field = slot.expr if isinstance(slot, sp.Derivative) else slot
            component = field.func.__name__[1]
            order = sum(count for _, count in slot.variable_count) if isinstance(slot, sp.Derivative) else 0
            maxima[component] = max(maxima[component], order)
    return len(sp.Add.make_args(expression)), sum(sp.cancel(value) != 0 for value in groups.values()), maxima


def _zero_shell_current_coefficient(serialized: str) -> tuple[sp.Expr, dict[str, Any]]:
    r = sp.Symbol("r", positive=True)
    local: dict[str, Any] = {name: sp.Symbol(name) for name in ("m", "Lambda", "omega", "alpha", "ell")}
    local.update({"r": r, "I": sp.I, "pi": sp.pi, "Derivative": sp.Derivative})
    names = tuple(f"F{component}{side}_r" for component in "ABCK" for side in "ab")
    functions = {name: sp.Function(name) for name in names}
    local.update(functions)
    current = sp.sympify(serialized, locals=local)
    substitutions: dict[sp.Expr, sp.Expr] = {}
    amplitudes: dict[str, sp.Symbol] = {}
    for side in "ab":
        a0, a1, a2, b1, b2, c2, k2 = sp.symbols(f"A0{side} A1{side} A2{side} B1{side} B2{side} C2{side} K2{side}")
        amplitudes.update({symbol.name: symbol for symbol in (a0, a1, a2, b1, b2, c2, k2)})
        profiles = {"A": a0 * r**2 + a1 * r + a2, "B": b1 * r + b2, "C": c2, "K": k2}
        for component, profile in profiles.items():
            field = functions[f"F{component}{side}_r"](r)
            substitutions[field] = profile
            for derivative in current.atoms(sp.Derivative):
                if derivative.expr == field:
                    substitutions[derivative] = sp.diff(profile, r, derivative.derivative_count)
    reduced = sp.cancel(current.subs(substitutions).doit())
    numerator, denominator = sp.fraction(reduced)
    pnum, pden = sp.Poly(sp.expand(numerator), r), sp.Poly(sp.expand(denominator), r)
    denominator_degree = max(monomial[0] for monomial in pden.monoms())
    coefficient = sp.cancel(pnum.coeff_monomial(r ** (denominator_degree + 2)) / pden.LC())
    for power in range(3, max(monomial[0] for monomial in pnum.monoms()) - denominator_degree + 1):
        _require(pnum.coeff_monomial(r ** (denominator_degree + power)) == 0, "zero-shell current gained a term above r^2")
    return sp.factor(coefficient), {**local, **amplitudes}


def _explicit_bianchi_rows(ell: int) -> list[sp.Expr]:
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    coordinates = [v, r, x, phi]
    schwarzschild = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -schwarzschild
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coordinates, metric)
    inverse = geometry.ginv
    p = sp.legendre(ell, x)
    p_prime = sp.diff(p, x)
    lam = ell * (ell + 1)

    # Independent sphere-Christoffel construction of Hess^TF(Y).
    gamma_xx = 1 / (1 - x**2)
    gamma_pp = 1 - x**2
    christoffel_x_xx = x / (1 - x**2)
    christoffel_x_pp = x * (1 - x**2)
    tensor_xx = sp.cancel(sp.diff(p, x, 2) - christoffel_x_xx * p_prime + lam * gamma_xx * p / 2)
    tensor_pp = sp.cancel(-christoffel_x_pp * p_prime + lam * gamma_pp * p / 2)
    _require(sp.cancel(gamma_pp * tensor_xx + gamma_xx * tensor_pp) == 0, f"ell={ell} STF trace failed")

    a, bc, cc, d, ec, f, gc = [sp.Function(name)(v, r) for name in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    carrier = sp.zeros(4)
    carrier[0, 0] = a * p
    carrier[0, 1] = carrier[1, 0] = bc * p
    carrier[1, 1] = cc * p
    carrier[0, 2] = carrier[2, 0] = d * p_prime
    carrier[1, 2] = carrier[2, 1] = ec * p_prime
    carrier[2, 2] = metric[2, 2] * f * p + gc * tensor_xx
    carrier[3, 3] = metric[3, 3] * f * p + gc * tensor_pp
    trace = sp.cancel(sum(inverse[i, j] * carrier[i, j] for i in range(4) for j in range(4)))
    rows: list[sp.Expr] = []
    for index in range(3):
        raw = sum(
            inverse[i, e] * geometry.covd2(carrier, e, i, index)
            for i in range(4)
            for e in range(4)
            if inverse[i, e] != 0
        ) - sp.diff(trace, coordinates[index]) / 2
        harmonic = p if index < 2 else p_prime
        stripped = sp.cancel(raw / harmonic)
        _require(not stripped.has(x), f"ell={ell} Bianchi row {index} did not strip")
        rows.append(stripped)
    return rows


def verify_payload(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")
    _require(payload["result_id"] == "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_DISPOSITION", "result-id drift")

    imports = {entry["path"]: entry["sha256"] for entry in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED_IMPORTS, "import ledger changed")
    for path, digest in EXPECTED_IMPORTS.items():
        _require(_sha256(ROOT / path) == digest, f"input hash drift: {path}")
    _require(
        payload["provenance"]["reconstruction_module_sha256"] == _sha256(RECONSTRUCTION_MODULE),
        "reconstruction-module hash drift",
    )
    _require(
        payload["provenance"]["literal_current_module_sha256"] == _sha256(LITERAL_CURRENT_MODULE),
        "literal-current-module hash drift",
    )
    _require(payload["provenance"]["carrier_asymptotics_module_sha256"] == _sha256(CARRIER_ASYMPTOTICS_MODULE), "carrier-module hash drift")
    _require(payload["provenance"]["sourced_lift_module_sha256"] == _sha256(SOURCED_LIFT_MODULE), "sourced-lift-module hash drift")
    _require(payload["provenance"]["sourced_lift_pilot_sha256"] == _sha256(SOURCED_LIFT_PILOT), "sourced-lift-pilot hash drift")
    _require(payload["provenance"]["sourced_lift_pilot_producer_sha256"] == _sha256(SOURCED_LIFT_PILOT_PRODUCER), "sourced-lift-pilot producer hash drift")

    result = payload["exact_symbolic_lambda_result"]
    harmonics = result["harmonic_conventions"]
    _require(harmonics["tensor_definition"] == "Y_AB^TF=D_A D_B Y+(Lambda/2)gamma_AB Y", "tensor definition changed")
    _require(harmonics["integrated_norms_relative_to_NLambda"]["STF_tensor"] == "Lambda*(Lambda-2)/2", "STF norm changed")
    _require(harmonics["P2_positive_control"] == {"Lambda": 6, "W_xx": "3/2", "W_phiphi": "-3*(1-x^2)^2/2"}, "P2 control changed")

    cascade = result["bianchi_cascade"]
    _require(cascade["pivot_coefficients"] == ["-Lambda/r**2", "-Lambda/r**2", "(2 - Lambda)/(2*r**2)"], "cascade pivots changed")
    _require(cascade["symbolic_lambda_closed"] is True, "symbolic cascade flag lost")
    _require(cascade["angular_sampling_used"] is False, "angular sampling introduced")
    symbolic_rows, local = _parse_rows(cascade["stripped_rows"])
    for ell in (3, 4):
        explicit = _explicit_bianchi_rows(ell)
        for index, (generic, fixture) in enumerate(zip(symbolic_rows, explicit)):
            difference = sp.cancel(generic.subs(local["Lambda"], ell * (ell + 1)) - fixture)
            _require(difference == 0, f"ell={ell} Bianchi row {index} mismatch")

    reconstruction = result["ricci_to_metric_reconstruction"]
    _require(reconstruction["field"] == "Q(Lambda,omega,m,r)", "reconstruction field changed")
    _require(reconstruction["all_seven_rows_present"] is True, "seven-row map incomplete")
    _require(set(reconstruction["metric_rows"]) == {"vv", "vr", "rr", "vx", "rx", "angP", "angW"}, "row ledger changed")
    _require(reconstruction["reconstruction"]["solved_rows"] == ["angW", "vx", "rx", "rr"], "triangular pivots changed")
    _require(set(reconstruction["reconstruction"]["constraint_rows"]) == {"vv", "vr", "angP"}, "constraint ledger changed")
    _require(set(reconstruction["reconstruction"]["solved_row_defects"].values()) == {"0"}, "nonzero pivot defect")
    _require(
        reconstruction["denominator_ledger"]["pure_representation_factors"] == ["Lambda - 2", "Lambda"],
        "representation denominator ledger changed",
    )
    _require(reconstruction["conformal_radical"]["metric_generator"]["Ch"] == "0", "conformal generator changed")

    current = result["literal_lee_wald_current"]
    _require(current["literal_current_closed"] is True, "literal current flag lost")
    _require(current["angular_reduction_defect"] == "0", "angular reduction defect nonzero")
    _require(current["mixed_P_Pprime_coefficient"] == "0", "mixed angular term returned")
    _require(current["angular_sampling_used"] is False, "angular sampling introduced in current")
    _require(current["norms"] == {"scalar": "2/(2*ell+1)", "vector": "2*Lambda/(2*ell+1)", "azimuth": "2*pi"}, "current norm table changed")
    _require(current["component"] == "F^v=omega^0", "selection-current component changed")
    _require(current["sphere_measure"] == "r^2 dx dphi", "slice measure changed")
    _require("Lambda" in current["sphere_integrated_slice_current"], "current lost symbolic Lambda")
    expanded_terms, raw_groups, derivative_maxima = _raw_current_group_audit(current["sphere_integrated_slice_current"])
    filtration = result["literal_current_filtration"]
    _require(expanded_terms == filtration["expanded_terms"] == 272, "expanded current term count changed")
    _require(raw_groups == filtration["raw_radial_jet_groups"] == 79, "raw current filtration changed")
    _require(derivative_maxima == filtration["maximum_derivative_order"] == {"A": 3, "B": 2, "C": 2, "K": 3}, "current derivative filtration changed")
    _require(filtration["exact_oriented_nonzero_groups"] == 79, "oriented current group count changed")
    _require(filtration["coarse_unordered_support_classes"] == 23 and filtration["coarse_projection_is_not_an_algebraic_reduction"] is True, "coarse filtration typing changed")
    _require(filtration["zero_shell_metric_depth"] == 2, "zero-shell current depth changed")
    _require(filtration["oscillatory_layers"] == {"weight_plus_2": "0", "weight_plus_1": "0", "first_discriminating_metric_depth": 2}, "oscillatory current filtration changed")
    coefficient, coefficient_local = _zero_shell_current_coefficient(current["sphere_integrated_slice_current"])
    expected_coefficient = sp.sympify(filtration["zero_shell_first_XX_coefficient"], locals=coefficient_local)
    _require(sp.cancel(coefficient - expected_coefficient) == 0, "zero-shell leading current coefficient changed")

    master = reconstruction["homogeneous_metric_master"]
    _require(master["lambda_zero_power"] == "-3", "homogeneous zero-rate power changed")
    _require(master["oscillatory_power"] == "-4*I*m*omega + 1", "homogeneous oscillatory power changed")
    _require(master["recurrence_diagonal"] == "-2*I*omega*(k - 3)", "homogeneous recurrence changed")
    _require(master["chain_resolution"]["ramification"] is False and master["chain_resolution"]["logarithm"] is False, "homogeneous chain resolution changed")
    reach = reconstruction["conformal_radical"]["traceless_slice_reachability"]
    _require(reach["log_generalized_pivots"] == ["2*I*omega", "-2*I*omega"], "conformal reachability pivots changed")

    carrier = result["generic_carrier_asymptotics"]
    _require(carrier["lambda_independent"] is True, "carrier powers gained Lambda dependence")
    _require(carrier["right_left_dimensions"] == {"zero": [3, 3], "oscillatory": [3, 3]}, "carrier eigenspace dimensions changed")
    _require(carrier["power_polynomials"]["zero"] == "(sigma + 1)*(sigma + 2)*(sigma + 3)", "zero-rate carrier polynomial changed")
    _require(carrier["slice"]["status"] == "FORMALLY_REACHABLE_CONFORMAL_QUOTIENT_SLICE", "carrier slice reachability lost")
    preflight = result["leading_sourced_lift_preflight"]
    _require(len(preflight["entries"]) == 6, "lift preflight branch count changed")
    _require(preflight["common_representation_denominator"] == "Lambda*(Lambda-2)", "lift denominator changed")
    _require({entry["candidate_metric_power"] for entry in preflight["entries"]} == {"2", "1-4*I*m*omega"}, "candidate lift powers changed")
    pilot = result["bounded_sourced_lift_depth2_pilot"]
    _require(pilot == _load(SOURCED_LIFT_PILOT), "embedded sourced-lift pilot drift")
    solved = {(branch["sector"], branch["branch_index"]): branch for branch in pilot["solved_branches"]}
    _require(set(solved) == {("zero", 0), ("zero", 1), ("zero", 2), ("oscillatory", 1)}, "depth-2 solved branch set changed")
    _require(all(solved[("zero", index)]["log_degree"] == 0 for index in range(3)), "zero depth-2 log degree changed")
    _require(solved[("oscillatory", 1)]["log_degree"] == 1, "oscillatory depth-2 log degree changed")
    _require(pilot["solution_denominator_factors"] == ["Lambda", "Lambda - 2"], "pilot solution denominator ledger changed")
    _require(pilot["rref_pivot_denominator_audit"].startswith("NOT_EXPOSED"), "pivot-wall uncertainty was silently promoted")
    _require({(entry["branch_index"], entry["bound_seconds"]) for entry in pilot["bounded_nonresults"]} == {(0, 180), (2, 180)}, "bounded nonresult ledger changed")

    gate = payload["downstream_gate"]
    _require(gate["first_missing_object"] == "SYMBOLIC_LAMBDA_SOURCED_POLAR_METRIC_JETS_WITH_ALL_SEVEN_CONSTRAINTS", "missing-object identity changed")
    _require(gate["disposition"] == "SHORTFALL_AFTER_LITERAL_CURRENT_AND_BRANCH_PREFLIGHT", "downstream disposition changed")
    _require(gate["change_of_splitting"]["XX_prime"] == "XX+T_dagger*EX+XE*T+T_dagger*EE*T", "splitting law changed")
    _require(gate["exact_domain_witness"]["cross_nonzero_certified"] is True, "cross witness lost")
    _require("a nonterminating symbolic run" in gate["not_used_as_obstruction"], "timeout boundary lost")
    _require(gate["exact_depth_requirements"]["oscillatory_branches_by_j"] == {"1": 3, "2": 4, "3": 5}, "oscillatory depth ledger changed")
    _require(gate["exact_depth_requirements"]["worst_case"].endswith("carrier depth 9"), "worst-case depth ledger changed")

    flags = payload["claim_flags"]
    for key in ("generic_polar_tensor_harmonics_certified", "generic_polar_bianchi_cascade_certified", "generic_polar_curvature_carrier_certified", "generic_polar_operator_rows_certified", "generic_polar_metric_reconstruction_certified", "generic_polar_conformal_quotient_certified", "generic_polar_literal_current_certified", "generic_polar_depth2_branch_pilot_certified"):
        _require(flags[key] is True, f"established flag lost: {key}")
    for key in (
        "generic_polar_route_B_identity_certified",
        "generic_polar_EE_EX_XX_table_certified",
        "parity_complete_selection_theorem_certified",
        "axial_theorem_modified",
        "ell2_promoted_to_generic",
        "exponent_only_result",
        "timeout_called_obstruction",
    ):
        _require(flags[key] is False, f"forbidden promotion: {key}")
    _require(payload["next_gate"]["disposition"] == "SHORTFALL", "terminal disposition changed")


def verify_atlas(payload: dict[str, Any]) -> None:
    atlas = _load(ATLAS)
    _require(len(atlas["entries"]) == 1, "atlas entry count changed")
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE), "atlas certificate hash drift")
    _require(atlas["schema"] == "pure-weyl-residual-atlas-fragment-v1", "atlas schema changed")
    _require(entry["descriptions"]["symplectic"] == "CERTIFIED", "atlas current status changed")
    _require(entry["mode_data"]["lee_wald"]["status"] == "CERTIFIED", "atlas literal current demoted")
    _require("EE/EX/XX table is open" in entry["mode_data"]["lee_wald"]["statement"], "atlas branch table promotion")
    _require(entry["mode_data"]["resonance"]["status"] == "OPEN", "atlas pivot-wall uncertainty lost")


def mutated(payload: dict[str, Any], path: tuple[Any, ...], value: Any) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    cursor: Any = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return result


def main() -> int:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    verify_atlas(payload)
    print("independent generic-l polar disposition verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
