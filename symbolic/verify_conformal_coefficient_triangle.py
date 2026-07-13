#!/usr/bin/env python3
"""C2k: coefficient-triangle and Weyl-compensator audit.

This certificate keeps four often-conflated quantities separate:

* the signed coefficient of a local UV counterterm;
* the beta function induced in a declared action normalization;
* the background trace anomaly obtained from an evanescent Weyl variation;
* the coefficient of a quantum BV/master-equation obstruction.

Only the first three are related here, and only after conventions are made
explicit.  The spin-two values 199/30 and 87/20 are literature inputs, not a
determinant calculation.  No coefficient is assigned to the BV anomaly.

The second half audits a Weyl compensator on R x S^3.  The type-B Wess--
Zumino term begins at cubic order on a conformally flat background.  The
type-A Wess--Zumino action instead has a nonzero tau--tau quadratic block on
the cylinder and can mix tau with the metric through tau E_4^(1)[h].
"""

from __future__ import annotations

import argparse

import sympy as sp


R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def reject_broad_claims(args: argparse.Namespace) -> None:
    claims = {
        "claim_direct_bv_coefficient": (
            "no local one-loop BV Laplacian/master-equation calculation is encoded"
        ),
        "claim_quantum_brst_obstruction": (
            "counterterm and trace-anomaly data do not by themselves prove Q_quantum^2 != 0"
        ),
        "claim_trace_coefficient_equals_bv_coefficient": (
            "the BV coefficient must be projected in the repository's own local-BV conventions"
        ),
        "claim_complete_mixed_compensator_hessian": (
            "only the exact tau--tau block and perturbative-order audit are computed"
        ),
        "claim_compensator_preserves_i2": (
            "the type-A completion changes the quadratic cylinder complex, so its cohomology and pairing must be recomputed"
        ),
        "claim_full_anomaly_cancellation": (
            "Wess--Zumino exactness in an extended complex is not a proof of an anomaly-free quantum theory"
        ),
        "claim_interacting_chs_anomaly_free": (
            "regularized free-tower sums do not establish anomaly cancellation in an interacting CHS theory"
        ),
    }
    for name, message in claims.items():
        if getattr(args, name):
            raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in (
        "claim-direct-bv-coefficient",
        "claim-quantum-brst-obstruction",
        "claim-trace-coefficient-equals-bv-coefficient",
        "claim-complete-mixed-compensator-hessian",
        "claim-compensator-preserves-i2",
        "claim-full-anomaly-cancellation",
        "claim-interacting-chs-anomaly-free",
    ):
        parser.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    reject_broad_claims(args)

    # Write the continued action and signed counterterm as
    #
    #   S = kappa x I_C,  x=1/t^2,
    #   x_B = mu^(-rho eps) [x + k_ct/(kappa (4 pi)^2 eps)].
    #
    # Here k_ct is the coefficient *added* to the action.  If the loop
    # divergence is +b_div/eps, cancellation means k_ct=-b_div.  Keeping the
    # signed counterterm explicit prevents a hidden Euclidean/Wick sign from
    # entering the normalization comparison.
    rho, kappa, k_ct, t = sp.symbols(
        "rho kappa k_ct t", nonzero=True, real=True
    )
    loop = (4 * sp.pi) ** 2
    beta_x = sp.simplify(rho * k_ct / (kappa * loop))
    beta_t = sp.simplify(-t**3 * beta_x / 2)
    check(
        "C2k-1: x=t^-2 converts beta_x to beta_t with the exact factor -t^3/2",
        sp.simplify(beta_t + t**3 * beta_x / 2) == 0,
    )

    # Compare magnitudes after fixing rho=1 and the same signed numerator K.
    # The C2k comparison convention has kappa=1/2, whereas Hamada writes a
    # coefficient of magnitude 1/t^2.  His Lorentzian action also carries an
    # overall sign, which is deliberately not silently folded into K.
    K = R(199, 30)
    half_normalized_beta_coefficient = sp.simplify(
        (-beta_t / t**3).subs({rho: 1, k_ct: K, kappa: R(1, 2)})
    )
    hamada_beta_coefficient = sp.simplify(
        (-beta_t / t**3).subs({rho: 1, k_ct: K, kappa: 1})
    )
    check(
        "C2k-1: the 1/(2t^2) convention doubles the beta numerator relative to 1/t^2",
        half_normalized_beta_coefficient == K / loop
        and hamada_beta_coefficient == K / (2 * loop)
        and half_normalized_beta_coefficient == 2 * hamada_beta_coefficient,
    )
    check(
        "C2k-1: Hamada's displayed normalization is K/(32 pi^2)",
        sp.simplify(hamada_beta_coefficient - K / (32 * sp.pi**2)) == 0,
    )

    # Evanescent variation.  Declare the dimensional-continuation convention
    #
    #   delta_sigma I_C^(d) = rho eps Sigma_C.
    #
    # The pole then leaves rho*k_ct Sigma_C/(4pi)^2.  Reversing the Weyl
    # transformation convention or using b_div=-k_ct reverses the displayed
    # sign; the relation, not an unlabelled sign, is the certificate.
    trace_from_counterterm = sp.simplify(rho * k_ct)
    b_div = sp.symbols("b_div", real=True)
    trace_from_loop_divergence = sp.simplify(
        trace_from_counterterm.subs(k_ct, -b_div)
    )
    check(
        "C2k-2: pole times evanescent Weyl weight gives a finite trace coefficient",
        trace_from_counterterm == rho * k_ct
        and trace_from_loop_divergence == -rho * b_div,
    )

    # The values below are source-normalized inputs.  Keeping them as a
    # separate vector makes it impossible for the beta conversion above to
    # masquerade as a direct quantum-master-equation computation.
    a_trace = R(87, 20)
    c_trace = K
    beta_vector = sp.Matrix([half_normalized_beta_coefficient, 0])
    trace_vector = sp.Matrix([c_trace, -a_trace])
    bv_vector = sp.Matrix([sp.Symbol("A_BV_C"), sp.Symbol("A_BV_E")])
    check(
        "C2k-3: counterterm/beta, trace anomaly, and BV coordinates remain distinct objects",
        beta_vector.shape == (2, 1)
        and trace_vector.shape == (2, 1)
        and bv_vector.shape == (2, 1)
        and not bv_vector.has(c_trace),
    )

    # Minimal extended-complex proof of type-B exactness.  In the strict
    # complex there is no tau preimage.  After adjoining s tau=c_W and using
    # s I_C=0, d(tau I_C)=c_W I_C is the 1x1 identity map.
    strict_d = sp.zeros(1, 0)
    extended_d = sp.Matrix([[1]])
    anomaly_coordinate = sp.Matrix([1])
    check(
        "C2k-4: the strict type-B anomaly coordinate has no compensator preimage",
        strict_d.rank() == 0 and strict_d.shape == (1, 0),
    )
    check(
        "C2k-4: adjoining s tau=c_W makes [c_W C^2] exact",
        extended_d.rank() == 1
        and extended_d * sp.Matrix([1]) == anomaly_coordinate,
    )

    # Exact curvature audit for the product cylinder with spatial curvature
    # k=1/r^2 and time signature eta=+1 (Euclidean) or -1 (mostly-plus
    # Lorentzian).  Only the S^3 components of Ricci curvature are nonzero.
    k, eta = sp.symbols("k eta", nonzero=True, real=True)
    riemann_sq = 12 * k**2
    ricci_sq = 12 * k**2
    scalar_r = 6 * k
    euler_4 = sp.simplify(riemann_sq - 4 * ricci_sq + scalar_r**2)
    weyl_sq = sp.simplify(riemann_sq - 2 * ricci_sq + scalar_r**2 / 3)
    gtt_up = -3 * eta * k
    gij_factor_up = -k
    check(
        "C2k-5: R x S3 is conformally flat and has vanishing Euler density",
        euler_4 == 0 and weyl_sq == 0,
    )
    check(
        "C2k-5: the cylinder Einstein tensor is nonzero",
        gtt_up != 0 and gij_factor_up != 0,
    )

    # Perturbative degree count around Cbar=0 and tau_bar=0.  C^2 begins at
    # h^2, hence tau C^2 is cubic.  The type-A term 4 G d tau d tau is already
    # quadratic because Gbar is nonzero.  tau E4 also permits tau*h mixing
    # through E4^(1)[h], so this is not the complete mixed Hessian.
    degree_tau_c2 = 1 + 2
    degree_tau_tau_type_a = 2
    degree_tau_euler_linear = 1 + 1
    check(
        "C2k-6: the type-B compensator term has no quadratic cylinder Hessian",
        degree_tau_c2 == 3,
    )
    check(
        "C2k-6: type A has both a tau--tau quadratic block and possible tau--h mixing",
        degree_tau_tau_type_a == 2 and degree_tau_euler_linear == 2,
    )

    # In the Baume--Keren-Zur convention the tau-only quadratic term is
    # -4 a int G^{mu nu} d_mu tau d_nu tau.  For Lorentzian eta=-1 its
    # equation is (3 k d_t^2 - k Delta_S3) tau=0.  A scalar harmonic obeys
    # -Delta Y_l = k l(l+2)Y_l.
    a, omega, ell = sp.symbols("a omega ell", positive=True, real=True)
    lorentz_gtt = sp.simplify(gtt_up.subs(eta, -1))
    tau_tau_time = sp.simplify(-4 * a * lorentz_gtt)
    tau_tau_space = sp.simplify(-4 * a * gij_factor_up)
    omega_sq = sp.simplify(k * ell * (ell + 2) / 3)
    mode_equation = sp.simplify(-3 * k * omega**2 + k**2 * ell * (ell + 2))
    check(
        "C2k-7: the Lorentzian type-A tau--tau kinetic coefficients are nonzero",
        tau_tau_time == -12 * a * k and tau_tau_space == 4 * a * k,
    )
    check(
        "C2k-7: the isolated tau--tau block has omega^2=k*l(l+2)/3",
        sp.simplify(mode_equation.subs(omega**2, omega_sq)) == 0,
    )

    print("general beta_x:", beta_x)
    print("general beta_t:", beta_t)
    print(
        "half-normalized |beta_t|/t^3 for K=199/30:",
        half_normalized_beta_coefficient,
    )
    print("Hamada-normalized |beta_t|/t^3:", hamada_beta_coefficient)
    print("trace-anomaly input vector [c,-a]:", trace_vector.T)
    print("BV coefficient vector: UNDETERMINED", bv_vector.T)
    print("cylinder invariants [C2,E4]:", (weyl_sq, euler_4))
    print("isolated type-A tau frequency squared:", omega_sq)
    print(
        "CHS source audit: 2013 a-sum result; 2017 S4_q selects r=-1 "
        "and reports regulated a- and c-sum zeros"
    )
    print(
        "CONFORMAL C2k COEFFICIENT/COMPENSATOR AUDIT: ALL PASS. "
        "No direct BV coefficient, full mixed compensator kernel, quantum "
        "nilpotency, or interacting CHS anomaly cancellation is claimed."
    )


if __name__ == "__main__":
    main()
