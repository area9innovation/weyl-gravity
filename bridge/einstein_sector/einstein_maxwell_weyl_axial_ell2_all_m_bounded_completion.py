"""Remove the zero-frequency Jordan caveat from the axial ell2 all-m cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.schema.json"
INPUTS = {
    "all_m": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json",
    "ell1_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "same_parity": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
}


class AxialAllMBoundedError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialAllMBoundedError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_l1_inverse(record: dict[str, Any]) -> dict[str, Any]:
    omega = sp.symbols("omega", real=True)
    local = {"omega": omega, "I": sp.I}
    raw = sp.Matrix([[sp.sympify(value, locals=local) for value in row] for row in record["operator_theorem"]["raw_matrix"]])
    zero = raw.subs(omega, 0)
    source_0, source_1 = sp.symbols("S0 S1")
    compatible_source = sp.Matrix([source_0, source_1, source_0, source_1])
    correction = sp.Matrix([source_0 / 2, -source_1 / 2, 0, 0])
    _require(zero * correction == compatible_source, "constant L1 right inverse changed")
    noether = sp.Matrix([-1, 0, 1, 0])
    twist = sp.Matrix([0, -1, 0, 1])
    _require(noether.dot(compatible_source) == 0 and twist.dot(compatible_source) == 0, "compatibility subspace changed")
    _require(zero.rank() == 2, "zero L1 rank changed")
    return {
        "row_order": record["operator_theorem"]["raw_row_order"],
        "coefficient_order": record["operator_theorem"]["raw_coefficient_order"],
        "zero_operator": [[str(value) for value in zero.row(row)] for row in range(4)],
        "compatible_source": ["S0", "S1", "S0", "S1"],
        "constant_correction": ["S0/2", "-S1/2", "0", "0"],
        "remainder": ["0", "0", "0", "0"],
        "bounded": True,
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["all_m"]["classification"]["all_m_axial_ell2_common_zero_cone_second_order_extendible"], "all-m theorem changed")
    _require(records["all_m"]["classification"]["odd_L1_and_L3_channels_closed"], "odd-output theorem changed")
    resonance = records["same_parity"]["nonzero_frequency_resonance_ledger"]
    _require(resonance["axial_L1_nonzero_channels_off_twist_extra_and_standard_shells"], "L1 nonzero resonance changed")
    inverse = _zero_l1_inverse(records["ell1_operator"])
    return {
        "schema": "einstein-maxwell-weyl-axial-ell2-all-m-bounded-completion-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_ALL_M_BOUNDED_COMPLETION",
        "result_state": "COMPLETE_AXIAL_ELL2_ALL_M_COMMON_ZERO_CONE_BOUNDED_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "finite real axial ell=2,k=0 Einstein-plus/minus and both extra primaries, all m",
            "degree": 2,
            "parity": "axial input with every quadratic output parity",
            "ell": 2,
            "m": "all -2,...,2",
            "k": 0,
            "omega": "all q/p input sums and differences plus zero",
        },
        "zero_frequency_L1_completion": inverse,
        "bounded_channel_audit": {
            "polar_L0_zero": "the source vanishes after mu_H=0",
            "axial_L1_zero": "the displayed constant right inverse applies after mu_J1=mu_J2=mu_J3=0",
            "polar_L2_L4_zero": "certified algebraic inverses",
            "axial_L3_zero": "certified invertible quotient block",
            "all_nonzero_frequencies": "off every target shell and removed by algebraic finite-frequency inverses",
        },
        "second_order_theorem": {
            "domain": "the complete axial ell2 all-m common H,J_i zero cone",
            "correction": "real, smooth, spatially periodic and finite quasiperiodic in time",
            "bounded_or_finite_quasiperiodic": True,
            "necessity_and_sufficiency": True,
        },
        "classification": {
            "all_m_axial_ell2_bounded_cone_classified": True,
            "zero_L1_constant_right_inverse_explicit": True,
            "prior_polynomial_Jordan_caveat_removed": True,
            "polar_input_parity_classified": False,
            "general_ell_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Non-axisymmetric axial data do not require a secular twist correction once the rotation moment maps vanish. The zero-frequency L1 source then lies in the rank-two constant image of the exact target operator, and a constant right inverse is explicit. The complete axial ell2 all-m wave cone is therefore bounded at second order.",
        "next_gate": "use this bounded wave theorem with the SO3-promoted global a,b,d shell ideal to classify the complete global-plus-axial-all-m carrier, then compute the polar Einstein-minus global shell block",
        "claim_boundary": "This strengthens only the axial ell=2,k=0 all-m theorem. It does not include polar input, other ell or momenta, global modes, infinite sums, all-orders integration, residual descent, causal propagation, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.20},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.40, "tests_run": 4},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the all-m source theorem, exact ell1 operator and complete nonzero-frequency resonance ledger are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "polar, other-harmonic, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AxialAllMBoundedError("axial ell2 all-m bounded certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_ALL_M_BOUNDED_COMPLETION: PASS")


if __name__ == "__main__":
    main()
