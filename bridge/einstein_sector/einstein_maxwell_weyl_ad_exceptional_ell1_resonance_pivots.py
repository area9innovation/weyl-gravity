"""Certify the full-time a,d adjoint pivots on exceptional ell=1 modes."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_ad_exceptional_ell1_source_explore import (
    axial_source,
    polar_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.schema.json"
INPUTS = {
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "standard_global_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "exceptional_L1_nonresonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance.json",
}


class ExceptionalADPivotError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalADPivotError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compute(case: tuple[str, str]) -> tuple[str, str, sp.Matrix]:
    parity, global_case = case
    producer = {"axial": axial_source, "polar": polar_source}[parity]
    return parity, global_case, producer(global_case)


def _direct_sources() -> dict[str, dict[str, sp.Matrix]]:
    cases = [(parity, global_case) for parity in ("axial", "polar") for global_case in ("a", "d")]
    with ProcessPoolExecutor(max_workers=4) as executor:
        values = list(executor.map(_compute, cases))
    result = {"axial": {}, "polar": {}}
    for parity, global_case, source in values:
        result[parity][global_case] = source.applyfunc(sp.factor)
    time = sp.symbols("t", real=True)
    expected = {
        "axial": {
            "a": sp.Matrix([0, 2 * sp.I * (sp.sqrt(3) * time - 21 * sp.I) / 3, 0, 2 * sp.I * (sp.sqrt(3) * time + sp.I)]),
            "d": sp.Matrix([0, sp.sqrt(3) * sp.I / 3, 0, sp.sqrt(3) * sp.I]),
        },
        "polar": {
            "a": sp.Matrix([0, -sp.I * (2 * sp.sqrt(3) * time - 3 * sp.I), 0, 0]),
            "d": sp.Matrix([0, -sp.sqrt(3) * sp.I, 0, 0]),
        },
    }
    for parity in expected:
        for global_case in expected[parity]:
            _require(
                (result[parity][global_case] - expected[parity][global_case]).applyfunc(sp.simplify) == sp.zeros(4, 1),
                f"{parity} {global_case} direct source changed",
            )
    return result


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["axial_operator"]["operator_theorem"]["primary_shells"]["extra_fourth_order"] == "omega^2=4/3", "axial exceptional shell changed")
    _require(records["polar_operator"]["operator_theorem"]["physical_shells"]["fourth_order"]["omega_squared"] == "4/3", "polar exceptional shell changed")
    _require("B=0" in records["standard_global_bounded"]["universal_complete_carrier_corollary"]["statement"], "universal twist-velocity elimination changed")
    _require(records["exceptional_L1_nonresonance"]["classification"]["no_exceptional_L1_output_resonance"], "generic L1 nonresonance changed")

    sources = _direct_sources()
    witnesses = {
        "axial": sp.Matrix([0, -sp.Rational(1, 3), 0, 1]),
        "polar": sp.Matrix([0, 1, 0, 0]),
    }
    projected = {
        parity: {
            global_case: sp.factor((witnesses[parity].T * sources[parity][global_case])[0])
            for global_case in ("a", "d")
        }
        for parity in ("axial", "polar")
    }
    expected_projected = {
        "axial": {
            "a": 4 * sp.I * (4 * sp.sqrt(3) * sp.symbols("t", real=True) + 15 * sp.I) / 9,
            "d": 8 * sp.sqrt(3) * sp.I / 9,
        },
        "polar": {
            "a": -sp.I * (2 * sp.sqrt(3) * sp.symbols("t", real=True) - 3 * sp.I),
            "d": -sp.sqrt(3) * sp.I,
        },
    }
    for parity in projected:
        for global_case in projected[parity]:
            _require(sp.simplify(projected[parity][global_case] - expected_projected[parity][global_case]) == 0, f"{parity} {global_case} projection changed")

    return {
        "schema": "einstein-maxwell-weyl-ad-exceptional-ell1-resonance-pivots-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AD_EXCEPTIONAL_ELL1_RESONANCE_PIVOTS",
        "result_state": "FULL_TIME_A_D_TIMES_EXCEPTIONAL_ELL1_ADJOINT_PIVOTS_CERTIFIED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic compatibility",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "radion position a or circumference velocity d crossed with one exceptional ell=1 extra-primary mode",
            "degree": 2,
            "parity": "axial and polar kept separate",
            "ell": "0 x 1 -> 1",
            "m": "m=0 direct fixture; every m by SO3 multiplicity one",
            "k": 0,
            "omega": "omega_exceptional^2=4/3",
        },
        "action_row_order": {
            "axial": ["2*metric_t", "-2*metric_x", "maxwell_t", "maxwell_x"],
            "polar": ["-metric_00", "2*metric_01", "-metric_11", "4*maxwell_phi"],
        },
        "exceptional_representatives": {
            "axial_Ht_Hx_Qt_Qx": ["0", "1", "0", "-3"],
            "polar_At_B_Ct_U": ["0", "1", "0", "0"],
        },
        "adjoint_witnesses": {parity: [str(value) for value in witness] for parity, witness in witnesses.items()},
        "direct_source_rows": {
            parity: {global_case: [str(sp.factor(value)) for value in sources[parity][global_case]] for global_case in ("a", "d")}
            for parity in ("axial", "polar")
        },
        "projected_adjoint_polynomials": {
            parity: {global_case: str(projected[parity][global_case]) for global_case in ("a", "d")}
            for parity in ("axial", "polar")
        },
        "polynomial_consequences": {
            "a_leading_coefficients": {"axial": "16*sqrt(3)*I/9", "polar": "-2*sqrt(3)*I"},
            "d_coefficients_after_a_zero": {"axial": "8*sqrt(3)*I/9", "polar": "-sqrt(3)*I"},
            "one_isolated_exceptional_mode": "bounded compatibility forces a=0 and then d=0 for every nonzero axial or polar exceptional coefficient when no other L=1,omega_exceptional source is present",
            "all_m_promotion": "a and d are rotational scalars, so both nonzero pivots are scalar SO3 intertwiners on V_1",
        },
        "collision_ledger": {
            "generic_generic_pairs": "excluded at the exceptional L=1 roots by the imported cross-ell nonresonance theorem",
            "exceptional_times_ell2_extra_difference": "LIVE: omega_(ell2 extra)=2*omega_exceptional, so the difference channel returns omega_exceptional and can screen the constant d pivot",
            "a_time_degree": "the t coefficient cannot be supplied by a product of two stationary oscillators; after the universal b=B=0 conditions it forces a times every exceptional coefficient to vanish",
        },
        "classification": {
            "direct_axial_a_d_exceptional_sources_computed": True,
            "direct_polar_a_d_exceptional_sources_computed": True,
            "full_time_polynomial_dependence_retained": True,
            "a_times_exceptional_leading_pivot_nonzero_both_parities": True,
            "d_times_exceptional_constant_pivot_nonzero_both_parities": True,
            "all_m_by_SO3_equivariance": True,
            "exceptional_times_ell2_extra_difference_collision_open": True,
            "complete_exceptional_mixed_bounded_zero_locus_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The radion and circumference-velocity columns do not disappear on the exceptional dipole. The full-time source has a nonzero a*t pivot in both parities, followed by a nonzero d constant pivot. This removes a from every bounded mixed exceptional branch, but d can only be eliminated after the live exceptional-times-ell2-extra difference-frequency source is computed.",
        "next_gate": "compute the eight axial/polar exceptional-times-ell2-extra L=1 difference-frequency adjoint columns and solve them jointly with the d control column and the exceptional L=2 self-defect",
        "claim_boundary": "This is a direct coefficient theorem, not the complete exceptional mixed bounded cone. It does not assume away the live exceptional-times-ell2-extra difference collision, classify nonzero momentum, construct causal propagation, descend residual states, or make particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_source_helper": {
                "path": str(Path(axial_source.__code__.co_filename).resolve().relative_to(ROOT)),
                "sha256": _sha256(Path(axial_source.__code__.co_filename).resolve()),
            },
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots",
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
        raise ExceptionalADPivotError("exceptional a/d pivot certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_AD_EXCEPTIONAL_ELL1_RESONANCE_PIVOTS: PASS")


if __name__ == "__main__":
    main()
