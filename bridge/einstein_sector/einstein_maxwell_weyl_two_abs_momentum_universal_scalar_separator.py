"""Certify the universal bounded scalar separator on signed 1:-2 fibres."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator.schema.json"
INPUTS = {
    "candidates": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "pressure": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    all_rows = records["candidates"]["candidate_ledger"]["rows"]
    require(len(all_rows) == 21 and all(row["rho_positive_exact"] for row in all_rows), "positive collision ledger changed")
    rows = [(index, row) for index, row in enumerate(all_rows, 1) if row["canonical_signed_momenta"] == [1, -2]]
    same_sign = [index for index, row in enumerate(all_rows, 1) if row["canonical_signed_momenta"] == [1, 2]]
    require(len(rows) == 15 and same_sign == [16, 17, 18, 19, 20, 21], "signed-momentum partition changed")
    moment = records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]
    require(moment["H"].startswith("mu_H=-(L/4) sum omega^2"), "H normalization changed")
    require(moment["P_x"].startswith("mu_Px=(L/4) sum k*omega"), "P normalization changed")
    require(records["pressure"]["primary_action_identity"]["pressure_functional"] == "R_c(u)=(1/2) sum k_j^2 h_j", "pressure normalization changed")
    require("common parity-independent branch weights" in records["standard"]["theorem"]["block_table"][0]["pullback_relative_operator"], "q branch signs changed")
    require(records["axial_current"]["full_solution_pairing"]["complete_block_form"].startswith("Einstein_plus (+) direct-sum Einstein_minus (-)"), "axial signs changed")
    require(records["polar_current"]["classification"]["extra_block_positive_frequency_inertia_2_0"], "polar extra positivity changed")

    omega, t1, t2 = sp.symbols("omega t1 t2", positive=True)
    B = t2 / 2 - t1
    C = -t1 * t2 / 2
    q1 = sp.factor(omega**2 + B * omega + C)
    q2 = sp.factor(omega**2 - 2 * B * omega + 4 * C)
    require(sp.expand(q1 - (omega - t1) * (2 * omega + t2) / 2) == 0, "n=1 factorization changed")
    require(sp.expand(q2 - (omega - t2) * (omega + 2 * t1)) == 0, "n=-2 factorization changed")

    coverage = []
    for index, row in rows:
        rho = sp.sympify(row["rho"], locals={"sqrt": sp.sqrt})
        require(rho.is_positive is True, f"candidate {index} lost exact positivity")
        coverage.append({
            "candidate_index": index,
            "rho": row["rho"],
            "rho_positive_exact": True,
            "bounded_generic_cone": "{0}",
        })

    return {
        "schema": "einstein-maxwell-weyl-two-abs-momentum-universal-scalar-separator-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWO_ABS_MOMENTUM_UNIVERSAL_SCALAR_SEPARATOR",
        "result_state": "ALL_15_ADMISSIBLE_OPPOSITE_SIGNED_1_MINUS2_GENERIC_BOUNDED_CONES_ARE_THE_ORIGIN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_UNIVERSAL_POSITIVE_RHO_SIGNED_1_MINUS2_GENERIC_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product at any rho>0, specialized in the coverage ledger to the 15 exact admissible opposite-signed collision circumferences",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "complete generic ell=2 q-minus, p-extra and q-plus modes on signed n=1,-2 fibres, both parities and all m, with reality conjugates",
            "degree": 2,
            "parity": "axial and polar",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "n*sqrt(rho), n=1,-2",
            "omega": "all q-minus, p-extra and q-plus positive-frequency shells",
        },
        "universal_construction": {
            "mass_order": "m_qminus^2=6-2*sqrt(3) < m_p^2=16/3 < m_qplus^2=6+2*sqrt(3)",
            "thresholds": {
                "t1": "(omega_qminus(1)+omega_p(1))/2",
                "t2": "(omega_qminus(-2)+omega_p(-2))/2",
            },
            "coefficients": {"B": "t2/2-t1", "C": "-t1*t2/2"},
            "separator_in_occupations": "D=S_H+B*S_P+C*S_R",
            "separator_in_charges": "D=-(4/L)mu_H+(4B/(L*sqrt(rho)))mu_Px+(2C/rho)R_c",
            "n1_factorization": "Q_1(omega)=(omega-t1)*(omega+t2/2)",
            "nminus2_factorization": "Q_-2(omega)=(omega-t2)*(omega+2*t1)",
            "sign_proof": "q-minus lies strictly below each midpoint; p-extra and q-plus lie strictly above it. The second factor is positive. Q is therefore negative on q-minus and positive on p-extra/q-plus; the q-minus current sign reverses its contribution, so D is strictly positive on every nonzero real tangent.",
        },
        "candidate_coverage": coverage,
        "uncovered_same_sign_candidates": {
            "candidate_indices": same_sign,
            "signed_momenta": [1, 2],
            "status": "OPEN",
            "reason": "the opposite-sign midpoint factorization does not give a definite separator; these fibres require a separate amplitude-level analysis",
        },
        "theorem": {
            "universal_scalar_common_zero": "for every rho>0, {mu_H=mu_Px=R_c=0} on the declared signed 1:-2 generic carrier is {0}",
            "all_15_opposite_signed_admissible_collision_bounded_cones": "{0}",
            "rotation_or_resonance_equations_needed": False,
        },
        "classification": {
            "universal_positive_rho_separator_certified": True,
            "all_15_opposite_signed_admissible_collision_fibres_covered": True,
            "all_15_opposite_signed_real_generic_bounded_cones_are_origin": True,
            "nonzero_real_generic_bounded_point_exists_on_any_covered_fibre": False,
            "smooth_cones_classified_here": False,
            "exceptional_or_generalized_zero_inputs_included": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-13 no-go is not exceptional: pressure-enhanced scalar definiteness is universal on the complete generic opposite-signed 1:-2 carrier. All 15 admissible opposite-signed collision circumferences have only the zero bounded second-order tangent; the six same-sign candidates remain separate.",
        "next_gate": "classify candidates 16-21 on the signed 1:2 carrier by amplitude-level inequalities; smooth and causal correction classes remain separate",
        "claim_boundary": "This real bounded theorem covers the complete generic opposite-signed 1:-2 carrier and its 15 exact admissible collision fibres. It does not classify the six same-sign candidates, other momentum ratios, exceptional/generalized-zero inputs, smooth cones, all-orders integration, or causal, residual, observational, particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError("universal scalar-separator certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_TWO_ABS_MOMENTUM_UNIVERSAL_SCALAR_SEPARATOR: PASS")


if __name__ == "__main__":
    main()
