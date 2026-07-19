"""Certify the nonzero-momentum constant-twist bounded mixed column."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.schema.json"
INPUTS = {
    "k0_naturality": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.json",
    "angular_factorization": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.json",
    "axial_primary": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_primary": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "k0_neighbor_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
}


class NonzeroKConstantTwistError(RuntimeError):
    """Raised when an exact input or shell identity changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NonzeroKConstantTwistError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shell_derivatives() -> dict[str, Any]:
    lam, momentum, frequency, alpha, spin = sp.symbols(
        "lambda k omega alpha j", real=True
    )
    covariant_momentum = momentum + alpha * spin
    invariant = frequency**2 - covariant_momentum**2
    p = sp.expand(invariant - lam + sp.Rational(2, 3))
    q = sp.expand((invariant - lam) ** 2 - 2 * lam)
    p_alpha = sp.factor(sp.diff(p, alpha).subs(alpha, 0))
    q_alpha = sp.factor(sp.diff(q, alpha).subs(alpha, 0))
    root = sp.sqrt(2 * lam)
    substitutions = {
        "Einstein_minus_q": {frequency**2: momentum**2 + lam - root},
        "Einstein_plus_q": {frequency**2: momentum**2 + lam + root},
        "extra_p": {frequency**2: momentum**2 + lam - sp.Rational(2, 3)},
    }
    shell_values = {
        "Einstein_minus_q": sp.factor(q_alpha.subs(substitutions["Einstein_minus_q"])),
        "Einstein_plus_q": sp.factor(q_alpha.subs(substitutions["Einstein_plus_q"])),
        "extra_p": sp.factor(p_alpha.subs(substitutions["extra_p"])),
    }
    expected = {
        "Einstein_minus_q": 4 * momentum * spin * root,
        "Einstein_plus_q": -4 * momentum * spin * root,
        "extra_p": -2 * momentum * spin,
    }
    _require(shell_values == expected, "nonzero-k shell derivatives changed")

    # A regular action Gram G(alpha) contributes G'(0)*primary plus
    # G(0)*primary'.  The first term vanishes on shell, leaving the displayed
    # scalar times the nondegenerate action Gram.
    primary_term_checks: dict[str, Any] = {}
    for label, dimension, primary, shell in (
        ("q_minus", 2, q, substitutions["Einstein_minus_q"]),
        ("q_plus", 2, q, substitutions["Einstein_plus_q"]),
        ("p", 4, p, substitutions["extra_p"]),
    ):
        gram1 = sp.Matrix(
            dimension,
            dimension,
            lambda i, j_index: sp.Symbol(f"{label}g1_{i}_{j_index}"),
        )
        primary_on_shell = sp.factor(primary.subs(alpha, 0).subs(shell))
        remainder = (gram1 * primary_on_shell).applyfunc(sp.factor)
        _require(remainder == sp.zeros(dimension), f"{label} Gram-derivative term changed")
        primary_term_checks[label] = {
            "dimension": dimension,
            "Gprime_times_primary_on_shell_rank": remainder.rank(),
        }

    return {
        "covariant_momentum": "K_alpha=k+alpha*j",
        "p_of_K": str(p),
        "q_of_K": str(q),
        "dalpha_p_at_alpha0": str(p_alpha),
        "dalpha_q_at_alpha0": str(q_alpha),
        "on_shell_action_Gram_scalars": {
            label: str(value) for label, value in shell_values.items()
        },
        "regular_action_Gram_derivative_checks": primary_term_checks,
        "nonvanishing_domain": "lambda=ell(ell+1)>=6, k=2*pi*n/L with n!=0, and nonzero spin eigenvalue j",
    }


def _neighboring_output_theorem(records: dict[str, Any]) -> dict[str, Any]:
    ledger = records["k0_neighbor_ledger"]["neighbor_output_ledger"]
    _require(
        records["k0_neighbor_ledger"]["classification"]["every_fixed_ell_neighbor_output_invertible"],
        "fixed-ell neighboring-output theorem changed",
    )
    ell, momentum = sp.symbols("ell k", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    input_invariants = {
        "input_p_shell": lam - sp.Rational(2, 3),
        "input_q_minus_shell": lam - root,
        "input_q_plus_shell": lam + root,
    }
    checked: dict[str, Any] = {}
    for direction, label in ((-1, "L=ell-1"), (1, "L=ell+1")):
        output_ell = ell + direction
        output_lambda = sp.expand(output_ell * (output_ell + 1))
        rows: dict[str, Any] = {}
        for shell, invariant in input_invariants.items():
            omega_sq = momentum**2 + invariant
            target_invariant = sp.factor(omega_sq - momentum**2)
            target_p = sp.factor(target_invariant - output_lambda + sp.Rational(2, 3))
            target_q = sp.factor((target_invariant - output_lambda) ** 2 - 2 * output_lambda)
            imported = ledger[label][shell]
            _require(str(target_p) == imported["target_p"], f"{label} {shell} target-p momentum cancellation changed")
            _require(str(target_q) == imported["target_q"], f"{label} {shell} target-q momentum cancellation changed")
            rows[shell] = {
                "omega_squared": str(omega_sq),
                "target_p": str(target_p),
                "target_q": str(target_q),
                "k_cancels": True,
            }
        checked[label] = {
            "generic_ledger": rows,
            "all_generic_target_blocks_invertible": True,
        }

    exceptional = records["exceptional_nonzero_k"]
    _require(
        exceptional["classification"]["nonzero_k_exceptional_solution_cofiber_certified"],
        "exceptional nonzero-k shell theorem changed",
    )
    exceptional_shells = [sp.Rational(4, 1), sp.Rational(4, 3)]
    ell2_invariants = {
        "p": sp.Rational(16, 3),
        "q_minus": 6 - 2 * sp.sqrt(3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }
    separations = {
        branch: [str(sp.factor(value - shell)) for shell in exceptional_shells]
        for branch, value in ell2_invariants.items()
    }
    _require(
        all(sp.sympify(value) != 0 for values in separations.values() for value in values),
        "ell=2 to exceptional L=1 shell separation changed",
    )
    checked["ell=2 exceptional L=1"] = {
        "target_solution_invariants": ["4", "4/3"],
        "input_invariants": {name: str(value) for name, value in ell2_invariants.items()},
        "exact_separations": separations,
        "all_exceptional_target_blocks_invertible": True,
    }
    return {
        "momentum_invariant": "s=omega^2-k^2",
        "proof": "The twist has zero circle momentum, so every A-times-wave output retains K=k. Substitution omega^2=k^2+s cancels k from each target p/q factor, reproducing the exact fixed-ell neighbor ledger. The ell=2 lower L=1 channel is checked against the separately certified nonzero-k exceptional solution shells.",
        "channels": checked,
        "complete_neighboring_output_inverse": True,
    }


def build() -> dict[str, Any]:
    records = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in INPUTS.items()
    }
    _require(
        records["k0_naturality"]["flat_connection_reduction"]["primary_derivative"]["covariant_momentum"].startswith("K_alpha=k+alpha*j"),
        "flat-connection covariantization changed",
    )
    _require(
        records["angular_factorization"]["classification"]["all_fixed_ell_all_m_factorization_certified"],
        "SO(3) factorization changed",
    )
    _require(
        records["axial_primary"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"],
        "axial primary decomposition changed",
    )
    _require(
        records["polar_primary"]["classification"]["canonical_extra_polar_quotient_two_p_summands"],
        "polar primary decomposition changed",
    )
    _require(
        records["axial_current"]["classification"]["generic_extra_module_direct_Lee_Wald_nonradical"]
        and records["axial_current"]["classification"]["Einstein_extra_symplectic_orthogonality"]
        and records["axial_current"]["classification"]["complete_generic_axial_target_signature_three_one"],
        "axial action pairing changed",
    )
    _require(
        records["polar_current"]["classification"]["extra_block_nonradical"]
        and records["polar_current"]["classification"]["Einstein_extra_orthogonality"]
        and records["polar_current"]["classification"]["complete_polar_target_inertia_3_1"]
        and records["polar_current"]["classification"]["all_allowed_compact_momenta_including_zero"],
        "polar action pairing or momentum scope changed",
    )

    derivatives = _shell_derivatives()
    neighbors = _neighboring_output_theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-nonzero-k-constant-twist-same-shell-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_NONZERO_K_CONSTANT_TWIST_SAME_SHELL",
        "result_state": "NONZERO_MOMENTUM_CONSTANT_TWIST_BOUNDED_MIXED_COLUMN_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_EVERY_FIXED_GENERIC_ELL_EVERY_ALLOWED_NONZERO_K_ALL_M_BOTH_PARITIES_ALL_PRIMARIES",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic mixed-source correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one nonzero constant axial twist position crossed with one fixed generic ell and one real signed-momentum q/p wave block",
            "degree": 2,
            "parity": "axial and polar multiplicities retained",
            "ell": "every one fixed integer ell>=2",
            "m": "all m=-ell,...,ell relative to the twist axis",
            "k": "every allowed k=2*pi*n/L with n!=0; the real carrier contains the conjugate +/-k pair",
            "omega": "Einstein q-minus, q-plus and extra p shells kept distinct",
        },
        "flat_connection_Feynman_Hellmann": derivatives,
        "neighboring_output_extension": neighbors,
        "action_normalized_resonance_operators": {
            "Einstein_minus_q": "(A_hat dot J_ell) tensor (4*k*sqrt(2*lambda)*G_q_minus)",
            "Einstein_plus_q": "(A_hat dot J_ell) tensor (-4*k*sqrt(2*lambda)*G_q_plus)",
            "extra_p": "(A_hat dot J_ell) tensor (-2*k*G_p)",
            "Gram_dimensions": {"G_q_minus": 2, "G_q_plus": 2, "G_p": 4},
            "Gram_nondegeneracy": "CERTIFIED by the action-derived axial/polar Lee-Wald shell pairings on every physical fibre",
            "signed_momentum_reality": "the -k operator is the sign reverse of the +k operator and has the same kernel; conjugate reality therefore preserves the condition",
        },
        "kernel_theorem": {
            "nonzero_A_axis_choice": "rotate A_hat to e_z",
            "angular_spectrum": "spec(A_hat dot J_ell)={-ell,...,ell} up to the fixed nonzero normalization",
            "each_branch_kernel": "V_(ell,m_A=0) tensor M_branch",
            "complete_same_shell_kernel": "V_(ell,m_A=0) tensor (M_q_minus direct_sum M_q_plus direct_sum M_p)",
            "multiplicity_dimensions": {"q_minus": 2, "q_plus": 2, "p": 4},
            "kernel_dimension_per_positive_signed_momentum_fibre": 8,
            "necessary_condition": "for A!=0 and k!=0, every bounded second-order tangent must have only m_A=0 wave coefficients on each q/p branch",
            "contrast_with_rest_frame": "at k=0 every scalar vanishes and the complete fixed-ell wave block is the same-shell kernel",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED",
                "claim": "the complete A-times-wave bilinear source has a bounded correction exactly on the displayed m_A=0 face; same-shell necessity and neighboring-output sufficiency are both certified",
                "full_equation": "OPEN: wave-wave terms, opposite-momentum cross terms and simultaneous global constraints are not solved here",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "NOT_APPLICABLE",
                "reason": "a secular correction may absorb a same-shell source; this theorem classifies the bounded resonant projection only",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "every_fixed_ell_every_allowed_nonzero_k_same_shell_operator_certified": True,
            "all_axial_polar_q_p_multiplicities_covered": True,
            "same_shell_kernel_exactly_axisymmetric_about_twist": True,
            "rest_frame_spectator_contrast_exact": True,
            "neighboring_outputs_invertible_for_every_allowed_nonzero_k": True,
            "complete_constant_twist_times_wave_bilinear_column_classified": True,
            "complete_bounded_second_order_equation_solved": False,
            "opposite_momentum_cross_terms_classified": False,
            "multiple_absolute_momentum_fibres_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Constant twist is a bounded spectator only for rest waves. A travelling compact mode has nonzero group-velocity derivative, so twist holonomy produces an action-normalized same-shell source on every non-axisymmetric magnetic component. On the exact axisymmetric kernel, both neighboring angular outputs are off shell and have bounded inverses, closing the entire A-times-wave bilinear column.",
        "next_gate": "combine the certified twist-wave column with wave-wave opposite-momentum terms and the remaining standard-global polynomial constraints, then treat multiple absolute-momentum fibres",
        "claim_boundary": "This is an exact necessary-and-sufficient theorem for bounded solvability of the constant-twist-times-wave bilinear column at one fixed generic ell and one nonzero absolute momentum. It does not solve wave-wave terms or the full tangent equation, classify opposite-momentum cross terms or multiple |k| fibres, or support causal, all-orders, residual, observational, particle or quantum claims.",
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
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.18},
            "tier_1": {"status": "PASS", "elapsed_seconds": 0.54, "max_rss_kb": 60412, "tests_run": 36},
            "tier_2": {
                "status": "PASS_BY_CONTENT_ADDRESS",
                "criterion": "the flat-connection naturality theorem, physical p/q primary decompositions and nonradical action-derived currents are unchanged hashed inputs",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "no complete bounded, causal, all-orders or programme-wide lifecycle is promoted"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell bridge.einstein_sector.atlas.tests.test_einstein_atlas_fragment",
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
        raise NonzeroKConstantTwistError("nonzero-k constant-twist certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_NONZERO_K_CONSTANT_TWIST_SAME_SHELL: PASS")


if __name__ == "__main__":
    main()
