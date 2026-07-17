"""Parity-neutral output and resonance ledger for same-parity ell=2 products."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.physics.wigner import wigner_3j


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_same_parity_output_resonance.schema.json"
INPUTS = {
    "full_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json",
    "axial_ell1_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
}


class Ell2SameParityOutputError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Ell2SameParityOutputError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def _nonzero(value: sp.Expr) -> dict[str, Any]:
    z = sp.symbols("z")
    polynomial = sp.Poly(sp.minpoly(value, z), z)
    _require(polynomial.TC() != 0, f"algebraic value vanished: {value}")
    return {
        "value": str(sp.factor(value)),
        "minimal_polynomial": str(polynomial.as_expr()),
        "nonzero_constant_term": str(polynomial.TC()),
        "certified_nonzero": True,
    }


def _angular_selection() -> dict[str, Any]:
    couplings: dict[str, Any] = {}
    for output_ell in range(5):
        witnesses = []
        for m1 in range(-2, 3):
            for m2 in range(-2, 3):
                total_m = m1 + m2
                if abs(total_m) > output_ell:
                    continue
                value = wigner_3j(2, 2, output_ell, m1, m2, -total_m)
                if value != 0:
                    witnesses.append([m1, m2, total_m, str(value)])
        _require(bool(witnesses), f"L={output_ell} coupling disappeared")
        couplings[str(output_ell)] = {
            "target_parity": "polar" if output_ell % 2 == 0 else "axial",
            "nonzero_witness": witnesses[0],
        }
    return {
        "tensor_product": "V_2 tensor V_2 = V_0+V_1+V_2+V_3+V_4",
        "scope": "same-parity axial-axial or polar-polar ell=2 input",
        "parity_rule": "the quadratic product has even spatial parity, hence polar even-L and axial odd-L outputs",
        "output_blocks": couplings,
        "axisymmetric_specialization": "m1=m2=0 kills odd L",
    }


def _resonance_ledger(records: dict[str, Any]) -> dict[str, Any]:
    three_branch_input = records["full_extra_face"]["provenance"]["inputs"]["three_branch_face"]
    three_branch = json.loads((ROOT / three_branch_input["path"]).read_text(encoding="utf-8"))
    frequencies = {
        name: _parse(channel["output_frequency"])
        for name, channel in three_branch["nonzero_frequency_channel_ledger"].items()
    }
    output: dict[str, Any] = {}
    for name, frequency in frequencies.items():
        squared = sp.factor(frequency**2)
        output[name] = {
            "frequency": str(frequency),
            "axial_L1": {
                "Omega": _nonzero(frequency),
                "Omega_squared_minus_4_over_3": _nonzero(squared - sp.Rational(4, 3)),
                "Omega_squared_minus_4": _nonzero(squared - 4),
            },
            "axial_L3": {
                "p": _nonzero(sp.factor(squared - (12 - sp.Rational(2, 3)))),
                "q": _nonzero(sp.factor((squared - 12) ** 2 - 24)),
            },
        }
    _require(len(output) == 9, "same-parity frequency type count changed")
    return {
        "nine_nonzero_frequency_types": output,
        "axial_L1_nonzero_channels_off_twist_extra_and_standard_shells": True,
        "axial_L3_nonzero_channels_off_p_and_q_shells": True,
        "axial_L3_zero_channel": {"p": "-34/3", "q": "120", "invertible": True},
        "polar_L2_L4": "exact p/q nonresonance and zero-frequency inverses imported from the full-extra face",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    ell1 = records["axial_ell1_operator"]
    _require(ell1["classification"]["extra_fourth_order_ell1_shell_discovered"], "axial L1 shell audit changed")
    zero_fibre = ell1["operator_theorem"]["zero_frequency_fibre"]
    _require(zero_fibre["left_cokernel_dimension"] == 2, "axial L1 zero cokernel changed")
    return {
        "schema": "einstein-maxwell-weyl-ell2-same-parity-output-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_SAME_PARITY_OUTPUT_RESONANCE",
        "result_state": "PARITY_NEUTRAL_SAME_PARITY_ELL2_OUTPUT_AND_RESONANCE_LEDGER_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_ELL2_K0_SAME_PARITY_OUTPUT_LEDGER",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "all angular and sum/difference-frequency output blocks common to pure axial and pure polar ell=2,k=0 quadratic inputs",
        "angular_selection": _angular_selection(),
        "zero_output_blocks": {
            "polar_L0": "constant-lapse pairing; source-specific H cancellation remains in each input theorem",
            "axial_L1": {
                "universal_Noether_rows": 1,
                "physical_cokernel_per_real_M": 1,
                "physical_pairing": "rotation moment map mu_JM",
            },
            "polar_L2_L4": "invertible",
            "axial_L3": "invertible because p=-34/3 and q=120",
        },
        "nonzero_frequency_resonance_ledger": _resonance_ledger(records),
        "classification": {
            "same_parity_output_selection_certified": True,
            "all_nine_nonzero_frequency_types_off_target_shells": True,
            "axial_and_polar_input_theorems_may_share_this_ledger": True,
            "axial_polar_cross_parity_covered": False,
            "general_ell_covered": False,
        },
        "interpretation": "The angular and resonance part of the ell=2 proof depends only on the common branch frequencies and the even parity of a same-parity quadratic product. It is therefore shared by axial-axial and polar-polar inputs; only their homogeneous source matrices differ.",
        "next_gate": "construct the odd-total-parity axial-polar output ledger, beginning with the exceptional polar L=1 operator",
        "claim_boundary": "This certificate does not contain an input-sector homogeneous source cancellation and does not cover axial-polar cross terms, general ell, opposite momentum, all-orders integration, causal propagation, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_same_parity_output_resonance --verify bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_same_parity_output_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_same_parity_output_resonance",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"same-parity output certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
