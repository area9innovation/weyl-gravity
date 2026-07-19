#!/usr/bin/env python3
"""Independent replay of the generic physical-Hessian linear layer."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-linear-curvature-v1.schema.json"


EXPECTED = {
    "V_rho_sigma": [
        ("V01", Fraction(-2, 3), "R delta_sym(mu,nu;alpha,beta) g^(rho,sigma)", "R", 0, 2, False),
        ("V02", Fraction(4, 3), "R g_(nu,beta) delta_sym(mu,alpha;rho,sigma)", "R", 0, 2, False),
        ("V03", Fraction(4, 3), "Ric_(alpha,beta) delta_sym(mu,nu;rho,sigma)", "Ric", 0, 2, True),
        ("V04", Fraction(4, 3), "Ric_(mu,nu) delta_sym(alpha,beta;rho,sigma)", "Ric", 0, 2, True),
        ("V05", Fraction(2), "Ric_(mu,alpha) delta_sym(nu,beta;rho,sigma)", "Ric", 0, 2, True),
        ("V06", Fraction(-4), "Ric_mu^rho g_(nu,beta) delta_alpha^sigma", "Ric", 0, 2, True),
        ("V07", Fraction(-4), "Ric_alpha^rho g_(nu,beta) delta_mu^sigma", "Ric", 0, 2, True),
        ("V08", Fraction(4), "Riem_(mu,alpha,nu,beta) g^(rho,sigma)", "Riem", 0, 2, True),
        ("V09", Fraction(2), "delta_sym(mu,nu;alpha,beta) Ric^(rho,sigma)", "Ric", 0, 2, True),
    ],
    "N_lambda": [
        ("N01", Fraction(1, 3), "delta_sym(mu,nu;alpha,beta) d^lambda R", "R", 1, 1, False),
        ("N02", Fraction(-4, 3), "d_mu Ric_(alpha,beta) delta_nu^lambda", "Ric", 1, 1, True),
        ("N03", Fraction(-2, 3), "d_alpha R g_(nu,beta) delta_mu^lambda", "R", 1, 1, False),
        ("N04", Fraction(-2), "d_mu Ric_(nu,beta) delta_alpha^lambda", "Ric", 1, 1, True),
        ("N05", Fraction(4), "d_alpha Ric_(mu,nu) delta_beta^lambda", "Ric", 1, 1, True),
        ("N06", Fraction(4), "d_alpha Ric_(mu,beta) delta_nu^lambda", "Ric", 1, 1, True),
        ("N07", Fraction(-4), "d_alpha Ric_mu^lambda g_(nu,beta)", "Ric", 1, 1, True),
        ("N08", Fraction(4), "d^lambda Riem_(mu,alpha,nu,beta)", "Riem", 1, 1, True),
    ],
    "U": [
        ("U01", Fraction(-1, 3), "delta_sym(mu,nu;alpha,beta) Box R", "R", 2, 0, False),
        ("U02", Fraction(-4, 3), "d_mu d_alpha R g_(nu,beta)", "R", 2, 0, False),
        ("U03", Fraction(4, 3), "d_mu d_nu Ric_(alpha,beta)", "Ric", 2, 0, True),
        ("U04", Fraction(2), "Box Ric_(mu,alpha) g_(nu,beta)", "Ric", 2, 0, True),
        ("U05", Fraction(2), "Box Riem_(mu,alpha,nu,beta)", "Riem", 2, 0, True),
    ],
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _canonical_digest(rows: dict[str, Any]) -> str:
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    source = stored["source_provenance"]
    if source["decompressed_tex_sha256"] != "7d8f044fbbc166ff67f4ff4258d6db5ff56d078a3c58884b9201e29d5b0ad118":
        raise ValueError("physical-Hessian source TeX digest drifted")
    if source["source_archive_sha256"] != "b77f6e6f2ad8ed324b5145824bee885f55348d5718ab47de4f07441deb188185":
        raise ValueError("physical-Hessian source archive digest drifted")

    rows = stored["source_operator"]["coefficient_rows"]
    for block_name, expected in EXPECTED.items():
        actual = rows[block_name]
        if len(actual) != len(expected):
            raise ValueError(f"{block_name} term count drifted")
        for term, reference in zip(actual, expected, strict=True):
            term_id, coefficient, seed, atom, background_derivatives, operator_derivatives, survives = reference
            replay = (
                term["term_id"],
                _fraction(term["coefficient"]),
                term["seed"],
                term["curvature_atom"],
                term["background_derivatives"],
                term["operator_derivatives"],
                term["scalar_flat_survives"],
            )
            if replay != reference or term["total_engineering_order"] != 4:
                raise ValueError(f"physical-Hessian source row drifted: {term_id}")
    if stored["source_operator"]["formula_digest"] != _canonical_digest(rows):
        raise ValueError("physical-Hessian formula digest drifted")

    gauge = stored["gauge_crosswalk"]
    if (
        _fraction(gauge["source_parameters"]["gamma1"]) != Fraction(1, 2)
        or _fraction(gauge["source_parameters"]["gamma2"]) != Fraction(-1, 6)
        or _fraction(gauge["source_parameters"]["tau"]) != Fraction(-1, 4)
        or gauge["same_gauge"] is not True
    ):
        raise ValueError("same-gauge physical-Hessian crosswalk drifted")

    projector = stored["traceless_projector"]
    matrix = [[_fraction(entry) for entry in row] for row in projector["matrix_in_symmetric_component_basis"]]
    if _multiply(matrix, matrix) != matrix or sum(matrix[i][i] for i in range(10)) != 9:
        raise ValueError("independent traceless-projector replay failed")

    scalar_flat = stored["scalar_flat_restriction"]
    counts = {
        block: sum(bool(term["scalar_flat_survives"]) for term in terms)
        for block, terms in rows.items()
    }
    if counts != scalar_flat["surviving_term_counts"] or counts != {"V_rho_sigma": 7, "N_lambda": 6, "U": 3}:
        raise ValueError("scalar-flat physical-Hessian restriction drifted")

    round_s4 = stored["round_S4_linear_crosscheck"]
    direct = {name: _fraction(value) for name, value in round_s4["direct_K_Box_rows"].items()}
    if direct != {
        "V01_scalar_curvature": Fraction(-8),
        "V08_Riemann_on_traceless_tensor": Fraction(-4),
        "V09_Ricci_derivative_metric": Fraction(6),
    } or sum(direct.values()) != -6:
        raise ValueError("round-S4 linear physical-Hessian replay failed")
    normalization = stored["repository_normalization"]
    if (
        _fraction(normalization["source_quadratic_prefactor"]) != Fraction(1, 4)
        or _fraction(normalization["flat_TT_leading_coefficient"]) != Fraction(1, 2)
        or normalization["repository_functional_Hessian"] != "H_repository=(1/2)H_source"
    ):
        raise ValueError("repository physical-Hessian normalization drifted")

    flags = stored["claim_flags"]
    positive = [name for name, enabled in flags.items() if enabled]
    if positive != [
        "LINEAR_CURVATURE_V_N_U_IMPORTED",
        "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY",
        "REPOSITORY_FUNCTIONAL_HESSIAN_NORMALIZED",
        "ROUND_S4_LINEAR_LAYER_CROSSCHECKED",
        "SAME_GAUGE_CROSSWALK_CERTIFIED",
        "SCALAR_FLAT_FIRST_CURVATURE_INSERTION_COMPLETE",
        "TRACELESS_PROJECTOR_CERTIFIED",
    ]:
        raise ValueError("generic physical-Hessian claim boundary drifted")
    if stored["third_curvature_applicability"]["status"] != "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY":
        raise ValueError("physical n3 activation gate drifted")
    if stored["negative_controls"]["full_Hessian_promotion"]["rejected"] is not True:
        raise ValueError("full-Hessian negative control drifted")

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise ValueError(f"physical-Hessian dependency drifted: {reference['path']}")
    return stored


def main() -> int:
    verify()
    print("independent generic physical-Hessian linear-curvature replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
