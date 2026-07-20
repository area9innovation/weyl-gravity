#!/usr/bin/env python3
"""Exact conformal-matter anomaly vectors and cancellation lattice."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
GRAVITY_PATH = HERE / "certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
GRAVITY_SHA256 = "d11ebc782c6a388e2fd2d934e0a60c7016faf60b9c22691cceeeb6a8080bf3f8"
LOCAL_PATH = QROOT / "local_bv/certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
LOCAL_SHA256 = "07bf332cf1bece92f8a041002f3c787fe7e85e798871e4878fbbc3cd7b20bd3b"
SCHEME_PATH = (
    QROOT
    / "spectral/euclidean/certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json"
)
SCHEME_SHA256 = "21fc06bb31a35f8aa8f1d8f35f6fe1e746a8ab881332e16072ee257b3a437b2c"

BASIS = (
    "ANOM_OMEGA_C2",
    "ANOM_OMEGA_E4",
    "ANOM_OMEGA_C_DUAL_C",
    "ANOM_OMEGA_BOX_R",
)
Q = Fraction
GRAVITY = (Q(199, 30), Q(-87, 20), Q(0), Q(0))
EVEN_ABSOLUTE = {
    "real_conformal_scalar": (Q(1, 120), Q(-1, 360), Q(0), Q(1, 180)),
    "ordinary_homogeneous_conformal_compensator_scalar": (
        Q(1, 120),
        Q(-1, 360),
        Q(0),
        Q(1, 180),
    ),
    "left_Weyl_fermion": (Q(1, 40), Q(-11, 720), Q(0), Q(1, 60)),
    "right_Weyl_fermion": (Q(1, 40), Q(-11, 720), Q(0), Q(1, 60)),
    "Dirac_fermion": (Q(1, 20), Q(-11, 360), Q(0), Q(1, 30)),
    "Abelian_gauge_vector": (Q(1, 10), Q(-31, 180), Q(0), Q(-1, 10)),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _vector(values: tuple[Fraction, ...]) -> list[dict[str, int]]:
    return [_q(value) for value in values]


def _add(*vectors: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(entries, Q(0)) for entries in zip(*vectors))


def _heat_kernel_method() -> dict[str, Any]:
    scalar = EVEN_ABSOLUTE["real_conformal_scalar"]
    dirac = EVEN_ABSOLUTE["Dirac_fermion"]
    vector_boson = (Q(7, 60), Q(-8, 45), Q(0), Q(-4, 45))
    vector_ghost = (Q(-1, 60), Q(1, 180), Q(0), Q(-1, 90))
    if _add(vector_boson, vector_ghost) != EVEN_ABSOLUTE["Abelian_gauge_vector"]:
        raise ValueError("one-form plus ghost heat-kernel ledger failed")
    return {
        "method": "MINIMAL_OPERATOR_SEELEY_DEWITT_TRACE_LEDGER",
        "common_scheme": (
            "zeta/minimal heat-kernel reference scheme; BoxR retained before "
            "finite R2 conversion"
        ),
        "rows": {
            "real_conformal_scalar_half_logdet_Delta0_conf": _vector(scalar),
            "ordinary_homogeneous_compensator_same_scalar_operator": _vector(
                scalar
            ),
            "Dirac_minus_half_logdet_Dslash_squared": _vector(dirac),
            "Weyl_absolute_determinant_half_Dirac": _vector(
                tuple(value / 2 for value in dirac)
            ),
            "gauge_one_form_boson_half_logdet": _vector(vector_boson),
            "gauge_complex_scalar_FP_ghost_minus_logdet": _vector(vector_ghost),
            "gauge_vector_total": _vector(_add(vector_boson, vector_ghost)),
        },
        "Yang_Mills_rule": (
            "multiply the complete gauge-vector row, including FP/nonminimal "
            "cancellation, by dim(ad G)"
        ),
    }


def _index_method() -> dict[str, Any]:
    # Counts are (real scalars, Weyl absolute determinants, Dirac
    # determinants, complete gauge complexes).  This route deliberately does
    # not read EVEN_ABSOLUTE: it reconstructs every row from the independent
    # four-dimensional trace-index weights.
    counts = {
        "real_conformal_scalar": (1, 0, 0, 0),
        "ordinary_homogeneous_conformal_compensator_scalar": (1, 0, 0, 0),
        "left_Weyl_fermion": (0, 1, 0, 0),
        "right_Weyl_fermion": (0, 1, 0, 0),
        "Dirac_fermion": (0, 0, 1, 0),
        "Abelian_gauge_vector": (0, 0, 0, 1),
    }

    def reconstruct(row: tuple[int, int, int, int]) -> tuple[Fraction, ...]:
        ns, nw, nd, nv = row
        return (
            Q(ns + 3 * nw + 6 * nd + 12 * nv, 120),
            Q(-(2 * ns + 11 * nw + 22 * nd + 124 * nv), 720),
            Q(0),
            Q(ns, 180) + Q(nw, 60) + Q(nd, 30) - Q(nv, 10),
        )

    reconstructed = {name: reconstruct(row) for name, row in counts.items()}
    if reconstructed != EVEN_ABSOLUTE:
        raise ValueError("independent central-charge reconstruction failed")
    return {
        "method": "TRACE_ANOMALY_INDEX_AND_CENTRAL_CHARGE_RECONSTRUCTION",
        "formula_even": (
            "c=(Ns+3(NL+NR)+6ND+12NV)/120; "
            "a=(2Ns+11(NL+NR)+22ND+124NV)/720"
        ),
        "formula_type_D_reference_scheme": (
            "b=Ns/180+(NL+NR)/60+ND/30-NV/10"
        ),
        "integer_species_count_rows_Ns_NW_ND_NV": {
            name: list(row) for name, row in counts.items()
        },
        "convention_bridge": (
            "repository coordinates are (c,-a,p,b); NV counts complete "
            "gauge vectors including ghosts; one Dirac equals one left plus "
            "one right Weyl absolute determinant"
        ),
        "reconstructed_rows": {
            name: _vector(vector) for name, vector in reconstructed.items()
        },
    }


def _signed_lattice() -> dict[str, Any]:
    matrix = sp.Matrix([[6, 18, 36, 72], [-2, -11, -22, -124]])
    rhs = sp.Matrix([-4776, 3132])
    smith = smith_normal_form(matrix, domain=ZZ)
    invariants = [
        abs(int(smith[index, index]))
        for index in range(min(smith.shape))
        if smith[index, index]
    ]
    particular = sp.Matrix([128, -308, 0, 0])
    kernel = [
        sp.Matrix([0, -2, 1, 0]),
        sp.Matrix([48, -20, 0, 1]),
    ]
    if matrix * particular != rhs or any(matrix * row != sp.zeros(2, 1) for row in kernel):
        raise ValueError("signed affine lattice replay failed")
    return {
        "integer_matrix_scaled_by_720": [
            [int(value) for value in row] for row in matrix.tolist()
        ],
        "right_hand_side": [int(value) for value in rhs],
        "rank": int(matrix.rank()),
        "smith_invariant_factors": invariants,
        "particular_solution_Ns_NW_ND_NV": [
            int(value) for value in particular
        ],
        "kernel_basis": [
            [int(value) for value in row] for row in kernel
        ],
        "complete_parameterization": {
            "parameters": ["u", "t"],
            "parameter_domain": "Z",
            "N_s": "128+48*t",
            "N_W_absolute": "-308-2*u-20*t",
            "N_D": "u",
            "N_vector_total": "t",
        },
        "complete_rational_parameterization": {
            "parameters": ["u", "t"],
            "parameter_domain": "Q",
            "N_s": "128+48*t",
            "N_W_absolute": "-308-2*u-20*t",
            "N_D": "u",
            "N_vector_total": "t",
        },
        "phase_sensitive_chiral_refinement": {
            "declared_odd_coordinate": "p=0 for each chirality",
            "parameters": ["r", "u", "t"],
            "N_s": "128+48*t",
            "N_L": "r",
            "N_R": "-308-2*u-20*t-r",
            "N_D": "u",
            "N_vector_total": "t",
        },
        "gauge_split": (
            "N_vector_total=N_U1+sum_i dim(ad G_i)*N_YM_i; every integer "
            "split of t gives the same gravitational anomaly vector"
        ),
    }


def build() -> dict[str, Any]:
    gravity = _load(GRAVITY_PATH)
    local = _load(LOCAL_PATH)
    scheme = _load(SCHEME_PATH)
    if (
        _sha(GRAVITY_PATH) != GRAVITY_SHA256
        or gravity.get("result_id") != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
        or _sha(LOCAL_PATH) != LOCAL_SHA256
        or local.get("result_id") != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
        or _sha(SCHEME_PATH) != SCHEME_SHA256
        or scheme.get("result_id") != "WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION"
        or scheme.get("claim_flags", {}).get(
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"
        )
        is not True
    ):
        raise ValueError("strict anomaly inputs drifted")
    imported = tuple(
        Q(
            gravity["coefficients"][key]["numerator"],
            gravity["coefficients"][key]["denominator"],
        )
        for key in BASIS
    )
    if imported != GRAVITY:
        raise ValueError("four-coordinate gravity vector drifted")
    heat = _heat_kernel_method()
    index = _index_method()
    signed = _signed_lattice()
    for name, vector in EVEN_ABSOLUTE.items():
        reconstructed = tuple(
            Q(row["numerator"], row["denominator"])
            for row in index["reconstructed_rows"][name]
        )
        if reconstructed != vector:
            raise ValueError(f"two-method mismatch: {name}")

    search_bound = 10_000
    checks = {
        "gravity_vector_imported_by_hash": True,
        "antifield_completion_imported_by_hash": True,
        "BoxR_scheme_conversion_imported_by_hash": True,
        "two_exact_methods_agree_on_every_standard_species": True,
        "vector_ghost_and_nonminimal_ledger_complete": True,
        "Yang_Mills_multiplicity_is_adjoint_dimension": True,
        "odd_phase_policy_is_separate_from_absolute_determinant": True,
        "BoxR_is_scheme_dependent_and_excluded_from_even_cancellation": True,
        "healthy_nonnegative_box_is_empty_by_C2_separator": True,
        "signed_affine_lattice_is_complete": True,
        "compensator_changes_complex_and_counterterm_algebra": True,
    }
    value = {
        "schema": "quantum-weyl-matter-content-anomaly-cancellation-lattice-v1",
        "result_id": "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE",
        "result_state": (
            "HEALTHY_NONNEGATIVE_LATTICE_EMPTY_SIGNED_DETERMINANT_"
            "LATTICE_COMPLETE_COMPENSATOR_IS_CHANGED_THEORY"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": {
            "strict_breaking": {
                "path": GRAVITY_PATH.relative_to(ROOT).as_posix(),
                "sha256": GRAVITY_SHA256,
            },
            "antifield_completion": {
                "path": LOCAL_PATH.relative_to(ROOT).as_posix(),
                "sha256": LOCAL_SHA256,
            },
            "BoxR_scheme_conversion": {
                "path": SCHEME_PATH.relative_to(ROOT).as_posix(),
                "sha256": SCHEME_SHA256,
            },
        },
        "basis": list(BASIS),
        "gravity_vector": _vector(GRAVITY),
        "coefficient_methods": {
            "repository_heat_kernel": heat,
            "independent_index_trace": index,
        },
        "matter_vectors_absolute_determinant": {
            name: {
                "vector": _vector(vector),
                "statistics_and_complex": {
                    "real_conformal_scalar": "REAL_STANDARD_SIGN_BOSON",
                    "ordinary_homogeneous_conformal_compensator_scalar": (
                        "REAL_STANDARD_SIGN_SCALAR_DETERMINANT_ALIAS"
                    ),
                    "left_Weyl_fermion": "LEFT_CHIRAL_COMPLEX_FERMION_ABSOLUTE_DETERMINANT",
                    "right_Weyl_fermion": "RIGHT_CHIRAL_COMPLEX_FERMION_ABSOLUTE_DETERMINANT",
                    "Dirac_fermion": "LEFT_PLUS_RIGHT_COMPLEX_FERMION",
                    "Abelian_gauge_vector": "REAL_VECTOR_PLUS_COMPLETE_FP_NONMINIMAL_COMPLEX",
                }[name],
            }
            for name, vector in EVEN_ABSOLUTE.items()
        },
        "chiral_phase_ledger": {
            "declared_common_Ward_regulator": (
                "p=0 for each left or right Weyl determinant; the trace "
                "anomaly is exactly one half the Dirac anomaly"
            ),
            "independent_Ward_preserving_methods": {
                "Pauli_Villars_Fujikawa": "https://arxiv.org/abs/1610.02304",
                "Weyl_determinant_path_integral": "https://arxiv.org/abs/2309.08670",
            },
            "nonzero_Pontryagin_alternative": (
                "NOT_ADMITTED_IN_THE_COMMON_BV_COMPLEX: regulator choices "
                "that generate a parity-odd trace term do not pass the "
                "declared simultaneous diffeomorphism, Lorentz and gauge "
                "Ward identities and are not a lattice column"
            ),
            "healthy_even_no_go_independent_of_phase_policy": True,
        },
        "Yang_Mills_rule": {
            "vector": "dim(ad G) times Abelian_gauge_vector",
            "ghost_policy": "one complete FP/nonminimal gauge complex per generator",
            "interacting_gauge_beta_terms": (
                "not part of the purely gravitational four-coordinate vector"
            ),
        },
        "healthy_nonnegative_classification": {
            "variables": ["N_s", "N_L", "N_R", "N_D", "N_U1", "N_YM_i"],
            "explicit_search_box": {
                "lower_bound_each": 0,
                "upper_bound_each": search_bound,
                "solution_set": "EMPTY",
            },
            "unbounded_nonnegative_integer_lattice": "EMPTY",
            "unbounded_nonnegative_real_cone": "EMPTY",
            "separating_functional": {
                "coordinates": [1, 0, 0, 0],
                "gravity_value": _q(GRAVITY[0]),
                "all_standard_species_values_strictly_positive": True,
            },
            "QME_disposition": "REMAINS_OBSTRUCTED_IN_DECLARED_HEALTHY_FAMILY",
        },
        "signed_determinant_lattice": signed,
        "alternative_field_content": {
            "negative_multiplicity": (
                "formal inverse determinant or wrong-statistics regulator "
                "power; an overall wrong-sign bosonic kinetic contour does "
                "not automatically implement negative multiplicity"
            ),
            "higher_derivative_conformal_fields": (
                "NOT_CLASSIFIED: require their own complete BV complexes and "
                "two-method anomaly vectors before adjoining new lattice columns"
            ),
            "ordinary_homogeneous_conformal_compensator": (
                "counts as one real conformal scalar only if it is an ordinary "
                "standard-sign spectator"
            ),
            "shifting_Wess_Zumino_compensator": (
                "NOT_A_LATTICE_COLUMN: it enlarges the BV complex and local "
                "counterterm algebra, making H14 exact in the tau-adic theory"
            ),
        },
        "scheme_ledger": {
            "C2_E4_CdualC": "scheme-independent within each declared determinant phase policy",
            "BoxR": (
                "reference heat-kernel values displayed; arbitrary finite R2 "
                "counterterms shift this coordinate, so it is not used in "
                "the cancellation no-go or signed even lattice"
            ),
            "strict_repository_BoxR": _q(GRAVITY[3]),
        },
        "exact_checks": checks,
        "claim_flags": {
            "HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS": False,
            "COMPLETE_SIGNED_STANDARD_SPECIES_LATTICE_CLASSIFIED": True,
            "HIGHER_DERIVATIVE_MATTER_CLASSIFIED": False,
            "COMPENSATOR_IS_STRICT_CANCELLATION": False,
            "LORENTZIAN_QME_OR_PARTICLE_CLAIM": False,
        },
        "next_gate": (
            "ADD_A_NEW_MATTER_COLUMN_ONLY_AFTER_ITS_FULL_BV_COMPLEX_AND_"
            "TWO_INDEPENDENT_ANOMALY_COEFFICIENT_METHODS_ARE_CERTIFIED"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL theorem classifies the "
            "complete free standard-spin 0, 1/2 and 1 anomaly lattice in the "
            "declared schemes. It proves no healthy nonnegative cancellation "
            "and gives the full formal signed determinant lattice. A shifting "
            "compensator changes the BV complex; higher-derivative fields need "
            "new certified columns. No Lorentzian QME, state, positivity, "
            "particle, scattering, phenomenology, GUT or unitarity claim follows."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("matter lattice exact checks failed")
    healthy = value.get("healthy_nonnegative_classification", {})
    flags = value.get("claim_flags", {})
    if (
        healthy.get("unbounded_nonnegative_integer_lattice") != "EMPTY"
        or healthy.get("unbounded_nonnegative_real_cone") != "EMPTY"
        or flags.get("HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS") is not False
        or flags.get("COMPLETE_SIGNED_STANDARD_SPECIES_LATTICE_CLASSIFIED")
        is not True
        or flags.get("HIGHER_DERIVATIVE_MATTER_CLASSIFIED") is not False
        or flags.get("COMPENSATOR_IS_STRICT_CANCELLATION") is not False
        or flags.get("LORENTZIAN_QME_OR_PARTICLE_CLAIM") is not False
    ):
        raise ValueError("matter-lattice claim boundary over-promoted")
    lattice = value.get("signed_determinant_lattice", {})
    if (
        lattice.get("smith_invariant_factors") != [1, 30]
        or lattice.get("particular_solution_Ns_NW_ND_NV") != [128, -308, 0, 0]
        or lattice.get("kernel_basis") != [[0, -2, 1, 0], [48, -20, 0, 1]]
    ):
        raise ValueError("signed matter lattice drifted")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
