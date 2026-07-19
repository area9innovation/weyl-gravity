#!/usr/bin/env python3
"""Import the algebraic curvature-squared block of the physical Hessian.

Ohta--Percacci print the projected monic zero-order tensor ``U`` for the
linear background split.  Their auxiliary gauge operator uses a derivative
ordering different from the later same-gauge Barvinsky et al. operator used
by this repository.  The difference is an exact Ricci commutator term in the
linear-curvature, two-derivative block; it cannot change the algebraic
curvature-squared block imported here.

This certificate deliberately stops before the mixed H1/H2 trace and before
any physical triangle integration.
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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-curvature-squared-v1.schema.json"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "round_S4_TT_hessian": HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json",
}

SOURCE_ARCHIVE_SHA256 = "f340a38925ea92a23b8ec0b08d0a871a77f549c79d7c41962158bcac6787fe39"
SOURCE_TEX_SHA256 = "03b79eb2fa03754c04aa1e1d653d4690e7a44a7f48f9ad402826ea670a8529e0"


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


def _row(
    term_id: str,
    coefficient: Fraction | int,
    seed: str,
    *,
    scalar_flat_survives: bool,
    tracefree_null: bool = False,
    source_cancellation: bool = False,
) -> dict[str, Any]:
    return {
        "term_id": term_id,
        "coefficient": _q(coefficient),
        "seed": seed,
        "curvature_order": 2,
        "operator_derivatives": 0,
        "total_engineering_order": 4,
        "scalar_flat_survives": scalar_flat_survives,
        "tracefree_null": tracefree_null,
        "source_cancellation": source_cancellation,
    }


def _operator_rows() -> list[dict[str, Any]]:
    # D=4, alpha=1/6, beta=-1, gamma=1/2 in Appendix A, eq. (curm),
    # after PWP and multiplication by K^{-1}=4 on the traceless bundle.
    return [
        _row("H201", 1, "(R^2/6-Ric^2+Riem^2/2)(g_mn g_ab-g_ma g_nb)", scalar_flat_survives=True),
        _row("H202", 1, "R g_nb Ric_ma", scalar_flat_survives=False),
        _row("H203", Fraction(-1, 2), "R g_ab Ric_mn", scalar_flat_survives=False, tracefree_null=True),
        _row("H204", Fraction(-1, 2), "R g_mn Ric_ab", scalar_flat_survives=False, tracefree_null=True),
        _row("H205", Fraction(1, 3), "R Riem_manb", scalar_flat_survives=False),
        _row("H206", 4, "g_ab Ric_mr Ric_n^r", scalar_flat_survives=True, tracefree_null=True),
        _row("H207", 0, "Ric_ma Ric_nb", scalar_flat_survives=True, source_cancellation=True),
        _row("H208", Fraction(2, 3), "Ric_mn Ric_ab", scalar_flat_survives=True),
        _row("H209", -2, "g_nb Ric_mr Ric_a^r", scalar_flat_survives=True),
        _row("H210", 2, "g_ab Ric^rl Riem_rm ln", scalar_flat_survives=True, tracefree_null=True),
        _row("H211", -4, "g_nb Ric^rl Riem_mr al", scalar_flat_survives=True),
        _row("H212", 12, "Ric^r_m Riem_rabn", scalar_flat_survives=True),
        _row("H213", 8, "Riem_ram l Riem_nb^rl", scalar_flat_survives=True),
        _row("H214", Fraction(-3, 2), "g_ab Riem_mrls Riem_n^rls", scalar_flat_survives=True, tracefree_null=True),
        _row("H215", -2, "Riem_ram l Riem^r_nb^l", scalar_flat_survives=True),
        _row("H216", 6, "Riem_rm ln Riem^r_a^l_b", scalar_flat_survives=True),
        _row("H217", 3, "g_nb Riem_m^rls Riem_a rls", scalar_flat_survives=True),
        _row("H218", Fraction(-3, 2), "g_mn Riem_a rls Riem_b rls", scalar_flat_survives=True, tracefree_null=True),
    ]


def _formula_digest(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _round_source_term_contributions() -> list[tuple[str, Fraction]]:
    """Replay eq. (w) on one unit off-diagonal TT tensor at K=1.

    Projection is invisible on traceless arguments.  Multiplication by the
    monic factor four and division by the tensor norm two gives the displayed
    eigenvalue contribution of each source-W row.
    """

    return [
        ("W01", Fraction(18)),
        ("W02", Fraction(-8)),
        ("W03", Fraction(-6)),
        ("W04", Fraction(6)),
        ("W05", Fraction(36)),
        ("W06", Fraction(0)),
        ("W07", Fraction(32)),
        ("W08", Fraction(0)),
        ("W09", Fraction(0)),
        ("W10", Fraction(-18)),
        ("W11", Fraction(0)),
        ("W12", Fraction(0)),
        ("W13", Fraction(-36)),
    ]


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    h1 = values["physical_H1"]
    round_s4 = values["round_S4_TT_hessian"]
    if (
        h1.get("claim_flags", {}).get("LINEAR_CURVATURE_V_N_U_IMPORTED") is not True
        or h1.get("gauge_crosswalk", {}).get("same_gauge") is not True
        or round_s4.get("operator_dictionary", {}).get("repository_Hessian")
        != "(1/2) Delta_2_perp(2) Delta_2_perp(4)"
    ):
        raise ValueError("physical H2 dependencies drifted")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_dependencies(values)
    rows = _operator_rows()
    if len(rows) != 18 or sum(row["tracefree_null"] for row in rows) != 6:
        raise AssertionError("projected H2 row count drifted")
    effective_scalar_flat = [
        row["term_id"]
        for row in rows
        if row["scalar_flat_survives"]
        and not row["tracefree_null"]
        and row["coefficient"] != _q(0)
    ]
    if effective_scalar_flat != [
        "H201", "H208", "H209", "H211", "H212", "H213", "H215", "H216", "H217"
    ]:
        raise AssertionError("scalar-flat H2 carrier set drifted")
    round_rows = _round_source_term_contributions()
    if sum(value for _, value in round_rows) != 24:
        raise AssertionError("round-S4 algebraic H2 replay drifted")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-curvature-squared-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED",
        "result_state": "ALGEBRAIC_CURVATURE_SQUARED_PHYSICAL_HESSIAN_IMPORTED_GAUGE_ORDERING_CROSSWALKED",
        "lifecycle_state": "COEFFICIENT_INPUT_IMPORTED_MIXED_TRACE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": values["physical_H1"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic local oriented metric; round-S4 and scalar-flat restrictions recorded",
            "field_bundle": "traceless symmetric rank-two metric fluctuations; pointwise rank nine",
            "curvature_order": "algebraic second order only",
            "operator_order": 4,
            "excluded": [
                "two derivatives acting on one background curvature (already in the H1 U block)",
                "mixed H1/H2 functional traces at third curvature order",
                "global Green, spectral-cut, contour and zero-mode data",
            ],
        },
        "source_provenance": {
            "title": "Ultraviolet Fixed Points in Conformal Gravity and General Quadratic Theories",
            "authors": "Nobuyoshi Ohta and Roberto Percacci",
            "arxiv": "1506.05526",
            "doi": "10.1088/0264-9381/33/3/035001",
            "source_url": "https://arxiv.org/abs/1506.05526",
            "source_archive_url": "https://export.arxiv.org/e-print/1506.05526",
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
            "decompressed_tex_sha256": SOURCE_TEX_SHA256,
            "equation_labels": ["d", "w", "proj", "hami", "curm"],
            "source_location": "Appendix A, linear split, projected monic U in equation (curm)",
            "source_scope_statement": "the source drops terms with two derivatives acting on a background curvature but prints every algebraic curvature-square term needed for H2",
        },
        "coupling_specialization": {
            "source_action": "alpha R^2+beta Ric^2+gamma Riem^2",
            "pure_Weyl_choice": {"alpha": _q(Fraction(1, 6)), "beta": _q(-1), "gamma": _q(Fraction(1, 2))},
            "identity": "alpha R^2+beta Ric^2+gamma Riem^2=(1/2)C^2",
            "leading_K_on_traceless_bundle": _q(Fraction(1, 4)),
            "monic_left_factor": _q(4),
            "Euler_policy": "the pure C^2 representative is used directly; no Euler-equivalent raw W representative is substituted",
        },
        "gauge_ordering_crosswalk": {
            "common_trace_gauge": "h=0 so chi_mu=nabla^nu h_mu_nu",
            "minimality_constraint": "c-d=-1/3",
            "source_ordering": {"c": _q(Fraction(2, 3)), "d": _q(1)},
            "repository_ordering": {"c": _q(Fraction(-1, 3)), "d": _q(0)},
            "operator_difference": "Y_d-Y_0=d[nabla_mu,nabla_nu]",
            "commutator_convention": "[nabla_mu,nabla_nu]chi^nu=Ric_mu_rho chi^rho",
            "quadratic_action_difference": "S_gf(d=0)-S_gf(d=1)=(1/2) integral chi_mu Ric^mu_nu chi^nu",
            "monic_H1_difference": "H1_repository-H1_source=2 G_Ric, G_Ric(L,H)=(nabla.L)_mu Ric^mu_nu (nabla.H)^nu",
            "curvature_squared_consequence": "the ordering correction has one background Ricci tensor and derivatives on both fluctuations, hence contributes to H1 and contributes zero to algebraic H2",
            "exact_fixture_ledger": [
                {"fixture": "F1", "repository_minus_source": _q(Fraction(29, 5)), "G_Ric": _q(Fraction(29, 10)), "ratio": _q(2)},
                {"fixture": "F2", "repository_minus_source": _q(Fraction(-61, 5)), "G_Ric": _q(Fraction(-61, 10)), "ratio": _q(2)},
                {"fixture": "F3", "repository_minus_source": _q(Fraction(-1, 3)), "G_Ric": _q(Fraction(-1, 6)), "ratio": _q(2)},
                {"fixture": "F4", "repository_minus_source": _q(-2), "G_Ric": _q(-1), "ratio": _q(2)},
                {"fixture": "F5", "repository_minus_source": _q(Fraction(53, 15)), "G_Ric": _q(Fraction(53, 30)), "ratio": _q(2)},
            ],
        },
        "source_operator": {
            "monic_operator": "H_source=1hat Box^2+H1+H2+O(curvature^3), H2=U_(2)",
            "projection": "U=K^{-1} P W P on traceless symmetric tensors",
            "symmetrization": ["mu<->nu", "alpha<->beta", "(mu,nu)<->(alpha,beta)"],
            "coefficient_rows": rows,
            "formula_digest": _formula_digest(rows),
        },
        "scalar_flat_restriction": {
            "condition": "R=0",
            "effective_nonzero_tracefree_term_ids": effective_scalar_flat,
            "effective_term_count": len(effective_scalar_flat),
            "algebraic_H2_complete_on_declared_domain": True,
        },
        "round_S4_crosscheck": {
            "sectional_curvature_symbol": "K",
            "algebraic_U2_on_TT": "+24 K^2 identity",
            "source_W_term_contributions_to_TT_eigenvalue": [
                {"term_id": term_id, "coefficient": _q(value)}
                for term_id, value in round_rows
            ],
            "full_monic_round_operator": "A^2+6KA+8K^2=(A+2K)(A+4K)",
            "linear_block_commutator_contribution_at_order_K2": "-16 K^2 identity",
            "sum": "+24 K^2-16 K^2=+8 K^2",
            "repository_functional_Hessian_sum": "+12 K^2-8 K^2=+4 K^2",
            "interpretation": "the algebraic H2 block is not the full order-K2 round remainder; contracted derivative indices in H1 supply the separate -16 K2 commutator row",
        },
        "third_curvature_applicability": {
            "newly_closed_input": "the algebraic H2 vertex needed by Tr(H0^-1 H1 H0^-1 H2)",
            "status": "H2_VERTEX_READY_MIXED_TRACE_NOT_COMPUTED",
            "not_closed": [
                "polarization of H2 into two labelled external curvatures",
                "the exact mixed H1/H2 momentum numerator and tensor trace",
                "projection and integration against the certified M14 corner class",
                "complete physical third-curvature functions or anomaly coefficients",
            ],
        },
        "claim_flags": {
            "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED": True,
            "GAUGE_ORDERING_COMMUTATOR_CROSSWALK_CERTIFIED": True,
            "GAUGE_ORDERING_DOES_NOT_CHANGE_ALGEBRAIC_H2": True,
            "ROUND_S4_H2_COMMUTATOR_SPLIT_CERTIFIED": True,
            "SCALAR_FLAT_H2_VERTEX_READY": True,
            "PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED": False,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": False,
            "PHYSICAL_THIRD_CURVATURE_FUNCTIONS_COMPLETE": False,
        },
        "negative_controls": {
            "raw_W_without_projection": {"rejected": True, "reason": "the operational tensor must be PWP and multiplied by K^-1 on the rank-nine bundle"},
            "round_remainder_identification": {"rejected": True, "reason": "+24 K2 is algebraic U2 only; the full round remainder is +8 K2 after the H1 derivative commutator"},
            "mixed_trace_promotion": {"rejected": True, "reason": "H2 is imported but its polarization, mixed trace, carrier projection and integration have not been computed"},
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "POLARIZE_SCALAR_FLAT_H2_AND_COMPUTE_EXACT_MIXED_H1_H2_TRACE_AGAINST_M14_CORNER_CLASS",
        "claim_boundary": "This is a LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL physical-Hessian input certificate. It supplies algebraic H2 but neither completes the physical determinant nor changes the QME or Lorentzian lifecycle state.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != encoded:
            raise SystemExit("stored physical H2 certificate is stale")
        print("generic physical-Hessian curvature-squared certificate: PASS")
        return 0
    OUTPUT.write_text(encoded)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
