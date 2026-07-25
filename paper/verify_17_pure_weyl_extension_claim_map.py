#!/usr/bin/env python3
"""Independent semantic, symbolic, and provenance verifier for Paper 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
DEFAULT_MAP = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def require_flag(data: dict, key: str, value: bool, label: str) -> None:
    actual = data.get("claim_flags", {}).get(key)
    if actual is not value:
        fail(f"{label} flag drift: {key}={actual!r}")


def verify_cocycle(claims: dict) -> None:
    r, omega = sp.symbols("r omega", nonzero=True)
    I = sp.I
    f = (r - 2) / r
    U = omega**2 - f * (6 / r**2 - 6 / r**3)

    def D(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(f * sp.diff(expr, r))

    q = sp.sympify(
        claims["exact_identities"]["bach_cocycle_normal_form"]["q"],
        locals={"I": I, "r": r, "omega": omega},
    )
    representative = sp.sympify(
        claims["exact_identities"]["bach_cocycle_normal_form"]["representative"],
        locals={"I": I, "r": r, "omega": omega},
    )
    Kq = D(D(D(q))) + 4 * U * D(q) + 2 * D(U) * q
    cocycle = I * (r - 2) * (2 * r * omega**2 + 3 * omega**2 + 12)
    cocycle /= 5 * r**4 * omega
    if sp.cancel(cocycle - Kq - representative) != 0:
        fail("Bach cocycle normal-form identity failed")
    slope = sp.limit(q / r, r, sp.oo)
    declared_slope = sp.sympify(
        claims["exact_identities"]["forced_gauge_asymptotic"][
            "q_slope_at_infinity"
        ],
        locals={"I": I, "omega": omega},
    )
    if sp.simplify(slope - declared_slope) != 0:
        fail("forced equivalence-gauge slope identity failed")
    if sp.simplify(4 * omega**2 * slope + I * omega / 2) != 0:
        fail("forced equivalence-gauge constant matching failed")

    q_minus_one = sp.sympify(
        claims["exact_identities"]["threshold_static_exactness"]["q_minus_one"],
        locals={"I": I, "r": r},
    )
    U0 = sp.simplify(U - omega**2)
    K0q = D(D(D(q_minus_one))) + 4 * U0 * D(q_minus_one)
    K0q += 2 * D(U0) * q_minus_one
    threshold_expansion = K0q / omega
    threshold_expansion += omega * (4 * D(q_minus_one) + I * f / 2)
    if sp.cancel(cocycle - threshold_expansion) != 0:
        fail("threshold static-exact cocycle decomposition failed")
    if sp.cancel(sp.limit(omega * cocycle, omega, 0) - K0q) != 0:
        fail("threshold cocycle residue identity failed")


def verify_commutator() -> None:
    x = sp.symbols("x")
    y = sp.Function("y")(x)
    q = sp.Function("q")(x)
    U = sp.Function("U")(x)

    def L(expr: sp.Expr) -> sp.Expr:
        return sp.diff(expr, x, 2) + U * expr

    def Q(expr: sp.Expr) -> sp.Expr:
        return q * sp.diff(expr, x) - sp.diff(q, x) * expr / 2

    commutator = sp.expand(L(Q(y)) - Q(L(y)))
    on_kernel = commutator.subs(sp.diff(y, x, 2), -U * y)
    on_kernel = on_kernel.subs(
        sp.diff(y, x, 3), -sp.diff(U, x) * y - U * sp.diff(y, x)
    )
    expected = -(
        sp.diff(q, x, 3) + 4 * U * sp.diff(q, x) + 2 * sp.diff(U, x) * q
    ) * y / 2
    if sp.simplify(on_kernel - expected) != 0:
        fail("triangular-gauge commutator identity failed")

    def Q_direct(expr: sp.Expr) -> sp.Expr:
        return 2 * q * sp.diff(expr, x) - sp.diff(q, x) * expr

    direct = sp.expand(L(Q_direct(y)) - Q_direct(L(y)))
    direct = direct.subs(sp.diff(y, x, 2), -U * y)
    direct = direct.subs(
        sp.diff(y, x, 3), -sp.diff(U, x) * y - U * sp.diff(y, x)
    )
    direct_expected = -(
        sp.diff(q, x, 3) + 4 * U * sp.diff(q, x) + 2 * sp.diff(U, x) * q
    ) * y
    if sp.simplify(direct - direct_expected) != 0:
        fail("direct field-redefinition factor-of-two identity failed")


def verify_mass_jost_and_confluence(claims: dict) -> None:
    omega, m, sigma, nu, t = sp.symbols(
        "omega m sigma nu t", nonzero=True
    )
    I = sp.I

    kprime = -1 / (2 * omega)
    rho_prime = sp.simplify(sigma * I * (2 * kprime + 1 / omega))
    if rho_prime != 0:
        fail("Coulomb exponent mass-derivative cancellation failed")
    mass_phase_slope = -sigma * I / (2 * omega)
    bach_scale = I * omega / 2
    if sp.simplify(bach_scale * mass_phase_slope - sigma / 4) != 0:
        fail("moving massive phase and rational-gauge slope mismatch")

    z, a, b, c, d = sp.symbols("z a b c d")
    T0 = sp.Matrix([[z, -1], [0, z]])
    perturbation = sp.Matrix([[a, b], [c, d]])
    determinant = sp.expand((T0 + m * perturbation).det())
    leading = z**2 + m * (a + d) * z + m * c
    if sp.expand(determinant - leading - m**2 * (a * d - b * c)) != 0:
        fail("generic-versus-filtered determinant expansion failed")

    S = sp.Matrix([[1, 1], [0, m]])
    P0 = sp.simplify(S * sp.diag(1, 0) * S.inv())
    Pm = sp.simplify(S * sp.diag(0, 1) * S.inv())
    if P0 != sp.Matrix([[1, -1 / m], [0, 0]]):
        fail("massless confluent projector identity failed")
    if Pm != sp.Matrix([[0, 1 / m], [0, 1]]):
        fail("massive confluent projector identity failed")
    N = sp.Matrix([[0, 1], [0, 0]])
    if sp.simplify(m * P0).applyfunc(lambda x: sp.limit(x, m, 0)) != -N:
        fail("massless projector residue failed")
    if sp.simplify(m * Pm).applyfunc(lambda x: sp.limit(x, m, 0)) != N:
        fail("massive projector residue failed")

    C = sp.simplify(S * sp.diag(1, -1) * S.inv())
    if C != sp.Matrix([[1, -2 / m], [0, -1]]):
        fail("confluent branch involution identity failed")
    if (m * C).applyfunc(lambda x: sp.limit(x, m, 0)) != -2 * N:
        fail("confluent involution residue failed")

    J = sp.simplify(S.inv().T * sp.diag(1, -1) * S.inv())
    if J != sp.Matrix([[1, -1 / m], [-1 / m, 0]]):
        fail("confluent Krein form identity failed")
    H = sp.simplify(J * C)
    if H != sp.Matrix([[1, -1 / m], [-1 / m, 2 / m**2]]):
        fail("singular positive C-metric identity failed")
    if (m * J).applyfunc(lambda x: sp.limit(x, m, 0)) != sp.Matrix(
        [[0, -1], [-1, 0]]
    ):
        fail("renormalized hyperbolic Krein limit failed")
    if (m**2 * H).applyfunc(lambda x: sp.limit(x, m, 0)) != sp.Matrix(
        [[0, 0], [0, 2]]
    ):
        fail("rank-one positive-metric limit failed")

    contour_quotient = (
        sp.exp(I * (omega + nu * m) * t) - sp.exp(I * omega * t)
    ) / m
    if sp.simplify(
        sp.limit(contour_quotient, m, 0)
        - I * nu * t * sp.exp(I * omega * t)
    ) != 0:
        fail("local two-pole contour Jordan limit failed")

    e11, e12, e21, e22, a11, a12, a21, a22 = sp.symbols(
        "e11 e12 e21 e22 a11 a12 a21 a22"
    )
    E = sp.Matrix([[e11, e12], [e21, e22]])
    A = sp.Matrix([[a11, a12], [a21, a22]])
    resolvent = (E + m * A).inv()
    mass_derivative = resolvent.diff(m).subs(m, 0)
    expected_derivative = -E.inv() * A * E.inv()
    if sp.simplify(mass_derivative - expected_derivative) != sp.zeros(2):
        fail("parent inverse mass-derivative identity failed")
    secant = sp.simplify(
        (E.inv() - (E + m * A).inv()) / m
        - E.inv() * A * (E + m * A).inv()
    )
    if secant != sp.zeros(2):
        fail("finite-mass noncommutative secant identity failed")
    second_derivative = resolvent.diff(m, 2).subs(m, 0)
    expected_second = 2 * E.inv() * A * E.inv() * A * E.inv()
    if sp.simplify(second_derivative - expected_second) != sp.zeros(2):
        fail("second critical-jet derivative identity failed")

    w, w0, P, Pdot = sp.symbols("w w0 P Pdot")
    pole_family = (P + m * Pdot) / (w - w0 - nu * m)
    pole_derivative = sp.diff(pole_family, m).subs(m, 0)
    expected_pole_derivative = (
        nu * P / (w - w0) ** 2 + Pdot / (w - w0)
    )
    if sp.simplify(pole_derivative - expected_pole_derivative) != 0:
        fail("massive-pole Laurent derivative identity failed")

    zeta = sp.symbols("zeta")
    matrix_symbols = sp.symbols(
        "p11 p12 p21 p22 h11 h12 h21 h22 "
        "a011 a012 a021 a022 a111 a112 a121 a122"
    )
    (
        p11,
        p12,
        p21,
        p22,
        h11,
        h12,
        h21,
        h22,
        a011,
        a012,
        a021,
        a022,
        a111,
        a112,
        a121,
        a122,
    ) = matrix_symbols
    Pmtrx = sp.Matrix([[p11, p12], [p21, p22]])
    Hmtrx = sp.Matrix([[h11, h12], [h21, h22]])
    A0mtrx = sp.Matrix([[a011, a012], [a021, a022]])
    A1mtrx = sp.Matrix([[a111, a112], [a121, a122]])
    scaled_critical = sp.expand(
        zeta**2
        * (Pmtrx / zeta + Hmtrx)
        * (A0mtrx + zeta * A1mtrx)
        * (Pmtrx / zeta + Hmtrx)
    )
    double_coefficient = scaled_critical.subs(zeta, 0)
    simple_coefficient = scaled_critical.diff(zeta).subs(zeta, 0)
    if sp.simplify(double_coefficient - Pmtrx * A0mtrx * Pmtrx) != sp.zeros(2):
        fail("canonical critical double coefficient failed")
    expected_simple = (
        Pmtrx * A0mtrx * Hmtrx
        + Hmtrx * A0mtrx * Pmtrx
        + Pmtrx * A1mtrx * Pmtrx
    )
    if sp.simplify(simple_coefficient - expected_simple) != sp.zeros(2):
        fail("canonical simple-pole frequency-derivative term failed")

    root = claims["exact_identities"]["root_polarization"]
    if root["principal_coefficient_square"] != "0":
        fail("nilpotent principal coefficient declaration drift")


def verify_period_matrix(claims: dict) -> None:
    y1, y2, dy1, dy2, V = sp.symbols("y1 y2 dy1 dy2 V")
    Y = sp.Matrix([[y1, y2], [dy1, dy2]])
    dA = sp.Matrix([[0, 0], [-V, 0]])
    W = y1 * dy2 - y2 * dy1
    actual = sp.simplify(Y.inv() * dA * Y)
    declared = claims["exact_identities"]["period_matrix"]
    expected = V / W * sp.Matrix(
        [[y1 * y2, y2**2], [-y1**2, -y1 * y2]]
    )
    if declared != [["y1*y2", "y2**2"], ["-y1**2", "-y1*y2"]]:
        fail("declared period matrix drift")
    if sp.simplify(actual - expected) != sp.zeros(2):
        fail("symmetric-square period matrix identity failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()

    paper = resolve(args.paper)
    claim_path = resolve(args.claim_map)
    claims = json.loads(claim_path.read_text())
    text = paper.read_text()

    if claims.get("paper_id") != "PAPER_17_PURE_WEYL_EXTENSION_RESONANCE":
        fail("wrong paper identity")
    if claims.get("lifecycle_state") != "DRAFT_ALLOWED":
        fail("paper lifecycle overpromotion")
    if claims.get("paper_sha256") != digest(paper):
        fail("paper hash drift")

    for name, authority in claims.get("authorities", {}).items():
        path = ROOT / authority["path"]
        if digest(path) != authority["sha256"]:
            fail(f"authority content drift: {name}")

    required = [
        "Mass-direction normal form",
        "Static exactness and the threshold lattice",
        "\\operatorname*{Res}_{\\omega=0}\\mathcal I_{\\rm Bach}",
        "Bulk class versus spectral frame",
        "\\mathcal I_{\\rm Bach}",
        "\\mathcal K_{U_2}q+\\frac{i\\omega}{2}f",
        "Explicit triangular gauge",
        "Symmetric-square period matrix",
        "Non-split physical-axis extension",
        "Local commutant",
        "Certified defective Schwarzschild resonance",
        "Resonant evaluation theorem",
        "\\mathfrak M_n([K])",
        "-\\frac{\\kappa_n}{\\alpha_n}",
        "Nonzero carrier in the generalized root",
        "Finite-interval outgoing Green pole",
        "Exterior cut-off Green pole",
        "exact transparent boundary conditions",
        "\\chi_{\\rm o}R_{\\rm ext}(\\omega)\\chi_{\\rm s}",
        "C_c^\\infty((r_H,r_I);\\C^6)",
        "Conditional global Fredholm promotion",
        "Exact local critical-mass-jet identification",
        "[\\mathcal I_{\\rm mass}]=[f]",
        "m=\\frac{i\\omega}{2}\\tau",
        "Forced moving-phase gauge",
        "Q_q=2qD-D(q)",
        "Coulomb cancellation and differentiated Jost classes",
        "\\rho_\\sigma'(0)=0",
        "Critical-mass Evans derivative and QNM velocity",
        "\\frac{2i}{\\omega_n}\\kappa_n\\ne0",
        "Reflected EP2 pair",
        "\\omega_n^\\sharp",
        "Boundary transgression as an audit",
        "Universal critical resonance and the covariant parent",
        "Universal critical-resonance criterion",
        "C_{-2}=-\\nu_nP_n",
        "Canonical simple pole and tangent state",
        "P_nA_n'P_n",
        "[-H_ng_n]",
        "Augmented QNM Hellmann--Feynman formula",
        "-\\frac{\\partial_ma}{\\partial_\\omega a}",
        "[\\dot u_n]\\in D/\\C u_n",
        "exact finite-mass secant identity",
        "Higher critical jets",
        "Critical mass derivative of the metric Green operator",
        "G_{-2}=-\\frac{\\nu_n}{4\\alpha_{\\rm W}}P_n",
        "Isolated parent-resonance contribution",
        "Einstein-shaped",
        "Generic versus filtration-preserving splitting",
        "Filtered critical-mass unfolding normal form",
        "Root-space polarization and nilpotent pole",
        "R_{-2}^2=0",
        "Confluent projectors and local contour",
        "Critical singularity of positive branch metrics",
        "Renormalized Krein limit",
        "Canonical pseudospectral scale",
        "does not establish a causal spacetime resolvent",
    ]
    for phrase in required:
        if phrase not in text:
            fail(f"required scoped statement missing: {phrase}")

    forbidden = [
        "the intrinsic radial parameter \\(\\tau\\) is the physical squared mass",
        "the causal spacetime resolvent has a second-order pole",
        "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term",
        "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)",
        "the full six-state commutant is the dual-number algebra",
        "the complete complex reducibility locus is known",
        "time-domain stability is established",
        "quantum unitarity is established",
        "the endpoint transgression vanishes",
        "the off-resonance normalization function \\(h(\\omega)\\) vanishes",
        "the physical mass deformation is a miniversal unfolding",
        "the local two-pole contour is the full retarded solution",
        "the projected metric Green coefficient is nilpotent",
    ]
    for phrase in forbidden:
        if phrase in text:
            fail(f"forbidden promotion present: {phrase}")

    for key, value in claims["fail_closed_scope"].items():
        if value is not False:
            fail(f"fail-closed promotion: {key}")

    authorities = claims["authorities"]
    filtration = json.loads((ROOT / authorities["factor_filtration"]["path"]).read_text())
    require_flag(
        filtration,
        "complete_RW_RW_Lx_triangular_filtration_certified",
        True,
        "filtration",
    )
    require_flag(
        filtration,
        "complete_direct_RW_square_plus_Lx_decomposition_certified",
        False,
        "filtration",
    )

    cocycle = json.loads((ROOT / authorities["projective_cocycle"]["path"]).read_text())
    for key in [
        "projective_gauge_law_exact",
        "generic_rational_ansatz_exhaustive",
        "generic_rational_cocycle_nontrivial",
        "declared_reduced_representative_exact",
    ]:
        require_flag(cocycle, key, True, "cocycle")
    require_flag(cocycle, "QNM_double_pole_established", False, "cocycle")

    simple = json.loads(
        (ROOT / authorities["simplicity_endomorphisms"]["path"]).read_text()
    )
    for key in [
        "axial_ell2_nonsplit_all_positive_real",
        "spin2_endomorphism_ring_scalar_positive_real",
        "spin2_simple_all_ell_positive_real",
    ]:
        require_flag(simple, key, True, "simplicity")
    require_flag(simple, "all_ell_bach_nonsplitting_established", False, "simplicity")

    commutant = json.loads((ROOT / authorities["local_commutant"]["path"]).read_text())
    require_flag(commutant, "local_commutant_dual_numbers_exact", True, "commutant")
    require_flag(commutant, "full_six_state_commutant_dual_numbers", False, "commutant")

    winding = json.loads((ROOT / authorities["qnm_winding"]["path"]).read_text())
    for key in [
        "full_closed_contour_nonzero_certified",
        "winding_number_certified",
        "unique_simple_spin_two_QNM_in_disk_certified",
    ]:
        require_flag(winding, key, True, "winding")

    selector = json.loads((ROOT / authorities["qnm_selector"]["path"]).read_text())
    require_flag(selector, "intrinsic_tangent_selector_nonzero", True, "selector")
    require_flag(selector, "repeated_spin_two_smith_valuations_0_2", True, "selector")

    spin1 = json.loads((ROOT / authorities["spin_one_unit"]["path"]).read_text())
    require_flag(spin1, "spin_one_jost_factor_unit_on_local_disk", True, "spin-one")
    require_flag(spin1, "full_connection_smith_valuations_0_0_2", True, "spin-one")

    fredholm = json.loads(
        (ROOT / authorities["fredholm_promotion"]["path"]).read_text()
    )
    for key in [
        "analytic_finite_interval_pencil_certified",
        "connection_smith_transferred_to_operator",
        "radial_green_operator_second_order_pole_certified",
        "principal_laurent_coefficient_rank_one",
        "physical_metric_reconstruction_nonzero",
    ]:
        require_flag(fredholm, key, True, "Fredholm promotion")
    for key in [
        "exterior_spacetime_causal_resolvent_certified",
        "retarded_inverse_transform_certified",
        "t_exp_iomega_t_term_certified",
        "time_domain_stability_certified",
    ]:
        require_flag(fredholm, key, False, "Fredholm promotion")

    mass = json.loads(
        (ROOT / authorities["critical_mass_parent"]["path"]).read_text()
    )
    for key in [
        "parent_mass_variation_exact",
        "mass_derivative_modulo_einstein_kernel_exact",
        "tt_difference_quotient_exact",
    ]:
        require_flag(mass, key, True, "critical mass parent")
    for key in [
        "physical_b_equals_minus_mass_derivative_of_jost",
        "physical_mass_jet_equals_intrinsic_radial_tau",
        "physical_massive_qnm_slope_certified",
    ]:
        require_flag(mass, key, False, "critical mass parent")

    continuation = json.loads(
        (ROOT / authorities["analytic_continuation"]["path"]).read_text()
    )
    for key in [
        "axial_mode_series_omega_poles_exact_certified",
        "domain_declared_excludes_poles",
        "no_branch_points_axial_certified",
    ]:
        require_flag(continuation, key, True, "analytic continuation")
    require_flag(continuation, "stability_qnm_scattering_claimed", False, "continuation")

    reconstruction = json.loads(
        (ROOT / authorities["metric_reconstruction"]["path"]).read_text()
    )
    require_flag(
        reconstruction,
        "complete_three_row_reconstruction_certified",
        True,
        "reconstruction",
    )

    verify_cocycle(claims)
    verify_commutator()
    verify_period_matrix(claims)
    verify_mass_jost_and_confluence(claims)

    root = claims["exact_identities"]["generalized_root"]
    if root["carrier_quotient"] != "-a1/b0":
        fail("generalized root carrier quotient identity failed")
    triangular = claims["exact_identities"]["triangular_gauge"]
    if triangular != {
        "operator": "q*D - D(q)/2",
        "commutator_on_kernel": "-K_U(q)/2",
        "direct_field_gauge": "Q_q=2*q*D-D(q)",
        "direct_commutator_on_kernel": "-K_U(q)",
    }:
        fail("triangular gauge factor normalization drift")
    resonant = claims["exact_identities"]["resonant_evaluation"]
    if resonant != {
        "selector": "b0/a1",
        "normalized_overlap": "beta/alpha",
        "resonance_velocity": "-kappa",
        "physical_mass_velocity": "2*I*kappa/omega",
        "carrier_quotient": "-1/kappa",
        "fredholm_principal_coefficient": "-kappa/alpha",
    }:
        fail("resonant evaluation chain declaration drift")
    mass_jet = claims["exact_identities"]["critical_mass_jet"]
    if mass_jet != {
        "mass_operator": "L - m*f",
        "mass_cocycle_class": "[f]",
        "bach_to_mass_class": "I*omega/2",
        "parameter_relation": "m = I*omega*tau/2",
        "coulomb_exponent": "sigma*I*(2*k+m/k)",
        "coulomb_exponent_mass_derivative_at_zero": "0",
        "evans_derivative_at_qnm": "b_B=I*omega*partial_m(a)/2",
        "qnm_velocity": "2*I*kappa/omega",
    }:
        fail("critical mass-jet declaration drift")
    transgression = claims["exact_identities"]["boundary_transgression"]
    if transgression != {
        "base_gauge": "Q(q)=q*D-D(q)/2",
        "field_redefinition_gauge": "Q_q=2*Q(q)",
        "bulk_identity": "K_Bach-I*omega*K_mass/2=-[L,Q_q]",
        "finite_cut_term": "-[W(tilde_u,Q_q*u)]_xminus^xplus",
        "qnm_endpoint_effect": "h(omega)*a(omega)",
    }:
        fail("boundary-transgression normalization drift")
    unfolding = claims["exact_identities"]["filtered_unfolding"]
    if unfolding != {
        "normal_form": [["z", "-1"], ["0", "z-mu"]],
        "generic_determinant_leading": "z**2+m*(a+d)*z+m*c",
        "generic_split": "sqrt(m) if c != 0",
        "filtered_split": "mu=dz_domega*nu*m+O(m**2)",
        "projector_scale": "1/abs(m)",
        "positive_metric_condition_scale": "1/abs(m)**2",
        "pseudospectral_radius": "sqrt(epsilon)",
    }:
        fail("filtered unfolding declaration drift")
    confluent = claims["exact_identities"]["confluent_limits"]
    if confluent != {
        "m_times_C": "-2*N",
        "tau_times_C": "4*I*N/omega",
        "m_times_J": [["0", "-1"], ["-1", "0"]],
        "m2_times_H": [["0", "0"], ["0", "2"]],
        "local_contour": "exp(I*omega*t)*(I+I*nu*t*N)",
    }:
        fail("confluent limit declaration drift")
    parent = claims["exact_identities"]["parent_mass_derivative"]
    if parent != {
        "metric_green": "-partial_m(E_m_inverse)/(4*alpha_W)",
        "finite_mass_secant": "(E_inverse-E_m_inverse)/m",
        "double_coefficient": "-nu*P/(4*alpha_W)",
        "simple_coefficient": "-Pdot/(4*alpha_W)",
        "overlap_velocity": "nu=-beta/alpha",
        "selector_coefficient": "-I*kappa*P/(2*alpha_W*omega)",
        "local_contour": (
            "-exp(I*omega*t)*(Pdot+I*t*nu*P)/(4*alpha_W)"
        ),
    }:
        fail("parent mass-derivative declaration drift")
    universal = claims["exact_identities"]["universal_critical_resonance"]
    if universal != {
        "critical_response": "R*A*R",
        "double_coefficient": "beta/alpha**2*u tensor tilde_u",
        "double_pole_iff": "beta != 0",
        "mass_velocity": "-beta/alpha",
        "canonical_tangent_class": "[u_dot] in D/(C*u)",
        "projected_coefficient_intrinsically_nilpotent": False,
        "full_extension_coefficient_nilpotent": True,
    }:
        fail("universal critical-resonance declaration drift")
    threshold = claims["exact_identities"]["threshold_static_exactness"]
    if threshold != {
        "q_minus_one": "-I*(15*r + 13 + 12/r + 9/r**2)/120",
        "symmetric_square_decomposition": "K_U=K_U0+4*omega**2*D",
        "cocycle_residue": "K_U0(q_minus_one)",
        "renormalized_class_limit": "I*[f]/2",
        "continuous_cokernel_identification_required": True,
    }:
        fail("threshold static-exactness declaration drift")
    simple_pole = claims["exact_identities"]["canonical_simple_pole"]
    if simple_pole != {
        "double_coefficient": "P*A0*P=-nu*P",
        "simple_coefficient": "P*A0*H+H*A0*P+P*A1*P=-Pdot",
        "frequency_derivative_term": "P*A1*P",
        "tangent_class": "-H*(A0+nu*L1)*u mod C*u",
        "left_tangent_class": "-tilde_u*(A0+nu*L1)*H mod C*tilde_u",
    }:
        fail("canonical simple-pole declaration drift")
    hellmann = claims["exact_identities"]["augmented_hellmann_feynman"]
    if hellmann != {
        "evans_parameter_derivative": "integral(yminus*Qp*yplus)+B_p",
        "velocity": "-a_m/a_omega=-beta/alpha",
        "mass_potential_derivative": "-f",
        "frequency_potential_derivative": "2*omega",
        "pairing": "bilinear_augmented_qnm",
    }:
        fail("augmented Hellmann-Feynman declaration drift")
    reflection = claims["exact_identities"]["reflection_pair"]
    if reflection != {
        "frequency": "-conjugate(omega)",
        "velocity": "-conjugate(nu)",
        "selector": "-conjugate(kappa)",
        "simple_residue": "-conjugate(P)",
        "double_coefficient": "conjugate(C_minus_2)",
        "simple_coefficient": "-conjugate(C_minus_1)",
    }:
        fail("reflection-pair declaration drift")
    higher = claims["exact_identities"]["higher_critical_jets"]
    if higher != {
        "operator": "R*(A*R)**p",
        "mass_derivative": "(-1)**p*partial_m**p(R_m)/factorial(p)",
        "pole_order_if_beta_nonzero": "p+1",
        "leading_coefficient": "beta**p/alpha**(p+1)*u tensor tilde_u",
    }:
        fail("higher critical-jet declaration drift")
    green = claims["exact_identities"]["green_principal_coefficient"]
    if green != {
        "connection": "-b0/a1**2",
        "outgoing_green": "b0/a1**2",
        "rank": 1,
    }:
        fail("Green principal coefficient declaration drift")

    print("PASS paper/17-pure-weyl-schwarzschild-extension-structure.tex")
    print(
        "PASS exact cocycle, endpoint-compatible mass jet, filtered "
        "unfolding, confluent metrics, and nilpotent root-space identities"
    )
    print("PASS authority provenance and fail-closed claim boundary")


if __name__ == "__main__":
    main()
