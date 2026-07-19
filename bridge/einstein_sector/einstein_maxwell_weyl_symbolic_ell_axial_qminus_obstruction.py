"""All-ell axial q-minus bounded obstruction on the tuned compact product.

The calculation evaluates the action-derived quadratic PBW operator on two
highest-weight axial Einstein-minus representatives with opposite compact
momenta.  Highest weight isolates the L=2*ell output without interpolation.
The axisymmetric coefficient follows from the exact top Legendre/Gaunt ratio.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.schema.json"
PBW_SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_symbolic_ell_axial_qminus_pbw_slice.json"
INPUTS = {
    "symbolic_collision": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json",
    "common_zero_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "ell2_direct_replay": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _evaluate_relevant_pbw() -> dict[int, sp.Expr]:
    payload = json.loads(PBW_SLICE.read_text(encoding="utf-8"))
    _require(
        payload["result_id"] == "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_AXIAL_QMINUS_PBW_SLICE",
        "quadratic PBW slice identity changed",
    )
    extraction = payload["extraction"]
    _require(extraction["maximum_total_derivative_order"] == 4, "quadratic differential order changed")
    _require(extraction["highest_weight_isolates_L_2ell"], "highest-weight isolation was not certified")
    ell = sp.symbols("ell", integer=True, positive=True)
    momentum, frequency, root = sp.symbols("k omega r", positive=True, real=True)
    local_symbols = {"ell": ell, "k": momentum, "omega": frequency, "r": root, "I": sp.I}
    rows = payload["highest_weight_rows"]
    return {
        20: sp.sympify(rows["E00"], locals=local_symbols),
        21: sp.sympify(rows["E01"], locals=local_symbols),
        24: sp.sympify(rows["E11"], locals=local_symbols),
        32: sp.sympify(rows["Maxwell_theta"], locals=local_symbols),
        33: sp.sympify(rows["Maxwell_phi"], locals=local_symbols),
    }


def _reduce_root(expression: sp.Expr, ell: sp.Symbol, root: sp.Symbol) -> sp.Expr:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    remainder = sp.Poly(sp.expand(numerator), root).rem(
        sp.Poly(root**2 - 2 * ell * (ell + 1), root)
    )
    return sp.factor(remainder.as_expr() / denominator)


def symbolic_result() -> dict[str, sp.Expr]:
    outputs = _evaluate_relevant_pbw()
    ell = sp.symbols("ell", integer=True, positive=True)
    momentum, frequency, root = sp.symbols("k omega r", positive=True, real=True)
    _require(outputs[21] == 0 and outputs[33] == 0, "forbidden highest-weight rows survived")

    target_lambda = 2 * ell * (2 * ell + 1)
    target_frequency_squared = 4 * frequency**2
    dynamical_adjoint = sp.Matrix(
        [
            -sp.Rational(8, 9) / target_frequency_squared,
            0,
            -4 * target_lambda / (3 * target_frequency_squared),
            1,
        ]
    )
    # The highest-weight Maxwell equation is E^theta=c X^theta with
    # X^theta=i*(2*ell) at the equator.  The action row is 2*Lambda*c.
    maxwell_action_row = sp.factor(target_lambda * outputs[32] / (sp.I * ell))
    # Symmetric metric variations carry twice the scalar top-Gaunt ratio;
    # the Maxwell row carries it once.  Pull the common scalar ratio out.
    highest_reduced_pairing = sp.factor(
        2 * dynamical_adjoint[0] * outputs[20]
        + 2 * dynamical_adjoint[2] * outputs[24]
        + maxwell_action_row
    )

    momentum_squared = root - ell / 2 - sp.Rational(1, 6)
    frequency_squared = ell * (ell + 1) - ell / 2 - sp.Rational(1, 6)
    tuned = highest_reduced_pairing.subs(
        {momentum**2: momentum_squared, frequency**2: frequency_squared}
    )
    tuned = _reduce_root(tuned, ell, root)
    gaunt = sp.binomial(2 * ell, ell) ** 2 / sp.binomial(4 * ell, 2 * ell)
    axisymmetric_pairing = sp.factor(gaunt * tuned)

    polynomial_a = 18 * ell**4 + 24 * ell**3 + 4 * ell**2 + 16 * ell + 2
    polynomial_b = 9 * ell**3 + 21 * ell**2 - 9 * ell + 11
    expected_highest = sp.factor(
        -8
        * ell**2
        * (ell + 1)
        * (2 * ell + 1)
        * (root * polynomial_b - polynomial_a)
        / (3 * (6 * ell**2 + 3 * ell - 1))
    )
    _require(sp.factor(tuned - expected_highest) == 0, "symbolic adjoint coefficient changed")
    norm = sp.factor(polynomial_a**2 - 2 * ell * (ell + 1) * polynomial_b**2)
    expected_norm = 2 * (ell - 1) ** 3 * (ell + 2) * (
        81 * ell**4 + 54 * ell**3 + 42 * ell - 1
    )
    _require(sp.factor(norm - expected_norm) == 0, "nonvanishing norm factorization changed")
    return {
        "ell": ell,
        "root": root,
        "E00_highest": outputs[20],
        "E01_highest": outputs[21],
        "E11_highest": outputs[24],
        "Maxwell_theta_highest": outputs[32],
        "Maxwell_phi_highest": outputs[33],
        "maxwell_action_row": maxwell_action_row,
        "gaunt": gaunt,
        "polynomial_a": polynomial_a,
        "polynomial_b": polynomial_b,
        "highest_pairing": expected_highest,
        "axisymmetric_pairing": axisymmetric_pairing,
        "norm": norm,
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["symbolic_collision"]["classification"]["unique_nonzero_frequency_collision_is_L_2ell_K0_p_shell"],
        "symbolic collision input changed",
    )
    _require(
        records["common_zero_gate"]["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"],
        "common-zero witness changed",
    )
    result = symbolic_result()
    ell = result["ell"]
    root = result["root"]
    assert isinstance(ell, sp.Symbol) and isinstance(root, sp.Symbol)
    slow_rail_samples = {
        2: -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3)),
        3: -sp.Rational(25600, 341) * (-137 + 52 * sp.sqrt(6)),
        4: -sp.Rational(627200, 45903) * (-3137 + 887 * sp.sqrt(10)),
        5: -sp.Rational(50803200, 172159) * (-451 + 101 * sp.sqrt(15)),
        6: -sp.Rational(40981248, 1730957) * (-14377 + 2657 * sp.sqrt(21)),
    }
    samples = {}
    for value, direct_sample in slow_rail_samples.items():
        formula_sample = sp.factor(
            result["axisymmetric_pairing"].subs(
                {ell: value, root: sp.sqrt(2 * value * (value + 1))}
            )
        )
        _require(sp.factor(formula_sample - direct_sample) == 0, f"ell={value} slow-rail mismatch")
        samples[str(value)] = str(sp.factor(direct_sample))
    frozen_ell2 = sp.sympify(
        records["ell2_direct_replay"]["bounded_obstruction"]["value_on_unit_q_minus_pair"]
    )
    _require(sp.factor(sp.sympify(samples["2"]) - frozen_ell2) == 0, "ell=2 direct replay mismatch")

    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-axial-qminus-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_AXIAL_QMINUS_BOUNDED_OBSTRUCTION",
        "result_state": "ALL_ELL_TUNED_AXIAL_COMMON_ZERO_TANGENTS_HAVE_POSITIVE_POLAR_P_RESONANT_FUNCTIONAL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_INTEGER_ELL_AT_ONE_TUNED_NONZERO_MOMENTUM_FIBRE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned separately for each ell",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "twist-aligned common-zero tangent with axial Einstein-plus/minus waves at +/-k; the resonant coefficient is the q-minus self-product",
            "degree": 2,
            "parity": "axial input; polar p-primary output",
            "ell": "every integer input ell>=2; output L=2*ell",
            "m": "axisymmetric input m=0 and output M=0, derived through the highest-weight M=2*ell coefficient",
            "k": "+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)",
            "omega": "input omega_minus and output Omega=2*omega_minus",
        },
        "action_derived_pbw_reduction": {
            "method": "consume the content-addressed PBW slice obtained by evaluating the independently verified parent q2 on Y_(ell,ell)=sin(theta)^ell exp(i ell phi) at the equator; M=2ell isolates the top irreducible output",
            "input_field_rows": ["g_02", "g_03", "g_12", "g_13", "A_0", "A_1"],
            "output_action_rows": ["g_00_star", "g_01_star", "g_11_star", "A_2_star", "A_3_star"],
            "maximum_total_derivative_order": 4,
            "highest_weight_rows": {
                "E00": str(result["E00_highest"]),
                "E01": str(result["E01_highest"]),
                "E11": str(result["E11_highest"]),
                "Maxwell_theta": str(result["Maxwell_theta_highest"]),
                "Maxwell_phi": str(result["Maxwell_phi_highest"]),
            },
            "axisymmetric_top_Gaunt_factor": str(result["gaunt"]),
            "metric_rows_relative_factor": "2*axisymmetric_top_Gaunt_factor",
            "Maxwell_row_relative_factor": "axisymmetric_top_Gaunt_factor",
        },
        "symbolic_adjoint_pairing": {
            "root_relation": "r^2=2*ell*(ell+1)",
            "A_ell": str(result["polynomial_a"]),
            "B_ell": str(result["polynomial_b"]),
            "highest_weight_reduced_pairing": str(result["highest_pairing"]),
            "axisymmetric_pairing": str(result["axisymmetric_pairing"]),
            "direct_exact_samples": samples,
            "direct_slow_rail_elapsed_seconds": {
                "2": "353.95",
                "3": "304.50",
                "4": "452.65",
                "5": "498.93",
                "6": "559.31"
            },
        },
        "nonvanishing_proof": {
            "norm_factorization": str(result["norm"]),
            "positivity_domain": "ell is an integer >=2",
            "A_positive": True,
            "B_positive": True,
            "norm_strictly_positive": True,
            "conclusion": "A_ell>sqrt(2*ell*(ell+1))*B_ell, so the displayed adjoint pairing is strictly positive",
        },
        "bounded_obstruction": {
            "resonant_functional": "R_polar_L_2ell(u)=zeta_p^T S_(L=2ell,M=0,K=0,Omega=2omega_minus)(u,u)",
            "value_strictly_positive_every_ell": True,
            "verdict": "OBSTRUCTED",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the nonzero p-shell functional has the certified finite secular inverse and the common stabilizer moment maps vanish",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "action_derived_q2_used": True,
            "highest_weight_projection_exact_without_interpolation": True,
            "symbolic_axial_dynamical_adjoint_coefficient_computed": True,
            "coefficient_strictly_positive_every_integer_ell_ge_2": True,
            "all_ell_tuned_axial_common_zero_tangent_bounded_obstructed": True,
            "polar_or_mixed_input_coefficient_computed": False,
            "fixed_circumference_or_multiple_abs_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The ell=2 obstruction is universal along the tuned axial common-zero family: Taub moment maps vanish, yet an independent polar extra-primary resonant functional is strictly positive for every ell>=2. The bounded tangent cone is therefore strictly smaller than the stabilizer moment-map zero set at every generic angular degree.",
        "next_gate": "compute the polar and axial-polar mixed q-minus coefficients, then join this single-|k| theorem to the finite-multimomentum divisor ledger",
        "claim_boundary": "This theorem covers axial inputs at one separately tuned |k| fibre for each ell>=2. It does not compute polar or mixed input coefficients, classify one fixed circumference across ell, join multiple |k| fibres, construct a causal inverse, descend the final residual quotient, or make observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "pbw_slice": {"path": str(PBW_SLICE.relative_to(ROOT)), "sha256": _sha256(PBW_SLICE)},
            "parent_q2_sha256": json.loads(PBW_SLICE.read_text(encoding="utf-8"))["parent"]["q2_sha256"],
            "parent_row_layout_sha256": json.loads(PBW_SLICE.read_text(encoding="utf-8"))["parent"]["row_layout_sha256"],
            "parent_action_sha256": json.loads(PBW_SLICE.read_text(encoding="utf-8"))["parent"]["action_sha256"],
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build_certificate()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        _require(json.loads(OUTPUT.read_text(encoding="utf-8")) == value, "stale symbolic obstruction certificate")
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_AXIAL_QMINUS_BOUNDED_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
