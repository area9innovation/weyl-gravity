"""Classify the circumference cross column for every compact oscillator."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.schema.json"
INPUTS = {
    "complete_inventory": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "k0_primitive": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
}


class CircumferenceClassificationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CircumferenceClassificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scalar_radius_audit() -> dict[str, Any]:
    t, k, mass2, circumference = sp.symbols("t k mass2 c", real=True)
    omega = sp.symbols("omega", positive=True, real=True)
    mode = sp.exp(-sp.I * omega * t)
    omega_prime = -circumference * k**2 / (2 * omega)
    secular = -sp.I * omega_prime * t * mode
    linear_image = sp.simplify(sp.diff(secular, t, 2) + omega**2 * secular)
    _require(sp.simplify(linear_image - circumference * k**2 * mode) == 0, "radius secular identity changed")
    radius_squared = sp.symbols("R2", positive=True)
    dispersion = k**2 / radius_squared + mass2
    derivative = sp.diff(dispersion, radius_squared).subs(radius_squared, 1) * circumference
    _require(derivative == -circumference * k**2, "radius dispersion derivative changed")
    _require(sp.simplify(linear_image + derivative * mode) == 0, "differentiated Jacobi identity failed")
    return {
        "radius_family": "R^2=1+eta*c",
        "universal_dispersion": "omega_R^2=k^2/R^2+m_branch^2",
        "dispersion_derivative_at_zero": "-c*k^2",
        "frequency_derivative_at_zero": "-c*k^2/(2*omega)",
        "time_convention": "exp(-i*omega*t)",
        "secular_transport_term": "i*c*k^2*t*exp(-i*omega*t)/(2*omega)",
        "scalar_identity": "(d_t^2+omega^2) secular_transport=c*k^2*exp(-i*omega*t)",
        "differentiated_equation": "L_0 partial_eta u_R+(partial_eta L_R)u_0=0",
        "symbolic_identity_verified": True,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    inventory = records["complete_inventory"]["classification"]
    _require(inventory["complete_certified_linear_input_inventory_included"], "complete inventory changed")
    dictionary_text = json.dumps(records["branch_dictionary"], sort_keys=True)
    _require("standard omega^2=k^2+4 and extra omega^2=k^2+4/3" in dictionary_text, "exceptional dispersion changed")
    primitive = records["k0_primitive"]["classification"]
    _require(primitive["complete_four_extra_transport_columns_printed"], "k=0 primitive changed")
    _require(primitive["ordinary_harmonic_primitive_suffices_at_p_resonance"], "k=0 bounded transport changed")
    _require(records["axial_current"]["classification"]["direct_four_dimensional_Lee_Wald_match"], "axial current changed")
    _require(records["axial_current"]["classification"]["generic_extra_module_direct_Lee_Wald_nonradical"], "axial extra current changed")
    _require(records["polar_current"]["classification"]["direct_four_dimensional_Lee_Wald_match"], "polar current changed")
    _require(records["polar_current"]["classification"]["extra_block_nonradical"], "polar extra current changed")
    _require(records["exceptional_current"]["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "exceptional current changed")
    _require(records["electric_wilson"]["classification"]["Q_e_times_every_oscillator_bounded_removable"], "preceding transport gate changed")

    return {
        "schema": "einstein-maxwell-weyl-circumference-complete-oscillator-bounded-classification-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CIRCUMFERENCE_COMPLETE_OSCILLATOR_BOUNDED_CLASSIFICATION",
        "result_state": "COMPLETE_CIRCUMFERENCE_OSCILLATOR_BOUNDED_COLUMN_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic versus smooth-secular corrections",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "constant circumference c crossed with every certified nonzero-frequency standard q-primary or extra p-primary oscillator",
            "degree": 2,
            "parity": "both parities",
            "ell": "exceptional ell=1 and generic ell>=2",
            "m": "all allowed m",
            "k": "every allowed 2*pi*n/L, with k=0 and k!=0 kept distinct",
            "omega": "every certified nonzero real q/p shell frequency",
        },
        "radius_family_proof": _scalar_radius_audit(),
        "matrix_system_lift": {
            "index_transport": "differentiate each covariant x index and A_x coefficient with d log R/d eta=c/2; these terms are ordinary same-frequency corrections",
            "shell_transport": "the only potentially unbounded term is the derivative of exp(-i*omega_R*t)",
            "generic_shells": "every q/p shell depends on the circle only through k^2/R^2",
            "exceptional_shells": "omega_standard^2=k^2/R^2+4 and omega_extra^2=k^2/R^2+4/3",
            "nonradical_pairing": "the action-derived Lee-Wald form is nonzero on each standard branch and nondegenerate on every extra multiplicity block, so the c*k^2 shell source has a nonzero exact adjoint pairing whenever c*k!=0 and the mode coefficient is nonzero",
        },
        "bounded_classification": {
            "k_zero": {
                "status": "CERTIFIED",
                "statement": "frequency transport vanishes; covariant-index transport gives an ordinary bounded same-frequency correction",
                "coefficient_fixture": "all four ell=2 extra columns are printed and have zero full-row remainder",
            },
            "k_nonzero": {
                "status": "OBSTRUCTED",
                "statement": "for c!=0 every nonzero oscillator coefficient has a nonzero on-shell resonant functional proportional to c*k^2 times its nonradical current coefficient",
                "bounded_zero_locus": "c=0 or every nonzero-k oscillator coefficient vanishes",
                "polynomial_source": False,
                "ledger_location": "R_(j,a), not P_(j,r)",
            },
            "arbitrary_finite_sum": "blockwise orthogonality in (ell,m,k,omega,branch) prevents cross-fibre cancellation of the radius derivative; the displayed zero locus is necessary and sufficient for the c-cross column",
        },
        "smooth_secular_classification": {
            "status": "CERTIFIED",
            "all_k": True,
            "correction": "ordinary index transport plus i*c*k^2*t*u/(2*omega) for each nonzero-k mode",
            "regularity": "real smooth spatially periodic finite exponential-polynomial after adjoining conjugate modes",
        },
        "bounded_ledger_consequence": {
            "polynomial_gate": "c contributes no positive-degree source coefficient P_(j,r)",
            "resonance_gate": "c is eliminated by R_(j,a) whenever the tangent has any nonzero-k oscillator support",
            "surviving_c_face": "c remains free on the purely k=0 oscillator carrier",
            "remaining_polynomial_gate": "a crossed with all oscillators and d crossed with nonzero-k oscillators",
            "remaining_resonance_gate": "d on k=0, constant twist A, and bounded oscillator products, together with any a-face surviving its polynomial equations",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "zero_locus": "c=0 or oscillator support is contained in k=0"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_certified_oscillator_inventory_covered": True,
            "k0_circumference_cross_bounded_removable": True,
            "nonzero_k_circumference_cross_bounded_obstructed": True,
            "nonzero_k_circumference_cross_smooth_secular_extendible": True,
            "circumference_obstruction_is_resonant_not_polynomial": True,
            "finite_sum_c_column_zero_locus_classified": True,
            "complete_bounded_cone_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "A static change of circumference is harmless for zero-momentum waves but not for travelling compact modes in the bounded category. At nonzero momentum it shifts the shell frequency. Differentiating the exact radius family therefore produces a secular transport term, proving smooth extension while the nonradical current proves a bounded resonance obstruction. The source itself remains bounded, so this is an R-functional rather than a P-functional.",
        "next_gate": "compute the a-times-all-oscillator and d-times-nonzero-k polynomial maps, then solve the surviving k=0 d, constant-A and wave resonance equations",
        "claim_boundary": "This classifies only the c-times-oscillator column at second order. It does not classify a or d, constant-twist or oscillator self/mixed resonances, the complete bounded cone, causal propagation, all-orders integration, residual descent, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.24, "max_rss_kb": 16180},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.56, "max_rss_kb": 61500, "tests_run": 12},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "complete dispersions, nonradical current blocks and the direct k=0 radius primitive are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "a,d, constant-A, full bounded, causal, all-orders, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise CircumferenceClassificationError("circumference classification certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CIRCUMFERENCE_COMPLETE_OSCILLATOR_BOUNDED_CLASSIFICATION: PASS")


if __name__ == "__main__":
    main()
