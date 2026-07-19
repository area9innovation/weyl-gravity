"""Enumerate every isolated positive circumference on the first two-|k| carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit import branch_offsets


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.schema.json"
INPUTS = {
    "identity_audit": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.json",
    "multimomentum": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_rows() -> list[dict[str, object]]:
    inputs, targets = branch_offsets()
    rows: list[dict[str, object]] = []
    for relative_sign in (-1, 1):
        n_1, n_2 = 1, 2 * relative_sign
        for first_name, first_offset in inputs.items():
            for second_name, second_offset in inputs.items():
                for (output_ell, target_name), target_offset in targets.items():
                    difference = target_offset - first_offset - second_offset
                    coefficient = sp.radsimp(n_1**2 * second_offset + n_2**2 * first_offset - n_1 * n_2 * difference)
                    constant = sp.radsimp(4 * first_offset * second_offset - difference**2)
                    if coefficient == 0:
                        continue
                    rho = sp.factor(sp.radsimp(-constant / (4 * coefficient)))
                    if rho.is_positive is not True:
                        continue
                    unsquared_sign = sp.radsimp(2 * n_1 * n_2 * rho + difference)
                    if unsquared_sign.is_positive is True:
                        temporal_channel = "SUM"
                    elif unsquared_sign.is_negative is True:
                        temporal_channel = "DIFFERENCE"
                    else:
                        raise AssertionError(f"undecided exact sign: {unsquared_sign}")
                    rows.append({
                        "relative_spatial_sign": relative_sign,
                        "canonical_signed_momenta": [n_1, n_2],
                        "first_branch": first_name,
                        "second_branch": second_name,
                        "output_ell": output_ell,
                        "target_branch": target_name,
                        "rho": str(rho),
                        "rho_positive_exact": True,
                        "unsquared_sign": str(sp.factor(unsquared_sign)),
                        "admissible_temporal_channel": temporal_channel,
                    })
    assert len(rows) == 21
    assert len({row["rho"] for row in rows}) == 21
    return rows


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["identity_audit"]["classification"]["no_identity_resonant_channel"]
    assert records["multimomentum"]["classification"]["finite_nonidentity_exceptional_circumference_set_certified"]
    rows = candidate_rows()
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-isolated-candidates-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ISOLATED_CANDIDATES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": records["identity_audit"]["scope"],
        "candidate_ledger": {
            "starting_canonical_rows": 198,
            "positive_admissible_rows": len(rows),
            "distinct_positive_rho_values": len({row["rho"] for row in rows}),
            "rows": rows,
        },
        "exact_sign_method": {
            "rho": "SymPy exact algebraic positivity; every retained rho has is_positive=True",
            "unsquared_test": "the sign of 2*n_1*n_2*rho+C-A-B fixes temporal SUM versus DIFFERENCE and removes squared spurious roots",
            "floating_point_decisions": False,
        },
        "reduced_source_workload": {
            "generic_circumference": "all cross-|n| nonzero-frequency blocks are off shell",
            "exceptional_circumferences": "exactly the 21 listed distinct rho values can carry a cross-|n| resonant functional",
            "next_computation": "for each listed row, impose parity/angular selection and compute the reduced adjoint source coefficient; zero rows are removable and nonzero rows enter R_j^bounded",
        },
        "classification": {
            "all_198_identity_audit_rows_filtered": True,
            "all_positive_candidates_decided_exactly": True,
            "unsquared_temporal_sign_test_complete": True,
            "twenty_one_distinct_admissible_candidates": True,
            "floating_point_sign_decision_used": False,
            "projected_source_coefficients_computed": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first two-|k| cross-fibre source problem is now a finite list of 21 exact circumference/branch/output rows. Generic circumference has no cross-fibre resonance, while each listed row still requires its own projected Weyl-Maxwell source coefficient.",
        "next_gate": "apply parity selection to the 21 rows, quotient symmetry-related source tensors, and compute the remaining adjoint pairings",
        "claim_boundary": "This is an exact isolated-candidate ledger, not a source theorem. It does not classify same-fibre rows, projected coefficients, bounded extension, the full two-fibre cone, infinite momentum support, causal, residual, all-orders or quantum claims.",
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
        raise AssertionError("stale ell2 two-absolute-momentum candidate ledger")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ISOLATED_CANDIDATES: PASS")


if __name__ == "__main__":
    main()
