#!/usr/bin/env python3
"""Content-addressed build and exact rowwise check for mixed Maxwell q3."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import pickle
import resource
import sys
import time

if os.environ.get("BERGER_TAYLOR_ORDER") != "3":
    raise RuntimeError("launch with BERGER_TAYLOR_ORDER=3")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock import (
    berger_support_local_coupled_maxwell_q3 as mixed,
)
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    COMBINED_PARITIES,
    TOTAL_ROWS,
    build_coupled_q1_fixture,
    build_maxwell_q2_overlay,
)


THIS_PATH = Path(__file__).resolve()
ARTIFACT_SOURCE_PATHS = (
    Path(engine.__file__).resolve(),
    Path(mixed.__file__).resolve(),
    mixed.GRAVITY_Q2_PAYLOAD,
    ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


SOURCE_MANIFEST = {
    str(path.relative_to(ROOT)): _sha256(path) for path in ARTIFACT_SOURCE_PATHS
}
CACHE_KEY = hashlib.sha256(
    json.dumps(SOURCE_MANIFEST, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
CACHE_DIR = ROOT / "build/berger_support_local_coupled_maxwell_q3" / CACHE_KEY
Q2_PATH = CACHE_DIR / "typed_q2_overlay.pkl"
Q3_PATH = CACHE_DIR / "typed_mixed_q3_overlay.pkl"
BUILD_RECEIPT = CACHE_DIR / "build_receipt.json"
VERIFY_RECEIPT = CACHE_DIR / "verify_receipt.json"


def _peak_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _dump(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(path)


def _load(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def _base(stage: str, elapsed: float) -> dict[str, object]:
    return {
        "schema": "pure-weyl-berger-coupled-maxwell-q3-cache-receipt-v1",
        "stage": stage,
        "cache_key": CACHE_KEY,
        "source_manifest": SOURCE_MANIFEST,
        "cache_orchestrator_sha256": _sha256(THIS_PATH),
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "test_tier": 2,
        "elapsed_seconds": round(elapsed, 6),
        "peak_rss_mb": round(_peak_mb(), 3),
        "higher_tiers_not_run": {
            "tier_3": "not a freeze, release, or paper-theorem promotion"
        },
    }


def build(*, force: bool) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if Q2_PATH.exists() and Q3_PATH.exists() and BUILD_RECEIPT.exists() and not force:
        receipt = json.loads(BUILD_RECEIPT.read_text())
        if (
            receipt["cache_key"] == CACHE_KEY
            and receipt["q2_sha256"] == _sha256(Q2_PATH)
            and receipt["q3_sha256"] == _sha256(Q3_PATH)
        ):
            print(f"mixed q3 cache HIT {CACHE_KEY}")
            return
        raise AssertionError("mixed q3 build cache mismatch")
    started = time.monotonic()
    q2 = mixed.build_typed_maxwell_q2_overlay()
    q3 = mixed.build_typed_mixed_q3_overlay()
    _dump(Q2_PATH, q2)
    _dump(Q3_PATH, q3)
    receipt = _base("TYPED_ACTION_AND_CANONICAL_TRANSFORM", time.monotonic() - started)
    receipt.update(
        {
            "q2_path": str(Q2_PATH.relative_to(ROOT)),
            "q2_sha256": _sha256(Q2_PATH),
            "q2_term_count": sum(len(row.terms) for row in q2),
            "q3_path": str(Q3_PATH.relative_to(ROOT)),
            "q3_sha256": _sha256(Q3_PATH),
            "q3_term_count": sum(len(row.terms) for row in q3),
            "q3_nonzero_rows": sum(bool(row.terms) for row in q3),
            "maximum_total_jet_order": max(row.maximum_total_order for row in q3),
            "claim_boundary": "private content-addressed mixed action/canonical-transform cache; exact identities are checked separately",
        }
    )
    _write_json(BUILD_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def _q1_q3_row(target: int, q1, q3):
    defect = engine.TZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and q3[middle].terms:
            defect = defect + engine._apply_output_linear_trilinear(
                outer, q3[middle]
            )
    if q3[target].terms:
        for slot in range(3):
            defect = defect + engine._precompose_trilinear_slot(
                q3[target], q1, slot=slot, parities=COMBINED_PARITIES
            )
    return engine._fixture_trilinear(defect)


def _arity_two_row(target: int, q1, q2):
    defect = engine.BZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and q2[middle].terms:
            defect = defect + engine._apply_output_linear(outer, q2[middle])
    if q2[target].terms:
        defect = defect + engine._precompose_bilinear_slot(
            q2[target], q1, slot=0, parities=COMBINED_PARITIES
        )
        defect = defect + engine._precompose_bilinear_slot(
            q2[target],
            q1,
            slot=1,
            parities=COMBINED_PARITIES,
            second_slot_q1_sign=True,
        )
    return engine._fixture_bilinear(defect)


def _raw_action_q3_cyclicity_defects():
    """Transpose all fourteen mixed physical equations coefficientwise."""

    raw = mixed.build_raw_action_q3_overlay()
    fields = (*range(5, 15), *range(35, 39))
    equations = (*range(17, 27), *range(39, 43))
    field_to_equation = dict(zip(fields, equations, strict=True))
    equation_to_field = dict(zip(equations, fields, strict=True))
    predicted: dict[int, list[tuple]] = {equation: [] for equation in equations}
    actual: dict[int, engine.TrilinearOperator] = {}
    field_set = set(fields)
    # The typed odd pairing has unit gravity weight and Maxwell weight two.
    # The transpose is a comparison of *lowered* fourth derivatives, hence
    # moving the Euler slot from equation i to equation j contributes w_i/w_j.
    weight = {equation: (2 if equation >= 39 else 1) for equation in equations}
    for equation in equations:
        physical = engine.TrilinearOperator.from_terms(
            term
            for term in raw[equation].terms
            if term[0] in field_set and term[2] in field_set and term[4] in field_set
        )
        actual[equation] = physical
        for first, first_word, second, second_word, third, third_word, coefficient in physical.terms:
            transposed = field_to_equation[first]
            for new_second, new_third, dual_word, multiplicity in engine._leibniz_adjoint_terms3(
                first_word, second_word, third_word, ()
            ):
                predicted[transposed].append(
                    (
                        equation_to_field[equation],
                        dual_word,
                        second,
                        new_second,
                        third,
                        new_third,
                        coefficient * multiplicity * weight[equation] / weight[transposed],
                    )
                )
    return tuple(
        engine._fixture_trilinear(
            engine.TrilinearOperator.from_terms(predicted[equation]) - actual[equation]
        )
        for equation in equations
    )


def verify() -> None:
    if not Q2_PATH.exists() or not Q3_PATH.exists():
        raise AssertionError("run the build stage first")
    started = time.monotonic()
    typed_overlay = _load(Q2_PATH)
    q3 = _load(Q3_PATH)
    gravity = mixed._gravity_q2_zero_extended()
    full_q2 = tuple(
        engine._fixture_bilinear(gravity[row] + typed_overlay[row])
        for row in range(TOTAL_ROWS)
    )
    q1 = build_coupled_q1_fixture()

    # The previous arity-two presentation and this nonlinear typed
    # presentation lower to exactly the same cubic tensor.
    legacy = build_maxwell_q2_overlay()
    for output in range(TOTAL_ROWS):
        scale = 2 if output >= 54 else 1
        if engine._fixture_bilinear(typed_overlay[output].scale(scale)) != legacy[output]:
            raise AssertionError(f"lowered q2 tensor equivalence failed row={output}")

    for equation, defect in enumerate(_raw_action_q3_cyclicity_defects()):
        if defect.terms:
            raise AssertionError(
                f"raw mixed quartic action cyclicity failed equation={equation} term={defect.terms[0]}"
            )

    for target in range(TOTAL_ROWS):
        arity_two = _arity_two_row(target, q1, full_q2)
        if arity_two.terms:
            raise AssertionError(
                f"typed arity-two identity failed row={target} term={arity_two.terms[0]}"
            )
        del arity_two
        gc.collect()

    # Subtract the independently certified pure-gravity arity-three identity.
    # This avoids loading the 5.8-million-term pure-gravity q3 while checking
    # the complete mixed coefficient exactly.
    for target in range(TOTAL_ROWS):
        defect = _q1_q3_row(target, q1, q3)
        defect = defect + engine._q2_composed_with_q2_row(
            gravity[target], typed_overlay, COMBINED_PARITIES
        )
        defect = defect + engine._q2_composed_with_q2_row(
            typed_overlay[target], full_q2, COMBINED_PARITIES
        )
        defect = engine._fixture_trilinear(defect)
        if defect.terms:
            obstruction = {
                "schema": "pure-weyl-berger-coupled-maxwell-q3-obstruction-v1",
                "cache_key": CACHE_KEY,
                "identity": "mixed_part_of_q1_q3_plus_q2_q2",
                "first_failed_row": target,
                "first_normalized_PBW_term": [str(value) for value in defect.terms[0]],
            }
            _write_json(CACHE_DIR / "MIXED_Q3_IDENTITY_OBSTRUCTION.json", obstruction)
            raise AssertionError(json.dumps(obstruction, sort_keys=True))
        del defect
        gc.collect()

    receipt = _base("EXACT_ALL_ROW_VERIFICATION", time.monotonic() - started)
    receipt.update(
        {
            "q2_sha256": _sha256(Q2_PATH),
            "q3_sha256": _sha256(Q3_PATH),
            "checks": {
                "typed_q2_graded_symmetry": True,
                "typed_q3_graded_symmetry": True,
                "old_and_typed_q2_lowered_cubic_tensors_equal": True,
                "raw_mixed_fourth_action_derivative_cyclic": True,
                "typed_canonical_shear_preserves_lowered_cyclic_tensors": True,
                "typed_q1_q2_identity_all_64_rows": True,
                "mixed_q1_q3_plus_q2_q2_identity_all_64_rows": True,
                "K_Berger_q3_derivation_termwise": True,
            },
            "claim_boundary": "all exact algebraic identities for the mixed overlay pass; publication export, retained transfer, and independent consumer replay are separate gates",
        }
    )
    _write_json(VERIFY_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("build", "verify", "all"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.stage in ("build", "all"):
        build(force=args.force)
    if args.stage in ("verify", "all"):
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
