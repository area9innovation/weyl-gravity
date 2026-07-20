"""Freeze audit for the finite-harmonic second-order cone structure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-finite-harmonic-cone-structural-freeze-fragment-v1.json"

INPUTS = {
    "complete_finite": (
        "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
        "4230400a4d4ddfc5181749879b13df159c8d4de3a307a42fa3c916de2ec6c885",
    ),
    "sign_resonance_join": (
        "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
        "63b605c2441e9cf9d38e8b542641f060cc1a240de0af377cee57ebb0c0b848fd",
    ),
    "all_m_intersection": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1.json",
        "48e782b8f1b37f7b603efdb9cc6b60b71f249fd94c6da99c4eb477613e2683b3",
    ),
    "abstract_finite_block": (
        "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
        "c80967db8cce02594a346bef3ec6a0f1d6863c85167aec7b661d2d102a248065",
    ),
    "paper_13": (
        "paper/13-compact-weyl-maxwell-second-order-tangent-cone.tex",
        "745b6c106f6e9153c12932d67bfd76292b1380a428d28e9950b277c5c6ce4e8b",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs() -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for name, (relative, expected) in INPUTS.items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(f"input drift: {name}: {actual} != {expected}")
        if path.suffix == ".json":
            loaded[name] = json.loads(path.read_text())
    return loaded


def build_certificate() -> dict:
    values = load_inputs()
    complete = values["complete_finite"]
    join = values["sign_resonance_join"]
    intersection = values["all_m_intersection"]
    abstract = values["abstract_finite_block"]

    assert complete["classification"]["complete_finite_harmonic_smooth_tangent_cone_classified"]
    assert complete["classification"]["complete_smooth_adjoint_cokernel_equals_five_stabilizers"]
    assert complete["classification"]["bounded_polynomial_and_resonant_ledger_defined"]
    assert not complete["classification"]["bounded_common_zero_locus_solved"]
    assert join["classification"]["bounded_necessity_and_sufficiency_formula_certified"]
    assert join["classification"]["complete_branch_labelled_obstruction_map_joined"]
    assert intersection["classification"]["physical_common_zero_is_origin"]
    assert abstract["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"

    provenance = {
        name: {"path": relative, "sha256": expected}
        for name, (relative, expected) in INPUTS.items()
    }
    return {
        "schema": "einstein-maxwell-weyl-finite-harmonic-cone-structural-freeze-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": provenance,
        "declared_carrier": complete["domain"],
        "second_order_equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
        "correction_classes": {
            "finite_exponential_polynomial": {
                "status": "THEOREM_READY_TIER3_BLOCKED",
                "criterion": "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
            },
            "bounded_or_finite_quasiperiodic": {
                "status": "LEDGER_READY_TIER3_BLOCKED_ZERO_LOCUS_OPEN",
                "criterion": "all mu_X, every positive polynomial coefficient P_(j,r), and every reduced characteristic-shell pairing R_(j,a) vanish",
            },
            "causal_retarded": {"status": "NO_CERTIFIED_MAP"},
        },
        "exponential_polynomial_surjectivity": {
            "scalar": "Every nonzero P(D_t) is surjective on finite exponential-polynomials; a root of multiplicity m costs at most m polynomial degrees.",
            "matrix": "Fibrewise unimodular Smith transformations reduce every nonzero matrix invariant factor to the scalar lemma.",
            "decisive_distinction": "A root of a nonzero invariant factor is removable by a secular primitive and is not a zero Smith factor.",
        },
        "output_strata": [
            {"stratum": "generic L>=2 nonstatic", "invariant_factors": ["1", "1", "p", "p*q"], "zero_factors": 0},
            {"stratum": "generic L>=2 static", "invariant_factors": ["p<0", "q>0"], "zero_factors": 0},
            {"stratum": "exceptional L=1 nonstatic", "invariant_factors": ["nonzero shell factors"], "zero_factors": 0},
            {"stratum": "scalar L=0 nonzero (Omega,K)", "invariant_factors": ["exact modulo local gauge and Noether"], "zero_factors": 0},
            {"stratum": "homogeneous L=0 zero block", "invariant_factors": ["D_t^4", "D_t^2", "0", "0"], "zero_factors": 2, "covectors": ["zeta_H", "zeta_Px"]},
            {"stratum": "axial dipole L=1 zero block", "invariant_factors": ["twist polynomial operator", "0", "0", "0"], "zero_factors": 3, "covectors": ["zeta_J1", "zeta_J2", "zeta_J3"]},
        ],
        "coverage_ledger": {
            "generic": "CERTIFIED",
            "exceptional": "CERTIFIED",
            "generalized_homogeneous": "CERTIFIED",
            "twist_position_and_velocity": "CERTIFIED",
            "electric_and_wilson": "CERTIFIED",
            "opposite_momentum_and_relative_phase": "CERTIFIED_AS_BLOCKWISE_LEDGER",
            "multiple_absolute_momentum": "CERTIFIED_FOR_FINITE_EP_AND_AS_BLOCKWISE_BOUNDED_LEDGER",
            "declared_cross_fibre": "CERTIFIED_AS_BLOCKWISE_LEDGER",
        },
        "adjoint_cokernel": {
            "decomposition": "coker(L_EP)=span(zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3)",
            "dimension": 5,
            "generalized_mode_slice_independence": "The Lee-Wald current of u and L_X u is conserved on the closed cylinder, including polynomial Jordan representatives.",
            "no_sixth_U1_cokernel": "Constant U1 reducibility is Noether-trivial on connection differences and the magnetic Chern class is fixed.",
        },
        "bounded_independence_witnesses": {
            "polynomial_growth": "A certified aligned global-extra tangent has all five mu_X zero and a nonzero t^2 source coefficient.",
            "characteristic_shell": "A certified twist-balanced exceptional tangent has all five mu_X zero and nonzero R_bounded.",
            "locked_all_m": "On the declared pure-extra k-to-2k face the physical common zero is the origin, while its complex resonance-only incidence is nontrivial.",
        },
        "freeze_disposition": {
            "structural_theorem": "THEOREM_READY_TIER3_BLOCKED",
            "paper_13_overall": "DRAFT_ALLOWED",
            "reason": "The scoped theorem and independent mutations pass, but the required Einstein-package Tier-3 rail fails on a transitive stale-provenance chain rooted at the Lee-Wald component API extension; fail-closed policy blocks lifecycle promotion. The unrestricted real common zero of the bounded quadratic ledger is also not classified.",
            "literature_position": "The momentum-map normal form is classical (Brill-Deser, Fischer-Marsden, Moncrief, Arms-Marsden-Moncrief); the model-specific contribution is the exhaustive Weyl-Maxwell block/cokernel and bounded P/R ledger.",
        },
        "classification": {
            "finite_exponential_polynomial_cone_theorem_ready": True,
            "bounded_obstruction_ledger_theorem_ready": True,
            "theorem_freeze_promoted": False,
            "tier3_provenance_relock_complete": False,
            "bounded_common_zero_locus_solved": False,
            "all_declared_output_strata_present": True,
            "five_and_only_five_EP_cokernel_covectors": True,
            "infinite_harmonic_causal_all_orders_residual_particle_quantum_claim": False,
        },
        "claim_boundary": "This audits the exact finite-support exponential-polynomial cone and complete blockwise bounded-obstruction ledger on the compact Plebański-Hacyan carrier, but does not promote a new theorem-freeze lifecycle because the required Tier-3 package rail has unresolved transitive provenance drift. It does not classify the unrestricted bounded common zero, prove an infinite-mode, Sobolev, retarded, all-orders or final-residual theorem, or make scattering, particle, positivity or quantum claims.",
        "next_gate": "Complete the content-addressed re-lock cascade rooted at f92e7a5e9, obtain a clean Einstein-package Tier-3 run, and only then promote the structural freeze; the unrestricted bounded P/R common zero and causal/retarded classes remain separate open gates.",
    }


def build_atlas(cert_hash: str) -> dict:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "generated_by": "bridge/einstein_sector/einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py",
        "generated_by_sha256": sha256(
            ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py"
        ),
        "entries": [{
            "id": "einstein.ph.wm.finite_harmonic_cone.structural_freeze",
            "scope": {
                "theory": "linearized four-dimensional Weyl-Maxwell target at second order",
                "background": "compactified magnetically supported Plebanski-Hacyan product",
                "boundaries": "closed S1_L times S2; finite EP or bounded finite quasiperiodic correction class",
                "charge_sector": "fixed magnetic Chern class; electric and Wilson tangents included",
                "carrier": "complete certified finite harmonic inventory before final residual quotient",
                "degree": 2, "parity": "all certified", "ell": "0, 1, and finite subsets of ell>=2",
                "m": "all certified magnetic labels", "k": "finite subsets of allowed compact momenta",
                "omega": "all certified shells plus generalized zero modes",
            },
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED",
                "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "All nonzero invariant factors, including shell roots, are EP-surjective."},
                "lee_wald": {"status": "CERTIFIED", "statement": "Five Taub covectors are slice-independent on the closed cylinder."},
                "taub_maps": {"status": "CERTIFIED", "statement": "Exactly H, Px and three lifted rotations survive in the EP cokernel."},
                "resonance": {"status": "OPEN", "statement": "The bounded P/R ledger is complete, but its unrestricted real common zero is open."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "CERTIFIED", "statement": "Necessary and sufficient blockwise P/R/moment ledger; global zero locus open."},
                    "smooth_secular": {"status": "CERTIFIED", "statement": "Exactly the five moment maps obstruct finite EP correction."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."},
                },
            },
            "evidence": [{"path": "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json", "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1", "sha256": cert_hash}],
            "claim_boundary": "Finite-support reduced-mode theorem only; bounded global zero locus, infinite completion, causal propagation, all orders, final residual descent and quantum interpretation remain open.",
        }],
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-finite-harmonic-cone-structural-freeze-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert = build_certificate()
    rendered = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert OUTPUT.read_text() == rendered
        atlas = build_atlas(sha256(OUTPUT))
        assert ATLAS.read_text() == json.dumps(atlas, indent=2, sort_keys=True) + "\n"
        print(f"{cert['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    ATLAS.write_text(json.dumps(build_atlas(sha256(OUTPUT)), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
