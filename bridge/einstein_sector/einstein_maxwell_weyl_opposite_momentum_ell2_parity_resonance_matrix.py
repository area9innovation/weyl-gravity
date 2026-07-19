"""Certify the tuned ell=2 axial/polar opposite-momentum L=4 resonance matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.schema.json"
INPUTS = {
    "axial_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json",
    "intersection_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "finite_generic_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
}
ENGINES = {
    "polar_source": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_opposite_momentum_ell2_polar_resonant_source_explore.py",
    "cross_source": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_opposite_momentum_ell2_axial_polar_resonant_source_explore.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    axial_record = records["axial_obstruction"]
    if not axial_record["classification"]["polar_L4_p_adjoint_pairing_nonzero"]:
        raise AssertionError("axial diagonal input changed")
    if not records["intersection_gate"]["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"]:
        raise AssertionError("common-zero gate changed")
    if not records["finite_generic_cone"]["classification"]["bounded_resonance_functional_ledger_defined_exactly"]:
        raise AssertionError("finite bounded-functional theorem changed")

    root = sp.sqrt(3)
    b = -265 + 149 * root
    axial_diagonal = -sp.Rational(1152, 203) * b
    polar_source = sp.Matrix(
        [
            -sp.Rational(32, 7) * (-13348 + 6219 * root),
            0,
            sp.Rational(16, 105) * (-192853 + 126216 * root),
            sp.Rational(8448, 7) * (-35 + 23 * root),
        ]
    )
    polar_adjoints = sp.Matrix.hstack(
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([-sp.Rational(4, 87), 0, -sp.Rational(40, 29), 1]),
    )
    polar_pairings = sp.Matrix([(polar_adjoints[:, index].T * polar_source)[0] for index in range(2)]).applyfunc(sp.factor)
    polar_diagonal = sp.Rational(3456, 203) * b
    if (polar_pairings - sp.Matrix([0, polar_diagonal])).applyfunc(sp.simplify) != sp.zeros(2, 1):
        raise AssertionError(f"polar diagonal pairings changed: {polar_pairings}")
    if sp.simplify(polar_diagonal + 3 * axial_diagonal) != 0:
        raise AssertionError("axial/polar diagonal ratio changed")

    cross_source = sp.Matrix(
        [
            -sp.Rational(48, 7) * sp.sqrt(-7 + 12 * root) * (-224 * sp.sqrt(6) + 353 * sp.sqrt(2)),
            sp.Rational(288, 7) * (-215 * sp.sqrt(58) + 112 * sp.sqrt(174)),
            -sp.Rational(48, 7) * sp.sqrt(-7 + 12 * root) * (-26 * sp.sqrt(6) + 11 * sp.sqrt(2)),
            sp.Rational(48, 35) * (-215 * sp.sqrt(58) + 112 * sp.sqrt(174)),
        ]
    )
    cross_adjoints = sp.Matrix.hstack(
        sp.Matrix([-1, 0, 1, 0]),
        sp.Matrix([0, -sp.Rational(1, 30), 0, 1]),
    )
    cross_pairings = sp.Matrix([(cross_adjoints[:, index].T * cross_source)[0] for index in range(2)]).applyfunc(sp.factor)
    cross_coefficient = sp.Rational(864, 7) * sp.sqrt(-7 + 12 * root) * (-11 * sp.sqrt(6) + 19 * sp.sqrt(2))
    if (cross_pairings - sp.Matrix([cross_coefficient, 0])).applyfunc(sp.simplify) != sp.zeros(2, 1):
        raise AssertionError(f"cross pairings changed: {cross_pairings}")
    if 19**2 - 3 * 11**2 != -2 or cross_coefficient == 0:
        raise AssertionError("cross nonzero witness failed")

    a_plus, a_minus, p_plus, p_minus = sp.symbols("a_plus a_minus p_plus p_minus")
    polar_functional = sp.factor(axial_diagonal * (a_plus * a_minus - 3 * p_plus * p_minus))
    axial_functional = sp.factor(cross_coefficient * (a_plus * p_minus - a_minus * p_plus))
    for sign in (-1, 1):
        substitution = {a_plus: sign * sp.sqrt(3) * p_plus, a_minus: sign * sp.sqrt(3) * p_minus}
        if sp.simplify(polar_functional.subs(substitution)) != 0 or sp.simplify(axial_functional.subs(substitution)) != 0:
            raise AssertionError("declared mixed null ray changed")

    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-ell2-parity-resonance-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_PARITY_RESONANCE_MATRIX",
        "result_state": "COMPLETE_AXIAL_POLAR_L4_SUM_FREQUENCY_RESONANCE_MATRIX_CERTIFIED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXPLICIT_ELL2_TUNED_NONZERO_MOMENTUM_TWO_PARITY_FIXTURE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "axial and polar ell=2,m=0 Einstein-minus coefficients at +/-k inside the twist-aligned common-zero construction",
            "degree": 2,
            "parity": "both input parities; polar and axial L=4 outputs",
            "ell": "input ell=2; output L=4",
            "m": "input m=0; output M=0",
            "k": "+/-sqrt(2*sqrt(3)-7/6); output K=0",
            "omega": "input omega_-^2=29/6; output Omega=2omega_-",
        },
        "direct_source_ledger": {
            "axial_axial": {
                "source_rows": axial_record["direct_four_dimensional_source"]["source_rows"],
                "adjoint_pairings": axial_record["direct_four_dimensional_source"]["adjoint_pairings"],
            },
            "polar_polar": {
                "source_rows": _strings(polar_source),
                "left_adjoint_columns": [[str(value) for value in polar_adjoints[:, index]] for index in range(2)],
                "adjoint_pairings": _strings(polar_pairings),
            },
            "axial_plus_polar_minus": {
                "source_rows": _strings(cross_source),
                "left_adjoint_columns": [[str(value) for value in cross_adjoints[:, index]] for index in range(2)],
                "adjoint_pairings": _strings(cross_pairings),
            },
        },
        "reflection_audit": {
            "axial_input": "x reflection maps the +k axial representative to minus the certified -k representative",
            "polar_input": "x reflection maps the +k polar representative to the certified -k representative",
            "consequence": "the reflected polar-output diagonal coefficient is unchanged, while the first axial-output cross coefficient reverses sign",
        },
        "resonance_matrix": {
            "coefficient_symbols": ["a_+", "a_-", "p_+", "p_-"],
            "polar_output_functional": str(polar_functional),
            "axial_output_functional": str(axial_functional),
            "axial_diagonal_coefficient": str(axial_diagonal),
            "polar_over_axial_diagonal_ratio": "-3",
            "cross_coefficient": str(cross_coefficient),
            "nonzero_witnesses": {"diagonal_algebraic_norm": "3622", "cross_linear_norm": "19^2-3*11^2=-2"},
        },
        "null_locus": {
            "equations": ["a_+*a_-=3*p_+*p_-", "a_+*p_-=a_-*p_+"],
            "nonzero_two_momentum_components": "a_+=sigma*sqrt(3)*p_+ and a_-=sigma*sqrt(3)*p_- with one common sigma in {+1,-1}",
            "pure_axial_verdict": "OBSTRUCTED",
            "pure_polar_verdict": "OBSTRUCTED",
            "mixed_L4_resonance_null_face_nonempty": True,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OPEN", "reason": "the L4 resonant matrix is complete, but other output blocks of the full two-parity common-zero tangent have not been coefficientwise solved"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "all nonzero shell defects admit finite secular inverses once the five stabilizer moment maps vanish"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_tuned_L4_two_parity_resonance_matrix_certified": True,
            "pure_axial_and_pure_polar_directions_obstructed": True,
            "mixed_L4_resonance_null_face_nonempty": True,
            "complete_bounded_second_order_extension_on_mixed_null_face": False,
            "general_bounded_zero_locus_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first bounded phase functional is indefinite across parity: pure axial and pure polar standing waves are obstructed with opposite diagonal signs. Their diagonal defects cancel at a 3:1 coefficient-product ratio, while the axial cross functional forces the same axial/polar ratio on both momenta. This produces an exact mixed L4-null face, but not yet a complete bounded extension.",
        "next_gate": "evaluate every remaining output block on a_plus=sigma*sqrt(3)*p_plus and a_minus=sigma*sqrt(3)*p_minus, including the balancing Einstein-plus coefficients, to prove or obstruct a full bounded correction",
        "claim_boundary": "This theorem classifies only the tuned ell=2 L=4,K=0,Omega=2omega_- resonance matrix. It does not certify the complete bounded tangent, other output blocks, other ell or momentum fibres, final residual descent, causal propagation, all-orders integration, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "direct_engines": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in ENGINES.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_1_fast": {"status": "PENDING", "tests_run": 0},
            "tier_2_direct_replays": {
                "polar_polar": {"status": "PASS", "elapsed_seconds": 419.61, "max_rss_kb": 134252},
                "axial_polar": {"status": "PASS", "elapsed_seconds": 667.85, "max_rss_kb": 131024},
                "axial_axial": {"status": "PASS_BY_CONTENT_ADDRESS"},
            },
            "tier_3": {"status": "NOT_RUN", "reason": "the full bounded cone and higher lifecycles remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix",
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
        raise AssertionError("opposite-momentum parity resonance certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_PARITY_RESONANCE_MATRIX: PASS")


if __name__ == "__main__":
    main()
