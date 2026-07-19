"""Candidatewise exact audit of the universal same-sign scalar occupation cone."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_collision_scalar_separation_classification import (
    CURRENT_SIGN,
    MASS_SQUARED,
    feature,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.schema.json"
INPUTS = {
    "universal_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "pressure": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
}
LABELS = [(n, branch) for n in (1, 2) for branch in MASS_SQUARED]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cofactors(block: sp.Matrix) -> list[sp.Expr]:
    values = [
        sp.factor((-1) ** column * block[:, [j for j in range(4) if j != column]].det())
        for column in range(4)
    ]
    return [-value for value in values] if values[0].is_negative is True else values


def audit_candidate(index: int, rho_text: str) -> dict[str, object]:
    rho = sp.sympify(rho_text)
    matrix = sp.Matrix.hstack(
        *[CURRENT_SIGN[branch] * feature(rho, n, branch) for n, branch in LABELS]
    )
    if matrix.rank() != 3:
        raise AssertionError(f"candidate {index} receiver rank changed")
    minors = []
    for support in itertools.combinations(range(6), 3):
        determinant = sp.factor(matrix[:, support].det())
        if determinant.is_zero is not False:
            raise AssertionError(f"candidate {index} acquired a support-three circuit")
        minors.append({"support_indices": list(support), "determinant": sp.sstr(determinant), "nonzero_exact": True})

    positive, other = [], []
    for support in itertools.combinations(range(6), 4):
        values = cofactors(matrix[:, support])
        if any(value.is_zero is not False for value in values):
            raise AssertionError(f"candidate {index} circuit degeneracy changed")
        signs = [1 if value.is_positive is True else -1 if value.is_negative is True else 0 for value in values]
        if 0 in signs:
            raise AssertionError(f"candidate {index} circuit sign undecided")
        record = {
            "support_indices": list(support),
            "support": [{"signed_momentum_n": LABELS[j][0], "branch": LABELS[j][1]} for j in support],
            "cofactor_weights": [sp.sstr(value) for value in values],
            "kernel_remainder": [sp.sstr(sp.expand(sp.factor(value))) for value in matrix[:, support] * sp.Matrix(values)],
        }
        if all(sign == 1 for sign in signs):
            record.update({"ray_id": f"R{len(positive)+1}", "all_weights_positive_exact": True})
            positive.append(record)
        else:
            record["sign_pattern"] = signs
            other.append(record)
    expected = [
        [(1, "q_minus"), (1, first), (2, "q_minus"), (2, second)]
        for first in ("p_extra", "q_plus")
        for second in ("p_extra", "q_plus")
    ]
    actual = [[(item["signed_momentum_n"], item["branch"]) for item in ray["support"]] for ray in positive]
    if actual != expected or len(other) != 11:
        raise AssertionError(f"candidate {index} positive circuit supports changed")
    return {
        "candidate_index": index,
        "rho": rho_text,
        "receiver_rank": 3,
        "occupation_ambient_dimension": 6,
        "cone_dimension": 3,
        "support_three_minors": minors,
        "positive_extreme_rays": positive,
        "nonpositive_circuits": other,
        "counts": {"support_three_minors": 20, "support_four_circuits": 15, "positive_extreme_rays": 4, "nonpositive_circuits": 11},
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    universal = records["universal_rays"]["classification"]
    if not universal["all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays"]:
        raise AssertionError("universal extreme-ray theorem changed")
    moment = records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]
    if not moment["H"].startswith("mu_H=-(L/4) sum omega^2") or not moment["P_x"].startswith("mu_Px=(L/4) sum k*omega"):
        raise AssertionError("moment-map normalization changed")
    if records["pressure"]["source_pairings"]["circle_pressure"]["functional"] != "R_c(u)=(1/2) sum_j k_j^2 h_j":
        raise AssertionError("pressure normalization changed")
    ledger = records["candidate_ledger"]["candidate_ledger"]["rows"]
    rows = []
    for index in range(16, 22):
        if ledger[index - 1]["canonical_signed_momenta"] != [1, 2]:
            raise AssertionError(f"candidate {index} momentum scope changed")
        rows.append(audit_candidate(index, ledger[index - 1]["rho"]))
    return {
        "schema": "einstein-maxwell-weyl-same-sign-collision-scalar-occupation-cones-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SCALAR_OCCUPATION_CONES",
        "result_state": "UNIVERSAL_FOUR_RAY_THEOREM_AUDITED_ON_ALL_SIX_ALGEBRAIC_CANDIDATES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_CANDIDATEWISE_SCALAR_OCCUPATION_AUDIT",
        "scope": {**records["universal_rays"]["scope"], "background": "six distinct algebraic collision candidates 16--21, retained separately"},
        "occupation_order": [{"index": i, "signed_momentum_n": n, "branch": branch, "current_sign": CURRENT_SIGN[branch]} for i, (n, branch) in enumerate(LABELS)],
        "candidate_rows": rows,
        "classification": {
            "all_six_scalar_occupation_cones_classified": True,
            "all_six_receiver_matrices_rank_three": True,
            "all_120_support_three_minors_nonzero": True,
            "all_90_support_four_circuits_classified": True,
            "four_positive_extreme_rays_per_candidate": True,
            "universal_extreme_support_combinatorics": True,
            "full_rotation_and_resonance_join_classified": False,
            "cross_background_mode_identification_made": False,
            "causal_residual_observational_or_quantum_claim": False
        },
        "theorem": "At each candidate 16--21, the exact 3x6 scalar receiver has twenty nonzero 3x3 minors and fifteen nondegenerate four-circuits, exactly four of which are positive; these instantiate the four universal moment-curve rays.",
        "interpretation": "This candidatewise algebraic audit independently checks the universal support theorem at every physical collision circumference. Amplitude lifts are certified separately.",
        "next_gate": "classify pairwise sums of the four lifted ray strata, retaining relative phases and parity vectors",
        "claim_boundary": "This is an exact candidatewise scalar projection audit. Rotations, resonance amplitudes, arbitrary sums, full bounded cones and higher lifecycles remain outside this certificate.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidatewise scalar occupation audit is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SCALAR_OCCUPATION_CONES: PASS")


if __name__ == "__main__":
    main()
