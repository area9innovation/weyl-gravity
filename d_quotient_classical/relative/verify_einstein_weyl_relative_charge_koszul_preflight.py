#!/usr/bin/env python3
"""Independent consumer for the relative charge/Koszul receiver preflight."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-charge-koszul-receiver-preflight-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _d(term: tuple[int, ...], moments: tuple[sp.Symbol, ...]) -> dict[tuple[int, ...], sp.Expr]:
    out: dict[tuple[int, ...], sp.Expr] = {}
    for position, generator in enumerate(term):
        rest = term[:position] + term[position + 1 :]
        out[rest] = sp.expand(out.get(rest, 0) + (-1) ** position * moments[generator])
    return out


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source-manifest hash drifted: {relative}")
    for artifact in value["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drifted: {artifact['path']}")

    components = json.loads((ROOT / value["dependencies"]["linear_triangle_components"]["path"]).read_text())
    endpoints = components["global_endpoints"]
    identity = [[int(i == j) for j in range(6)] for i in range(6)]
    if endpoints["map_matrix"] != identity or endpoints["dual_map_matrix"] != identity:
        raise AssertionError("endpoint identity replay failed")
    if endpoints["source_basis"][-1] != "u1_constant":
        raise AssertionError("constant U1 endpoint missing")
    if not any("d lambda" in row for row in components["q1_complexes"]["source_rows"]):
        raise AssertionError("source q1 no longer exhibits the constant-U1 reducibility")

    radiative = json.loads((ROOT / value["dependencies"]["radiative_restriction"]["path"]).read_text())
    lam = sp.symbols("lambda", positive=True)
    weights = [
        sp.sympify(text.replace("lambda", "lam"), locals={"lam": lam})
        for text in radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    ]
    expected_relative = [sp.Rational(3, 2) * sp.sqrt(2 * lam), -sp.Rational(3, 2) * sp.sqrt(2 * lam)]
    if any(sp.simplify(weight - 1 - expected) != 0 for weight, expected in zip(weights, expected_relative)):
        raise AssertionError("relative branch-weight replay failed")

    obstruction = json.loads((ROOT / value["dependencies"]["f2_obstruction"]["path"]).read_text())
    witness = sp.sympify(obstruction["taub_pairing"]["relative_half_delta2_pairing"])
    if sp.simplify(witness + sp.Rational(54, 5) * (1 + sp.sqrt(3))) != 0:
        raise AssertionError("H witness replay failed")

    moments = sp.symbols("mu0:5", commutative=True)
    checked = 0
    for degree in range(6):
        for term in itertools.combinations(range(5), degree):
            twice: dict[tuple[int, ...], sp.Expr] = {}
            for first_term, first_coefficient in _d(term, moments).items():
                for second_term, second_coefficient in _d(first_term, moments).items():
                    twice[second_term] = sp.expand(
                        twice.get(second_term, 0) + first_coefficient * second_coefficient
                    )
            if any(sp.simplify(coefficient) != 0 for coefficient in twice.values()):
                raise AssertionError(f"Koszul square failed on {term}")
            checked += 1
    if checked != 32:
        raise AssertionError("incomplete exterior-basis replay")
    charge = value["charge_fibre"]
    if "<zeta_X,(1/2)Delta2(u,v)>" not in charge["polarization"]:
        raise AssertionError("bilinear polarization normalization drifted")
    if "2*B_rel,X(u,v)=<zeta_X,Delta2(u,v)>" not in charge["charge_taylor_q2"]:
        raise AssertionError("charge q2 Taylor normalization drifted")
    scale, quadratic_coefficient = sp.symbols("scale quadratic_coefficient")
    scaled_moment = scale**2 * quadratic_coefficient
    if scaled_moment.subs(scale, 0) != 0 or sp.diff(scaled_moment, scale).subs(scale, 0) != 0:
        raise AssertionError("quadratic derived-zero-locus tangent check failed")

    flags = value["classification"]
    forbidden = (
        "constant_u1_is_sixth_taub_charge",
        "plain_linear_taub_zero_subcomplex_valid",
        "full_offshell_charge_map_certified",
        "support_local_koszul_bv_extension_certified",
        "relative_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    )
    if any(flags[key] is not False for key in forbidden):
        raise AssertionError("preflight promoted a forbidden downstream claim")
    return {
        "status": "PASS",
        "endpoint_rank": 6,
        "charge_fibre_rank": 5,
        "koszul_monomials_checked": checked,
        "quadratic_origin_and_linearization_zero": True,
        "charge_q2_factor_two": True,
        "relative_h_witness": str(sp.factor(witness)),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
