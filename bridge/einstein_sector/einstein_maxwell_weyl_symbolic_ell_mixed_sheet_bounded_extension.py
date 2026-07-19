"""Join the all-ell mixed q-minus sheets to one bounded second-order jet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.schema.json"
INPUTS = {
    "parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json",
    "standard_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.json",
    "finite_generic_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "common_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    parity = records["parity_matrix"]["classification"]
    census = records["standard_census"]["classification"]
    generic = records["finite_generic_cone"]
    common = records["common_zero"]
    _require(parity["complete_resonance_zero_variety_classified"] and parity["nonzero_two_momentum_null_sheets_exist_every_integer_ell_ge_2"], "mixed sheets changed")
    _require(census["all_standard_qminus_qplus_input_pairs_covered"] and census["unique_nonzero_frequency_standard_branch_collision_is_qminus_L2ell_p"], "standard census changed")
    _require(generic["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"], "bounded cokernel decomposition changed")
    _require(generic["bounded_resonance_functionals"]["necessity_and_sufficiency"].startswith("a bounded or finite-quasiperiodic correction exists exactly"), "bounded sufficiency changed")
    _require(common["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"], "common-zero occupation changed")
    witness = common["exact_intersection_witness"]
    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-mixed-sheet-bounded-extension-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_MIXED_SHEET_BOUNDED_EXTENSION",
        "result_state": "EVERY_ELL_HAS_TWO_NONZERO_MIXED_PARITY_STANDARD_BRANCH_BOUNDED_SECOND_ORDER_JETS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_INTEGER_ELL_ONE_TUNED_NONZERO_MOMENTUM_FIBRE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned separately for each ell",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "wave-only axisymmetric q-minus mixed-parity sheet plus equal-opposite-momentum q-plus balance; no twist or extra-primary input",
            "degree": 2,
            "parity": "both q-minus parities with either common sheet sign; one normalized q-plus multiplicity",
            "ell": "every integer ell>=2",
            "m": "m=0 relative to the declared axis",
            "k": witness["resonant_k_squared"],
            "omega": "q-minus and q-plus positive-frequency branches and their real conjugates",
        },
        "declared_tangent": {
            "sheet_sign": "sigma=+1 or sigma=-1",
            "qminus_ratio": "a_+=sigma*sqrt(ell*(ell+1)/2)*p_+ and a_-=sigma*sqrt(ell*(ell+1)/2)*p_-",
            "opposite_momentum_choice": "choose p_+=p_- nonzero and normalize the common scale so each signed q-minus density equals the displayed q-minus density",
            "qminus_density_each_sign": witness["positive_frequency_inputs"]["Einstein_minus"],
            "qplus_density_each_sign": witness["positive_frequency_inputs"]["Einstein_plus"],
            "qplus_choice": "choose equal +k and -k coefficients in any one action-normalized q-plus multiplicity",
            "reality": "adjoin the negative-frequency complex conjugates",
            "twist": "zero",
        },
        "five_moment_maps": {
            "mu_H": "zero by the imported action-normalized q-plus/q-minus density balance",
            "mu_Px": "zero because every occupied branch has equal +k and -k density",
            "mu_J1": "zero on m=0 rank-one densities",
            "mu_J2": "zero on m=0 rank-one densities",
            "mu_J3": "zero on m=0 rank-one densities",
        },
        "bounded_blockwise_proof": {
            "abstract_criterion": generic["bounded_resonance_functionals"]["necessity_and_sufficiency"],
            "zero_block": "the complete reduced zero-block cokernel is span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}; all five pairings vanish",
            "nonzero_frequency_census": "the complete standard-branch census leaves exactly one shell collision, q-minus x q-minus to polar p at L=2ell,K=0,Omega=2omega_minus",
            "unique_polar_output": "vanishes on either mixed sheet by a_+*a_- - ell*(ell+1)*p_+*p_-/2=0",
            "unique_axial_output": "vanishes on either mixed sheet by a_+*p_- - a_-*p_+=0",
            "all_other_blocks": "off shell and algebraically invertible in the finite generic quotient",
            "conclusion": "every finite quadratic source block lies in the bounded image of the reduced Weyl-Maxwell operator",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "the bounded correction belongs to this larger class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "both_symbolic_mixed_sheet_signs_covered": True,
            "every_integer_ell_ge_2_has_nonzero_bounded_second_order_jet": True,
            "complete_standard_branch_quadratic_output_census_used": True,
            "five_moment_maps_and_all_bounded_resonant_functionals_vanish": True,
            "bounded_correction_exists_by_complete_cokernel_criterion": True,
            "full_mixed_sheet_amplitude_cone_classified": False,
            "extra_primary_or_multiple_abs_momentum_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The ell=2 balanced extension is not isolated. At every generic angular degree, the opposite signs of the axial and polar q-minus self-sources create two mixed sheets; a positive q-plus occupation cancels the compact Hamiltonian without introducing another shell collision. Hence each ell has two explicit nonzero bounded second-order jets. This proves nonlinear survival to second order for a standard Einstein-sector mixture, not nonlinear closure of the whole Einstein image.",
        "next_gate": "classify the full action-normalized amplitude cone on the two sheets and then join distinct absolute momentum fibres",
        "claim_boundary": "This certifies two explicit wave-only bounded second-order families for each separately tuned ell>=2. It does not classify the full sheet amplitude cone, extra-primary inputs, a fixed circumference across ell, multiple |k| fibres, all-orders integration, causal transport, residual descent, observation or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build_certificate()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        _require(json.loads(OUTPUT.read_text(encoding="utf-8")) == value, "stale mixed-sheet extension certificate")
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_MIXED_SHEET_BOUNDED_EXTENSION: PASS")


if __name__ == "__main__":
    main()
