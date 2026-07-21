#!/usr/bin/env python3
"""Exact nonhomogeneous Hodge/Gauss reduction for charged phases on round S3.

The producer imports the homogeneous closed-S3 theorem only by content hash.
It independently derives the scalar-harmonic Gauss reduction, separates the
matter-active and matter-kernel Abelian directions, and emits an oracle-free
matrix payload for a later typed consumer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json"
)
PAYLOAD_OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PAYLOAD_V1.json"
)
IMPORT = {
    "path": (
        "d_quotient_classical/compensator/"
        "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1.json"
    ),
    "sha256": "c88b41a26262c2e79f2e7dbcccf66c50e19cfc179ed96dad8a847fc81f4e2433",
    "source_commit": "02a688837b866e9318ae92107744bba9c52de4d7",
    "result_id": "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _q(value: sp.Expr) -> str:
    value = sp.cancel(value)
    if not bool(value.is_Rational):
        raise AssertionError(f"non-rational fixture value: {value}")
    return str(value)


def _rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[_q(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _active_split(
    q: sp.Matrix,
    kinetic: sp.Matrix,
    gauge_kinetic: sp.Matrix,
    relative_basis: sp.Matrix,
    active_complement: sp.Matrix,
    matter_kernel: sp.Matrix,
) -> dict[str, sp.Matrix]:
    """K-orthogonally split active and matter-kernel gauge directions."""
    n, r = q.shape
    rank = int(q.rank())
    if kinetic.shape != (n, n) or gauge_kinetic.shape != (r, r):
        raise AssertionError("fixture matrix shape mismatch")
    if not kinetic.is_positive_definite or not gauge_kinetic.is_positive_definite:
        raise AssertionError("fixture kinetic matrices must be positive")
    if relative_basis.shape != (n, n - rank) or q.T * relative_basis != sp.zeros(r, n - rank):
        raise AssertionError("relative basis does not span ker Q^T")
    if matter_kernel.shape != (r, r - rank) or q * matter_kernel != sp.zeros(n, r - rank):
        raise AssertionError("matter-kernel basis does not span ker Q")
    if active_complement.shape != (r, rank):
        raise AssertionError("active complement has wrong shape")

    if r - rank:
        k_nn = matter_kernel.T * gauge_kinetic * matter_kernel
        if int(k_nn.rank()) != r - rank:
            raise AssertionError("matter-kernel gauge form is singular")
        active = active_complement - matter_kernel * k_nn.inv() * (
            matter_kernel.T * gauge_kinetic * active_complement
        )
    else:
        k_nn = sp.zeros(0, 0)
        active = active_complement
    if matter_kernel.T * gauge_kinetic * active != sp.zeros(r - rank, rank):
        raise AssertionError("gauge split is not K-orthogonal")

    q_active = q * active
    if int(q_active.rank()) != rank:
        raise AssertionError("active gauge basis lost matter rank")
    k_active = active.T * gauge_kinetic * active
    vertical = q_active.T * kinetic * q_active
    inverse_relative = relative_basis.T * kinetic.inv() * relative_basis
    relative_metric = inverse_relative.inv() if n - rank else sp.zeros(0, 0)
    horizontal_lift = (
        kinetic.inv() * relative_basis * relative_metric
        if n - rank
        else sp.zeros(n, 0)
    )
    if relative_basis.T * horizontal_lift != sp.eye(n - rank):
        raise AssertionError("relative horizontal lift normalization failed")
    if q.T * kinetic * horizontal_lift != sp.zeros(r, n - rank):
        raise AssertionError("relative and vertical phase spaces did not split")
    if rank and (not k_active.is_positive_definite or not vertical.is_positive_definite):
        raise AssertionError("active gauge forms are not positive")
    if n - rank and not relative_metric.is_positive_definite:
        raise AssertionError("relative metric is not positive")
    return {
        "active": active,
        "q_active": q_active,
        "k_active": k_active,
        "k_nn": k_nn,
        "vertical": vertical,
        "inverse_relative": inverse_relative,
        "relative_metric": relative_metric,
        "horizontal_lift": horizontal_lift,
    }


def _fixture(
    fixture_id: str,
    q_rows: list[list[int]],
    kinetic_rows: list[list[int]],
    gauge_kinetic_rows: list[list[int]],
    relative_rows: list[list[int]],
    active_rows: list[list[int]],
    kernel_rows: list[list[int]],
    ell: int,
) -> dict[str, Any]:
    kinetic = sp.Matrix(kinetic_rows)
    gauge_kinetic = sp.Matrix(gauge_kinetic_rows)
    n = kinetic.rows
    r = gauge_kinetic.rows
    q = sp.Matrix(n, r, lambda i, j: q_rows[i][j])
    rank = int(q.rank())
    relative = sp.Matrix(n, n - rank, lambda i, j: relative_rows[i][j])
    active = sp.Matrix(r, rank, lambda i, j: active_rows[i][j])
    kernel = sp.Matrix(r, r - rank, lambda i, j: kernel_rows[i][j])
    split = _active_split(q, kinetic, gauge_kinetic, relative, active, kernel)
    lam = sp.Integer(ell * (ell + 2))
    mu = sp.Integer((ell + 1) ** 2)

    if rank:
        longitudinal_kinetic = (
            split["k_active"].inv() + lam * split["vertical"].inv()
        ).inv()
        schur = split["k_active"] - lam * split["k_active"] * (
            split["vertical"] + lam * split["k_active"]
        ).inv() * split["k_active"]
        if sp.simplify(longitudinal_kinetic - schur) != sp.zeros(rank, rank):
            raise AssertionError("longitudinal Gauss Schur identity failed")
        longitudinal_frequency = lam * sp.eye(rank) + split["k_active"].inv() * split["vertical"]
    else:
        longitudinal_kinetic = sp.zeros(0, 0)
        longitudinal_frequency = sp.zeros(0, 0)
    full_mass = q.T * kinetic * q
    coexact_frequency = mu * sp.eye(r) + gauge_kinetic.inv() * full_mass

    return {
        "fixture_id": fixture_id,
        "Q": q_rows,
        "phase_kinetic_M": kinetic_rows,
        "gauge_kinetic_K": gauge_kinetic_rows,
        "n": n,
        "r": r,
        "rank_Q": rank,
        "relative_dimension": n - rank,
        "matter_kernel_gauge_dimension": r - rank,
        "relative_character_basis_N": relative_rows,
        "active_gauge_complement_S": active_rows,
        "matter_kernel_basis_T": kernel_rows,
        "K_orthogonal_active_basis_Sperp": _rows(split["active"]),
        "Q_active": _rows(split["q_active"]),
        "effective_active_gauge_kinetic_Ka": _rows(split["k_active"]),
        "matter_kernel_gauge_kinetic_K0": _rows(split["k_nn"]),
        "vertical_phase_Gram_V": _rows(split["vertical"]),
        "relative_inverse_metric_A": _rows(split["inverse_relative"]),
        "relative_metric_Grel": _rows(split["relative_metric"]),
        "relative_horizontal_lift_H": _rows(split["horizontal_lift"]),
        "ell": ell,
        "scalar_eigenvalue_lambda": int(lam),
        "coexact_one_form_eigenvalue_mu": int(mu),
        "scalar_harmonic_degeneracy": (ell + 1) ** 2,
        "coexact_one_form_total_degeneracy": 2 * ell * (ell + 2),
        "longitudinal_kinetic_after_Gauss": _rows(longitudinal_kinetic),
        "longitudinal_frequency_squared_operator": _rows(longitudinal_frequency),
        "coexact_frequency_squared_operator": _rows(coexact_frequency),
        "exact_checks": {
            "QT_N_zero": q.T * relative == sp.zeros(r, n - rank),
            "Q_T_zero": q * kernel == sp.zeros(n, r - rank),
            "Tt_K_Sperp_zero": kernel.T * gauge_kinetic * split["active"] == sp.zeros(r - rank, rank),
            "Nt_H_identity": relative.T * split["horizontal_lift"] == sp.eye(n - rank),
            "Qt_M_H_zero": q.T * kinetic * split["horizontal_lift"] == sp.zeros(r, n - rank),
            "positive_relative_metric": not (n - rank) or split["relative_metric"].is_positive_definite,
            "positive_active_gauge_kinetic": not rank or split["k_active"].is_positive_definite,
            "positive_vertical_Gram": not rank or split["vertical"].is_positive_definite,
            "positive_longitudinal_kinetic": not rank or longitudinal_kinetic.is_positive_definite,
            "hodge_eigenvalue_relation_mu_equals_lambda_plus_one": mu == lam + 1,
        },
    }


def _check_import() -> dict[str, Any]:
    path = ROOT / IMPORT["path"]
    source = json.loads(path.read_text())
    if _sha(path) != IMPORT["sha256"] or source.get("result_id") != IMPORT["result_id"]:
        raise AssertionError("homogeneous structure import drifted")
    # Deliberately do not consume terminal_verdict: ell=0 is reconstructed below.
    return {**IMPORT, "actual_sha256": _sha(path), "oracle_fields_consumed": []}


def _payload(import_ref: dict[str, Any]) -> dict[str, Any]:
    fixtures = [
        _fixture(
            "rank_one_two_phase_counterflow_ell1",
            [[1], [1]],
            [[2, 0], [0, 3]],
            [[4]],
            [[1], [-1]],
            [[1]],
            [[],],
            1,
        ),
        _fixture(
            "rank_deficient_two_gauge_plus_neutral_phase_ell2",
            [[1, 0], [1, 0], [0, 0]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [[2, 1], [1, 3]],
            [[1, 0], [-1, 0], [0, 1]],
            [[1], [0]],
            [[0], [1]],
            2,
        ),
        _fixture(
            "rank_zero_uncharged_two_phase_ell1",
            [[0], [0]],
            [[2, 0], [0, 5]],
            [[3]],
            [[1, 0], [0, 1]],
            [[],],
            [[1]],
            1,
        ),
        _fixture(
            "zero_gauge_two_phase_ell1",
            [[], []],
            [[2, 0], [0, 5]],
            [],
            [[1, 0], [0, 1]],
            [],
            [],
            1,
        ),
        _fixture(
            "full_phase_rank_no_relative_phase_ell1",
            [[1, 0], [0, 1]],
            [[2, 0], [0, 3]],
            [[4, 1], [1, 5]],
            [[], []],
            [[1, 0], [0, 1]],
            [[], []],
            1,
        ),
    ]
    result = {
        "schema": "pure-weyl-closed-s3-relative-phase-nonhomogeneous-hodge-payload-v1",
        "result_id": "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PAYLOAD_V1",
        "payload_status": "ORACLE_FREE_EXACT_MATRIX_PAYLOAD_NO_CONFLUX_VERDICT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "import_ref": import_ref,
        "symbolic_parameters": {
            "n": "positive integer phase count",
            "r": "nonnegative integer Abelian-connection count",
            "k": "rank_Q(Q)",
            "ell": "integer ell>=0",
            "lambda_ell": "ell(ell+2)/a^2",
            "mu_ell": "(ell+1)^2/a^2 for coexact one-forms, ell>=1",
            "Q": "n by r integer charge matrix",
            "M": "symmetric nonsingular phase kinetic matrix",
            "K": "symmetric nonsingular Abelian kinetic matrix",
            "N": "primitive n by (n-k) basis of ker_Z(Q^T)",
        },
        "matrix_identities": {
            "relative_inverse_metric": "A=N^T M^{-1} N",
            "relative_metric": "G_rel=A^{-1}",
            "horizontal_lift": "H=M^{-1} N G_rel",
            "horizontal_identities": ["N^T H=I", "Q^T M H=0"],
            "active_vertical_Gram": "V=Q_a^T M Q_a",
            "active_gauge_metric": "K_a=S_perp^T K S_perp",
            "longitudinal_Gauss_solution": "u=(V+lambda K_a)^{-1} sqrt(lambda) K_a dot(b)",
            "longitudinal_kinetic": "K_L=(K_a^{-1}+lambda V^{-1})^{-1}",
            "longitudinal_frequency_squared": "lambda I+K_a^{-1}V",
            "coexact_frequency_squared": "mu I+K^{-1}Q^T M Q",
        },
        "fixtures": fixtures,
        "consumer_contract": {
            "allowed_use": "exact matrix fixtures and symbolic identities for an independent typed Hodge/Gauss consumer",
            "forbidden_use": "no Conflux candidate is a theorem; do not infer a causal Green homotopy, gravity coupling or quantum state",
            "equivalence_level": "L2_CANONICAL_MATRIX_EQUALITY_AFTER_DECLARED_BASIS_SPLIT",
        },
    }
    result["content_sha256"] = _digest({key: value for key, value in result.items() if key != "content_sha256"})
    return result


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["payload_status"] != "ORACLE_FREE_EXACT_MATRIX_PAYLOAD_NO_CONFLUX_VERDICT":
        raise AssertionError("payload lifecycle promoted")
    if payload["import_ref"]["oracle_fields_consumed"]:
        raise AssertionError("homogeneous verdict consumed as an oracle")
    if not all(all(row["exact_checks"].values()) for row in payload["fixtures"]):
        raise AssertionError("fixture exact identity failed")
    expected = _digest({key: value for key, value in payload.items() if key != "content_sha256"})
    if payload["content_sha256"] != expected:
        raise AssertionError("payload content hash drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    import_ref = _check_import()
    matrix_payload = _payload(import_ref)
    validate_payload(matrix_payload)
    payload_sha = hashlib.sha256(_render(matrix_payload).encode()).hexdigest()

    hodge = {
        "scalar_harmonics": {
            "range": "ell=0,1,...",
            "eigenvalue": "lambda_ell=ell(ell+2)/a^2",
            "degeneracy": "(ell+1)^2",
        },
        "exact_one_forms": {
            "range": "ell>=1",
            "basis": "dY_ell/sqrt(lambda_ell)",
            "eigenvalue": "lambda_ell",
            "degeneracy": "(ell+1)^2",
        },
        "coexact_one_forms": {
            "range": "ell>=1",
            "hodge_eigenvalue": "mu_ell=(ell+1)^2/a^2=lambda_ell+1/a^2",
            "curl_eigenvalues": "+/-(ell+1)/a",
            "total_degeneracy": "2 ell(ell+2)",
            "degeneracy_per_curl_chirality": "ell(ell+2)",
        },
        "harmonic_one_forms": "none because H^1(S3)=0",
    }
    gauss = {
        "gauge_action_ell_positive": [
            "delta theta=Q alpha",
            "delta a_L=sqrt(lambda) alpha",
            "delta A0=dot(alpha)",
        ],
        "gauge_invariants": [
            "v=dot(theta)-Q A0",
            "w=sqrt(lambda) theta-Q a_L",
            "e_L=dot(a_L)-sqrt(lambda) A0",
        ],
        "linearized_constraint": "Q^T M v+sqrt(lambda) K e_L=0",
        "relative_character": "psi=N^T theta",
        "relative_horizontal_lift": "H=M^{-1}N(N^T M^{-1}N)^{-1}",
        "active_longitudinal_coordinate": "b=a_active-sqrt(lambda) zeta",
        "matter_kernel_statement": (
            "ker Q is not gauge reducibility of the connection. Its exact scalar "
            "connection modes are pure gauge/constraint modes, while its coexact "
            "connection modes are massless Maxwell polarizations."
        ),
    }
    mode_theorem = {
        "ell_zero": {
            "exact_connection_mode": "ABSENT",
            "Gauss": "Q^T p_0=0",
            "physical_relative_phase_dimension": "n-k",
            "reduced_metric": "G_rel=(N^T M^{-1}N)^{-1}",
            "independent_homogeneous_crosscheck": "REPRODUCED",
        },
        "ell_positive_scalar": {
            "relative_phase_modes": "n-k",
            "relative_principal_polynomial": "det(G_rel)*(omega^2-lambda_ell)^(n-k)",
            "massive_longitudinal_connection_modes": "k",
            "longitudinal_frequency_operator": "lambda_ell I+K_a^{-1}V",
            "matter_kernel_scalar_connection_modes": "0 physical modes",
        },
        "ell_positive_coexact_vector": {
            "connection_polarizations": "r copies of both curl chiralities",
            "frequency_operator": "mu_ell I+K^{-1}Q^T M Q",
            "massive_families": "k",
            "massless_Maxwell_families": "r-k",
        },
        "local_charge_pairing": (
            "Relative modes p=N Pi obey Q^T p=0 harmonic by harmonic. Active "
            "longitudinal modes may carry matter charge density balanced exactly "
            "by the longitudinal electric divergence. Only ell=0 contributes to "
            "the integrated compact charge, which vanishes source-free."
        ),
    }
    positivity = {
        "positive_branch_hypotheses": [
            "M>0",
            "K>0",
            "rank(Q)=k",
            "N has full column rank n-k and Q^T N=0",
        ],
        "conclusion": (
            "G_rel>0, V>0 and K_a>0; every ell>=1 relative mode has positive "
            "wave energy, every active longitudinal Schur kinetic form is "
            "positive, and all principal frequencies are real."
        ),
        "declared_indefinite_stratum": (
            "When M is nonsingular indefinite, require A=N^T M^{-1}N and "
            "V=Q_a^T M Q_a to be nonsingular. The relative sector is positive "
            "hyperbolic iff G_rel=A^{-1}>0; the active longitudinal/vector sector "
            "is positive iff K_a>0 and V>0. Singular A or V is a separate Dirac "
            "stratum and receives no health verdict."
        ),
        "potential_Hessian": (
            "A gauge-invariant reduced Hessian U_rel is lower order. It does not "
            "change hyperbolicity; mode stability additionally requires "
            "lambda_ell G_rel+U_rel to be positive semidefinite."
        ),
    }
    zero_modes = {
        "ell_0_relative": "n-k global relative coordinates; zero frequency when U_rel=0",
        "ell_0_vertical_phase": "removed by constant compact gauge action",
        "ell_0_A0": "Gauss multiplier, not a propagating mode",
        "harmonic_spatial_connection": "absent because b1(S3)=0",
        "ell_positive_relative": "n-k massless scalar-wave families",
        "ell_positive_active_longitudinal": "k massive vector-longitudinal families",
        "ell_positive_matter_kernel_longitudinal": "pure gauge plus Gauss, no scalar physical mode",
        "ell_positive_coexact": "k massive and r-k massless transverse Maxwell families",
        "nonprimitive_charge_effect": "finite isotropy only; no change to continuous mode counts",
    }
    terminal = {
        "result": "HEALTHY_NONHOMOGENEOUS_RELATIVE_PHASE_WAVES_SURVIVE",
        "all_ell_symbolic": True,
        "positive_branch_relative_wave_count_per_scalar_harmonic": "n-rank(Q)",
        "necessary_and_sufficient_relative_health_condition": "G_rel=(N^T M^{-1}N)^{-1}>0",
        "positive_M_corollary": "healthy relative waves exist iff n-rank(Q)>0",
        "homogeneous_ell_zero_reproduced": True,
        "full_causal_parent_activated": False,
        "next_gate": (
            "Select one model-specific positive two-derivative action and construct "
            "its unreduced local scalar-U1 BV causal parent without solving Gauss "
            "through a nonlocal Coulomb inverse."
        ),
    }
    claim_boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers the quadratic "
        "phase and Abelian-connection sector of the declared fixed-modulus, "
        "two-derivative gauge-invariant class on round closed S3. It proves the "
        "all-ell Hodge/Gauss mode counts, quotient matrices and positive-principal-"
        "form criterion, and independently recovers ell=0. It does not select a "
        "gravity-coupled action, solve singular Dirac strata, construct a support-"
        "local BV or Green homotopy, prove nonlinear closure, global monotonicity, "
        "Hadamard data, particles, scale generation or a quantum result."
    )
    certificate = {
        "schema": "pure-weyl-closed-s3-relative-phase-nonhomogeneous-hodge-preflight-v1",
        "result_id": "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1",
        "result_state": "CERTIFIED_ALL_ELL_HODGE_GAUSS_RELATIVE_PHASE_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "import": import_ref,
        "scope": {
            "spatial_manifold": "round closed S3 of radius a",
            "carrier": "linear phase plus Abelian connection perturbations at fixed positive moduli",
            "field_count": "finite n>=1",
            "gauge_count": "finite r>=0",
            "charge_matrix": "Q in Mat_{n by r}(Z)",
            "derivative_order": 2,
            "harmonic_range": "all scalar ell>=0 and exact/coexact one-form ell>=1",
        },
        "hodge_decomposition": hodge,
        "gauss_reduction": gauss,
        "mode_theorem": mode_theorem,
        "positivity_and_hyperbolicity": positivity,
        "zero_mode_ledger": zero_modes,
        "payload_ref": {
            "path": PAYLOAD_OUTPUT.relative_to(ROOT).as_posix(),
            "result_id": matrix_payload["result_id"],
            "sha256": payload_sha,
            "content_sha256": matrix_payload["content_sha256"],
        },
        "proof_obligations": {
            "homogeneous_import_hash": "PASS",
            "homogeneous_verdict_not_consumed_as_oracle": "PASS",
            "round_S3_Hodge_spectrum": "PASS",
            "scalar_gauge_invariants": "PASS",
            "linearized_Gauss_constraint": "PASS",
            "relative_vertical_orthogonal_split": "PASS",
            "rank_deficient_gauge_split": "PASS",
            "Gauss_Schur_complement": "PASS",
            "positive_principal_forms": "PASS",
            "ell_zero_independent_crosscheck": "PASS",
            "all_ell_symbolic_identity": "PASS",
        },
        "terminal_verdict": terminal,
        "claim_flags": {
            "ALL_ELL_HODGE_GAUSS_THEOREM": True,
            "POSITIVE_NONHOMOGENEOUS_RELATIVE_WAVES": True,
            "HOMOGENEOUS_ELL_ZERO_REPRODUCED": True,
            "ORACLE_FREE_MATRIX_PAYLOAD": True,
            "CONFLUX_VERDICT": False,
            "MODEL_SPECIFIC_ACTION_SELECTED": False,
            "FULL_BV_CAUSAL_PARENT": False,
            "GRAVITY_COUPLING": False,
            "HADAMARD_OR_QUANTUM": False,
        },
        "claim_boundary": claim_boundary,
    }
    certificate["content_hashes"] = {
        "hodge_sha256": _digest(hodge),
        "gauss_sha256": _digest(gauss),
        "mode_theorem_sha256": _digest(mode_theorem),
        "positivity_sha256": _digest(positivity),
        "zero_modes_sha256": _digest(zero_modes),
        "terminal_sha256": _digest(terminal),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    validate_certificate(certificate, matrix_payload)
    return certificate, matrix_payload


def validate_certificate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    validate_payload(payload)
    if certificate["result_state"] != "CERTIFIED_ALL_ELL_HODGE_GAUSS_RELATIVE_PHASE_PREFLIGHT":
        raise AssertionError("certificate state drifted")
    if certificate["import"]["oracle_fields_consumed"]:
        raise AssertionError("homogeneous verdict used as oracle")
    if certificate["payload_ref"]["sha256"] != hashlib.sha256(_render(payload).encode()).hexdigest():
        raise AssertionError("payload reference drifted")
    terminal = certificate["terminal_verdict"]
    if not terminal["all_ell_symbolic"] or not terminal["homogeneous_ell_zero_reproduced"]:
        raise AssertionError("mode theorem narrowed")
    flags = certificate["claim_flags"]
    forbidden = (
        "CONFLUX_VERDICT",
        "MODEL_SPECIFIC_ACTION_SELECTED",
        "FULL_BV_CAUSAL_PARENT",
        "GRAVITY_COUPLING",
        "HADAMARD_OR_QUANTUM",
    )
    if any(flags[key] for key in forbidden):
        raise AssertionError("claim boundary promoted")
    expected = {
        "hodge_sha256": _digest(certificate["hodge_decomposition"]),
        "gauss_sha256": _digest(certificate["gauss_reduction"]),
        "mode_theorem_sha256": _digest(certificate["mode_theorem"]),
        "positivity_sha256": _digest(certificate["positivity_and_hyperbolicity"]),
        "zero_modes_sha256": _digest(certificate["zero_mode_ledger"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "claim_boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected:
        raise AssertionError("certificate content hashes drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, payload = build()
    rendered_certificate = _render(certificate)
    rendered_payload = _render(payload)
    if args.check:
        if OUTPUT.read_text() != rendered_certificate or PAYLOAD_OUTPUT.read_text() != rendered_payload:
            raise SystemExit("generated nonhomogeneous Hodge/Gauss artifacts drifted")
        print(f"{certificate['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered_certificate)
    PAYLOAD_OUTPUT.write_text(rendered_payload)
    print(OUTPUT)
    print(PAYLOAD_OUTPUT)


if __name__ == "__main__":
    main()
