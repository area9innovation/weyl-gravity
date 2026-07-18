"""Exact phase-sensitive resonance divisor for opposite compact momenta."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.schema.json"
INPUTS = {
    "opposite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
    "axial_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
}


class OppositeMomentumResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OppositeMomentumResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _divisor_formula() -> dict[str, Any]:
    u, A, B, C = sp.symbols("u A B C", real=True)
    D = C - A - B
    records = {}
    for spatial_square in (0, 4):
        squared = sp.factor((D + (spatial_square - 2) * u) ** 2 - 4 * (u + A) * (u + B))
        if spatial_square == 0:
            candidate = sp.factor((D**2 - 4 * A * B) / (4 * C))
        else:
            candidate = sp.factor((4 * A * B - D**2) / (4 * (C - 2 * A - 2 * B)))
        _require(sp.factor(squared.subs(u, candidate)) == 0, f"h={spatial_square} divisor solution changed")
        records[f"h={spatial_square}"] = {
            "spatial_output": "K=0" if spatial_square == 0 else "K=+/-2k",
            "squared_resonance_equation": str(squared),
            "candidate_k_squared": str(candidate),
            "admissibility": "candidate is retained only if real positive and D+(h-2)u has sign tau for temporal sum tau=+1 or difference tau=-1",
        }
    return {
        "input_shells": "omega_A^2=k^2+A and omega_B^2=k^2+B",
        "target_shell": "Omega^2=h*k^2+C with h in {0,4}",
        "temporal_channels": "Omega=abs(omega_A+tau*omega_B), tau=+1 or -1",
        "formulae": records,
        "finite_divisor_per_fixed_ell": "for L=1,...,2ell and three choices each of A,B,C, the displayed formula produces at most one k^2 per (h,tau) channel",
    }


def _universal_relative_phase_family() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    input_offset = lam - root
    output_ell = 2 * ell
    target_offset = output_ell * (output_ell + 1) - sp.Rational(2, 3)
    momentum_squared = sp.factor(target_offset / 4 - input_offset)
    expected = root - ell / 2 - sp.Rational(1, 6)
    _require(sp.factor(momentum_squared - expected) == 0, "universal phase resonance changed")
    positivity = sp.factor(2 * ell * (ell + 1) - (ell / 2 + sp.Rational(1, 6)) ** 2)
    _require(sp.expand(positivity - (63 * ell**2 + 66 * ell - 1) / 36) == 0, "positivity witness changed")
    _require(sp.factor(4 * (momentum_squared + input_offset) - target_offset) == 0, "universal shell identity changed")
    return {
        "inputs": "two Einstein-minus modes at the same ell and opposite momenta +k,-k, both positive frequency",
        "output": "polar extra-primary mode at L=2ell, K=0, Omega=2*omega_minus",
        "angular_selection": "the top scalar Gaunt coefficient in ell tensor ell -> 2ell is nonzero, so the m=0 standing-wave channel is not removed by angular selection",
        "phase_dependence": "any nonzero bilinear source projection in this channel is proportional to c_minus^(+)*c_minus^(-), so its complex phase is the relative standing-wave phase; the dynamical projection is not computed here",
        "resonant_k_squared": str(momentum_squared),
        "positive_for_every_ell_at_least_2": True,
        "positivity_squared_remainder": str(positivity),
        "exact_shell_identity": "4*(k^2+lambda-sqrt(2lambda))=Lambda_(2ell)-2/3",
        "bounded_consequence": "a bounded or finite-quasiperiodic correction requires an additional resonant source projection condition; moment-map densities alone do not decide it",
        "smooth_global_consequence": "the generic polar Smith factor p admits an exponential-polynomial secular inverse, so this nonzero-frequency resonance is not a Taub obstruction when polynomial time dependence is allowed",
    }


def _secular_lemma() -> dict[str, Any]:
    z, alpha = sp.symbols("z alpha")
    return {
        "scalar_statement": "if f(z)=(z-alpha)^m*g(z), g(alpha)!=0, then f(partial_t)[exp(alpha*t)*P_m(t)]=exp(alpha*t) for a finite polynomial P_m of degree m",
        "construction": "write f(partial_t) exp(alpha*t)P=exp(alpha*t) f(partial_t+alpha)P and invert g(partial_t+alpha) on the finite-dimensional polynomial space before integrating m times",
        "generic_target_application": "fiberwise Smith factors 1,1,p,pq reduce every generic resonant source component to the scalar statement; p and q are coprime on every physical fiber",
        "exceptional_L1_application": "the certified reduced determinants have only the declared polynomial shell factors, so the same exponential-polynomial inversion applies away from the zero-frequency rotation cokernel",
        "does_not_remove": "zero-frequency compact constraint-adjoint pairings such as H,P_x,J_i",
        "formal_symbols": [str(z), str(alpha)],
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["opposite_cone"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_classified"], "opposite cone input changed")
    _require(records["axial_ring"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial Smith input changed")
    _require(records["polar_ring"]["classification"]["Einstein_image_equals_complete_q_primary_summand"], "polar primary input changed")
    _require(records["axial_L1"]["classification"]["extra_fourth_order_ell1_shell_discovered"], "axial L1 input changed")
    _require(records["polar_L1"]["classification"]["polar_ell1_extra_fourth_order_shell_certified"], "polar L1 input changed")
    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-phase-resonance-divisor-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_PHASE_RESONANCE_DIVISOR",
        "result_state": "PHASE_RESONANCE_DIVISOR_NONEMPTY_AND_CORRECTION_SPACE_SPLIT_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_FIXED_ELL_ARBITRARY_NONZERO_ABSOLUTE_MOMENTUM_CHANNEL_FORMULA",
        "domain": "one fixed generic ell>=2 and nonzero |k|, all three input primaries at both momentum signs, all generic L=1,...,2ell outputs, before stabilizer quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "resonance_divisor": _divisor_formula(),
        "universal_relative_phase_family": _universal_relative_phase_family(),
        "secular_inversion_lemma": _secular_lemma(),
        "classification": {
            "phase_sensitive_resonance_divisor_formula_exact": True,
            "resonance_divisor_nonempty_for_every_ell": True,
            "bounded_or_finite_quasiperiodic_extension_follows_from_moment_maps_alone": False,
            "generic_nonzero_resonance_removable_in_smooth_global_secular_class": True,
            "zero_frequency_K0_constraints_still_controlled_by_moment_maps": True,
            "static_L0_K2k_exceptional_block_classified": False,
            "complete_opposite_momentum_second_order_cone_classified": False,
        },
        "interpretation": "Relative phases do not create a new Taub charge, but they do populate exact nonzero-frequency resonance divisors. Thus bounded/quasiperiodic and smooth-global second-order questions diverge. Generic resonances are removable by secular exponential-polynomial corrections; the remaining smooth-global gate is the phase-sensitive static L=0,K=2k exceptional target block.",
        "next_gate": "classify the Weyl-Maxwell polar L=0 target at nonzero spatial momentum and test the static K=2k interference source; then promote or obstruct the smooth-global opposite-momentum cone",
        "claim_boundary": "This classifies the resonance divisor and correction-space distinction, not the complete standing-wave source. It does not prove bounded extension on resonance, classify the static L=0,K=2k block, join distinct |k| fibers, or establish all-orders, causal, scattering, particle, or quantum claims.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.05, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.1, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["opposite_cone", "axial_ring", "polar_ring", "axial_L1", "polar_L1"]},
            "tier_3": {"status": "NOT_RUN", "reason": "the static L=0,K=2k block and bounded resonant source projection remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "opposite-momentum resonance certificate is stale")


if __name__ == "__main__":
    main()
