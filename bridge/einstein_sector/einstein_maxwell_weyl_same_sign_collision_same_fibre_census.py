"""Certify all nonzero-frequency same-fibre blocks off shell at candidates 16--21."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import certified_nonzero_interval, fraction_string


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.schema.json"
INPUTS = {
    "collision_classifier": ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json",
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "ell0_nonzero_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell0_homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "ell1_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
}
MASS = {"q_minus": 6 - 2 * sp.sqrt(3), "p_extra": sp.Rational(16, 3), "q_plus": 6 + 2 * sp.sqrt(3)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def witness(value: sp.Expr) -> dict[str, object]:
    certified = certified_nonzero_interval(sp.factor(value))
    if certified is None:
        raise AssertionError(f"same-fibre shell collision found: {value}")
    bounds, digits = certified
    return {
        "expression": sp.sstr(sp.factor(value)),
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }


def candidate_row(index: int, rho: sp.Expr) -> dict[str, object]:
    channels = []
    for n in (1, 2):
        omega = {branch: sp.sqrt(n * n * rho + mass) for branch, mass in MASS.items()}
        for first, second in itertools.combinations_with_replacement(MASS, 2):
            temporal = [("SUM", omega[first] + omega[second], 4 * n * n * rho)]
            if first != second:
                temporal.append(("DIFFERENCE", omega[first] - omega[second], sp.S.Zero))
            for kind, frequency, momentum_squared in temporal:
                spectral = sp.factor(frequency**2 - momentum_squared)
                defects = [
                    {"output_ell": 1, "target": "extra", "witness": witness(spectral - sp.Rational(4, 3))},
                    {"output_ell": 1, "target": "standard", "witness": witness(spectral - 4)},
                ]
                for ell in (2, 3, 4):
                    lam = ell * (ell + 1)
                    defects.extend([
                        {"output_ell": ell, "target": "p_extra", "witness": witness(spectral - (lam - sp.Rational(2, 3)))},
                        {"output_ell": ell, "target": "q_primary", "witness": witness((spectral - lam) ** 2 - 2 * lam)},
                    ])
                channels.append({
                    "abs_momentum_n": n,
                    "first_branch": first,
                    "second_branch": second,
                    "temporal_channel": kind,
                    "ell0_disposition": "empty nonzero-Fourier quotient" if kind == "SUM" else "empty homogeneous nonzero-frequency quotient",
                    "defects": defects,
                })
    if len(channels) != 18 or sum(len(row["defects"]) for row in channels) != 144:
        raise AssertionError("same-fibre census cardinality changed")
    return {"candidate_index": index, "rho": sp.sstr(rho), "channel_count": 18, "nonzero_defect_count": 144, "channels": channels}


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    classifier = records["collision_classifier"]
    if classifier["summary"]["positive_farkas_candidate_indices"] != list(range(16, 22)):
        raise AssertionError("same-sign candidate set changed")
    if not records["ell0_nonzero_fourier"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"]:
        raise AssertionError("ell0 Fourier quotient changed")
    if not records["ell0_homogeneous"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"]:
        raise AssertionError("homogeneous quotient changed")
    if records["ell1_cofiber"]["theorem"]["shells"] != {"extra": "4/3", "standard": "4"}:
        raise AssertionError("ell1 shells changed")
    source_rows = records["candidate_ledger"]["candidate_ledger"]["rows"]
    for index in range(16, 22):
        if source_rows[index - 1]["canonical_signed_momenta"] != [1, 2]:
            raise AssertionError(f"candidate {index} same-sign momentum scope changed")
    rows = [candidate_row(index, sp.sympify(source_rows[index - 1]["rho"])) for index in range(16, 22)]
    return {
        "schema": "einstein-maxwell-weyl-same-sign-collision-same-fibre-census-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SAME_FIBRE_CENSUS",
        "result_state": "ALL_SIX_SAME_SIGN_CANDIDATES_HAVE_NO_NONZERO_FREQUENCY_SAME_FIBRE_SHELL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_SIX_SAME_SIGN_COLLISION_BACKGROUNDS_SAME_FIBRE_SHELL_CENSUS",
        "scope": {
            **classifier["scope"],
            "background": "six distinct candidates 16--21 only, retained separately",
            "carrier": "same-fibre products of all generic ell=2 branches on each n=1 and n=2 fibre",
            "omega": "all positive-positive sums and unequal-branch positive-negative differences; zero-frequency equal-branch products excluded",
        },
        "candidate_rows": rows,
        "summary": {"candidate_indices": list(range(16, 22)), "channels_per_candidate": 18, "defects_per_candidate": 144, "total_exact_nonzero_defects": 864},
        "classification": {
            "all_six_same_sign_candidates_checked_exactly": True,
            "all_108_same_fibre_temporal_channels_off_shell": True,
            "all_864_target_shell_defects_nonzero": True,
            "same_fibre_nonzero_frequency_source_matrices_required": False,
            "zero_frequency_receiver_imported_separately": True,
            "cross_fibre_resonance_join_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "For candidates 16--21, the only remaining bounded nonzero-frequency conditions are their already classified cross-fibre resonance ideals; no same-fibre source matrix is needed.",
        "next_gate": "intersect each candidate-specific cross-fibre zero variety with its exact Farkas scalar-null occupation and the rotation-zero locus",
        "claim_boundary": "This is an exact shell census on six distinct generic backgrounds. It excludes zero-frequency equal-branch sources, does not yet construct bounded points or classify the six full cones, and makes no all-orders, causal, residual, observational or quantum claim.",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": sha(Path(__file__)), "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()}},
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_same_fibre_census --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_collision_same_fibre_census",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_collision_same_fibre_census",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(json.loads(rendered))
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("same-sign same-fibre census is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SAME_FIBRE_CENSUS: PASS")


if __name__ == "__main__":
    main()
