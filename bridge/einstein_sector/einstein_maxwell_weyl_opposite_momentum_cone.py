"""Exact common moment-map cone for paired opposite compact momenta."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    _rotation_representation,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_cone.schema.json"
INPUTS = {
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
}


class OppositeMomentumConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OppositeMomentumConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cone_theorem() -> dict[str, Any]:
    return {
        "domain": "one physical ell>=2 and one nonzero allowed |k|=2*pi*|n|/L, with independent positive-frequency amplitudes at +k and -k",
        "density_matrices": {
            "rho_plus^sigma": "positive semidefinite, rank<=2",
            "rho_extra^sigma": "positive semidefinite, rank<=4",
            "rho_minus^sigma": "positive semidefinite, rank<=2",
            "sigma": "+ or - labels the sign of compact momentum",
        },
        "moments": {
            "A_s^sigma": "tr(rho_s^sigma)",
            "j_s,a^sigma": "tr(rho_s^sigma*T_ell,a)",
        },
        "common_zero_equations": {
            "H": "sum_s eta_s*omega_s^2*(A_s^+ + A_s^-)=0",
            "P_x": "k*sum_s eta_s*omega_s*(A_s^+ - A_s^-)=0",
            "J_a": "sum_s eta_s*omega_s*(j_s,a^+ + j_s,a^-)=0 for a=1,2,3",
            "signs": "eta_plus=eta_extra=+1, eta_minus=-1",
        },
        "classification": "The complete common-zero cone in the paired fixed-(ell,|k|) block is exactly the inverse image of these five linear equations in the product of the six displayed positive-semidefinite rank strata.",
        "reconstruction": "Every density satisfying the rank bounds factors as C^dagger*C and reconstructs positive-frequency amplitudes. Reality supplies the conjugate negative-frequency coefficients.",
        "strict_extension_of_single_travelling_result": "A single nonzero-k travelling block has only the origin, but paired opposite momenta permit nonzero cancellation of P_x.",
    }


def _standing_subcone() -> dict[str, Any]:
    regressions: dict[str, Any] = {}
    a_plus, a_extra = sp.symbols("a_plus a_extra", nonnegative=True, real=True)
    for ell in range(2, 9):
        lam = sp.Integer(ell * (ell + 1))
        for momentum_squared in (sp.Integer(1), sp.Integer(4), sp.Rational(9, 4)):
            w_minus_sq = momentum_squared + lam - sp.sqrt(2 * lam)
            w_extra_sq = momentum_squared + lam - sp.Rational(2, 3)
            w_plus_sq = momentum_squared + lam + sp.sqrt(2 * lam)
            a_minus = sp.factor(
                (w_plus_sq * a_plus + w_extra_sq * a_extra) / w_minus_sq
            )
            energy = sp.simplify(
                w_plus_sq * a_plus + w_extra_sq * a_extra - w_minus_sq * a_minus
            )
            _require(energy == 0, "standing energy balance changed")
            representation = _rotation_representation(ell)
            vector = sp.zeros(2 * ell + 1, 1)
            vector[ell] = 1
            angular = representation["angular_form"]
            for generator in ("J0", "Jplus", "Jminus"):
                _require(
                    sp.simplify((vector.T * angular * representation[generator] * vector)[0]) == 0,
                    "standing m=0 rotation expectation changed",
                )
            regressions[f"ell={ell},k2={momentum_squared}"] = str(energy)
    return {
        "definition": "rho_s^+=rho_s^- for every branch s; this is the phase-insensitive standing-wave density condition",
        "P_x": "0 identically",
        "neutral_rank_one_face": "rho_s^+=rho_s^-=a_s*|ell,0><ell,0|",
        "parameters": "a_plus,a_extra>=0, not both zero",
        "balance": "a_minus=(omega_plus^2*a_plus+omega_extra^2*a_extra)/omega_minus^2",
        "all_five_moment_maps": "zero",
        "dimension_before_scale_and_phases": 2,
        "warning": "Equal densities do not require pointwise equality of the +k and -k amplitude matrices; relative internal phases are invisible to stabilizer charges but can affect the quadratic source.",
        "exact_regressions": regressions,
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["moment_map_bridge"]["classification"]["generic_H_Px_J_selection_rules_certified"],
        "moment-map selection rules changed",
    )
    _require(
        records["k0_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"],
        "k=0 density-cone input changed",
    )
    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-cone-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_COMMON_ZERO_CONE",
        "result_state": "PAIRED_OPPOSITE_MOMENTUM_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_FIXED_ELL_AND_NONZERO_ABSOLUTE_MOMENTUM",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "paired_density_cone_theorem": _cone_theorem(),
        "standing_wave_subcone": _standing_subcone(),
        "classification": {
            "complete_fixed_ell_absolute_k_common_zero_cone_classified": True,
            "nonzero_standing_wave_subcone_constructed": True,
            "single_travelling_block_no_go_preserved": True,
            "relative_phase_quadratic_source_classified": False,
            "cross_absolute_k_cancellations_classified": False,
            "exceptional_global_blocks_classified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "Opposite travelling waves reopen the Taub-zero locus at nonzero momentum. Equal +k/-k branch densities cancel compact momentum exactly, after which the same negative Einstein-minus direction balances the positive Einstein-plus and extra occupations. This is a charge-cone theorem, not yet a second-order extension theorem, because the source sees phases that the density moment maps forget.",
        "next_gate": "evaluate the full quadratic source on the standing-wave face as a function of the relative +k/-k phases, then join compatible fibres across distinct |k|",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE result classifies a fixed-(ell,|k|) paired-momentum common-zero cone. It does not prove quadratic-source solvability, classify cancellations between distinct |k|, include exceptional/global modes, or establish causal or quantum physics.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_cone --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_cone",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"opposite-momentum certificate stale: {path}")


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
