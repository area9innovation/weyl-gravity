#!/usr/bin/env python3
"""Export the fail-closed quartic calibration and redshift disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-quartic-calibration-relational-redshift-disposition-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-quartic-calibration-relational-redshift-disposition.md"
)
DEPENDENCIES = {
    "quartic_family": PACKAGE
    / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json",
    "quartic_family_payload": PACKAGE
    / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json",
    "quartic_moduli_gate": PACKAGE
    / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE.json",
    "quartic_moduli_payload": PACKAGE
    / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE_PAYLOAD.json",
    "observable_disposition": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json",
    "latest_action_gate": PACKAGE
    / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE
    / "verify_berger_quartic_calibration_relational_redshift_disposition.py",
    PACKAGE
    / "tests/test_berger_quartic_calibration_relational_redshift_disposition.py",
    SCHEMA,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    family = values["quartic_family"]
    family_payload = values["quartic_family_payload"]
    moduli = values["quartic_moduli_gate"]
    latest = values["latest_action_gate"]
    observable = values["observable_disposition"]

    if len(family["module_classification"]) != 2:
        raise AssertionError("emitter-labelled quartic classification drifted")
    if any(
        row["Maxwell_and_U1_invariant_dimension"] != 6
        for row in family["module_classification"]
    ):
        raise AssertionError("quartic invariant dimension drifted")
    if len(family_payload["modules"]) != 12:
        raise AssertionError("serialized quartic family dimension drifted")
    completion = moduli["completion_space"]
    if len(completion["basis"]) != 12 or completion["q3_parameter_map_rank"] != 12:
        raise AssertionError("quartic completion-space rank drifted")
    arity_three = moduli["full_arity_three_gate"]
    if (
        arity_three["admissible_subvariety"] != "EMPTY"
        or arity_three["witness_polynomial"]
        != "-4*g0*h0 + sum_i lambda_i*0"
    ):
        raise AssertionError("terminal quartic obstruction drifted")
    arity_two = latest["arity_two_gate"]
    if (
        arity_two["status"] != "OBSTRUCTED"
        or arity_two["full_covariance_projection"] != "EMPTY_ADMISSIBLE_LOCUS"
    ):
        raise AssertionError("latest arity-two action gate drifted")
    for audit in arity_two["per_emitter_audits"].values():
        projection = audit["complete_covariance_projection"]
        if (
            projection["action_image_rank"],
            projection["source_augmented_rank"],
        ) != (934, 935):
            raise AssertionError("latest covariance ranks drifted")
    witness = arity_two["decisive_witness"]
    if witness["output"] != 59 or witness["coefficient"] != [[-3, 1], [0, 1]]:
        raise AssertionError("latest Maxwell-cotangent witness drifted")

    survival = observable["standalone_observable_survival_ledger"]
    if len(survival) != 5:
        raise AssertionError("standalone observer survival ledger drifted")
    if any(
        row["common_action_transport"] not in {"NO_CERTIFIED_MAP", "OBSTRUCTED"}
        for row in survival.values()
    ):
        raise AssertionError("a standalone observable was silently promoted")

    return {
        "schema": (
            "closed-universe-berger-quartic-calibration-relational-"
            "redshift-disposition-v1"
        ),
        "result_id": (
            "BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION"
        ),
        "setting_id": latest["setting_id"],
        "claim_status": (
            "OBSTRUCTED_NO_ADMISSIBLE_QUARTIC_COMPLETION_OR_"
            "NONLINEAR_REDSHIFT_CALIBRATION_DOMAIN"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name].get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "imported_quartic_family": {
            "ambient_parameter_dimension": len(completion["basis"]),
            "basis": completion["basis"],
            "q3_parameter_map_rank": completion["q3_parameter_map_rank"],
            "pairing": family["minimal_quartic_ansatz"]["pairing"],
            "Maxwell_and_Berger_U1_invariant": True,
            "status_before_master_identities": "CERTIFIED_AMBIENT_FAMILY",
        },
        "master_identity_precedence": {
            "older_arity_three_admissible_subvariety": (
                arity_three["admissible_subvariety"]
            ),
            "older_witness_polynomial": arity_three["witness_polynomial"],
            "latest_arity_two_admissible_locus": (
                arity_two["full_covariance_projection"]
            ),
            "latest_action_image_rank_per_emitter": 934,
            "latest_source_augmented_rank_per_emitter": 935,
            "latest_first_quotient_witness": witness,
            "logical_effect": (
                "the empty arity-two common-action locus precedes and is "
                "stronger than any quartic q3 or detector calculation"
            ),
        },
        "calibration_map_disposition": {
            "declared_detector_tensor": "NO_CERTIFIED_MAP",
            "moduli_to_detector_tensor_polynomial": (
                "NOT_APPLICABLE_EMPTY_DOMAIN"
            ),
            "rank": "NOT_APPLICABLE_EMPTY_DOMAIN",
            "kernel": "NOT_APPLICABLE_EMPTY_DOMAIN",
            "stabilizer_orbits": "NOT_APPLICABLE_EMPTY_DOMAIN",
            "blind_directions": "NOT_APPLICABLE_EMPTY_DOMAIN",
            "minimal_calibration_observables": "NOT_APPLICABLE_EMPTY_DOMAIN",
            "not_the_zero_map": True,
            "reason": (
                "none of the twelve ambient quartic directions is attached "
                "to a cubic common action surviving the preceding identities"
            ),
        },
        "relational_redshift_disposition": {
            "completion_independent_nonlinear_redshift": "NO_CERTIFIED_MAP",
            "two_event_dynamical_clock_construction_performed": False,
            "transported_phase_rod_detector_construction_performed": False,
            "gauge_invariance": "NO_CERTIFIED_MAP",
            "causal_support": "NO_CERTIFIED_MAP",
            "K_Berger_covariance": "NO_CERTIFIED_MAP",
            "backreacted_rank": "NO_CERTIFIED_MAP",
            "tangent_cone_admissibility": "NO_CERTIFIED_MAP",
            "Einstein_extra_Weyl_Maxwell_sensitivity": "NO_CERTIFIED_MAP",
        },
        "standalone_observable_survival_ledger": survival,
        "nonpromotion_theorem": {
            "linear_or_source_free_results_invalidated": [],
            "linear_or_source_free_results_promoted": [],
            "statement": (
                "The empty nonlinear action locus neither invalidates the "
                "five imported observables in their original scoped carriers "
                "nor supplies a map transporting them to a same-action "
                "quartic observer algebra."
            ),
        },
        "smallest_additional_action_representation": latest[
            "first_missing_action_representation"
        ],
        "mutation_controls": {
            "dependency_hash_mutation": "DETECTED",
            "quartic_dimension_or_rank_mutation": "DETECTED",
            "arity_three_empty_locus_or_witness_mutation": "DETECTED",
            "arity_two_rank_or_Maxwell_cotangent_witness_mutation": "DETECTED",
            "causal_support_shortcut": (
                "FORBIDDEN: an empty action locus cannot be relabelled as a "
                "completion-independent or zero detector response"
            ),
        },
        "assumption_ledger": [
            "All imported certificates are consumed byte-for-byte by SHA-256.",
            "The twelve quartic directions are ambient action directions, not admissible nonlinear theories after the master identities.",
            "No compact-product mode is identified with a Berger apparatus row.",
        ],
        "missing_object_ledger": [
            "temporal Maxwell/emitter antifield covariance action module",
            "nonempty q1-closed cubic common-action locus",
            "same-action admissible quartic q3 family",
            "same-action clocks, rods, receiver, memory and detector tensor",
            "causal nonlinear relational redshift and its calibration map",
        ],
        "next_gate": (
            "ADJOIN_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_"
            "AND_REPLAY_ARITY_TWO_BEFORE_QUARTIC_CALIBRATION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE disposition imports the "
            "twelve-dimensional quartic action family, its rank-twelve q3 "
            "parameter map, the terminal empty arity-three locus, the "
            "standalone observer survival ledger, and the newer complete "
            "temporal scalar-density action obstruction by exact hash. The "
            "newer gate is already empty at arity two with ranks 934<935 per "
            "emitter and first Maxwell-cotangent quotient coefficient "
            "A_plus_0 <- (tau,e0 e1 K0_01) = -3 g0 h0. Therefore there is no "
            "admissible quartic theory domain on which a completion-independent "
            "redshift or a moduli-to-detector calibration polynomial can be "
            "defined. NOT_APPLICABLE_EMPTY_DOMAIN is not a zero-response "
            "theorem. The five earlier observer results remain certified only "
            "in their original scopes. No causal support, K_Berger, detector, "
            "redshift, memory, recoil, tangent-cone, branch or quantum claim is "
            "promoted."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-quartic-calibration-"
                "relational-redshift-disposition"
            ),
            "input_commit": "0e1e26d48",
            "source_manifest": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    return """# Quartic calibration and relational-redshift disposition

The twelve-dimensional Maxwell/Berger-U(1)-invariant quartic action family
and its rank-twelve q3 parameter map remain certified as an ambient family.
They do not define twelve admissible nonlinear theories.  The older complete
arity-three gate has empty admissible locus, and the newer complete temporal
scalar-density calculation is already obstructed at arity two:

```text
rank(action image) = 934
rank(action image + typed source) = 935
A_plus_0 <- (tau, e0 e1 K0_01) = -3 g0 h0.
```

Consequently the moduli-to-detector tensor map is
`NOT_APPLICABLE_EMPTY_DOMAIN`, not the zero map.  Its rank, kernel,
stabilizers, blind directions and number of calibration observables are
likewise not applicable.  No completion-independent nonlinear relational
redshift exists on the current action family.

The five imported linear, source-free or formal-order observer results remain
certified in their original scopes, but none is promoted to the obstructed
same-action nonlinear carrier.  The next representation is the temporal
Maxwell/emitter-antifield covariance module with A-plus/tau/K and cyclic
K-plus/tau/A descendants.

CLOSE-OUT: OBSTRUCTED — the current action family has no admissible quartic theory domain on which a nonlinear redshift or calibration map can be defined
EVIDENCE: closed_universe_observers/certificates/BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report_text = report(value)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.emit:
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(report_text)
    if args.check and (
        not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != report_text
    ):
        raise SystemExit("stale quartic calibration/redshift disposition")
    print(
        "BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION "
        "generation: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
