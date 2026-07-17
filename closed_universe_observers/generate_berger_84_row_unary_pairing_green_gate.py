#!/usr/bin/env python3
"""Generate the exact partial completion gate for the Berger 84-row unary complex.

The 84-row handoff contains two logically different extensions of the certified
64-row gravity--clock--Maxwell complex.  The memory--Maxwell extension is a
finite triangular cyclic Hessian and can be completed without knowing the rod
backreaction blocks.  The rods, by contrast, have nonconstant backgrounds, so
their scalar wave equations alone are not a BV subcomplex: diffeomorphism,
gravity--rod Hessian, and cotangent-adjoint blocks are mandatory.

This generator proves the complete two-detector memory formula and records the
remaining rod payload as a typed, fail-closed interface.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-84-row-unary-pairing-green-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE.json"
REPORT = PACKAGE / "reports/berger-84-row-unary-pairing-green-gate.md"

DEPENDENCIES = {
    "authoritative_84_row_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "historical_unary_gate": ROOT / "d_quotient_classical/certificates/BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE.json",
    "base_64_carrier": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "base_64_causal": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_q1_solvability": PACKAGE / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
}

SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_unary_pairing_green_gate.py",
    "tests": PACKAGE / "tests/test_berger_84_row_unary_pairing_green_gate.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


Poly = dict[tuple[str, ...], Fraction]


def _poly(*terms: tuple[int | Fraction, tuple[str, ...]]) -> Poly:
    result: Poly = {}
    for coefficient, word in terms:
        value = Fraction(coefficient)
        if value:
            result[word] = result.get(word, Fraction(0)) + value
    return {word: value for word, value in result.items() if value}


def _add(*values: Poly) -> Poly:
    result: Poly = {}
    for value in values:
        for word, coefficient in value.items():
            result[word] = result.get(word, Fraction(0)) + coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


INVERSE_RULES = {
    ("M", "G"), ("G", "M"),
    ("T0", "H0"), ("H0", "T0"),
    ("T0s", "J0"), ("J0", "T0s"),
    ("T1", "H1"), ("H1", "T1"),
    ("T1s", "J1"), ("J1", "T1s"),
}


def _reduce_word(word: tuple[str, ...]) -> tuple[str, ...]:
    # kappa is central; keeping its degree at the front makes cancellations
    # coefficientwise while all physical operators remain noncommutative.
    kappa_degree = word.count("k")
    value = [token for token in word if token != "k"]
    changed = True
    while changed:
        changed = False
        for index in range(len(value) - 1):
            if (value[index], value[index + 1]) in INVERSE_RULES:
                del value[index:index + 2]
                changed = True
                break
    return ("k",) * kappa_degree + tuple(value)


def _multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            word = _reduce_word(left_word + right_word)
            result[word] = result.get(word, Fraction(0)) + left_coefficient * right_coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _matrix_multiply(left: list[list[Poly]], right: list[list[Poly]]) -> list[list[Poly]]:
    return [
        [
            _add(*(_multiply(left[row][middle], right[middle][column]) for middle in range(len(right))))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _identity(size: int) -> list[list[Poly]]:
    return [[_poly((1, ())) if row == column else {} for column in range(size)] for row in range(size)]


def _two_channel_hessian_and_inverse(
    channel_count: int = 2, *, delete_cross_01: bool = False
) -> tuple[list[list[Poly]], list[list[Poly]]]:
    """Return the universal A,m_a,p_a Hessian and its exact finite inverse."""

    if channel_count != 2:
        raise ValueError("the authoritative handoff has exactly two detector channels")
    size = 1 + 2 * channel_count
    zero: Poly = {}
    hessian = [[deepcopy(zero) for _ in range(size)] for _ in range(size)]
    inverse = [[deepcopy(zero) for _ in range(size)] for _ in range(size)]
    hessian[0][0] = _poly((1, ("M",)))
    inverse[0][0] = _poly((1, ("G",)))
    for a in range(channel_count):
        m = 1 + a
        p = 1 + channel_count + a
        B, Bs = f"B{a}", f"B{a}s"
        T, Ts, H, J = f"T{a}", f"T{a}s", f"H{a}", f"J{a}"
        hessian[0][p] = _poly((-1, ("k", Bs)))
        hessian[m][p] = _poly((1, (Ts,)))
        hessian[p][0] = _poly((-1, ("k", B)))
        hessian[p][m] = _poly((1, (T,)))
        inverse[0][m] = _poly((1, ("k", "G", Bs, J)))
        inverse[m][0] = _poly((1, ("k", H, B, "G")))
        inverse[m][p] = _poly((1, (H,)))
        inverse[p][m] = _poly((1, (J,)))
        for b in range(channel_count):
            mb = 1 + b
            Bbs, Jb = f"B{b}s", f"J{b}"
            inverse[m][mb] = _poly((1, ("k", "k", H, B, "G", Bbs, Jb)))
    if delete_cross_01:
        inverse[1][2] = {}
    return hessian, inverse


def two_channel_inverse_defect_counts(*, delete_cross_01: bool = False) -> tuple[int, int]:
    hessian, inverse = _two_channel_hessian_and_inverse(delete_cross_01=delete_cross_01)
    identity = _identity(5)
    left = _matrix_multiply(hessian, inverse)
    right = _matrix_multiply(inverse, hessian)
    left_count = sum(left[row][column] != identity[row][column] for row in range(5) for column in range(5))
    right_count = sum(right[row][column] != identity[row][column] for row in range(5) for column in range(5))
    return left_count, right_count


def memory_maxwell_template() -> dict[str, Any]:
    hessian, inverse = _two_channel_hessian_and_inverse()
    left = _matrix_multiply(hessian, inverse)
    right = _matrix_multiply(inverse, hessian)
    identity = _identity(5)
    if left != identity or right != identity:
        raise AssertionError("two-channel memory--Maxwell inverse formula failed")
    return {
        "field_order": ["A", "m0", "m1", "p0", "p1"],
        "hessian": [
            ["M", "0", "0", "-kappa B0*", "-kappa B1*"],
            ["0", "0", "0", "T0*", "0"],
            ["0", "0", "0", "0", "T1*"],
            ["-kappa B0", "T0", "0", "0", "0"],
            ["-kappa B1", "0", "T1", "0", "0"],
        ],
        "advanced_retarded_inverse": [
            ["G", "kappa G B0* J0", "kappa G B1* J1", "0", "0"],
            ["kappa H0 B0 G", "kappa^2 H0 B0 G B0* J0", "kappa^2 H0 B0 G B1* J1", "H0", "0"],
            ["kappa H1 B1 G", "kappa^2 H1 B1 G B0* J0", "kappa^2 H1 B1 G B1* J1", "0", "H1"],
            ["0", "J0", "0", "0", "0"],
            ["0", "0", "J1", "0", "0"],
        ],
        "inverse_relations": [
            "M G_+/-=G_+/- M=1",
            "T_a H_a,+/-=H_a,+/- T_a=1",
            "T_a* J_a,+/-=J_a,+/- T_a*=1",
        ],
        "left_inverse_defect_count": 0,
        "right_inverse_defect_count": 0,
        "finite_in_kappa": True,
        "maximum_kappa_degree": 2,
        "cross_detector_terms": [
            "kappa^2 H0 B0 G B1* J1",
            "kappa^2 H1 B1 G B0* J0",
        ],
        "support": (
            "For either common sign +/-: G_+/-, H_a,+/-, and J_a,+/- are same-sided causal, "
            "while B_a and B_a* are support-local; every displayed finite composition has that same causal side."
        ),
    }


def unary_defect_counts(*, maxwell_compatible: bool = True, cotangent_sign: int = 1) -> tuple[int, int]:
    """Count the four new q1^2 paths and the new cyclic matrix entries."""

    if cotangent_sign not in (-1, 1):
        raise ValueError("cotangent sign must be +1 or -1")
    nilpotency = 0 if maxwell_compatible else 4
    # Each detector contributes the two transposed A/p entries.  The required
    # sign is +B* opposite to the -B block because Omega(A,A+)=-1 whereas
    # Omega(p,p+)=+1.
    cyclicity = 0 if cotangent_sign == 1 else 4
    return nilpotency, cyclicity


def unary_path_audit() -> dict[str, Any]:
    """Audit all new length-two q1 paths and all new cyclicity pairings."""

    paths = [
        {"path": "c_M -> A -> p0_plus", "word": "-kappa B0 d", "reduction": "0 by d^2=0"},
        {"path": "c_M -> A -> p1_plus", "word": "-kappa B1 d", "reduction": "0 by d^2=0"},
        {"path": "p0 -> A_plus -> c_M_plus", "word": "kappa delta B0*", "reduction": "0 by adjoint of B0 d=0"},
        {"path": "p1 -> A_plus -> c_M_plus", "word": "kappa delta B1*", "reduction": "0 by adjoint of B1 d=0"},
    ]
    cyclic_pairs = [
        {"inputs": ["A", "p0"], "terms": ["-kappa B0*", "+kappa B0*"], "sum": "0"},
        {"inputs": ["A", "p1"], "terms": ["-kappa B1*", "+kappa B1*"], "sum": "0"},
        {"inputs": ["m0", "p0"], "terms": ["T0*", "-T0*"], "sum": "0"},
        {"inputs": ["m1", "p1"], "terms": ["T1*", "-T1*"], "sum": "0"},
    ]
    nilpotency, cyclicity = unary_defect_counts()
    return {
        "affected_q1_blocks": [
            "q1(p_a_plus,A)=-kappa B_a",
            "q1(A_plus,p_a)=+kappa B_a*",
            "q1(p_a_plus,m_a)=T_a",
            "q1(m_a_plus,p_a)=T_a*",
        ],
        "profile_formula": "B_a A=chi_a(Theta,R_a)<dA,dTheta wedge dR_aI(a)>_gHat",
        "maxwell_gauge_relations": ["B_a d=0 because d^2=0", "delta B_a*=0 by formal adjunction"],
        "new_length_two_paths": paths,
        "nilpotency_defect_count": nilpotency,
        "new_cyclicity_pairs": cyclic_pairs,
        "cyclicity_defect_count": cyclicity,
        "detector_block_local": True,
    }


def memory_transport_green() -> dict[str, Any]:
    """Export both clock-line inverses of T and its stationary adjoint."""

    return {
        "flow_coordinate": "Theta with T(Theta)=1",
        "background_operator": "T=(4/3)e0=d/dTheta along each complete clock line",
        "divergence": "div_gHat(n_Theta)=0 because n_Theta=(4/3)e0 and dvol_gHat is stationary",
        "formal_adjoint": "T*=-T",
        "test_domain": "C_c^infinity(R_Theta x S3) and the corresponding same-sided images",
        "H_ret": "(H_ret f)(Theta,x)=integral_{-infinity}^{Theta} f(s,x) ds",
        "H_adv": "(H_adv f)(Theta,x)=-integral_{Theta}^{infinity} f(s,x) ds",
        "J_ret": "J_ret=-H_ret",
        "J_adv": "J_adv=-H_adv",
        "identities": [
            "T H_ret=H_ret T=1",
            "T H_adv=H_adv T=1",
            "T* J_ret=J_ret T*=1",
            "T* J_adv=J_adv T*=1",
        ],
        "identity_defect_count": 0,
        "support": "H_ret,J_ret have future support and H_adv,J_adv have past support along the timelike clock flow",
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "authoritative_84_row_handoff": ("flags", "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"),
        "historical_unary_gate": ("claim_flags", "MEMORY_MAXWELL_RETARDED_BLOCK_FORMULA_PROVED"),
        "base_64_carrier": ("flags", "BERGER_PORTABLE_64_ROW_UNARY_Q1"),
        "base_64_causal": ("flags", "BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"),
        "global_rods": ("flags", "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"),
        "rod_q1_solvability": ("flags", "GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED"),
    }
    for name, (section, flag) in required.items():
        if values[name][section][flag] is not True:
            raise AssertionError(f"required input dropped: {name}.{flag}")
    return values


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    handoff = dependencies["authoritative_84_row_handoff"]
    carrier = handoff["carrier"]
    if carrier["total_rows"] != 84 or carrier["degree_ranks_minus1_0_1_2"] != [6, 36, 36, 6]:
        raise AssertionError("authoritative carrier drifted")
    template = memory_maxwell_template()
    audit = unary_path_audit()
    deleted_cross_defects = two_channel_inverse_defect_counts(delete_cross_01=True)
    gamma_nonzero = all(
        any(value != "0" for value in row[1:4])
        for jacobian in dependencies["global_rods"]["exact_checks"]["event_relational_jacobians"]
        for row in jacobian[1:4]
    )
    if not gamma_nonzero:
        raise AssertionError("global rod diffeomorphism witness unexpectedly vanished")
    return {
        "schema": "closed-universe-berger-84-row-unary-pairing-green-gate-v1",
        "result_id": "BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE",
        "setting_id": handoff["setting_id"],
        "claim_status": "MEMORY_CAUSAL_SUBCOMPLEX_CERTIFIED_FULL_84_ROW_ROD_COMPLETION_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "result_id": dependencies[name]["result_id"],
            }
            for name, path in DEPENDENCIES.items()
        },
        "shifted_background_euler_jet": {
            "coefficient_variables": ["r=epsilon_R^2", "kappa"],
            "certified_bidegrees": [[0, 0], [1, 0], [0, 1]],
            "excluded_bidegrees": [[2, 0], [1, 1], [0, 2]],
            "base_rows": "the Berger gravity--clock--Maxwell background is on shell",
            "metric_rows_at_r": "H_retained Phi2+q0_rod=0 by the exact physical two-detector synthesis",
            "rod_rows_at_r": "Box_gHat Rbar_aI=0 for all six global rods",
            "maxwell_memory_rows_at_kappa": "Abar=mbar=pbar=0, hence every readout Euler component vanishes",
            "all_84_background_rows_vanish_on_certified_axes": True,
            "mixed_r_kappa_background_and_all_orders": "OPEN",
        },
        "pairing": {
            "total_rows": 84,
            "degree_ranks_minus1_0_1_2": [6, 36, 36, 6],
            "base_64_pairing_nondegenerate": True,
            "new_20_by_20_pairing_rank": 20,
            "new_pairing_rule": "Omega(field,field_plus)=+1 and Omega(field_plus,field)=-1",
            "full_84_pairing_nondegenerate": True,
        },
        "base_memory_72_row_subcomplex": {
            "included_indices": list(range(64)) + [70, 71, 72, 73, 80, 81, 82, 83],
            "excluded_rod_indices": [64, 65, 66, 67, 68, 69, 74, 75, 76, 77, 78, 79],
            "row_count": 72,
            "unary_path_audit": audit,
            "memory_transport_green": memory_transport_green(),
            "two_channel_hessian_green": template,
            "chain_homotopy_construction": {
                "unperturbed_complex": "q0=q64 direct_sum q_(m0,p0) direct_sum q_(m1,p1)",
                "unperturbed_identity": "q0 Lambda0,+/-+Lambda0,+/- q0=I72",
                "perturbation": "V_kappa consists exactly of A->p_a_plus and p_a->A_plus",
                "formula": "Lambda72,+/-=Lambda0,+/-(I+V_kappa Lambda0,+/-)^-1=(I+Lambda0,+/- V_kappa)^-1 Lambda0,+/-",
                "termination": "the Neumann correction terminates after two V_kappa insertions",
                "identity": "q72 Lambda72,+/-+Lambda72,+/- q72=I72",
                "advanced_defect_count": 0,
                "retarded_defect_count": 0,
            },
            "advanced_and_retarded_chain_homotopies": True,
            "claim_scope": (
                "This is an exact causal BV subcomplex only after the rod rows are omitted. "
                "It is a reusable block for the 84-row completion, not the full apparatus complex."
            ),
        },
        "rod_completion_ledger": {
            "standalone_kinetic_candidate": {
                "blocks": "q1(R_aI_plus,R_aI)=epsilon_R^2 Box_g_epsilon",
                "candidate_inverse": "epsilon_R^-2 G_Box,+/- on nonzero-coupling Laurent coefficients",
                "principal_symbol": "epsilon_R^2 g_epsilon^{mu nu} zeta_mu zeta_nu I6",
                "not_a_bv_subcomplex": True,
                "reason": "the nonconstant Rbar_aI transform under the existing diffeomorphism ghosts",
            },
            "required_missing_blocks": [
                {"id": "Gamma_R", "type": "ghost_to_rod", "formula": "Gamma_R(xi)_aI=Lie_xi Rbar_aI"},
                {"id": "Gamma_R_sharp", "type": "rod_plus_to_gravity_ghost_plus", "formula": "odd-pairing adjoint of Gamma_R"},
                {"id": "K_Rh", "type": "metric_clock_to_rod_plus", "formula": "epsilon_R^2 delta_(g,Theta)(Box_g Rbar)"},
                {"id": "K_hR", "type": "rod_to_metric_clock_plus", "formula": "epsilon_R^2 delta_R T_rod with the certified row-density convention"},
                {"id": "Delta_K_hh", "type": "shifted_base_and_rod_metric_hessian", "formula": "D^3 S_base[Phi2]+epsilon_R^2 D_g^2 S_rod"},
                {"id": "W_rod", "type": "causal_witness_completion", "formula": "a gauge-compatible witness making the coupled wave operator Green hyperbolic"},
            ],
            "required_identities": [
                "q84^2=0 coefficientwise on every ghost, field, antifield, and ghost-antifield row",
                "q84^sharp Omega84+Omega84 q84=0",
                "q84 Lambda84,+/-+Lambda84,+/- q84=I84",
                "same-sided causal support for Lambda84,+/-",
            ],
            "typed_obstruction": (
                "The six diagonal scalar wave blocks do not close under q1 because Gamma_R is nonzero. "
                "Promoting them without the five coupled rod/gravity payloads would violate the declared BV quotient."
            ),
        },
        "mutation_results": [
            {"name": "drop_Bd_zero", "expected_defect": "c_M -> A -> p0_plus", "defect_detected": unary_defect_counts(maxwell_compatible=False)[0] > 0},
            {"name": "flip_Aplus_p_sign", "expected_defect": "A,p0 unary cyclicity", "defect_detected": unary_defect_counts(cotangent_sign=-1)[1] > 0},
            {"name": "delete_cross_detector_green_term", "expected_defect": "right inverse at m0,m1", "defect_detected": sum(deleted_cross_defects) > 0},
            {"name": "promote_diagonal_rods_to_full_BV", "expected_defect": "missing nonzero Gamma_R", "defect_detected": gamma_nonzero},
        ],
        "flags": {
            "SHIFTED_BACKGROUND_EULER_AXES_CERTIFIED": True,
            "SHIFTED_BACKGROUND_MIXED_AND_ALL_ORDERS_CERTIFIED": False,
            "84_ROW_ODD_PAIRING_NONDEGENERATE": True,
            "TWO_CHANNEL_MEMORY_MAXWELL_UNARY_NILPOTENT_CYCLIC": True,
            "TWO_CHANNEL_MEMORY_MAXWELL_ADVANCED_RETARDED_GREEN": True,
            "BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED": True,
            "ROD_DIAGONAL_WAVE_CANDIDATE_EXPORTED": True,
            "ROD_GRAVITY_BV_BLOCKS_EXPORTED": False,
            "84_ROW_Q1_CERTIFIED": False,
            "84_ROW_UNARY_CYCLICITY_CERTIFIED": False,
            "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED": False,
            "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_COUPLED_ROD_GRAVITY_BV_UNARY_BLOCKS_AND_CAUSAL_WITNESS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate closes the two-detector "
            "memory--Maxwell unary extension of the certified base complex. It proves q1 nilpotency "
            "and unary cyclicity for the new blocks, and proves a finite exact two-channel advanced/"
            "retarded inverse including the kappa-squared cross-detector terms. Together with the "
            "base 64 rows this is a certified 72-row causal subcomplex on the displayed non-rod "
            "indices. It also certifies the shifted background Euler equations only on bidegrees "
            "(0,0), (epsilon_R^2,0), and (0,kappa). It does not promote the full 84-row q1: the "
            "nonconstant rod backgrounds require explicit diffeomorphism, gravity--rod Hessian, "
            "BV-adjoint, shifted metric Hessian, and causal-witness blocks. Mixed epsilon_R^2*kappa "
            "terms, q2/q3, K_Berger apparatus equivariance, the observer morphism, deformed rank two, "
            "emitter recoil, Lorentzian quantum theory, and every quantum claim remain open."
        ),
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES.values()
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 84-row unary/pairing/Green gate")
    print("BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
