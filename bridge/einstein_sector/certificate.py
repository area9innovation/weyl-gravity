"""Build and verify the fail-closed Einstein-sector theorem certificate.

This module does not attempt to prove a global Lorentzian boundary-value
theorem.  It records the exact local Einstein-to-Bach implication and checks
the already-certified local-mode and closed-cylinder residual statements on
which the interpretation depends.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "einstein_sector_theorem.json"

INPUTS = {
    "local_free_bv": ROOT / "bridge" / "certificates" / "free_bv_complex.json",
    "metric_to_residual": ROOT / "bridge" / "certificates" / "metric_to_residual.json",
    "cylinder_preimages": ROOT / "bridge" / "certificates" / "cylinder_metric_preimages.json",
    "helicity_two_channel": ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_helicity_two_channel.json",
    "completed_residual": ROOT
    / "analytic_completion"
    / "certificates"
    / "completed_H4.json",
    "compensated_characteristic_snapshot": ROOT
    / "bridge"
    / "certificates"
    / "compensated_nonzero_characteristic_snapshot.json",
    "compensated_sourced_defect_chain_map": ROOT
    / "bridge"
    / "certificates"
    / "compensated_sourced_defect_chain_map.json",
}


class EinsteinSectorCertificateError(RuntimeError):
    """Raised when an upstream theorem input does not meet the import gate."""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EinsteinSectorCertificateError(message)


def _verify_inputs(records: dict[str, dict[str, Any]]) -> None:
    local = records["local_free_bv"]
    _require(
        local.get("cohomology") == "H(q)_one-particle = W+ direct-sum W-",
        "local free BV input does not certify W+ direct-sum W-",
    )

    residual = records["metric_to_residual"]
    _require(
        residual.get("one_particle", {}).get("h4") == 0,
        "metric-to-residual input does not certify one-particle H4=0",
    )
    _require(
        residual.get("two_particle", {}).get("h4") == 2,
        "metric-to-residual input does not certify two-particle H4=2",
    )
    _require(
        residual.get("two_particle", {}).get("interpretation")
        == ["Pontryagin/odd", "Weyl-square/even"],
        "metric-to-residual input changed the two residual class roles",
    )

    preimages = records["cylinder_preimages"]
    families = {row.get("family"): row for row in preimages.get("records", [])}
    _require(set(families) == {"E", "A", "L"}, "cylinder E/A/L inventory changed")
    _require(
        families["E"].get("minimum_energy") == 2,
        "Einstein-root E tower no longer starts at energy two",
    )
    _require(
        preimages.get("parity_completion", {}).get("map") == "alpha<->gamma",
        "cylinder parity completion is absent",
    )

    helicity = records["helicity_two_channel"]
    _require(helicity.get("exact") is True, "helicity-two channel is not exact")
    _require(
        helicity.get("complex_weights") == ["+2i", "-2i"],
        "helicity weights are not the two spin-two weights",
    )
    _require(
        helicity.get("linearized_Weyl_symbol", {}).get("target_quotient_dimension")
        == 2,
        "physical Weyl-symbol quotient is not two-dimensional",
    )
    _require(
        helicity.get("linearized_Weyl_symbol", {}).get("is_isomorphism") is True,
        "linearized Weyl map is not certified on the helicity quotient",
    )

    completed = records["completed_residual"]
    _require(
        completed.get("selected_boundary_problem")
        == "closed cylinder with all fifteen residual generators gauged",
        "completed residual input is not the selected closed-cylinder problem",
    )
    _require(
        completed.get("centered", {}).get("one_particle_H4") == 0,
        "completed residual one-particle H4 changed",
    )
    _require(
        completed.get("interpretation")
        == "two classical ghost-dressed weight-four vertex classes, not particles",
        "completed residual classes are no longer guarded as non-particle classes",
    )

    characteristic = records["compensated_characteristic_snapshot"]
    _require(
        characteristic.get("result_state")
        == "SCOPED_EXACT_SNAPSHOT_CERTIFIED_GLOBAL_CLASSICAL_FREEZE_OPEN"
        and characteristic.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "compensated characteristic snapshot scope drifted",
    )
    branches = characteristic.get("branches", {})
    _require(
        branches.get("massless", {}).get("cohomology_dimensions")
        == {"-1": 0, "0": 2, "1": 2, "2": 0}
        and branches.get("second_root", {}).get("cohomology_dimensions")
        == {"-1": 0, "0": 5, "1": 5, "2": 0},
        "compensated characteristic cohomology inventory drifted",
    )
    flags = characteristic.get("claim_flags", {})
    _require(
        flags.get("operator_export_independently_verified") is True
        and flags.get("momentum_reversing_odd_bv_pairings_nondegenerate") is True
        and flags.get("zero_momentum_global_modes_classified") is False
        and flags.get("physical_cauchy_symplectic_pairing_computed_here") is False
        and flags.get("classical_import_freeze_complete") is False
        and flags.get("lorentzian_causal_claim") is False,
        "compensated characteristic claim boundary drifted",
    )

    sourced = records["compensated_sourced_defect_chain_map"]
    _require(
        sourced.get("result_state")
        == "UNIVERSAL_SOURCE_WARD_CHAIN_MAP_CERTIFIED_MATTER_BV_LIFT_OPEN"
        and sourced.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "compensated sourced-defect chain-map scope drifted",
    )
    source_flags = sourced.get("claim_flags", {})
    _require(
        source_flags.get("bach_obstruction_chain_map_exact") is True
        and source_flags.get("einstein_defect_chain_map_exact") is True
        and source_flags.get("matter_inclusive_bv_complex_constructed") is False
        and source_flags.get("lorentzian_causal_claim") is False,
        "compensated sourced-defect claim boundary drifted",
    )
    source_fibers = sourced.get("compatible_source_fibers", {})
    _require(
        source_fibers.get("generic", {}).get("compatible_source_dimension") == 1
        and source_fibers.get("null", {}).get("compatible_source_dimension") == 5,
        "compatible-source fiber inventory drifted",
    )


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _verify_inputs(records)

    return {
        "schema": "pure-weyl-einstein-sector-theorem-v1",
        "result_id": "CLASSICAL_EINSTEIN_SECTOR_THEOREM",
        "result_state": "PROVED_WITH_OPEN_BOUNDARY_RAIL",
        "source_commit": "46d95a1f6f04e446a4d5290ec5666af3af6cd392",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": {
            "name": "Einstein locus and closed-cylinder state separation",
            "hypotheses": [
                "dimension is four",
                "g is a smooth pseudo-Riemannian Einstein metric with Ric(g)=Lambda g",
                "the pure-Weyl equation is B_mn(g)=0",
                "state claims use the certified linearized unit-cylinder polarization",
            ],
            "conclusions": [
                "every Einstein metric is Bach-flat",
                "Einstein solutions map to the conformally-Einstein locus of pure-Weyl solutions",
                "the converse fails in general: Bach-flat does not imply conformally Einstein",
                "this is an exact solution sector, not an equality of theories or a global Weyl gauge slice",
                "no inclusion of observable algebras follows without a boundary/BFV comparison map",
            ],
            "exact_identity_proof": [
                "Ric=Lambda g implies R=4 Lambda and parallel Schouten tensor",
                "the contracted Bianchi identity then gives divergence-free Weyl curvature",
                "the double-divergence term in B_mn vanishes",
                "the Ricci-Weyl contraction is Lambda times a trace of Weyl and vanishes",
                "therefore B_mn=0",
            ],
            "quotient_caveat": (
                "After quotienting Einstein solutions by Diff and Weyl solutions by "
                "Diff x Weyl, the natural object is a map onto the conformally-Einstein "
                "locus; set-theoretic injectivity is not asserted."
            ),
        },
        "one_particle_before_residual_quotient": {
            "local_bv_cohomology": "W+ direct-sum W-",
            "weyl_symbol_quotient_dimension": 2,
            "helicity_weights": ["+2", "-2"],
            "cylinder_realization": (
                "the parity-complete E tower starts at energy two; A and L are the "
                "additional conformal-gravity towers"
            ),
            "interpretation": (
                "the usual radiative spin-two modes exist in local oscillator/BV "
                "cohomology before residual SO(4,2) reduction"
            ),
        },
        "closed_cylinder_residual_result": {
            "boundary_problem": "closed cylinder with all fifteen residual generators gauged",
            "one_particle_h4": 0,
            "reason": (
                "gauging D permits the Cartan contraction of every nonzero total-energy "
                "one-particle cochain; this is a global residual quotient, not local "
                "elimination of radiative helicities"
            ),
            "surviving_h4": ["W_+^2", "W_-^2"],
            "survivor_role": "ghost-dressed deformation/vertex classes, not particles",
            "non_contradiction": (
                "if cylinder time translation or asymptotic symmetries are retained as "
                "physical charges, the absolute residual complex used here is not the "
                "physical-state complex"
            ),
        },
        "compensated_local_symbol_snapshot": {
            "phase": "flat constant compensator v!=0 with c1=alpha=-1 and v=1 fixture",
            "generic_cohomology": [0, 0, 0, 0],
            "nonzero_null_cohomology": [0, 2, 2, 0],
            "second_root_cohomology": [0, 5, 5, 0],
            "representative_data": "exact inclusions, pi_cl projections, and homotopies",
            "pairing": "nondegenerate odd BV pairing between p and -p cohomology fibers",
            "interpretation": (
                "the two null degree-zero classes are local helicity-two precursors "
                "before the global residual quotient; the five second-root classes "
                "are the extra Einstein--Weyl branch"
            ),
            "scope": (
                "REDUCED-MODE symbol fibers only; p=0 global modes, the physical "
                "Cauchy/radiative pairing, global classical freeze, and causal "
                "scattering remain open"
            ),
        },
        "compensated_sourced_defect_chain_map": {
            "source_complex": "external (T_mn,J_phi) Diff x Weyl Ward complex",
            "obstruction_chain_map": "Q(T) intertwines Ward rows exactly",
            "defect_chain_map": "Delta=G1(h_hat)-T/c1 intertwines Diff and divergence rows",
            "residual_identity": "E_EW=(c1 I+2 alpha Q)Delta+(2 alpha/c1)Q(T)",
            "generic_source_dimensions": {"ward_cycles": 6, "Q_compatible": 1},
            "null_source_dimensions": {"ward_cycles": 6, "Q_compatible": 5},
            "scope": (
                "universal external-source chain theorem only; a matter-inclusive "
                "BV lift, causal propagation, nonlinear closure, and scattering remain open"
            ),
        },
        "classification": {
            "einstein_solutions_subset_conformal_solutions": "ESTABLISHED_AS_A_MAP_OF_SOLUTION_LOCI",
            "einstein_observables_subset_reduced_conformal_observables": "NOT_ESTABLISHED",
            "einstein_as_global_gauge_slice": "FALSE_IN_GENERAL",
            "einstein_as_exact_solution_sector": "ESTABLISHED",
            "einstein_as_boundary_selected_sector": "CONDITIONAL_ON_ADDITIONAL_BOUNDARY_DATA",
            "einstein_as_phase_or_effective_sector": "MODEL_DEPENDENT_NOT_ESTABLISHED_HERE",
        },
        "background_inventory": {
            "survive": [
                "all four-dimensional Ricci-flat metrics",
                "all four-dimensional Einstein metrics with cosmological constant",
                "their Weyl transforms as pure-Weyl solutions",
            ],
            "additional_conformal_solutions": [
                "Bach-flat metrics that are not conformally Einstein",
                "linearized A and L cylinder towers in addition to the E tower",
            ],
        },
        "scale_statement": {
            "pure_weyl": "no intrinsic Einstein-Hilbert mass scale",
            "possible_mechanisms": [
                "a Weyl compensator with a phi^2 R coupling and nonzero gauge-fixed value",
                "matter expectation values or spontaneous Weyl breaking",
                "a boundary/background cosmological scale",
            ],
            "status": "NO_MECHANISM_CERTIFIED_IN_THIS_THEOREM",
        },
        "boundary_and_cauchy_ledger": [
            {
                "problem": "asymptotically de Sitter or Euclidean anti-de Sitter",
                "prescription": "Maldacena-type Neumann boundary condition",
                "status": "LITERATURE_ESTABLISHED_AT_SEMICLASSICAL_OR_TREE_LEVEL",
                "dependency_boundary": "not a repository Lorentzian scattering certificate",
                "source": "https://arxiv.org/abs/1105.5632",
            },
            {
                "problem": "asymptotically flat Einstein scattering",
                "prescription": (
                    "retain asymptotic Poincare/BMS charges and eliminate non-Einstein "
                    "fourth-order data by a nonlinear Einstein-sector boundary condition"
                ),
                "status": "OPEN",
                "required_dependency_tag": "LORENTZIAN-CAUSAL",
            },
            {
                "problem": "Einstein Cauchy data on the closed cylinder",
                "prescription": (
                    "use a relative or boundary BFV complex with D as Hamiltonian, then "
                    "prove preservation of the Einstein constraint"
                ),
                "status": "OPEN",
                "required_dependency_tag": "LORENTZIAN-CAUSAL",
            },
        ],
        "next_theorem_commission": {
            "name": "Asymptotically flat Einstein scattering sector inside pure Weyl gravity",
            "dependency_tag": "LORENTZIAN-CAUSAL",
            "status": "OPEN_FAIL_CLOSED",
            "load_bearing_question": (
                "Is the Einstein sector dynamically and causally closed under the "
                "chosen Lorentzian radiative boundary conditions?"
            ),
            "target": (
                "construct an Einstein radiative subcomplex of the asymptotically flat "
                "Bach complex and prove that causal evolution, boundary BFV reduction, "
                "and the radiative symplectic form restrict to it"
            ),
            "obligations": [
                {
                    "id": "AF-E1",
                    "claim": "admissible asymptotically flat function spaces and fourth-order data are specified",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E2",
                    "claim": "retarded and advanced Bach complexes with null-infinity boundary data are constructed",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E3",
                    "claim": "charged asymptotic conformal transformations are separated from gauge transformations",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E4",
                    "claim": "the non-Einstein branch is excluded by causal admissibility rather than nonlocal future data",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E5",
                    "claim": "nonlinear Bach evolution preserves the Einstein initial-data constraint",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E6",
                    "claim": "the Green/current pairing restricts to the radiative symplectic form at null infinity",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E7",
                    "claim": "the resulting Einstein asymptotic state space is exactly helicity plus or minus two",
                    "status": "OPEN",
                },
                {
                    "id": "AF-E8",
                    "claim": "all additional Weyl solutions are classified as extra radiative channels or non-radiative data",
                    "status": "OPEN",
                },
            ],
            "promotion_rule": (
                "No Einstein scattering-sector claim may be promoted until AF-E1 through "
                "AF-E8 have machine-readable certificates and the affected Lorentzian "
                "certificate chain passes."
            ),
        },
        "external_sources": [
            {
                "claim": "Neumann boundary selection of Einstein solutions in asymptotic dS/EAdS",
                "url": "https://arxiv.org/abs/1105.5632",
            },
            {
                "claim": "existence of Bach-flat metrics that are not conformally Einstein",
                "url": "https://arxiv.org/abs/1303.5781",
            },
        ],
        "claim_flags": {
            "exact_local_solution_inclusion": True,
            "local_helicity_two_modes_present": True,
            "closed_cylinder_one_particle_residual_vanishing": True,
            "observable_algebra_embedding": False,
            "asymptotically_flat_scattering_recovered": False,
            "einstein_cauchy_problem_recovered": False,
            "einstein_hilbert_scale_generated": False,
            "einstein_sector_causally_closed_at_null_infinity": False,
            "ordinary_helicity_two_scattering_space_recovered": False,
            "extra_asymptotic_weyl_channels_classified": False,
            "lorentzian_quantum_theorem": False,
        },
        "inputs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "verification_command": (
            "python3 -m bridge.einstein_sector.certificate --verify "
            "bridge/certificates/einstein_sector_theorem.json"
        ),
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    actual = _load(path)
    expected = build_certificate()
    _require(actual == expected, f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the canonical certificate")
    parser.add_argument("--verify", type=Path, help="verify a certificate against current inputs")
    args = parser.parse_args()

    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
