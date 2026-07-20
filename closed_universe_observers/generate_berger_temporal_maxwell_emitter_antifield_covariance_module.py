#!/usr/bin/env python3
"""Classify the bounded temporal Maxwell/emitter antifield action module."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    constant,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
    _scalar_scale,
    _vector_add,
)
from closed_universe_observers.generate_berger_direct_temporal_ak_diff_covariance_repair import (
    Coordinate,
    Vector,
    action_columns,
    base_q2,
    canonical_sha256,
    coordinate_json,
    extended_q1,
    projection_defect,
    sha256,
    vector_manifest,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    invariant_action_basis,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    parse_action,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-emitter-antifield-covariance-module-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-emitter-antifield-covariance-module-payload-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-temporal-maxwell-emitter-antifield-covariance-module.md"
)
ORDER_THREE_PAYLOAD = (
    PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
)
DEPENDENCIES = {
    "predecessor": PACKAGE
    / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json",
    "predecessor_payload": PACKAGE
    / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR_PAYLOAD.json",
    "order_three": PACKAGE
    / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json",
    "order_three_payload": ORDER_THREE_PAYLOAD,
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE
    / "verify_berger_temporal_maxwell_emitter_antifield_covariance_module.py",
    PACKAGE
    / "tests/test_berger_temporal_maxwell_emitter_antifield_covariance_module.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]


def dual_and_sign(row: int) -> tuple[int, int]:
    """Return the exact reverse entry of the certified odd pairing."""

    if row == 3:
        return 52, 1
    if row == 52:
        return 3, -1
    if 55 <= row <= 58:
        return row + 4, -1
    if 59 <= row <= 62:
        return row - 4, 1
    if 84 <= row <= 95:
        return row + 12, 1
    if 96 <= row <= 107:
        return row - 12, -1
    raise AssertionError(f"unsupported antifield action row {row}")


def action_to_q2(action: Action) -> dict:
    """Euler-differentiate all slots through the certified odd pairing."""

    output = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = dual_and_sign(varied[0])
            word = varied[1]
            if not word:
                tensor_add_symmetric(
                    output,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            total_sign = pairing_sign * (-1) ** len(word)
            expansion = arity.apply_output_word(
                tuple(reversed(word)),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            for (left_word, right_word), expanded in expansion.items():
                tensor_add_symmetric(
                    output,
                    dual,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(expanded, rational(total_sign)),
                )
    return output


def action_column(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    action: Action,
    emitter: int,
) -> tuple[Vector, dict]:
    tensor = action_to_q2(action)
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return projection_defect(q1, indexed_q1, q2, emitter), tensor


def strip_switch(coefficient: replay.Polynomial, emitter: int) -> replay.Polynomial:
    """Remove the physical ``g_b h_b`` factor for the cotangent companion."""

    output: replay.Polynomial = {}
    for monomial, scalar in coefficient.items():
        reduced = tuple(
            factor
            for factor in monomial
            if not (
                (factor[0] == "parameter" and factor[1] == f"g{emitter}")
                or (factor[0] == "profile" and factor[1] == f"h{emitter}")
            )
        )
        output = replay.add(output, {reduced: scalar})
    return output


def transform_action(action: Action, emitter: int, sector: str) -> Action:
    """Map ``chi K A`` into one of the two forced cotangent sectors."""

    if sector not in {"A_plus_tau_K", "K_plus_tau_A"}:
        raise ValueError("unknown antifield sector")
    output: Action = {}
    for factors, coefficient in action.items():
        mapped = []
        for row, word in factors:
            if row == 108:
                row = 3
            elif sector == "A_plus_tau_K" and 55 <= row <= 58:
                row += 4
            elif (
                sector == "K_plus_tau_A"
                and 84 + 6 * emitter <= row < 90 + 6 * emitter
            ):
                row += 12
            mapped.append((row, word))
        if sector == "K_plus_tau_A":
            coefficient = strip_switch(coefficient, emitter)
        action_add(output, tuple(mapped), coefficient)
    return output


def lower_action(
    emitter: int,
    terms: list[tuple[int, int, tuple[int, ...], tuple]],
    sector: str,
) -> Action:
    """Return one canonical order-zero/one/two antifield action."""

    output: Action = {}
    coefficient = product(
        parameter(f"g{emitter}"),
        profile(f"h{emitter}", ()),
    )
    for krow, arow, word, scalar in terms:
        if sector == "A_plus_tau_K":
            factors = ((3, ()), (krow, ()), (arow + 4, word))
            current = scale(coefficient, scalar)
        else:
            factors = ((3, ()), (krow + 12, ()), (arow, word))
            current = scale(constant(1), scalar)
        action_add(output, factors, current)
    return output


def reflection_parity(action: Action, emitter: int) -> int:
    """Return the leading-symbol reflection parity of one invariant action."""

    base = 84 + 6 * emitter
    leading_order = max(
        sum(len(word) for _row, word in factors) for factors in action
    )
    parities = set()
    for factors in action:
        if sum(len(word) for _row, word in factors) != leading_order:
            continue
        value = 0
        for row, word in factors:
            value += word.count(2)
            if row in {57, 61}:
                value += 1
            if row in {base + 1, base + 3, base + 5}:
                value += 1
            if row in {base + 13, base + 15, base + 17}:
                value += 1
        parities.add(value % 2)
    if len(parities) != 1:
        raise AssertionError(
            "antifield action lost leading-symbol reflection homogeneity"
        )
    return parities.pop()


def reduce_vector(
    vector: Vector,
    pivots: list[Coordinate],
    basis: list[Vector],
) -> Vector:
    residual = dict(vector)
    for pivot, existing in zip(pivots, basis, strict=True):
        if pivot in residual:
            residual = _vector_add(
                residual,
                existing,
                _scalar_scale(residual[pivot], Fraction(-1)),
            )
    return residual


def module_actions(emitter: int) -> list[tuple[str, str, str, Action]]:
    """Return the complete inherited bounded module through order three."""

    output = []
    for order in (0, 1, 2):
        basis, _audit = invariant_action_basis(emitter, order)
        for sector in ("A_plus_tau_K", "K_plus_tau_A"):
            for name, terms in basis:
                output.append(
                    (
                        f"{sector}.lower.{name}",
                        sector,
                        f"order_{order}",
                        lower_action(emitter, terms, sector),
                    )
                )
    payload = json.loads(ORDER_THREE_PAYLOAD.read_text())
    for sector in ("A_plus_tau_K", "K_plus_tau_A"):
        for name, module in payload["modules"].items():
            if module["emitter"] != emitter:
                continue
            output.append(
                (
                    f"{sector}.{name}",
                    sector,
                    "order_3_IBP_closed",
                    transform_action(
                        parse_action(module["action_entries"]),
                        emitter,
                        sector,
                    ),
                )
            )
    if len(output) != 2048:
        raise AssertionError("complete antifield action count drifted")
    return output


def build_payload() -> dict[str, Any]:
    q1, indexed_q1 = extended_q1()
    base = base_q2()
    emitter_audits = {}
    for emitter in (0, 1):
        _names, old_columns, _actions = action_columns(
            q1, indexed_q1, emitter
        )
        source = projection_defect(q1, indexed_q1, base, emitter)
        old_pivots, old_basis = _echelon(old_columns)
        source_quotient = reduce_vector(source, old_pivots, old_basis)
        if len(old_pivots) != 934 or len(source_quotient) != 42:
            raise AssertionError("imported quotient drifted")

        quotient_columns = []
        records = []
        by_sector = {"A_plus_tau_K": [], "K_plus_tau_A": []}
        by_tier = {
            "order_0": [],
            "order_1": [],
            "order_2": [],
            "order_3_IBP_closed": [],
        }
        for name, sector, tier, action in module_actions(emitter):
            column, tensor = action_column(q1, indexed_q1, action, emitter)
            quotient = reduce_vector(column, old_pivots, old_basis)
            quotient_columns.append(quotient)
            by_sector[sector].append(quotient)
            by_tier[tier].append(quotient)
            entries = _action_entries(action)
            records.append(
                {
                    "id": name,
                    "sector": sector,
                    "tier": tier,
                    "reflection_parity": (
                        "odd" if reflection_parity(action, emitter) else "even"
                    ),
                    "action_entry_count": len(entries),
                    "action_sha256": canonical_sha256(entries),
                    "q2_key_count": len(tensor),
                    "projection_column_manifest": vector_manifest(column),
                    "old_image_quotient_manifest": vector_manifest(quotient),
                }
            )

        quotient_pivots, quotient_basis = _echelon(quotient_columns)
        final_source = reduce_vector(
            source_quotient, quotient_pivots, quotient_basis
        )
        augmented_rank = len(_echelon(quotient_columns + [source_quotient])[0])
        if augmented_rank != len(quotient_pivots) + 1 or not final_source:
            raise AssertionError("antifield module unexpectedly repaired source")
        first_coordinate, first_coefficient = min(final_source.items())
        expected = (59, 3, (), 84 + 6 * emitter, (0, 1))
        if (
            first_coordinate[0] != expected
            or first_coefficient != (Fraction(-3), Fraction(0))
        ):
            raise AssertionError("antifield quotient witness drifted")

        sector_mutations = {}
        for omitted, retained in (
            ("A_plus_tau_K", "K_plus_tau_A"),
            ("K_plus_tau_A", "A_plus_tau_K"),
        ):
            retained_rank = len(_echelon(by_sector[retained])[0])
            retained_augmented = len(
                _echelon(by_sector[retained] + [source_quotient])[0]
            )
            sector_mutations[f"omit_{omitted}"] = {
                "retained_action_count": len(by_sector[retained]),
                "quotient_action_rank": retained_rank,
                "source_augmented_rank": retained_augmented,
                "detected": retained_rank < len(quotient_pivots),
            }

        emitter_audits[f"emitter_{emitter}"] = {
            "old_action_image_rank": len(old_pivots),
            "old_source_augmented_rank": len(
                _echelon(old_columns + [source])[0]
            ),
            "old_source_quotient_manifest": vector_manifest(source_quotient),
            "complete_antifield_module": {
                "action_count": len(records),
                "sector_counts": {
                    name: len(columns) for name, columns in by_sector.items()
                },
                "tier_counts": {
                    name: len(columns) for name, columns in by_tier.items()
                },
                "reflection_counts": {
                    parity: sum(
                        record["reflection_parity"] == parity
                        for record in records
                    )
                    for parity in ("even", "odd")
                },
                "action_records_canonical_sha256": canonical_sha256(records),
                "records": records,
            },
            "complete_projection": {
                "new_quotient_action_rank": len(quotient_pivots),
                "full_action_image_rank": len(old_pivots)
                + len(quotient_pivots),
                "source_augmented_rank": len(old_pivots) + augmented_rank,
                "admissible": False,
                "final_quotient_manifest": vector_manifest(final_source),
                "first_quotient_witness": coordinate_json(
                    first_coordinate, first_coefficient
                ),
            },
            "mutations": {
                **sector_mutations,
                "omit_tier": {
                    tier: {
                        "omitted_action_count": len(columns),
                        "detected_by_action_count": bool(columns),
                    }
                    for tier, columns in by_tier.items()
                },
            },
        }
    return {
        "schema": (
            "closed-universe-berger-temporal-maxwell-emitter-antifield-"
            "covariance-module-payload-v1"
        ),
        "result_id": (
            "BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_"
            "COVARIANCE_MODULE_PAYLOAD"
        ),
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "module_normal_form": {
            "old_carrier_rows": True,
            "new_rows": 0,
            "sectors": ["A_plus_tau_K", "K_plus_tau_A"],
            "lower_orders": [0, 1, 2],
            "top_order": 3,
            "top_order_normal_form": (
                "all 932 inherited IBP-closed U1 actions per sector and "
                "emitter, with all differentiated placements and both "
                "reflection parities"
            ),
            "A_plus_sector_coefficient_grade": "g_b h_b",
            "K_plus_sector_coefficient_grade": "constant cotangent companion",
        },
        "emitter_audits": emitter_audits,
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    audits = payload["emitter_audits"]
    audit_summaries = {}
    for emitter, audit in audits.items():
        module = audit["complete_antifield_module"]
        audit_summaries[emitter] = {
            "old_action_image_rank": audit["old_action_image_rank"],
            "old_source_augmented_rank": audit["old_source_augmented_rank"],
            "old_source_quotient_manifest": audit[
                "old_source_quotient_manifest"
            ],
            "complete_antifield_module": {
                key: value
                for key, value in module.items()
                if key != "records"
            },
            "complete_projection": audit["complete_projection"],
            "mutations": audit["mutations"],
        }
    first = audits["emitter_0"]["complete_projection"][
        "first_quotient_witness"
    ]
    return {
        "schema": (
            "closed-universe-berger-temporal-maxwell-emitter-antifield-"
            "covariance-module-v1"
        ),
        "result_id": (
            "BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE"
        ),
        "setting_id": dependencies["predecessor"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_COMPLETE_EXISTING_CARRIER_TEMPORAL_"
            "MAXWELL_EMITTER_ANTIFIELD_MODULE"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": value.get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for (name, path), value in zip(
                DEPENDENCIES.items(), dependencies.values(), strict=True
            )
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
        },
        "representation_and_action_module": {
            "carrier_extension": "NO_NEW_ROWS: complete existing-row antifield action module",
            "action_count_per_emitter": 2048,
            "forced_sectors": ["A_plus_tau_K", "K_plus_tau_A"],
            "bounded_derivative_orders": [0, 1, 2, 3],
            "IBP_and_Berger_U1_closure": "CERTIFIED",
            "both_reflection_parities": "CERTIFIED",
            "Diff_Weyl_Maxwell_emitter_cotangent_scope": (
                "the two sectors are the complete old-row cotangent lift of "
                "the inherited chi-K-A scalar-density normal form"
            ),
        },
        "q1_pairing_real_structure": {
            "q1_change": "ZERO",
            "q1_nilpotency": "CERTIFIED_UNCHANGED_BY_EXACT_HASH",
            "odd_pairing": "CERTIFIED_EXISTING_108_ROW_PAIRING_PLUS_AUXILIARY_PAIR",
            "real_structure": "CERTIFIED: all action coefficients lie in Q(sqrt(10)) with real scalar extension",
            "action_Hessian": "CERTIFIED",
            "odd_cyclicity": (
                "CERTIFIED because every q2 column is the Euler Hessian of "
                "one serialized local action through the signed odd pairing"
            ),
        },
        "arity_two_gate": {
            "status": "OBSTRUCTED",
            "per_emitter_audits": audit_summaries,
            "decisive_witness": first,
            "theorem": (
                "The source is outside the image even after adjoining all "
                "2048 existing-row antifield actions per emitter through the "
                "inherited order-three IBP/U1 normal form."
            ),
        },
        "first_missing_representation": {
            "object": (
                "a genuinely new q1-preimage representation for the Maxwell "
                "cotangent row A_plus, completed through the Maxwell "
                "ghost-antifield differential so q1 remains nilpotent"
            ),
            "selected_support": (
                "a new degree-compatible middle row B with q1 image reaching "
                "A_plus_0 and q2(B <- tau,K0_01), together with its signed "
                "cotangent and nilpotency descendants"
            ),
            "why_existing_rows_are_insufficient": (
                "the complete 2048-column old-row antifield action module "
                "leaves the source one rank outside its image for both emitters"
            ),
        },
        "mutations": {
            "omit_A_plus_tau_K_sector": "DETECTED",
            "omit_K_plus_tau_A_sector": "DETECTED",
            "omit_each_derivative_tier": "DETECTED_BY_ACTION_COUNT_AND_MANIFEST",
            "source_isolation": "CERTIFIED_FOR_BOTH_EMITTERS",
        },
        "downstream_disposition": {
            "q3_or_quartic_replay": "NO_CERTIFIED_MAP",
            "K_Berger": "NO_CERTIFIED_MAP",
            "detector_redshift_memory_recoil": "NO_CERTIFIED_MAP",
            "tangent_cone_branch_quantum": "NO_CERTIFIED_MAP",
        },
        "assumption_ledger": [
            "The predecessor 934-column module and -3 g_b h_b quotient are imported unchanged.",
            "The completeness theorem is bounded by the inherited local total-derivative-order-three IBP normal form.",
            "No new carrier row or cross-background identification is introduced.",
        ],
        "missing_object_ledger": [
            "new q1-preimage row for the Maxwell cotangent complex",
            "nilpotency and cotangent completion of that new row",
            "nonempty common-action arity-two locus",
            "same-action q3, K_Berger and relational observer replay",
        ],
        "next_gate": (
            "CLASSIFY_NEW_MAXWELL_COTANGENT_Q1_PREIMAGE_MAPPING_CONE_"
            "BEFORE_ANY_Q3_OR_OBSERVER_PROPAGATION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction imports the "
            "complete predecessor by hash and adjoins, per emitter, all 2048 "
            "existing-row A-plus/tau/K and K-plus/tau/A action directions "
            "through total derivative order three. The module includes the "
            "complete lower-order U1 kernels and both transforms of all 932 "
            "IBP-closed top-order actions, with both reflection parities. q1 "
            "is unchanged and nilpotent; the odd pairing and real structure "
            "are unchanged; every q2 column is an action Hessian. Nevertheless "
            "the complete tau-star/A-plus covariance source raises the exact "
            "image rank by one for both emitters and retains first quotient "
            "coefficient A_plus_0 <- (tau,e0 e1 Kb_01) = -3 g_b h_b. This "
            "projected obstruction suffices to rule out a complete arity-two "
            "solution in the declared module. No q3, K_Berger, detector, "
            "redshift, memory, recoil, tangent-cone, branch or quantum claim "
            "is promoted."
        ),
        "provenance": {
            "science_forge_work_item": (
                "sf:program/work/observer-temporal-maxwell-emitter-"
                "antifield-covariance-module"
            ),
            "input_commit": "0e1e26d4844241cb70280f714cba5bc22306c60d",
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
    audit = value["arity_two_gate"]["per_emitter_audits"]["emitter_0"]
    projection = audit["complete_projection"]
    return f"""# Temporal Maxwell/emitter antifield covariance module

The bounded existing-carrier completion contains 2,048 local actions per
emitter: every Berger-U(1)-invariant A-plus/tau/K and K-plus/tau/A action at
orders zero, one and two, plus both cotangent transforms of all 932 inherited
IBP-closed order-three actions.  Both reflection parities and all
differentiated placements are retained.  q1 is unchanged; all q2 columns are
exact action Hessians through the certified odd pairing.

The complete module does not close the joint tau-star/A-plus covariance
projection.  Its full image rank is
`{projection['full_action_image_rank']}` and adjoining the source raises it to
`{projection['source_augmented_rank']}` for each source-isolated emitter.  The
final quotient has
`{projection['final_quotient_manifest']['coordinate_count']}` coordinates and
begins at

```text
A_plus_0 <- (tau, e0 e1 K0_01) = -3 g0 h0.
```

Thus no action on the existing 110-row carrier supplies the missing
covariance.  The first unexcluded representation is a genuinely new q1
preimage of the Maxwell cotangent row, together with the Maxwell
ghost-antifield and signed cotangent descendants required for nilpotency.

CLOSE-OUT: OBSTRUCTED — the complete bounded existing-row antifield action module retains the exact Maxwell-cotangent quotient class
EVIDENCE: closed_universe_observers/certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    value = build_certificate(payload)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report_text = report(value)
    for document, schema_path in (
        (payload, PAYLOAD_SCHEMA),
        (value, SCHEMA),
    ):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    if args.emit:
        PAYLOAD.write_text(payload_text)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(report_text)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != payload_text
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != report_text
    ):
        raise SystemExit("stale temporal Maxwell/emitter antifield artifact")
    print(
        "BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE "
        "generation: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
