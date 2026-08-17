#!/usr/bin/env python3
"""Build an evidence-pinned end-to-end passport atlas for competing theories.

The atlas is a crosswalk, not a new physics calculation.  Every promoted stage
is tied to an assertion in an existing result.  A source edit therefore makes
generation fail until the crosswalk is reviewed rather than silently changing
the meaning of a passport.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1.json"
REPORT = FOUNDATIONS / "reports/end-to-end-theory-passport-atlas-v1.md"

STAGES = [
    ("FOUNDATIONAL_ASSUMPTIONS", "Foundational assumptions", "What mathematical and physical rules are being accepted at the start?"),
    ("STATE_SPACE", "State space", "What objects count as possible physical configurations or states?"),
    ("DYNAMICS", "Dynamics", "What law says how those objects evolve, respond, or are weighted?"),
    ("OBSERVABLE", "Observable", "What quantity is connected to an operation or measurement?"),
    ("PREDICTION", "Prediction", "What definite number or curve does the model produce?"),
    ("EMPIRICAL_BENCHMARK", "Empirical benchmark", "What happens when that prediction meets a declared dataset or experimental estimate?"),
]

STATUS_VOCABULARY = [
    {"id": "ESTABLISHED_EXACT", "plain_meaning": "An exact or formally checked result closes this stage in the stated scope.", "counts_as_ready": True},
    {"id": "ESTABLISHED_SCOPED", "plain_meaning": "A declared or literature-backed ingredient closes this stage only inside an explicit model boundary.", "counts_as_ready": True},
    {"id": "ESTABLISHED_NUMERIC", "plain_meaning": "A reproducible numerical calculation closes this stage under its stated protocol.", "counts_as_ready": True},
    {"id": "EMPIRICAL_PASS", "plain_meaning": "The prediction reaches data and passes the declared comparison gate; this is not validation of the complete theory.", "counts_as_ready": True},
    {"id": "EMPIRICAL_FAIL", "plain_meaning": "The prediction reaches data but fails the declared comparison gate; this is a scoped negative result, not a universal refutation.", "counts_as_ready": False},
    {"id": "PARTIAL", "plain_meaning": "Useful stage-local evidence exists, but a required piece or bridge is still missing.", "counts_as_ready": False},
    {"id": "OPEN", "plain_meaning": "The stage is required for this journey and has not been established.", "counts_as_ready": False},
    {"id": "NOT_REACHED", "plain_meaning": "The journey cannot yet make this claim because an earlier required stage is open.", "counts_as_ready": False},
]
READY = {item["id"] for item in STATUS_VOCABULARY if item["counts_as_ready"]}
ASSESSED = READY | {"EMPIRICAL_FAIL", "PARTIAL"}

SOURCE_FILES = {
    "GR_CASSINI": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
    "NGC3198_COMMON": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
    "MANNHEIM_NGC3198": "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json",
    "BT_EUCLIDEAN": "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json",
    "KREIN_FREE": "foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json",
    "CODED_WAVE": "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json",
    "PURE_WEYL": "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def pointer(value: Any, path: str) -> Any:
    if path == "":
        return value
    current = value
    for raw in path.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def assertion(source: str, path: str, expected: Any) -> dict[str, Any]:
    return {"source": source, "pointer": path, "expected": expected}


def stage(stage_id: str, status: str, summary: str, boundary: str, *assertions: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": stage_id,
        "status": status,
        "summary": summary,
        "boundary": boundary,
        "source_assertions": list(assertions),
    }


def joins_for(stages: list[dict[str, Any]]) -> list[dict[str, str]]:
    joins = []
    for left, right in zip(stages, stages[1:]):
        if left["status"] in READY and right["status"] in READY:
            status = "CLOSED"
            explanation = "Both adjacent stages are established in the declared passport scope."
        elif right["status"] == "EMPIRICAL_FAIL" and left["status"] in READY:
            status = "CLOSED_WITH_NEGATIVE_OUTCOME"
            explanation = "The prediction reaches the benchmark, where the declared comparison gate fails."
        elif right["status"] == "NOT_REACHED":
            status = "NOT_REACHED"
            explanation = "An earlier missing bridge prevents this join from carrying a claim."
        else:
            status = "OPEN"
            explanation = "At least one adjacent stage is partial or open, so composition is not certified."
        joins.append({"from": left["id"], "to": right["id"], "status": status, "explanation": explanation})
    return joins


def summarize(stages: list[dict[str, Any]], empirical: str) -> dict[str, Any]:
    ready_through = None
    first_blocker = None
    for item in stages:
        if item["status"] in READY:
            ready_through = item["id"]
        else:
            first_blocker = item["id"]
            break
    furthest = next((item["id"] for item in reversed(stages) if item["status"] in ASSESSED), None)
    reaches_benchmark = stages[-1]["status"] in {"EMPIRICAL_PASS", "EMPIRICAL_FAIL"}
    return {
        "contiguous_ready_through": ready_through,
        "first_blocker_or_failure": first_blocker,
        "furthest_stage_with_evidence": furthest,
        "ready_stage_count": sum(item["status"] in READY for item in stages),
        "assessed_stage_count": sum(item["status"] in ASSESSED for item in stages),
        "reaches_empirical_benchmark": reaches_benchmark,
        "empirical_disposition": empirical,
        "complete_theory": False,
    }


def passport(
    passport_id: str,
    label: str,
    family: str,
    scope: str,
    benchmark: str,
    dependency_tags: list[str],
    stages: list[dict[str, Any]],
    empirical: str,
    next_step: str,
) -> dict[str, Any]:
    if [item["id"] for item in stages] != [item[0] for item in STAGES]:
        raise ValueError(f"stage order for {passport_id}")
    return {
        "id": passport_id,
        "label": label,
        "family": family,
        "scope": scope,
        "benchmark_group": benchmark,
        "dependency_tags": dependency_tags,
        "stages": stages,
        "joins": joins_for(stages),
        "journey_summary": summarize(stages, empirical),
        "highest_value_next_step": next_step,
    }


def definitions() -> list[dict[str, Any]]:
    A = assertion
    return [
        passport(
            "STANDARD_GR_CASSINI", "Standard GR — Cassini", "Mainstream general relativity",
            "Static, spherical, asymptotically flat solar exterior and the published Cassini gamma estimate.",
            "CASSINI_SOLAR_SYSTEM", ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "Four-dimensional Lorentzian metric gravity with the vacuum Einstein equation outside the Sun.", "This does not cover the solar interior, cosmology, or quantum gravity.", A("GR_CASSINI", "/model_identity/id", "STANDARD_GR_VACUUM_SOLAR_EXTERIOR")),
                stage("STATE_SPACE", "ESTABLISHED_SCOPED", "Static spherical exterior metrics with asymptotic-flatness and Newtonian normalization.", "This is a deliberately restricted classical sector, not the full solution space of GR.", A("GR_CASSINI", "/model_identity/sector", "Static, spherically symmetric, asymptotically flat vacuum exterior of the Sun")),
                stage("DYNAMICS", "ESTABLISHED_EXACT", "The reduced Einstein equations integrate exactly to the Schwarzschild exterior.", "Exact only inside the declared ansatz and boundary normalization.", A("GR_CASSINI", "/claim_flags/vacuum_field_equation_to_solution_derived", True)),
                stage("OBSERVABLE", "ESTABLISHED_EXACT", "Null propagation identifies the Cassini-sensitive delay coefficient as 1+gamma.", "The operational map imports the experiment's fitted-parameter interpretation.", A("GR_CASSINI", "/claim_flags/null_delay_gamma_plus_one_coefficient_derived", True), A("GR_CASSINI", "/claim_flags/cassini_observable_map_registered", True)),
                stage("PREDICTION", "ESTABLISHED_EXACT", "The model predicts gamma=1, hence gamma-1=0.", "This is one weak-field prediction, not a test of every GR sector.", A("GR_CASSINI", "/claim_flags/ppn_gamma_equals_one_derived_exactly", True)),
                stage("EMPIRICAL_BENCHMARK", "EMPIRICAL_PASS", "The prediction lies inside the publisher's displayed Cassini uncertainty band.", "The raw spacecraft data and likelihood were not reanalysed.", A("GR_CASSINI", "/claim_flags/prediction_inside_reported_band", True), A("GR_CASSINI", "/claim_flags/cassini_likelihood_reproduced", False)),
            ], "SUPPORTED_IN_DECLARED_SCOPE", "Add an independently reproduced second solar-system benchmark and a systematics-aware comparison."),
        passport(
            "NEWTONIAN_BARYONS_NGC3198", "Newtonian baryons — NGC 3198", "Classical baryons-only control",
            "One fitted stellar scale, fixed gas, and a common analytic thin-disk geometry compared with 39 SPARC velocities.",
            "NGC3198_COMMON_PROTOCOL", ["LOCAL-ALGEBRAIC"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "Classical Newtonian gravity for the declared stellar and gas disk model.", "The common analytic disk is a comparison control, not the full SPARC mass model.", A("NGC3198_COMMON", "/models/0/model_id", "NEWTONIAN_BARYONS_ONLY")),
                stage("STATE_SPACE", "ESTABLISHED_SCOPED", "Circular tracers respond to a thin exponential stellar disk plus a fixed gas disk.", "Distance, inclination and baryonic systematics are not marginalized.", A("NGC3198_COMMON", "/claim_flags/common_baryonic_geometry_used", True)),
                stage("DYNAMICS", "ESTABLISHED_SCOPED", "The circular-speed law contains only the Newtonian stellar and gas contributions.", "One stellar mass scale is fitted to this same galaxy.", A("NGC3198_COMMON", "/models/0/parameter_count", 1)),
                stage("OBSERVABLE", "ESTABLISHED_SCOPED", "The observable is the rotation speed at the common set of 39 galactic radii.", "Only tabulated random velocity errors enter the objective.", A("NGC3198_COMMON", "/models/0/metrics/point_count", 39)),
                stage("PREDICTION", "ESTABLISHED_NUMERIC", "A deterministic fit produces a complete 39-point baryons-only rotation curve.", "This is an in-sample fit, not a held-out prediction.", A("NGC3198_COMMON", "/models/0/parameter_boundary_hit", False)),
                stage("EMPIRICAL_BENCHMARK", "EMPIRICAL_FAIL", "The reduced chi-squared is about 128.72 and fails the declared <=2 random-error gate.", "This rejects this bounded baryons-only control, not Newtonian gravity in every setting.", A("NGC3198_COMMON", "/models/0/random_error_gate/passed", False)),
            ], "FAILED_DECLARED_GATE", "Use the failure as a calibrated baseline when testing added halo or modified-gravity structure."),
        passport(
            "GR_NFW_NGC3198", "GR + NFW halo — NGC 3198", "Mainstream dark-halo phenomenology",
            "Newtonian weak-field baryons plus an NFW halo, with three fitted parameters under the common 39-point protocol.",
            "NGC3198_COMMON_PROTOCOL", ["LOCAL-ALGEBRAIC"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "Weak-field general relativity represented by Newtonian baryons plus an NFW dark-matter halo.", "No cosmological halo prior or posterior is included.", A("NGC3198_COMMON", "/models/1/model_id", "GR_NFW_DARK_HALO")),
                stage("STATE_SPACE", "ESTABLISHED_SCOPED", "The model combines the common stellar/gas disks with a spherical NFW halo.", "The halo is a phenomenological fitted component for one galaxy.", A("NGC3198_COMMON", "/claim_flags/common_baryonic_geometry_used", True)),
                stage("DYNAMICS", "ESTABLISHED_SCOPED", "Circular speed is the baryonic contribution plus the NFW circular-speed formula.", "The fit has q_star, V200 and concentration as free parameters.", A("NGC3198_COMMON", "/models/1/parameter_count", 3)),
                stage("OBSERVABLE", "ESTABLISHED_SCOPED", "The observable is the rotation speed at the same 39 radii used for both competing curves.", "The comparison uses random errors only.", A("NGC3198_COMMON", "/models/1/metrics/point_count", 39)),
                stage("PREDICTION", "ESTABLISHED_NUMERIC", "Independent optimizers agree on a fitted 39-point NFW rotation curve.", "The curve is fitted in-sample and has two more parameters than the one-parameter alternatives.", A("NGC3198_COMMON", "/claim_flags/independent_optimizer_agreement_required", True), A("NGC3198_COMMON", "/models/1/parameter_boundary_hit", False)),
                stage("EMPIRICAL_BENCHMARK", "EMPIRICAL_PASS", "Reduced chi-squared about 0.965 passes the declared <=2 gate and has the lowest AICc here.", "One galaxy without systematic-error marginalization does not select a complete theory.", A("NGC3198_COMMON", "/models/1/random_error_gate/passed", True), A("NGC3198_COMMON", "/ranking_by_AICc/0", "GR_NFW_DARK_HALO"), A("NGC3198_COMMON", "/claim_flags/complete_theory_selected", False)),
            ], "SUPPORTED_IN_DECLARED_SCOPE", "Repeat the common protocol across a preregistered galaxy sample with nuisance parameters and held-out tests."),
        passport(
            "MANNHEIM_NGC3198", "Mannheim conformal gravity — NGC 3198", "Mannheim–Kazanas programme",
            "The pure-metric conformal-gravity rotation law, common analytic disk geometry, and the same 39 SPARC velocities.",
            "NGC3198_COMMON_PROTOCOL", ["LOCAL-ALGEBRAIC"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "Four-dimensional pure-metric conformal gravity in the Mannheim–Kazanas phenomenological branch.", "The matter-sector interpretation is an explicit unresolved assumption.", A("MANNHEIM_NGC3198", "/model_identity/id", "MANNHEIM_OBRIEN_NGC3198_THIN_DISK"), A("MANNHEIM_NGC3198", "/claim_flags/matter_coupling_dispute_resolved", False)),
                stage("STATE_SPACE", "ESTABLISHED_SCOPED", "Static weak-field metrics and thin stellar/gas disks describe massive circular tracers.", "This assumes the displayed metric governs massive tracers; no galactic interior matter solution is supplied.", A("MANNHEIM_NGC3198", "/model_identity/benchmark", "GALACTIC_DYNAMICS")),
                stage("DYNAMICS", "ESTABLISHED_SCOPED", "Certified exterior and orbit-law predecessors feed the published thin-disk and universal-term formula.", "The disk integration is literature-transcribed and does not resolve the matter coupling.", A("MANNHEIM_NGC3198", "/claim_flags/exact_local_predecessors_imported_by_hash", True)),
                stage("OBSERVABLE", "ESTABLISHED_SCOPED", "The operational quantity is the circular rotation speed across NGC 3198.", "The later SPARC data are not identical to the original fitting dataset.", A("NGC3198_COMMON", "/models/2/metrics/point_count", 39)),
                stage("PREDICTION", "ESTABLISHED_NUMERIC", "A one-parameter common-protocol fit produces the complete Mannheim curve.", "This differs from reproducing the original Mannheim likelihood.", A("NGC3198_COMMON", "/models/2/model_id", "MANNHEIM_CONFORMAL_GRAVITY"), A("NGC3198_COMMON", "/models/2/parameter_count", 1)),
                stage("EMPIRICAL_BENCHMARK", "EMPIRICAL_FAIL", "Reduced chi-squared about 3.20 fails the declared <=2 random-error gate despite a low unweighted RMS.", "This is a bounded one-galaxy result, not a universal refutation of conformal gravity.", A("NGC3198_COMMON", "/models/2/random_error_gate/passed", False), A("MANNHEIM_NGC3198", "/claim_flags/empirical_support_established", False)),
            ], "FAILED_DECLARED_GATE", "Resolve or parameterize the massive-matter coupling, then test a preregistered multi-galaxy sample with systematics."),
        passport(
            "BATEMAN_TUROK_EUCLIDEAN", "Bateman–Turok — finite Euclidean lattice", "Bateman–Turok programme",
            "The positive finite-volume Euclidean lattice slice, not the proposed full Lorentzian Krein theory.",
            "NO_EMPIRICAL_BENCHMARK", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "A finite periodic graph, ordinary real integration, and a positive Euclidean weight.", "Finite graph does not mean a finite field-value space.", A("BT_EUCLIDEAN", "/source_classification/foundation", "FINITE_DISCRETE")),
                stage("STATE_SPACE", "ESTABLISHED_EXACT", "Mean-zero real lattice fields with positive Omega have a finite partition function and normalized Gibbs state.", "This is a Euclidean statistical state, not a Lorentzian physical state.", A("BT_EUCLIDEAN", "/claim_flags/finite_partition_function_supports_normalized_gibbs_state", True)),
                stage("DYNAMICS", "PARTIAL", "A nonlinear Euclidean action and Gibbs weighting are explicit, but no Lorentzian time evolution or continuation is established.", "Euclidean weighting cannot silently stand in for causal dynamics.", A("BT_EUCLIDEAN", "/claim_flags/lorentzian_transfer_established", False)),
                stage("OBSERVABLE", "PARTIAL", "Finite-volume lattice observables can be sampled under the positive Gibbs measure.", "No Born rule, scattering observable, or laboratory event rate is connected.", A("BT_EUCLIDEAN", "/claim_flags/five_finite_euclidean_capabilities_imported", True)),
                stage("PREDICTION", "PARTIAL", "Two samplers coarsely reproduce declared L=4 and L=6 finite-volume quantities.", "No controlled continuum or regulator-independent prediction follows.", A("BT_EUCLIDEAN", "/claim_flags/independent_sampler_coarse_reproduction_recorded", True), A("BT_EUCLIDEAN", "/claim_flags/continuum_reconstruction_established", False)),
                stage("EMPIRICAL_BENCHMARK", "OPEN", "No empirical benchmark has been connected to this Euclidean construction.", "Numerical reproducibility of the regulator is not empirical validation.", A("BT_EUCLIDEAN", "/claim_flags/empirical_agreement_assessed", False)),
            ], "NOT_TESTED", "Construct a controlled continuum and Euclidean-to-Lorentzian bridge before defining a physical observable."),
        passport(
            "KREIN_FREE_MODE", "Krein free-mode ground state", "Indefinite-metric / Krein programme",
            "The explicit free reduced-mode bosonic Krein–Fock carrier and its ground-state dynamics.",
            "NO_EMPIRICAL_BENCHMARK", ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_SCOPED", "Ordinary local algebra on a reduced Krein–Fock carrier with an explicit companion positive form.", "This is a reduced free system, not a full field theory.", A("KREIN_FREE", "/interface/carrier_transition", "IDENTICAL_FREE_KREIN_FOCK_CARRIER")),
                stage("STATE_SPACE", "ESTABLISHED_EXACT", "The energy selects a unique normalized vector ground state and unique normal zero-energy density state.", "Selection is conditional on the free ground-state criterion.", A("KREIN_FREE", "/claim_flags/free_ground_state_selected", True), A("KREIN_FREE", "/claim_flags/unique_normal_zero_energy_density_state_proved", True)),
                stage("DYNAMICS", "ESTABLISHED_EXACT", "The same total-energy operator generates a dynamics that fixes the vacuum.", "Stationarity alone would not make the state unique.", A("KREIN_FREE", "/claim_flags/vacuum_dynamics_invariance_proved", True), A("KREIN_FREE", "/claim_flags/stationarity_alone_implies_uniqueness", False)),
                stage("OBSERVABLE", "OPEN", "No generalized Born rule or operational field observable is joined to this state and dynamics.", "A valid free state is not yet a measurement theory.", A("KREIN_FREE", "/claim_flags/brst_compatible_state_constructed", False)),
                stage("PREDICTION", "NOT_REACHED", "No experimental number or curve follows without an observable and probability rule.", "Reduced-mode energy identities are not phenomenological predictions.", A("KREIN_FREE", "/claim_flags/interacting_ground_state_selected", False)),
                stage("EMPIRICAL_BENCHMARK", "NOT_REACHED", "No dataset is in scope for the certified free-mode interface.", "No empirical agreement is implied.", A("KREIN_FREE", "/claim_flags/lorentzian_claim", False)),
            ], "NOT_TESTED", "Define a physical observable and probability rule on the same carrier, then compute a bounded prediction."),
        passport(
            "CONSTRUCTIVE_CODED_WAVE", "Constructive coded wave observable", "Reverse mathematics / computable physics",
            "Rationally coded one-dimensional chiral-wave data and one bounded smeared observable over a weak base theory.",
            "NO_EMPIRICAL_BENCHMARK", ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_EXACT", "Finite rational codes use primitive-recursive arithmetic; RCA_0 supplies coded completion and uniform limits.", "RCA_0 is proved sufficient, not necessary or weakest.", A("CODED_WAVE", "/claim_flags/rca0_upper_bound_proved", True), A("CODED_WAVE", "/claim_flags/weakest_base_proved", False)),
                stage("STATE_SPACE", "ESTABLISHED_SCOPED", "Mean-zero rational step-pair initial data represent two chiral wave components.", "The full wave state is not reconstructed from the one observable.", A("CODED_WAVE", "/claim_flags/declared_rational_initial_data", True)),
                stage("DYNAMICS", "ESTABLISHED_EXACT", "Explicit translations evolve the two chiral components, with a uniform bounded-time reconstruction theorem.", "This does not establish curved-spacetime or variable-coefficient dynamics.", A("CODED_WAVE", "/claim_flags/uniform_bounded_time_convergence_proved", True)),
                stage("OBSERVABLE", "ESTABLISHED_EXACT", "A declared polygonal detector produces a bounded smeared amplitude with explicit rational approximants.", "It is one detector profile, not a point field or probability rule.", A("CODED_WAVE", "/claim_flags/declared_bounded_linear_observable", True), A("CODED_WAVE", "/claim_flags/explicit_cutoff_function_proved", True)),
                stage("PREDICTION", "OPEN", "The observable has no empirical calibration, source model, or measured target.", "Computing an amplitude is not yet predicting an experiment.", A("CODED_WAVE", "/claim_flags/empirical_calibration_proved", False)),
                stage("EMPIRICAL_BENCHMARK", "NOT_REACHED", "No empirical dataset can be compared until the detector profile and initial data are operationally calibrated.", "No observational support is claimed.", A("CODED_WAVE", "/claim_flags/new_lorentzian_claim", False)),
            ], "NOT_TESTED", "Calibrate a coded source and detector against one bounded wave experiment without strengthening the logical base silently."),
        passport(
            "PURE_WEYL_BV_CAUSAL", "Pure Weyl BV — causal quantum route", "Repository pure-Weyl BV–BFV programme",
            "The immutable 386-row classical BV carrier through nonlinear causal compatibility and a BRST Hadamard pseudo-state.",
            "NO_EMPIRICAL_BENCHMARK", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            [
                stage("FOUNDATIONAL_ASSUMPTIONS", "ESTABLISHED_EXACT", "The content-pinned classical pure-Weyl BV snapshot passes its import gate.", "The classical complex is authoritative; this does not certify the quantum theory.", A("PURE_WEYL", "/claim_flags/strict_pure_weyl_classical_gate_passed", True)),
                stage("STATE_SPACE", "PARTIAL", "A full-row BRST Hadamard pseudo-state exists, but positivity on physical cohomology is not certified.", "Hadamard regularity and Ward identities do not turn an indefinite covariance into a physical state.", A("PURE_WEYL", "/claim_flags/strict_386_full_bv_hadamard_two_point_constructed", True), A("PURE_WEYL", "/claim_flags/strict_386_physical_cohomology_positivity_certified", False)),
                stage("DYNAMICS", "ESTABLISHED_EXACT", "The same carrier has typed q2/q3 nonlinear compatibility with retarded and advanced Green homotopies.", "This is a causal perturbative envelope, not an all-order convergent interacting theory.", A("PURE_WEYL", "/claim_flags/strict_386_q2_q3_green_compatibility_certified", True), A("PURE_WEYL", "/claim_flags/strict_386_lambda2_general_source_cocycle_closed", True)),
                stage("OBSERVABLE", "OPEN", "No positive physical-state quotient has yet been joined to an operational observable.", "The residual Weyl-square classes are deformation classes, not one-particle graviton states.", A("PURE_WEYL", "/claim_flags/strict_386_physical_cohomology_positivity_certified", False)),
                stage("PREDICTION", "NOT_REACHED", "Renormalized Lorentzian products and a restored QME are still absent, so no quantum prediction is promoted.", "Reduced-mode or Euclidean calculations cannot fill this Lorentzian gap.", A("PURE_WEYL", "/claim_flags/renormalized_lorentzian_products_constructed", False), A("PURE_WEYL", "/claim_flags/strict_pure_weyl_qme_restored", False)),
                stage("EMPIRICAL_BENCHMARK", "NOT_REACHED", "No observational benchmark is connected to the certified quantum route.", "Classical phenomenology from another assembly cannot be transferred without a typed interface.", A("PURE_WEYL", "/claim_flags/lorentzian_full_theory_certified", False)),
            ], "NOT_TESTED", "Decide physical-cohomology positivity on the same 386-row Hadamard carrier; then construct Lorentzian products and restore or obstruct the QME."),
    ]


def build() -> dict[str, Any]:
    sources: dict[str, dict[str, Any]] = {}
    loaded: dict[str, dict[str, Any]] = {}
    for source_id, relative in SOURCE_FILES.items():
        path = ROOT / relative
        value = load(path)
        result_id = value.get("result_id")
        if not isinstance(result_id, str) or not result_id:
            raise ValueError(f"missing source result id: {relative}")
        loaded[source_id] = value
        sources[source_id] = {
            "path": relative,
            "result_id": result_id,
            "sha256": sha(path),
            "human_report": value.get("human_report"),
        }

    passports = definitions()
    for item in passports:
        for item_stage in item["stages"]:
            if not item_stage["source_assertions"]:
                raise ValueError(f"unseeded stage: {item['id']} {item_stage['id']}")
            for claim in item_stage["source_assertions"]:
                actual = pointer(loaded[claim["source"]], claim["pointer"])
                if actual != claim["expected"]:
                    raise ValueError(f"source drift: {item['id']} {item_stage['id']} {claim['source']} {claim['pointer']}: {actual!r}")

    empirical = {item["journey_summary"]["empirical_disposition"] for item in passports}
    value = {
        "schema_version": "foundational-end-to-end-theory-passport-atlas-v1",
        "result_id": "FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1",
        "result_kind": "EVIDENCE_PINNED_CROSS_ASSEMBLY_END_TO_END_COMPARISON",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-17",
        "repository_base_commit": "e070091ae701d959d4c8c5f1a76574d4fb13875f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "title": "Theory passports: from assumptions to observations",
        "plain_language_purpose": "Show how far each proposed physical framework travels along the same six-step route, where it first stops, and whether it has actually met data.",
        "comparison_rule": "Stages compare functions in a research journey, not claims of equal mathematical structure. Only evidence pinned to the named source and boundary may close a stage.",
        "stage_vocabulary": [{"id": item[0], "label": item[1], "question": item[2]} for item in STAGES],
        "status_vocabulary": STATUS_VOCABULARY,
        "sources": sources,
        "passports": passports,
        "atlas_summary": {
            "passport_count": len(passports),
            "benchmark_groups": sorted({item["benchmark_group"] for item in passports}),
            "empirical_dispositions": sorted(empirical),
            "reaches_empirical_benchmark": sum(item["journey_summary"]["reaches_empirical_benchmark"] for item in passports),
            "passes_declared_empirical_gate": sum(item["journey_summary"]["empirical_disposition"] == "SUPPORTED_IN_DECLARED_SCOPE" for item in passports),
            "fails_declared_empirical_gate": sum(item["journey_summary"]["empirical_disposition"] == "FAILED_DECLARED_GATE" for item in passports),
            "not_yet_empirically_tested": sum(item["journey_summary"]["empirical_disposition"] == "NOT_TESTED" for item in passports),
            "complete_theories": 0,
        },
        "claim_flags": {
            "fixed_six_stage_crosswalk_complete": True,
            "all_stage_promotions_source_asserted": True,
            "common_ngc3198_protocol_exposed": True,
            "scoped_empirical_pass_and_failure_distinguished": True,
            "stage_local_evidence_distinguished_from_end_to_end_composition": True,
            "complete_theory_selected": False,
            "matrix_cell_grades_promoted": False,
            "new_empirical_analysis_performed": False,
        },
        "does_not_establish": [
            "that the six stage functions have identical mathematical meaning in classical, quantum, Euclidean, constructive, and indefinite-metric theories",
            "that a stage-local theorem composes with later evidence unless the passport join is closed",
            "that passing one bounded empirical gate validates a complete theory",
            "that failing one bounded empirical gate universally refutes a research programme",
            "population-level or held-out observational performance for any galactic model",
            "a new Lorentzian, quantum, continuum, positivity, or QME result",
            "any promotion of a completion-matrix cell",
        ],
        "independent_checker": {
            "path": "foundations/check_theory_passport_atlas.py",
            "method": "Independently validates the fixed passport/stage contract, source pins and assertions, summaries, joins, and fail-closed boundary flags without importing the producer.",
        },
        "human_report": "foundations/reports/end-to-end-theory-passport-atlas-v1.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    stage_labels = {item["id"]: item["label"] for item in value["stage_vocabulary"]}
    status_short = {
        "ESTABLISHED_EXACT": "exact", "ESTABLISHED_SCOPED": "scoped", "ESTABLISHED_NUMERIC": "numeric",
        "EMPIRICAL_PASS": "pass", "EMPIRICAL_FAIL": "fail", "PARTIAL": "partial", "OPEN": "open", "NOT_REACHED": "—",
    }
    lines = [
        "# Theory passports: assumptions to observations", "",
        "**Result:** `FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1`. **Lifecycle:** `CLASSIFIED`.", "",
        value["plain_language_purpose"], "",
        "A passport is not a score for which theory is true. It is an evidence-pinned route map. A green empirical endpoint means only that a particular prediction passed a particular gate; a red endpoint means only that the declared bounded comparison failed.", "",
        "## Overview", "",
        "| Passport | Assumptions | State | Dynamics | Observable | Prediction | Data | First blocker or failure |", "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in value["passports"]:
        cells = [status_short[entry["status"]] for entry in item["stages"]]
        first = item["journey_summary"]["first_blocker_or_failure"]
        lines.append(f"| {item['label']} | " + " | ".join(cells) + f" | {stage_labels.get(first, 'none')} |")
    lines += ["", "## How to read the statuses", ""]
    lines += [f"- **{item['id'].replace('_', ' ').title()}:** {item['plain_meaning']}" for item in value["status_vocabulary"]]
    lines += ["", "## Passports", ""]
    for item in value["passports"]:
        summary = item["journey_summary"]
        lines += [
            f"### {item['label']}", "", item["scope"], "",
            f"**Empirical disposition:** `{summary['empirical_disposition']}`. **Ready through:** `{summary['contiguous_ready_through']}`. **First blocker/failure:** `{summary['first_blocker_or_failure']}`.", "",
        ]
        for entry in item["stages"]:
            lines += [f"- **{stage_labels[entry['id']]} — `{entry['status']}`:** {entry['summary']} Boundary: {entry['boundary']}"]
        lines += ["", f"**Highest-value next step:** {item['highest_value_next_step']}", ""]
    lines += ["## Evidence and audit boundary", ""]
    lines += [f"- `{source_id}` → `{source['path']}` (`{source['sha256']}`)" for source_id, source in value["sources"].items()]
    lines += ["", "Every stage carries JSON-pointer assertions into these content-pinned sources. Generation refuses source drift; the independent checker recomputes pins, assertions, joins, and summary counts.", "", "This atlas does not establish:", ""]
    lines += [f"- {item}." for item in value["does_not_establish"]]
    lines += ["", "## Reproduce", "", "```bash", "python3 foundations/build_theory_passport_atlas.py --write", "python3 foundations/check_theory_passport_atlas.py", "python3 foundations/verify_theory_passport_atlas.py", "```", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        REPORT.write_text(report(value))
    else:
        print(json.dumps(value, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
