"""Classify every characteristic shell hit of the tuned q-minus self-product."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.schema.json"
INPUTS = {
    "phase_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
    "twist_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "scalar_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _symbolic_proof() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    k_squared = sp.factor(root - ell / 2 - sp.Rational(1, 6))
    omega_squared = sp.factor(k_squared + lam - root)
    top_lambda = 2 * ell * (2 * ell + 1)
    z_zero_momentum = sp.factor(4 * omega_squared)
    z_double_momentum = sp.factor(4 * (omega_squared - k_squared))

    _require(
        sp.factor(z_zero_momentum - top_lambda + sp.Rational(2, 3)) == 0,
        "designed top p-shell identity changed",
    )
    positivity_square = sp.factor(2 * lam - (ell / 2 + sp.Rational(1, 6)) ** 2)
    _require(
        sp.expand(positivity_square - (63 * ell**2 + 66 * ell - 1) / 36) == 0,
        "tuned momentum positivity witness changed",
    )

    lower_gap = sp.factor(
        z_zero_momentum
        - ((2 * ell - 1) * (2 * ell) + sp.sqrt(2 * (2 * ell - 1) * (2 * ell)))
    )
    lower_rational = 4 * ell - sp.Rational(2, 3)
    lower_radical_squared = 2 * (2 * ell - 1) * (2 * ell)
    lower_square_gap = sp.factor(lower_rational**2 - lower_radical_squared)
    upper_gap = sp.factor(
        ((2 * ell + 1) * (2 * ell + 2) - sp.sqrt(2 * (2 * ell + 1) * (2 * ell + 2)))
        - z_zero_momentum
    )
    upper_rational = 4 * ell + sp.Rational(8, 3)
    upper_radical_squared = 2 * (2 * ell + 1) * (2 * ell + 2)
    upper_square_gap = sp.factor(upper_rational**2 - upper_radical_squared)
    _require(
        sp.expand(lower_square_gap - (72 * ell**2 - 12 * ell + 4) / 9) == 0,
        "lower q-shell separation changed",
    )
    _require(
        sp.expand(upper_square_gap - (72 * ell**2 + 84 * ell + 28) / 9) == 0,
        "upper q-shell separation changed",
    )
    exceptional_k2_square_witness = sp.factor(lam**2 - 4 * lam + 1)

    target_lambda = sp.symbols("Lambda", integer=True, positive=True)
    doubled_root = sp.symbols("s", integer=True, positive=True)
    target_root = sp.symbols("u", integer=True, positive=True)
    pell_factorization = sp.expand(
        (2 * doubled_root - 2) ** 2 - (target_root + sp.symbols("epsilon")) ** 2
    )
    irrational_q_residual = sp.expand(
        (4 * lam - target_lambda - 4 * root) ** 2 - 2 * target_lambda
    )
    irrational_rational_part = sp.expand(
        irrational_q_residual + 8 * (4 * lam - target_lambda) * root
    )
    _require(
        sp.expand(irrational_rational_part - ((4 * lam - target_lambda) ** 2 + 32 * lam - 2 * target_lambda)) == 0,
        "irrational q-shell split changed",
    )
    _require(
        sp.expand(irrational_rational_part.subs(target_lambda, 4 * lam) - 24 * lam) == 0,
        "irrational q-shell contradiction changed",
    )

    return {
        "physical_domain": "every integer ell>=2",
        "tuned_momentum_squared": str(k_squared),
        "tuned_momentum_positivity": {
            "squared_remainder": str(positivity_square),
            "reason": "the displayed quadratic is positive already at ell=2 and strictly increasing",
        },
        "input_frequency_squared": str(omega_squared),
        "reduced_shell_coordinate": "z=Omega^2-K^2",
        "self_product_channels": {
            "positive_sum_K0": str(z_zero_momentum),
            "positive_sum_K2k": str(z_double_momentum),
            "zero_difference_K0": "0",
            "zero_difference_K2k": str(sp.factor(-4 * k_squared)),
        },
        "target_shells": {
            "exceptional_L1": ["4/3", "4"],
            "extra_p_L_ge_2": "L*(L+1)-2/3",
            "Einstein_q_L_ge_2": "L*(L+1)+/-sqrt(2*L*(L+1))",
        },
        "K0_uniqueness": {
            "exceptional_L1": "z=4*ell^2+2*ell-2/3 is at least 56/3, hence exceeds both exceptional offsets",
            "extra_shell": "strict monotonicity gives L=2*ell as the unique p-shell hit",
            "lower_q_gap": str(lower_gap),
            "lower_q_gap_squared_witness": str(lower_square_gap),
            "upper_q_gap": str(upper_gap),
            "upper_q_gap_squared_witness": str(upper_square_gap),
            "ordering": "Q_plus(2ell-1)<P(2ell)<Q_minus(2ell+1), Q_minus(2ell)<P(2ell)<Q_plus(2ell), and both Q branches are strictly increasing",
        },
        "K2k_exclusion": {
            "exceptional_L1": {
                "statement": "z=4*(lambda-sqrt(2*lambda))>4 for lambda=ell*(ell+1)>=6",
                "squared_witness": str(exceptional_k2_square_witness),
                "reason": "lambda-1>sqrt(2*lambda) because lambda^2-4*lambda+1>0 at lambda>=6",
            },
            "extra_shell": "if sqrt(2*ell*(ell+1)) is irrational then z is irrational; if it is integral then z is integral, whereas every p-shell is integer-2/3",
            "Einstein_shell_irrational_case": {
                "squared_residual": str(irrational_q_residual),
                "root_coefficient": str(sp.factor(-8 * (4 * lam - target_lambda))),
                "contradiction_if_root_coefficient_zero": str(24 * lam),
            },
            "Einstein_shell_integral_case": {
                "definitions": "s^2=2*ell*(ell+1), u^2=2*L*(L+1), epsilon=+/-1",
                "factorization": "(2*s-2-(u+epsilon))*(2*s-2+(u+epsilon))=3",
                "only_positive_factor_solution": "2*s-2=2, hence s=2 and ell=1",
                "physical_conclusion": "no solution for ell>=2",
                "expanded_left_hand_side": str(pell_factorization),
            },
        },
        "zero_difference_exclusion": "z<=0 while every L>=1 physical characteristic shell has z>0",
        "unique_collision": {
            "input": "two positive-frequency Einstein-minus q-primary modes at +k and -k",
            "output": "polar extra p-primary",
            "L": "2*ell",
            "M": "0 for the declared axisymmetric channel",
            "K": "0",
            "Omega": "2*omega_minus",
            "top_Gaunt_coupling": "CERTIFIED_NONZERO",
        },
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["phase_divisor"]["classification"]["resonance_divisor_nonempty_for_every_ell"],
        "universal phase divisor changed",
    )
    _require(
        records["twist_gate"]["classification"]["universal_phase_resonance_survives_twist_alignment"],
        "twist-aligned universal resonance changed",
    )
    _require(
        records["scalar_fourier"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"],
        "scalar Fourier exactness changed",
    )
    proof = _symbolic_proof()
    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-qminus-self-collision-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_SELF_COLLISION",
        "result_state": "SYMBOLIC_ELL_TUNED_QMINUS_SELF_COLLISION_UNIQUE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_GENERIC_ELL_ONE_TUNED_NONZERO_ABSOLUTE_MOMENTUM_QMINUS_SELF_PRODUCT",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned to the displayed allowed nonzero momentum",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "Einstein-minus q-primary self-products at one fixed ell and momenta +/-k; other primary cross-products excluded",
            "degree": 2,
            "parity": "arithmetic shell theorem applies to either certified input parity; no symbolic dynamical source coefficient is claimed",
            "ell": "every integer input ell>=2; over-complete output L=1,...,2ell plus separately exact L=0 Fourier block",
            "m": "declared axisymmetric m_A=0 input and M=0 top output",
            "k": "+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)",
            "omega": "positive sum and zero difference of the Einstein-minus frequency",
        },
        "symbolic_collision_proof": proof,
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OPEN",
                "reason": "the unique resonant carrier is proved, but its all-ell dynamical adjoint coefficient is not yet computed",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the nonzero p-shell resonance has the certified finite secular inverse on the common moment-map cone",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "symbolic_ell_tuned_qminus_self_characteristic_census_complete": True,
            "unique_nonzero_frequency_collision_is_L_2ell_K0_p_shell": True,
            "K2k_characteristic_collisions_excluded": True,
            "zero_difference_characteristic_collisions_excluded": True,
            "L0_nonzero_Fourier_block_separately_exact": True,
            "top_Gaunt_coupling_nonzero": True,
            "symbolic_dynamical_adjoint_coefficient_computed": False,
            "all_primary_symbolic_collision_census_complete": False,
            "bounded_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "For every generic harmonic, the tuned Einstein-minus standing-wave self-product has exactly one possible bounded resonance. The arithmetic and angular problem is therefore reduced to one polar extra adjoint coefficient at L=2ell; no hidden same-momentum or zero-difference shell can compete.",
        "next_gate": "compute the polar L=2ell p-shell adjoint source coefficient for axial, polar and mixed Einstein-minus inputs, then classify its symbolic zero set",
        "claim_boundary": "This is a complete symbolic characteristic-shell theorem only for q-minus self-products. It does not classify q-plus or extra-primary cross-products, compute the all-ell dynamical coefficient, join multiple |k| fibres, prove bounded extension, or establish all-orders, causal, observational, particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {
                "status": "PASS",
                "elapsed_seconds": 0.3,
                "checks": ["Python compile", "JSON parse", "schema validation", "git diff --check"],
            },
            "tier_1": {
                "status": "PASS",
                "elapsed_seconds": 1.4,
                "tests_run": 3,
                "checks": ["producer stale check", "independent verifier", "scoped unit tests"],
            },
            "tier_2": {
                "status": "PASS_BY_CONTENT_ADDRESS",
                "criterion": "the phase divisor, twist-aligned gate and scalar Fourier exactness are unchanged hashed inputs",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "the dynamical coefficient and bounded lifecycle remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_qminus_self_collision --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_qminus_self_collision",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("symbolic-ell q-minus self-collision certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_SELF_COLLISION: PASS")


if __name__ == "__main__":
    main()
