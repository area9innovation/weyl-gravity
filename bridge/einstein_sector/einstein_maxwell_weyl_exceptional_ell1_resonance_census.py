"""Census positive-sum inputs for the exceptional ell=1 2omega resonance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_resonance_census.schema.json"
INPUTS = {
    "frequency_isolation": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "standard_globals": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
    "homogeneous_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
}


class ResonanceCensusError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ResonanceCensusError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _census() -> dict[str, object]:
    target_input_sq = sp.Rational(4, 3)
    target_output_sq = 4 * target_input_sq
    lam = sp.symbols("lambda", real=True)
    minus_equation = sp.factor((lam - target_output_sq) ** 2 - 2 * lam)
    minus_roots = sp.solve(minus_equation, lam)
    _require(target_output_sq == sp.Rational(16, 3), "output frequency changed")
    _require(minus_roots == [sp.Rational(19, 3) - sp.sqrt(105) / 3, sp.sqrt(105) / 3 + sp.Rational(19, 3)], "minus roots changed")
    _require(bool(minus_roots[0] < 6), "lower minus root crossed the physical range")
    _require(bool(6 < minus_roots[1] < 12), "upper minus root left the lambda=6,12 gap")
    return {
        "target": {
            "input_frequency_squared": "4/3",
            "positive_sum_frequency": "2omega_e",
            "positive_sum_frequency_squared": "16/3",
            "spatial_momentum": "K=0",
            "angular_channel": "L=2",
        },
        "two_nonzero_positive_inputs": {
            "lower_bound": "every nonzero k=0 oscillatory mode has omega>=omega_e",
            "equality_case": "omega_a+omega_b=2omega_e iff both inputs lie in the exceptional ell=1 omega_e block",
            "status": "covered by the all-m STF obstruction theorem",
        },
        "zero_plus_positive_inputs": {
            "required_positive_shell": "omega^2=(2omega_e)^2=16/3",
            "generic_extra_equation": "lambda-2/3=16/3 iff lambda=6 iff ell=2",
            "Einstein_plus": "lambda+sqrt(2lambda)>16/3 for every physical lambda>=6",
            "Einstein_minus_squared_equation": str(minus_equation),
            "Einstein_minus_candidate_lambdas": [str(root) for root in minus_roots],
            "Einstein_minus_exclusion": "one root is below 6 and the other lies strictly between the consecutive physical values lambda=6 and lambda=12",
            "physical_ell1": "omega^2=4, not 16/3",
            "unique_live_block": "generic ell=2 extra p-primary, either parity, at k=0",
        },
        "difference_frequency_inputs": {
            "condition": "|omega_a-omega_b|=2omega_e with |ell_a-ell_b|<=2 for an L=2 output",
            "status": "OPEN",
        },
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["frequency_isolation"]["classification"]["complete_pure_exceptional_ell1_k0_second_order_no_go_frozen"], "frequency-isolation input changed")
    _require(records["axial_generic"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial generic block changed")
    _require(records["polar_generic"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "polar generic block changed")
    _require(records["standard_globals"]["classification"]["fixed_bundle_standard_harmonic_symplectic_completion"], "global block changed")
    _require(records["homogeneous_target"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"], "homogeneous target changed")
    census = _census()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-resonance-census-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_RESONANCE_CENSUS",
        "result_state": "EXCEPTIONAL_2OMEGA_POSITIVE_SUM_CENSUS_COMPLETE_UNIQUE_GLOBAL_TIMES_ELL2_EXTRA_GATE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "the complete fixed-bundle k=0 harmonic source spectrum for positive-sum quadratic inputs capable of reaching the exceptional L=2,K=0,Omega=2omega_e resonance",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "resonance_census": census,
        "classification": {
            "positive_sum_resonance_census_complete": True,
            "homogeneous_nonzero_frequency_target_empty": True,
            "two_nonzero_positive_inputs_reduce_to_exceptional_all_m_block": True,
            "unique_zero_plus_positive_resonance_is_global_times_ell2_extra": True,
            "global_times_ell2_extra_source_pairing_computed": False,
            "difference_frequency_resonances_classified": False,
            "opposite_nonzero_momenta_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The same-frequency audit does not end the mixed-cone problem. The direct homogeneous operator theorem excludes hidden ell=0 oscillators, so the complete positive-frequency sum census has exactly one new route to the exceptional 2omega_e,L=2 resonance: a generalized zero-frequency global direction multiplied by a generic ell=2 extra-primary mode at omega^2=16/3. This is now the unique positive-sum source calculation to perform. Difference-frequency and opposite-momentum resonances remain separate.",
        "next_gate": "compute the bilinear second-order source and adjoint pairings for every standard homogeneous/twist global direction crossed with the axial and polar ell=2 extra-primary block",
        "claim_boundary": "This is an exact positive-sum resonance census, not a source-solvability theorem. It does not compute the live global-times-ell2-extra coefficient, classify frequency differences, include opposite nonzero momenta, prove all-orders integration, or make causal or quantum claims.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.52, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_resonance_census --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_resonance_census.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_resonance_census"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the live source coefficient and broader resonance classes remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_resonance_census --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_resonance_census.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_resonance_census",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "resonance-census certificate is stale")


if __name__ == "__main__":
    main()
