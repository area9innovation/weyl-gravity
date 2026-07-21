#!/usr/bin/env python3
"""Generate the fail-closed legacy Berger receiver-admissibility replay."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
PKG = ROOT / "closed_universe_observers"
CERT = PKG / "certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json"
SCHEMA = PKG / "schema/berger-legacy-receiver-admissibility-replay-v1.schema.json"
REPORT = PKG / "reports/berger-legacy-receiver-admissibility-replay-v1.md"

HISTORICAL_SOURCE_COMMIT = "aa5ca7814798dfbcc92ee52e462d25af74806515"
HISTORICAL_REPOSITORY_PATH = (
    "physics/symplectic-reconstruction/closed_universe_observers/certificates/"
    "CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
)
HISTORICAL_CONTRACT_SHA256 = "e2c9aad23b667ec16bbb124b72066d803f3607fc4bd89acd459b53f672a43918"
HISTORICAL_CROSSWALK = {
    "path": "closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json",
    "source_commit": HISTORICAL_SOURCE_COMMIT,
    "repository_path": HISTORICAL_REPOSITORY_PATH,
    "sha256": HISTORICAL_CONTRACT_SHA256,
    "resolution": "IMMUTABLE_GIT_BLOB",
}
HISTORICAL_FIVE_DISPOSITIONS = {
    "observer.general.charged_physical_time_relational_event_map": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_finite_resolution_sampling": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_emitter_receiver_composition": "CONDITIONAL_INTERFACE_ONLY",
    "observer.two_phase_counterflow.unrestricted_charged_time_event_map_contract": "NO_CERTIFIED_MAP",
    "observer.two_phase_counterflow.fixed_charge_relational_observable_obstruction": "CLOCK_REMOVED_OBSTRUCTED",
}
INTERFACE = {
    "path": "closed_universe_observers/generated/CHARGED_TIME_PHYSICAL_RECEIVER_CROSSWALK_INTERFACE_V1.json",
    "sha256": "a687208198e0b272b1cdb821e9dba5faf5f089fc87f8fcd03db67132e8767b1b",
}

LEGACY = {
    "dynamical_emitter": (
        "closed_universe_observers/certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
        "ad84b7ba1de4d35affc4624415fe66ba4bb09927b71a77acc59257da924c9d78",
    ),
    "localized_transfer": (
        "closed_universe_observers/certificates/BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER.json",
        "2dc293d4edad9d7e687b5080b05ec9a40b16a83a55ecc2dd655e935295cb6148",
    ),
    "detector_covectors": (
        "closed_universe_observers/certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
        "d91786a68bc15691eaea64bc48c93d3d4523f7fe3e13f1cda7b065d2ba08c947",
    ),
    "smeared_transfer": (
        "closed_universe_observers/certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
        "09f723df60cd4e1bee3efa86f0c9319baee5f539ae2008d9d03230eb42398f23",
    ),
    "detector_records": (
        "closed_universe_observers/certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
        "a77eb1cd8abeee608ee02ce52a0a35f0fdb84531946ef78cc5e36145afc14b6d",
    ),
    "selected_preparations": (
        "closed_universe_observers/certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json",
        "83663f884e69735f5233a0231d3d974d7c4886f42664cf7f1f375a841ac96019",
    ),
    "quartic_redshift": (
        "closed_universe_observers/certificates/BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION.json",
        "5aeb9d795916e05c5dba6fbc5650682e5c741fd83162181bdbcb413a55a54d13",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_contract(ref: dict | None = None) -> tuple[dict, dict]:
    source = dict(HISTORICAL_CROSSWALK if ref is None else ref)
    assert source == HISTORICAL_CROSSWALK, "historical source declaration drift"
    commit = source["source_commit"]
    repository_path = source["repository_path"]
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert resolved == commit, "historical source commit did not resolve exactly"
    object_spec = f"{commit}:{repository_path}"
    object_type = subprocess.run(
        ["git", "cat-file", "-t", object_spec],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert object_type == "blob", "historical receiver contract is not a regular Git blob"
    payload = subprocess.run(
        ["git", "show", object_spec],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(payload).hexdigest() == source["sha256"], "historical blob hash drift"
    document = json.loads(payload)
    rows = {row["atlas_id"]: row["admissibility_status"] for row in document["observer_carrier_census"]}
    assert rows == HISTORICAL_FIVE_DISPOSITIONS, "historical five-row scientific dispositions drift"
    completeness = document["census_completeness"]
    assert completeness["complete"] and completeness["discovered_count"] == 5
    return document, {
        "path": source["path"],
        "repository_path": repository_path,
        "source_commit": commit,
        "object_type": object_type,
        "resolution": source["resolution"],
        "result_id": document["result_id"],
        "sha256": source["sha256"],
    }


def rejects_historical_mutation(**changes) -> bool:
    mutated = dict(HISTORICAL_CROSSWALK)
    mutated.update(changes)
    try:
        historical_contract(mutated)
    except (AssertionError, subprocess.CalledProcessError, json.JSONDecodeError):
        return True
    return False


def field(status: str, witness: str) -> dict:
    return {"status": status, "witness": witness}


def classify_receiver(*, receiver_class=True, nonradical=True, denominator=True,
                      retarded=True, background_map=True) -> str:
    if not receiver_class or not background_map:
        return "NO_CERTIFIED_MAP"
    if not nonradical:
        return "RADICAL_UNDEFINED_RESPONSE"
    if not denominator:
        return "UNDEFINED_ZERO_DENOMINATOR"
    if not retarded:
        return "CAUSAL_INTERPRETATION_LOST"
    return "CERTIFIED_ADMISSIBLE"


def required_fields(kind: str) -> dict:
    absent = {
        "mode_scope": field("NO_CERTIFIED_MAP", "No single receiver scope fixes theory, background, boundaries, charge fibre, carrier and harmonic labels."),
        "local_BV_class": field("NO_CERTIFIED_MAP", "No action-derived local detector BV class is exported."),
        "cocycle_witness": field("NO_CERTIFIED_MAP", "No detector cocycle equation is exported."),
        "representative_quotient": field("NO_CERTIFIED_MAP", "No receiver representative quotient is exported."),
        "descended_pairing": field("NO_CERTIFIED_MAP", "No pairing descended to a receiver residual quotient is exported."),
        "nonradical_witness": field("NO_CERTIFIED_MAP", "No nonradical receiver class witness is exported."),
        "nonzero_period": field("NO_CERTIFIED_MAP", "A nonzero pre-quotient response is not a descended receiver period."),
        "retarded_support_map": field("NO_CERTIFIED_MAP", "No support-preserving retarded map on receiver classes is exported."),
        "monotone_clock_interval": field("CERTIFIED", "The positive Berger phase clock has rate dTheta/dt=3/4 on the declared detector windows."),
        "sampled_denominator_margin": field("NO_CERTIFIED_MAP", "No charged-time sampled denominator or positive margin is exported."),
        "D_action": field("NO_CERTIFIED_MAP", "No action of raw D on the receiver quotient is exported."),
        "R_action": field("NO_CERTIFIED_MAP", "No independent phase-rotation action on the receiver quotient is exported."),
        "K_action": field("NO_CERTIFIED_MAP", "No K=D-vR action separately intertwined on the receiver quotient is exported."),
    }
    if kind in {"dynamical_emitter", "localized_transfer", "smeared_transfer"}:
        absent["retarded_support_map"] = field(
            "CERTIFIED",
            "Retarded source-to-probe support is certified only before receiver cohomology and quotient descent.",
        )
    if kind == "detector_covectors":
        absent["retarded_support_map"] = field(
            "OBSTRUCTED",
            "The exported detector-to-emitter map is advanced and adjoint; it is not a retarded physical signal.",
        )
    if kind == "detector_records":
        absent["retarded_support_map"] = field(
            "OPEN", "The detector preflight explicitly leaves the smeared retarded transfer open."
        )
    if kind == "selected_preparations":
        absent["retarded_support_map"] = field(
            "NOT_APPLICABLE", "The advanced shadow selects emitter Cauchy data and is not a receiver signal map."
        )
    if kind == "quartic_redshift":
        absent = {name: field("OBSTRUCTED", "The common-action completion domain is empty before receiver population.")
                  for name in absent}
    return absent


def inventory(kind: str, doc: dict) -> dict:
    common = {
        "clock_and_rod_dependence": "Positive Berger phase clock and local rod-labelled D0/D1 profiles; apparatus inclusion in the action is not certified.",
        "relational_redshift": "NO_CERTIFIED_MAP",
        "recoil_backreaction_order": "not included in the certified response carrier",
        "survives_gauge_reduction": False,
        "boundary_dependence": "compact S3 spatial slices; compact detector/source time supports where declared; no boundary flux receiver theorem",
    }
    if kind == "dynamical_emitter":
        return common | {
            "detector_response": "leading triangular source-to-probe matrix with nonzero diagonal",
            "response_rank": "2",
            "emitter_preparation": "two localized co-closed free massive-two-form Cauchy preparations",
            "profile_dependency": "detector-selected local massive polarization and ordered switches",
            "green_dependency": "retarded Maxwell Green map plus an advanced adjoint only for preparation selection",
        }
    if kind == "localized_transfer":
        return common | {
            "detector_response": "localized-current triangular source-to-probe matrix",
            "response_rank": "2",
            "emitter_preparation": "two predeclared localized conserved Maxwell currents, not dynamical action variables",
            "profile_dependency": "normalized nonnegative C-G4 localization bumps and D0/D1 windows",
            "green_dependency": "certified unary retarded Maxwell contraction",
        }
    if kind == "detector_covectors":
        return common | {
            "detector_response": "not evaluated",
            "response_rank": "NOT_APPLICABLE",
            "emitter_preparation": "advanced detector covector operator only",
            "profile_dependency": "exact normalized clock bumps and local radial profile families",
            "green_dependency": "advanced Maxwell and massive-emitter Green images are unevaluated",
        }
    if kind == "smeared_transfer":
        return common | {
            "detector_response": "diagonal homogeneous-Maxwell source-to-probe matrix with positive entries",
            "response_rank": "2",
            "emitter_preparation": "two predeclared compact-time currents occupying all of S3",
            "profile_dependency": "nonnegative normalized rod smearings in disjoint clock windows",
            "green_dependency": "exact retarded Maxwell solution in the homogeneous e1/e2 sector",
        }
    if kind == "detector_records":
        return common | {
            "detector_response": "not computed; only independent normalized test-probe functionals",
            "response_rank": "OPEN",
            "emitter_preparation": "none",
            "profile_dependency": "local rod charts, D0/D1 clock windows and persistent probe memories",
            "green_dependency": "retarded signal imported but detector evaluation left open",
        }
    if kind == "selected_preparations":
        return common | {
            "detector_response": "positive diagonal leading coefficient conditional on nonzero advanced covector data",
            "response_rank": "not independently a two-source/two-receiver matrix",
            "emitter_preparation": "positive-energy dual massive-two-form Cauchy profiles",
            "profile_dependency": "detector-selected compact Cauchy profiles one switch gap before D0/D1",
            "green_dependency": "advanced Green images unevaluated; support used only for source selection",
        }
    return common | {
        "detector_response": "NOT_APPLICABLE_EMPTY_DOMAIN",
        "response_rank": "NOT_APPLICABLE_EMPTY_DOMAIN",
        "emitter_preparation": "NO_CERTIFIED_MAP",
        "profile_dependency": "no same-action clock/rod/detector tensor exists on the empty completion locus",
        "green_dependency": "NO_CERTIFIED_MAP",
    }


def carrier_gate(kind: str, doc: dict) -> dict:
    setting = doc["setting_id"]
    source_roles = {
        "dynamical_emitter": "SOURCE_PREPARATION_AND_LEADING_RESPONSE",
        "localized_transfer": "EXTERNAL_SOURCE_TO_PROBE_TRANSFER",
        "detector_covectors": "PROBE_PROFILE_AND_ADVANCED_ADJOINT",
        "smeared_transfer": "HOMOGENEOUS_SOURCE_TO_PROBE_TRANSFER",
        "detector_records": "PROBE_DETECTOR_PREFLIGHT",
        "selected_preparations": "SOURCE_PREPARATION",
        "quartic_redshift": "EMPTY_NONLINEAR_DISPOSITION",
    }
    first = {
        "dynamical_emitter": "ACTION_DERIVED_RECEIVER_UNARY_THEORY",
        "localized_transfer": "ACTION_DERIVED_EMITTER_AND_RECEIVER_UNARY_THEORY",
        "detector_covectors": "ACTION_DERIVED_RECEIVER_UNARY_THEORY",
        "smeared_transfer": "ACTION_DERIVED_RECEIVER_UNARY_THEORY",
        "detector_records": "ACTION_DERIVED_RECEIVER_UNARY_THEORY",
        "selected_preparations": "RECEIVER_CLASS_MAP_FROM_SOURCE_PREPARATION",
        "quartic_redshift": "NONEMPTY_COMMON_ACTION_UNARY_THEORY",
    }[kind]
    theory = (
        "OBSTRUCTED_EMPTY_DOMAIN" if kind == "quartic_redshift"
        else "NO_CERTIFIED_MAP_TO_ACTION_DERIVED_RECEIVER"
    )
    return {
        "declared_setting_id": setting,
        "candidate_role": source_roles[kind],
        "same_action_derived_unary_theory": theory,
        "same_background": "CERTIFIED_ONLY_WITHIN_EACH_HASHED_LEGACY_FIXTURE; NO_GLOBAL_NAME_MATCH",
        "same_charge_fibre": "NO_CERTIFIED_MAP",
        "same_residual_quotient": "NO_CERTIFIED_MAP",
        "first_missing_condition": first,
        "first_missing_witness": (
            "The terminal common-action locus is empty."
            if kind == "quartic_redshift"
            else "The rods, detector smearings and memories are probe data outside an exported action-derived receiver unary complex."
        ),
    }


def build() -> dict:
    receiver_contract, receiver_contract_ref = historical_contract()
    refs = {"receiver_contract": receiver_contract_ref}
    docs = {"receiver_contract": receiver_contract}
    for name, ref in (("receiver_interface", (INTERFACE["path"], INTERFACE["sha256"])),
                      *LEGACY.items()):
        source, expected = ref
        path = ROOT / source
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(f"dependency drift: {name}: {actual}")
        doc = json.loads(path.read_text())
        docs[name] = doc
        refs[name] = {
            "path": source,
            "result_id": doc.get("result_id", doc.get("interface_id")),
            "sha256": actual,
        }

    required = docs["receiver_interface"]["receiver_required_fields"]
    rows = []
    for kind in LEGACY:
        doc = docs[kind]
        fields = required_fields(kind)
        if sorted(fields) != sorted(required):
            raise AssertionError(f"receiver interface drift for {kind}")
        rows.append({
            "legacy_key": kind,
            "result_id": doc["result_id"],
            "claim_status_imported": doc["claim_status"],
            "source_ref": refs[kind],
            "carrier_gate": carrier_gate(kind, doc),
            "receiver_fields": fields,
            "operational_inventory": inventory(kind, doc),
            "admissibility_status": "NO_CERTIFIED_MAP",
            "physical_receiver_promoted": False,
        })

    replay = {
        "rank_two_response_certificates": [
            "BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO",
            "BERGER_LOCALIZED_EMITTER_RANK_TWO_TRANSFER",
            "BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER",
        ],
        "rank_two_probe_basis_not_response": "BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS",
        "pairing_radical_result": "NO_LEGACY_CERTIFICATE_EXPORTS_A_DESCENDED_RECEIVER_PAIRING_OR_NONRADICAL_WITNESS",
        "support_result": "THREE_RETARDED_SOURCE_TO_PROBE_MAPS_SURVIVE_PREQUOTIENT; ADVANCED_ADJOINT_IS_PREPARATION_ONLY",
        "denominator_result": "NO_LEGACY_CERTIFICATE_EXPORTS_A_SAMPLED_RECEIVER_DENOMINATOR_MARGIN",
    }
    mutations = [
        {
            "name": "cloned_or_radical_receiver",
            "detected": classify_receiver(nonradical=False) == "RADICAL_UNDEFINED_RESPONSE",
            "classification": classify_receiver(nonradical=False),
        },
        {
            "name": "advanced_only_detector_map",
            "detected": classify_receiver(retarded=False) == "CAUSAL_INTERPRETATION_LOST",
            "classification": classify_receiver(retarded=False),
        },
        {
            "name": "cross_background_name_match",
            "detected": classify_receiver(background_map=False) == "NO_CERTIFIED_MAP",
            "classification": classify_receiver(background_map=False),
        },
        {
            "name": "rank_two_without_receiver_class",
            "detected": classify_receiver(receiver_class=False) == "NO_CERTIFIED_MAP",
            "classification": classify_receiver(receiver_class=False),
        },
        {
            "name": "wrong_historical_commit",
            "detected": rejects_historical_mutation(source_commit="0" * 40),
            "classification": "IMMUTABLE_HISTORICAL_BLOB_REJECTED",
        },
        {
            "name": "wrong_historical_path",
            "detected": rejects_historical_mutation(repository_path=HISTORICAL_REPOSITORY_PATH + ".missing"),
            "classification": "IMMUTABLE_HISTORICAL_BLOB_REJECTED",
        },
        {
            "name": "wrong_historical_blob_hash",
            "detected": rejects_historical_mutation(sha256="0" * 64),
            "classification": "IMMUTABLE_HISTORICAL_BLOB_REJECTED",
        },
        {
            "name": "mutable_current_path_substitution",
            "detected": rejects_historical_mutation(
                source_commit="HEAD",
                sha256=sha256(ROOT / HISTORICAL_CROSSWALK["path"]),
            ),
            "classification": "MUTABLE_CURRENT_PATH_FORBIDDEN",
        },
    ]
    value = {
        "schema": "closed-universe-berger-legacy-receiver-admissibility-replay-v1",
        "result_id": "BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1",
        "claim_status": "CERTIFIED_COMPLETE_FAIL_CLOSED_LEGACY_BERGER_RECEIVER_CENSUS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "receiver_interface_required_fields": required,
        "carrier_compatibility_theorem": {
            "ordering": ["action_derived_unary_theory", "background", "charge_fibre", "residual_quotient"],
            "result": "NO_SINGLE_LEGACY_ROW_POPULATES_ALL_FOUR_CARRIER_IDENTITIES",
            "name_matching_forbidden": True,
            "advanced_signal_forbidden": True,
        },
        "legacy_receiver_census": rows,
        "independent_replay_targets": replay,
        "mutation_results": mutations,
        "census_completeness": {
            "expected_count": len(LEGACY),
            "discovered_count": len(rows),
            "classified_count": len(rows),
            "unclassified_result_ids": [],
            "complete": True,
        },
        "flags": {
            "LEGACY_CENSUS_COMPLETE": True,
            "THREE_PREQUOTIENT_RANK_TWO_RESPONSES_REPLAYED": True,
            "ACTION_DERIVED_PHYSICAL_RECEIVER_CERTIFIED": False,
            "DESCENDED_RECEIVER_PAIRING_CERTIFIED": False,
            "POSITIVE_DENOMINATOR_MARGIN_CERTIFIED": False,
            "ADVANCED_MAP_PROMOTED_AS_SIGNAL": False,
            "PHYSICAL_REDSHIFT_CERTIFIED": False,
            "NONLINEAR_CLAIM": False,
            "PARTICLE_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_ACTION_DERIVED_BERGER_RECEIVER_BV_CLASS_QUOTIENT_PAIRING_AND_SEPARATE_D_R_K_ACTIONS",
        "claim_boundary": (
            "This exact audit preserves three legacy rank-two retarded source-to-probe response results in their original "
            "pre-quotient carriers and certifies a complete seven-row missing-condition ledger. No legacy row supplies an "
            "action-derived receiver BV class, receiver residual quotient, descended nonradical period, sampled denominator "
            "margin and separately typed D/R/K actions on one carrier; therefore no physical receiver or relational redshift "
            "is promoted. The advanced adjoint remains a preparation map. This does not establish nonexistence and makes no "
            "nonlinear, particle, phenomenology or quantum claim."
        ),
        "provenance": {
            "producer_method": "typed audit over one immutable historical Git blob, the current receiver interface and seven legacy certificates",
            "independent_method": "symbolic matrix-rank reconstruction plus structural pairing, support and denominator replay",
            "higher_tiers_not_run": {
                "tier_2": "the historical five-row contract is resolved by exact commit, repository path, blob type and SHA-256; all other inputs are current-path exact hashes",
                "tier_3": "owned by the dedicated post-repair fixed-point successor",
            },
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    return value


def render(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def report() -> str:
    return """# Legacy Berger receiver-admissibility replay

The seven legacy Berger emitter, detector, transfer and redshift certificates
have been replayed against the charged-time physical-receiver interface.  Three
source-to-probe transfer matrices retain exact rank two in their original
pre-quotient carriers.  That does not make their probe smearings descended
physical receivers.

No row exports all of an action-derived detector BV class and cocycle, a
receiver quotient, a descended nonradical period, a sampled denominator margin,
and separately typed D, R and K actions.  The detector-to-emitter advanced map
remains an adjoint preparation device, and the quartic redshift carrier remains
empty.  The complete census therefore promotes no physical receiver and no
relational redshift.

EVIDENCE: closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json
CLOSE-OUT: DONE — seven legacy rows classified with exact first-missing-condition witnesses
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.emit:
        CERT.write_text(render(result))
        REPORT.write_text(report())
    if args.check and (CERT.read_text() != render(result) or REPORT.read_text() != report()):
        raise SystemExit("stale legacy receiver replay")
    print("BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1 generation: PASS")
