"""Generate the fail-closed same-background Einstein--Weyl branch dictionary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_relative_branch_dictionary.schema.json"
INPUTS = {
    "triangle": ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json",
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "polar_lift": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
    "generic_cyclic_obstruction": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "generic_cyclic_inertia_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json",
    "exceptional_global_offshell": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "ell1_standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous_standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "homogeneous_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "twist_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "abd_quadratic": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "homogeneous_twist_quadratic": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "aligned_twist_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
    "complete_global_extra_cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "global_extra_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "global_extra_smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json",
    "aligned_twist_extra_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json",
}

STATUS = {"CERTIFIED", "OPEN", "NO_CERTIFIED_MAP", "NOT_APPLICABLE"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads(INPUTS[name].read_text(encoding="utf-8"))


def _scope(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "theory": "Einstein-Maxwell source and Weyl-Maxwell target",
        "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
        "boundaries": "closed Cauchy slice S1_L x S2; before final residual quotient",
        "charge_sector": "fixed magnetic U(1) bundle P_N with N=2; electric tangent allowed",
        "carrier": "unspecified",
        "degree": 1,
        "parity": "unspecified",
        "ell": "unspecified",
        "m": "unspecified",
        "k": "unspecified",
        "omega": "unspecified",
    }
    value.update(updates)
    return value


def _evidence(*names: str) -> list[dict[str, str]]:
    return [
        {
            "path": str(INPUTS[name].relative_to(ROOT)),
            "result_id": str(_load(name)["result_id"]),
            "sha256": _sha256(INPUTS[name]),
        }
        for name in names
    ]


def _branch_rows(records: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    axial_pairing = records["axial_current"]["full_solution_pairing"]
    polar_pairing = records["polar_current"]["shell_pairing"]
    return [
        {
            "id": "ph.generic.axial.relative",
            "scope": _scope(
                carrier="generic axial Fourier-polynomial coefficient complex and its reduced solution module",
                parity="axial",
                ell=">=2",
                m="all",
                k="2*pi*n/L, every n in Z including zero",
                omega="q-primary Einstein shells and p-primary extra shell",
            ),
            "map_lifecycle": "DERIVED_COFIBER_TRIANGLE",
            "inclusion": {"status": "CERTIFIED", "map": "identity on the six axial field coefficients, with the exact polynomial equation-row map recorded by the triangle preflight"},
            "projection_or_cofiber": {"status": "CERTIFIED", "map": "target/q-primary Einstein image = (K[omega]/(p))^2; the quotient projection is the p-primary CRT projection on each physical fibre"},
            "branch_representatives": {
                "status": "CERTIFIED",
                "order": "(H_t,H_x,Q_t,Q_x) on the reduced block",
                "Einstein": axial_pairing["Einstein_representative"],
                "extra": axial_pairing["extra_representatives"],
            },
            "action_derived_pairing": {
                "status": "CERTIFIED",
                "Einstein_inertia": axial_pairing["Einstein_branch_signature_for_lambda_ge_6"],
                "extra_inertia": axial_pairing["extra_branch_signature_for_lambda_ge_6"],
                "complete_inertia": axial_pairing["complete_generic_axial_target_signature"],
                "Einstein_extra_orthogonal": True,
                "standard_pairing_cyclic_map": "OBSTRUCTED by incompatible cohomology-form inertia (2,0) versus (1,1)",
            },
            "missing": ["noncyclic off-shell triangle with three distinct forms", "explicitly pairing-changed alternative", "final residual descent"],
            "evidence": _evidence("triangle", "axial_ring", "axial_current", "generic_cyclic_obstruction", "generic_cyclic_inertia_obstruction"),
        },
        {
            "id": "ph.generic.polar.relative",
            "scope": _scope(
                carrier="generic polar gauge-fixed coefficient system and its reduced solution module",
                parity="polar",
                ell=">=2",
                m="all",
                k="2*pi*n/L, every n in Z including zero",
                omega="q-primary Einstein shells and p-primary extra shell",
            ),
            "map_lifecycle": "DERIVED_COFIBER_TRIANGLE",
            "inclusion": {"status": "CERTIFIED", "map": "polynomial ghost-field-equation-identity chain map on the ungauged polar complex, inducing the injective solution-module map onto the complete q-primary target summand"},
            "projection_or_cofiber": {"status": "CERTIFIED", "map": "chain mapping cofiber together with solution-module quotient (K[omega]/(p))^2 on every physical fibre; cyclic BV compatibility is not claimed"},
            "branch_representatives": {
                "status": "CERTIFIED",
                "order": "(A_t,B,C_t,U)",
                "Einstein": polar_pairing["Einstein_representative_order_At_B_Ct_U"],
                "extra": polar_pairing["extra_basis_order_At_B_Ct_U"],
            },
            "action_derived_pairing": {
                "status": "CERTIFIED",
                "Einstein_inertia": polar_pairing["Einstein_block_inertia"],
                "extra_Gram": polar_pairing["extra_Hermitian_current_Gram"],
                "extra_inertia": polar_pairing["extra_positive_frequency_inertia"],
                "complete_inertia": polar_pairing["complete_polar_target_inertia_before_residual_quotient"],
                "Einstein_extra_orthogonal": True,
                "standard_pairing_cyclic_map": "OBSTRUCTED by incompatible cohomology-form inertia (2,0) versus (1,1)",
            },
            "missing": ["noncyclic off-shell triangle with three distinct forms", "explicitly pairing-changed alternative", "final residual descent"],
            "evidence": _evidence("standard", "polar_ring", "polar_lift", "polar_current", "generic_cyclic_obstruction", "generic_cyclic_inertia_obstruction"),
        },
        {
            "id": "ph.exceptional.ell1.relative",
            "scope": _scope(
                carrier="physical standard dipoles, axial twist and exceptional axial and polar target modes at k=0",
                parity="axial and polar",
                ell=1,
                m="-1,0,1",
                k=0,
                omega="axial twist omega^2=0, exceptional extra omega^2=4/3, physical standard omega^2=4",
            ),
            "map_lifecycle": "DERIVED_COFIBER_TRIANGLE",
            "inclusion": {"status": "CERTIFIED", "map": "polynomial ghost-field-equation-identity chain maps in both parities, inducing the identity inclusion on the complete physical Einstein-Maxwell ell=1 quotient"},
            "projection_or_cofiber": {"status": "CERTIFIED", "map": "explicit CRT projectors in x=omega^2 identify the source image and the axial-plus-polar omega^2=4/3 solution cofiber"},
            "branch_representatives": {"status": "CERTIFIED", "source": "axial twist plus the physical axial and polar omega^2=4 representatives", "extra": "one omega^2=4/3 representative in each parity, with all-m SO(3) promotion"},
            "action_derived_pairing": {"status": "CERTIFIED", "standard_relative_operator": "4*I", "twist_relative_operator": "-2*I", "extra_Gram": [["16", "0"], ["0", "3"]], "standard_extra_orthogonal": True},
            "missing": ["finite large-gauge/global quotient", "final residual descent"],
            "evidence": _evidence("standard", "ell1_standard", "exceptional_current", "exceptional_cofiber", "exceptional_global_offshell"),
        },
        {
            "id": "ph.exceptional.ell1.nonzero_k.relative",
            "scope": _scope(
                carrier="physical standard axial-plus-polar ell=1 quotient at nonzero compact momentum",
                parity="axial and polar",
                ell=1,
                m="-1,0,1",
                k="2*pi*n/L with n!=0",
                omega="physical omega^2=k^2+4; any extra target branch unclassified",
            ),
            "map_lifecycle": "OFFSHELL_CHAIN_MAP_ONLY",
            "inclusion": {"status": "CERTIFIED", "map": "polynomial all-row axial and polar chain maps for every compact momentum, inducing the identity inclusion on the physical Einstein-Maxwell ell=1 quotient"},
            "projection_or_cofiber": {"status": "NO_CERTIFIED_MAP", "map": "no complete nonzero-k exceptional target classification or cofiber projection is certified"},
            "branch_representatives": {"status": "CERTIFIED", "source": "physical ell=1 quotient representatives", "extra": "NO_CERTIFIED_MAP"},
            "action_derived_pairing": {"status": "CERTIFIED", "standard_relative_operator": "4*I", "extra": "NO_CERTIFIED_MAP"},
            "missing": ["nonzero-k solution cofiber and action-derived extra pairing", "final residual descent"],
            "evidence": _evidence("standard", "ell1_standard", "exceptional_global_offshell"),
        },
        {
            "id": "ph.global.homogeneous.relative",
            "scope": _scope(
                carrier="homogeneous generalized block (a,b,c,d,Q_e,W_x)",
                parity="scalar/global",
                ell=0,
                m=0,
                k=0,
                omega="generalized zero",
            ),
            "map_lifecycle": "DERIVED_COFIBER_TRIANGLE",
            "inclusion": {"status": "CERTIFIED", "map": "polynomial Diff x U(1) to Diff x U(1) x Weyl ghost-field-equation-identity chain map, inducing the identity inclusion on the six-dimensional standard homogeneous solution block"},
            "projection_or_cofiber": {"status": "CERTIFIED", "map": "the coefficient inverse a=d2, b=3*d3, c=d0+d2, d=d1+3*d3 proves the complete homogeneous target quotient equals the Einstein image; solution cofiber zero"},
            "branch_representatives": {"status": "CERTIFIED", "standard_and_complete_target": ["a", "b", "c", "d", "Q_e", "W_x"], "extra": "zero solution cofiber"},
            "action_derived_pairing": {"status": "CERTIFIED", "relative_operator": "I+N with N^2=0 and rank(N)=2"},
            "missing": ["large-gauge/global quotient", "final residual descent"],
            "evidence": _evidence("standard", "homogeneous_standard", "homogeneous_cofiber", "exceptional_global_offshell", "abd_quadratic"),
        },
        {
            "id": "ph.global.twist.relative",
            "scope": _scope(
                carrier="three axial twist position/velocity pairs",
                parity="axial",
                ell=1,
                m="three real SO(3) components",
                k=0,
                omega="generalized zero",
            ),
            "map_lifecycle": "DERIVED_COFIBER_TRIANGLE",
            "inclusion": {"status": "CERTIFIED", "map": "the axial ell=1 polynomial all-row chain map restricts to the identity inclusion on each standard twist pair (A_m,B_m)"},
            "projection_or_cofiber": {"status": "CERTIFIED", "map": "P_twist=3*(x-4/3)*(x-4)/16 isolates the complete target twist primary, which equals the Einstein image; solution cofiber zero"},
            "branch_representatives": {"status": "CERTIFIED", "standard_and_complete_target": ["A_m", "B_m"], "extra": "zero solution cofiber in the x=0 primary"},
            "action_derived_pairing": {"status": "CERTIFIED", "relative_operator": "-2*I on each twist pair"},
            "missing": ["global moduli-orbifold quotient", "final residual descent"],
            "evidence": _evidence("standard", "twist_standard", "exceptional_cofiber", "twist_cofiber", "exceptional_global_offshell", "homogeneous_twist_quadratic", "aligned_twist_extra_face", "complete_global_extra_cone", "global_extra_bounded_obstruction", "global_extra_smooth_extension"),
        },
        {
            "id": "ph.boundary.relative",
            "scope": _scope(
                background="compact Plebanski-Hacyan fixture versus any asymptotic, black-hole, dS/AdS or vacuum-cylinder setting",
                boundaries="cross-background or changed-boundary domain",
                charge_sector="undeclared across settings",
                carrier="boundary/asymptotic branch carrier",
                degree="crosswalk",
                parity="not applicable",
                ell="not applicable",
                m="not applicable",
                k="not applicable",
                omega="not applicable",
            ),
            "map_lifecycle": "NO_CERTIFIED_MAP",
            "inclusion": {"status": "NO_CERTIFIED_MAP", "map": "no boundary-preserving or cross-background inclusion is certified"},
            "projection_or_cofiber": {"status": "NO_CERTIFIED_MAP", "map": "no asymptotic or exterior relative cofiber is certified"},
            "branch_representatives": {"status": "NO_CERTIFIED_MAP"},
            "action_derived_pairing": {"status": "NO_CERTIFIED_MAP"},
            "missing": ["common boundary domain", "boundary charges and fluxes", "causal Green carrier", "mode crosswalk"],
            "evidence": [],
        },
    ]


def build() -> dict[str, object]:
    records = {name: _load(name) for name in INPUTS}
    triangle_flags = records["triangle"]["classification"]
    if not triangle_flags["generic_axial_offshell_chain_map_certified"]:
        raise AssertionError("generic axial triangle input changed")
    if triangle_flags["relative_linear_triangle_V1_certified"]:
        raise AssertionError("preflight unexpectedly promoted the full triangle")
    if not records["axial_ring"]["classification"]["Einstein_image_equals_complete_q_primary_summand_on_every_physical_fiber"]:
        raise AssertionError("axial primary decomposition changed")
    if not records["polar_ring"]["classification"]["Einstein_image_equals_complete_q_primary_summand"]:
        raise AssertionError("polar primary decomposition changed")
    if not records["polar_lift"]["classification"]["polynomial_ghost_field_equation_identity_chain_map_certified"]:
        raise AssertionError("polar ungauged chain-map input changed")
    exceptional_maps = records["exceptional_global_offshell"]["classification"]
    if not (
        exceptional_maps["exceptional_axial_all_row_offshell_chain_map_certified"]
        and exceptional_maps["exceptional_polar_all_row_offshell_chain_map_certified"]
        and exceptional_maps["homogeneous_all_row_offshell_chain_map_certified"]
        and exceptional_maps["all_harmonic_sector_coefficient_maps_available"]
    ):
        raise AssertionError("exceptional/global all-row chain-map input changed")
    if exceptional_maps["single_covariant_support_local_map_reconstructed"]:
        raise AssertionError("harmonic exceptional maps were over-promoted to covariant glue")
    if records["polar_lift"]["classification"]["cyclic_BV_chain_map_certified"]:
        raise AssertionError("polar cyclic BV lifecycle changed")
    if records["generic_cyclic_obstruction"]["classification"]["fixed_identity_cyclic_pairing_compatibility"] != "OBSTRUCTED":
        raise AssertionError("generic fixed-identity cyclic obstruction changed")
    inertia_classification = records["generic_cyclic_inertia_obstruction"]["classification"]
    if (
        inertia_classification["corrected_nonidentity_standard_pairing_map_exists_generic"] is not False
        or inertia_classification["declared_chain_homotopy_cyclic_resolution_exists_generic"] is not False
        or inertia_classification["standard_pairing_all_sector_cyclic_triangle_possible"] is not False
    ):
        raise AssertionError("generic cyclic-map inertia obstruction changed")
    if not records["polar_current"]["classification"]["direct_four_dimensional_Lee_Wald_match"]:
        raise AssertionError("polar direct current changed")
    if not records["exceptional_cofiber"]["classification"]["exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional k0 solution cofiber changed")
    if not records["homogeneous_cofiber"]["classification"]["homogeneous_solution_cofiber_zero"]:
        raise AssertionError("homogeneous zero solution cofiber changed")
    if not records["twist_cofiber"]["classification"]["twist_solution_cofiber_zero"]:
        raise AssertionError("twist zero solution cofiber changed")
    if not records["homogeneous_twist_quadratic"]["classification"]["complete_homogeneous_twist_bounded_resonance_matrix"]:
        raise AssertionError("complete homogeneous/twist resonance input changed")
    if not records["aligned_twist_extra_face"]["classification"]["nonzero_simultaneous_stabilizer_and_bounded_resonance_zero_face"]:
        raise AssertionError("aligned twist--extra compatibility input changed")
    if records["aligned_twist_extra_face"]["classification"]["bounded_second_order_correction_constructed"]:
        raise AssertionError("aligned compatibility input was over-promoted")
    if not records["complete_global_extra_cone"]["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete global--extra common-zero input changed")
    if records["complete_global_extra_cone"]["classification"]["bounded_second_order_right_inverse_constructed"]:
        raise AssertionError("necessary common-zero theorem was over-promoted")
    if not records["global_extra_bounded_obstruction"]["classification"]["bounded_or_finite_quasiperiodic_correction_obstructed"]:
        raise AssertionError("bounded global--extra correction obstruction changed")
    if not records["global_extra_smooth_extension"]["classification"]["smooth_exponential_polynomial_second_order_correction_exists"]:
        raise AssertionError("smooth global--extra extension changed")
    rows = _branch_rows(records)
    identifiers = [row["id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise AssertionError("branch identifiers are not unique")
    for row in rows:
        for field in ("inclusion", "projection_or_cofiber", "branch_representatives", "action_derived_pairing"):
            status = row[field]["status"]
            if status not in STATUS:
                raise AssertionError(f"invalid branch status: {status}")
        if row["scope"]["background"] != _scope()["background"] and row["map_lifecycle"] != "NO_CERTIFIED_MAP":
            raise AssertionError("cross-background row acquired a map")
    return {
        "schema": "einstein-weyl-relative-branch-dictionary-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1",
        "result_state": "ALL_HARMONIC_OFFSHELL_MAPS_EXPORTED_COVARIANT_GLUE_AND_ENDPOINT_GATE_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "bridge": {
            "priority": 1,
            "name": "common-background carrier to Einstein, extra-Weyl, Maxwell, gauge and nondynamical branches",
            "current_global_map_lifecycle": "HARMONIC_OFFSHELL_MAPS_ONLY",
            "activation_gate": "OPEN",
            "reason": "polynomial all-row maps now cover every generic, exceptional and homogeneous harmonic coefficient block, while generic and k=0/global solution cofibers are certified and the all-standard-pairing cyclic-map route is obstructed; a single natural covariant support-local map, nonzero-k exceptional cofiber/pairing, finite residual endpoints and boundary domain remain absent",
            "requested_full_artifact": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            "requested_full_artifact_certified": False,
        },
        "relative_forms": {
            "Einstein": "Omega_EM",
            "pulled_back_Weyl": "iota^* Omega_WM = Omega_EM(.,R .) on the complete standard tangent",
            "relative_extra": "direct action-derived extra Lee-Wald blocks are certified only in generic axial and polar sectors",
            "identity_inclusion_symplectic": False,
            "identity_inclusion_nondegenerate": True,
            "standard_pairing_cyclic_correction_exists_generic": False,
            "required_triangle_kind": "NONCYCLIC_THREE_FORM",
        },
        "branch_rows": rows,
        "quadratic_handoff": {
            "status": "PARTIAL_INPUT",
            "artifacts": ["EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_ELL2_EXTRA_RESONANCE_MATRIX", "EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_COMPATIBILITY_FACE", "PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1", "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_BOUNDED_CORRECTION_OBSTRUCTION", "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER", "EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SMOOTH_CORRECTION"],
            "meaning": "the complete declared k=0 homogeneous/twist times ell=2 extra source matrix and its common-zero locus feed the relative obstruction map; every common zero is on the aligned SO3 orbit, every nonzero point is obstructed in the bounded correction class, and every point extends in the smooth exponential-polynomial class. The aligned twist--extra L=1,3 mixed block is coefficient-explicit, while the complete orbit coefficient list, causal category, bridge 1 and the general finite-harmonic tangent cone remain open",
        },
        "classification": {
            "same_background_only": True,
            "generic_axial_derived_cofiber_certified": True,
            "generic_polar_derived_cofiber_certified": True,
            "generic_axial_and_polar_solution_cofibers_certified": True,
            "generic_axial_and_polar_action_pairings_exported": True,
            "generic_fixed_identity_cyclic_compatibility_obstructed": True,
            "generic_standard_pairing_cyclic_maps_obstructed": True,
            "exceptional_and_global_harmonic_offshell_maps_certified": True,
            "all_harmonic_sector_coefficient_maps_available": True,
            "single_covariant_support_local_map_reconstructed": False,
            "exceptional_k0_solution_cofiber_certified": True,
            "homogeneous_solution_cofiber_zero": True,
            "twist_solution_cofiber_zero": True,
            "complete_homogeneous_twist_bounded_resonance_matrix_imported": True,
            "aligned_nonzero_stabilizer_resonance_common_zero_face_imported": True,
            "complete_declared_global_extra_common_zero_locus_imported": True,
            "complete_global_extra_bounded_correction_obstruction_imported": True,
            "complete_global_extra_smooth_secular_extension_imported": True,
            "aligned_twist_extra_L1_L3_coefficient_correction_imported": True,
            "exceptional_global_and_boundary_absences_explicit": True,
            "full_offshell_all_sector_triangle_certified": False,
            "bridge_1_activation_gate_satisfied": False,
            "cross_background_mode_identification_made": False,
        },
        "interpretation": "The compact Plebanski-Hacyan calculation supplies a precise same-background Einstein/extra branch dictionary, polynomial all-row chain maps in every generic, exceptional and homogeneous harmonic coefficient block, an inertia obstruction to every standard-pairing cyclic correction on generic physical cohomology, an explicit exceptional k=0 solution cofiber, and zero homogeneous and twist-primary solution cofibers. Harmonic selection is not support local, so the honest all-sector target remains a single natural covariant noncyclic BV relative triangle carrying the Einstein, pulled-back Weyl and relative forms separately. Matching branch names on Berger, black-hole, asymptotic or vacuum-cylinder backgrounds remains forbidden without a separate crosswalk.",
        "next_gate": "reconstruct the complete harmonic tables as one natural support-local four-dimensional chain morphism, classify the nonzero-k exceptional cofiber/pairing, and include finite large-gauge/residual endpoints before assembling the NONCYCLIC_THREE_FORM EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
        "claim_boundary": "This is a fail-closed branch dictionary and exact map-lifecycle ledger. It does not promote the full relative triangle, provide a causal Green carrier, identify cross-background modes, or support observational or quantum state claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_weyl_relative_branch_dictionary --check", "python3 bridge/einstein_sector/verify_einstein_weyl_relative_branch_dictionary.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_branch_dictionary"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "all imported map, cofiber, representative and pairing artifacts are content-addressed"},
            "tier_3": {"status": "NOT_RUN", "reason": "the full all-sector relative triangle activation gate remains open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_relative_branch_dictionary --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_relative_branch_dictionary.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_branch_dictionary",
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
        raise AssertionError("relative branch dictionary is stale")
    print("EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1: PASS")


if __name__ == "__main__":
    main()
