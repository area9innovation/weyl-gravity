#!/usr/bin/env python3
"""Generate the legacy Berger operational frequency-ratio nonactivation theorem."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
PKG = ROOT / "closed_universe_observers"
CERT = PKG / "certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json"
SCHEMA = PKG / "schema/berger-legacy-receiver-operational-frequency-ratio-nonactivation-v1.schema.json"
REPORT = PKG / "reports/berger-legacy-receiver-operational-frequency-ratio-nonactivation-v1.md"
REQUEST = ROOT / "planning/forge-requests/positive-berger-action-derived-local-receiver-bv-cocycle.json"

AUDIT = {
    "path": "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json",
    "sha256": "3851a46dc9ab2b2f1ca092a67ffd17c7ecdb21b18b8a238f72c8de091835fde5",
}
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def historical_contract(ref: dict | None = None) -> tuple[dict, dict]:
    source = dict(HISTORICAL_CROSSWALK if ref is None else ref)
    assert source == HISTORICAL_CROSSWALK, "historical source declaration drift"
    commit = source["source_commit"]
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert resolved == commit, "historical source commit did not resolve exactly"
    object_spec = f"{commit}:{source['repository_path']}"
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
    dispositions = {
        row["atlas_id"]: row["admissibility_status"]
        for row in document["observer_carrier_census"]
    }
    assert dispositions == HISTORICAL_FIVE_DISPOSITIONS, "historical five-row scientific dispositions drift"
    completeness = document["census_completeness"]
    assert completeness["complete"] and completeness["discovered_count"] == 5
    return document, {
        "path": source["path"],
        "repository_path": source["repository_path"],
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


def request_value() -> dict:
    return {
        "id": "sf:forge-request/positive-berger-action-derived-local-receiver-bv-cocycle",
        "kind": "work",
        "schema": "work-v0",
        "body": {
            "owner": "classical-observer-berger-receiver-unary",
            "state": "REQUESTED",
            "objective": (
                "Supply the first common missing physical datum certified by "
                "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json: "
                "one same-background, action-derived local detector receiver BV cocycle embedded in an executable positive-Berger unary complex. "
                "The first consumer is sf:program/work/observer-berger-legacy-receiver-operational-frequency-ratio. "
                "The existing probe smearings, memories and advanced detector covectors are inputs to compare against, not action-derived receiver rows."
            ),
            "depends_on": ["sf:program/work/observer-berger-legacy-receiver-operational-frequency-ratio"],
            "stop_condition": (
                "Land one content-addressed positive-Berger receiver-unary payload derived from a declared master action and background solution. "
                "Pin the theory, background, boundaries and unrestricted charge fibre; enumerate the detector/rod/memory fields and BV duals with degrees and parities; "
                "export their exact q1 rows, signed pairing and inclusion into the ambient unary complex; prove q1^2=0 and pairing cyclicity; and export compact local forms A and B "
                "with the exact cocycle identity sA+dB=0, support data in one detector worldtube, and separate raw-D, phase-R and K=D-vR unary actions. "
                "Provide a method-distinct verifier and mutations deleting the action origin, cocycle identity, support declaration or one symmetry action. "
                "This producer stops at the executable unary cocycle carrier; the observer consumer will separately compute the residual quotient, nonradical pairing, period, "
                "denominator margin and any operational ratio."
            ),
            "forbid": (
                "No probe smearing or persistent register called an action-derived BV row; no advanced Green covector used as a signal; no matching by Berger, D0/D1 or polarization names; "
                "no external current promoted to a dynamical emitter; no fixed-charge clock resurrection; no coordinate-frequency ratio called redshift; no quotient, nonzero period, "
                "denominator, nonlinear memory, particle or quantum conclusion inferred by the producer."
            ),
            "notes": [
                "This is a physics-domain producer request routed through the programme coordinator; it does not ask Forge to invent a replacement action.",
                "It is deliberately the smallest common missing datum: the action-derived receiver unary cocycle carrier. Quotient, pairing and ratio gates remain separate observer work.",
                "The three maximal linear candidates retain exact pre-quotient rank-two response, but all fail before receiver quotient descent.",
            ],
        },
    }


def import_ref(path_text: str, expected: str) -> tuple[dict, dict]:
    path = ROOT / path_text
    actual = sha256(path)
    if actual != expected:
        raise AssertionError(f"dependency drift: {path_text}: {actual}")
    doc = json.loads(path.read_text())
    return doc, {"path": path_text, "result_id": doc["result_id"], "sha256": actual}


def build() -> tuple[dict, dict]:
    audit, audit_ref = import_ref(AUDIT["path"], AUDIT["sha256"])
    crosswalk, crosswalk_ref = historical_contract()
    rows = {row["legacy_key"]: row for row in audit["legacy_receiver_census"]}
    if set(rows) != {
        "dynamical_emitter", "localized_transfer", "detector_covectors", "smeared_transfer",
        "detector_records", "selected_preparations", "quartic_redshift",
    }:
        raise AssertionError("legacy census drift")
    if any(row["physical_receiver_promoted"] for row in rows.values()):
        raise AssertionError("positive branch activated")

    maximal = [
        {
            "candidate_id": "DYNAMICAL_MASSIVE_TWO_FORM_EMITTER_TO_PROBE_CHAIN",
            "component_keys": ["dynamical_emitter", "selected_preparations", "detector_covectors", "detector_records"],
            "response_rank": 2,
            "retarded_dependence": "CERTIFIED_PREQUOTIENT",
            "first_missing_condition": rows["dynamical_emitter"]["carrier_gate"]["first_missing_condition"],
            "independent_witness": "No action-derived receiver local_BV_class/cocycle or receiver q1 row occurs in the hashed component certificates.",
            "ratio_status": "UNDEFINED_NO_PHYSICAL_RECEIVER",
        },
        {
            "candidate_id": "LOCALIZED_EXTERNAL_MAXWELL_CURRENT_TO_PROBE_CHAIN",
            "component_keys": ["localized_transfer", "detector_records"],
            "response_rank": 2,
            "retarded_dependence": "CERTIFIED_PREQUOTIENT",
            "first_missing_condition": rows["localized_transfer"]["carrier_gate"]["first_missing_condition"],
            "independent_witness": "The emitter currents are predeclared external currents and the detector remains outside an action-derived receiver unary complex.",
            "ratio_status": "UNDEFINED_NO_PHYSICAL_RECEIVER",
        },
        {
            "candidate_id": "HOMOGENEOUS_MAXWELL_SOURCE_TO_PROBE_CHAIN",
            "component_keys": ["smeared_transfer", "detector_records"],
            "response_rank": 2,
            "retarded_dependence": "CERTIFIED_PREQUOTIENT",
            "first_missing_condition": rows["smeared_transfer"]["carrier_gate"]["first_missing_condition"],
            "independent_witness": "The Maxwell causal unary is certified, but CLASSICAL_OBSERVER_MAP and D descent with source/rod/memory are explicitly false.",
            "ratio_status": "UNDEFINED_NO_PHYSICAL_RECEIVER",
        },
    ]
    dominated = {
        "detector_covectors": "component of the dynamical chain; advanced adjoint only",
        "detector_records": "common probe preflight with no response matrix",
        "selected_preparations": "source-preparation extension of the dynamical chain",
        "quartic_redshift": "terminal empty nonlinear action domain, not a nonempty linear receiver candidate",
    }
    request = request_value()
    request_bytes = render(request).encode()
    mutations = [
        {"name": "promote_rank_two_before_receiver_descent", "detected": True, "classification": "NO_CERTIFIED_MAP"},
        {"name": "use_advanced_covector_as_signal", "detected": True, "classification": "CAUSAL_INTERPRETATION_LOST"},
        {"name": "identify_equal_coordinate_frequencies_as_redshift", "detected": True, "classification": "COORDINATE_CONTROL_ONLY"},
        {"name": "cross_unary_match_by_detector_name", "detected": True, "classification": "NO_CERTIFIED_MAP"},
        {"name": "divide_without_positive_receiver_margin", "detected": True, "classification": "UNDEFINED_ZERO_DENOMINATOR"},
        {"name": "resurrect_fixed_charge_relative_clock", "detected": True, "classification": "CLOCK_REMOVED_OBSTRUCTED"},
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
        "schema": "closed-universe-berger-legacy-receiver-operational-frequency-ratio-nonactivation-v1",
        "result_id": "BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1",
        "claim_status": "CERTIFIED_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_ON_LEGACY_CENSUS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {"legacy_receiver_audit": audit_ref, "receiver_crosswalk": crosswalk_ref},
        "legacy_source_refs": {key: audit["dependency_refs"][key] for key in (
            "dynamical_emitter", "localized_transfer", "detector_covectors", "smeared_transfer",
            "detector_records", "selected_preparations", "quartic_redshift",
        )},
        "maximal_candidate_definition": (
            "A maximal candidate is a nonempty legacy linear source-to-probe chain with a certified response matrix that is not a strict component of another chain on the same declared source carrier."
        ),
        "maximal_candidate_replay": maximal,
        "nonmaximal_disposition": dominated,
        "operational_ratio_theorem": {
            "definition": "C_emit,recv=(S_epsilon nu_emit)/(S_epsilon nu_recv) after receiver-class evaluation on one action/background/charge fibre",
            "domain_conditions": [
                "action-derived compact emitter and receiver records",
                "representative-independent descended receiver pairing and nonzero period",
                "support-preserving retarded path",
                "regular monotone clock band and strictly positive sampled receiver denominator margin",
                "separately intertwined D, R and K actions",
            ],
            "domain_on_legacy_census": "EMPTY",
            "result": "UNDEFINED_NO_PHYSICAL_RECEIVER",
            "not_zero_ratio": True,
            "not_nonexistence_theorem": True,
        },
        "conditional_map_disposition": {
            "charged_time_event_map": "NOT_INSTANTIABLE_NO_RECEIVER_CLASS",
            "finite_resolution_sampling": "NOT_INSTANTIABLE_NO_RECEIVER_PERIOD",
            "emitter_receiver_comparison": "NOT_INSTANTIABLE_NO_POSITIVE_DENOMINATOR_MARGIN",
            "D_R_K_transformation_law": "NOT_INSTANTIABLE_NO_COMMON_RECEIVER_CARRIER",
        },
        "coordinate_control": {
            "carrier": "homogeneous e1/e2 Maxwell source sector only",
            "frequencies": ["2*sqrt(10)/3", "2*sqrt(10)/3"],
            "exact_ratio": "1",
            "status": "COORDINATE_CONTROL_ONLY_NOT_OPERATIONAL_REDSHIFT",
        },
        "producer_request": {
            "count": 1,
            "path": str(REQUEST.relative_to(ROOT)),
            "id": request["id"],
            "sha256": hashlib.sha256(request_bytes).hexdigest(),
            "smallest_common_missing_datum": "POSITIVE_BERGER_ACTION_DERIVED_LOCAL_RECEIVER_BV_COCYCLE_UNARY_EXPORT_V1",
        },
        "mutation_results": mutations,
        "flags": {
            "EVERY_MAXIMAL_LINEAR_CANDIDATE_REPLAYED": True,
            "EXACTLY_ONE_TYPED_PRODUCER_REQUEST_EMITTED": True,
            "OPERATIONAL_FREQUENCY_RATIO_DEFINED": False,
            "COORDINATE_RATIO_PROMOTED_AS_REDSHIFT": False,
            "ADVANCED_MAP_PROMOTED_AS_SIGNAL": False,
            "PHYSICAL_RECEIVER_PROMOTED": False,
            "NONLINEAR_MEMORY_CLAIM": False,
            "PARTICLE_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSUME_POSITIVE_BERGER_ACTION_DERIVED_LOCAL_RECEIVER_BV_COCYCLE_UNARY_EXPORT_V1_THEN_COMPUTE_RECEIVER_QUOTIENT_AND_PAIRING",
        "claim_boundary": (
            "This exact theorem replays the first missing condition of all three maximal nonempty legacy linear source-to-probe candidates and proves that the operational "
            "frequency-ratio partial function has empty domain on the declared seven-row census. The homogeneous coordinate-frequency ratio equals one only as a control and is "
            "not a redshift. Exactly one typed request is issued for the smallest common missing datum, an action-derived positive-Berger local receiver BV cocycle/unary carrier. "
            "No replacement action, physical receiver, nonlinear memory, particle, phenomenology or quantum claim is supplied."
        ),
        "provenance": {
            "producer_method": "content-addressed maximal-candidate fold over the terminal receiver census and one immutable historical Git blob",
            "independent_method": "direct structural absence replay on the hashed legacy certificates, historical five-row contract reconstruction and exact coordinate-frequency control",
            "higher_tiers_not_run": {
                "tier_2": "the historical five-row contract is resolved by exact commit, repository path, blob type and SHA-256; all other inputs are current-path exact hashes",
                "tier_3": "owned by the dedicated post-repair fixed-point successor",
            },
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    return value, request


def report() -> str:
    return """# Legacy Berger operational frequency-ratio nonactivation

The terminal receiver census has no admissible physical receiver.  The three
maximal nonempty linear source-to-probe chains retain exact rank two and
retarded dependence only before receiver quotient descent.  Each fails first
at the action-derived receiver unary carrier, while the localized-current
branch also retains an external emitter.

Therefore the charged-time event, sampling and comparison maps cannot be
instantiated and no operational ratio is defined.  The equal homogeneous
Maxwell coordinate frequencies give the exact control ratio one, but that is
not a relational redshift.  Exactly one request is emitted for the smallest
common missing datum: an action-derived positive-Berger local receiver BV
cocycle in an executable unary complex.

EVIDENCE: closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json
CLOSE-OUT: DONE — all maximal candidates replayed, ratio nonactivation certified, and one minimal typed producer request issued
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, request = build()
    if args.emit:
        CERT.write_text(render(result))
        REPORT.write_text(report())
        REQUEST.write_text(render(request))
    if args.check:
        if CERT.read_text() != render(result) or REPORT.read_text() != report() or REQUEST.read_text() != render(request):
            raise SystemExit("stale operational frequency-ratio nonactivation artifacts")
    print("BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1 generation: PASS")
