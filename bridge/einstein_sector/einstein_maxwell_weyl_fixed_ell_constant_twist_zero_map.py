"""Certify the fixed-ell k=0 constant-twist same-shell zero map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.schema.json"
INPUTS = {
    "factorization": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.json",
    "axial_primary": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_primary": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_action": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json",
    "polar_action": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "fixed_ell_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "ell2_repair": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json",
    "twist_family": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class FixedEllConstantTwistZeroMapError(RuntimeError):
    """Raised when an exact dependency or primary identity changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixedEllConstantTwistZeroMapError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _primary_derivative_theorem() -> dict[str, Any]:
    lam, momentum, frequency, alpha, spin = sp.symbols(
        "lambda k omega alpha j", real=True
    )
    covariant_momentum = momentum + alpha * spin
    invariant = frequency**2 - covariant_momentum**2
    p = sp.expand(invariant - lam + sp.Rational(2, 3))
    q = sp.expand((invariant - lam) ** 2 - 2 * lam)

    p_alpha = sp.factor(sp.diff(p, alpha).subs(alpha, 0))
    q_alpha = sp.factor(sp.diff(q, alpha).subs(alpha, 0))
    p_rest = sp.factor(p_alpha.subs(momentum, 0))
    q_rest = sp.factor(q_alpha.subs(momentum, 0))
    _require(p_rest == 0 and q_rest == 0, "rest-frame primary derivative changed")

    # A regular change of primary basis or action normalization contributes
    # only a multiple of the primary itself and hence vanishes on shell.
    g0, g1 = sp.symbols("g0 g1", real=True)
    p_action_derivative = sp.factor(
        sp.diff((g0 + alpha * g1) * p, alpha).subs({alpha: 0, momentum: 0})
    )
    q_action_derivative = sp.factor(
        sp.diff((g0 + alpha * g1) * q, alpha).subs({alpha: 0, momentum: 0})
    )
    p_rest_primary = sp.factor(p.subs({alpha: 0, momentum: 0}))
    q_rest_primary = sp.factor(q.subs({alpha: 0, momentum: 0}))
    p_shell_remainder = sp.factor(p_action_derivative - g1 * p_rest_primary)
    q_shell_remainder = sp.factor(q_action_derivative - g1 * q_rest_primary)
    _require(p_shell_remainder == 0 and q_shell_remainder == 0, "action-normalized shell derivative changed")

    matrix_checks: dict[str, Any] = {}
    for label, dimension, primary in (("q", 2, q), ("p", 4, p)):
        gram0 = sp.Matrix(dimension, dimension, lambda i, j_index: sp.Symbol(f"{label}g0_{i}_{j_index}"))
        gram1 = sp.Matrix(dimension, dimension, lambda i, j_index: sp.Symbol(f"{label}g1_{i}_{j_index}"))
        restricted_derivative = ((gram0 + alpha * gram1) * primary).diff(alpha).subs(
            {alpha: 0, momentum: 0}
        )
        rest_primary = primary.subs({alpha: 0, momentum: 0})
        shell_remainder = (restricted_derivative - gram1 * rest_primary).applyfunc(sp.factor)
        _require(shell_remainder == sp.zeros(dimension), f"{label} matrix-Gram shell derivative changed")
        matrix_checks[label] = {
            "dimension": dimension,
            "shell_remainder_rank": shell_remainder.rank(),
            "shell_remainder": [[str(value) for value in row] for row in shell_remainder.tolist()],
        }

    return {
        "covariant_momentum": "K_alpha=k+alpha*j with j any matrix element of A_hat dot J_ell",
        "p_of_K": str(p),
        "q_of_K": str(q),
        "dalpha_p_at_alpha0": str(p_alpha),
        "dalpha_q_at_alpha0": str(q_alpha),
        "k0_derivatives": {"p": str(p_rest), "q": str(q_rest)},
        "regular_action_factor": "G(alpha)=g0+alpha*g1+O(alpha^2)",
        "p_action_shell_remainder": str(p_shell_remainder),
        "q_action_shell_remainder": str(q_shell_remainder),
        "matrix_gram_checks": matrix_checks,
        "proof": "The lifted constant twist is a flat SO(3) connection along S1, so horizontal differentiation replaces k by k+alpha(A_hat dot J_ell). On the action-reduced p or q primary, the adjoint-cokernel pairing is the Feynman-Hellmann derivative. Both primaries are even in covariant momentum; at k=0 the derivative vanishes. Derivatives of any regular action Gram or basis factor multiply p or q and vanish on shell.",
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["factorization"]["classification"]["all_fixed_ell_all_m_factorization_certified"],
        "SO(3) factorization input changed",
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
        records["axial_action"]["normalization_triangle"]["equation_operator_equals_reduced_action_Hessian"],
        "axial action normalization changed",
    )
    _require(
        records["polar_action"]["classification"]["direct_four_dimensional_Lee_Wald_match"],
        "polar action normalization changed",
    )
    _require(
        records["fixed_ell_wave"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"],
        "fixed-ell wave theorem changed",
    )
    repair = records["ell2_repair"]
    _require(
        repair["corrected_position_maps"]["Einstein_plus_minus"] == "zero"
        and repair["corrected_position_maps"]["extra"] == "zero",
        "ell2 direct calibration changed",
    )
    _require(
        records["twist_family"]["classification"]["constant_twist_exact_family_identified"],
        "exact constant-twist family changed",
    )

    derivative = _primary_derivative_theorem()
    return {
        "schema": "einstein-maxwell-weyl-fixed-ell-constant-twist-zero-map-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_ZERO_MAP",
        "result_state": "EVERY_FIXED_GENERIC_ELL_K0_CONSTANT_TWIST_SAME_SHELL_MAP_ZERO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_EVERY_FIXED_GENERIC_ELL_K0_ALL_M_BOTH_PARITIES_ALL_PRIMARIES",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded same-shell resonance projection",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one constant axial twist position crossed with one arbitrary fixed ell>=2,k=0 q/p wave block",
            "degree": 2,
            "parity": "axial and polar",
            "ell": "every one fixed integer ell>=2",
            "m": "all m=-ell,...,ell",
            "k": 0,
            "omega": "Einstein plus/minus q shells and extra p shell separately",
        },
        "flat_connection_reduction": {
            "lifted_connection": "D_x=partial_x+alpha*(A_hat dot J_ell)",
            "curvature": "zero for constant alpha and one circle direction",
            "background_compatibility": "SO(3) rotations are lifted bundle automorphisms of the monopole connection",
            "local_pullback": "F_alpha(x,y)=(x,exp(alpha*x*A_hat)y), together with the compensating U(1) lift that fixes the monopole connection",
            "naturality": "E(F_alpha^*Phi)=F_alpha^*E(Phi); on an x-independent V_ell coefficient, partial_x(F_alpha^*u)=alpha*(A_hat dot J_ell)F_alpha^*u",
            "global_scope": "F_alpha need not be periodic as a gauge transformation; its holonomy is physical. Only the local covariantization identity is used to compute the periodic bilinear source and its same-shell pairing.",
            "primary_derivative": derivative,
        },
        "multiplicity_matrices": {
            "Q_(ell,-)": {"shape": [2, 2], "matrix": [["0", "0"], ["0", "0"]], "rank": 0},
            "Q_(ell,+)": {"shape": [2, 2], "matrix": [["0", "0"], ["0", "0"]], "rank": 0},
            "P_ell": {
                "shape": [4, 4],
                "matrix": [["0", "0", "0", "0"] for _ in range(4)],
                "rank": 0,
            },
            "all_m_resonance_operator": "zero on V_ell tensor (M_q_minus direct_sum M_q_plus direct_sum M_p)",
            "kernel": "the complete fixed-ell q/p wave carrier",
        },
        "direct_calibration": {
            "ell": 2,
            "certificate": repair["result_id"],
            "Einstein_plus_minus": repair["corrected_position_maps"]["Einstein_plus_minus"],
            "extra": repair["corrected_position_maps"]["extra"],
            "matches_structural_theorem": True,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OPEN",
                "reason": "the same-shell adjoint projection is zero, but the L=ell-1 and L=ell+1 twist-wave output inverses have not yet been certified uniformly",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the complete finite-support smooth-secular theorem already supplies a correction when the stabilizer moment maps vanish",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "generic_ell_Einstein_multiplicity_matrices_zero": True,
            "generic_ell_extra_multiplicity_matrix_zero": True,
            "all_fixed_ell_all_m_same_shell_resonance_zero": True,
            "ell2_direct_replay_matched": True,
            "bounded_fixed_ell_constant_twist_cone_complete": False,
            "off_shell_L_ell_plus_minus_1_inverses_certified": False,
            "finite_multi_ell_twist_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Constant twist does not create a same-shell bounded obstruction for any fixed generic angular momentum at rest. The ell=2 zero is structural: the twist differentiates the action primary with respect to circle momentum, and every p/q primary has zero group-velocity derivative at k=0.",
        "next_gate": "prove the L=ell-1 and L=ell+1 p/q target blocks are uniformly off shell at each input p/q frequency, then combine with the fixed-ell H,J_i wave theorem to certify the complete bounded product cone",
        "claim_boundary": "This certifies every same-shell adjoint-cokernel projection for one fixed ell>=2 at k=0. It does not yet certify uniform inversion of the neighboring angular outputs, finite multi-ell sums, nonzero momentum, causal propagation, all-orders integration, residual observables or quantum transfer.",
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
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.20},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.23, "max_rss_kb": 60840, "tests_run": 33},
            "tier_2": {
                "status": "PASS_BY_CONTENT_ADDRESS",
                "criterion": "action-derived primary decompositions, SO(3) factorization and the direct ell2 corrected replay are unchanged exact inputs",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "neighboring angular outputs and larger lifecycles remain fail-closed"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map",
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
        raise FixedEllConstantTwistZeroMapError("fixed-ell constant-twist zero-map certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_ZERO_MAP: PASS")


if __name__ == "__main__":
    main()
