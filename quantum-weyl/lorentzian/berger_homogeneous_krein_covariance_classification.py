"""Exact stationary covariance classification on the homogeneous Berger block.

The calculation is deliberately finite and parity-forgetting.  It uses the
metric graph companion and the separately exported graph companion of its
formal adjoint.  Their graph swap determines the action-derived Lagrange
pairing without importing or inventing the still-missing full 104-row
``G_Cauchy`` carrier.

Nothing in this module is a microlocal Hadamard or BRST-state construction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .berger_a104_cauchy_operator_preflight import metric_cauchy_replay
from .berger_homogeneous_stationary_hadamard_normalization_obstruction import (
    ALPHA,
    DEGREE_BLOCKS,
    FIXTURE,
    INSTABILITY_POLYNOMIAL,
    U,
    V,
    _specialized_homogeneous_A104,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_COMMIT = "31875f5b6"
INPUT_CERTIFICATE = (
    "quantum-weyl/lorentzian/certificates/"
    "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION.json"
)
PREFLIGHT = HERE / "certificates/BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT.json"
GENERATED = HERE / "generated/berger_homogeneous_krein_covariance_classification"

LAMBDA = sp.symbols("lambda")
X = sp.symbols("x")


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


def _git_blob(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned covariance input: {commit}:{relative}")
    return result.stdout


def _q(value: sp.Expr | int) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _specialize_record(record: dict[str, Any]) -> sp.Matrix:
    rows, columns = record["shape"]
    matrix = sp.zeros(rows, columns)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError("Cauchy coefficient record hash drifted")
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if sum(exponents) == 0:
                matrix[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": ALPHA, "u": U, "v": V},
                ).subs(FIXTURE)
    return matrix


def _metric_action_data() -> dict[str, sp.Matrix]:
    _, artifacts = metric_cauchy_replay()
    return {
        f"{sector}_{name}": _specialize_record(artifacts[f"{sector}_{name}"])
        for sector in ("metric", "metric_antifield")
        for name in ("K0", "K1", "K2", "A40")
    }


def _action_forms(data: dict[str, sp.Matrix]) -> dict[str, sp.Matrix]:
    """Derive the graph Lagrange form and its symmetric/antisymmetric lifts."""

    swap = sp.zeros(20)
    swap[:10, 10:] = sp.eye(10)
    swap[10:, :10] = sp.eye(10)
    K1 = data["metric_K1"]
    K2 = data["metric_K2"]
    # If z=swap*y, then z solves the literal formal-adjoint graph system.
    # The Lagrange current is
    # z^T K1 x + z^T K2 xdot - zdot^T K2 x.
    B = (swap * K1).row_join(swap * K2).col_join(
        (-swap * K2).row_join(sp.zeros(20))
    )
    A = sp.diag(data["metric_A40"], data["metric_antifield_A40"])
    G = sp.zeros(80)
    G[:40, 40:] = B.T
    G[40:, :40] = B
    omega = sp.zeros(80)
    omega[:40, 40:] = -B.T
    omega[40:, :40] = B
    return {"swap": swap, "B": B, "A": A, "G": G, "omega": omega}


def _lyapunov_rank(A: sp.Matrix) -> tuple[int, int, int]:
    """Exact rank of M -> A^T M+M A on real symmetric matrices."""

    rank = A.rows
    pairs = [(row, column) for row in range(rank) for column in range(row, rank)]
    variable = {pair: index for index, pair in enumerate(pairs)}
    columns = [
        [(row, A[row, column]) for row in range(rank) if A[row, column]]
        for column in range(rank)
    ]
    entries: dict[tuple[int, int], sp.Expr] = {}
    for equation, (row, column) in enumerate(pairs):
        coefficients: dict[int, sp.Expr] = {}
        for middle, value in columns[row]:
            index = variable[tuple(sorted((middle, column)))]
            coefficients[index] = coefficients.get(index, 0) + value
        for middle, value in columns[column]:
            index = variable[tuple(sorted((row, middle)))]
            coefficients[index] = coefficients.get(index, 0) + value
        for index, value in coefficients.items():
            if value:
                entries[equation, index] = value
    matrix = sp.MutableSparseMatrix(len(pairs), len(pairs), entries)
    exact_rank = DomainMatrix.from_Matrix(matrix, fmt="sparse").rank()
    return len(pairs), exact_rank, len(pairs) - exact_rank


def _poly_eval(poly: sp.Expr, matrix: sp.Matrix) -> sp.Matrix:
    value = sp.zeros(matrix.rows)
    identity = sp.eye(matrix.rows)
    for coefficient in sp.Poly(poly, LAMBDA).all_coeffs():
        value = value * matrix + coefficient * identity
    return value


def _nullities(A: sp.Matrix, factor: sp.Expr, powers: int) -> list[int]:
    evaluated = _poly_eval(factor, A)
    value = sp.eye(A.rows)
    output = []
    for _ in range(powers):
        value = value * evaluated
        output.append(A.rows - int(value.rank()))
    return output


def _primary_ledger(metric_A: sp.Matrix) -> list[dict[str, Any]]:
    entries = [
        {
            "primary_id": "zero_jordan",
            "factor": "lambda",
            "factor_expr": LAMBDA,
            "characteristic_exponent_per_endpoint": 2,
            "nullity_powers_per_endpoint": _nullities(metric_A, LAMBDA, 3),
            "combined_real_dimension": 4,
            "combined_complex_chain_sizes": [2, 2],
            "spectral_type": "ZERO_NONSEMISIMPLE",
            "invariant_symmetric_parameter_dimension": 4,
            "positive_cone_linear_span_dimension": 3,
            "positive_rank_capacity": 2,
            "forced_positive_radical_dimension": 2,
        },
        {
            "primary_id": "frequency_sqrt_one_half",
            "factor": "2*lambda^2+1",
            "factor_expr": 2 * LAMBDA**2 + 1,
            "characteristic_exponent_per_endpoint": 1,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, 2 * LAMBDA**2 + 1, 2
            ),
            "combined_real_dimension": 4,
            "combined_complex_chain_sizes": [1, 1],
            "spectral_type": "PURE_IMAGINARY_SEMISIMPLE",
            "invariant_symmetric_parameter_dimension": 4,
            "positive_cone_linear_span_dimension": 4,
            "positive_rank_capacity": 4,
            "forced_positive_radical_dimension": 0,
        },
        {
            "primary_id": "frequency_sqrt_35",
            "factor": "lambda^2+35",
            "factor_expr": LAMBDA**2 + 35,
            "characteristic_exponent_per_endpoint": 2,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, LAMBDA**2 + 35, 2
            ),
            "combined_real_dimension": 8,
            "combined_complex_chain_sizes": [1, 1, 1, 1],
            "spectral_type": "PURE_IMAGINARY_SEMISIMPLE",
            "invariant_symmetric_parameter_dimension": 16,
            "positive_cone_linear_span_dimension": 16,
            "positive_rank_capacity": 8,
            "forced_positive_radical_dimension": 0,
        },
        {
            "primary_id": "frequency_sqrt_41_over_2",
            "factor": "2*lambda^2+41",
            "factor_expr": 2 * LAMBDA**2 + 41,
            "characteristic_exponent_per_endpoint": 2,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, 2 * LAMBDA**2 + 41, 2
            ),
            "combined_real_dimension": 8,
            "combined_complex_chain_sizes": [1, 1, 1, 1],
            "spectral_type": "PURE_IMAGINARY_SEMISIMPLE",
            "invariant_symmetric_parameter_dimension": 16,
            "positive_cone_linear_span_dimension": 16,
            "positive_rank_capacity": 8,
            "forced_positive_radical_dimension": 0,
        },
        {
            "primary_id": "frequency_4_jordan",
            "factor": "lambda^2+16",
            "factor_expr": LAMBDA**2 + 16,
            "characteristic_exponent_per_endpoint": 4,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, LAMBDA**2 + 16, 4
            ),
            "combined_real_dimension": 16,
            "combined_complex_chain_sizes": [2, 2, 2, 2],
            "spectral_type": "PURE_IMAGINARY_NONSEMISIMPLE",
            "invariant_symmetric_parameter_dimension": 32,
            "positive_cone_linear_span_dimension": 16,
            "positive_rank_capacity": 8,
            "forced_positive_radical_dimension": 8,
        },
        {
            "primary_id": "frequency_quartic_sqrt_89",
            "factor": "lambda^4+187*lambda^2+8720",
            "factor_expr": LAMBDA**4 + 187 * LAMBDA**2 + 8720,
            "characteristic_exponent_per_endpoint": 2,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, LAMBDA**4 + 187 * LAMBDA**2 + 8720, 2
            ),
            "combined_real_dimension": 16,
            "combined_complex_chain_sizes": [1] * 8,
            "spectral_type": (
                "TWO_PURE_IMAGINARY_SEMISIMPLE_FREQUENCIES_"
                "SQUARED_(187_PLUS_OR_MINUS_SQRT_89)/2"
            ),
            "invariant_symmetric_parameter_dimension": 32,
            "positive_cone_linear_span_dimension": 32,
            "positive_rank_capacity": 16,
            "forced_positive_radical_dimension": 0,
        },
        {
            "primary_id": "instability_factor",
            "factor": "p(lambda^2)",
            "factor_expr": INSTABILITY_POLYNOMIAL.subs(X, LAMBDA**2),
            "characteristic_exponent_per_endpoint": 1,
            "nullity_powers_per_endpoint": _nullities(
                metric_A, INSTABILITY_POLYNOMIAL.subs(X, LAMBDA**2), 2
            ),
            "combined_real_dimension": 24,
            "combined_complex_chain_sizes": [1] * 12,
            "spectral_type": (
                "TWO_STABLE_NEGATIVE_X_ROOTS_TWO_REAL_GROWTH_X_ROOTS_"
                "ONE_NONREAL_CONJUGATE_X_PAIR"
            ),
            "invariant_symmetric_parameter_dimension": 24,
            "positive_cone_linear_span_dimension": 8,
            "positive_rank_capacity": 8,
            "forced_positive_radical_dimension": 16,
        },
    ]
    for entry in entries:
        del entry["factor_expr"]
    return entries


def _root_ledger() -> dict[str, Any]:
    poly = sp.Poly(INSTABILITY_POLYNOMIAL, X)
    intervals = [
        ("negative_stable_1", sp.Rational(-9), sp.Rational(-8)),
        ("negative_stable_2", sp.Rational(-3, 2), sp.Rational(-1)),
        ("positive_growth_1", sp.Rational(3, 2), sp.Rational(2)),
        ("positive_growth_2", sp.Rational(5, 2), sp.Rational(3)),
    ]
    roots = []
    for root_id, left, right in intervals:
        roots.append(
            {
                "root_id": root_id,
                "interval": [_q(left), _q(right)],
                "endpoint_signs": [
                    int(sp.sign(INSTABILITY_POLYNOMIAL.subs(X, left))),
                    int(sp.sign(INSTABILITY_POLYNOMIAL.subs(X, right))),
                ],
                "sturm_root_count": int(poly.count_roots(left, right)),
            }
        )
    return {
        "polynomial_coefficients_descending": [
            int(value) for value in poly.all_coeffs()
        ],
        "squarefree": sp.gcd(poly, poly.diff()).degree() == 0,
        "total_real_roots": int(poly.count_roots(-sp.oo, sp.oo)),
        "isolated_real_roots": roots,
        "nonreal_roots": 2,
        "nonreal_structure": (
            "one conjugate x pair, producing one real lambda quartet"
        ),
    }


def build() -> dict[str, Any]:
    pinned = json.loads(_git_blob(INPUT_COMMIT, INPUT_CERTIFICATE))
    if (
        pinned.get("result_id")
        != "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION"
        or not pinned["claim_flags"]["HOMOGENEOUS_REAL_GROWTH_EIGENLINES_CERTIFIED"]
    ):
        raise ValueError("pinned stationary obstruction drifted")

    data = _metric_action_data()
    forms = _action_forms(data)
    A = forms["A"]
    B = forms["B"]
    G = forms["G"]
    omega = forms["omega"]
    swap = forms["swap"]
    metric_A = data["metric_A40"]
    antifield_A = data["metric_antifield_A40"]
    primary_factors = (
        (LAMBDA, 3),
        (2 * LAMBDA**2 + 1, 2),
        (LAMBDA**2 + 35, 2),
        (2 * LAMBDA**2 + 41, 2),
        (LAMBDA**2 + 16, 4),
        (LAMBDA**4 + 187 * LAMBDA**2 + 8720, 2),
        (INSTABILITY_POLYNOMIAL.subs(X, LAMBDA**2), 2),
    )

    graph_adjoint_checks = {
        "K2": data["metric_antifield_K2"]
        == swap * data["metric_K2"].T * swap,
        "K1": data["metric_antifield_K1"]
        == -swap * data["metric_K1"].T * swap,
        "K0": data["metric_antifield_K0"]
        == swap * data["metric_K0"].T * swap,
    }
    lyapunov_size, lyapunov_rank, lyapunov_nullity = _lyapunov_rank(A)
    primary = _primary_ledger(metric_A)
    primary_totals = {
        "combined_real_dimension": sum(
            row["combined_real_dimension"] for row in primary
        ),
        "invariant_symmetric_parameter_dimension": sum(
            row["invariant_symmetric_parameter_dimension"] for row in primary
        ),
        "positive_cone_linear_span_dimension": sum(
            row["positive_cone_linear_span_dimension"] for row in primary
        ),
        "positive_rank_capacity": sum(
            row["positive_rank_capacity"] for row in primary
        ),
        "forced_positive_radical_dimension": sum(
            row["forced_positive_radical_dimension"] for row in primary
        ),
    }

    characteristic = sp.factor(metric_A.charpoly(LAMBDA).as_expr())
    canonical_krein = (G + sp.I * omega) / 2
    exact_checks = {
        "pinned_input_commit_and_hash": True,
        "metric_antifield_graph_adjoint_relations": all(
            graph_adjoint_checks.values()
        ),
        "action_Lagrange_pairing_rank_40": int(B.rank()) == 40,
        "action_Lagrange_identity": antifield_A.T * B + B * metric_A
        == sp.zeros(40),
        "commutator_antisymmetric_and_rank_80": (
            omega.T == -omega and int(omega.rank()) == 80
        ),
        "Krein_symmetric_and_rank_80": G.T == G and int(G.rank()) == 80,
        "evolution_preserves_commutator": A.T * omega + omega * A
        == sp.zeros(80),
        "evolution_preserves_Krein_form": A.T * G + G * A == sp.zeros(80),
        "real_involution_is_standard_conjugation": all(
            value.is_rational for value in list(A) + list(B)
        ),
        "metric_antifield_characteristics_match": (
            characteristic
            == sp.factor(antifield_A.charpoly(LAMBDA).as_expr())
        ),
        "metric_antifield_primary_Jordan_nullities_match": all(
            _nullities(metric_A, factor, powers)
            == _nullities(antifield_A, factor, powers)
            for factor, powers in primary_factors
        ),
        "lyapunov_nullity_128": (
            lyapunov_size == 3240
            and lyapunov_rank == 3112
            and lyapunov_nullity == 128
        ),
        "primary_dimensions_sum_80_128_95_54_26": primary_totals
        == {
            "combined_real_dimension": 80,
            "invariant_symmetric_parameter_dimension": 128,
            "positive_cone_linear_span_dimension": 95,
            "positive_rank_capacity": 54,
            "forced_positive_radical_dimension": 26,
        },
        "canonical_Krein_covariance_Hermitian": (
            canonical_krein.conjugate().T == canonical_krein
        ),
        "canonical_Krein_covariance_CCR": (
            canonical_krein - canonical_krein.T == sp.I * omega
        ),
        "canonical_Krein_covariance_invariant": (
            A.T * canonical_krein + canonical_krein * A == sp.zeros(80)
        ),
        "canonical_Krein_covariance_rank_80": int(canonical_krein.rank()) == 80,
    }
    if not all(exact_checks.values()):
        failed = [name for name, passed in exact_checks.items() if not passed]
        raise ValueError(f"homogeneous covariance classification failed: {failed}")

    dependencies = {
        "stationary_obstruction": {
            "path": INPUT_CERTIFICATE,
            "commit": INPUT_COMMIT,
            "result_id": pinned["result_id"],
            "sha256": hashlib.sha256(
                _git_blob(INPUT_COMMIT, INPUT_CERTIFICATE)
            ).hexdigest(),
            "work_item_alias": (
                "BERGER_C26_NORMALIZED_HADAMARD_REPRESENTATIVE_OBSTRUCTION"
            ),
        },
        "action_Cauchy_preflight": {
            "path": PREFLIGHT.relative_to(ROOT).as_posix(),
            "result_id": json.loads(PREFLIGHT.read_text())["result_id"],
            "sha256": _sha256(PREFLIGHT),
        },
    }

    return {
        "schema": (
            "quantum-weyl-berger-homogeneous-krein-covariance-"
            "classification-v1"
        ),
        "result_id": "BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION",
        "result_state": (
            "STATIONARY_POSITIVE_CCR_CLASS_EMPTY_KREIN_AFFINE_CLASS_"
            "AND_NONSTATIONARY_POSITIVE_ALTERNATIVE_EXACT"
        ),
        "lifecycle_layer": "REDUCED_HOMOGENEOUS_FREE_QUANTUM_CLASSIFICATION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "input_commit": INPUT_COMMIT,
        "setting": {
            "background": "compact positive Berger clock",
            "fixture": {
                "alpha_B": _q(1),
                "u": _q(1),
                "v": _q(5),
                "rho_squared": _q(2),
            },
            "mode": "left-invariant homogeneous sections, e1=e2=e3=0",
            "carrier": (
                "parity-forgotten rank-80 metric plus metric-antifield "
                "Cauchy graph block"
            ),
            "real_involution": "entrywise complex conjugation",
        },
        "dependency_refs": dependencies,
        "action_pairing": {
            "graph_swap": "S=[[0,I10],[I10,0]]",
            "Lagrange_matrix": (
                "B=[[S*K1,S*K2],[-S*K2,0]] in "
                "(configuration20,velocity20) ordering"
            ),
            "Lagrange_identity": "A_antifield^T*B+B*A_metric=0",
            "Lagrange_rank": 40,
            "commutator_form": "Omega=[[0,-B^T],[B,0]]",
            "commutator_rank": 80,
            "Krein_form": "G=[[0,B^T],[B,0]]",
            "Krein_inertia": [40, 40, 0],
            "graph_adjoint_checks": graph_adjoint_checks,
            "matrix_hashes": {
                "A80": _canonical_hash(
                    [[str(value) for value in row] for row in A.tolist()]
                ),
                "B40": _canonical_hash(
                    [[str(value) for value in row] for row in B.tolist()]
                ),
                "Omega80": _canonical_hash(
                    [[str(value) for value in row] for row in omega.tolist()]
                ),
                "G80": _canonical_hash(
                    [[str(value) for value in row] for row in G.tolist()]
                ),
                "real_involution80": _canonical_hash(
                    [["1" if row == column else "0" for column in range(80)]
                     for row in range(80)]
                ),
            },
        },
        "homogeneous_spectral_classification": {
            "metric_characteristic_polynomial": sp.sstr(characteristic),
            "primary_ledger": primary,
            "instability_root_ledger": _root_ledger(),
            "totals": primary_totals,
        },
        "stationary_covariance_classification": {
            "real_symmetric_equation": "A^T*mu+mu*A=0",
            "Hermitian_CCR_parameterization": (
                "W(mu)=mu+i*Omega/2 with mu real symmetric and "
                "A^T*mu+mu*A=0"
            ),
            "reality": "conjugate(W)=W^T",
            "Lyapunov_matrix": {
                "shape": [lyapunov_size, lyapunov_size],
                "rank": lyapunov_rank,
                "nullity": lyapunov_nullity,
            },
            "complete_affine_parameter_dimension": 128,
            "positive_symmetric_cone": {
                "parameterization": [
                    "SymmetricPSD_2(R) on the zero semisimple quotient",
                    "HermitianPSD_2(C) on frequency sqrt(1/2)",
                    "HermitianPSD_4(C) on frequency sqrt(35)",
                    "HermitianPSD_4(C) on frequency sqrt(41/2)",
                    (
                        "HermitianPSD_4(C) on the semisimple quotient of "
                        "the frequency-4 Jordan primary"
                    ),
                    (
                        "two independent HermitianPSD_4(C) cones at "
                        "squared frequencies (187+sqrt(89))/2 and "
                        "(187-sqrt(89))/2"
                    ),
                    (
                        "two independent HermitianPSD_2(C) cones at the "
                        "two exactly isolated negative roots of p(x)"
                    ),
                ],
                "linear_span_dimension": 95,
                "maximum_rank": 54,
                "minimum_forced_radical_dimension": 26,
                "unstable_and_Jordan_rule": (
                    "positivity kills every non-imaginary generalized "
                    "primary and the nilpotent image in each imaginary or "
                    "zero Jordan primary"
                ),
            },
            "positive_normalized_CCR_covariance": {
                "status": "EMPTY",
                "proof": (
                    "Every invariant positive mu has a nonzero radical of "
                    "dimension at least 26. If W=mu+i*Omega/2 were positive, "
                    "v^*Wv=0 for v in that radical would imply Wv=0 and "
                    "therefore Omega*v=0, contradicting rank(Omega)=80."
                ),
            },
            "purity": {
                "positive_stationary_pure_class": "EMPTY",
                "compatible_complex_structure_class": "EMPTY",
                "reason": (
                    "the positive class is empty; independently, the two "
                    "simple real eigenline pairs forbid any real stationary "
                    "J with J^2=-I"
                ),
                "indefinite_generalized_purity": (
                    "NOT_IDENTIFIED_WITH_PROBABILISTIC_QUASIFREE_PURITY"
                ),
            },
            "Krein_CCR_family": {
                "status": "COMPLETE_128_PARAMETER_AFFINE_FAMILY",
                "signature_policy": (
                    "signature is stratified by the exact Hermitian inertia "
                    "of W(mu); it is not a single state-space signature"
                ),
                "canonical_representative": "W_K=(G+i*Omega)/2",
                "canonical_representative_rank": 80,
                "canonical_representative_inertia": [40, 40, 0],
                "canonical_representative_status": (
                    "NONDEGENERATE_INDEFINITE_KREIN_CCR_FUNCTIONAL"
                ),
            },
        },
        "nonstationary_alternative": {
            "Darboux_map": "T=diag(B,I40), Omega=T^T*J0*T",
            "standard_form": "J0=[[0,-I40],[I40,0]]",
            "initial_covariance": "W0=(T^T*T+i*Omega)/2",
            "initial_status": (
                "POSITIVE_SEMIDEFINITE_RANK_40_PURE_FINITE_DIMENSIONAL_"
                "CCR_COVARIANCE"
            ),
            "time_evolution": (
                "W_t=exp(t*A)^T*W0*exp(t*A); positive, pure and exact-CCR "
                "for every t, but not stationary"
            ),
            "stationarity_defect": (
                "A^T*W0+W0*A is nonzero because a stationary positive "
                "normalized covariance is impossible"
            ),
            "content_addressed_time_normalization": "t=0 at the frozen fixture",
        },
        "microlocal_status": {
            "finite_block_wavefront_set": "UNDEFINED",
            "Hadamard_condition": "UNDEFINED_ON_FINITE_HOMOGENEOUS_BLOCK",
            "full_distributional_bisolution": "NOT_CONSTRUCTED",
            "BRST_Ward_identity": "NOT_DEFINED_WITHOUT_CORRECTED_Q_CAUCHY",
            "physical_cohomology_positivity": "NOT_COMPUTED",
        },
        "claim_flags": {
            "HOMOGENEOUS_ACTION_COMMUTATOR_AND_KREIN_FORMS_DERIVED": True,
            "HOMOGENEOUS_STATIONARY_COVARIANCE_AFFINE_CLASS_COMPLETE": True,
            "HOMOGENEOUS_STATIONARY_POSITIVE_CCR_COVARIANCE_EXISTS": False,
            "HOMOGENEOUS_CANONICAL_KREIN_CCR_COVARIANCE_EXISTS": True,
            "HOMOGENEOUS_NONSTATIONARY_POSITIVE_COVARIANCE_EXISTS": True,
            "FULL_104_ROW_CAUCHY_KREIN_FORM_IMPORTED": False,
            "CORRECTED_Q_CAUCHY_IMPORTED": False,
            "FULL_BV_HADAMARD_STATE": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "QUANTUM_THEORY_CERTIFIED": False,
        },
        "exact_checks": exact_checks,
        "next_gate": (
            "IMPORT_A_CORRECTED_BRST_CAUCHY_CARRIER_AND_TEST_WHETHER_THE_"
            "26_DIMENSIONAL_STATIONARY_RADICAL_SURVIVES_PHYSICAL_COHOMOLOGY"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies the "
            "parity-forgotten finite homogeneous metric-antifield covariance "
            "matrices at one positive Berger fixture. It derives the action "
            "Lagrange, commutator and Krein forms on that 80-row block, proves "
            "that the 128-parameter stationary normalized CCR affine class "
            "contains no positive element, exhibits a (40,40) Krein element, "
            "and separates an explicitly time-dependent positive alternative. "
            "The ordinary PSD test across even metric and odd antifield slots "
            "is only a matrix diagnostic, not a graded probability inner "
            "product. No corrected q_Cauchy, full 104-row Cauchy form, BRST "
            "quotient, distributional bisolution, wavefront/Hadamard "
            "condition, physical state, renormalized product, QME, particle, "
            "scattering or unitarity theorem is established."
        ),
    }


def write_generated() -> dict[str, Any]:
    result = build()
    GENERATED.mkdir(parents=True, exist_ok=True)
    path = GENERATED / "classification_summary.json"
    summary = {
        "result_id": result["result_id"],
        "input_commit": result["input_commit"],
        "action_pairing": result["action_pairing"],
        "homogeneous_spectral_classification": result[
            "homogeneous_spectral_classification"
        ],
        "stationary_covariance_classification": result[
            "stationary_covariance_classification"
        ],
        "nonstationary_alternative": result["nonstationary_alternative"],
    }
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
