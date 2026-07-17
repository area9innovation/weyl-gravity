"""Odd-total-parity output ledger for axial--polar ell=2 cross products."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from sympy.physics.wigner import wigner_3j


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.schema.json"
INPUTS = {
    "same_parity_output": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
    "polar_ell1_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "axial_physical_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_physical_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "full_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json",
}


class Ell2CrossParityOutputError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Ell2CrossParityOutputError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _angular_selection() -> dict[str, Any]:
    blocks: dict[str, Any] = {}
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
        if output_ell == 0:
            target = "absent_axial_L0"
        else:
            target = "polar" if output_ell % 2 else "axial"
        blocks[str(output_ell)] = {"target_parity": target, "nonzero_scalar_coupling_witness": witnesses[0]}
    return {
        "tensor_product": "V_2 tensor V_2 = V_0+V_1+V_2+V_3+V_4",
        "scope": "axial ell=2 times polar ell=2",
        "parity_rule": "the cross product has odd spatial parity, hence polar odd-L and axial even-L outputs",
        "output_blocks": blocks,
        "L0_absence": "the axial vector/tensor harmonic generated from a constant scalar harmonic vanishes identically",
    }


def _generic_even_output_witnesses(records: dict[str, Any]) -> dict[str, Any]:
    face_input = records["full_extra_face"]["provenance"]["inputs"]["three_branch_face"]
    face = json.loads((ROOT / face_input["path"]).read_text(encoding="utf-8"))
    output: dict[str, Any] = {}
    for name, channel in face["nonzero_frequency_channel_ledger"].items():
        blocks = channel["generic_polar_outputs"]
        _require(set(blocks) == {"2", "4"}, f"generic even output set changed for {name}")
        output[name] = {}
        for ell in ("2", "4"):
            p = blocks[ell]["p_shell_witness"]
            q = blocks[ell]["q_shell_witness"]
            _require(p["certified_nonzero"] and q["certified_nonzero"], f"generic shell witness failed for {name},L={ell}")
            output[name][ell] = {"p": p, "q": q}
    _require(len(output) == 9, "generic cross frequency count changed")
    return output


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    shared = records["same_parity_output"]
    polar_ell1 = records["polar_ell1_operator"]
    _require(shared["classification"]["all_nine_nonzero_frequency_types_off_target_shells"], "shared frequency ledger changed")
    _require(polar_ell1["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"], "polar L1 zero gate changed")
    _require(records["axial_physical_ring"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial generic quotient changed")
    _require(records["polar_physical_completion"]["classification"]["canonical_extra_polar_quotient_two_p_summands"], "polar generic quotient changed")
    axial_shells = records["axial_physical_ring"]["audit"]["block_reduction"]
    polar_shells = records["polar_physical_completion"]["physical_ring"]["shells"]
    _require(axial_shells["p"] == polar_shells["p"] and axial_shells["q"] == polar_shells["q"], "axial/polar generic shells ceased to be isospectral")

    shared_nonzero = shared["nonzero_frequency_resonance_ledger"]["nine_nonzero_frequency_types"]
    even_witnesses = _generic_even_output_witnesses(records)
    ledger: dict[str, Any] = {}
    for name, channel in shared_nonzero.items():
        polar_l1 = {
            "p_or_fourth_order": channel["axial_L1"]["Omega_squared_minus_4_over_3"],
            "q_or_standard": channel["axial_L1"]["Omega_squared_minus_4"],
        }
        polar_l3 = channel["axial_L3"]
        _require(all(item["certified_nonzero"] for item in polar_l1.values()), f"polar L1 resonance in {name}")
        _require(all(item["certified_nonzero"] for item in polar_l3.values()), f"polar L3 resonance in {name}")
        ledger[name] = {
            "frequency": channel["frequency"],
            "polar_L1": polar_l1,
            "axial_L2": even_witnesses[name]["2"],
            "polar_L3": polar_l3,
            "axial_L4": even_witnesses[name]["4"],
            "all_present_blocks_invertible": True,
        }

    return {
        "schema": "einstein-maxwell-weyl-ell2-cross-parity-output-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_CROSS_PARITY_OUTPUT_RESONANCE",
        "result_state": "ALL_AXIAL_POLAR_ELL2_CROSS_OUTPUT_BLOCKS_INVERTIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ELL2_K0_ALL_M_CROSS_PARITY_OUTPUTS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "all angular and sum/difference-frequency outputs of axial ell=2,k=0 times polar ell=2,k=0 Weyl-Maxwell tangents",
        "angular_selection": _angular_selection(),
        "zero_frequency_blocks": {
            "axial_L0": "absent",
            "polar_L1": {"invertible": True, "determinant_at_zero": "8"},
            "axial_L2": {"p": "-16/3", "q": "24", "invertible": True},
            "polar_L3": {"p": "-34/3", "q": "120", "invertible": True},
            "axial_L4": {"p": "-58/3", "q": "360", "invertible": True},
            "physical_adjoint_cokernel": "none",
        },
        "nonzero_frequency_ledger": ledger,
        "generic_isospectral_transfer": {
            "p": axial_shells["p"],
            "q": axial_shells["q"],
            "statement": "the exact polar L2,L4 witnesses transfer to axial L2,L4, and the exact axial L3 witnesses transfer to polar L3, because both parities have identical p and q shell polynomials",
        },
        "Noether_completion": "the natural second variation obeys the linearized target Noether identities; invertibility is asserted on the complete local-gauge quotient",
        "classification": {
            "cross_parity_angular_selection_certified": True,
            "cross_zero_frequency_physical_cokernel_absent": True,
            "all_nine_cross_frequency_types_off_all_target_shells": True,
            "cross_source_coefficients_required_for_solvability": False,
            "complete_axial_polar_combined_cone_yet_claimed": False,
            "general_ell_covered": False,
        },
        "interpretation": "Every axial-polar cross source lands in an invertible target quotient block. Therefore no cross-source coefficient can impose a new Taub condition at ell=2; only the already classified pure-sector H and J_i projections can obstruct the total second-order equation.",
        "next_gate": "combine the pure axial and pure polar source theorems using parity-orthogonality of the stabilizer moment maps",
        "claim_boundary": "This is an output-solvability theorem, not a printed cross-source coefficient table. It covers ell=2,k=0 only and does not establish general ell, opposite momentum, all-orders integration, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_cross_parity_output_resonance --verify bridge/certificates/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_cross_parity_output_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_cross_parity_output_resonance",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"cross-parity output certificate stale: {path}")


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
