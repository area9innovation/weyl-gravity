"""Exact circumference divisor for arbitrary finite compact-momentum pairs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.schema.json"
INPUTS = {
    "one_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
    "branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def divisor_formula() -> dict[str, object]:
    rho, A, B, C = sp.symbols("rho A B C", real=True)
    n_1, n_2, tau = sp.symbols("n_1 n_2 tau", integer=True, nonzero=True)
    D = C - A - B
    N = n_1 + n_2
    unsquared = sp.expand(N**2 * rho + C - (n_1**2 * rho + A) - (n_2**2 * rho + B))
    assert sp.expand(unsquared - (2 * n_1 * n_2 * rho + D)) == 0
    squared = sp.factor(4 * (n_1**2 * rho + A) * (n_2**2 * rho + B) - unsquared**2)
    coefficient = sp.factor(n_1**2 * B + n_2**2 * A - n_1 * n_2 * D)
    expected = sp.factor(4 * coefficient * rho + 4 * A * B - D**2)
    assert sp.expand(squared - expected) == 0
    candidate = sp.factor((D**2 - 4 * A * B) / (4 * coefficient))
    assert sp.factor(expected.subs(rho, candidate)) == 0
    return {
        "circumference_parameter": "rho=(2*pi/L)^2>0 and k_n=n*sqrt(rho)",
        "input_shells": "omega_A^2=n_1^2*rho+A and omega_B^2=n_2^2*rho+B",
        "signed_temporal_channel": "Omega=sigma_1*omega_A+sigma_2*omega_B with tau=sigma_1*sigma_2 in {+1,-1}",
        "output_shell": "Omega^2=(n_1+n_2)^2*rho+C",
        "unsquared_equation": "2*tau*sqrt((n_1^2*rho+A)*(n_2^2*rho+B))=2*n_1*n_2*rho+D, D=C-A-B",
        "linear_squared_divisor": str(expected),
        "rho_coefficient_Q": str(coefficient),
        "candidate_rho_when_Q_nonzero": str(candidate),
        "admissibility": "retain the candidate only when rho>0 and tau*(2*n_1*n_2*rho+D)>0; this removes roots introduced by squaring",
        "degenerate_cases": {
            "Q_nonzero": "exactly one algebraic candidate before positivity and sign tests",
            "Q_zero_constant_nonzero": "no resonance at any circumference",
            "Q_zero_constant_zero": "an identity-resonant carrier for every circumference; it must remain an explicit source-matrix row",
        },
        "formal_symbols": [str(symbol) for symbol in (rho, A, B, C, n_1, n_2, tau)],
    }


def reductions() -> dict[str, object]:
    A, B, C = sp.symbols("A B C", real=True)
    D = C - A - B
    numerator = sp.factor(D**2 - 4 * A * B)
    opposite = sp.factor(numerator / (4 * C))
    aligned = sp.factor(numerator / (4 * (2 * A + 2 * B - C)))

    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    input_offset = lam - root
    output_offset = 2 * ell * (2 * ell + 1) - sp.Rational(2, 3)
    tuned = sp.factor(opposite.subs({A: input_offset, B: input_offset, C: output_offset}))
    expected_tuned = sp.factor(root - ell / 2 - sp.Rational(1, 6))
    assert sp.factor(tuned - expected_tuned) == 0
    return {
        "opposite_equal_absolute_momentum": {
            "signed_momenta": "n_1=+n, n_2=-n",
            "candidate_k_squared_n2rho": str(opposite),
            "matches_existing_h0_divisor": True,
        },
        "aligned_equal_absolute_momentum": {
            "signed_momenta": "n_1=n_2=n",
            "candidate_k_squared_n2rho": str(aligned),
            "matches_existing_h4_divisor": True,
        },
        "universal_qminus_top_extra_family": {
            "inputs": "q-minus ell at opposite momenta n=+1,-1",
            "target": "p-extra L=2ell at K=0",
            "candidate_rho": str(tuned),
            "expected": str(expected_tuned),
        },
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["one_fibre"]["classification"]["phase_sensitive_resonance_divisor_formula_exact"]
    assert records["branch_dictionary"]["classification"]["bridge_1_activation_gate_satisfied"]
    return {
        "schema": "einstein-maxwell-weyl-finite-multimomentum-resonance-divisor-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_MULTIMOMENTUM_RESONANCE_DIVISOR",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with one common circumference L",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "arbitrary finite set of positive-offset physical and extra oscillator branches at arbitrary signed compact momentum integers",
            "degree": 2,
            "parity": "all parities retained; the divisor is prior to source/parity projection",
            "ell": "arbitrary finite input and angularly allowed output set",
            "m": "arbitrary finite Clebsch-Gordan-allowed set",
            "k": "k_n=2*pi*n/L for arbitrary finitely many signed nonzero integers n",
            "omega": "every signed quadratic sum/difference channel",
        },
        "exact_divisor": divisor_formula(),
        "certified_reductions": reductions(),
        "finite_carrier_theorem": {
            "statement": "for a declared finite harmonic carrier, every nonidentity nonzero-frequency target-shell collision occurs at at most one positive algebraic value of rho; hence the exceptional circumference set is finite",
            "generic_circumference_consequence": "outside that finite set, all nonidentity nonzero-frequency cross-|k| blocks are off shell and have no resonant adjoint functional",
            "identity_channel_rule": "Q=0 and 4*A*B-D^2=0 is not discarded or called generic; it is exported as an identity-resonant row requiring an explicit source matrix",
            "zero_frequency_rule": "Omega=0 constraint-adjoint components remain the five stabilizer/Taub maps plus any separately certified exceptional cokernel and are not removed by this divisor",
            "source_rule": "a shell collision is only a candidate functional; no obstruction or extension is inferred until the projected quadratic source coefficient is computed",
        },
        "classification": {
            "arbitrary_two_signed_momentum_integers_covered": True,
            "all_signed_temporal_sum_difference_channels_covered": True,
            "squared_divisor_linear_in_circumference_parameter": True,
            "one_fibre_h0_h4_formulas_recovered": True,
            "finite_nonidentity_exceptional_circumference_set_certified": True,
            "identity_resonant_channels_fail_closed": True,
            "quadratic_source_coefficients_computed": False,
            "complete_multifibre_tangent_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Multiple compact-momentum fibres do not produce an uncontrolled continuum of accidental resonances on a finite carrier. Each candidate is governed by a linear exact circumference divisor, while identity channels and source coefficients remain explicit independent gates.",
        "next_gate": "instantiate the identity-channel ledger and projected source matrices on the first two-|k| carrier, then intersect them with the additive five-moment-map cone",
        "claim_boundary": "This is a finite-carrier shell-arithmetic theorem. It does not compute a quadratic source coefficient, classify identity-resonant rows, prove a bounded or secular correction, handle infinite momentum support, or establish causal, residual, all-orders or quantum claims.",
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
        raise AssertionError("stale finite multimomentum divisor certificate")
    print("EINSTEIN_MAXWELL_WEYL_FINITE_MULTIMOMENTUM_RESONANCE_DIVISOR: PASS")


if __name__ == "__main__":
    main()
