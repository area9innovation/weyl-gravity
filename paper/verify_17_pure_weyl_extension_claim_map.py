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


def verify_provenance(claims: dict, paper: Path) -> None:
    if claims.get("paper_sha256") != digest(paper):
        fail("paper hash drift")
    if claims.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        fail("dependency-tag drift")
    for name, authority in claims.get("authorities", {}).items():
        path = resolve(Path(authority["path"]))
        if not path.exists():
            fail(f"missing authority: {name}")
        if digest(path) != authority["sha256"]:
            fail(f"authority hash drift: {name}")


def verify_cocycle(claims: dict) -> None:
    r, omega = sp.symbols("r omega", nonzero=True)
    f = (r - 2) / r
    U = omega**2 - f * (6 / r**2 - 6 / r**3)

    def D(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(f * sp.diff(expr, r))

    identity = claims["exact_identities"]["bach_cocycle_normal_form"]
    q = sp.sympify(
        identity["q"], locals={"I": sp.I, "r": r, "omega": omega}
    )
    representative = sp.sympify(
        identity["representative"],
        locals={"I": sp.I, "r": r, "omega": omega},
    )
    Kq = D(D(D(q))) + 4 * U * D(q) + 2 * D(U) * q
    cocycle = (
        sp.I
        * (r - 2)
        * (2 * r * omega**2 + 3 * omega**2 + 12)
        / (5 * r**4 * omega)
    )
    if sp.cancel(cocycle - Kq - representative) != 0:
        fail("cocycle normal-form identity failed")
    slope = sp.limit(q / r, r, sp.oo)
    if sp.simplify(slope + sp.I / (8 * omega)) != 0:
        fail("mass-gauge infinity slope failed")


def verify_gauge_and_mass(claims: dict) -> None:
    x = sp.symbols("x")
    y = sp.Function("y")(x)
    q = sp.Function("q")(x)
    U = sp.Function("U")(x)

    def L(expr: sp.Expr) -> sp.Expr:
        return sp.diff(expr, x, 2) + U * expr

    def on_kernel(expr: sp.Expr) -> sp.Expr:
        expr = sp.expand(expr).subs(sp.diff(y, x, 2), -U * y)
        return expr.subs(
            sp.diff(y, x, 3),
            -sp.diff(U, x) * y - U * sp.diff(y, x),
        )

    Q = q * sp.diff(y, x) - sp.diff(q, x) * y / 2
    expected = -(
        sp.diff(q, x, 3)
        + 4 * U * sp.diff(q, x)
        + 2 * sp.diff(U, x) * q
    ) * y / 2
    if sp.simplify(on_kernel(L(Q) - (
        q * sp.diff(L(y), x) - sp.diff(q, x) * L(y) / 2
    )) - expected) != 0:
        fail("triangular-gauge commutator failed")

    mass = claims["exact_identities"]["complete_massive_first_jet"]
    expected_mass = {
        "mass_parameter": "m=mu**2",
        "physical_system": "coupled_QZ",
        "massless_factorization": "RW_spin2 direct_sum Maxwell_spin1",
        "factor_transform_determinant": "omega**(-4)",
        "naive_graded_mass_operator": "L-m*f",
        "naive_graded_mass_class": "[f]",
        "physical_tensor_mass_class": "(1/3)*[f]",
        "bach_to_physical_mass_class": "3*I*omega/2",
        "fixed_frequency_tangent_relation": "m=3*I*omega*tau/2",
        "spectral_global_reparameterization": False,
        "complete_coupled_massive_axial_first_jet": True,
        "reverse_tensor_to_vector_multiplier": "-16/(27*omega**2)",
        "physical_mass_primitive": "r/(6*omega**2)",
        "coulomb_exponent": "sigma*I*(2*k+m/k)",
        "coulomb_exponent_mass_derivative_at_zero": "0",
        "reduced_physical_r_slope": "-sigma*I/(6*omega)",
        "scaled_bach_r_slope": "sigma/4",
        "endpoint_comparison_status": "EXACT_LEADING_ASYMPTOTIC",
        "all_order_differentiated_jost_certified": False,
        "opposite_jost_admixture_excluded": False,
        "physical_mass_velocity_certified": False,
    }
    if mass != expected_mass:
        fail("complete massive first-jet declaration drift")
    omega, sigma = sp.symbols("omega sigma", nonzero=True)
    kprime = -1 / (2 * omega)
    rho_prime = sigma * sp.I * (2 * kprime + 1 / omega)
    if sp.simplify(rho_prime) != 0:
        fail("Coulomb exponent derivative did not cancel")

    r = sp.symbols("r", nonzero=True)
    f = (r - 2) / r
    u2 = omega**2 - f * (6 / r**2 - 6 / r**3)

    def Dr(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(f * sp.diff(expr, r))

    def KU(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(
            Dr(Dr(Dr(expr))) + 4 * u2 * Dr(expr) + 2 * Dr(u2) * expr
        )

    physical_density = (
        (r - 2) * (3 * r**4 * omega**2 - 20 * r + 30)
        / (3 * r**5 * omega**2)
    )
    if sp.cancel(
        physical_density - KU(r / (6 * omega**2)) - f / 3
    ) != 0:
        fail("complete physical tensor mass normal form failed")
    reduced_slope = -sigma * sp.I / (2 * omega) + sigma * sp.I / (
        3 * omega
    )
    if sp.simplify(
        (3 * sp.I * omega / 2) * reduced_slope - sigma / 4
    ) != 0:
        fail("factor-three endpoint slope failed")


def verify_resonance_and_green(claims: dict) -> None:
    identities = claims["exact_identities"]
    smith = identities["smith_and_root"]
    if smith != {
        "defective_smith_type": [0, 0, 2],
        "semisimple_smith_type": [0, 1, 1],
        "selector": "kappa=b/a_prime=beta/alpha",
        "carrier_quotient": "-1/kappa",
        "intrinsic_tau_velocity": "-kappa",
        "physical_mass_velocity_relation": (
            "CONDITIONAL_nu=2*I*kappa/(3*omega)"
        ),
        "kappa_re_enclosure": ["-0.047", "0.022"],
        "kappa_im_enclosure": ["0.064", "0.138"],
    }:
        fail("Smith/root declaration drift")
    if float(smith["kappa_im_enclosure"][0]) <= 0:
        fail("selector enclosure no longer excludes zero")

    alpha, beta, u, v = sp.symbols("alpha beta u v", nonzero=True)
    P = sp.Matrix([[u * v / alpha]])
    A = sp.Matrix([[beta / (u * v)]])
    if sp.simplify((P * A * P)[0] - beta * u * v / alpha**2) != 0:
        fail("rank-one Green coefficient algebra failed")

    green = identities["green_principal_coefficient"]
    if green != {
        "rank": 1,
        "pole_order": 2,
        "coefficient": "-beta*u tensor tilde_u/alpha**2",
        "cutoff_exterior": True,
        "global_causal_resolvent": False,
    }:
        fail("Green-principal declaration drift")

    parent = identities["parent_mass_derivative"]
    if parent != {
        "identity": "G_W=-(partial_m inverse(E+m*A)|0)/(4*alpha_W)",
        "double_coefficient": "-nu*P/(4*alpha_W)",
        "isolated_contour_only": True,
        "certified_scalar_selector_identified_with_parent_nu": False,
    }:
        fail("parent mass-derivative declaration drift")

    trace = identities["outgoing_trace_bridge"]
    if trace != {
        "principal_coefficient": (
            "-beta*O_scri(u) tensor (tilde_u*chi_s)/alpha**2"
        ),
        "analytic_on_local_jost_family": True,
        "global_causal_trace": False,
    }:
        fail("outgoing-trace declaration drift")


def verify_reconstruction_and_source(claims: dict) -> None:
    identities = claims["exact_identities"]
    reconstruction = identities["null_infinity_reconstruction"]
    if reconstruction["einstein_bondi_shear_nonzero"] is not True:
        fail("Einstein Bondi-shear nonannihilation drift")
    if reconstruction["carrier_standard_strain_falloff"] is not False:
        fail("generalized falloff promotion")

    r, omega = sp.symbols("r omega", nonzero=True)
    H0E, H1E = -r, 2 * r
    H0R, H1R = 3 * r**2 / 4 - 3 * r / 2, -3 * r**2 / 2
    if sp.limit(H0R / (r * H0E), r, sp.oo) != -sp.Rational(3, 4):
        fail("carrier/Einstein H0 leading ratio failed")
    if sp.limit(H1R / (r * H1E), r, sp.oo) != -sp.Rational(3, 4):
        fail("carrier/Einstein H1 leading ratio failed")
    if sp.simplify(2 * sp.I * (-1) / omega + 2 * sp.I / omega) != 0:
        fail("Einstein Bondi-shear algebra failed")

    source = identities["conserved_traceless_source"]
    expected = {
        "P_t": "0",
        "P_r": "mu*F/(2*I*omega*r*f)",
        "P_tensor": "d_r(r*F)/(2*I*omega)",
        "master_source": "f*S_odd=F",
        "conserved": True,
        "traceless": True,
        "adjoint_choice": "F=eta*conjugate(tilde_u)",
        "adjoint_overlap": "integral(eta*abs(tilde_u)**2,drstar)>0",
        "source_domain": "COMPLEXIFIED_FREQUENCY_DOMAIN",
        "real_causal_temporally_compact": False,
        "specified_trajectory": False,
    }
    if source != expected:
        fail("conserved-source declaration drift")

    F = sp.Function("F")(r)
    mu = sp.symbols("mu", nonzero=True)
    f = sp.Function("f")(r)
    Pr_up = mu * F / (2 * sp.I * omega * r)
    Ptensor = sp.diff(r * F, r) / (2 * sp.I * omega)
    conservation = sp.diff(Pr_up, r) + 2 * Pr_up / r - mu * Ptensor / r**2
    if sp.simplify(conservation) != 0:
        fail("conserved-source radial identity failed")


def verify_authority_flags(claims: dict) -> None:
    def certificate(name: str) -> dict:
        path = resolve(Path(claims["authorities"][name]["path"]))
        return json.loads(path.read_text())

    checks = [
        ("factor_filtration", "complete_RW_RW_Lx_triangular_filtration_certified", True),
        ("qnm_winding", "unique_simple_spin_two_QNM_in_disk_certified", True),
        ("qnm_selector", "intrinsic_tangent_selector_nonzero", True),
        ("spin_one_unit", "full_connection_smith_valuations_0_0_2", True),
        ("fredholm_promotion", "radial_green_operator_second_order_pole_certified", True),
        ("null_infinity_reconstruction", "einstein_bondi_shear_nonzero", True),
        ("null_infinity_reconstruction", "generalized_constant_component_standard_falloff", False),
        ("conserved_source_overlap", "stress_energy_conserved", True),
        ("conserved_source_overlap", "stress_energy_traceless", True),
        ("conserved_source_overlap", "constructed_source_adjoint_overlap_nonzero", True),
        (
            "complete_massive_axial_jet",
            "complete_first_mass_squared_jet_transformed",
            True,
        ),
        (
            "complete_massive_axial_jet",
            "factor_three_Bach_mass_crosswalk_exact",
            True,
        ),
        (
            "complete_massive_axial_jet",
            "all_order_differentiated_Jost_map_certified",
            False,
        ),
        (
            "complete_massive_axial_jet",
            "physical_QNM_velocity_certified",
            False,
        ),
        ("critical_mass_parent", "physical_mass_jet_equals_intrinsic_radial_tau", False),
        ("critical_mass_parent", "physical_b_equals_minus_mass_derivative_of_jost", False),
        ("critical_mass_parent", "physical_massive_qnm_slope_certified", False),
    ]
    for authority, flag, expected in checks:
        actual = certificate(authority).get("claim_flags", {}).get(flag)
        if actual is not expected:
            fail(f"authority flag drift: {authority}.{flag}={actual!r}")


def verify_manuscript(claims: dict, paper: Path) -> None:
    text = paper.read_text()
    required = [
        "The paper has five results.",
        "GPT-5.6.sol",
        "Asger Alstrup Palm",
        "\\texttt{LOCAL-ALGEBRAIC}",
        "\\texttt{REDUCED-MODE}",
        "Global retarded ringdown expansion",
        "Not established",
        "The polynomially weighted term",
        "isolated local resonance contour",
        "specified material trajectory",
        "The complete coupled-system map and its leading differentiated endpoint",
        "all-order parameter dependence",
        "complexified frequency-domain conserved and traceless",
    ]
    for phrase in required:
        if phrase not in text:
            fail(f"required manuscript boundary missing: {phrase}")

    removed_programme_sections = [
        "\\section{Spectral velocity generating function}",
        "\\section{Second-order spectral flow}",
        "\\section{Finite-time coherent forcing}",
        "\\section{Two-parameter unfolding}",
        "\\section{Canonical Krein--Jordan geometry}",
        "\\section{Detector-level normal form}",
    ]
    for phrase in removed_programme_sections:
        if phrase in text:
            fail(f"publication consolidation drift: {phrase}")

    forbidden_promotions = [
        "the causal spacetime resolvent has a second-order pole",
        "a rigorous \\(t e^{i\\omega_nt}\\) ringdown term",
        "the local resonance contour is the full retarded solution",
        "the generalized constant component has standard asymptotic falloff",
        "a specified astrophysical source excites the pole",
        "detector sensitivity is established",
    ]
    lowered = text.lower()
    for phrase in forbidden_promotions:
        if phrase.lower() in lowered:
            fail(f"forbidden promotion: {phrase}")

    flags = claims["claim_flags"]
    required_false = [
        "all_order_differentiated_massive_jost_crosswalk",
        "endpoint_compatible_physical_mass_jet_exact",
        "physical_massive_qnm_slope_certified",
        "real_causal_source_overlap_nonzero",
        "global_causal_resolvent",
        "complete_retarded_qnm_expansion",
        "generalized_constant_component_standard_falloff",
        "specified_astrophysical_source_overlap",
        "detector_sensitivity",
        "quantum_positivity_statement",
    ]
    for key in required_false:
        if flags.get(key) is not False:
            fail(f"fail-closed claim flag drift: {key}")

    required_true = [
        "graded_mass_squared_direction_exact",
        "complete_coupled_massive_axial_first_jet_crosswalk_exact",
        "outgoing_trace_bridge_exact",
        "complexified_conserved_traceless_source_overlap_nonzero",
    ]
    for key in required_true:
        if flags.get(key) is not True:
            fail(f"required scoped claim flag drift: {key}")

    tcb = claims.get("trusted_computing_base", {})
    if tcb.get("immutable_doi_archive_available") is not False:
        fail("archive submission gate drift")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()
    paper = resolve(args.paper)
    claim_map = resolve(args.claim_map)
    claims = json.loads(claim_map.read_text())
    verify_provenance(claims, paper)
    verify_cocycle(claims)
    verify_gauge_and_mass(claims)
    verify_resonance_and_green(claims)
    verify_reconstruction_and_source(claims)
    verify_authority_flags(claims)
    verify_manuscript(claims, paper)
    print("PASS: Paper 17 consolidated claim map verified")


if __name__ == "__main__":
    main()
