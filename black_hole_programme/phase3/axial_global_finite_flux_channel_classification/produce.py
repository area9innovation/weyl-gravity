"""Produce the fail-closed axial global finite-flux classifier disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
ATLAS = ROOT / (
    "residual_atlas/"
    "phase3-black-hole-axial-global-finite-flux-channel-classification-"
    "fragment-v1.json"
)
ENDPOINT = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"
ENDPOINT_SHA256 = "59fb9b443ce0b92ce016f53c376cb367bcf004e00d1b241ad22ec925e99deed2"
EXPECTED_CONNECTION = ROOT / (
    "black_hole_programme/phase3/"
    "axial_global_connection_matrix_v5/chunks/channel-handoff-v6.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crosswalk() -> dict:
    return {
        "raw_horizon_order": [
            "XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus"
        ],
        "public_horizon_order": [
            "XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout"
        ],
        "public_index_to_raw_index": [0, 1, 3, 5, 2, 4],
        "raw_index_to_public_index": [0, 1, 4, 2, 5, 3],
        "raw_future_regular_selector": [0, 1, 2],
        "public_future_regular_selector": [0, 1, 4],
        "future_regular_origin_order": ["XH0a", "XH0b", "EH0"],
        "additional_origin_columns": [0, 1],
        "einstein_origin_columns": [2],
        "infinity_order": ["XI0", "XI1", "XI2", "XI3", "EI0", "EI2"],
        "Iminus_selector": [0, 1, 4],
        "Iplus_selector": [2, 3, 5],
    }


def missing_fields() -> list[str]:
    return [
        "global_connection_certified=true on a finite rational subdivision of [1/2,3/4]",
        "one validated correlated 6x3 connection enclosure per frequency cell",
        "the frozen infinity order XI0,XI1,XI2,XI3,EI0,EI2",
        "the raw/public horizon crosswalk and raw future-regular selector [0,1,2]",
        "whole-cell exact or validated ranks for T, Pminus*T and Pplus*T",
        "whole-cell kernels, exceptional walls and no-crossing witnesses",
        "realified pulled-back Gram enclosures with exact rank/radical/inertia witnesses",
        "the future-horizon outward Gram in the same coefficient basis",
        "the orientation-correct current conservation defect GHplus+Tplus^dagger*Gplus*Tplus-Tminus^dagger*Gminus*Tminus",
        "uniform multiplier and inverse bounds needed for the L2 wave-packet extension",
        "content hashes for every affine handoff and independent replay receipt",
    ]


def build_document() -> dict:
    if sha256(ENDPOINT) != ENDPOINT_SHA256:
        raise RuntimeError("pinned endpoint certificate hash changed")
    endpoint = json.loads(ENDPOINT.read_text())
    if endpoint["result_id"] != "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1":
        raise RuntimeError("endpoint result identity changed")
    if not endpoint["claim_flags"]["endpoint_rank_radical_inertia_certified"]:
        raise RuntimeError("endpoint Gram input is not certified")

    connection_present = EXPECTED_CONNECTION.exists()
    status = (
        "INCOMPATIBLE_GLOBAL_CONNECTION"
        if connection_present
        else "MISSING_GLOBAL_CONNECTION"
    )
    # Deliberately refuse to activate on an unknown future payload.  The v6
    # producer must emit the typed handoff listed below; a point matrix or a
    # v5 runtime shortfall is not silently adapted.
    return {
        "schema": (
            "phase3-black-hole-axial-global-finite-flux-channel-"
            "classification-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_GLOBAL_FINITE_FLUX_CHANNEL_"
            "CLASSIFICATION_V1"
        ),
        "result_token": "MISSING_GLOBAL_CONNECTION_NOT_ACTIVATED",
        "lifecycle": "NOT_ACTIVATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior with M=1",
            "sector": "axial ell=2",
            "frequency_interval": ["1/2", "3/4"],
            "positive_frequency_core": "C_c^infinity((1/2,3/4);C^3)",
            "completion": "L2([1/2,3/4];C^3)",
        },
        "activation": {
            "status": status,
            "expected_handoff_path": str(EXPECTED_CONNECTION.relative_to(ROOT)),
            "expected_handoff_schema": "phase3-axial-global-channel-handoff-v1",
            "path_present": connection_present,
            "missing_or_unverified_fields": missing_fields(),
            "rule": (
                "No cell is classified until the complete typed handoff and "
                "whole-cell witnesses pass an independent verifier."
            ),
        },
        "basis_contract": crosswalk(),
        "endpoint_input": {
            "path": str(ENDPOINT.relative_to(ROOT)),
            "sha256": ENDPOINT_SHA256,
            "result_id": endpoint["result_id"],
            "Iminus_basis": endpoint["endpoint_grams"]["Iminus"]["basis"],
            "Iplus_basis": endpoint["endpoint_grams"]["Iplus"]["basis"],
            "Iminus_inertia": endpoint["common_verdict"][
                "inertia_for_alpha_W_positive"
            ],
            "Iplus_inertia": endpoint["common_verdict"][
                "inertia_for_alpha_W_positive"
            ],
        },
        "classifier_contract": {
            "populated_maps": "Cminus=Pminus*T and Cplus=Pplus*T",
            "pullback_forms": (
                "gminus=Cminus^dagger*Gminus*Cminus and "
                "gplus=Cplus^dagger*Gplus*Cplus"
            ),
            "populated_radical_dimension": (
                "nullity(g_endpoint)-nullity(C_endpoint)"
            ),
            "physical_quotient_dimension": "rank(g_endpoint)",
            "realification": "[[Re(g),-Im(g)],[Im(g),Re(g)]]",
            "conservation": "GHplus+gplus-gminus=0",
            "one_sided_relation": (
                "If Cminus is invertible and GHplus is certified, map Iminus "
                "to Hplus direct_sum Iplus; never call it a full scattering "
                "matrix because the Hminus incoming block is absent."
            ),
            "wavepacket_extension": (
                "A finite rational cell cover plus uniform multiplier bounds "
                "extends the pointwise quotient classification to the "
                "declared compactly supported core and L2 completion."
            ),
            "exact_oracle_boundary": (
                "classifier.classify_exact_cell is a correctness oracle for "
                "constant exact fixtures. It cannot activate a parameter "
                "cell; interval activation requires the separately validated "
                "affine-cell witnesses listed in activation."
            ),
            "affine_interval_adapter": (
                "affine_adapter validates correlated center-plus-linear-plus-"
                "remainder pullbacks, proves 3x3 rank by a determinant "
                "enclosure, and certifies whole-cell Hermitian inertia by an "
                "exact inverse-perturbation bound; it remains unexercised "
                "until the typed global handoff exists."
            ),
        },
        "classification": {
            "status": "NOT_COMPUTED",
            "frequency_cells": [],
            "exceptional_cells": [],
            "global_additional_channel_status": "UNPOPULATED_NOT_ZERO",
            "reason": "validated global connection handoff is absent",
        },
        "forbidden_promotions": {
            "formal_infinity_vector_called_global": False,
            "public_selector_applied_to_raw_initializer": False,
            "radial_current_identified_with_null_flux": False,
            "exceptional_wall_flattened": False,
            "partial_relation_called_full_scattering": False,
            "positive_metric_inferred_from_inertia": False,
            "CPT_or_stability_claimed": False,
        },
        "claim_flags": {
            "endpoint_grams_imported": True,
            "global_connection_imported": False,
            "whole_interval_channel_classified": False,
            "additional_global_channel_classified": False,
            "current_conservation_on_populated_quotient": False,
            "wavepacket_channel_extension_certified": False,
            "one_sided_J_isometry_certified": False,
            "full_scattering_matrix_constructed": False,
            "CPT_stability_positivity_or_unitarity_established": False,
        },
        "does_not_establish": [
            "a horizon-to-infinity connection matrix",
            "a populated finite-flux Einstein or additional channel",
            "a scattering matrix or J-isometry",
            "pole exclusion, stability, CPT, positivity, particles or unitarity",
        ],
        "verification": {
            "producer": (
                "python3 -m black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification.produce --check"
            ),
            "verifier": (
                "python3 -m black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification.verify"
            ),
            "mutations": (
                "python3 -m black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification.mutations"
            ),
            "tests": (
                "python3 -m unittest "
                "black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification.tests."
                "test_classifier -v"
            ),
        },
    }


def atlas_fragment(document: dict) -> dict:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "black_hole",
        "generated_by": (
            "black_hole_programme/phase3/"
            "axial_global_finite_flux_channel_classification/produce.py"
        ),
        "generated_by_sha256": sha256(HERE / "produce.py"),
        "status_vocabulary": [
            "CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE",
            "NO_CERTIFIED_MAP",
        ],
        "description_axes": [
            "causal", "symplectic", "nonlinear", "observational", "quantum",
        ],
        "entries": [{
            "id": (
                "black_hole.schwarzschild.phase3."
                "axial_global_finite_flux_channel_classification"
            ),
            "claim_boundary": (
                "The exact endpoint flux spaces are available, but the "
                "validated horizon-to-infinity connection handoff is absent. "
                "The global finite-flux channel classifier is therefore "
                "fail-closed and not activated."
            ),
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "OPEN",
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "scope": {
                "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
                "background": "Schwarzschild exterior, M=1",
                "carrier": "repaired six-state axial Bach reconstruction",
                "parity": "axial",
                "ell": 2,
                "m": "real-field involution",
                "k": "not applicable",
                "omega": "L2([1/2,3/4];C^3)",
                "degree": 1,
                "charge_sector": "small-gauge endpoint quotient",
                "boundaries": "Hplus, Iminus and Iplus; Hminus block absent",
            },
            "mode_data": {
                "dispersion": {
                    "status": "OPEN",
                    "statement": "The globally populated channel relation is not constructed.",
                },
                "lee_wald": {
                    "status": "OPEN",
                    "statement": (
                        "Endpoint Grams are certified separately; their "
                        "pullback through a global connection is not."
                    ),
                },
                "resonance": {
                    "status": "OPEN",
                    "statement": "Exceptional global frequency cells are not classified.",
                },
                "taub_maps": {
                    "status": "NOT_APPLICABLE",
                    "statement": "No compact Taub map enters this linear exterior problem.",
                },
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "smooth_secular": {
                        "status": "NOT_APPLICABLE",
                        "statement": "No nonlinear correction is evaluated.",
                    },
                    "bounded_or_finite_quasiperiodic": {
                        "status": "NOT_APPLICABLE",
                        "statement": "No nonlinear correction is evaluated.",
                    },
                    "causal_retarded": {
                        "status": "NO_CERTIFIED_MAP",
                        "statement": "The full two-boundary scattering map is absent.",
                    },
                },
            },
            "evidence": [{
                "path": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "result_id": document["result_id"],
            }],
        }],
        "verification_commands": [
            document["verification"]["producer"],
            document["verification"]["verifier"],
            (
                "python3 residual_atlas/validate_fragment.py "
                "residual_atlas/phase3-black-hole-axial-global-finite-flux-"
                "channel-classification-fragment-v1.json"
            ),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build_document()
    if args.check:
        if document != json.loads(OUTPUT.read_text()):
            raise SystemExit("classifier certificate drift")
        expected_atlas = atlas_fragment(document)
        if expected_atlas != json.loads(ATLAS.read_text()):
            raise SystemExit("classifier atlas drift")
    else:
        OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        ATLAS.write_text(
            json.dumps(atlas_fragment(document), indent=2, sort_keys=True) + "\n"
        )


if __name__ == "__main__":
    main()
