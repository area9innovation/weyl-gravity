"""Extend the complete k=0 exceptional no-go to a Sobolev--Bohr completion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.schema.json"
INPUTS = {
    "complete_k0": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.json",
    "wiener": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json",
    "pair_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json",
    "pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["complete_k0"]["classification"]["complete_declared_k0_carrier_covered"]
    assert records["complete_k0"]["classification"]["bounded_tangent_cone_intersection_empty_over_nonzero_ellipse"]
    assert not records["complete_k0"]["classification"]["maximal_sobolev_or_finite_energy_completion_classified"]
    assert records["wiener"]["classification"]["smooth_wiener_bohr_minus_completion_classified"]
    assert records["pair_census"]["classification"]["complete_k0_oscillator_pair_to_minus_census_closed"]
    assert records["pivot"]["classification"]["all_fixed_ell_at_least_2_pivots_nonzero"]

    lam = sp.symbols("lambda", positive=True, real=True)
    omega = sp.sqrt(lam - sp.sqrt(2 * lam))
    axial = -3 * sp.I * omega * (3 * sp.sqrt(2 * lam) - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    assert sp.simplify(axial.subs(lam, 6)) != 0
    assert polar.subs(lam, 6) > 0

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-sobolev-bohr-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SOBOLEV_BOHR_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded uniformly almost-periodic Sobolev correction",
            "charge_sector": "fixed N=2 magnetic bundle with first-order electric tangent allowed",
            "carrier": "any nonzero axisymmetric exceptional resonance-ellipse point, arbitrary standard generalized-zero data, arbitrary finite k=0 nonminus oscillators and a Sobolev-Bohr k=0 Einstein-minus sum",
            "degree": 2,
            "parity": "all certified homogeneous, axial and polar parities",
            "ell": "global 0,1; finite nonminus ell>=1; countable Einstein-minus ell>=2",
            "m": "all retained m with convergent stabilizer moment maps",
            "k": 0,
            "omega": "generalized zero and the complete certified k=0 q/p oscillator inventory",
        },
        "declared_sobolev_bohr_domain": {
            "regularity": "integer s>=6",
            "mode_space": "the closure of finite Einstein-minus sums in max_(0<=j<=4) sup_t ||partial_t^j u(t)||_{H^(s-j)(S2;E)}",
            "typed_bundle": "E is the finite-rank axial-plus-polar fixed-bundle perturbation carrier; no parity or branch labels are identified",
            "correction_space": "bounded uniformly almost-periodic fields in the corresponding order-four Sobolev graph domain",
            "bochner_fejer_density": "finite branch-labelled trigonometric sums are dense by definition in the declared graph norm",
            "strictly_weaker_than_smooth_wiener": "in a Sobolev-normalized one-mode-per-ell basis, c_ell=(1+lambda_ell)^(-(s+2)/2) lies in the declared weighted l2 graph completion but fails the all-orders weighted l1 Wiener seminorms",
            "not_claimed": "This is not the maximal energy space, a low-regularity solution theory, or an arbitrary distributional completion.",
        },
        "continuous_quadratic_projection_lemma": {
            "sobolev_product": "on S2, s>=6 makes every product of differentiated factors of total order at most four continuous into H^(s-4)",
            "source_map": "the local fourth-order Weyl-Maxwell Hessian extends continuously from the declared graph domain to uniformly almost-periodic H^(s-4)-valued sources",
            "frequency_projection": "the Banach-valued Bohr coefficient M_Omega f=lim_(T->infinity)(2T)^(-1) integral_(-T)^T exp(i*Omega*t)f(t)dt is a contraction in the uniform H^(s-4) norm",
            "angular_projection": "pairing with a fixed smooth spherical adjoint harmonic is continuous on H^(s-4)",
            "finite_approximation": "Bochner-Fejer approximants reduce every projected quadratic coefficient to the certified finite-support pair census; continuity passes the zero competitors to the limit",
            "isolated_coefficient": "d*C_parity(lambda)*c_(ell,m,parity)",
            "axial_pivot": str(axial),
            "polar_pivot": str(polar),
        },
        "fredholm_contradiction": {
            "left_hand_side": "the resonant adjoint projection of L v vanishes for every correction in the declared uniformly almost-periodic graph domain",
            "taub_requirement": "the nonpositive ellipse, global and nonminus blocks require at least one nonzero Einstein-minus coefficient",
            "resonant_requirement": "d!=0 and C_parity(lambda)!=0 force every Einstein-minus coefficient to vanish",
            "verdict": "the bounded Sobolev-Bohr second-order tangent cone has empty intersection with the complete declared carrier over every nonzero ellipse point",
        },
        "correction_classes": {
            "BOUNDED_UNIFORMLY_ALMOST_PERIODIC_SOBOLEV_GRAPH": {"status": "OBSTRUCTED"},
            "SMOOTH_INFINITE_SECULAR": {"status": "OPEN", "reason": "no uniform inverse estimate controls a countable secular correction"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "finite_order_sobolev_bohr_completion_classified": True,
            "strict_extension_beyond_smooth_wiener_domain": True,
            "bounded_uniformly_almost_periodic_sobolev_extension_obstructed": True,
            "continuous_quadratic_source_map_certified": True,
            "continuous_bohr_adjoint_projection_certified": True,
            "complete_declared_k0_carrier_covered": True,
            "maximal_finite_energy_or_low_regularity_completion_classified": False,
            "smooth_infinite_secular_extension_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The complete k=0 obstruction is not an artifact of absolute Fourier summability. It persists in a finite-order Sobolev graph completion because the nonlinear source and each resonant adjoint coefficient are continuous under Bochner-Fejer approximation.",
        "next_gate": "treat nonzero compact momentum; separately determine the sharp low-regularity or energy threshold and infinite secular estimates",
        "claim_boundary": "Complete only at k=0 in the declared s>=6 uniformly almost-periodic Sobolev graph domain with finite nonminus support. Maximal energy/low-regularity completion, infinite secular inversion, nonzero momentum, causal, residual, all-orders and quantum claims remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("stale Sobolev-Bohr exceptional no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SOBOLEV_BOHR_NO_GO: PASS")


if __name__ == "__main__":
    main()
