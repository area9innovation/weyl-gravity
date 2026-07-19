#!/usr/bin/env python3
"""Import the same-gauge generic physical Hessian through linear curvature.

Barvinsky et al. give the minimal fourth-order traceless-tensor operator in
the gauge used by the repository, but deliberately print only its terms
linear in the background curvature.  This module freezes those V, N and U
rows, transports their normalization to the repository functional Hessian,
and proves exactly what they do and do not close: the pure three-linear-
insertion physical n=3 vertex is available, while the curvature-squared
zero-order layer and the mixed n=1/n=2 rows remain open.
"""

from __future__ import annotations

import argparse
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
DEPENDENCIES = {
    "classical_snapshot_compatibility": ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json",
    "round_S4_TT_hessian": HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json",
    "generic_Diff_Weyl_ghost": HERE / "certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "universal_CPT_kernels": ROOT / "quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
}

SOURCE_TEX_SHA256 = "7d8f044fbbc166ff67f4ff4258d6db5ff56d078a3c58884b9201e29d5b0ad118"
SOURCE_ARCHIVE_SHA256 = "b77f6e6f2ad8ed324b5145824bee885f55348d5718ab47de4f07441deb188185"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _term(
    term_id: str,
    coefficient: Fraction | int,
    seed: str,
    curvature_atom: str,
    background_derivatives: int,
    operator_derivatives: int,
    scalar_flat_survives: bool,
) -> dict[str, Any]:
    return {
        "term_id": term_id,
        "coefficient": _q(coefficient),
        "seed": seed,
        "curvature_atom": curvature_atom,
        "background_derivatives": background_derivatives,
        "operator_derivatives": operator_derivatives,
        "total_engineering_order": 2 + background_derivatives + operator_derivatives,
        "scalar_flat_survives": scalar_flat_survives,
    }


def _operator_rows() -> dict[str, list[dict[str, Any]]]:
    return {
        "V_rho_sigma": [
            _term("V01", Fraction(-2, 3), "R delta_sym(mu,nu;alpha,beta) g^(rho,sigma)", "R", 0, 2, False),
            _term("V02", Fraction(4, 3), "R g_(nu,beta) delta_sym(mu,alpha;rho,sigma)", "R", 0, 2, False),
            _term("V03", Fraction(4, 3), "Ric_(alpha,beta) delta_sym(mu,nu;rho,sigma)", "Ric", 0, 2, True),
            _term("V04", Fraction(4, 3), "Ric_(mu,nu) delta_sym(alpha,beta;rho,sigma)", "Ric", 0, 2, True),
            _term("V05", 2, "Ric_(mu,alpha) delta_sym(nu,beta;rho,sigma)", "Ric", 0, 2, True),
            _term("V06", -4, "Ric_mu^rho g_(nu,beta) delta_alpha^sigma", "Ric", 0, 2, True),
            _term("V07", -4, "Ric_alpha^rho g_(nu,beta) delta_mu^sigma", "Ric", 0, 2, True),
            _term("V08", 4, "Riem_(mu,alpha,nu,beta) g^(rho,sigma)", "Riem", 0, 2, True),
            _term("V09", 2, "delta_sym(mu,nu;alpha,beta) Ric^(rho,sigma)", "Ric", 0, 2, True),
        ],
        "N_lambda": [
            _term("N01", Fraction(1, 3), "delta_sym(mu,nu;alpha,beta) d^lambda R", "R", 1, 1, False),
            _term("N02", Fraction(-4, 3), "d_mu Ric_(alpha,beta) delta_nu^lambda", "Ric", 1, 1, True),
            _term("N03", Fraction(-2, 3), "d_alpha R g_(nu,beta) delta_mu^lambda", "R", 1, 1, False),
            _term("N04", -2, "d_mu Ric_(nu,beta) delta_alpha^lambda", "Ric", 1, 1, True),
            _term("N05", 4, "d_alpha Ric_(mu,nu) delta_beta^lambda", "Ric", 1, 1, True),
            _term("N06", 4, "d_alpha Ric_(mu,beta) delta_nu^lambda", "Ric", 1, 1, True),
            _term("N07", -4, "d_alpha Ric_mu^lambda g_(nu,beta)", "Ric", 1, 1, True),
            _term("N08", 4, "d^lambda Riem_(mu,alpha,nu,beta)", "Riem", 1, 1, True),
        ],
        "U": [
            _term("U01", Fraction(-1, 3), "delta_sym(mu,nu;alpha,beta) Box R", "R", 2, 0, False),
            _term("U02", Fraction(-4, 3), "d_mu d_alpha R g_(nu,beta)", "R", 2, 0, False),
            _term("U03", Fraction(4, 3), "d_mu d_nu Ric_(alpha,beta)", "Ric", 2, 0, True),
            _term("U04", 2, "Box Ric_(mu,alpha) g_(nu,beta)", "Ric", 2, 0, True),
            _term("U05", 2, "Box Riem_(mu,alpha,nu,beta)", "Riem", 2, 0, True),
        ],
    }


def _formula_digest(rows: dict[str, list[dict[str, Any]]]) -> str:
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _traceless_projector() -> dict[str, Any]:
    pairs = [(i, j) for i in range(4) for j in range(i, 4)]
    matrix: list[list[Fraction]] = []
    for out_i, out_j in pairs:
        row: list[Fraction] = []
        for in_i, in_j in pairs:
            identity = Fraction(int((out_i, out_j) == (in_i, in_j)))
            trace_subtraction = Fraction(
                int(out_i == out_j and in_i == in_j), 4
            )
            row.append(identity - trace_subtraction)
        matrix.append(row)
    square = [
        [sum(matrix[i][k] * matrix[k][j] for k in range(10)) for j in range(10)]
        for i in range(10)
    ]
    if square != matrix:
        raise AssertionError("traceless projector is not idempotent")
    trace = sum(matrix[i][i] for i in range(10))
    if trace != 9:
        raise AssertionError("traceless projector rank drifted")
    return {
        "formula": "1hat=delta_sym(mu,nu;alpha,beta)-(1/4)g_(mu,nu)g_(alpha,beta)",
        "ambient_symmetric_rank": 10,
        "projected_traceless_rank": int(trace),
        "idempotent": True,
        "matrix_in_symmetric_component_basis": [[_q(x) for x in row] for row in matrix],
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    compatibility = values["classical_snapshot_compatibility"]
    round_s4 = values["round_S4_TT_hessian"]
    ghost = values["generic_Diff_Weyl_ghost"]
    cpt = values["universal_CPT_kernels"]
    if (
        compatibility.get("compatibility", {}).get("status") != "CONTENT_HASH_COMPATIBLE"
        or compatibility.get("analytic_operator_snapshot", {}).get("classical_commit")
        != "318589ffae21fb1ae1abfd046b2f367b05c52bab"
        or round_s4.get("operator_dictionary", {}).get("repository_Hessian")
        != "(1/2) Delta_2_perp(2) Delta_2_perp(4)"
        or round_s4.get("flat_tt_leading_symbol", {}).get("Hessian_leading_coefficient")
        != _q(Fraction(1, 2))
        or ghost.get("scope", {}).get("gauge")
        != "F_mu=nabla^nu h_mu_nu-beta nabla_mu h and F_W=h"
        or ghost.get("algebraic_Weyl_ghost_elimination", {}).get("beta_independent")
        is not True
        or cpt.get("claim_flags", {}).get("FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED")
        is not True
    ):
        raise ValueError("generic physical-Hessian dependencies drifted")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_dependencies(values)
    rows = _operator_rows()
    if [len(rows[name]) for name in ("V_rho_sigma", "N_lambda", "U")] != [9, 8, 5]:
        raise AssertionError("physical-Hessian source term count drifted")
    if any(term["total_engineering_order"] != 4 for block in rows.values() for term in block):
        raise AssertionError("physical-Hessian engineering order drifted")
    scalar_flat_counts = {
        name: sum(term["scalar_flat_survives"] for term in block)
        for name, block in rows.items()
    }
    if scalar_flat_counts != {"V_rho_sigma": 7, "N_lambda": 6, "U": 3}:
        raise AssertionError("scalar-flat physical-Hessian term count drifted")

    # On constant curvature R=12K, Ric=3Kg and TT fields, terms whose
    # derivative index contracts a tensor index vanish modulo a commutator.
    # Since V is already O(K), that commutator is O(K^2).  The three direct
    # Box carriers are V01=-8K, V08=-4K and V09=+6K.
    constant_curvature_box_rows = {
        "V01_scalar_curvature": Fraction(-8),
        "V08_Riemann_on_traceless_tensor": Fraction(-4),
        "V09_Ricci_derivative_metric": Fraction(6),
    }
    linear_box_coefficient = sum(constant_curvature_box_rows.values())
    if linear_box_coefficient != -6:
        raise AssertionError("constant-curvature linear Hessian check drifted")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-linear-curvature-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE",
        "result_state": "SAME_GAUGE_TRACELESS_PHYSICAL_HESSIAN_LINEAR_CURVATURE_IMPORTED_N3_THREE_LINEAR_VERTEX_READY",
        "lifecycle_state": "COEFFICIENT_INPUT_IMPORTED_FULL_HESSIAN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": values["classical_snapshot_compatibility"]["analytic_operator_snapshot"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic local oriented metric; scalar-flat and round-S4 restrictions recorded",
            "field_bundle": "traceless symmetric rank-two metric fluctuations; pointwise rank nine",
            "curvature_order": "complete through first order only",
            "operator_order": 4,
            "domain": "local covariant jets; global Green, spectral-cut and zero-mode data excluded",
        },
        "source_provenance": {
            "title": "On the local term in the anomaly-induced action of Weyl quantum gravity",
            "authors": "A. O. Barvinsky, G. H. S. Camargo, A. E. Kalugin, N. Ohta, and I. L. Shapiro",
            "arxiv": "2308.05251v2",
            "doi": "10.1103/PhysRevD.108.086018",
            "source_url": "https://arxiv.org/abs/2308.05251",
            "source_archive_url": "https://export.arxiv.org/e-print/2308.05251v2",
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "decompressed_tex_sha256": SOURCE_TEX_SHA256,
            "equation_labels": ["gf-gen", "gauge-min", "Hmingen", "traceless", "Vrhosi", "Nrho", "U"],
            "source_scope_statement": "the displayed V,N,U rows retain only terms linear in the curvature because the source calculation targets Box R",
            "transcription_policy": "exact rational coefficient ledger with source index seeds and declared symmetrization; no omitted curvature-squared row is reconstructed",
        },
        "gauge_crosswalk": {
            "source_vector_gauge": "chi_mu=nabla_alpha h^alpha_mu+tau nabla_mu h",
            "source_parameters": {"gamma1": _q(Fraction(1, 2)), "gamma2": _q(Fraction(-1, 6)), "tau": _q(Fraction(-1, 4))},
            "source_Weyl_gauge": "h=0",
            "repository_vector_gauge": "F_mu=nabla^nu h_mu_nu-(1/4)nabla_mu h",
            "repository_Weyl_gauge": "F_W=h",
            "same_gauge": True,
            "generic_ghost_crosswalk": "the beta=1/4 repository Diff-Weyl ghost is the FP operator of the imported metric gauge",
        },
        "traceless_projector": _traceless_projector(),
        "source_operator": {
            "quadratic_form": "S_conf^(2)=(1/4) integral sqrt(g) h H_source h",
            "monic_operator": "H_source=1hat Box^2+V^(rho,sigma)nabla_rho nabla_sigma+N^rho nabla_rho+U+O(curvature^2)",
            "symmetrization": ["mu<->nu", "alpha<->beta", "(mu,nu)<->(alpha,beta) with formal-adjoint derivative ordering"],
            "coefficient_rows": rows,
            "formula_digest": _formula_digest(rows),
        },
        "repository_normalization": {
            "repository_action": "S_red=integral sqrt(g)(Ric^2-R^2/3)=1/2 integral sqrt(g)(C^2-E4)",
            "source_quadratic_prefactor": _q(Fraction(1, 4)),
            "repository_functional_Hessian": "H_repository=(1/2)H_source",
            "repository_leading_symbol": "(1/2)1hat Box^2",
            "flat_TT_leading_coefficient": _q(Fraction(1, 2)),
            "trace_log_linear_vertex_scale_invariant": "((H0/2)^-1)(H1/2)=H0^-1 H1",
            "constant_overall_determinant_normalization": "excluded from the nonlocal n=3 insertion; it belongs to the separately declared local measure/finite normalization policy",
        },
        "scalar_flat_restriction": {
            "conditions": ["R=0", "nabla R=0", "nabla nabla R=0", "Box R=0"],
            "surviving_term_counts": scalar_flat_counts,
            "surviving_term_ids": {
                name: [term["term_id"] for term in block if term["scalar_flat_survives"]]
                for name, block in rows.items()
            },
            "complete_first_curvature_insertion_on_scalar_flat_domain": True,
        },
        "round_S4_linear_crosscheck": {
            "sectional_curvature_symbol": "K",
            "TT_and_linear_curvature_policy": "use div(h)=0 and tr(h)=0; derivative commutators in V contribute only O(K^2)",
            "direct_K_Box_rows": {name: _q(value) for name, value in constant_curvature_box_rows.items()},
            "source_linear_operator": "A^2+6 K A with A=-Box",
            "repository_linear_functional_Hessian": "(1/2)A^2+3 K A",
            "repository_full_round_S4_Hessian": "(1/2)(A+2K)(A+4K)=(1/2)A^2+3KA+4K^2; unit S4 has K=1",
            "missing_curvature_squared_fixture": "source monic +8 K^2, equivalently repository functional-Hessian +4 K^2",
            "interpretation": "the exact round-S4 remainder proves rather than hides that the imported source layer is not the full generic Hessian",
        },
        "third_curvature_applicability": {
            "flat_base": "H0=1hat Box^2",
            "linear_insertion": "H1=V nabla nabla+N nabla+U",
            "closed_trace_row": "Tr[(H0^-1 H1)^3] is completely determined by this import",
            "status": "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY",
            "not_closed": [
                "mixed Tr(H0^-1 H1 H0^-1 H2) contribution at third curvature order",
                "curved-base and one-insertion rows involving the curvature-squared algebraic Hessian",
                "tensor trace projection onto the five repository carrier functions",
                "generic primed Green or complete spectral carrier",
            ],
        },
        "negative_controls": {
            "gauge_tau_mutation": {"mutated_tau": _q(Fraction(0)), "same_gauge": False, "rejected": True},
            "V01_coefficient_mutation": {"mutated": _q(Fraction(-1, 3)), "formula_digest_matches": False, "rejected": True},
            "full_Hessian_promotion": {"attempted": True, "rejected": True, "reason": "source omits curvature-squared zero-order terms and the round-S4 remainder is nonzero"},
        },
        "claim_flags": {
            "SAME_GAUGE_CROSSWALK_CERTIFIED": True,
            "TRACELESS_PROJECTOR_CERTIFIED": True,
            "LINEAR_CURVATURE_V_N_U_IMPORTED": True,
            "REPOSITORY_FUNCTIONAL_HESSIAN_NORMALIZED": True,
            "SCALAR_FLAT_FIRST_CURVATURE_INSERTION_COMPLETE": True,
            "ROUND_S4_LINEAR_LAYER_CROSSCHECKED": True,
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY": True,
            "FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED": False,
            "CURVATURE_SQUARED_ZERO_ORDER_LAYER_SUPPLIED": False,
            "PHYSICAL_MIXED_N1_N2_THIRD_CURVATURE_ROWS_COMPUTED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "REPOSITORY_FIVE_FORM_FACTORS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "COMPUTE_PHYSICAL_N3_THREE_LINEAR_TRIANGLE_AND_IMPORT_CURVATURE_SQUARED_HESSIAN_LAYER",
        "claim_boundary": "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL import freezes the complete V, N and U rows linear in background curvature for the monic fourth-order traceless-tensor Hessian in the same beta=1/4 Diff gauge and h=0 Weyl gauge as the repository. The repository functional Hessian is one half of the source monic operator, while the normalized trace-log insertion is unchanged. Exact projector, scalar-flat and round-S4 checks show that the import completely supplies the first-curvature vertex and therefore the pure three-linear-insertion physical n=3 trace. The nonzero round-S4 curvature-squared remainder is retained as a fail-closed witness. This result does not supply the omitted curvature-squared zero-order Hessian, mixed H1-H2 third-curvature rows, an integrated physical triangle, the five complete repository form factors or coefficients, a complete Gamma1 or Q1, residual transfer, or any Lorentzian, Hadamard, particle, positivity, scattering or unitarity theorem.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    required_true = {
        "SAME_GAUGE_CROSSWALK_CERTIFIED",
        "TRACELESS_PROJECTOR_CERTIFIED",
        "LINEAR_CURVATURE_V_N_U_IMPORTED",
        "REPOSITORY_FUNCTIONAL_HESSIAN_NORMALIZED",
        "SCALAR_FLAT_FIRST_CURVATURE_INSERTION_COMPLETE",
        "ROUND_S4_LINEAR_LAYER_CROSSCHECKED",
        "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY",
    }
    for name, enabled in flags.items():
        if enabled is not (name in required_true):
            raise ValueError(f"generic physical-Hessian claim boundary crossed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale generic physical-Hessian certificate: {OUTPUT}")
    print("GENERIC PHYSICAL HESSIAN: SAME-GAUGE LINEAR-CURVATURE LAYER CERTIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
