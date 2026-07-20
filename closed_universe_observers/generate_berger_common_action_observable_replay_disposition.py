#!/usr/bin/env python3
"""Export the fail-closed Berger common-action observable replay disposition."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    isotypic_decomposition,
    parse_coordinate,
    parse_scalar,
    vector_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-common-action-observable-replay-disposition-v1.schema.json"
)
REPORT = PACKAGE / "reports/berger-common-action-observable-replay-disposition.md"
DEPENDENCIES = {
    "minimal_channel": PACKAGE
    / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO.json",
    "minimal_payload": PACKAGE
    / "certificates/BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO_PAYLOAD.json",
    "representation_payload": PACKAGE
    / "certificates/BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION_PAYLOAD.json",
    "obstruction_payload": PACKAGE
    / "certificates/BERGER_COMMON_ACTION_OBSTRUCTION_MODULE_PAYLOAD.json",
    "records": PACKAGE
    / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json",
    "rank_two": PACKAGE
    / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "redshift": ROOT
    / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "recoil": PACKAGE
    / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "backreaction": PACKAGE
    / "certificates/BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_common_action_observable_replay_disposition.py",
    PACKAGE / "tests/test_berger_common_action_observable_replay_disposition.py",
    SCHEMA,
]
ZERO = (Fraction(0), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _profile_first_jet(coordinate) -> bool:
    return any(
        factor[0] == "profile" and factor[2] == (1,)
        for factor in coordinate[1]
    )


def _vector(entries, coordinates):
    return {
        coordinates[index]: parse_scalar(scalar)
        for index, scalar in entries
    }


def _rank(vectors):
    return len(_echelon(vectors)[0])


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    closure = [
        parse_coordinate(value)
        for value in values["representation_payload"]["closure_coordinate_basis"]
    ]
    closure_index = {
        coordinate: index for index, coordinate in enumerate(closure)
    }
    first_jet_closure = [
        coordinate for coordinate in closure if _profile_first_jet(coordinate)
    ]
    if len(first_jet_closure) != 108:
        raise AssertionError("profile-first-jet closure dimension drifted")
    decomposition = isotypic_decomposition(first_jet_closure)
    if decomposition != {0: 60, 2: 48}:
        raise AssertionError("profile-first-jet decomposition drifted")

    old_payload = values["obstruction_payload"]
    old_coordinates = [
        parse_coordinate(value) for value in old_payload["coordinate_basis"]
    ]
    old_vectors = {
        name: _vector(entries, old_coordinates)
        for name, entries in old_payload["vectors"].items()
    }
    minimal_vectors = {
        name: _vector(
            entries,
            closure,
        )
        for name, entries in values["minimal_payload"][
            "ward_vectors_on_900_coordinate_closure"
        ].items()
    }
    image = [
        old_vectors[name] for name in ("z_00", "z_01", "z_10", "z_11")
    ] + [minimal_vectors["epsilon_0"], minimal_vectors["epsilon_1"]]
    source = minimal_vectors["typed_maxwell_source"]
    image_first = [
        {
            coordinate: coefficient
            for coordinate, coefficient in vector.items()
            if _profile_first_jet(coordinate)
        }
        for vector in image
    ]
    source_first = {
        coordinate: coefficient
        for coordinate, coefficient in source.items()
        if _profile_first_jet(coordinate)
    }
    if (
        len(source_first),
        _rank(image_first),
        _rank(image_first + [source_first]),
    ) != (24, 2, 3):
        raise AssertionError("next action module ranks drifted")
    if vector_action(source_first):
        raise AssertionError("next action module ceased to be invariant")

    imported = {
        "two_record_poisson_algebra": {
            "result_id": values["records"]["result_id"],
            "imported_claim_status": values["records"]["claim_status"],
            "survival": "CERTIFIED_IN_ORIGINAL_SCOPED_AFFINE_K_LINEAR_CARRIER",
            "common_action_transport": "NO_CERTIFIED_MAP",
            "boundary": "does not construct the full apparatus Dirac bracket or recoil",
        },
        "leading_dynamical_emitter_rank_two": {
            "result_id": values["rank_two"]["result_id"],
            "imported_claim_status": values["rank_two"]["claim_status"],
            "survival": "CERTIFIED_AT_LEADING_FREE_EMITTER_ORDER",
            "common_action_transport": "NO_CERTIFIED_MAP",
            "boundary": "not a nonlinear interacting-rank or backreacted theorem",
        },
        "g0_relational_redshift": {
            "result_id": values["redshift"]["result_id"],
            "imported_claim_status": values["redshift"]["claim_status"],
            "survival": "CERTIFIED_SOURCE_FREE_GLOBAL_REDUCED_FIXTURE",
            "common_action_transport": "NO_CERTIFIED_MAP",
            "boundary": "localized retarded dressing and backreaction remain open",
        },
        "absolute_g3_recoil_order": {
            "result_id": values["recoil"]["result_id"],
            "imported_claim_status": values["recoil"]["claim_status"],
            "survival": "CERTIFIED_FORMAL_OPERATOR_AND_ORDER_ONLY",
            "common_action_transport": "NO_CERTIFIED_MAP",
            "boundary": "numerical coefficient and interacting gauge descent remain open",
        },
        "emitter_stress_clock_q2_ledger": {
            "result_id": values["backreaction"]["result_id"],
            "imported_claim_status": values["backreaction"]["claim_status"],
            "survival": "CERTIFIED_ACTION_DERIVED_Q2_JET_LEDGER",
            "common_action_transport": "OBSTRUCTED",
            "boundary": "complete q1q2/common-action replay and solved backreaction remain open",
        },
    }
    if values["minimal_channel"]["activation_disposition"][
        "representation_complete_common_action_extension_exists"
    ]:
        raise AssertionError("minimal channel unexpectedly activated replay")

    return {
        "schema": "closed-universe-berger-common-action-observable-replay-disposition-v1",
        "result_id": "BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION",
        "setting_id": values["minimal_channel"]["setting_id"],
        "claim_status": "OBSTRUCTED_NO_REPRESENTATION_COMPLETE_COMMON_ACTION_REPLAY",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name].get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "replay_gate": {
            "minimal_channel_committed_result": values["minimal_channel"][
                "result_id"
            ],
            "minimal_channel_status": values["minimal_channel"]["claim_status"],
            "representation_complete_common_action_carrier_exists": False,
            "unary_q2_rebuild_performed": False,
            "nonlinear_observable_row_classified": False,
            "reason": (
                "the complete typed-Maxwell class remains outside the "
                "action-derived rank-six image on the 900-coordinate closure"
            ),
        },
        "standalone_observable_survival_ledger": imported,
        "nonpromotion_theorem": {
            "linear_results_invalidated": [],
            "linear_results_promoted_to_nonlinear": [],
            "detector_rank_two_on_representation_complete_action_carrier": (
                "NO_CERTIFIED_MAP"
            ),
            "redshift_on_representation_complete_action_carrier": (
                "NO_CERTIFIED_MAP"
            ),
            "recoil_or_backreaction_on_gauge_reduced_interacting_carrier": (
                "NO_CERTIFIED_MAP"
            ),
            "theorem": (
                "The common-action no-go does not falsify the imported "
                "linear, source-free, or formal-order theorems in their own "
                "declared carriers. It also supplies no map transporting any "
                "of them to one representation-complete interacting carrier."
            ),
        },
        "smallest_next_action_module": {
            "id": "M_profile_first_jet_weight_zero",
            "ambient_closure_sector": "g_b h_b' vertical profile-jet grade one",
            "ambient_dimension": len(first_jet_closure),
            "ambient_isotypic_dimensions": {
                str(weight): dimension
                for weight, dimension in decomposition.items()
            },
            "current_projected_action_image_rank": _rank(image_first),
            "source_augmented_rank": _rank(image_first + [source_first]),
            "required_new_module": "one weight-0 real line",
            "source_vector_entries": [
                [
                    closure_index[coordinate],
                    [
                        [coefficient[0].numerator, coefficient[0].denominator],
                        [coefficient[1].numerator, coefficient[1].denominator],
                    ],
                ]
                for coordinate, coefficient in sorted(
                    source_first.items(),
                    key=lambda item: closure_index[item[0]],
                )
            ],
            "action_realization_status": "NO_CERTIFIED_MAP",
            "activation_gate": (
                "declare a complete local Berger-invariant scalar action "
                "ansatz with nonzero projection to this line, differentiate "
                "all cyclic slots, and replay the rank-six image"
            ),
        },
        "activation_disposition": {
            "common_action_relational_observable_theorem": False,
            "nonlinear_detector_rank_two": False,
            "nonlinear_redshift": False,
            "gauge_reduced_recoil_backreaction": False,
            "same_background_branch_to_observer_bridge": False,
            "quantum_promotion": False,
        },
        "next_gate": (
            "ACTION_REALIZATION_OF_M_PROFILE_FIRST_JET_WEIGHT_ZERO"
        ),
        "claim_boundary": (
            "This exact mixed-tag disposition imports the committed minimal "
            "Berger invariant-channel no-go and asks whether existing observer "
            "results can be replayed on one representation-complete common-"
            "action carrier. No such carrier exists: the complete typed-"
            "Maxwell class remains outside the rank-six action image on the "
            "900-coordinate closure. The unary and q2 rows are therefore not "
            "rebuilt as a repaired theory, and no nonlinear observable row is "
            "fabricated. Five imported statements retain their own original "
            "scope: the C-G4 two-record Poisson algebra on its coefficientwise "
            "affine-K plane, the leading free-emitter rank-two response, the "
            "source-free global G0 redshift fixture, the formal absolute-g3 "
            "recoil order/operator, and the action-derived emitter stress/"
            "clock q2 ledger. None is invalidated, but none is transported to "
            "a representation-complete interacting gauge quotient. The "
            "smallest next action module is exported on the exact profile-"
            "first-jet closure sector: its ambient dimension is 108 with "
            "isotypic dimensions 60 at weight zero and 48 at weight two; the "
            "current projected image has rank two and the invariant typed "
            "source raises it to three. Action realization of that one new "
            "weight-zero line remains NO_CERTIFIED_MAP. No old 440-dimensional "
            "cokernel representation, nonlinear rank promotion, branch map, "
            "particle, positivity, scattering, phenomenology or quantum claim "
            "is made."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-common-action-repair-observable-replay"
            ),
            "input_commit": "ff43b676",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def report(value: dict[str, Any]) -> str:
    module = value["smallest_next_action_module"]
    return f"""# Berger common-action observable replay disposition

No representation-complete common-action carrier exists after the minimal
epsilon-channel test, so no repaired unary/`q2` or nonlinear detector replay is
performed.

The existing two-record algebra, leading dynamical-emitter rank-two response,
source-free global redshift fixture, formal absolute-`g3` recoil operator, and
emitter stress/clock `q2` ledger remain certified only in their original
declared scopes.  None is promoted to a nonlinear interacting observer
theorem.

The smallest next action module is `{module['id']}`.  Its exact profile-first-
jet ambient sector has dimension {module['ambient_dimension']} and isotypic
dimensions `(60,48)` at weights `(0,2)`.  The current projected action image
has rank two; the invariant source raises it to three.  A local cyclic action
realizing that new trivial line remains `NO_CERTIFIED_MAP`.

CLOSE-OUT: OBSTRUCTED — no representation-complete common-action carrier exists for an observable replay; scoped linear results survive without nonlinear promotion
EVIDENCE: closed_universe_observers/certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    rendered_report = report(value)
    if args.emit:
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check and (
        not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != rendered_report
    ):
        raise SystemExit("stale common-action observable replay disposition")
    print("BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
