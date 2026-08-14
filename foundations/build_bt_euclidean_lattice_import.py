#!/usr/bin/env python3
"""Import the certified BT Euclidean lattice result into the foundations atlas."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
PILOT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json"
PREFLIGHT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1.json"
PARITY = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
REPORT = FOUNDATIONS / "reports/bt-euclidean-lattice-foundational-import.md"
EVIDENCE_ID = "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def coordinate(obligation: str) -> dict[str, str]:
    return {
        "foundation": "FINITE_DISCRETE",
        "carrier": "SMOOTH_DISTRIBUTIONAL",
        "obligation": obligation,
    }


def build() -> dict[str, Any]:
    pilot, preflight, parity = load(PILOT), load(PREFLIGHT), load(PARITY)
    if pilot.get("certificate") != "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1":
        raise ValueError("pilot identity")
    if preflight.get("certificate") != "REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1":
        raise ValueError("preflight identity")
    if parity.get("certificate") != "REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1":
        raise ValueError("parity identity")
    if pilot.get("lifecycle_state") != "CLASSIFIED" or preflight.get("lifecycle_state") != "CLASSIFIED":
        raise ValueError("source lifecycle")

    direct = [
        ("KINEMATICS_OBSERVABLES", "The finite periodic graph, mean-zero real field, positive variable, lattice action, and finite-volume observables are explicit."),
        ("STATE_EXISTENCE", "Coercivity after zero-mode fixing makes the finite-dimensional partition function finite, so a normalized Euclidean Gibbs state exists."),
        ("STATE_REPRESENTATION", "The state is represented by the positive normalized density exp(-S_E,L)/Z on the real mean-zero field hyperplane."),
        ("PROBABILITY_RULE", "Measurable finite-lattice events receive ordinary Euclidean statistical probabilities by integration against the normalized Gibbs measure."),
        ("INTERACTION_CONSTRUCTION", "For nonzero lambda the exact positive action is nonlinear; the two-site mean-zero restriction has quartic coefficient (28/3) lambda^2."),
    ]
    decisions = [
        {
            "coordinate": coordinate(obligation),
            "evidence_role": "DIRECT_LOCAL",
            "new_status": "LOCAL_RESULT",
            "status_change": True,
            "finding": finding,
            "boundary": "This is a finite Euclidean statistical construction, not a Lorentzian state, Born rule, continuum theory, or full Weyl-gravity model.",
        }
        for obligation, finding in direct
    ]
    decisions.append({
        "coordinate": coordinate("RECONSTRUCTION_LIMITS"),
        "evidence_role": "SUPPORTING",
        "new_status": "PRIORITY_GAP",
        "status_change": False,
        "finding": "The L=4 and L=6 independent-sampler preflight supplies a concrete finite-volume test and exposes the next numerical gate, but no controlled continuum or Lorentzian reconstruction.",
        "boundary": "No topology, uniform error bound, regulator-independent limit, reflection positivity theorem, analytic continuation, or observable matching is established.",
    })

    value = {
        "schema_version": "foundational-bt-euclidean-lattice-import-v1",
        "result_id": EVIDENCE_ID,
        "result_kind": "FOUNDATIONAL_EVIDENCE_IMPORT_AND_SCOPED_CARRIER_INTERFACE",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "source_classification": {
            "foundation": "FINITE_DISCRETE",
            "carrier": "SMOOTH_DISTRIBUTIONAL",
            "reason": "The base graph is finite, but the field values range over a noncompact real vector space and the state is a smooth density; this is not a finite exact sample space.",
        },
        "capability_decisions": decisions,
        "exact_evidence": {
            "configuration": pilot["finite_lattice_definition"]["carrier"],
            "positive_variable": pilot["finite_lattice_definition"]["positive_variable"],
            "zero_mode_constraint": pilot["finite_lattice_definition"]["zero_mode_constraint"],
            "action": pilot["finite_lattice_definition"]["action"],
            "measure": pilot["finite_lattice_definition"]["measure"],
            "normalizability": pilot["finite_lattice_definition"]["normalizability"],
            "interaction_witness": {
                "restriction": "two-site mean-zero direction phi=(t,-t), with a=2*lambda*t",
                "exact_action": "[(exp(a)-1)^2+(exp(-a)-1)^2]/(2*lambda^2)",
                "series_through_quartic": "4*t^2+(28/3)*lambda^2*t^4+O(t^6)",
                "quartic_coefficient": "28/3*lambda^2",
                "nonlinear_when": "lambda!=0",
            },
            "probability_rule": "P_L(A)=Z_L^-1 integral_A exp(-S_E,L(phi)) dphi on the mean-zero hyperplane",
        },
        "numerical_reproducibility_records": [{
            "id": "BT_L4_L6_INDEPENDENT_SAMPLER_REPRODUCTION",
            "assembly": "BT_EUCLIDEAN_LATTICE_PROGRAMME",
            "dependency_tag": "EUCLIDEAN-SPECTRAL",
            "status": "COARSE_REPRODUCTION_ONLY",
            "algorithms": ["zero-mode-projected HMC", "independent local random-scan Metropolis"],
            "gate_passed": "all declared finite-volume observables agree within four combined standard errors",
            "precision_gate": "not all declared observables agree within two combined standard errors",
            "maximum_absolute_cross_sampler_z": preflight["maximum_absolute_cross_sampler_z"],
            "finite_size_change_cross_algorithm_z": preflight["finite_size_change_cross_algorithm_z"],
            "continuum_status": preflight["disposition"]["continuum_step_scaling"],
            "evidence": [preflight["certificate"]],
        }],
        "carrier_interface": {
            "id": "EUCLIDEAN_TO_KREIN_CARRIER",
            "label": "Positive Euclidean lattice carrier versus BT Krein carrier",
            "status": "CERTIFIED",
            "relation": "INCOMPATIBLE",
            "source_coordinates": [coordinate("STATE_REPRESENTATION")],
            "target_coordinates": [{
                "foundation": "CLASSICAL_STANDARD",
                "carrier": "KREIN_INDEFINITE",
                "obligation": "STATE_REPRESENTATION",
            }],
            "scope": "The positive-Omega Euclidean lattice path integral and the all-real-Omega two-field BT path integral cannot be identified as the same full nonperturbative configuration space and measure.",
            "witness": {
                "source_domain": pilot["finite_lattice_definition"]["positive_variable"],
                "target_domain_caveat": parity["corroborating"]["their_caveat"],
            },
            "evidence": [pilot["certificate"], parity["certificate"], EVIDENCE_ID],
            "does_not_establish": "No obstruction is proved to a conditional perturbative, Osterwalder-Schrader, analytic-continuation, or other explicitly constructed bridge.",
        },
        "claim_flags": {
            "five_finite_euclidean_capabilities_imported": True,
            "finite_partition_function_supports_normalized_gibbs_state": True,
            "independent_sampler_coarse_reproduction_recorded": True,
            "full_nonperturbative_carriers_identified": False,
            "continuum_reconstruction_established": False,
            "physical_state_selection_established": False,
            "empirical_agreement_assessed": False,
            "lorentzian_transfer_established": False,
            "new_physics_dimension_established": False,
        },
        "does_not_establish": [
            "a finite exact carrier or finite probability sample space",
            "a physical-state-selection theorem from zero-mode fixing",
            "reflection positivity or Osterwalder-Schrader reconstruction",
            "a continuum or infinite-volume limit",
            "analytic continuation to the BT Krein theory",
            "a Born rule, scattering probability, or laboratory event rate",
            "empirical validation or out-of-sample robustness",
            "a graviton or full Weyl-gravity lattice theory",
            "a new physical dimension",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {"inputs": [
            {"path": str(PILOT.relative_to(ROOT)), "sha256": sha(PILOT)},
            {"path": str(PREFLIGHT.relative_to(ROOT)), "sha256": sha(PREFLIGHT)},
            {"path": str(PARITY.relative_to(ROOT)), "sha256": sha(PARITY)},
        ]},
        "independent_checker": {
            "path": "foundations/check_bt_euclidean_lattice_import.py",
            "checks": [
                "content-pinned source certificates",
                "exact five-direct plus one-supporting capability partition",
                "exact two-site quartic interaction coefficient",
                "coarse-four-sigma versus precision-two-sigma numerical boundary",
                "scoped positive-Euclidean versus all-real-Krein non-identity",
                "fail-closed continuum, empirical, and Lorentzian flags",
            ],
        },
        "human_report": "foundations/reports/bt-euclidean-lattice-foundational-import.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    return "\n".join([
        "# BT Euclidean lattice: foundational import", "",
        f"**Result:** `{value['result_id']}`", "",
        "## Established", "",
        "The certified BT lattice supplies five direct capabilities in the `FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL` cell family: explicit kinematics and observables, existence of a normalized finite-volume Gibbs state, a measure representation of that state, Euclidean statistical probabilities, and a nonlinear interaction.", "",
        "The state-existence statement is finite-dimensional and exact: after the constant mode is removed, the action is coercive and its partition function is finite. The interaction is not merely inferred numerically; on a two-site mean-zero direction the exact action contains `(28/3) lambda^2 t^4` when `lambda != 0`.", "",
        "## Numerical rail", "",
        "HMC and an independently implemented local Metropolis chain agree at the declared coarse four-standard-error gate, but not at a two-standard-error precision gate. The L=4 to L=6 interaction-proxy change remains unresolved. This is a `COARSE_REPRODUCTION_ONLY` numerical record, not empirical validation.", "",
        "## Carrier interface", "",
        "The positive-`Omega` Euclidean lattice measure is not identical to the all-real-`Omega` two-field BT/Krein path integral. The certified relation is therefore `INCOMPATIBLE` only for full nonperturbative identity. A conditional perturbative, reflection-positive, or analytic-continuation bridge remains an open construction problem.", "",
        "## Foundations consequence", "",
        "The five direct cells become local results. `RECONSTRUCTION_LIMITS` stays a priority gap: the finite construction and its two-volume preflight provide supporting evidence, but no topology, uniform bound, limit identification, reflection positivity, Lorentzian map, or observable matching.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/build_bt_euclidean_lattice_import.py --check",
        "python3 foundations/check_bt_euclidean_lattice_import.py",
        "python3 foundations/verify_bt_euclidean_lattice_import.py",
        "python3 -m unittest foundations.tests.test_bt_euclidean_lattice_import",
        "```", "", "## Boundaries", "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print(EVIDENCE_ID + ": " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print(EVIDENCE_ID + ": wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
