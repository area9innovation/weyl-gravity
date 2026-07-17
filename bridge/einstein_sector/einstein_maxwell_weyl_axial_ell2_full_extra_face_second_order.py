"""Second-order extension with both degenerate axial extra polarizations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.schema.json"
INPUTS = {
    "e1_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_zero_source_fixture.json",
    "e1_e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_e2_zero_source_fixture.json",
    "three_branch_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json",
    "balanced_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
}


class FullExtraFaceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FullExtraFaceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in values])


def _source_rank(records: dict[str, Any]) -> dict[str, Any]:
    previous = records["three_branch_face"]["raw_amplitude_balance"]
    old_vectors = {
        name: _vector(values)
        for name, values in previous["zero_source_vectors_E00_E11_E22_Maxwell1"].items()
    }
    e1 = _vector(records["e1_self"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"])
    cross = _vector(records["e1_e2"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"])
    direction = sp.Matrix([1, 0, sp.Rational(1, 2), 0])
    tau = {
        "plus": old_vectors["plus"][0],
        "extra_e1": e1[0],
        "extra_e2": old_vectors["extra"][0],
        "minus": old_vectors["minus"][0],
    }
    for name, vector in {
        "plus": old_vectors["plus"],
        "extra_e1": e1,
        "extra_e2": old_vectors["extra"],
        "minus": old_vectors["minus"],
    }.items():
        _require(sp.simplify(vector - tau[name] * direction) == sp.zeros(4, 1), f"{name} source direction changed")
    _require(cross == sp.zeros(4, 1), "degenerate extra interference source changed")
    _require(tau["minus"] > 0 and all(tau[name] < 0 for name in ("plus", "extra_e1", "extra_e2")), "source signs changed")

    gram = records["axial_pairing"]["pairing"]["normalized_Gram"]
    k, omega, lam = sp.symbols("k omega lambda", real=True)
    local = {"k": k, "omega": omega, "lambda": lam, "lam": lam}
    gram_matrix = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=local) for value in row]
            for row in gram
        ]
    ).subs({k: 0, lam: 6, omega: 4 / sp.sqrt(3)})
    _require(gram_matrix[0, 1] == 0, "k=0 extra Gram interference changed")
    _require(sp.simplify(tau["extra_e1"] / tau["extra_e2"] - gram_matrix[0, 0] / gram_matrix[1, 1]) == 0, "source/Gram ratio mismatch")

    x_plus, x_e1, x_e2 = sp.symbols("x_plus x_e1 x_e2", nonnegative=True, real=True)
    x_minus = sp.factor(
        -(
            tau["plus"] * x_plus
            + tau["extra_e1"] * x_e1
            + tau["extra_e2"] * x_e2
        )
        / tau["minus"]
    )
    remainder = sp.simplify(
        tau["plus"] * x_plus
        + tau["extra_e1"] * x_e1
        + tau["extra_e2"] * x_e2
        + tau["minus"] * x_minus
    )
    _require(remainder == 0, "four-branch balance changed")
    return {
        "source_row_direction": [str(value) for value in direction],
        "Taub_source_coefficients": {name: str(value) for name, value in tau.items()},
        "extra_internal_Hermitian_source_matrix": [
            [str(tau["extra_e1"]), "0"],
            ["0", str(tau["extra_e2"])],
        ],
        "extra_interference_source": [str(value) for value in cross],
        "extra_source_matrix_rank": 2,
        "spacetime_row_rank": 1,
        "source_matrix_proportional_to_extra_Lee_Wald_Gram": True,
        "parameters": "x_plus,x_e1,x_e2>=0, not all zero; arbitrary constant complex phases",
        "x_minus": str(x_minus),
        "balanced_remainder": str(remainder),
        "homogeneous_zero_source_cancels_on_entire_face": True,
    }


def _homogeneous_nonzero_compatibility(record: dict[str, Any]) -> dict[str, Any]:
    Omega = sp.symbols("Omega", nonzero=True, real=True)
    matrix = sp.Matrix(
        [
            [sp.sympify(value, locals={"Omega": Omega, "I": sp.I}) for value in row]
            for row in record["homogeneous_operator"]["matrix"]
        ]
    )
    left_null = matrix.T.nullspace()
    _require(matrix.rank() == 2 and len(left_null) == 2, "homogeneous nonzero rank changed")
    expected = [sp.Matrix([1, 0, 0, 0]), sp.Matrix([0, sp.Rational(1, 2), 1, 0])]
    # Compare subspaces without relying on basis normalization.
    null_matrix = sp.Matrix.hstack(*left_null)
    for vector in expected:
        _require(null_matrix.row_join(vector).rank() == null_matrix.rank(), "homogeneous left-null basis changed")
    return {
        "operator_rank_for_Omega_nonzero": 2,
        "left_null_conditions": ["S_E00=0", "S_E11/2+S_E22=0"],
        "quadratic_Noether_reason": "the exact target Noether identity N(Phi)E(Phi)=0 gives N^(0)S^(2)=0 for every pair of on-shell first-order modes; at Omega!=0 these two conditions are precisely the left-null conditions",
        "image_equals_Noether_kernel": True,
        "consequence": "every actual nonzero-frequency homogeneous source, including channels containing e1, has an algebraic correction",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["e1_self"]["case"] == "e1_self", "e1 fixture changed")
    _require(records["e1_e2"]["case"] == "e1_e2", "e1/e2 fixture changed")
    _require(records["three_branch_face"]["classification"]["two_parameter_positive_quadrant_face_second_order_extendible"], "prior face changed")
    source_rank = _source_rank(records)
    compatibility = _homogeneous_nonzero_compatibility(records["balanced_source"])
    old_ledger = records["three_branch_face"]["nonzero_frequency_channel_ledger"]
    _require(len(old_ledger) == 9, "frequency ledger changed")
    for channel in old_ledger.values():
        for output in channel["generic_polar_outputs"].values():
            _require(output["p_shell_witness"]["certified_nonzero"], "p resonance changed")
            _require(output["q_shell_witness"]["certified_nonzero"], "q resonance changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-ell2-full-extra-face-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_FULL_EXTRA_FACE_SECOND_ORDER",
        "result_state": "THREE_PARAMETER_AXISYMMETRIC_AXIAL_FACE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_ELL2_M0_AXIAL_BOTH_EXTRA_POLARIZATIONS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "real axial ell=2,m=0,k=0 tangents spanning Einstein-plus, both degenerate extra p-primary representatives, and Einstein-minus",
        "zero_frequency_source_rank": source_rank,
        "nonzero_homogeneous_channels": compatibility,
        "angular_and_frequency_closure": {
            "axisymmetric_product": "two m=0 ell=2 axial modes produce only even polar L=0,2,4 outputs; odd L Clebsch-Gordan coefficients vanish",
            "frequency_set": "adding e1 creates no new output frequencies because e1 and e2 share omega_extra",
            "nine_frequency_types_inherited": True,
            "ell2_ell4_p_and_q_nonresonance_inherited": True,
            "zero_frequency_ell2_ell4_invertible": True,
        },
        "second_order_correction": {
            "homogeneous_zero": "zero after the displayed H balance",
            "homogeneous_nonzero": "exists by exact image=Noether-kernel equality",
            "polar_ell2_ell4": "unique exact inverse at zero and every inherited nonzero frequency",
            "real_reconstruction": "multiply bilinear channel corrections by the chosen complex amplitudes and add conjugates",
            "complete_for_declared_face": True,
        },
        "classification": {
            "both_axial_extra_polarizations_included": True,
            "three_parameter_positive_cone_second_order_extendible": True,
            "arbitrary_constant_relative_phases_allowed": True,
            "all_m_promoted": False,
            "polar_input_parity_classified": False,
            "general_ell_classified": False,
            "opposite_momentum_phase_source_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The second axial extra polarization does not cut the Paper-91 mixed cone. Its self-source lies on the same single spacetime cokernel ray, its interference source with the first extra polarization vanishes exactly, and its coefficient is proportional to the positive extra Lee-Wald Gram entry. The axisymmetric second-order cone therefore grows from two to three nonnegative parameters before overall scale and phases.",
        "next_gate": "compute odd-L zero-frequency channels for non-axisymmetric m data, then repeat the internal source-rank test in polar parity and at symbolic ell",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers both axial extra polarizations only on the ell=2,m=0,k=0 face. It does not promote all m, polar parity, general ell, standing-wave phases, all-orders solutions, or causal/quantum claims.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_extra_zero_source_fixture --case e1_self --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_zero_source_fixture.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_extra_zero_source_fixture --case e1_e2 --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_e2_zero_source_fixture.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"full-extra face certificate stale: {path}")


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
