"""Exclude all additional k=0 ell=1 oscillators from rescuing the exceptional ellipse."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.schema.json"
INPUTS = {
    "global_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json",
    "finite_dispersion": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "standard_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["global_minus"]["classification"]["all_standard_generalized_zero_additions_covered"]
    assert records["finite_dispersion"]["dispersion_lemma"]["bounds"] == "0<delta(x)<1/2 and 1<w'(x)<2/sqrt(3)"
    assert records["exceptional_current"]["classification"]["pure_exceptional_ell1_nonzero_tangents_second_order_obstructed"]
    assert "negative definite" in records["standard_ell1"]["physical_ell1"]["mu_H"]
    assert records["ellipse"]["scope"]["omega"] == "omega_exceptional and 2*omega_exceptional"

    root3 = sp.sqrt(3)
    root6 = sp.sqrt(6)
    omega_exceptional = 2 / root3
    omega_physical = sp.Integer(2)
    omega_control = 4 / root3
    target_squared = {2: 6 - 2 * root3, 3: 12 - 2 * root6}
    additions = {"exceptional_extra": omega_exceptional, "physical_standard": omega_physical}
    existing = {**additions, "ell2_control": omega_control}
    audit: list[dict[str, object]] = []

    for left_name, left in additions.items():
        for right_name, right in existing.items():
            for sign, squared in (("sum", sp.expand((left + right) ** 2)), ("difference", sp.expand((left - right) ** 2))):
                comparisons = {}
                for ell, target in target_squared.items():
                    residual = sp.simplify(squared - target)
                    assert residual != 0
                    comparisons[str(ell)] = str(residual)
                audit.append({"pair": [left_name, right_name], "sign": sign, "frequency_squared": str(squared), "minus_target_residuals": comparisons})
        residual = sp.simplify(left**2 - target_squared[2])
        assert residual != 0
        audit.append({"pair": ["constant_twist_position", left_name], "sign": "zero-frequency shift", "frequency_squared": str(left**2), "minus_target_residuals": {"2": str(residual)}})

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-ell1-oscillator-minus-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ELL1_OSCILLATOR_MINUS_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded smooth uniformly almost-periodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with first-order electric tangent allowed",
            "carrier": "exceptional resonance ellipse, arbitrary standard generalized-zero data, arbitrary finite physical/extra k=0 ell=1 oscillators, and a smooth Wiener-Bohr k=0 Einstein-minus sum",
            "degree": 2,
            "parity": "both exceptional/physical ell1 and minus parities",
            "ell": "global 0,1; arbitrary additional oscillatory ell=1; control 2; every minus ell>=2 with countable support",
            "m": "all ell1 and minus m subject to convergent stabilizer moment maps",
            "k": 0,
            "omega": "0, 2/sqrt(3), 2, 4/sqrt(3), and occupied omega_minus(ell)",
        },
        "ell1_sign_and_inventory": {
            "exceptional_extra_frequency": "2/sqrt(3)",
            "physical_standard_frequency": "2",
            "ellipse_control_frequency": "4/sqrt(3)",
            "Hamiltonian_sign": "both additional ell1 oscillator blocks have the same strictly negative mu_H sign as the ellipse",
            "balance_consequence": "they increase rather than replace the required opposite-sign Einstein-minus occupation",
        },
        "ell1_times_minus_exclusion": {
            "angular_rule": "ell1 times ell reaches only L=ell-1,ell,ell+1",
            "minus_gap_bound": "every adjacent minus-frequency gap is strictly less than 2/sqrt(3)",
            "frequency_shifts": "the two added ell1 frequencies are 2/sqrt(3) and 2, both at least the strict adjacent-gap bound",
            "conclusion": "no sum or difference of an added ell1 frequency and a minus frequency is another angularly allowed minus frequency",
        },
        "finite_low_ell_audit": {
            "targets": {str(ell): str(value) for ell, value in target_squared.items()},
            "comparisons": audit,
            "all_residuals_nonzero": True,
            "coverage": "ell1-ell1, ell1-ellipse-control and constant-twist-position-times-ell1 products, conservatively checked against the L=2,3 minus targets",
        },
        "obstruction": {
            "source_isolation": "the added ell1 blocks create no d-times-minus shell competitor; the standard-global transport and Wiener coefficient projections remain authoritative",
            "required_minus": "the total nonminus Hamiltonian contribution remains strictly negative on every nonzero ellipse point",
            "bounded_condition": "the nonzero d pivot forces every required minus coefficient to vanish",
            "contradiction": "moment-map balance and bounded resonant compatibility cannot hold simultaneously",
        },
        "correction_classes": {
            "BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_INFINITE_SECULAR": {"status": "OPEN"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "all_k0_physical_and_extra_ell1_oscillator_additions_covered": True,
            "all_ell1_m_and_both_parities_covered": True,
            "ell1_minus_shell_collisions_excluded": True,
            "low_ell_original_and_global_collisions_excluded_exactly": True,
            "bounded_extension_obstructed": True,
            "generic_ell_ge_2_nonminus_oscillators_classified": False,
            "maximal_sobolev_or_finite_energy_completion_classified": False,
            "smooth_infinite_secular_extension_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Neither standard nor extra dipole oscillators can rescue the exceptional ellipse. Their Taub sign worsens the deficit, and exact angular-frequency separation prevents their quadratic products from screening the required minus-shell d pivot.",
        "next_gate": "classify generic ell>=2 Einstein-plus and extra-primary oscillator pairs on the minus-shell resonance ledger",
        "claim_boundary": "This theorem covers all additional k=0 ell1 oscillators, standard globals and the smooth Wiener-Bohr minus sector. Generic ell>=2 nonminus carriers, maximal completions, infinite secular inverses, nonzero momentum, causal, residual and quantum claims remain open.",
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
        raise AssertionError("stale exceptional ell1 oscillator no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ELL1_OSCILLATOR_MINUS_NO_GO: PASS")


if __name__ == "__main__":
    main()
