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
        "Reduced outgoing Green pole",
        "C_c^\\infty((r_H,r_I);\\C^6)",
        "Conditional global Fredholm promotion",
        "Physical Einstein--Weyl mass identification",
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

    root = claims["exact_identities"]["generalized_root"]
    if root["carrier_quotient"] != "-a1/b0":
        fail("generalized root carrier quotient identity failed")
    resonant = claims["exact_identities"]["resonant_evaluation"]
    if resonant != {
        "selector": "b0/a1",
        "normalized_overlap": "beta/alpha",
        "resonance_velocity": "-kappa",
        "carrier_quotient": "-1/kappa",
        "fredholm_principal_coefficient": "-kappa/alpha",
    }:
        fail("resonant evaluation chain declaration drift")
    green = claims["exact_identities"]["green_principal_coefficient"]
    if green != {
        "connection": "-b0/a1**2",
        "outgoing_green": "b0/a1**2",
        "rank": 1,
    }:
        fail("Green principal coefficient declaration drift")

    print("PASS paper/17-pure-weyl-schwarzschild-extension-structure.tex")
    print("PASS exact cocycle, triangular gauge, period matrix, and root-chain identities")
    print("PASS authority provenance and fail-closed claim boundary")


if __name__ == "__main__":
    main()
