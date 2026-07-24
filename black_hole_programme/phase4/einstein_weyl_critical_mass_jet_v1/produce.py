#!/usr/bin/env python3
"""Produce the exact critical Einstein--Weyl parent mass-jet certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

IMPORTS = {
    "second_order_parent": (
        ROOT
        / "black_hole_programme/phase4/second_order_parent_flux_v1/certificate.json"
    ),
    "parent_resolvent": (
        ROOT
        / "black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/certificate.json"
    ),
    "intrinsic_radial_partial_jet": (
        ROOT
        / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "intrinsic_horizon_moving_phase": (
        ROOT
        / "black_hole_programme/phase3/axial_partial_jet_horizon_moving_phase_v1/certificate.json"
    ),
    "intrinsic_infinity_reduced_phase": (
        ROOT
        / "black_hole_programme/phase3/axial_partial_jet_infinity_reduced_phase_preflight_v1/certificate.json"
    ),
    "physical_connection_ep2": (
        ROOT
        / "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_matrix(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(entry) == 0 for entry in matrix)


def exact_data() -> dict:
    # A finite exact representative verifies the variational algebra under the
    # only operator hypotheses used in the theorem: formal self-adjointness of
    # E and algebraicity/self-adjointness of A.
    h1, h2, p1, p2, mass = sp.symbols("h1 h2 p1 p2 mass")
    e11, e12, e22 = sp.symbols("e11 e12 e22")
    a11, a12, a22 = sp.symbols("a11 a12 a22")
    h = sp.Matrix([h1, h2])
    phi = sp.Matrix([p1, p2])
    E = sp.Matrix([[e11, e12], [e12, e22]])
    A = sp.Matrix([[a11, a12], [a12, a22]])
    lagrangian = (
        (phi.T * E * h)[0]
        - sp.Rational(1, 2) * (phi.T * A * phi)[0]
        + mass * sp.Rational(1, 2) * (h.T * E * h)[0]
    )
    grad_phi = sp.Matrix([sp.diff(lagrangian, p1), sp.diff(lagrangian, p2)])
    grad_h = sp.Matrix([sp.diff(lagrangian, h1), sp.diff(lagrangian, h2)])
    assert zero_matrix(grad_phi - (E * h - A * phi))
    assert zero_matrix(grad_h - (E * phi + mass * E * h))

    # Differentiating (E+m A)phi(m)=0 and using E h=A phi gives
    # E(h+partial_m phi)=0.  The exact residual is checked algebraically.
    phid1, phid2 = sp.symbols("phid1 phid2")
    phidot = sp.Matrix([phid1, phid2])
    derivative_equation = E * phidot + A * phi
    lift_equation = E * h - A * phi
    kernel_residual = E * (h + phidot)
    assert zero_matrix(kernel_residual - lift_equation - derivative_equation)

    # TT difference quotient.  A=I on this sector and E commutes with E+mI.
    E_num = sp.Matrix([[2, 1], [1, 3]])
    I2 = sp.eye(2)
    lhs = (E_num * (E_num + mass * I2)).inv()
    rhs = (E_num.inv() - (E_num + mass * I2).inv()) / mass
    assert zero_matrix(lhs - rhs)
    rhs_limit = rhs.applyfunc(lambda entry: sp.limit(entry, mass, 0))
    assert zero_matrix(rhs_limit - E_num.inv() ** 2)

    # Finite-mass branch sign in the confluent basis
    # E=u0, X=(u_mass-u0)/mass.
    C_mass = sp.Matrix([[1, -2 / mass], [0, -1]])
    assert C_mass**2 == sp.eye(2)
    N_mass = -mass * (C_mass + sp.eye(2)) / 2
    N_zero = N_mass.applyfunc(lambda entry: sp.limit(entry, mass, 0))
    expected_N = sp.Matrix([[0, 1], [0, 0]])
    assert N_zero == expected_N
    assert N_zero**2 == sp.zeros(2)

    # Critical cancellation of opposite-sign branch pairings.
    ee, ex, xe, xx = sp.symbols("ee ex xe xx")
    omega_mass_form = (
        ee - (ee + mass * (ex + xe) + mass**2 * xx)
    ) / mass
    assert sp.limit(omega_mass_form, mass, 0) == -(ex + xe)

    # Massive asymptotic phase and Schwarzschild Coulomb exponent.
    omega, M, rstar = sp.symbols("omega M rstar", nonzero=True)
    k = sp.sqrt(omega**2 - mass)
    dk0 = sp.simplify(sp.diff(k, mass).subs(mass, 0))
    # The chosen analytic branch has sqrt(omega**2)=omega.
    dk0 = dk0.xreplace({sp.sqrt(omega**2): omega})
    assert sp.simplify(dk0 + 1 / (2 * omega)) == 0
    phase_plus_ratio = sp.I * rstar * dk0
    phase_minus_ratio = -sp.I * rstar * dk0
    assert sp.simplify(phase_plus_ratio + sp.I * rstar / (2 * omega)) == 0
    assert sp.simplify(phase_minus_ratio - sp.I * rstar / (2 * omega)) == 0

    coulomb = M * (mass - 2 * omega**2) / (sp.I * k)
    coulomb0 = sp.simplify(coulomb.subs(mass, 0)).xreplace(
        {sp.sqrt(omega**2): omega}
    )
    dcoulomb0 = sp.simplify(sp.diff(coulomb, mass).subs(mass, 0)).xreplace(
        {
            sp.sqrt(omega**2): omega,
            (omega**2) ** sp.Rational(3, 2): omega**3,
        }
    )
    assert sp.simplify(coulomb0 - 2 * sp.I * M * omega) == 0
    assert sp.simplify(dcoulomb0) == 0

    zeta = sp.symbols("zeta")
    k_scaled = omega * sp.sqrt(1 - zeta)
    coulomb_scaled = M * omega * (zeta - 2) / (sp.I * sp.sqrt(1 - zeta))
    assert sp.diff(coulomb_scaled, zeta).subs(zeta, 0) == 0

    # Conditional implicit-root and threshold-scaling algebra.
    a_w, a_m, b = sp.symbols("a_w a_m b", nonzero=True)
    root_slope = -a_m / a_w
    assert sp.simplify(root_slope.subs(a_m, -b) - b / a_w) == 0
    ell = sp.symbols("ell", integer=True, positive=True)
    exponent_b = -(ell + 3)
    exponent_a2 = -2 * (ell + 1)
    exponent_inverse_shear = sp.simplify(exponent_b - exponent_a2)
    assert exponent_inverse_shear == ell - 1

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
        }
        for name, path in IMPORTS.items()
    }

    return {
        "schema": "einstein-weyl-critical-mass-jet-v1",
        "status": "EXACT_CRITICAL_MASS_PARENT_JET_RADIAL_CROSSWALK_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "literature_context": {
            "einstein_weyl_qnms": {
                "arxiv": "2412.15037v3",
                "journal": "Phys. Rev. D 111, 064059 (2025)",
                "verified_context": [
                    "action convention R-alpha*C^2 with alpha=1/(2*mu_lit^2)",
                    "Schwarzschild carries unchanged GR modes and massive spin-two vector/tensor modes",
                    "massive infinity momentum k=sqrt(omega^2-mu_lit^2)",
                    "massive Coulomb exponent x=M*(mu_lit^2-2*omega^2)/(i*k)",
                    "the massive tensor QNM tends to the massless GR mode as mu_lit tends to zero",
                ],
                "role": "context only; exact claims below are rederived locally",
            },
            "critical_gravity": {
                "arxiv": "1106.4657v3",
                "journal": "Phys. Rev. D 84, 064001 (2011)",
                "verified_context": [
                    "massive ghostlike and massless spin-two branches coalesce at criticality",
                    "the coalescence produces logarithmic modes in the AdS critical-gravity setting",
                ],
                "scope_warning": "the present result is asymptotically flat Schwarzschild, not an AdS boundary-condition theorem",
            },
        },
        "normalization": {
            "mass_parameter": (
                "mass denotes the signed squared-mass coefficient in the "
                "rescaled parent equations; its exact relation to a literature "
                "mu_lit^2 depends on the chosen sign and Einstein-operator normalization"
            ),
            "regular_carrier": "phi=q=delta Ric-(1/6)g delta R",
            "conventional_auxiliary_relation": (
                "in the R-alpha*C^2 convention of arXiv:2412.15037, "
                "f_EW=-phi/mu_lit^2"
            ),
            "intrinsic_parameter_candidate": "tau=-mass",
        },
        "parent_mass_family": {
            "action": (
                "S=4*alpha_W*Integral[phi.E(h)"
                "-(1/2)phi.A(phi)+(mass/2)h.E(h)]"
            ),
            "hypotheses": [
                "E is the formally self-adjoint linearized Einstein operator",
                "A(phi)=phi-g*trace(phi) is algebraic and self-adjoint",
                "Euler transgression is treated separately",
            ],
            "equations": [
                "E(h)=A(phi)",
                "E(phi)+mass*E(h)=0",
                "(E+mass*A)(phi)=0",
            ],
            "massive_constraint": {
                "divergence": "div(A(phi))=0 for mass nonzero",
                "trace": "trace(E(phi))=0 under the divergence constraint, so -3*mass*trace(phi)=0",
                "conclusion": "trace(phi)=0 and div(phi)=0 for mass nonzero",
            },
        },
        "critical_mass_derivative": {
            "branch_equation": "(E+mass*A)phi(mass)=0",
            "derivative_at_zero": "E(phi_dot)+A(phi_0)=0",
            "metric_lift": "E(h)=A(phi_0)",
            "kernel_identity": "E(h+phi_dot)=0",
            "quotient_identity": "[h]=-[partial_mass phi] in solutions modulo ker(E)",
            "tau_form": "for tau=-mass, [h]=[partial_tau phi] at tau=0",
        },
        "tt_difference_quotient": {
            "scope": "transverse-traceless spin-two subspace where A=I",
            "operator": "E*(E+mass)",
            "inverse": "(1/mass)*(E^-1-(E+mass)^-1)",
            "critical_limit": "E^-2",
            "scope_warning": "outside TT retain A and operator ordering",
        },
        "endpoint_phase": {
            "momentum": "k=sqrt(omega^2-mass)",
            "branch": "k(omega,0)=omega",
            "partial_mass_k_at_zero": "-1/(2*omega)",
            "phase_derivatives": {
                "exp(+i*k*rstar)": "-i*rstar/(2*omega) times the base phase",
                "exp(-i*k*rstar)": "+i*rstar/(2*omega) times the base phase",
            },
            "schwarzschild_coulomb_exponent": (
                "x=M*(mass-2*omega^2)/(i*sqrt(omega^2-mass))"
            ),
            "coulomb_values": {
                "x_at_zero": "2*i*M*omega",
                "partial_mass_x_at_zero": "0",
            },
            "new_endpoint_reading": (
                "the first mass jet produces the linear-rstar generalized phase "
                "but no first-order Coulomb log(r) and no horizon-exponent shift"
            ),
            "horizon_import": (
                "the independent intrinsic endpoint certificate has "
                "dot_lambda_H=0, but equality of its tau with -mass is not used"
            ),
            "uniform_variable": "zeta=mass/omega^2",
            "analytic_wedge": "|zeta|<1 on the selected square-root branch",
        },
        "finite_mass_branch_sign": {
            "basis": "E=u_0, X=(u_mass-u_0)/mass",
            "matrix": "[[1,-2/mass],[0,-1]]",
            "involution": True,
            "finite_limit": False,
            "renormalized_operator": "N_mass=-(mass/2)*(C_mass+I)",
            "limit": "[[0,1],[0,0]]",
            "nilpotent_square": "N_0^2=0",
            "critical_pairing_limit": (
                "(Omega_E(u0,u0')-Omega_E(u_mass,u_mass'))/mass "
                "tends to -Omega_E(u0,X')-Omega_E(X,u0')"
            ),
        },
        "conditional_qnm_slope": {
            "hypotheses": [
                "the physical massive tensor branch reduces to the same scalar Jost family",
                "compatible mass-analytic moving endpoint frames exist",
                "b=-partial_mass a at mass=0 in the certified triangular normalization",
                "the scalar QNM zero is simple",
            ],
            "identity": "d omega_n/d mass=b(omega_n)/a'(omega_n)",
            "intrinsic_tau_identity": "d omega_n/d tau=-b/a'",
            "status": "CONDITIONAL_PHYSICAL_MASS_CROSSWALK_OPEN",
        },
        "conditional_threshold_scaling": {
            "ansatz": (
                "a_ell(omega,mass)=omega^(-(ell+1))*"
                "F_ell(mass/omega^2)+lower terms"
            ),
            "consequence": "b_ell/a_ell^2=O(omega^(ell-1))",
            "ell_two": "O(omega)",
            "status": "PREDICTION_NOT_UNIFORM_MATCHING_THEOREM",
        },
        "crosswalk_gate": {
            "existing_intrinsic_family": "B(tau)=B0+tau*B1",
            "existing_scope": (
                "exact local radial partial jet with compatible endpoint "
                "mass interpretation explicitly absent"
            ),
            "decisive_test": (
                "[I_mass]=[I_Bach] in C(r)/K_U C(r), after reducing the "
                "finite-mass axial helicity-two system to the certified RW companion gauge"
            ),
            "required_steps": [
                "derive the finite-mass axial first-order carrier system in the same conventions",
                "differentiate it with respect to the signed mass coefficient at zero",
                "reduce the helicity-two part to the certified RW companion frame",
                "compute the projective cocycle",
                "solve or obstruct the K_U coboundary equation for the difference",
                "then construct compatible moving massive endpoint frames",
            ],
            "status": "OPEN_NOT_ASSUMED",
        },
        "maxwell_limit": {
            "literature_observation": (
                "the finite-mass axial vector polarizations become target-gauge "
                "at zero mass"
            ),
            "candidate_reading": (
                "the certified Maxwell quotient is a Stueckelberg-rescaled "
                "helicity-one remnant"
            ),
            "status": "INTERPRETATION_NOT_EXACT_FINITE_MASS_SCALING_CERTIFICATE",
        },
        "claim_flags": {
            "parent_mass_variation_exact": True,
            "mass_derivative_modulo_einstein_kernel_exact": True,
            "tt_difference_quotient_exact": True,
            "finite_mass_branch_sign_singular_limit_exact": True,
            "nilpotent_residue_exact": True,
            "massive_momentum_derivative_exact": True,
            "coulomb_exponent_first_mass_derivative_zero": True,
            "intrinsic_horizon_dot_lambda_zero_imported": True,
            "physical_mass_jet_equals_intrinsic_radial_tau": False,
            "physical_b_equals_minus_mass_derivative_of_jost": False,
            "physical_massive_qnm_slope_certified": False,
            "threshold_inverse_shear_asymptotic_certified": False,
            "maxwell_stueckelberg_limit_certified": False,
            "fredholm_double_pole_established": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "that the certified intrinsic axial radial tau equals minus the physical spin-two squared mass",
            "equality of the massive and Bach projective cocycle classes",
            "a compatible massive horizon/infinity Jost family in the certified radial frame",
            "b=-partial_mass a for the physical scalar Jost coefficient",
            "a certified massive-spin-two QNM derivative or eikonal benchmark",
            "a threshold O(omega) inverse-shear theorem",
            "a smooth finite-mass Stueckelberg construction of the Maxwell quotient",
            "a physical Fredholm double pole or generalized ringdown theorem",
            "a nonlocal C classification or any quantum positivity statement",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "einstein-weyl-critical-mass-jet-receipt-v1",
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "commands": [
            "python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.produce",
            "python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.test_mass_jet",
        ],
        "claim_boundary": (
            "exact covariant parent mass jet; physical axial radial/Jost "
            "crosswalk remains open"
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
