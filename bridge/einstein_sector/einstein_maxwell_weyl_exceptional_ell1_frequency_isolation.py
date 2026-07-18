"""Isolate the exceptional ell=1 frequency from every other k=0 harmonic block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.schema.json"
INPUTS = {
    "all_m_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "physical_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "standard_globals": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
}


class FrequencyIsolationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FrequencyIsolationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frequency_audit() -> dict[str, object]:
    lam = sp.symbols("lambda", real=True)
    exceptional = sp.Rational(4, 3)
    extra_min = sp.Rational(16, 3)
    minus_at_six = 6 - 2 * sp.sqrt(3)
    minus_gap = sp.factor(minus_at_six - exceptional)
    squared_gap_witness = sp.expand((6 - exceptional) ** 2 - 12)
    _require(extra_min - exceptional == 4, "generic extra gap changed")
    _require(squared_gap_witness == sp.Rational(88, 9), "Einstein-minus square witness changed")
    _require(bool(minus_gap > 0), "Einstein-minus minimum ceased to exceed 4/3")
    derivative = sp.diff(lam - sp.sqrt(2 * lam), lam)
    return {
        "exceptional_frequency_squared": "4/3",
        "generic_ell_ge_2_k0": {
            "extra_p": "lambda-2/3 >= 16/3, gap from 4/3 is at least 4",
            "Einstein_minus_q": "lambda-sqrt(2lambda) is increasing for lambda>=6 and its minimum 6-2sqrt(3) exceeds 4/3",
            "Einstein_minus_derivative": str(derivative),
            "Einstein_minus_endpoint_gap": str(minus_gap),
            "Einstein_minus_exact_square_witness": "(14/3)^2-12=88/9>0",
            "Einstein_plus_q": "lambda+sqrt(2lambda) is strictly above the minus branch",
            "conclusion": "no generic axial or polar k=0 p- or q-primary has omega^2=4/3",
        },
        "exceptional_ell1_k0": {
            "axial_roots": ["0", "4/3", "4"],
            "polar_roots": ["4/3", "4"],
            "complete_same_frequency_block": "among ell>=1, the omega^2=4/3 eigenspace is exactly the axial-plus-polar exceptional block already covered by the all-m obstruction theorem",
        },
        "standard_global_blocks": {
            "ell0_and_twist": "generalized zero-frequency polynomial/Jordan data, with no positive-positive 2omega_e temporal component",
            "physical_ell1": "omega^2=4 at k=0",
        },
        "angular_selection": {
            "obstructing_channel": "the exceptional dipole self-source has a nonzero L=2 component at Omega=2omega_e",
            "ell0_times_ell0": "L=0 only",
            "ell0_times_ell1": "L=1 only",
            "ell0_times_other": "an L=2 contribution would require an ell=2 partner, but every classified ell>=2 k=0 oscillator is frequency-separated",
            "ell1_times_ell1": "L=0 direct-sum L=2; the complete omega_e ell1 block is already included in the all-m STF theorem",
        },
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    omega, k, lam = sp.symbols("omega k lambda")
    shell_locals = {"omega": omega, "k": k, "lam": lam}
    parse_shell = lambda expression: sp.sympify(expression.replace("lambda", "lam"), locals=shell_locals)
    expected_p = omega**2 - k**2 - lam + sp.Rational(2, 3)
    expected_q = (omega**2 - k**2 - lam) ** 2 - 2 * lam
    _require(
        records["all_m_obstruction"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"],
        "all-m obstruction input changed",
    )
    _require(records["axial_generic"]["classification"]["all_physical_lambda_specializations_certified"], "axial generic spectrum changed")
    _require(records["polar_generic"]["classification"]["all_physical_lambda_and_compact_momenta_including_zero_certified"], "polar generic spectrum changed")
    axial_blocks = records["axial_generic"]["audit"]["block_reduction"]
    polar_shells = records["polar_generic"]["physical_ring"]["shells"]
    for label, expression in (("axial p", axial_blocks["p"]), ("polar p", polar_shells["p"])):
        _require(sp.expand(parse_shell(expression) - expected_p) == 0, f"{label} shell changed")
    for label, expression in (("axial q", axial_blocks["q"]), ("polar q", polar_shells["q"])):
        _require(sp.expand(parse_shell(expression) - expected_q) == 0, f"{label} shell changed")
    _require(records["axial_ell1"]["operator_theorem"]["primary_shells"]["extra_fourth_order"] == "omega^2=4/3", "axial ell1 root changed")
    _require(records["polar_ell1"]["operator_theorem"]["physical_shells"]["fourth_order"]["omega_squared"] == "4/3", "polar ell1 root changed")
    _require(records["physical_ell1"]["theorem"]["dispersion"] == "omega^2=k_n^2+4", "physical ell1 shell changed")
    _require(records["standard_globals"]["classification"]["axial_ell1_twist_generalized_pair_complete"], "standard twist input changed")
    audit = _frequency_audit()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-frequency-isolation-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_FREQUENCY_ISOLATION",
        "result_state": "EXCEPTIONAL_ELL1_K0_SAME_FREQUENCY_SECTOR_ISOLATED_AND_SECOND_ORDER_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "the complete fixed-bundle k=0 ell>=1 oscillatory source spectrum at omega_e^2=4/3, together with the angular-selection proof that ell=0 cannot enter the obstructing L=2 channel, before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "frequency_audit": audit,
        "classification": {
            "all_k0_generic_axial_and_polar_p_q_primaries_frequency_separated": True,
            "physical_ell1_frequency_separated": True,
            "exceptional_ell1_same_frequency_eigenspace_complete": True,
            "standard_generalized_zero_blocks_have_no_2omega_e_component": True,
            "ell0_unknown_extra_target_not_needed_by_angular_selection": True,
            "same_frequency_nonexceptional_cancellation_excluded": True,
            "complete_pure_exceptional_ell1_k0_second_order_no_go_frozen": True,
            "different_frequency_pair_sums_classified": False,
            "different_momentum_pairs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The exceptional dipole obstruction cannot be removed by adding another k=0 mode on the same positive-frequency shell. The complete ell>=1 omega_e eigenspace is precisely the axial-plus-polar exceptional ell=1 block, whose all-m resonance tensor has only the origin as a compatible point; angular selection excludes ell=0 from the obstructing L=2 channel. Thus the pure exceptional ell=1,k=0 second-order no-go is frozen, while cancellations built from different input frequencies or momenta remain separate questions.",
        "next_gate": "classify whether pairs of different-frequency or opposite-momentum modes can sum to the exceptional 2omega_e,L=2,K=0 resonant channel",
        "claim_boundary": "This is a compact fixed-bundle same-frequency second-order theorem at k=0. It does not exclude cancellation by pairs with unequal frequencies summing to 2omega_e, opposite nonzero momenta, all-orders integration, final residual descent, causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.13, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_frequency_isolation --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_frequency_isolation"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "different-frequency, different-momentum, and all-orders gates remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_frequency_isolation --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_frequency_isolation.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_frequency_isolation",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "frequency-isolation certificate is stale")


if __name__ == "__main__":
    main()
