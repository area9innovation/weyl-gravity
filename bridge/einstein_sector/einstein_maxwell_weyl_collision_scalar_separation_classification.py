"""Classify scalar H/Px/Rc separation on all 21 ell=2 collision fibres."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_collision_scalar_separation_classification.schema.json"
INPUTS = {
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "pressure": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
    "standard_inclusion": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "candidate13_separator": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json",
    "universal_opposite_sign_separator": ROOT / "bridge/certificates/einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator.json",
}

MASS_SQUARED = {
    "q_minus": 6 - 2 * sp.sqrt(3),
    "p_extra": sp.Rational(16, 3),
    "q_plus": 6 + 2 * sp.sqrt(3),
}
CURRENT_SIGN = {"q_minus": -1, "p_extra": 1, "q_plus": 1}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def feature(rho: sp.Expr, n: int, branch: str) -> sp.Matrix:
    omega = sp.sqrt(n * n * rho + MASS_SQUARED[branch])
    return sp.Matrix([omega**2, n * omega, n * n])


def separating_row(index: int, row: dict[str, object]) -> dict[str, object]:
    rho = sp.sympify(row["rho"])
    momenta = [int(n) for n in row["canonical_signed_momenta"]]
    require(momenta == [1, -2], f"candidate {index} is not an opposite-sign fibre")
    omega_m1 = sp.sqrt(rho + MASS_SQUARED["q_minus"])
    omega_p1 = sp.sqrt(rho + MASS_SQUARED["p_extra"])
    omega_m2 = sp.sqrt(4 * rho + MASS_SQUARED["q_minus"])
    omega_p2 = sp.sqrt(4 * rho + MASS_SQUARED["p_extra"])
    t1 = (omega_m1 + omega_p1) / 2
    t2 = (omega_m2 + omega_p2) / 2
    a = sp.Integer(1)
    b = t2 / 2 - t1
    c = -t1 * t2 / 2
    covector = sp.Matrix([a, b, c])
    coefficients: list[dict[str, object]] = []
    for n in momenta:
        for branch in MASS_SQUARED:
            value = sp.factor(CURRENT_SIGN[branch] * covector.dot(feature(rho, n, branch)))
            require(value.is_positive is True, f"candidate {index} lost strict separation on {branch}, n={n}")
            coefficients.append({
                "signed_momentum_n": n,
                "branch": branch,
                "current_sign": CURRENT_SIGN[branch],
                "exact_signed_coefficient": sp.sstr(value),
                "strictly_positive_exact": True,
            })
    return {
        "candidate_index": index,
        "rho": row["rho"],
        "signed_momenta": momenta,
        "classification": "STRICT_SCALAR_SEPARATOR",
        "midpoints": {"t1": sp.sstr(t1), "t2": sp.sstr(t2)},
        "separating_covector_abc": [sp.sstr(a), sp.sstr(b), sp.sstr(c)],
        "universal_factorization": {
            "n=1": "Q_1(omega)=(omega-t1)*(omega+t2/2)",
            "n=-2": "Q_-2(omega)=(omega-t2)*(omega+2*t1)",
            "ordering": "omega_qminus(n)<t_|n|<omega_p(n)<omega_qplus(n), while the second factor is positive",
        },
        "charge_functional": f"D=(-4*({sp.sstr(a)})/L)*mu_H+(4*({sp.sstr(b)})/(L*sqrt(rho)))*mu_Px+(2*({sp.sstr(c)})/rho)*R_c",
        "branch_fibre_coefficients": coefficients,
        "consequence": "{mu_H=mu_Px=R_c=0}={0}; hence the complete bounded generic two-fibre cone is {0}",
    }


def farkas_row(index: int, row: dict[str, object]) -> dict[str, object]:
    rho = sp.sympify(row["rho"])
    momenta = [int(n) for n in row["canonical_signed_momenta"]]
    require(momenta == [1, 2], f"candidate {index} is not a same-sign fibre")
    fourth_branch = "q_plus" if index in {16, 18, 19} else "p_extra"
    support = [(1, "q_minus"), (1, "q_plus"), (2, "q_minus"), (2, fourth_branch)]
    matrix = sp.Matrix.hstack(*[CURRENT_SIGN[branch] * feature(rho, n, branch) for n, branch in support])
    weights = []
    for column in range(4):
        minor = matrix[:, [j for j in range(4) if j != column]].det()
        weights.append((-1) ** column * minor)
    if weights[0].is_negative is True:
        weights = [-value for value in weights]
    require(all(value.is_positive is True for value in weights), f"candidate {index} lost its positive Farkas witness")
    require(all(sp.simplify(value) == 0 for value in matrix * sp.Matrix(weights)), f"candidate {index} Farkas dependence changed")
    return {
        "candidate_index": index,
        "rho": row["rho"],
        "signed_momenta": momenta,
        "classification": "POSITIVE_FARKAS_DEPENDENCE_NO_STRICT_SCALAR_SEPARATOR",
        "support": [{"signed_momentum_n": n, "branch": branch} for n, branch in support],
        "positive_weights": [sp.sstr(sp.factor(value)) for value in weights],
        "exact_identity": "sum_i y_i*current_sign(branch_i)*(omega_i^2,n_i*omega_i,n_i^2)=0 with every y_i>0",
        "consequence": "the scalar H/Px/Rc common zero is nontrivial, but the full resonance-joined bounded cone remains OPEN",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    ledger = records["candidate_ledger"]
    require(ledger["classification"]["twenty_one_distinct_admissible_candidates"], "collision ledger changed")
    require(ledger["candidate_ledger"]["positive_admissible_rows"] == 21, "collision count changed")
    moment = records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]
    require(moment["H"].startswith("mu_H=-(L/4) sum omega^2"), "Hamiltonian normalization changed")
    require(moment["P_x"].startswith("mu_Px=(L/4) sum k*omega"), "momentum normalization changed")
    require(records["pressure"]["source_pairings"]["circle_pressure"]["functional"] == "R_c(u)=(1/2) sum_j k_j^2 h_j", "pressure normalization changed")
    require("common parity-independent branch weights" in records["standard_inclusion"]["theorem"]["block_table"][0]["pullback_relative_operator"], "q-branch parity convention changed")
    require(records["axial_current"]["classification"]["complete_generic_axial_target_signature_three_one"], "axial current signs changed")
    require(records["polar_current"]["classification"]["complete_polar_target_inertia_3_1"], "polar current signs changed")
    require(records["candidate13_separator"]["classification"]["candidate13_complete_bounded_cone_is_origin"], "candidate-13 separator input changed")
    universal = records["universal_opposite_sign_separator"]["classification"]
    require(universal["universal_positive_rho_separator_certified"], "universal opposite-sign separator changed")
    require(universal["all_15_opposite_signed_real_generic_bounded_cones_are_origin"], "universal 15-fibre coverage changed")

    rows = ledger["candidate_ledger"]["rows"]
    classifications = [separating_row(i, row) if i <= 15 else farkas_row(i, row) for i, row in enumerate(rows, 1)]
    return {
        "schema": "einstein-maxwell-weyl-collision-scalar-separation-classification-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COLLISION_SCALAR_SEPARATION_CLASSIFICATION",
        "result_state": "UNIVERSAL_OPPOSITE_SIGN_BOUNDED_ORIGIN_AND_SIX_SCALAR_NONSEPARABLE_COLLISION_FIBRES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_21_ELL2_TWO_ABSOLUTE_MOMENTUM_COLLISION_BACKGROUNDS_SCALAR_RECEIVER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "21 distinct tuned compact magnetically supported Plebanski-Hacyan circumference fibres, kept separate",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "complete generic ell=2 q-minus, p-extra and q-plus coefficients on each candidate's two signed momentum fibres, both parities and all m, with reality conjugates",
            "degree": 2,
            "parity": "axial and polar",
            "ell": 2,
            "m": "all m=-2,...,2",
            "k": "candidatewise signed n=(1,-2) or (1,2), never identified across rho",
            "omega": "all generic q-minus, p-extra and q-plus positive-frequency shells",
        },
        "normalization": {
            "shell_features": "x_(branch,n)=(omega^2,n*omega,n^2)",
            "current_signs": CURRENT_SIGN,
            "charge_conversion": "S_H=-4*mu_H/L, S_P=4*mu_Px/(L*sqrt(rho)), S_R=2*R_c/rho",
        },
        "candidate_rows": classifications,
        "summary": {
            "strictly_separated_candidate_indices": list(range(1, 16)),
            "positive_farkas_candidate_indices": list(range(16, 22)),
            "opposite_sign_fibre_theorem": "for every rho>0 the n=(1,-2) complete generic carrier has bounded cone {0}; in particular this closes collision candidates 1-15",
            "same_sign_fibre_theorem": "all six n=(1,2) backgrounds have a nonzero scalar H/Px/Rc common-zero witness, so scalar separation alone cannot decide their full bounded cones",
        },
        "classification": {
            "all_21_collision_backgrounds_checked_exactly": True,
            "floating_point_sign_decision_used": False,
            "universal_positive_rho_opposite_sign_separator_certified": True,
            "fifteen_strict_scalar_separators_certified": True,
            "fifteen_complete_bounded_generic_cones_are_origin": True,
            "six_positive_farkas_dependences_certified": True,
            "six_scalar_common_zero_sets_nontrivial": True,
            "six_full_resonance_joined_bounded_cones_classified": False,
            "cross_background_mode_identification_made": False,
            "exceptional_or_generalized_zero_inputs_included": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Momentum orientation is decisive for the scalar bounded receiver: a universal midpoint factorization pressure-separates every positive-rho opposite-sign fibre, while every same-sign collision fibre has an exact nonzero scalar-null occupation. Only the six same-sign backgrounds require a resonance-amplitude join to decide their full bounded cones.",
        "next_gate": "compute and join the resonance ideals only for candidate indices 16 through 21; keep the six circumference backgrounds and their carrier maps distinct",
        "claim_boundary": "This classifies the real scalar H/Px/Rc receiver on all 21 declared generic ell=2 collision backgrounds. It proves complete bounded-origin theorems for indices 1-15, but does not classify the full bounded cones for 16-21, include exceptional/global inputs, identify backgrounds, prove all-orders integration, or construct causal, residual, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_collision_scalar_separation_classification --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_collision_scalar_separation_classification",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_collision_scalar_separation_classification",
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
        raise AssertionError("collision scalar-separation certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_COLLISION_SCALAR_SEPARATION_CLASSIFICATION: PASS")


if __name__ == "__main__":
    main()
