#!/usr/bin/env python3
"""Import the exact CPT-III/IV universal kernels for the five pure-gravity rows.

The result is deliberately split in two.  The Barvinsky--Vilkovisky
rank-one minimal scalar-Laplacian fixture is coefficient-bearing and exact.
The repository conformal-graviton determinant is not identified with that
fixture: its generic-background bundle endomorphism/connection trace map is
not yet available.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json"
SCHEMA = HERE / "schema/cpt-universal-third-curvature-kernels-v1.schema.json"
DEPENDENCIES = {
    "carrier_manifest": HERE
    / "certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "repository_multiplicity_ledger": ROOT
    / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "repository_elliptic_complex": ROOT
    / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "repository_local_coefficients": ROOT
    / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
}

a1, a2, a3, d1, d2, d3 = sp.symbols("a1 a2 a3 d1 d2 d3", nonzero=True)
L12, L13, L23 = sp.symbols("L12 L13 L23")
ALPHAS = (a1, a2, a3)
BOXES = (d1, d2, d3)
LOG_KERNELS = {(1, 2): L12, (1, 3): L13, (2, 3): L23}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _canonical(expr: sp.Expr) -> str:
    return sp.sstr(sp.factor_terms(sp.cancel(expr)))


def _groups() -> dict[str, tuple[tuple[int, int, int], ...]]:
    return {
        "S3": tuple(itertools.permutations((1, 2, 3))),
        "S2_23": ((1, 2, 3), (1, 3, 2)),
        "S2_12": ((1, 2, 3), (2, 1, 3)),
        "C3": ((1, 2, 3), (2, 3, 1), (3, 1, 2)),
    }


def _permute(expr: sp.Expr, permutation: tuple[int, int, int]) -> sp.Expr:
    replacements: dict[sp.Expr, sp.Expr] = {}
    for old, new in enumerate(permutation, start=1):
        replacements[ALPHAS[old - 1]] = ALPHAS[new - 1]
        replacements[BOXES[old - 1]] = BOXES[new - 1]
    for (left, right), symbol in LOG_KERNELS.items():
        image = tuple(sorted((permutation[left - 1], permutation[right - 1])))
        replacements[symbol] = LOG_KERNELS[image]
    return sp.cancel(expr.xreplace(replacements))


def _average(expr: sp.Expr, group: Iterable[tuple[int, int, int]]) -> sp.Expr:
    group_tuple = tuple(group)
    return sp.cancel(sum((_permute(expr, p) for p in group_tuple), sp.S.Zero) / len(group_tuple))


def _raw_kernels() -> dict[str, dict[str, Any]]:
    return {
        "I10": {
            "source_structure": 10,
            "derivative_order": 0,
            "stabilizer": "S3",
            "dff": a1 * a2 * a3 / 3,
            "tree": sp.Rational(1, 270) / d3 - d1 / (540 * d2 * d3),
            "logs": sp.S.Zero,
        },
        "I24": {
            "source_structure": 24,
            "derivative_order": 2,
            "stabilizer": "S2_23",
            "dff": (
                -2 * a1 / 45 + a1 * a2 / 45 + a1 * a3 / 45
            )
            / d1
            + (
                -5 * a2 / 54
                - 23 * a1 * a2 / 270
                + 2 * a1**2 * a2 / 5
                - 4 * a1**3 * a2 / 15
                + a2**2 / 270
                + 13 * a2 * a3 / 270
                - a1 * a2 * a3 / 5
                + 4 * a1 * a2 * a3**2 / 15
            )
            / d2,
            "tree": sp.Rational(1, 540) / (d2 * d3),
            "logs": -L23 / (30 * d1),
        },
        "I25": {
            "source_structure": 25,
            "derivative_order": 2,
            "stabilizer": "S2_23",
            "dff": (
                -13 * a1 / 135
                - 56 * a1 * a2 / 135
                + 28 * a1 * a2**2 / 45
                + 32 * a1**2 * a2**2 / 45
                + 16 * a1 * a2**2 * a3 / 15
            )
            / d1
            + (
                -8 * a3 / 45
                - 37 * a1 * a3 / 135
                + 16 * a1**3 * a3 / 45
                + 11 * a2 * a3 / 135
                + 28 * a1 * a2 * a3 / 45
                - 4 * a2**2 * a3 / 45
                - 16 * a1 * a2**2 * a3 / 45
                + a3**2 / 135
                + 32 * a1 * a3**2 / 45
                - 16 * a1**2 * a3**2 / 45
                - 32 * a1 * a2 * a3**2 / 45
                + 16 * a2**2 * a3**2 / 45
            )
            / d3,
            "tree": -sp.Rational(1, 135) / (d1 * d3)
            + sp.Rational(1, 270) / (d2 * d3),
            "logs": -2 * L12 / (15 * d3),
        },
        "I28": {
            "source_structure": 28,
            "derivative_order": 4,
            "stabilizer": "S2_12",
            "dff": 8 * a1**2 * a2**2 * a3 / (3 * d1 * d2),
            "tree": sp.Rational(1, 135) / (d1 * d2 * d3),
            "logs": sp.S.Zero,
        },
        "I29": {
            "source_structure": 29,
            "derivative_order": 6,
            "stabilizer": "C3",
            "dff": 8 * a1**2 * a2**2 * a3**2 / (3 * d1 * d2 * d3),
            "tree": sp.S.Zero,
            "logs": sp.S.Zero,
        },
    }


def _scaled(expr: sp.Expr, scale: sp.Symbol) -> sp.Expr:
    substitutions = {box: scale * box for box in BOXES}
    substitutions.update({symbol: symbol / scale for symbol in LOG_KERNELS.values()})
    return sp.cancel(expr.xreplace(substitutions))


def _validate_kernel_math(kernels: dict[str, dict[str, Any]]) -> None:
    t = sp.symbols("t", nonzero=True)
    groups = _groups()
    for carrier_id, row in kernels.items():
        derivative_order = int(row["derivative_order"])
        group = groups[str(row["stabilizer"])]
        dff = sp.cancel(row["dff"])
        explicit = sp.cancel(row["tree"] + row["logs"])
        expected_dff_degree = -derivative_order // 2
        expected_gamma_degree = -(1 + derivative_order // 2)
        if sp.simplify(_scaled(dff, t) - t**expected_dff_degree * dff) != 0:
            raise ValueError(f"{carrier_id} alpha numerator has wrong box homogeneity")
        if sp.simplify(_scaled(explicit, t) - t**expected_gamma_degree * explicit) != 0:
            raise ValueError(f"{carrier_id} explicit term has wrong box homogeneity")
        sym_dff = _average(dff, group)
        sym_explicit = _average(explicit, group)
        for permutation in group:
            if sp.simplify(_permute(sym_dff, permutation) - sym_dff) != 0:
                raise ValueError(f"{carrier_id} alpha symmetrizer failed")
            if sp.simplify(_permute(sym_explicit, permutation) - sym_explicit) != 0:
                raise ValueError(f"{carrier_id} explicit symmetrizer failed")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    manifest = values["carrier_manifest"]
    ledger = values["repository_multiplicity_ledger"]
    elliptic = values["repository_elliptic_complex"]
    coefficients = values["repository_local_coefficients"]
    kernels = _raw_kernels()
    _validate_kernel_math(kernels)

    manifest_ids = [row["carrier_id"] for row in manifest["carrier_manifest"]]
    if manifest_ids != list(kernels):
        raise ValueError("CPT kernel carriers drifted from the certified manifest")
    if (
        ledger.get("analytic_route") != "EUCLIDEAN_ELLIPTIC"
        or elliptic.get("result_state")
        != "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC"
        or coefficients.get("coefficient_result", {}).get("coefficients", {}).get("C2")
        != {"numerator": 199, "denominator": 30}
    ):
        raise ValueError("repository Euclidean dependencies drifted")

    groups = _groups()
    rows: list[dict[str, Any]] = []
    for carrier_id, row in kernels.items():
        group = groups[row["stabilizer"]]
        dff = sp.cancel(row["dff"])
        explicit = sp.cancel(row["tree"] + row["logs"])
        sym_dff = _average(dff, group)
        sym_explicit = _average(explicit, group)
        derivative_order = int(row["derivative_order"])
        rows.append(
            {
                "carrier_id": carrier_id,
                "source_structure": row["source_structure"],
                "stabilizer": row["stabilizer"],
                "stabilizer_order": len(group),
                "explicit_derivative_order": derivative_order,
                "gamma_box_homogeneity": -(1 + derivative_order // 2),
                "raw_alpha_numerator_dff": _canonical(dff),
                "raw_tree_term": _canonical(row["tree"]),
                "raw_log_term": _canonical(row["logs"]),
                "symmetrized_alpha_numerator_dff": _canonical(sym_dff),
                "symmetrized_explicit_term": _canonical(sym_explicit),
                "source_formula": "Gamma_i=<dff_i/(-Omega)>_3+tree_i+log_i",
                "kernel_status": "EXACT_UNIVERSAL_MINIMAL_LAPLACE_KERNEL_IMPORTED",
                "repository_coefficient_status": "NOT_COMPUTED",
            }
        )

    formula_digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-cpt-universal-third-curvature-kernels-v1",
        "result_id": "CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS",
        "result_state": "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED_REPOSITORY_CONFORMAL_GRAVITON_TRACE_SUBSTITUTION_OPEN",
        "lifecycle_state": "COEFFICIENT_COMPUTED_SOURCE_FIXTURE_ONLY",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": coefficients["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "noncompact asymptotically flat scalar-flat representative, modulo total derivatives and O(curvature^4)",
            "source_operator": "minimal second-order Laplace-type operator; rank-one scalar fixture sets P=0 and bundle curvature=0",
            "repository_target": "strict pure-Weyl full-BV one-loop determinant on a generic off-shell scalar-flat background",
        },
        "kernel_convention": {
            "omega": "Omega=a2*a3*d1+a1*a3*d2+a1*a2*d3",
            "simplex_average": "<P/(-Omega)>_3=int_{a_i>=0} da1 da2 da3 delta(1-a1-a2-a3) P/(-Omega)",
            "log_kernel": "Lij=log(di/dj)/(di-dj)=Lji",
            "source_effective_action_normalization": "-W=[2(4*pi)^2]^(-1) int sqrt(g) tr sum_i Gamma_i Re_i",
            "boxes": "di=Box_i acts on the labelled curvature i",
            "symmetrization": "each raw Gamma_i is averaged over the certified stabilizer of its carrier before it is used independently",
        },
        "universal_kernels": rows,
        "formula_digest": formula_digest,
        "source_fixture": {
            "operator": "F=-Box on one real scalar, P=0, bundle curvature=0",
            "bundle_rank": 1,
            "result": "the five symmetrized Gamma_i above are the complete pure-gravity third-curvature functions for this source fixture",
            "status": "COEFFICIENT_COMPUTED",
            "claim_boundary": "This fixture validates the exact kernels and their normalization; it is not the Weyl-graviton determinant.",
        },
        "repository_matching_audit": {
            "special_background_data_available": [
                "round-S4 constrained determinant factors and multiplicities",
                "Ricci-flat local b4 coefficient match",
                "generic principal-symbol elliptic sequence",
            ],
            "why_rank_sum_is_invalid": "for tensor and ghost bundles, P and bundle connection curvature are themselves linear in background curvature and their CPT rows feed the same pure-gravity carrier functions; constrained Einstein-background ranks do not determine those trace substitutions",
            "functional_nonidentifiability": "the available fixtures determine finitely many local b4 coordinates, whereas the target consists of five three-variable functions modulo one symmetric 4D relation",
            "minimal_missing_physical_import": "a same-gauge generic-background full-BV Hessian reduced either to minimal Laplace-type blocks with complete tr(1,P,P^2,P^3,Rcal^2,Rcal^3,...) substitution maps through curvature order three, or a direct nonminimal fourth-order covariant-perturbation kernel, together with the matching generic-background measure",
            "verdict": "NO_REPOSITORY_FORM_FACTOR_COEFFICIENT_CAN_BE_INFERRED_FROM_THE_CURRENT_SPECIAL_BACKGROUND_LEDGER",
        },
        "claim_flags": {
            "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED": True,
            "SOURCE_SCALAR_FIXTURE_COEFFICIENTS_COMPUTED": True,
            "KERNEL_STABILIZERS_EXACTLY_VERIFIED": True,
            "KERNEL_HOMOGENEITIES_EXACTLY_VERIFIED": True,
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED": False,
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "source_provenance": {
            "title": "Covariant perturbation theory. IV. Third order in the curvature",
            "authors": ["A. O. Barvinsky", "Yu. V. Gusev", "V. V. Zhytnikov", "G. A. Vilkovisky"],
            "arxiv": "0911.1168",
            "url": "https://arxiv.org/abs/0911.1168",
            "source_archive_sha256": "0b6f1f693d56390b00bd19a583cc1edb695330ee128c1dbdbbc727ad554357a4",
            "ancillary_file": "anc/ffwa.m",
            "ancillary_file_sha256": "6a9bc97cab8793aeda563513f6d0bf6ad20b387a4f52c9e1d76d7e9c27bdbd5f",
            "formula_locations": ["section 7, equations (7.11), (7.25), (7.26), (7.29), (7.30)", "anc/ffwa.m structures 10,24,25,28,29"],
            "use": "exact alpha-representation, tree terms, logarithmic kernels, symmetries, and source normalization",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "GENERIC_BACKGROUND_FULL_BV_HESSIAN_TRACE_SUBSTITUTION_INTO_THE_FIVE_CPT_KERNELS_AND_PARITY_ODD_DERIVATIVE_MANIFEST",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate imports, in exact rational alpha form, the five universal pure-gravity third-curvature kernels Gamma_10, Gamma_24, Gamma_25, Gamma_28 and Gamma_29 from the primary CPT ancillary source. It independently checks their box homogeneity and the S3, S2_23, S2_23, S2_12 and C3 stabilizer projections. For the rank-one minimal scalar Laplacian with P and bundle curvature zero, these are coefficient-bearing form factors in the source normalization. They are not the repository conformal-graviton functions: tensor-bundle endomorphism and connection-curvature rows contribute after the generic-background full-BV Hessian is substituted, while the current repository determinant ledger is fixed only on special Einstein/Ricci-flat carriers plus a principal-symbol elliptic complex. The exact nonidentifiability audit therefore forbids a rank-only promotion. This result does not compute any of the five repository functions or coefficients, classify the parity-odd derivative sector, fix finite C2 or absolute dressed Rhat2 normalizations, supply complete Gamma1 or Q1, construct renormalized products, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, scattering, positivity or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if any(
        flags[name]
        for name in (
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED",
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED",
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED",
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE",
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "RESIDUAL_TRANSFER_AUTHORIZED",
            "LORENTZIAN_CERTIFIED",
        )
    ):
        raise ValueError("universal CPT kernel import crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale CPT universal-kernel certificate: {OUTPUT}")
    print("CPT UNIVERSAL KERNELS: FIVE IMPORTED; REPOSITORY TRACE SUBSTITUTION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
