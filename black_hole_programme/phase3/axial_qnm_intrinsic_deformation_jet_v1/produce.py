#!/usr/bin/env python3
"""Produce the exact intrinsic-deformation dual-number jet certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
INPUTS = {
    "projective_cocycle": (
        ROOT / "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
    "local_smith_dichotomy": (
        ROOT / "black_hole_programme/phase3/"
        "axial_qnm_local_smith_dichotomy/certificate.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(value)))


def matrix_strings(value: sp.Matrix) -> list[list[str]]:
    return [
        [encode(value[i, j]) for j in range(value.cols)]
        for i in range(value.rows)
    ]


def produce() -> dict:
    projective = json.loads(INPUTS["projective_cocycle"].read_text())
    smith = json.loads(INPUTS["local_smith_dichotomy"].read_text())
    if not projective["claim_flags"]["generic_rational_cocycle_nontrivial"]:
        raise RuntimeError("projective cocycle input is not certified nontrivial")
    if not smith["claim_flags"]["local_smith_dichotomy_exact"]:
        raise RuntimeError("local Smith input is not certified exact")

    # Work in the dual-number ring by retaining coefficients through first
    # order in tau.  L and S are commuting placeholders for linear operators
    # acting on the declared vectors; no analytic boundary realization is
    # used here.
    tau = sp.Symbol("tau")
    L, S, x, y = sp.symbols("L S x y")
    expanded = sp.expand((L + tau * S) * (y + tau * x))
    jet_remainder = sp.rem(expanded, tau**2, tau)
    expected_jet = L * y + tau * (L * x + S * y)
    if sp.expand(jet_remainder - expected_jet) != 0:
        raise RuntimeError("dual-number operator jet identity failed")

    # In the ordered column basis (epsilon, 1), multiplication by a+epsilon*b
    # has the requested upper-triangular regular representation.
    a, b, u, v = sp.symbols("a b u v")
    regular_matrix = sp.Matrix([[a, b], [0, a]])
    input_coefficients = sp.Matrix([u, v])
    output_coefficients = regular_matrix * input_coefficients
    expected_output = sp.Matrix([a * u + b * v, a * v])
    if output_coefficients != expected_output:
        raise RuntimeError("dual-number regular representation failed")

    # First-order implicit-function identity at a simple scalar zero.  alpha
    # represents partial_omega a, beta represents partial_tau a, and nu is
    # omega_n'(0).  This is a formal local consequence only; no QNM or beta
    # has been evaluated.
    alpha, beta = sp.symbols("alpha beta", nonzero=True)
    nu = sp.Symbol("nu")
    chain_equation = alpha * nu + beta
    solved_shift = sp.solve(chain_equation, nu)[0]
    if sp.simplify(solved_shift + beta / alpha) != 0:
        raise RuntimeError("implicit QNM-shift identity failed")
    kappa = sp.simplify(beta / alpha)

    # Conditional first variation of the scalar real-axis flux law.  Barred
    # symbols are independent formal conjugates; the identity becomes a
    # physical flux statement only for a real, endpoint-compatible scalar
    # family with the declared conjugation.
    ain, aout, bin_, bout = sp.symbols("A_in A_out b_in b_out")
    ain_bar, aout_bar, bin_bar, bout_bar = sp.symbols(
        "A_in_bar A_out_bar b_in_bar b_out_bar"
    )
    flux_tau = (
        (ain + tau * bin_) * (ain_bar + tau * bin_bar)
        - (aout + tau * bout) * (aout_bar + tau * bout_bar)
    )
    flux_derivative = sp.expand(flux_tau).coeff(tau, 1)
    expected_flux_derivative = (
        ain_bar * bin_ + ain * bin_bar
        - aout_bar * bout - aout * bout_bar
    )
    if sp.expand(flux_derivative - expected_flux_derivative) != 0:
        raise RuntimeError("conditional flux derivative identity failed")

    # Partial dual-number jet: only the repeated spin-two factor is jetted,
    # while the spin-one factor f is tau-constant.  The ordered column basis
    # is (epsilon*spin2, spin2, spin1).
    c, d = sp.symbols("c d")
    f_scalar = sp.Symbol("f", nonzero=True)
    partial_jet = sp.Matrix([
        [a, b, c],
        [0, a, d],
        [0, 0, f_scalar],
    ])
    partial_inverse = partial_jet.inv().applyfunc(sp.cancel)
    mixing = sp.cancel(-d / (a * f_scalar))
    mixing_derivative = sp.cancel(
        (b * d - a * c) / (a**2 * f_scalar)
    )
    expected_partial_inverse = sp.Matrix([
        [1 / a, -b / a**2, mixing_derivative],
        [0, 1 / a, mixing],
        [0, 0, 1 / f_scalar],
    ]).applyfunc(sp.cancel)
    if partial_inverse != expected_partial_inverse:
        raise RuntimeError("partial-jet inverse identity failed")

    a1, b1, c1, d1, f1 = sp.symbols("a_1 b_1 c_1 d_1 f_1")
    a2p, b2p, c2p, d2p, f2p = sp.symbols(
        "a_2p b_2p c_2p d_2p f_2p"
    )
    jet1 = sp.Matrix([
        [a1, b1, c1],
        [0, a1, d1],
        [0, 0, f1],
    ])
    jet2 = sp.Matrix([
        [a2p, b2p, c2p],
        [0, a2p, d2p],
        [0, 0, f2p],
    ])
    product_base_a = a1 * a2p
    product_base_d = a1 * d2p + d1 * f2p
    product_base_f = f1 * f2p
    product_tangent_a = b1 * a2p + a1 * b2p
    product_tangent_d = b1 * d2p + a1 * c2p + c1 * f2p
    jet_of_product = sp.Matrix([
        [product_base_a, product_tangent_a, product_tangent_d],
        [0, product_base_a, product_base_d],
        [0, 0, product_base_f],
    ])
    if sp.expand(jet1 * jet2 - jet_of_product) != sp.zeros(3):
        raise RuntimeError("partial-jet product functor failed")

    # Conditional contour-moment theorem.  The certificate proves the local
    # residue and zero-free frame-renormalization algebra.  The global sum is
    # the residue theorem under the explicitly ledgered analytic-domain
    # hypotheses; no physical contour is supplied or evaluated here.
    z = sp.Symbol("z")
    omega_j = sp.Symbol("omega_j")
    k = sp.Symbol("k", integer=True, nonnegative=True)
    a2, b1 = sp.symbols("a_2 b_1")
    a_local = alpha * z + a2 * z**2
    b_local = beta + b1 * z
    zero_count_residue = sp.simplify(
        sp.limit(z * sp.diff(a_local, z) / a_local, z, 0)
    )
    moment_residue = sp.simplify(
        sp.limit(
            z * (omega_j + z)**k * b_local / a_local,
            z,
            0,
        )
    )
    if zero_count_residue != 1:
        raise RuntimeError("simple-zero count residue failed")
    if sp.simplify(moment_residue - omega_j**k * beta / alpha) != 0:
        raise RuntimeError("contour-moment local residue failed")

    u0 = sp.Symbol("u_0", nonzero=True)
    u_tau = sp.Symbol("u_tau")
    renormalized_a = u0 * a
    renormalized_b = u_tau * a + u0 * b
    quotient_shift = sp.simplify(
        renormalized_b / renormalized_a - b / a
    )
    if sp.simplify(quotient_shift - u_tau / u0) != 0:
        raise RuntimeError("endpoint-renormalization quotient law failed")

    # Tangent of the 2x2 Jost determinant.  This is a finite determinant
    # identity; identifying these columns with analytic physical Jost frames
    # is separately and explicitly conditional.
    xh0, xh1, xp0, xp1 = sp.symbols("X_H0 X_H1 X_p0 X_p1")
    yh0, yh1, yp0, yp1 = sp.symbols("Y_H0 Y_H1 Y_p0 Y_p1")
    x_h = sp.Matrix([xh0, xh1])
    x_p = sp.Matrix([xp0, xp1])
    y_h = sp.Matrix([yh0, yh1])
    y_p = sp.Matrix([yp0, yp1])
    determinant_family = sp.expand(
        sp.Matrix.hstack(x_h + tau * y_h, x_p + tau * y_p).det()
    )
    determinant_tangent = sp.expand(determinant_family).coeff(tau, 1)
    expected_determinant_tangent = (
        sp.Matrix.hstack(x_h, y_p).det()
        + sp.Matrix.hstack(y_h, x_p).det()
    )
    if sp.expand(
        determinant_tangent - expected_determinant_tangent
    ) != 0:
        raise RuntimeError("Jost determinant tangent identity failed")

    # Conditional finite-cluster algebra, independently instantiated at N=3.
    # The model verifies moment completeness, root interpolation, resultant
    # selection, gcd defect counting, Newton reconstruction, and centered
    # moments without supplying any physical contour or QNM root.
    omega = sp.Symbol("omega")
    roots = sp.symbols("omega_1 omega_2 omega_3")
    kappas = sp.symbols("kappa_1 kappa_2 kappa_3")
    vandermonde = sp.Matrix([
        [1, 1, 1],
        list(roots),
        [root**2 for root in roots],
    ])
    vandermonde_det = sp.factor(vandermonde.det())
    expected_vandermonde_det = sp.factor(
        (roots[1] - roots[0])
        * (roots[2] - roots[0])
        * (roots[2] - roots[1])
    )
    if sp.simplify(vandermonde_det - expected_vandermonde_det) != 0:
        raise RuntimeError("N=3 Vandermonde determinant failed")

    cluster_p = sp.expand(sp.prod(omega - root for root in roots))
    cluster_q = sp.expand(sum(
        kappa * sp.prod(
            omega - other
            for other in roots
            if other != root
        )
        for root, kappa in zip(roots, kappas)
    ))
    interpolation_values = [
        sp.factor(cluster_q.subs(omega, root))
        for root in roots
    ]
    expected_interpolation_values = [
        sp.factor(
            kappa * sp.diff(cluster_p, omega).subs(omega, root)
        )
        for root, kappa in zip(roots, kappas)
    ]
    if any(
        sp.simplify(value - expected) != 0
        for value, expected in zip(
            interpolation_values,
            expected_interpolation_values,
        )
    ):
        raise RuntimeError("N=3 Q interpolation failed")

    resultant = sp.factor(sp.resultant(cluster_p, cluster_q, omega))
    resultant_product = sp.factor(sp.prod(interpolation_values))
    if sp.simplify(resultant - resultant_product) != 0:
        raise RuntimeError("N=3 resultant product failed")

    # Branchwise gcd counts: all defective, one semisimple, two semisimple,
    # and all semisimple.  Generic nonzero root differences are represented
    # by specializing to three distinct exact roots.
    exact_root_subs = dict(zip(roots, [sp.Integer(1), 2, 4]))
    p_exact = sp.Poly(cluster_p.subs(exact_root_subs), omega)
    gcd_degrees = {}
    kappa_patterns = {
        "three_defective": [1, 1, 1],
        "two_defective": [1, 1, 0],
        "one_defective": [1, 0, 0],
        "zero_defective": [0, 0, 0],
    }
    for label, values in kappa_patterns.items():
        substitutions = {
            **exact_root_subs,
            **dict(zip(kappas, values)),
        }
        q_branch = sp.Poly(cluster_q.subs(substitutions), omega)
        gcd_degrees[label] = sp.degree(sp.gcd(p_exact, q_branch))
    if gcd_degrees != {
        "three_defective": 0,
        "two_defective": 1,
        "one_defective": 2,
        "zero_defective": 3,
    }:
        raise RuntimeError("N=3 gcd defect-count model failed")

    power_sums = {
        degree: sp.expand(sum(root**degree for root in roots))
        for degree in range(4)
    }
    e1 = power_sums[1]
    e2 = sp.expand((power_sums[1]**2 - power_sums[2]) / 2)
    e3 = sp.expand(
        (
            power_sums[1]**3
            - 3 * power_sums[1] * power_sums[2]
            + 2 * power_sums[3]
        ) / 6
    )
    newton_p = sp.expand(omega**3 - e1 * omega**2 + e2 * omega - e3)
    if sp.expand(newton_p - cluster_p) != 0:
        raise RuntimeError("N=3 Newton reconstruction failed")

    weighted_moments = {
        degree: sp.expand(sum(
            kappa * root**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(3)
    }
    p_coefficients = sp.Poly(cluster_p, omega).all_coeffs()
    q_from_moments = sp.expand(
        weighted_moments[0] * omega**2
        + (weighted_moments[1] + p_coefficients[1]
           * weighted_moments[0]) * omega
        + weighted_moments[2]
        + p_coefficients[1] * weighted_moments[1]
        + p_coefficients[2] * weighted_moments[0]
    )
    if sp.expand(q_from_moments - cluster_q) != 0:
        raise RuntimeError("N=3 root-free Q reconstruction failed")

    centroid = sp.expand(power_sums[1] / 3)
    centered_moments = {
        degree: sp.expand(sum(
            kappa * (root - centroid)**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(3)
    }
    centered_from_raw = {
        degree: sp.expand(sum(
            sp.binomial(degree, index)
            * (-centroid)**(degree - index)
            * weighted_moments[index]
            for index in range(degree + 1)
        ))
        for degree in range(3)
    }
    if any(
        sp.expand(centered_moments[degree]
                  - centered_from_raw[degree]) != 0
        for degree in range(3)
    ):
        raise RuntimeError("N=3 centered-moment transform failed")

    zeta = sp.Symbol("zeta")
    resolvent = sp.factor(sum(
        kappa / (zeta - root)
        for root, kappa in zip(roots, kappas)
    ))
    rational_resolvent = sp.factor(
        cluster_q.subs(omega, zeta) / cluster_p.subs(omega, zeta)
    )
    if sp.cancel(resolvent - rational_resolvent) != 0:
        raise RuntimeError("N=3 extension resolvent identity failed")
    extended_moments = {
        degree: sp.expand(sum(
            kappa * root**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(7)
    }
    inverse_zeta = sp.Symbol("inverse_zeta")
    laurent_series = sp.expand(
        sp.series(
            resolvent.subs(zeta, 1 / inverse_zeta),
            inverse_zeta,
            0,
            7,
        ).removeO()
    )
    expected_laurent = sp.expand(sum(
        extended_moments[degree] * inverse_zeta**(degree + 1)
        for degree in range(6)
    ))
    if sp.expand(laurent_series - expected_laurent) != 0:
        raise RuntimeError("N=3 resolvent Laurent moments failed")

    hankel = sp.Matrix(3, 3, lambda row, column:
                       extended_moments[row + column])
    hankel_factor = (
        vandermonde * sp.diag(*kappas) * vandermonde.T
    )
    if sp.simplify(hankel - hankel_factor) != sp.zeros(3):
        raise RuntimeError("N=3 Hankel factorization failed")
    hankel_det = sp.factor(hankel.det())
    discriminant = sp.factor(sp.discriminant(cluster_p, omega))
    expected_hankel_det = sp.factor(discriminant * sp.prod(kappas))
    if sp.simplify(hankel_det - expected_hankel_det) != 0:
        raise RuntimeError("N=3 Hankel determinant/discriminant failed")
    if sp.simplify(hankel_det + resultant) != 0:
        raise RuntimeError("N=3 Hankel/resultant sign failed")
    omega_diagonal = sp.diag(*roots)
    kappa_diagonal = sp.diag(*kappas)
    gram = vandermonde * vandermonde.T
    shifted_gram = vandermonde * omega_diagonal * vandermonde.T
    shifted_hankel = (
        vandermonde * kappa_diagonal * omega_diagonal * vandermonde.T
    )
    v_exact = vandermonde.subs(exact_root_subs)
    omega_exact = omega_diagonal.subs(exact_root_subs)
    gram_exact = v_exact * v_exact.T
    shifted_gram_exact = v_exact * omega_exact * v_exact.T
    hankel_exact = v_exact * kappa_diagonal * v_exact.T
    shifted_hankel_exact = (
        v_exact * kappa_diagonal * omega_exact * v_exact.T
    )
    multiplication_omega = gram_exact.inv() * shifted_gram_exact
    multiplication_kappa = gram_exact.inv() * hankel_exact
    if gram_exact * multiplication_omega != shifted_gram_exact:
        raise RuntimeError("N=3 omega multiplication operator failed")
    if gram_exact * multiplication_kappa != hankel_exact:
        raise RuntimeError("N=3 kappa multiplication operator failed")
    if sp.simplify(
        multiplication_omega * multiplication_kappa
        - multiplication_kappa * multiplication_omega
    ) != sp.zeros(3):
        raise RuntimeError("N=3 multiplication commutator failed")
    if sp.simplify(
        shifted_hankel_exact
        - shifted_gram_exact * gram_exact.inv() * hankel_exact
    ) != sp.zeros(3):
        raise RuntimeError("N=3 shifted Hankel join failed")
    joint_eigenvectors = v_exact.T.inv()
    if sp.simplify(
        multiplication_omega * joint_eigenvectors
        - joint_eigenvectors * omega_exact
    ) != sp.zeros(3):
        raise RuntimeError("N=3 omega joint eigenpairs failed")
    if sp.simplify(
        multiplication_kappa * joint_eigenvectors
        - joint_eigenvectors * kappa_diagonal
    ) != sp.zeros(3):
        raise RuntimeError("N=3 kappa joint eigenpairs failed")

    recurrence_models = {}
    hankel_ranks = {}
    for label, values in kappa_patterns.items():
        substitutions = {
            **exact_root_subs,
            **dict(zip(kappas, values)),
        }
        active_roots = [
            value_root
            for value_root, value_kappa in zip([1, 2, 4], values)
            if value_kappa != 0
        ]
        reduced_denominator = sp.expand(sp.prod(
            zeta - value_root for value_root in active_roots
        ))
        if not active_roots:
            reduced_denominator = sp.Integer(1)
        degree = len(active_roots)
        branch_moments = {
            index: sp.expand(extended_moments[index].subs(substitutions))
            for index in range(7)
        }
        coefficients = sp.Poly(reduced_denominator, zeta).all_coeffs()
        for start in range(7 - degree):
            recurrence_value = sp.expand(sum(
                coefficients[index] * branch_moments[start + degree - index]
                for index in range(degree + 1)
            ))
            if recurrence_value != 0:
                raise RuntimeError(
                    f"N=3 recurrence failed for {label} at {start}"
                )
        branch_hankel = hankel.subs(substitutions)
        rank = int(branch_hankel.rank())
        if rank != degree:
            raise RuntimeError(f"N=3 Hankel rank failed for {label}")
        hankel_ranks[label] = rank
        recurrence_models[label] = {
            "reduced_denominator": encode(reduced_denominator),
            "degree": degree,
            "coefficients": [encode(value) for value in coefficients],
        }

    mu = [sp.Integer(-1), sp.Integer(-2), sp.Integer(-3)]
    lam_nodes = [sp.Integer(5), sp.Integer(6), sp.Integer(7)]
    exact_roots = [sp.Integer(1), sp.Integer(2), sp.Integer(4)]
    resolvent_exact = resolvent.subs(exact_root_subs)
    cauchy_mu = sp.Matrix([
        [1 / (node - root) for root in exact_roots] for node in mu
    ])
    cauchy_lambda = sp.Matrix([
        [1 / (node - root) for root in exact_roots]
        for node in lam_nodes
    ])
    loewner = (
        cauchy_mu * sp.diag(*kappas) * cauchy_lambda.T
    ).applyfunc(sp.cancel)
    shifted_loewner = (
        cauchy_mu
        * sp.diag(*[
            kappa * root for root, kappa in zip(exact_roots, kappas)
        ])
        * cauchy_lambda.T
    ).applyfunc(sp.cancel)
    for row in range(3):
        for column in range(3):
            direct_loewner = sp.cancel(
                (
                    resolvent_exact.subs(zeta, mu[row])
                    - resolvent_exact.subs(zeta, lam_nodes[column])
                )
                / (lam_nodes[column] - mu[row])
            )
            direct_shifted = sp.cancel(
                (
                    mu[row] * resolvent_exact.subs(zeta, mu[row])
                    - lam_nodes[column]
                    * resolvent_exact.subs(zeta, lam_nodes[column])
                )
                / (lam_nodes[column] - mu[row])
            )
            if sp.cancel(direct_loewner - loewner[row, column]) != 0:
                raise RuntimeError("N=3 Loewner factorization failed")
            if sp.cancel(
                direct_shifted - shifted_loewner[row, column]
            ) != 0:
                raise RuntimeError("N=3 shifted-Loewner factorization failed")
    pencil_ratio = sp.factor(
        (
            shifted_loewner - zeta * loewner
        ).det() / loewner.det()
    )
    expected_pencil_ratio = sp.factor(sp.prod(
        root - zeta for root in exact_roots
    ))
    if sp.cancel(pencil_ratio - expected_pencil_ratio) != 0:
        raise RuntimeError("N=3 Loewner generalized spectrum failed")

    document = {
        "schema": "phase3-axial-qnm-intrinsic-deformation-jet-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_DUAL_NUMBER_JET_QNM_SHIFT_UNEVALUATED",
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2 repeated spin-two filtered block",
            "coefficient_ring": "O[epsilon]/(epsilon**2)",
            "ordering_convention": (
                "column coordinates in the ordered dual-number basis "
                "(epsilon,1)"
            ),
            "claim_kind": "formal local algebra over the imported scalar block",
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "schema": (
                    projective["schema"]
                    if name == "projective_cocycle"
                    else smith["schema"]
                ),
                "status": (
                    projective["status"]
                    if name == "projective_cocycle"
                    else smith["status"]
                ),
            }
            for name, path in INPUTS.items()
        },
        "operator_jet": {
            "family": "L_tau=L+tau*S",
            "section": "y_tau=y+tau*x",
            "expanded_mod_tau_squared": encode(jet_remainder),
            "zeroth_order_equation": "L*y=0",
            "first_order_equation": "L*x+S*y=0",
            "identity_verified": True,
            "interpretation": (
                "The repeated scalar block is the first dual-number jet of "
                "the auxiliary intrinsic scalar family."
            ),
            "physical_parameter_tangent_claimed": False,
        },
        "dual_number_connection": {
            "scalar_coefficient": "a_epsilon=a+epsilon*b",
            "basis": ["epsilon", "1"],
            "coordinate_action": (
                "(u,v) -> (a*u+b*v,a*v), representing "
                "(a+epsilon*b)*(u*epsilon+v)"
            ),
            "regular_matrix": matrix_strings(regular_matrix),
            "input_coefficients": ["u", "v"],
            "output_coefficients": [
                encode(value) for value in output_coefficients
            ],
            "identity_verified": True,
            "connection_reading": (
                "If analytic endpoint-compatible scalar connection frames "
                "exist for a(omega,tau), then b(omega)=partial_tau "
                "a(omega,tau)|_{tau=0} in the induced jet frame."
            ),
            "analytic_endpoint_compatible_frames_constructed": False,
        },
        "simple_zero_shift": {
            "hypotheses": [
                "a(omega_n,0)=0",
                "alpha=partial_omega*a(omega_n,0)!=0",
                "beta=partial_tau*a(omega_n,0)",
                "a local differentiable zero branch omega_n(tau) exists",
            ],
            "chain_equation": encode(chain_equation),
            "omega_prime": encode(solved_shift),
            "kappa": encode(kappa),
            "normalization_correspondence": (
                "Under compatible operator/connection normalization, "
                "alpha corresponds to alpha_n and beta to beta_n."
            ),
            "conditional_identification": "beta_n/alpha_n=-omega_n'(0)",
            "identity_verified": True,
            "simple_QNM_supplied": False,
            "beta_n_evaluated": False,
        },
        "conditional_global_connection": {
            "statement": (
                "b(omega)=partial_tau a(omega,tau)|_{tau=0}, and the "
                "complete repeated scalar connection is the first variation "
                "of the scalar connection."
            ),
            "hypotheses": [
                "an analytic scalar family L_tau on a common radial domain",
                "analytic horizon and infinity endpoint frames compatible with tau",
                "a fixed endpoint normalization whose first jet is the repeated block",
            ],
            "hypotheses_certified_here": False,
            "global_b_derivative_established": False,
        },
        "conditional_flux_variation": {
            "base_law": "|A_in(tau)|**2-|A_out(tau)|**2=1",
            "formal_derivative": encode(flux_derivative),
            "real_form": (
                "2*Re(conjugate(A_in)*b_in"
                "-conjugate(A_out)*b_out)=0"
            ),
            "hypotheses": [
                "tau and omega are real",
                "L_tau has the required real/self-adjoint scalar flux structure",
                "endpoint frames preserve the scalar Wronskian normalization",
            ],
            "hypotheses_certified_here": False,
            "flux_theorem_established": False,
        },
        "partial_jet_functor": {
            "base_family": (
                "C(tau)=[[a(tau),d(tau)],[0,f]] with partial_tau*f=0"
            ),
            "ordered_basis": ["epsilon*spin2", "spin2", "spin1"],
            "definitions": [
                "b=partial_tau*a|_0",
                "c=partial_tau*d|_0",
            ],
            "jet_matrix": matrix_strings(partial_jet),
            "inverse": matrix_strings(partial_inverse),
            "inverse_expected": matrix_strings(expected_partial_inverse),
            "multiplicativity": {
                "J_C1": matrix_strings(jet1),
                "J_C2": matrix_strings(jet2),
                "J_C1C2": matrix_strings(jet_of_product),
                "identity": "J(C1*C2)=J(C1)*J(C2)",
                "verified": True,
            },
            "inverse_identity": "J(C**(-1))=J(C)**(-1)",
            "inverse_identity_verified": True,
            "extension_ratios": {
                "partial_tau_inverse_a": "-b/a**2",
                "M": "-d/(a*f)",
                "partial_tau_M": "(b*d-a*c)/(a**2*f)",
            },
            "ratio_identities_verified": True,
            "conditional_endpoint_reading": (
                "Applying J to T_minus, T_plus, or a scattering identity "
                "requires endpoint-compatible partial-jet frames induced "
                "by the same analytic tau-family."
            ),
            "compatible_endpoint_partial_jet_frames_constructed": False,
            "matching_tau_family_constructed": False,
            "T_plus_recovered": False,
            "scattering_identity_recovered": False,
        },
        "conditional_contour_moments": {
            "domain_hypotheses": [
                "D is a bounded domain with positively oriented boundary",
                "a(omega,0) and b(omega) are analytic on a neighborhood of closure(D)",
                "a has no zero on boundary(D)",
                "the zeros omega_j in D are distinct and simple",
                "k is a nonnegative integer",
            ],
            "zero_count": (
                "N_D=(1/(2*pi*I))*integral_boundary(D) "
                "(partial_omega*a/a)*domega"
            ),
            "zero_count_result": "N_D=number of simple zeros in D",
            "local_zero_count_residue": encode(zero_count_residue),
            "moment": (
                "K_k=(1/(2*pi*I))*integral_boundary(D) "
                "omega**k*(b/a)*domega"
            ),
            "moment_result": (
                "K_k=sum_j omega_j**k*b(omega_j)/a'(omega_j)"
            ),
            "local_model": {
                "a": encode(a_local),
                "b": encode(b_local),
                "omega": "omega_j+z",
            },
            "local_moment_residue": encode(moment_residue),
            "single_zero_corollary": (
                "If N_D=1, K_0=b(omega_n)/a'(omega_n)"
            ),
            "compatible_normalization_corollary": (
                "If alpha_n=a'(omega_n) and beta_n=b(omega_n), "
                "then K_0=beta_n/alpha_n=-omega_n'(0)."
            ),
            "endpoint_renormalization": {
                "law": "a_tilde(omega,tau)=u(omega,tau)*a(omega,tau)",
                "hypothesis": (
                    "u is analytic and zero-free on a neighborhood of closure(D)"
                ),
                "b_tilde": "u_tau*a+u*b",
                "quotient_shift": encode(quotient_shift),
                "moment_difference": (
                    "(1/(2*pi*I))*integral_boundary(D) "
                    "omega**k*(u_tau/u)*domega=0"
                ),
                "zero_count_difference": (
                    "(1/(2*pi*I))*integral_boundary(D) "
                    "(partial_omega*u/u)*domega=0"
                ),
                "invariance": (
                    "N_D and every K_k are unchanged by the declared "
                    "zero-free analytic endpoint renormalization."
                ),
            },
            "identity_verified": True,
            "analytic_domain_supplied": False,
            "contour_evaluated": False,
            "physical_QNM_zero_count_certified": False,
        },
        "conditional_jost_determinant_tangent": {
            "column_family": (
                "X_H(tau)=X_H+tau*Y_H and "
                "X_+(tau)=X_++tau*Y_+"
            ),
            "determinant_family": encode(determinant_family),
            "tangent": encode(determinant_tangent),
            "formula": (
                "E_tau=det(X_H,Y_+)+det(Y_H,X_+)"
            ),
            "identity_verified": True,
            "hypotheses": [
                "analytic endpoint-compatible scalar horizon and infinity Jost columns",
                "a fixed determinant normalization compatible with the repeated block",
            ],
            "hypotheses_certified_here": False,
            "physical_jost_tangent_established": False,
        },
        "conditional_finite_cluster_algebra": {
            "hypotheses": [
                "D satisfies the conditional contour hypotheses above",
                "a has exactly N distinct simple zeros omega_j in D",
                "P_D is the monic polynomial product_j(omega-omega_j)",
                "kappa_j=b(omega_j)/a'(omega_j)",
            ],
            "local_algebra": (
                "A_D=O(D)/(a), identified by evaluation with C**N "
                "at the N distinct simple zeros"
            ),
            "complete_moments": (
                "K_k=sum_j omega_j**k*kappa_j for k=0,...,N-1"
            ),
            "vandermonde_completeness": (
                "The moment vector is V*kappa; "
                "det(V)=product_{i<j}(omega_j-omega_i)!=0."
            ),
            "cluster_polynomials": {
                "P_D": "product_j(omega-omega_j)",
                "Q_D": "partial_tau P_D|_0",
                "Q_interpolation": (
                    "Q_D(omega_j)=kappa_j*P_D'(omega_j)"
                ),
                "Q_formula": (
                    "Q_D=sum_j kappa_j*product_{m!=j}(omega-omega_m)"
                ),
            },
            "defect_selectors": {
                "some_defective": (
                    "Q_D is not identically zero iff at least one kappa_j "
                    "is nonzero."
                ),
                "all_defective": (
                    "Res(P_D,Q_D)!=0 iff every kappa_j is nonzero."
                ),
                "count": (
                    "N_defective=N-degree(gcd(P_D,Q_D))."
                ),
            },
            "root_free_reconstruction": {
                "root_power_sums": (
                    "S_k=(1/(2*pi*I))*integral omega**k*a'/a; "
                    "Newton identities reconstruct monic P_D from S_1,...,S_N."
                ),
                "Q_from_moments": (
                    "If P_D=omega**N+p_1*omega**(N-1)+... and "
                    "Q_D=q_0*omega**(N-1)+..., then "
                    "q_m=sum_{j=0}^m p_j*K_{m-j}, p_0=1."
                ),
                "center": "omega_bar=S_1/N",
                "centered_moments": (
                    "Khat_k=sum_j(omega_j-omega_bar)**k*kappa_j"
                ),
                "centered_from_raw": (
                    "Khat_k=sum_{m=0}^k binomial(k,m)"
                    "*(-omega_bar)**(k-m)*K_m"
                ),
            },
            "extension_resolvent": {
                "definition": (
                    "R_D(z)=(1/(2*pi*I))*integral_boundary(D) "
                    "b(omega)/((z-omega)*a(omega))*domega"
                ),
                "partial_fraction": (
                    "R_D(z)=sum_j kappa_j/(z-omega_j)=Q_D(z)/P_D(z)"
                ),
                "reduced_denominator": "P_D/gcd(P_D,Q_D)",
                "laurent_expansion": (
                    "R_D(z)=sum_{k>=0} K_k*z**(-k-1) near infinity"
                ),
            },
            "hankel_theorem": {
                "definition": "H_N=(K_{p+q})_{p,q=0}^{N-1}",
                "factorization": "H_N=V*diag(kappa_j)*V**T",
                "rank": "rank(H_N)=number of nonzero kappa_j",
                "radical_dimension": (
                    "dim(rad(H_N))=number of zero kappa_j"
                ),
                "determinant": (
                    "det(H_N)=disc(P_D)*product_j(kappa_j)"
                ),
                "resultant_sign": (
                    "det(H_N)=(-1)**(N*(N-1)/2)*Res(P_D,Q_D)"
                ),
            },
            "minimal_recurrence": {
                "degree": (
                    "D_def=degree(P_D/gcd(P_D,Q_D))=rank(H_N)"
                ),
                "statement": (
                    "If P_def(z)=z**D_def+c_1*z**(D_def-1)+...+c_D, "
                    "then K_{m+D_def}+c_1*K_{m+D_def-1}+...+c_D*K_m=0."
                ),
                "zero_sequence_convention": (
                    "If D_def=0, P_def=1 and all K_m vanish."
                ),
            },
            "joint_multiplication_operators": {
                "organizing_class": (
                    "kappa_D=[b]*[a']**(-1) in A_D=O(D)/(a)"
                ),
                "matrices": [
                    "G=V*V**T",
                    "G1=V*Omega*V**T",
                    "H=V*Kappa*V**T",
                    "H1=V*Kappa*Omega*V**T",
                ],
                "operators": [
                    "M_omega=G**(-1)*G1",
                    "M_kappa=G**(-1)*H",
                ],
                "identities": [
                    "[M_omega,M_kappa]=0",
                    "H1=G1*G**(-1)*H",
                    "the joint eigenpairs are (omega_j,kappa_j)",
                    "rank(M_kappa)=number of defective roots",
                ],
            },
            "conditional_loewner_theorem": {
                "definitions": [
                    "L_pq=(R_D(mu_p)-R_D(lambda_q))/(lambda_q-mu_p)",
                    "Ls_pq=(mu_p*R_D(mu_p)-lambda_q*R_D(lambda_q))/(lambda_q-mu_p)",
                ],
                "hypotheses": [
                    "left and right nodes are distinct and avoid the poles",
                    "each node set contains at least D_def generic nodes",
                    "the corresponding Cauchy evaluation matrices have full column rank",
                ],
                "factorizations": [
                    "L=C_mu*diag(kappa_j)*C_lambda**T",
                    "Ls=C_mu*diag(kappa_j*omega_j)*C_lambda**T",
                ],
                "conclusion": (
                    "rank(L)=D_def and, after a rank-D_def compression, "
                    "the finite generalized eigenvalues of (Ls,L) are "
                    "exactly the defective omega_j."
                ),
                "sampling_nodes_supplied": False,
                "rank_or_eigenvalues_computed": False,
            },
            "conditional_reality_symmetry": {
                "hypotheses": [
                    "a(-conjugate(omega))=conjugate(a(omega))",
                    "b(-conjugate(omega))=conjugate(b(omega))",
                    "D is invariant under omega -> -conjugate(omega)",
                ],
                "consequences": [
                    "omega_j -> -conjugate(omega_j)",
                    "kappa_j -> -conjugate(kappa_j)",
                    "R_D(-conjugate(z))=conjugate(R_D(z))",
                    "K_k=(-1)**(k+1)*conjugate(K_k)",
                    "even K_k are purely imaginary and odd K_k are real",
                ],
                "hypotheses_certified_here": False,
                "physical_reality_consequences_established": False,
            },
            "n3_exact_model": {
                "P": encode(cluster_p),
                "Q": encode(cluster_q),
                "vandermonde": matrix_strings(vandermonde),
                "vandermonde_determinant": encode(vandermonde_det),
                "Q_at_roots": [
                    encode(value) for value in interpolation_values
                ],
                "resultant": encode(resultant),
                "resultant_product": encode(resultant_product),
                "gcd_degrees": {
                    label: int(degree)
                    for label, degree in gcd_degrees.items()
                },
                "power_sums": {
                    str(degree): encode(value)
                    for degree, value in power_sums.items()
                },
                "newton_P": encode(newton_p),
                "weighted_moments": {
                    str(degree): encode(value)
                    for degree, value in weighted_moments.items()
                },
                "Q_from_moments": encode(q_from_moments),
                "centroid": encode(centroid),
                "centered_moments": {
                    str(degree): encode(value)
                    for degree, value in centered_moments.items()
                },
                "extension_resolvent": encode(resolvent),
                "rational_resolvent": encode(rational_resolvent),
                "laurent_through_K5": encode(laurent_series),
                "Hankel": matrix_strings(hankel),
                "Hankel_factor": matrix_strings(hankel_factor),
                "Hankel_determinant": encode(hankel_det),
                "discriminant": encode(discriminant),
                "Hankel_ranks": hankel_ranks,
                "G": matrix_strings(gram),
                "G1": matrix_strings(shifted_gram),
                "H1": matrix_strings(shifted_hankel),
                "joint_operator_root_specialization": ["1", "2", "4"],
                "M_omega": matrix_strings(multiplication_omega),
                "M_kappa": matrix_strings(multiplication_kappa),
                "joint_eigenvectors": matrix_strings(joint_eigenvectors),
                "multiplication_commutator": matrix_strings(
                    sp.simplify(
                        multiplication_omega * multiplication_kappa
                        - multiplication_kappa * multiplication_omega
                    )
                ),
                "recurrence_models": recurrence_models,
                "Loewner_left_nodes": [encode(value) for value in mu],
                "Loewner_right_nodes": [
                    encode(value) for value in lam_nodes
                ],
                "Loewner": matrix_strings(loewner),
                "shifted_Loewner": matrix_strings(shifted_loewner),
                "pencil_determinant_ratio": encode(pencil_ratio),
                "identities_verified": True,
            },
            "analytic_cluster_supplied": False,
            "actual_N_computed": False,
            "actual_P_D_computed": False,
            "actual_Q_D_computed": False,
            "actual_defective_count_computed": False,
            "actual_resolvent_computed": False,
            "actual_hankel_rank_computed": False,
            "actual_loewner_spectrum_computed": False,
        },
        "claim_flags": {
            "operator_dual_number_jet_exact": True,
            "dual_number_regular_representation_exact": True,
            "simple_zero_shift_identity_exact": True,
            "compatible_normalization_ratio_identity_exact": True,
            "conditional_contour_moment_residue_identity_exact": True,
            "zero_free_endpoint_renormalization_invariance_exact": True,
            "conditional_jost_determinant_tangent_identity_exact": True,
            "partial_jet_functor_exact": True,
            "partial_jet_extension_ratio_identities_exact": True,
            "conditional_finite_cluster_algebra_exact": True,
            "n3_cluster_model_independently_exact": True,
            "conditional_extension_resolvent_hankel_recurrence_exact": True,
            "conditional_generic_loewner_theorem_exact": True,
            "analytic_endpoint_scalar_frames_constructed": False,
            "analytic_contour_domain_supplied": False,
            "contour_moment_evaluated": False,
            "physical_cluster_data_computed": False,
            "physical_extension_resolvent_or_hankel_computed": False,
            "physical_loewner_rank_or_spectrum_computed": False,
            "physical_reality_symmetry_certified": False,
            "compatible_endpoint_partial_jet_frames_constructed": False,
            "T_plus_recovered_by_partial_jet": False,
            "scattering_identity_recovered_by_partial_jet": False,
            "global_b_derivative_established": False,
            "physical_QNM_supplied": False,
            "beta_n_evaluated": False,
            "physical_QNM_smith_case_selected": False,
            "EP2_established": False,
            "physical_QNM_fredholm_realization_constructed": False,
            "flux_theorem_established": False,
        },
        "does_not_establish": [
            "an analytic endpoint-compatible auxiliary scalar scattering family",
            "the value or nonvanishing of b at any physical QNM",
            "the value or nonvanishing of beta_n",
            "a physical QNM Smith branch or exceptional point",
            "a physical analytic Fredholm realization or resolvent pole",
            "a real-axis or horizon flux theorem for the auxiliary family",
            "an evaluated contour moment or a certified QNM zero count",
            "analytic endpoint-compatible scalar Jost columns",
            "an actual cluster size, cluster polynomial, resultant, gcd, or defective-mode count",
            "an evaluated extension resolvent, Hankel rank, recurrence, or Loewner spectrum",
            "the conditional reality symmetry hypotheses for the physical scalar frames",
            "the outgoing map T_plus or a physical scattering identity from the partial jet alone",
            "a new physical coupling or changed fundamental theory",
        ],
        "provenance": {
            "producer": "produce.py",
            "verifier": "verify.py",
            "schema": {
                "path": "schema.json",
                "sha256": sha256(SCHEMA),
            },
            "arithmetic": "exact SymPy polynomial and matrix algebra",
            "external_scientific_inputs": [],
        },
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


def main() -> None:
    document = produce()
    print(
        "PASS:",
        document["status"],
        "->",
        OUTPUT,
    )


if __name__ == "__main__":
    main()
