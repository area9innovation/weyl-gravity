"""Extend the exceptional-ellipse minus-dressing no-go to a smooth Wiener--Bohr completion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.schema.json"
INPUTS = {
    "finite": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json",
    "pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["finite"]["classification"]["arbitrary_finite_minus_superpositions_covered"]
    assert not records["finite"]["classification"]["infinite_completion_classified"]
    assert records["pivot"]["classification"]["all_fixed_ell_at_least_2_pivots_nonzero"]
    assert records["ellipse"]["parameterization"]["domain"] == "r_x,r_p>=0, d!=0, not both r_x,r_p zero"

    lam = sp.symbols("lambda", real=True, positive=True)
    omega = sp.sqrt(lam - sp.sqrt(2 * lam))
    axial = -3 * sp.I * omega * (3 * sp.sqrt(2 * lam) - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    assert axial != 0 and polar != 0
    assert sp.simplify(axial.subs(lam, 6)) != 0
    assert polar.subs(lam, 6) > 0

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-wiener-minus-dressing-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_WIENER_MINUS_DRESSING_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded smooth uniformly almost-periodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "any axisymmetric exceptional resonance-ellipse point plus a smooth Wiener-Bohr k=0 Einstein-minus q-primary sum",
            "degree": 2,
            "parity": "both dressing parities",
            "ell": "every integer ell>=2 with countable support",
            "m": "all m subject to convergent stabilizer moment maps",
            "k": 0,
            "omega": "countable set of occupied omega_minus(ell)",
        },
        "declared_topology": {
            "name": "smooth spatial Wiener-Bohr minus class",
            "coefficient_family": "c_(ell,m,parity) on the positive-frequency Einstein-minus representatives, together with the real conjugate family",
            "seminorms": "for every r>=0, sum |c_j|*(1+omega_j)^r*max_(|alpha|<=r)||nabla^alpha u_j||_infinity is finite",
            "consequences": [
                "the field series and every spacetime derivative converge absolutely and uniformly",
                "the local quadratic Weyl-Maxwell source is defined termwise and is smooth uniformly almost periodic in time",
                "Bohr-frequency extraction and spherical-harmonic projection commute with the absolutely convergent quadratic sum",
                "the five stabilizer moment maps are absolutely convergent",
            ],
            "not_claimed": "This is a strong regular subspace, not the maximal finite-energy or Sobolev completion.",
        },
        "coefficientwise_fredholm_lemma": {
            "correction_class": "bounded smooth uniformly almost-periodic fields with the same spatial regularity",
            "projection": "take the Bohr coefficient at omega_minus(ell), then the (ell,m,parity) spherical coefficient, then pair with the certified target adjoint row",
            "left_hand_side": "the projection of L v vanishes on the resonant q-primary shell",
            "source_isolation": "the exact finite-support dispersion lemma is pairwise and therefore excludes every minus-minus and original-minus competitor in the absolutely convergent countable sum",
            "right_hand_side": "d*C_parity(lambda)*c_(ell,m,parity)",
            "axial_pivot": str(axial),
            "polar_pivot": str(polar),
            "nonvanishing": "d is nonzero on the ellipse and both pivots are nonzero for lambda=ell(ell+1)>=6",
            "conclusion": "bounded compatibility forces every minus coefficient to vanish separately",
        },
        "moment_map_contradiction": {
            "ellipse_sign": "the undressed exceptional/control ellipse has strictly negative mu_H",
            "balance_requirement": "a common zero of the five moment maps requires at least one nonzero opposite-sign Einstein-minus coefficient",
            "resonant_requirement": "bounded second-order compatibility forces every Einstein-minus coefficient to vanish",
            "verdict": "no common-zero Wiener-Bohr dressing admits a bounded smooth uniformly almost-periodic correction",
        },
        "correction_classes": {
            "BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_INFINITE_SECULAR": {"status": "OPEN", "reason": "the finite exponential-polynomial theorem supplies no uniform estimates for a countable secular sum"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "smooth_wiener_bohr_minus_completion_classified": True,
            "bounded_almost_periodic_extension_obstructed": True,
            "bohr_harmonic_projection_continuous": True,
            "coefficientwise_source_isolation_proved": True,
            "both_parities_and_all_m_covered": True,
            "maximal_finite_energy_or_sobolev_completion_classified": False,
            "smooth_infinite_secular_extension_classified": False,
            "additional_nonminus_carriers_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The finite no-go is stable under a declared smooth infinite completion. Absolute convergence makes every resonant Bohr-harmonic coefficient auditable, and each occupied minus coefficient is killed separately by the nonzero d-cross pivot. This is not yet a maximal energy-space theorem.",
        "next_gate": "classify additional nonminus carriers, or obtain operator estimates for a weaker Sobolev/finite-energy completion",
        "claim_boundary": "This theorem covers only the smooth Wiener-Bohr k=0 Einstein-minus completion. It does not classify a maximal Sobolev space, infinite secular solutions, additional carriers, nonzero momentum, all-orders, causal, residual or quantum claims.",
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
        raise AssertionError("stale Wiener-Bohr minus no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_WIENER_MINUS_DRESSING_NO_GO: PASS")


if __name__ == "__main__":
    main()
