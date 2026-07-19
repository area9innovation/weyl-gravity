#!/usr/bin/env python3
"""Certify the compact-product relative f2 Taub obstruction.

The strict arity-two defect is evaluated on the certified periodic ell=2
Einstein--Maxwell plus mode.  Its constant-lapse pairing is then reconstructed
from the exact Weyl/Einstein radiative current ratio and the covariant
moment-map--Taub identity.  A nonzero pairing with the target adjoint class
rules out every f2 whose value lies in the declared smooth fixed-bundle target
correction domain.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-f2-taub-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-f2-taub-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_f2_taub_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_f2_taub_obstruction.py"

DEPENDENCIES = {
    "strict_delta2_certificate": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json",
    "strict_delta2_payload": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_arity_two_defect_v1/delta2.json",
    "linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "linear_triangle_components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "periodic_graviton": ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json",
    "radiative_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "relative_solution_form": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "moment_map_taub_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "target_adjoint_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json",
    "fixed_bundle_domain": ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _s(value: sp.Expr) -> str:
    return str(sp.factor(sp.radsimp(sp.simplify(value))))


def _mode_point_evaluation(payload: dict, mode: dict) -> dict:
    source_index = {row["row_id"]: index for index, row in enumerate(payload["source_rows"])}
    target_rows = payload["target_rows"]
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    root = sp.sqrt(3)
    omega = sp.sqrt(6 + 2 * root)
    harmonic = (3 * sp.cos(theta) ** 2 - 1) / 2
    fields = {
        source_index["g_13"]: 3 * sp.cos(omega * time) * sp.sin(theta) ** 2 * sp.cos(theta),
        source_index["A_1"]: root * sp.cos(omega * time) * harmonic,
    }
    coordinates = (time, space, theta, azimuth)
    point = {time: 0, space: 0, theta: sp.pi / 2, azimuth: 0}
    jets: dict[tuple[int, tuple[int, ...]], sp.Expr] = {}

    def jet(row: int, word: list[int]) -> sp.Expr:
        key = (row, tuple(word))
        if key not in jets:
            expression = fields.get(row, sp.S.Zero)
            for axis in word:
                expression = sp.diff(expression, coordinates[axis])
            jets[key] = sp.simplify(expression.subs(point))
        return jets[key]

    values: dict[int, sp.Expr] = {}
    for term in payload["content"]["terms"]:
        left, right = term["inputs"]
        contribution = (
            sp.Rational(term["coefficient"])
            * jet(left["row"], left["word"])
            * jet(right["row"], right["word"])
        )
        if contribution:
            output = term["output_row"]
            values[output] = sp.simplify(values.get(output, sp.S.Zero) + contribution)

    nonzero = {
        target_rows[index]["row_id"]: value
        for index, value in values.items()
        if sp.simplify(value) != 0
    }
    expected_rows = {"g_00_star", "g_11_star", "g_22_star", "g_33_star"}
    if set(nonzero) != expected_rows:
        raise AssertionError(f"unexpected nonzero point rows: {sorted(nonzero)}")

    theta_symbol = sp.symbols("theta", real=True)
    chevreton = mode["chevreton_second_order_time_zero"]["tensor_matrix"]
    diagonal = {
        f"g_{axis}{axis}_star": sp.sympify(
            chevreton[axis][axis], locals={"theta": theta_symbol}
        ).subs(theta_symbol, sp.pi / 2)
        for axis in range(4)
    }
    ratios = {
        row: sp.simplify(nonzero[row] / diagonal[row]) for row in expected_rows
    }
    if set(ratios.values()) != {-sp.Rational(3, 2)}:
        raise AssertionError(f"Delta2/Chevreton normalization drifted: {ratios}")
    return {
        "fixture": "ell=2,m=0,k=0 axial Einstein-Maxwell plus branch",
        "base_point": "t=0, theta=pi/2 in the frozen product-coordinate PBW frame",
        "input_rows": ["g_13", "A_1"],
        "nonzero_delta2_rows": {row: _s(nonzero[row]) for row in sorted(nonzero)},
        "chevreton_rows_at_point": {row: _s(diagonal[row]) for row in sorted(diagonal)},
        "delta2_over_chevreton": "-3/2",
        "all_other_target_rows_zero": True,
        "jet_values_replayed": len(jets),
        "purpose": "local coefficient and sign normalization only; the global obstruction uses the compact Taub/current pairing",
    }


def _exact_obstruction(records: dict[str, dict]) -> dict:
    mode = records["periodic_graviton"]
    radiative = records["radiative_restriction"]
    relative_form = records["relative_solution_form"]
    moment = records["moment_map_taub_bridge"]
    adjoint = records["target_adjoint_witness"]
    domain = records["fixed_bundle_domain"]
    triangle = records["linear_triangle_components"]

    if mode["classification"]["periodic_l2_gravitational_tangent_certified"] is not True:
        raise AssertionError("periodic ell=2 tangent is not certified")
    if any(value != "0" for row in mode["first_order_mode"]["linearized_einstein_residual"] for value in row):
        raise AssertionError("Einstein linear residual drifted")
    if any(value != "0" for value in mode["first_order_mode"]["linearized_maxwell_residual"]):
        raise AssertionError("Maxwell linear residual drifted")
    if moment["classification"]["generic_covariant_moment_map_Taub_equality_certified"] is not True:
        raise AssertionError("moment-map--Taub equality is not certified")
    if relative_form["cyclic_obstruction_theorem"]["solution_pairing_identity"] != "iota^*Omega_WM(u,v)-Omega_EM(u,v)=Omega_EM(u,Dv), D=R-I":
        raise AssertionError("relative solution-form identity drifted")
    if adjoint["classification"]["fixed_bundle_constraint_cokernel_class"] is not True:
        raise AssertionError("target constant-lapse adjoint class is not certified")
    if domain["classification"]["fixed_compact_u1_domain_frozen"] is not True:
        raise AssertionError("fixed compact U(1) domain is not frozen")
    endpoints = triangle["global_endpoints"]
    if endpoints["map_matrix"] != endpoints["dual_map_matrix"] or endpoints["map_matrix"] != [
        [int(i == j) for j in range(6)] for i in range(6)
    ]:
        raise AssertionError("global endpoint map is not the certified identity")

    root = sp.sqrt(3)
    eigenvalue = sp.Integer(6)
    imported_weights = radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    plus_weight = sp.sympify(
        imported_weights[0].replace("lambda", "lam"), locals={"lam": eigenvalue}
    )
    if sp.simplify(plus_weight - (1 + 3 * root)) != 0:
        raise AssertionError("ell=2 plus relative weight drifted")
    mu_w = sp.sympify(mode["adjoint_cokernel_witness"]["normalized_source_pairing_at_t_zero"])
    mu_e = sp.radsimp(mu_w / plus_weight)
    relative = sp.simplify(mu_w - mu_e)
    chevreton_average = sp.sympify(
        mode["chevreton_second_order_time_zero"]["normalized_sphere_average_tt"]
    )
    if sp.simplify(relative - sp.Rational(3, 2) * chevreton_average) != 0:
        raise AssertionError("global relative/Chevreton normalization drifted")
    if relative == 0:
        raise AssertionError("relative Taub pairing unexpectedly vanished")
    return {
        "q2_convention": "q2 is the polarized second action derivative D^2E; the Taub pairing uses (1/2)D^2E",
        "target_moment_map_mu_W": _s(mu_w),
        "radiative_relative_weight_w_plus": _s(plus_weight),
        "derived_source_moment_map_mu_E": _s(mu_e),
        "relative_half_delta2_pairing": _s(relative),
        "chevreton_normalized_sphere_average": _s(chevreton_average),
        "relative_pairing_over_chevreton_average": "3/2",
        "nonzero": True,
        "derivation": [
            "Omega_W restricted to the included plus branch equals w_plus times Omega_E",
            "the certified relative solution form is iota^*Omega_W-Omega_E",
            "the source and target time-translation endpoints map identically",
            "the covariant moment-map--Taub theorem gives mu=(1/2)Omega(u,L_D u)",
            "the endpoint-dual identity and Noether/Taub theorem identify <zeta_H,(1/2)Delta2(u,u)> with mu_W-mu_E",
        ],
    }


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    delta_certificate = records["strict_delta2_certificate"]
    if delta_certificate["result_state"] != "NONZERO_STRICT_ARITY_TWO_DEFECT_F2_SOLVE_REQUIRED":
        raise AssertionError("strict Delta2 input drifted")
    if delta_certificate["defect_payload"]["sha256"] != _sha(DEPENDENCIES["strict_delta2_payload"]):
        raise AssertionError("strict Delta2 payload is not the certified payload")
    triangle = records["linear_triangle"]
    if triangle["acceptance_flags"]["GLOBAL_ENDPOINTS_INCLUDED"] is not True:
        raise AssertionError("relative linear triangle lost its global endpoints")

    point = _mode_point_evaluation(records["strict_delta2_payload"], records["periodic_graviton"])
    obstruction = _exact_obstruction(records)
    source_manifest = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-relative-f2-taub-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "FROZEN_UNARY_RELATIVE_F2_OBSTRUCTED_BY_NONZERO_CONSTANT_LAPSE_CLASS",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1_L x S2",
            "boundaries": "closed Cauchy slice S1_L x S2 before final residual quotient",
            "charge_sector": "fixed compact U(1) bundle P_N with N=2 and fixed second-order charges",
            "carrier": "the frozen support-local 38-to-40-row unary triangle on the full smooth periodic fixed-bundle field domain",
            "degree": "arity-two field correction f2(u,u) in target degree zero",
            "parity": "one certified axial ell=2 source witness",
            "ell": "2",
            "m": "0",
            "k": "0",
            "omega": "omega^2=6+2*sqrt(3), plus branch",
        },
        "dependencies": {
            name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()
        },
        "local_delta2_normalization": point,
        "taub_pairing": obstruction,
        "obstruction_theorem": {
            "f2_equation": "Delta2(u,u)+q1_W f2(u,u)=0 for every source q1_E cocycle u",
            "adjoint_annihilation": "<zeta_H,q1_W v>=0 for every smooth periodic fixed-bundle target correction v, including secular-in-time smooth corrections",
            "witness_pairing": obstruction["relative_half_delta2_pairing"],
            "contradiction": "pairing the f2 equation with zeta_H would force the displayed nonzero relative Taub number to vanish",
            "verdict": "no f2 with values in the declared target correction domain extends the frozen unary map on the full source carrier",
        },
        "classification": {
            "strict_delta2_replayed_on_witness": True,
            "source_mode_is_q1_cocycle": True,
            "target_constant_lapse_annihilates_q1_exact_corrections": True,
            "relative_taub_pairing_nonzero": True,
            "frozen_unary_full_domain_f2_exists": False,
            "support_local_full_domain_f2_exists": False,
            "smooth_periodic_full_domain_f2_exists": False,
            "arity_three_direct_morphism_authorized": False,
            "taub_zero_restricted_source_obstructed": False,
            "relative_cofiber_or_mapping_cone_obstructed": False,
            "modified_unary_or_endpoint_map_obstructed": False,
            "different_background_obstructed": False,
            "causal_or_quantum_claim": False,
        },
        "allowed_repairs": [
            "restrict the source to a declared relative moment-map/Taub-zero derived sector",
            "replace the direct morphism by a relative cofiber or mapping-cone construction carrying the charge class",
            "enlarge the charge fibre or carrier with an explicitly typed noncontractible row",
            "modify the unary or endpoint map and recompute Delta2",
            "port the comparison to a background with a separately certified relative split",
        ],
        "next_gate": "CHOOSE_RELATIVE_TAUB_ZERO_OR_COFIBER_ARCHITECTURE_BEFORE_ARITY_THREE",
        "provenance": {
            "source_manifest": source_manifest,
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_f2_taub_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_f2_taub_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_f2_taub_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-f2-taub-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction applies to the frozen support-local unary Einstein--Weyl triangle on the full smooth periodic fixed-P_N source and target domains. One certified ell=2 plus-branch q1 cocycle has nonzero relative constant-lapse Taub pairing, while the target adjoint class annihilates every q1_W-exact correction in that domain; hence no f2, support-local or otherwise, can extend this f1 there. The theorem does not obstruct restriction to a relative Taub-zero derived source sector, a relative cofiber or mapping cone, a larger charge carrier, a modified unary/endpoint map, another background, causal propagation, observables, particles or quantum states. Arity three is not authorized for the obstructed direct full-domain morphism."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["taub_pairing"]["nonzero"] is not True:
        raise AssertionError("nonzero Taub witness dropped")
    if value["classification"]["frozen_unary_full_domain_f2_exists"] is not False:
        raise AssertionError("obstruction was weakened")


def _report() -> str:
    return r"""# Relative Einstein--Weyl f2 Taub obstruction

The exact strict defect

\[
\Delta_2=q_{2,W}(f_1,f_1)-f_1q_{2,E}
\]

does not admit an (f_2) correction on the full smooth periodic fixed-bundle
carrier of the frozen unary triangle.

For the certified axial (ell=2,m=0,k=0) Einstein--Maxwell plus mode,

\[
\omega^2=6+2\sqrt3,
\qquad
w_+=1+3\sqrt3,
\]

the target Weyl--Maxwell Taub pairing is

\[
\mu_W=-12\sqrt3-\frac{72}{5}.
\]

The exact radiative-current restriction gives

\[
\mu_E=\frac{\mu_W}{w_+}
=-\frac{6}{5}(3+\sqrt3),
\]

and therefore

\[
\left\langle\zeta_H,\frac12\Delta_2(u,u)\right\rangle
=\mu_W-\mu_E
=-\frac{54}{5}(1+\sqrt3)\neq0.
\]

The independently certified constant-lapse target class obeys

\[
\langle\zeta_H,q_{1,W}v\rangle=0
\]

for every smooth periodic correction (v) on the fixed compact (U(1))
bundle, including smooth secular corrections. Pairing the arity-two morphism
equation

\[
\Delta_2(u,u)+q_{1,W}f_2(u,u)=0
\]

with (zeta_H) gives a contradiction.

As a coefficient/sign regression, direct evaluation of the complete 50,854
term PBW defect on this mode at (t=0,\theta=\pi/2) leaves precisely the four
diagonal metric Euler rows and equals (-3/2) times the independently derived
Chevreton tensor there. The global obstruction uses the compact current/Taub
pairing, not that single point.

This is a scoped obstruction to extending the frozen unary map on the full
fixed-bundle carrier. It does not rule out a Taub-zero derived source sector,
a relative cofiber or mapping cone, a larger charge carrier, a modified unary
or endpoint map, or a different background. The direct arity-three morphism
calculation is therefore not authorized; the next architectural choice is
between a relative Taub-zero restriction and a charge-carrying cofiber.
"""


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _guards(value: dict) -> None:
    mutations = (
        ("classification", "frozen_unary_full_domain_f2_exists", True),
        ("classification", "arity_three_direct_morphism_authorized", True),
        ("classification", "taub_zero_restricted_source_obstructed", True),
        ("classification", "causal_or_quantum_claim", True),
        ("taub_pairing", "nonzero", False),
    )
    for section, key, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][key] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted {section}.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
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
            raise AssertionError("relative f2 obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
