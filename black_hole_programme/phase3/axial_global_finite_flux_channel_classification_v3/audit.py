from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


RESULT_ID = "PURE_WEYL_PHASE3_AXIAL_GLOBAL_FINITE_FLUX_CHANNEL_CLASSIFICATION_V3"
PACKAGE = Path("black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3")

IMPORTS = {
    "boundary_contract": (
        Path("black_hole_programme/phase3/boundary_flux_contract/certificate.json"),
        "3ee56677677f66df7ccba021a1e40cfd3af7e548aa24f991b8bae8f4689550ef",
    ),
    "radial_cover": (
        Path(
            "black_hole_programme/phase3/axial_global_connection_matrix_v5/chunks/"
            "artifacts/global_map_cover_manifest.json"
        ),
        "d5b2e4ddef623136155b315be5ff847f14597440b21e5bd1c4beb800d2ba16d8",
    ),
    "incoming": (
        Path("black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json"),
        "f223358ca9de0f6d819684ce61d62677d6e5f8c5d4edaa600e2bae02719af0ef",
    ),
    "null_grams": (
        Path("black_hole_programme/phase3/axial_null_flux_gram/certificate.json"),
        "59fb9b443ce0b92ce016f53c376cb367bcf004e00d1b241ad22ec925e99deed2",
    ),
    "horizon_gram": (
        Path(
            "black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/"
            "future_horizon_outward_gram.json"
        ),
        "3051f43f73e4649dede60176e12f13afc59bdd5b3e8e09970db842a1ede00fdb",
    ),
    "transport_free_stokes": (
        Path(
            "black_hole_programme/phase3/"
            "axial_transport_free_outgoing_defect_preflight_v1/certificate.json"
        ),
        "833e0bdb3e1e443a5a351050b9b47fb4555a9b069db73b46e228f96245fa0aa9",
    ),
    "outgoing_population": (
        Path(
            "black_hole_programme/phase3/"
            "axial_outgoing_population_cell_half_v1/certificate.json"
        ),
        "de7e3a944e945b00fea9e2b5f7abffc8789c7449cae9eae222c047912a4f3d0f",
    ),
}


class AuditError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _verify_radial_cover(root: Path, manifest: dict[str, Any]) -> None:
    _require(manifest["schema"] == "phase3-axial-global-map-cover-v1", "wrong radial schema")
    _require(manifest["status"] == "CERTIFIED", "radial cover is not certified")
    cover = manifest["cover"]
    _require(cover["lower"] == "1/2" and cover["upper"] == "129/256", "wrong radial cover")
    _require(cover["child_count"] == 16, "wrong radial child count")
    _require(
        cover["no_duplicates"] and cover["no_extras"] and cover["no_gaps_or_overlaps"],
        "radial cover flags fail",
    )
    entries = manifest["entries"]
    _require(len(entries) == 16, "radial entry count fails")
    cursor = Fraction(1, 2)
    for index, entry in enumerate(entries):
        _require(entry["child_id"] == f"q{index:02d}", "radial child order fails")
        _require(entry["child_index"] == index, "radial child index fails")
        lower = parse_fraction(entry["lower"])
        upper = parse_fraction(entry["upper"])
        _require(lower == cursor and upper - lower == Fraction(1, 4096), "radial gap/width")
        cursor = upper
        for field in ("global_map", "tail_join"):
            artifact = root / entry[field]["path"]
            _require(artifact.is_file(), f"missing radial artifact {artifact}")
            _require(sha256(artifact) == entry[field]["sha256"], f"hash mismatch {artifact}")
        global_map = load_json(root / entry["global_map"]["path"])
        _require(
            global_map["schema"] == "phase3-axial-final-frequency-child-global-map-v1"
            and global_map["status"] == "CERTIFIED",
            "global radial-map status/schema fails",
        )
        proof = global_map["proof"]
        _require(
            proof["ok"]
            and proof["factor_rank_certified"]
            and proof["factor_rank"] == 12
            and proof["crosswalk_rank_certified"]
            and proof["crosswalk_rank"] == 12,
            "global radial-map rank proof fails",
        )
    _require(cursor == Fraction(129, 256), "radial terminal boundary fails")


def _verify_sources(root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    sources: dict[str, dict[str, Any]] = {}
    imports: list[dict[str, str]] = []
    for name, (relative, expected_hash) in IMPORTS.items():
        path = root / relative
        _require(path.is_file(), f"missing import {relative}")
        actual = sha256(path)
        _require(actual == expected_hash, f"import drift {relative}: {actual}")
        sources[name] = load_json(path)
        imports.append({"name": name, "path": str(relative), "sha256": actual})

    boundary = sources["boundary_contract"]
    _require(boundary["result_id"] == "PURE_WEYL_PHASE3_BOUNDARY_FLUX_CONTRACT_V1", "boundary id")
    _require(boundary["claim_flags"]["boundary_flux_contract_defined"], "boundary contract absent")
    _require(
        boundary["declaration"]["pilot_domain"]["hat_omega_interval"] == ["1/2", "3/4"],
        "boundary pilot drift",
    )

    radial = sources["radial_cover"]
    _verify_radial_cover(root, radial)

    incoming = sources["incoming"]
    _require(
        incoming["claim_flags"]["Tminus_invertible_all_real_positive_omega_certified"],
        "Tminus theorem absent",
    )
    _require(
        incoming["factor_adapted_Iminus_gram"]["full_inertia_for_alpha_W_positive"] == [1, 2, 0],
        "incoming inertia drift",
    )
    factor = incoming["factor_adapted_Iminus_gram"]
    _require(factor["carrier_factor_plane"]["inertia"] == [1, 1, 0], "spin-two factor drift")
    _require(factor["spin_one_quotient_line"]["inertia"] == [0, 1, 0], "spin-one factor drift")
    _require(
        factor["spin_one_quotient_line"]["unit_quotient_norm"] == "-32/(15*omega)",
        "spin-one quotient normalization drift",
    )

    null = sources["null_grams"]
    _require(null["common_verdict"]["rank"] == 3, "null rank drift")
    _require(
        null["common_verdict"]["inertia_for_alpha_W_positive"] == [1, 2, 0],
        "null inertia drift",
    )
    for endpoint in ("Iminus", "Iplus"):
        classification = null["endpoint_grams"][endpoint]["classification"]
        _require(classification["rank"] == 3 and classification["radical_dimension"] == 0, endpoint)
        _require(
            classification["inertia_for_alpha_W_positive"]
            == {"negative": 2, "positive": 1, "zero": 0},
            f"{endpoint} inertia",
        )

    horizon = sources["horizon_gram"]
    _require(horizon["status"] == "PASS", "horizon Gram does not pass")
    _require(horizon["rank"] == 3, "horizon rank drift")
    _require(horizon["inertia_for_alpha_W_positive"] == [1, 2, 0], "horizon inertia drift")
    _require(
        horizon["ldl_pivot_signs_on_closed_interval"] == ["positive", "negative", "negative"],
        "horizon LDL signs drift",
    )

    stokes = sources["transport_free_stokes"]
    tier_b = stokes["tier_B_abstract_pseudo_isometry"]
    _require(tier_b["raw_embedding"]["certified"], "raw pseudo-isometry absent")
    _require(tier_b["abstract_stokes_identity"]["certified"], "Stokes identity absent")
    _require(tier_b["raw_embedding"]["injective"], "embedding injectivity absent")

    outgoing = sources["outgoing_population"]
    flags = outgoing["claim_flags"]
    _require(flags["Tplus_invertible_on_declared_cell"], "Tplus cell theorem absent")
    _require(flags["full_outgoing_trace_space_populated_on_declared_cell"], "outgoing population")
    _require(flags["cell_L2_multiplier_bounded_isomorphism"], "outgoing L2 theorem absent")
    _require(flags["O_inertia_1_2_0_on_declared_cell"], "outgoing defect inertia absent")
    _require(
        outgoing["scope"]["frequency_interval"] == ["0.49995", "0.50005"],
        "outgoing cell drift",
    )
    return sources, imports


def _intersection(sources: dict[str, dict[str, Any]]) -> tuple[Fraction, Fraction]:
    radial = sources["radial_cover"]["cover"]
    outgoing = sources["outgoing_population"]["scope"]["frequency_interval"]
    null = sources["null_grams"]["declaration"]["frequency_interval"]
    horizon = sources["horizon_gram"]["frequency_interval"]
    lower = max(
        parse_fraction(radial["lower"]),
        parse_fraction(outgoing[0]),
        parse_fraction(null[0]),
        parse_fraction(horizon[0]),
    )
    upper = min(
        parse_fraction(radial["upper"]),
        parse_fraction(outgoing[1]),
        parse_fraction(null[1]),
        parse_fraction(horizon[1]),
    )
    _require(lower == Fraction(1, 2), "joint lower endpoint drift")
    _require(upper == Fraction(10001, 20000), "joint upper endpoint drift")
    _require(lower < upper, "empty joint pilot")
    return lower, upper


def build_certificate(root: Path) -> dict[str, Any]:
    sources, imports = _verify_sources(root)
    lower, upper = _intersection(sources)
    return {
        "schema": "phase3-axial-global-finite-flux-channel-classification-v3",
        "result_id": RESULT_ID,
        "status": "PASS",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "coupling_sign": "alpha_W>0",
            "joint_pilot_interval": [str(lower), str(upper)],
            "joint_pilot_interval_decimal": ["0.5", "0.50005"],
            "zero_frequency": "excluded",
        },
        "imports": imports,
        "radial_connection_pilot": {
            "certified": True,
            "frequency_cover": ["1/2", "129/256"],
            "radial_map": "r=32 to r=4",
            "frequency_children": 16,
            "rank_each_global_map": 12,
            "interpretation": (
                "content-addressed interior transport pilot only; physical endpoint population "
                "is established independently by boundary devissage and Stokes"
            ),
        },
        "finite_flux_spaces": {
            "incoming_Iminus": {
                "dimension": 3,
                "rank": 3,
                "radical_dimension": 0,
                "inertia": [1, 2, 0],
                "population": "Tminus is invertible for every real omega>0",
            },
            "outgoing_Iplus": {
                "dimension": 3,
                "rank": 3,
                "radical_dimension": 0,
                "inertia": [1, 2, 0],
                "population": "Tplus is invertible throughout the joint pilot interval",
            },
            "future_horizon": {
                "dimension": 3,
                "rank": 3,
                "radical_dimension": 0,
                "inertia": [1, 2, 0],
                "orientation": "future inner-boundary outward",
            },
            "common_signature_basis": "each form is congruent to J=diag(1,-1,-1)",
        },
        "factor_resolved_incoming_channels": {
            "spin_two_extension_plane": {
                "basis": ["EI", "RI0"],
                "inertia": [1, 1, 0],
                "canonical_gram_over_pi_alpha_W": [
                    ["0", "576*omega/5"],
                    ["576*omega/5", "0"],
                ],
                "classification": "one positive and one negative null-paired spin-two channel",
            },
            "spin_one_quotient": {
                "basis": ["SI_unit"],
                "inertia": [0, 1, 0],
                "unit_quotient_norm_over_pi_alpha_W": "-32/(15*omega)",
                "classification": "one strictly negative spin-one quotient channel",
            },
            "attribution_boundary": (
                "this exact factor attribution is certified in the incoming factor frame; "
                "the outgoing and horizon theorem certifies matching inertia, not identical raw bases"
            ),
        },
        "population_and_scattering": {
            "unique_outgoing_preimage": (
                "for every omega in the joint pilot interval, each outgoing trace has one "
                "and only one future-horizon-regular coefficient vector"
            ),
            "band_limited_Tplus": (
                "multiplication by Tplus is a bounded isomorphism on "
                "L2([1/2,10001/20000];C^3)"
            ),
            "raw_maps": {
                "Rraw": "Tplus*Tminus^(-1)",
                "Araw": "Tminus^(-1)",
                "Sraw": "vertical_stack(Rraw,Araw)",
            },
            "oriented_stokes_identity": (
                "Gminus=Rraw^dagger*Gplus*Rraw+Araw^dagger*Hout*Araw"
            ),
            "pseudo_isometry": (
                "Sraw^dagger*(Gplus direct_sum Hout)*Sraw=Gminus pointwise and after "
                "integration over the joint pilot interval"
            ),
            "embedding": True,
            "negative_flux_population": (
                "because Tminus and Tplus are invertible, the negative classical Lee-Wald "
                "directions in both null trace spaces are populated on the joint pilot interval"
            ),
        },
        "generic_positive_real_corollary": {
            "outgoing_exceptional_set": "locally finite scalar reflection-zero set",
            "Tplus_invertible": "open dense full-measure subset of omega>0",
            "compact_band_multiplier": (
                "injective with dense range; a bounded isomorphism exactly when the band "
                "contains no exceptional frequency"
            ),
        },
        "claim_flags": {
            "boundary_flux_contract_established": True,
            "content_addressed_radial_pilot_established": True,
            "matching_three_channel_Krein_spaces_on_joint_pilot": True,
            "incoming_factor_resolved_signature_established": True,
            "full_outgoing_population_on_joint_pilot": True,
            "band_limited_pseudo_isometry_established": True,
            "generic_positive_real_outgoing_population_established": True,
            "explicit_Tplus_entries_established": False,
            "whole_original_pilot_outgoing_population_established": False,
            "full_positive_axis_inverse_bound_established": False,
            "time_domain_or_quantum_claim": False,
        },
        "does_not_establish": [
            "that the radial microfactor cover alone is a physical endpoint connection",
            "the explicit 3x3 Tplus entries or extension mixing amplitudes",
            "Tplus invertibility on the whole original [1/2,3/4] pilot interval",
            "absence or location of isolated positive-real reflection zeros outside the joint cell",
            "a uniform inverse bound on the full positive real axis",
            "limiting absorption, resolvent bounds, time-domain boundedness or decay",
            "a Green-resolvent pole theorem",
            "positive energy, particles, ghosts, CPT or quantum unitarity",
            "polar parity or ell other than two",
        ],
        "verification": {
            "producer": (
                "python3 -m black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification_v3.produce"
            ),
            "verifier": (
                "python3 -m black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification_v3.verify"
            ),
            "tests": (
                "python3 -m unittest -v black_hole_programme.phase3."
                "axial_global_finite_flux_channel_classification_v3.test_classification"
            ),
        },
    }
