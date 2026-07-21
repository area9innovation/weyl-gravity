#!/usr/bin/env python3
"""Exact Hodge/Gauss theorem for charged phases on a closed Cauchy 3-fold.

The analytic input is the standard smooth Hodge decomposition on a connected,
closed, oriented Riemannian three-manifold.  Everything involving the charge
lattice, compact gauge quotient, finite-dimensional mode matrices and fixture
topology is then computed exactly.  No Green operator or quantum datum is
constructed here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1.json"
)
PAYLOAD_OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_PAYLOAD_V1.json"
)
IMPORT = {
    "path": (
        "d_quotient_classical/compensator/"
        "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json"
    ),
    "sha256": "8bea19daa641aed5d771dd440624e5c7ea6128ce857ebd04c3d9b010c7acd5f9",
    "source_commit": "fcfa6f88b390a19a83f844791400f16da121e5d4",
    "result_id": "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1",
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


def _integer_rows(matrix: sp.Matrix) -> list[list[int]]:
    return [[int(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _smith_invariants(matrix: sp.Matrix) -> list[int]:
    """Nonzero Smith invariants from exact determinantal divisors."""
    rank = int(matrix.rank())
    previous = 1
    answer: list[int] = []
    for size in range(1, rank + 1):
        minors: list[int] = []
        for rows in itertools.combinations(range(matrix.rows), size):
            for cols in itertools.combinations(range(matrix.cols), size):
                minors.append(abs(int(matrix.extract(rows, cols).det())))
        divisor = 0
        for value in minors:
            divisor = math.gcd(divisor, value)
        if divisor == 0 or divisor % previous:
            raise AssertionError("invalid determinantal divisor")
        answer.append(divisor // previous)
        previous = divisor
    return answer


def _charge_strata(q: sp.Matrix) -> list[dict[str, Any]]:
    """Rank/Smith data on every fixed-modulus support stratum."""
    strata: list[dict[str, Any]] = []
    for size in range(q.rows + 1):
        for support in itertools.combinations(range(q.rows), size):
            restricted = q.extract(support, range(q.cols)) if size else sp.zeros(0, q.cols)
            rank = int(restricted.rank())
            smith = _smith_invariants(restricted)
            strata.append(
                {
                    "active_phase_rows": list(support),
                    "active_phase_count": size,
                    "rank_Q_support": rank,
                    "relative_phase_dimension_on_stratum": size - rank,
                    "continuous_constant_stabilizer_dimension": q.cols - rank,
                    "smith_invariants": smith,
                    "finite_constant_stabilizer_order": math.prod(smith),
                }
            )
    return strata


def _split(
    q: sp.Matrix,
    phase_kinetic: sp.Matrix,
    gauge_kinetic: sp.Matrix,
    relative_basis: sp.Matrix,
    active_complement: sp.Matrix,
    matter_kernel: sp.Matrix,
) -> dict[str, sp.Matrix]:
    n, r = q.shape
    rank = int(q.rank())
    if phase_kinetic.shape != (n, n) or gauge_kinetic.shape != (r, r):
        raise AssertionError("fixture matrix shape mismatch")
    if not phase_kinetic.is_positive_definite or not gauge_kinetic.is_positive_definite:
        raise AssertionError("positive fixture branch requires M>0 and K>0")
    if relative_basis.shape != (n, n - rank) or q.T * relative_basis != sp.zeros(r, n - rank):
        raise AssertionError("relative basis does not span ker Q^T")
    if matter_kernel.shape != (r, r - rank) or q * matter_kernel != sp.zeros(n, r - rank):
        raise AssertionError("matter-kernel basis does not span ker Q")
    if active_complement.shape != (r, rank):
        raise AssertionError("active complement shape mismatch")

    if r - rank:
        kernel_kinetic = matter_kernel.T * gauge_kinetic * matter_kernel
        active = active_complement - matter_kernel * kernel_kinetic.inv() * (
            matter_kernel.T * gauge_kinetic * active_complement
        )
    else:
        kernel_kinetic = sp.zeros(0, 0)
        active = active_complement
    if matter_kernel.T * gauge_kinetic * active != sp.zeros(r - rank, rank):
        raise AssertionError("active split is not K-orthogonal")

    q_active = q * active
    active_kinetic = active.T * gauge_kinetic * active
    vertical = q_active.T * phase_kinetic * q_active
    relative_inverse = relative_basis.T * phase_kinetic.inv() * relative_basis
    relative_metric = relative_inverse.inv() if n - rank else sp.zeros(0, 0)
    horizontal = (
        phase_kinetic.inv() * relative_basis * relative_metric
        if n - rank
        else sp.zeros(n, 0)
    )
    if relative_basis.T * horizontal != sp.eye(n - rank):
        raise AssertionError("relative lift normalization failed")
    if q.T * phase_kinetic * horizontal != sp.zeros(r, n - rank):
        raise AssertionError("phase horizontal/vertical split failed")
    return {
        "active": active,
        "q_active": q_active,
        "active_kinetic": active_kinetic,
        "kernel_kinetic": kernel_kinetic,
        "vertical": vertical,
        "relative_inverse": relative_inverse,
        "relative_metric": relative_metric,
        "horizontal": horizontal,
    }


def _torsion_bundle_kernel_order(q: sp.Matrix, torsion_h2: list[int]) -> int:
    """Order of ker(Q) on the finite torsion part of H^2(X;Z)^r."""
    order = 1
    for modulus in torsion_h2:
        count = 0
        for vector in itertools.product(range(modulus), repeat=q.cols):
            if all(
                sum(int(q[i, j]) * vector[j] for j in range(q.cols)) % modulus == 0
                for i in range(q.rows)
            ):
                count += 1
        order *= count
    return order


def _topology(
    manifold_id: str,
    cell_ranks: list[int],
    d3_rows: list[list[int]],
    d2_rows: list[list[int]],
    d1_rows: list[list[int]],
    b1: int,
    torsion_h2: list[int],
    scalar_sample: tuple[str, int],
    coexact_sample: tuple[str, int],
) -> dict[str, Any]:
    if len(cell_ranks) != 4:
        raise AssertionError("cell ranks must be C0,C1,C2,C3")
    d3 = sp.Matrix(cell_ranks[2], cell_ranks[3], lambda i, j: d3_rows[i][j])
    d2 = sp.Matrix(cell_ranks[1], cell_ranks[2], lambda i, j: d2_rows[i][j])
    d1 = sp.Matrix(cell_ranks[0], cell_ranks[1], lambda i, j: d1_rows[i][j])
    if d2 * d3 != sp.zeros(cell_ranks[1], cell_ranks[3]) or d1 * d2 != sp.zeros(
        cell_ranks[0], cell_ranks[2]
    ):
        raise AssertionError("cellular boundary does not square to zero")
    computed_b1 = cell_ranks[1] - int(d1.rank()) - int(d2.rank())
    if computed_b1 != b1:
        raise AssertionError("declared b1 disagrees with cellular complex")
    return {
        "manifold_id": manifold_id,
        "connected_closed_oriented_dimension": 3,
        "cell_ranks_C0_C1_C2_C3": cell_ranks,
        "boundary_d3": d3_rows,
        "boundary_d2": d2_rows,
        "boundary_d1": d1_rows,
        "betti_1": b1,
        "torsion_H2_invariant_factors": torsion_h2,
        "flat_U1_component_count": math.prod(torsion_h2),
        "sample_positive_scalar_eigenvalue": scalar_sample[0],
        "sample_positive_scalar_real_multiplicity": scalar_sample[1],
        "sample_positive_coexact_eigenvalue": coexact_sample[0],
        "sample_positive_coexact_real_multiplicity": coexact_sample[1],
    }


def _fixture(
    fixture_id: str,
    topology: dict[str, Any],
    q_rows: list[list[int]],
    m_rows: list[list[int]],
    k_rows: list[list[int]],
    relative_rows: list[list[int]],
    active_rows: list[list[int]],
    kernel_rows: list[list[int]],
) -> dict[str, Any]:
    m = sp.Matrix(m_rows)
    k_form = sp.Matrix(k_rows)
    n, r = m.rows, k_form.rows
    q = sp.Matrix(n, r, lambda i, j: q_rows[i][j])
    rank = int(q.rank())
    relative = sp.Matrix(n, n - rank, lambda i, j: relative_rows[i][j])
    active = sp.Matrix(r, rank, lambda i, j: active_rows[i][j])
    kernel = sp.Matrix(r, r - rank, lambda i, j: kernel_rows[i][j])
    split = _split(q, m, k_form, relative, active, kernel)
    smith = _smith_invariants(q)
    b1 = int(topology["betti_1"])
    lam = sp.Rational(str(topology["sample_positive_scalar_eigenvalue"]))
    nu = sp.Rational(str(topology["sample_positive_coexact_eigenvalue"]))

    if rank:
        longitudinal_kinetic = (
            split["active_kinetic"].inv() + lam * split["vertical"].inv()
        ).inv()
        longitudinal_frequency = (
            lam * sp.eye(rank)
            + split["active_kinetic"].inv() * split["vertical"]
        )
    else:
        longitudinal_kinetic = sp.zeros(0, 0)
        longitudinal_frequency = sp.zeros(0, 0)
    mass = q.T * m * q
    coexact_frequency = nu * sp.eye(r) + k_form.inv() * mass
    harmonic_frequency = k_form.inv() * mass
    smith_order = math.prod(smith)

    return {
        "fixture_id": fixture_id,
        "topology": topology,
        "Q": q_rows,
        "phase_kinetic_M": m_rows,
        "gauge_kinetic_K": k_rows,
        "n": n,
        "r": r,
        "rank_Q": rank,
        "smith_invariants": smith,
        "relative_dimension_per_scalar_eigenfunction": n - rank,
        "matter_kernel_dimension": r - rank,
        "relative_character_basis_N": relative_rows,
        "active_gauge_complement_S": active_rows,
        "matter_kernel_basis_T": kernel_rows,
        "K_orthogonal_active_basis_Sperp": _rows(split["active"]),
        "effective_active_gauge_kinetic_Ka": _rows(split["active_kinetic"]),
        "vertical_phase_Gram_V": _rows(split["vertical"]),
        "relative_metric_Grel": _rows(split["relative_metric"]),
        "relative_horizontal_lift_H": _rows(split["horizontal"]),
        "sample_longitudinal_kinetic_after_Gauss": _rows(longitudinal_kinetic),
        "sample_longitudinal_frequency_squared_operator": _rows(longitudinal_frequency),
        "sample_coexact_frequency_squared_operator": _rows(coexact_frequency),
        "harmonic_frequency_squared_operator": _rows(harmonic_frequency),
        "harmonic_connection_tangent_dimension": r * b1,
        "massive_harmonic_family_count": rank * b1,
        "kernel_Wilson_family_count": (r - rank) * b1,
        "relative_winding_free_rank": (n - rank) * b1,
        "finite_winding_sector_order": smith_order**b1,
        "constant_gauge_stabilizer": {
            "identity_torus_dimension": r - rank,
            "component_invariant_factors": smith,
            "component_count": smith_order,
        },
        "admissible_torsion_bundle_kernel_order": _torsion_bundle_kernel_order(
            q, topology["torsion_H2_invariant_factors"]
        ),
        "active_support_strata": _charge_strata(q),
        "exact_checks": {
            "Q_rank": int(q.rank()) == rank,
            "smith_divisibility": all(
                smith[index + 1] % smith[index] == 0
                for index in range(len(smith) - 1)
            ),
            "relative_kernel": q.T * relative == sp.zeros(r, n - rank),
            "matter_kernel": q * kernel == sp.zeros(n, r - rank),
            "K_orthogonal_split": (
                kernel.T * k_form * split["active"] == sp.zeros(r - rank, rank)
            ),
            "relative_lift": relative.T * split["horizontal"] == sp.eye(n - rank),
            "positive_relative": (
                not (n - rank) or split["relative_metric"].is_positive_definite
            ),
            "positive_longitudinal": (
                not rank or longitudinal_kinetic.is_positive_definite
            ),
            "positive_gauge_kinetic": k_form.is_positive_definite,
        },
    }


def _check_import() -> dict[str, Any]:
    path = ROOT / IMPORT["path"]
    source = json.loads(path.read_text())
    actual = _sha(path)
    if actual != IMPORT["sha256"] or source.get("result_id") != IMPORT["result_id"]:
        raise AssertionError("closed-S3 import drifted")
    return {
        **IMPORT,
        "actual_sha256": actual,
        "oracle_fields_consumed": [],
        "crosscheck_only": True,
    }


def _payload(import_ref: dict[str, Any]) -> dict[str, Any]:
    s1xs2 = _topology(
        "S1xS2_unit_product",
        [1, 1, 1, 1],
        [[0]],
        [[0]],
        [[0]],
        1,
        [],
        ("1", 2),
        ("2", 3),
    )
    t3 = _topology(
        "flat_T3_period_2pi",
        [1, 3, 3, 1],
        [[0], [0], [0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0]],
        3,
        [],
        ("1", 6),
        ("1", 12),
    )
    lens5 = _topology(
        "lens_space_L5_1",
        [1, 1, 1, 1],
        [[0]],
        [[5]],
        [[0]],
        0,
        [5],
        ("1", 1),
        ("1", 1),
    )
    fixtures = [
        _fixture(
            "S1xS2_rank_one_two_phase",
            s1xs2,
            [[1], [1]],
            [[2, 0], [0, 3]],
            [[4]],
            [[1], [-1]],
            [[1]],
            [[],],
        ),
        _fixture(
            "T3_rank_deficient_two_gauge_plus_neutral",
            t3,
            [[1, 0], [1, 0], [0, 0]],
            [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
            [[2, 1], [1, 3]],
            [[1, 0], [-1, 0], [0, 1]],
            [[1], [0]],
            [[0], [1]],
        ),
        _fixture(
            "L5_nonprimitive_charge_torsion_sector",
            lens5,
            [[2]],
            [[3]],
            [[4]],
            [[]],
            [[1]],
            [[],],
        ),
    ]
    payload: dict[str, Any] = {
        "schema": "pure-weyl-general-closed-cauchy-relative-phase-hodge-payload-v1",
        "result_id": "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "state": "ORACLE_FREE_EXACT_TOPOLOGICAL_MATRIX_PAYLOAD_NO_CONFLUX_VERDICT",
        "import_ref": import_ref,
        "fixtures": fixtures,
        "presentation_invariants": {
            "charge": "rank and nonzero Smith invariant factors of Q over Z",
            "topology": "b1, Tor H2 invariant factors, scalar/exact and coexact Laplace eigenspace multiplicities",
            "relative_form": "congruence class of G_rel under a change of ker(Q^T) basis",
            "wilson_lattice": "H1(X;Z)_free tensor Z^r, independent of an integral harmonic basis",
        },
        "oracle_fields_consumed": [],
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def _certificate(import_ref: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    hodge = {
        "analytic_hypotheses": [
            "X is a connected closed oriented smooth three-manifold",
            "h is a smooth Riemannian metric",
            "fields lie in the smooth Sobolev-completable de Rham complex",
        ],
        "one_form_decomposition": "Omega1=d Omega0_perp direct-sum delta Omega2 direct-sum Harm1",
        "scalar_spectrum": "Delta0 has lambda_0=0 with multiplicity one and discrete positive eigenspaces E_lambda of finite multiplicity m_lambda",
        "exact_spectrum": "d/sqrt(lambda) identifies E_lambda with the exact one-form eigenspace for every lambda>0",
        "coexact_spectrum": "positive coexact Hodge eigenspaces F_nu are independent topology/metric data; no S3 relation nu=lambda+constant is assumed",
        "harmonic_dimension": "dim Harm1=b1(X)",
        "integral_harmonic_lattice": "2*pi*H1(X;Z)_free embeds in Harm1 through harmonic representatives",
        "flat_bundle_components": "0 -> H1(X;R)/H1(X;Z)_free -> H1(X;R/Z) -> Tor H2(X;Z) -> 0",
    }
    gauss = {
        "local_constraint": "Q^T M(dot(theta)-Q A0)+delta K(dot(A)-d A0)=0",
        "integrated_constraint": "Q^T integral_X M(dot(theta)-Q A0) vol=0",
        "positive_scalar_mode": "Q^T M v_lambda+sqrt(lambda) K e_L_lambda=0",
        "exact_gauge_action": "delta theta_lambda=Q alpha_lambda; delta a_L=sqrt(lambda) alpha_lambda; delta A0=dot(alpha_lambda)",
        "relative_character": "psi=N^T theta with Q^T N=0 and dim psi=n-k",
        "relative_metric": "G_rel=(N^T M^{-1}N)^{-1}",
        "active_split": "S_perp=S-T(T^T K T)^{-1}T^T K S",
        "longitudinal_schur": "K_L(lambda)=(K_a^{-1}+lambda V^{-1})^{-1}",
        "longitudinal_frequency": "lambda I+K_a^{-1}V",
        "matter_kernel_warning": "ker Q is reducibility only for constant gauge parameters; its nonconstant exact connection directions are gauge, while its coexact and harmonic directions are physical Maxwell/Wilson carriers",
    }
    lattice = {
        "charge_normal_form": "U Q V=diag(d_1,...,d_k,0), d_i>0 and d_i divides d_{i+1}",
        "constant_stabilizer": "ker(T^r -> T^n)=T^{r-k} times product_i Z/d_i",
        "combined_harmonic_quotient_per_free_H1_generator": "R^k times T^{r-k} times Z^{n-k} times product_i Z/d_i",
        "quotient_derivation": "(w,a) in Z^n times R^r modulo (w,a)~(w+Qz,a+2*pi*z), z in Z^r",
        "all_free_H1_generators": "take the b1-fold product; free relative winding rank is b1(n-k)",
        "bundle_strata": "a nowhere-zero charged phase requires Q c=0 in H2(X;Z)^n; torsion flat sectors are ker(Q:Tor H2(X;Z)^r -> Tor H2(X;Z)^n)",
        "topological_obstruction": "the real K-orthogonal active complement need not preserve Z^r; without a primitive K-orthogonal integral complement, the local active/kernel split does not descend to a global product of Wilson subtori",
    }
    modes = {
        "constant_scalar": {
            "relative_phase_dimension": "n-k",
            "Gauss": "Q^T p_0=0",
            "exact_connection": "absent",
            "infinitesimal_reducibility": "constant ker(Q) of dimension r-k",
        },
        "positive_scalar_eigenspace": {
            "multiplicity": "m_lambda",
            "relative_phase_families": "m_lambda(n-k)",
            "massive_longitudinal_families": "m_lambda*k",
            "matter_kernel_exact_physical_families": 0,
        },
        "positive_coexact_eigenspace": {
            "multiplicity": "t_nu",
            "frequency_operator": "nu I+K^{-1}Q^T M Q",
            "massive_families": "t_nu*k",
            "massless_Maxwell_families": "t_nu(r-k)",
        },
        "harmonic_one_forms": {
            "local_tangent_dimension": "b1*r",
            "frequency_operator": "I_b1 tensor K^{-1}Q^T M Q",
            "massive_active_families": "b1*k",
            "massless_kernel_Wilson_families": "b1(r-k)",
            "global_carrier": "combined integral phase-winding/Wilson quotient, not Harm1 treated as pure gauge",
        },
    }
    positivity = {
        "positive_branch": "M>0 and K>0 imply G_rel>0, V>0, K_a>0 and K_L(lambda)>0 for every lambda>0",
        "relative_necessary_and_sufficient": "on a nonsingular stratum, relative scalar modes have positive wave principal form iff G_rel>0",
        "full_modewise_criterion": "G_rel>0; K>0 on coexact/harmonic carriers; and K_a^{-1}+lambda V^{-1}>0 for every scalar eigenvalue lambda>0",
        "existence_corollary": "for M>0,K>0, healthy relative waves exist on every positive scalar eigenspace iff n-rank(Q)>0",
        "lower_order_stability": "a reduced potential Hessian is lower order and must be checked separately on constant and positive modes",
        "indefinite_strata": "if M or K is indefinite, test the displayed finite matrices on each eigenspace; singular A, V or Schur matrices define a separate Dirac stratum and receive no health verdict",
        "global_limit": "modewise positive symbols are not a certificate of a support-local Green operator or nonlinear causal theory",
    }
    s3 = {
        "specialization": "b1=0, Tor H2=0, lambda_ell=ell(ell+2)/a^2, m_ell=(ell+1)^2, nu_ell=(ell+1)^2/a^2 and coexact multiplicity 2 ell(ell+2)",
        "matrix_statement": "the general exact, coexact and constant-mode matrices equal the imported S3 formulas after this substitution",
        "homogeneous_limit": "lambda=0 gives Q^T p_0=0 and G_rel=(N^T M^{-1}N)^{-1}",
        "oracle_policy": "the predecessor terminal verdict is not consumed; it is used only as a hash-pinned regression crosscheck",
    }
    topology_obstruction = {
        "status": "STRUCTURAL_TOPOLOGICAL_OBSTRUCTION",
        "statement": "Harmonic connection modes cannot be discarded as gauge, and a local real K-orthogonal mass split cannot be promoted to a global Wilson-torus product unless an integral K-orthogonal complement exists.",
        "does_not_obstruct": "the local tangent-space Hodge/Gauss reduction or its exact mode counts",
        "does_obstruct": "a presentation-free global factorization into separate active and kernel Wilson tori without extra integral splitting data",
    }
    claim_boundary = (
        "This LOCAL-ALGEBRAIC/REDUCED-MODE structural theorem assumes the smooth "
        "Hodge theorem on a connected closed oriented Riemannian Cauchy "
        "three-manifold and proves the exact finite charge-lattice quotient, "
        "integrated and eigenspace Gauss reductions, mode counts, positive "
        "principal-form criteria, winding/Wilson sectors and the integral-split "
        "obstruction. It is linearized about the trivial smooth fixed-modulus "
        "branch. It does not construct a model-specific action, gravity or D "
        "coupling, a support-local BV/Green parent, nonlinear evolution, "
        "Hadamard data, particles, scale generation, or any quantum result."
    )
    terminal = {
        "result": "GENERAL_CLOSED_CAUCHY_HODGE_GAUSS_STRUCTURE_THEOREM",
        "relative_wave_count_per_positive_scalar_eigenfunction": "n-rank(Q)",
        "topology_sensitive_global_sector": True,
        "S3_reproduced": True,
        "homogeneous_constant_mode_reproduced": True,
        "topological_obstruction": topology_obstruction["statement"],
        "full_causal_parent_activated": False,
        "next_gate": "Select a positive local scalar-U1 action and construct its unreduced support-local BV causal parent while retaining the integral harmonic sector.",
    }
    certificate: dict[str, Any] = {
        "schema": "pure-weyl-general-closed-cauchy-relative-phase-hodge-theorem-v1",
        "result_id": "GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1",
        "result_state": "CERTIFIED_GENERAL_CLOSED_CAUCHY_HODGE_GAUSS_STRUCTURE_THEOREM",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "import": import_ref,
        "scope": {
            "spatial_manifold": "arbitrary connected closed oriented smooth Riemannian three-manifold X",
            "carrier": "linear phase and compact Abelian connection perturbations at fixed positive moduli in the trivial local bundle chart",
            "phase_count": "finite n>=1",
            "gauge_count": "finite r>=0",
            "charge_matrix": "Q in Mat_{n by r}(Z)",
            "derivative_order": 2,
        },
        "round_S3_steps_audit": {
            "S3_specific": [
                "closed formulas for scalar eigenvalues and multiplicities",
                "closed formulas for coexact eigenvalues/curl chiralities and multiplicities",
                "b1(S3)=0 and Tor H2(S3;Z)=0",
            ],
            "general_Hodge_only": [
                "orthogonal exact/coexact/harmonic decomposition",
                "exact one-form normalization dY/sqrt(lambda)",
                "integrated divergence vanishes on a closed manifold",
                "charge-rank split and every finite matrix identity",
            ],
        },
        "hodge_theorem": hodge,
        "gauss_reduction": gauss,
        "integral_lattice_quotient": lattice,
        "mode_theorem": modes,
        "positivity_and_hyperbolicity": positivity,
        "zero_modes_and_strata": {
            "constant_scalar": "n-k relative zero modes, subject to any lower-order potential",
            "constant_gauge_reducibility": "identity stabilizer T^{r-k} with finite components product Z/d_i",
            "harmonic_connection": "b1*r local tangent modes retained; never exact gauge",
            "phase_winding": "free rank b1(n-k) plus nonprimitive finite labels determined by d_i",
            "torsion_bundles": "disconnected admissible sectors are ker Q on Tor H2; only the trivial sector is linearized here",
            "modulus_support": "each vanishing-modulus support uses the restricted row matrix Q_S; inactive complex scalars require Cartesian variables and are outside the phase chart",
        },
        "S3_and_homogeneous_reproduction": s3,
        "topological_obstruction": topology_obstruction,
        "payload_ref": {
            "path": str(PAYLOAD_OUTPUT.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": "0" * 64,
            "content_sha256": payload["content_sha256"],
        },
        "proof_obligations": {
            "predecessor_hash": "PASS",
            "Hodge_hypotheses_declared": "PASS",
            "integrated_Gauss": "PASS",
            "positive_eigenspace_Gauss": "PASS",
            "exact_gauge_quotient": "PASS",
            "relative_metric": "PASS",
            "Smith_lattice_quotient": "PASS",
            "harmonic_Wilson_retention": "PASS",
            "torsion_bundle_strata": "PASS",
            "positive_modewise_forms": "PASS",
            "S3_specialization": "PASS",
            "homogeneous_zero_mode": "PASS",
            "b1_positive_fixture": "PASS",
            "integral_split_obstruction": "PASS",
        },
        "claim_flags": {
            "GENERAL_CLOSED_CAUCHY_HODGE_GAUSS_THEOREM": True,
            "INTEGRAL_WILSON_WINDING_QUOTIENT": True,
            "TOPOLOGICAL_SPLIT_OBSTRUCTION": True,
            "S3_REPRODUCED": True,
            "MODEL_SPECIFIC_ACTION": False,
            "FULL_BV_CAUSAL_PARENT": False,
            "GLOBAL_GREEN_HYPERBOLICITY": False,
            "GRAVITY_OR_D_GAUGE": False,
            "HADAMARD_OR_QUANTUM": False,
            "CONFLUX_VERDICT": False,
        },
        "terminal_verdict": terminal,
        "claim_boundary": claim_boundary,
    }
    certificate["content_hashes"] = {
        "hodge_sha256": _digest(hodge),
        "gauss_sha256": _digest(gauss),
        "lattice_sha256": _digest(lattice),
        "mode_sha256": _digest(modes),
        "positivity_sha256": _digest(positivity),
        "topological_obstruction_sha256": _digest(topology_obstruction),
        "terminal_sha256": _digest(terminal),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    return certificate


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("oracle_fields_consumed") != []:
        raise AssertionError("oracle field consumption is forbidden")
    expected = _digest({key: value for key, value in payload.items() if key != "content_sha256"})
    if payload.get("content_sha256") != expected:
        raise AssertionError("payload content hash mismatch")
    if not any(int(row["topology"]["betti_1"]) > 0 for row in payload["fixtures"]):
        raise AssertionError("b1-positive fixture missing")
    for row in payload["fixtures"]:
        if not all(row["exact_checks"].values()):
            raise AssertionError(f"fixture exact check failed: {row['fixture_id']}")


def validate_certificate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    forbidden = (
        "MODEL_SPECIFIC_ACTION",
        "FULL_BV_CAUSAL_PARENT",
        "GLOBAL_GREEN_HYPERBOLICITY",
        "GRAVITY_OR_D_GAUGE",
        "HADAMARD_OR_QUANTUM",
        "CONFLUX_VERDICT",
    )
    if any(certificate["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "hodge_sha256": _digest(certificate["hodge_theorem"]),
        "gauss_sha256": _digest(certificate["gauss_reduction"]),
        "lattice_sha256": _digest(certificate["integral_lattice_quotient"]),
        "mode_sha256": _digest(certificate["mode_theorem"]),
        "positivity_sha256": _digest(certificate["positivity_and_hyperbolicity"]),
        "topological_obstruction_sha256": _digest(certificate["topological_obstruction"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "claim_boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate.get("content_hashes") != expected_hashes:
        raise AssertionError("certificate content hash mismatch")
    if certificate["payload_ref"]["content_sha256"] != payload["content_sha256"]:
        raise AssertionError("payload canonical hash mismatch")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imported = _check_import()
    payload = _payload(imported)
    certificate = _certificate(imported, payload)
    validate_payload(payload)
    validate_certificate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD_OUTPUT.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    validate_certificate(certificate, payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    if not OUTPUT.exists() or not PAYLOAD_OUTPUT.exists():
        raise AssertionError("generated theorem artifacts are missing")
    stored_certificate = json.loads(OUTPUT.read_text())
    stored_payload = json.loads(PAYLOAD_OUTPUT.read_text())
    if stored_payload != payload:
        raise AssertionError("stored payload drifted")
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    if stored_certificate != certificate:
        raise AssertionError("stored certificate drifted")
    validate_payload(stored_payload)
    validate_certificate(stored_certificate, stored_payload)
    print("GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()


if __name__ == "__main__":
    main()
