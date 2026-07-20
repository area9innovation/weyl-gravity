"""Join harmonic Taub signs to the complete finite-harmonic obstruction map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_harmonic_sign_resonance_join.schema.json"
INPUTS = {
    "sign": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
    "finite": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "k0_complete": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.json",
    "candidate13": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.json",
    "opposite_momentum": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.json",
    "polynomial_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "resonance_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
}


class JoinError(RuntimeError):
    pass


def _require(value: bool, message: str) -> None:
    if not value:
        raise JoinError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    sign = records["sign"]["classification"]
    finite = records["finite"]["classification"]
    k0 = records["k0_complete"]["classification"]
    candidate13 = records["candidate13"]["classification"]
    opposite = records["opposite_momentum"]["classification"]
    _require(sign["finite_pure_extra_harmonic_sums_negative"], "pure-extra sign theorem changed")
    _require(sign["Einstein_q_minus_opposite_sign_all_ell_both_parities"], "Einstein balancing sign changed")
    _require(finite["complete_smooth_adjoint_cokernel_equals_five_stabilizers"], "smooth cokernel changed")
    _require(finite["bounded_polynomial_and_resonant_ledger_defined"], "bounded ledger disappeared")
    _require(not finite["bounded_common_zero_locus_solved"], "full bounded cone was promoted upstream")
    _require(k0["bounded_zero_locus_necessary_and_sufficient"], "k=0 zero locus lost sufficiency")
    _require(k0["arbitrary_finite_generic_ell_complete_global_bounded_cone_classified"], "k=0 carrier changed")
    _require(not k0["exceptional_wave_inputs_classified"], "exceptional waves silently entered k=0 theorem")
    _require(not k0["nonzero_momentum_classified"], "nonzero momentum silently entered k=0 theorem")
    _require(candidate13["candidate13_complete_bounded_cone_is_origin"], "candidate-13 control changed")
    _require(opposite["two_nonzero_mixed_qminus_components_survive"], "opposite-momentum control changed")

    return {
        "schema": "einstein-maxwell-weyl-harmonic-sign-resonance-join-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HARMONIC_SIGN_RESONANCE_JOIN",
        "result_state": "COMPLETE_JOIN_AND_MAXIMAL_CERTIFIED_K0_MIXED_BOUNDED_CONE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_FINITE_HARMONIC_JOIN_WITH_MAXIMAL_COMPLETE_K0_SUBCARRIER",
        "scope": {
            "theory": "Einstein-Maxwell image and additional-Weyl cofiber inside Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle; electric tangent retained until the obstruction map removes it",
            "carrier": "complete certified finite harmonic inventory for the joined map; maximal classified subcarrier is all standard globals plus arbitrary finite generic ell>=2,k=0 q/p waves",
            "degree": 2,
            "parity": "axial and polar where present",
            "ell": "joined map: homogeneous 0, exceptional 1 and generic >=2; classified subcarrier: globals plus arbitrary finite generic ell>=2",
            "m": "all certified SO3 multiplicities",
            "k": "joined map: every certified compact momentum; classified subcarrier: k=0",
            "omega": "all certified q/p shells and generalized-zero polynomial classes",
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "result_id": records[name]["result_id"],
                    "sha256": _sha256(path),
                }
                for name, path in INPUTS.items()
            },
        },
        "branch_labelled_obstruction_map": {
            "equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
            "bounded_codomain": "stab* direct_sum polynomial_growth direct_sum characteristic_shell",
            "stabilizer_block": [
                "mu_H",
                "mu_Px",
                "mu_J1",
                "mu_J2",
                "mu_J3",
            ],
            "polynomial_growth_block": "P_(j,r), for every output j=(L,M,K,Omega,parity) and every certified positive temporal degree r",
            "characteristic_shell_block": "R_(j,a)=<zeta_(j,a),S_j(u,u)> for every exact reduced left-kernel basis vector a on a nonzero-frequency p/q target shell",
            "block_orthogonality": {
                "harmonic": "distinct (L,M,K,Omega,parity) output blocks are direct summands",
                "zero_vs_nonzero_frequency": "stabilizer covectors are excluded from P and R; R uses only nonzero characteristic shells",
                "branch": "the stationary Lee-Wald form is branch-diagonal, so the Hamiltonian sign ledger is an orthogonal occupation sum before P/R are evaluated",
            },
            "bounded_necessity_and_sufficiency": "O_bounded(u)=0 iff a bounded or finite-quasiperiodic second-order correction exists on the complete certified finite carrier",
            "smooth_restriction": "O_smooth=(mu_H,mu_Px,mu_J1,mu_J2,mu_J3); P and R admit finite secular primitives",
        },
        "sign_join": {
            "pure_additional_weyl_face": "mu_H<0 for every nonzero real finite pure-extra tangent, hence its common zero with P and R is the origin",
            "Einstein_q_minus": "has the opposite Hamiltonian sign in every generic ell>=2 parity and can balance additional-Weyl occupation",
            "global_blocks": "homogeneous and twist solution cofibers vanish; they are standard generalized-zero image data, not additional-Weyl exceptions",
            "constant_twist": "constant twist position is an exact zero-energy global modulus and is controlled separately by P/R cross columns",
        },
        "maximal_complete_mixed_subcarrier": {
            "domain": "complete standard homogeneous/twist/Maxwell globals plus an arbitrary finite sum of generic ell>=2,k=0 q-minus, q-plus and both p-extra multiplicities, all m and both parities",
            "bounded_zero_locus": {
                "wave_free": records["k0_complete"]["complete_bounded_zero_locus"]["static_stratum"],
                "wave_nonzero": records["k0_complete"]["complete_bounded_zero_locus"]["wave_stratum"],
                "intersection": records["k0_complete"]["complete_bounded_zero_locus"]["intersection"],
            },
            "necessity_and_sufficiency": True,
            "why_complete": "all polynomial and shell columns on this carrier are either the displayed global eliminators, identically zero, or have certified bounded inverses; cross-ell outputs are off shell and finite blockwise corrections add",
            "mu_Px": "automatic at k=0",
        },
        "separate_nonzero_momentum_controls": {
            "candidate13": "complete bounded cone is the origin on its declared two-|k| all-m both-parity carrier",
            "tuned_opposite_momentum": "two nonzero mixed q-minus components survive on its distinct axisymmetric all-primary carrier",
            "crosswalk": "NO_CERTIFIED_MAP between these distinct circumference/momentum carriers; they are controls, not pieces of one cone",
        },
        "independence_witnesses": {
            "polynomial": "the aligned global-extra tangent has all five moment maps zero but a nonzero positive-degree source coefficient P",
            "resonant": "the twist-balanced exceptional tangent has all five moment maps zero but a nonzero characteristic-shell functional R",
            "consequence": "moment-map cancellation is not bounded solvability on the complete finite carrier",
        },
        "unclassified_remainder": {
            "first_family": "exceptional ell=1 oscillator inputs mixed with generic waves and globals at arbitrary compact momentum, followed by unions of multiple |k| fibres",
            "functional_map": "CERTIFIED as the coefficientwise {mu,P,R} zero-locus formula",
            "common_zero_geometry": "OPEN",
            "reason": "the existing exact inputs do not classify simultaneous cancellations among every exceptional/global/opposite-momentum polynomial and shell row",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "complete_map": "CERTIFIED",
                "maximal_k0_subcarrier_zero_locus": "CERTIFIED",
                "full_finite_carrier_zero_locus": "OPEN",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "complete_zero_locus": "CERTIFIED: mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
            },
            "CAUSAL_RETARDED": {
                "status": "NO_CERTIFIED_MAP",
            },
        },
        "classification": {
            "complete_branch_labelled_obstruction_map_joined": True,
            "block_orthogonality_certified": True,
            "bounded_necessity_and_sufficiency_formula_certified": True,
            "smooth_finite_harmonic_cone_certified": True,
            "pure_extra_face_is_origin": True,
            "maximal_generic_k0_global_mixed_bounded_cone_classified": True,
            "candidate13_and_opposite_momentum_controls_kept_separate": True,
            "exceptional_generic_global_arbitrary_k_common_zero_classified": False,
            "multiple_abs_momentum_full_cone_classified": False,
            "infinite_harmonic_completion_classified": False,
            "all_orders_causal_residual_observational_or_quantum_claim": False,
        },
        "claim_boundary": "This exact join is confined to the compact Plebanski-Hacyan reduced harmonic programme. The full finite bounded obstruction map is complete as a formula, while only the declared arbitrary-finite generic k=0 plus standard-global subcarrier has a classified mixed zero locus. Exceptional/global arbitrary-k unions, multiple |k| fibres, infinite completion, all-orders integration, final residual descent, causal propagation, observables, particles and quantum norms remain open.",
        "next_gate": "classify exceptional ell=1 wave cross columns with generic/global inputs at arbitrary k, then join multiple |k| fibres without identifying their phases or circumference backgrounds",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_harmonic_sign_resonance_join --verify bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_harmonic_sign_resonance_join.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_harmonic_sign_resonance_join",
        ],
    }


def verify(path: Path = OUTPUT) -> None:
    if json.loads(path.read_text(encoding="utf-8")) != build_certificate():
        raise JoinError(f"stale certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        verify(args.verify)


if __name__ == "__main__":
    main()
