"""Close the zero-frequency source on the balanced exceptional ellipse fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.schema.json"
INPUTS = {
    "balance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json",
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
    "exceptional": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.json",
    "polar_e1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_e1_zero_source_fixture.json",
    "polar_e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_e2_zero_source_fixture.json",
    "polar_cross": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_cross_zero_source_fixture.json",
    "axial_neutral": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json",
    "same_parity_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in values])


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    if records["exceptional"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"] != ["-16/9", "0", "-8/9", "0"]:
        raise AssertionError("exceptional zero source changed")
    if records["polar_e1"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"] != ["-12/5", "0", "-6/5", "0"]:
        raise AssertionError("polar B-unit source changed")
    if records["polar_e2"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"] != ["-29952/5", "0", "-14976/5", "0"]:
        raise AssertionError("polar first-basis source changed")
    if records["polar_cross"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"] != ["0", "0", "0", "0"]:
        raise AssertionError("polar control interference changed")
    if records["same_parity_zero"]["zero_output_blocks"]["polar_L2_L4"] != "invertible":
        raise AssertionError("zero-frequency polar target inversion changed")
    if "d has zero self-source" not in records["standard_global"]["bounded_correction"]["homogeneous_c_d_Wx"]:
        raise AssertionError("circumference velocity self-source changed")

    d = sp.symbols("d", real=True, nonzero=True)
    root = sp.sqrt(3)
    rx2 = sp.Rational(115, 16) * d**2
    y1sq = rx2**2 / (243 * d**2)
    y2sq = sp.Rational(75, 746496) * d**2
    source_normalized_e2 = sp.Rational(120250, 729) * (6 + 5 * root) * d**2
    direct_minus2 = sp.factor(source_normalized_e2 / 48)

    exceptional = _vector(["-16/9", "0", "-8/9", "0"]) * rx2
    # Ellipse y1 multiplies the first action basis (-8,0,-72,48), namely the
    # direct fixture called extra_e2.  Ellipse y2 multiplies
    # (64/sqrt(3))*(0,1,0,0).
    control_1 = _vector(["-29952/5", "0", "-14976/5", "0"]) * y1sq
    control_2 = _vector(["-12/5", "0", "-6/5", "0"]) * sp.Rational(4096, 3) * y2sq
    tau_minus = sp.Rational(48, 5) * (-6 + 5 * root)
    einstein_minus = sp.Matrix([tau_minus, 0, tau_minus / 2, 0]) * direct_minus2
    total = (exceptional + control_1 + control_2 + einstein_minus).applyfunc(sp.factor)
    if total != sp.zeros(4, 1):
        raise AssertionError(f"balanced homogeneous source did not cancel: {total}")

    components = {
        "exceptional_axial_self": [str(sp.factor(value)) for value in exceptional],
        "ell2_polar_control_e1_self": [str(sp.factor(value)) for value in control_1],
        "ell2_polar_control_e2_self": [str(sp.factor(value)) for value in control_2],
        "ell2_polar_control_interference": ["0", "0", "0", "0"],
        "ell2_axial_Einstein_minus_self": [str(sp.factor(value)) for value in einstein_minus],
        "circumference_velocity_self": ["0", "0", "0", "0"],
    }
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-zero-frequency-source-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ZERO_FREQUENCY_SOURCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": records["balance"]["scope"],
        "direct_representative_amplitudes": {
            "exceptional_axial": "|x|^2=(115/16)d^2",
            "ell2_polar_first_action_basis": "|y1|^2=|x|^4/(243*d^2)",
            "ell2_polar_second_action_basis": "|y2|^2=75*d^2/746496",
            "Einstein_minus_axial": "|A_-|^2=(60125/17496)*(6+5sqrt(3))*d^2",
        },
        "homogeneous_zero_frequency_source": {
            "row_order": ["E00", "E11", "E22", "Maxwell1"],
            "components": components,
            "combined": ["0", "0", "0", "0"],
            "constant_lapse_ray": "every nonzero component is proportional to (1,0,1/2,0)",
        },
        "remaining_zero_frequency_channels": {
            "exceptional_axial_self": "L=2 polar target at Omega=0 is invertible",
            "ell2_control_and_Einstein_minus_self_products": "L=2 and L=4 polar targets at Omega=0 are invertible",
            "cross_products_of_unequal_frequencies": "do not contribute at Omega=0",
            "conclusion": "every zero-frequency channel has a bounded algebraic correction; the homogeneous correction is zero",
        },
        "classification": {
            "direct_exceptional_zero_source_computed": True,
            "mixed_ell_normalization_repaired": True,
            "combined_homogeneous_zero_frequency_source_cancels": True,
            "all_other_zero_frequency_outputs_invertible": True,
            "complete_zero_frequency_source_solved": True,
            "complete_nonzero_frequency_polynomial_source_solved": False,
            "bounded_second_order_extension_certified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The corrected Einstein-minus amplitude cancels the full homogeneous source vector, not merely its constant-lapse pairing. Every other zero-frequency output is on an invertible polar target block. The remaining bounded gate consists only of the actual nonzero-frequency polynomial cross sources involving d and the added Einstein-minus oscillator.",
        "next_gate": "compute the d-times-Einstein-minus and all Einstein-minus cross-source time polynomials and test whether their off-shell inverses remain bounded",
        "claim_boundary": "This closes the complete zero-frequency source only on one axisymmetric pure-axial ellipse endpoint. It does not solve the nonzero-frequency polynomial sources, certify a bounded extension, assemble all m, treat nonzero momentum, or make causal, residual or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("stale exceptional ellipse zero-frequency source certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_ZERO_FREQUENCY_SOURCE: PASS")


if __name__ == "__main__":
    main()
