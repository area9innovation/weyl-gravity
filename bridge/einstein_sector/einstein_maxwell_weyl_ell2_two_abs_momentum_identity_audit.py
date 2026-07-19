"""Audit identity-resonant rows for the ell=2, |n|={1,2} carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.schema.json"
INPUTS = {
    "multimomentum": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json",
    "scalar_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_offsets() -> tuple[dict[str, sp.Expr], dict[tuple[int, str], sp.Expr]]:
    inputs = {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }
    targets: dict[tuple[int, str], sp.Expr] = {}
    for output_ell in range(1, 5):
        eigenvalue = output_ell * (output_ell + 1)
        if output_ell == 1:
            targets[(output_ell, "standard")] = sp.Integer(4)
            targets[(output_ell, "extra")] = sp.Rational(4, 3)
        else:
            targets[(output_ell, "q_minus")] = eigenvalue - sp.sqrt(2 * eigenvalue)
            targets[(output_ell, "p_extra")] = eigenvalue - sp.Rational(2, 3)
            targets[(output_ell, "q_plus")] = eigenvalue + sp.sqrt(2 * eigenvalue)
    return inputs, targets


def identity_rows() -> list[dict[str, object]]:
    inputs, targets = branch_offsets()
    rows: list[dict[str, object]] = []
    for relative_sign in (-1, 1):
        n_1, n_2 = 1, 2 * relative_sign
        for first_name, first_offset in inputs.items():
            for second_name, second_offset in inputs.items():
                for (output_ell, target_name), target_offset in targets.items():
                    difference = sp.expand(target_offset - first_offset - second_offset)
                    coefficient = sp.radsimp(
                        n_1**2 * second_offset
                        + n_2**2 * first_offset
                        - n_1 * n_2 * difference
                    )
                    constant = sp.radsimp(4 * first_offset * second_offset - difference**2)
                    coefficient_zero = sp.simplify(coefficient) == 0
                    constant_zero = sp.simplify(constant) == 0
                    if coefficient_zero and constant_zero:
                        raise AssertionError(
                            f"identity resonance appeared: {(relative_sign, first_name, second_name, output_ell, target_name)}"
                        )
                    rows.append(
                        {
                            "relative_spatial_sign": relative_sign,
                            "canonical_signed_momenta": [n_1, n_2],
                            "first_branch": first_name,
                            "second_branch": second_name,
                            "output_ell": output_ell,
                            "target_branch": target_name,
                            "rho_coefficient_Q": str(sp.factor(coefficient)),
                            "constant_4AB_minus_D2": str(sp.factor(constant)),
                            "Q_zero": coefficient_zero,
                            "constant_zero": constant_zero,
                            "identity_resonant": False,
                        }
                    )
    return rows


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["multimomentum"]["classification"]["identity_resonant_channels_fail_closed"]
    assert records["scalar_fourier"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"]
    rows = identity_rows()
    assert len(rows) == 198
    q_zero_count = sum(bool(row["Q_zero"]) for row in rows)
    constant_zero_count = sum(bool(row["constant_zero"]) for row in rows)
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-identity-audit-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_IDENTITY_AUDIT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with arbitrary common circumference L",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all q-minus, p-extra and q-plus ell=2 oscillators on the two absolute momentum fibres |n|=1 and |n|=2",
            "degree": 2,
            "parity": "all input/output parity combinations conservatively retained",
            "ell": "input ell=2 times ell=2; over-complete output L=1,2,3,4 with L=0 handled by the exact nonzero-Fourier scalar complex",
            "m": "all Clebsch-Gordan-allowed values",
            "k": "signed n in {+/-1,+/-2} times 2*pi/L, restricted here to cross-|n| pairs",
            "omega": "all signed temporal sum/difference channels",
        },
        "canonical_reduction": {
            "representatives": "n_1=1,n_2=+2 and n_1=1,n_2=-2",
            "completeness": "simultaneous momentum-sign reversal leaves Q and the constant invariant; ordered input branch pairs cover interchange of the |n| assignments",
            "input_branch_count": 3,
            "target_shell_count": 11,
            "relative_spatial_sign_count": 2,
            "audited_row_count": len(rows),
        },
        "identity_audit": {
            "rows": rows,
            "Q_zero_row_count": q_zero_count,
            "constant_zero_row_count": constant_zero_count,
            "identity_resonant_row_count": 0,
        },
        "consequence": {
            "all_cross_fibre_channels_nonidentity": True,
            "exceptional_circumference_set": "finite; each of the 198 canonical channels has at most one candidate rho before positivity and unsquared-sign tests",
            "generic_circumference": "outside that finite set every nonzero-frequency |n|=1 times |n|=2 source block is off shell",
            "isolated_candidates": "at exceptional circumferences the projected source coefficient remains an independent resonant-functional gate",
            "L0_output": "the output momentum is nonzero for cross-|n| pairs, and the certified polar L=0 nonzero-Fourier Diff-Weyl-U1 complex is exact",
        },
        "classification": {
            "complete_cross_abs_momentum_identity_audit": True,
            "all_three_input_primary_branches_covered": True,
            "all_physical_L1_to_L4_target_shells_covered": True,
            "no_identity_resonant_channel": True,
            "generic_circumference_cross_fibre_nonresonance_certified": True,
            "isolated_circumference_source_coefficients_computed": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first genuine two-|k| ell=2 carrier has no resonance that persists for every circumference. Cross-fibre nonlinear coupling is generically off shell, but finitely many isolated circumference candidates still require direct source matrices.",
        "next_gate": "enumerate the admissible positive isolated circumference candidates up to exact symmetry and compute their projected source matrices before intersecting with H,P_x,J_i",
        "claim_boundary": "This excludes identity resonances only for ell=2 cross pairs between |n|=1 and |n|=2. It does not classify the isolated circumference candidates, source coefficients, same-fibre rows, the full two-fibre tangent cone, infinite momentum support, causal, residual, all-orders or quantum claims.",
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
        raise AssertionError("stale ell2 two-absolute-momentum identity audit")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_IDENTITY_AUDIT: PASS")


if __name__ == "__main__":
    main()
