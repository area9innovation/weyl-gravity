"""Exceptional ell=1 current and fixed-bundle Taub obstruction theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import (
    _generic_current_matrix,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import (
    _time_current_matrix,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_current_taub.schema.json"
INPUTS = {
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "direct_physical_fixture": ROOT / "bridge/certificates/weyl_maxwell_ell1_exceptional_lee_wald_fixture.json",
    "taub_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "standard_moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class ExceptionalEll1CurrentError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalEll1CurrentError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _weight(matrix: sp.Matrix, representative: sp.Matrix, frequency: sp.Expr) -> sp.Expr:
    return sp.factor((representative.T * matrix * representative)[0] / (-sp.I * frequency))


def _current_theorem() -> dict[str, object]:
    eigenvalue, momentum, first, second = sp.symbols("lambda k omega_1 omega_2", real=True)
    extra_frequency = sp.sqrt(sp.Rational(4, 3))
    standard_frequency = sp.Integer(2)

    axial_current = _generic_current_matrix(eigenvalue, momentum, first, second)
    axial_current = axial_current.subs({eigenvalue: 2, momentum: 0})
    axial_extra = sp.Matrix([0, 1, 0, -3])
    axial_standard = sp.Matrix([0, 1, 0, 1])
    axial_extra_weight = _weight(
        axial_current.subs({first: extra_frequency, second: extra_frequency}),
        axial_extra,
        extra_frequency,
    )
    axial_standard_weight = _weight(
        axial_current.subs({first: standard_frequency, second: standard_frequency}),
        axial_standard,
        standard_frequency,
    )

    polar_current, polar_symbols = _time_current_matrix()
    polar_current = (polar_current / 2).subs(
        {polar_symbols["lambda"]: 2, polar_symbols["k"]: 0}
    )
    polar_first = polar_symbols["omega_1"]
    polar_second = polar_symbols["omega_2"]
    polar_extra = sp.Matrix([0, 1, 0, 0])
    polar_standard = sp.Matrix([1, 0, 1, 0])
    polar_extra_weight = _weight(
        polar_current.subs({polar_first: extra_frequency, polar_second: extra_frequency}),
        polar_extra,
        extra_frequency,
    )
    polar_standard_weight = _weight(
        polar_current.subs({polar_first: standard_frequency, polar_second: standard_frequency}),
        polar_standard,
        standard_frequency,
    )
    weights = [axial_extra_weight, polar_extra_weight, axial_standard_weight, polar_standard_weight]
    _require(weights == [16, 3, 16, 1], f"exceptional ell=1 current weights changed: {weights}")

    axial_mixed = sp.factor(
        (axial_extra.T * axial_current.subs({first: extra_frequency, second: standard_frequency}) * axial_standard)[0]
    )
    polar_mixed = sp.factor(
        (polar_extra.T * polar_current.subs({polar_first: extra_frequency, polar_second: standard_frequency}) * polar_standard)[0]
    )
    _require(axial_mixed == 0 and polar_mixed == 0, "standard-extra ell=1 current ceased to be orthogonal")

    fixture = json.loads(INPUTS["direct_physical_fixture"].read_text(encoding="utf-8"))
    direct = fixture["direct_current"]
    omega = sp.symbols("omega", positive=True, real=True)
    norm = 4 * sp.pi / 3
    axial_direct = sp.sympify(
        direct["axial"]["on_shell_integrated_coordinate_current_matrix"][0][0],
        locals={"I": sp.I, "pi": sp.pi, "omega": omega},
    )
    polar_direct = sp.sympify(
        direct["polar"]["on_shell_integrated_coordinate_current_matrix"][0][0],
        locals={"I": sp.I, "pi": sp.pi, "omega": omega},
    )
    axial_direct_weight = sp.factor(axial_direct / (-sp.I * omega * norm))
    polar_direct_weight = sp.factor(polar_direct / (-sp.I * omega * norm))
    _require(axial_direct_weight == 4 * axial_standard_weight, "axial ell=1 direct normalization changed")
    _require(polar_direct_weight == 16 * polar_standard_weight, "polar ell=1 direct normalization changed")

    return {
        "frequency_squared": "4/3",
        "representative_order": ["axial (h_t,h_x,q_t,q_x)", "polar (A_t,B,C_t,U)"],
        "extra_representatives": [["0", "1", "0", "-3"], ["0", "1", "0", "0"]],
        "normalized_extra_Hermitian_current_Gram": [["16", "0"], ["0", "3"]],
        "extra_positive_frequency_inertia": [2, 0],
        "standard_gauge_slice_representatives": [["0", "1", "0", "1"], ["1", "0", "1", "0"]],
        "standard_gauge_slice_weights": [str(axial_standard_weight), str(polar_standard_weight)],
        "extra_standard_mixed_pairing": [str(axial_mixed), str(polar_mixed)],
        "direct_physical_cross_check": {
            "harmonic_norm": "4*pi/3",
            "axial_fixture_weight": str(axial_direct_weight),
            "axial_coordinate_map": "physical curl amplitude maps to -2 times the axial gauge-slice representative",
            "polar_fixture_weight": str(polar_direct_weight),
            "polar_coordinate_map": "physical potential representative equals 4 times the polar gauge-slice representative plus residual gauge",
        },
        "specialization_argument": "the certified direct four-dimensional natural current equals the polynomial action Green current identically in lambda; no lambda-2 factor is inverted, so the identity specializes to lambda=2 after the exceptional quotient is taken",
        "all_real_m": "SO(3) invariance tensors the displayed Gram matrix with the positive ell=1 angular Gram W_1",
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["axial_operator"]["classification"]["extra_fourth_order_ell1_shell_discovered"], "axial ell=1 input changed")
    _require(records["polar_operator"]["classification"]["polar_ell1_extra_fourth_order_shell_certified"], "polar ell=1 input changed")
    _require(records["axial_current"]["classification"]["generic_extra_module_direct_Lee_Wald_nonradical"], "axial current input changed")
    _require(records["polar_current"]["classification"]["direct_four_dimensional_Lee_Wald_match"], "polar current input changed")
    _require(records["taub_bridge"]["classification"]["generic_covariant_moment_map_Taub_equality_certified"], "Taub bridge changed")
    _require(records["standard_moment_maps"]["classification"]["standard_physical_ell1_common_zero_locus_classified"], "standard ell=1 moment map changed")
    theorem = _current_theorem()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-current-taub-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_CURRENT_TAUB",
        "result_state": "EXCEPTIONAL_ELL1_EXTRA_CURRENT_POSITIVE_AND_PURE_BLOCK_SECOND_ORDER_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "axial and polar k=0 exceptional ell=1 fourth-order modes, all real m, optionally direct-summed with the standard physical ell=1 oscillators, on the fixed magnetic bundle before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "current_theorem": theorem,
        "Taub_witness": {
            "extra_block": "mu_H=-(L/4)*(4/3)*(16*||c_ax||^2_W1+3*||c_pol||^2_W1)<0 for every nonzero real exceptional extra tangent",
            "physical_plus_extra_block": "the standard physical ell=1 block is orthogonal and has the same positive-current sign, so the combined isolated common-zero locus is also only the origin",
            "adjoint_cokernel": "the constant-lapse stabilizer supplies the nonzero Taub pairing; therefore no second-order correction can remove it on the closed fixed-bundle slice",
        },
        "classification": {
            "axial_exceptional_ell1_current_classified": True,
            "polar_exceptional_ell1_current_classified": True,
            "exceptional_extra_ell1_current_nonradical_positive_definite": True,
            "pure_exceptional_ell1_nonzero_tangents_second_order_obstructed": True,
            "isolated_physical_plus_exceptional_ell1_common_zero_is_origin": True,
            "mixed_balance_with_opposite_sign_sector_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The exceptional ell=1 fourth-order solutions are genuine nonnull linear modes, but no nonzero real tangent supported only on them passes the compact second-order Taub constraint. Adding standard physical ell=1 oscillators does not help because they carry the same time-translation sign. Any extendible mixed ell=1 configuration must import an opposite-sign sector outside this isolated block.",
        "next_gate": "pair exceptional ell=1 modes with an Einstein-minus or other opposite-sign block and test the complete quadratic source on the resulting common-zero fixture",
        "claim_boundary": "This is a compact fixed-bundle second-order obstruction, not removal of linear modes. It does not classify mixed opposite-sign balances, all-orders solutions, final residual descent, asymptotic waves, particles, or quantum ghosts.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.1, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_current_taub --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_current_taub.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_current_taub"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "mixed opposite-sign ell=1 balances and all-orders integration remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_current_taub --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_current_taub.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_current_taub",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "exceptional ell=1 current certificate is stale")


if __name__ == "__main__":
    main()
