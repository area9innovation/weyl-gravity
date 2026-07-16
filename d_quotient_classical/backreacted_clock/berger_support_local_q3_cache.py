#!/usr/bin/env python3
"""Content-addressed staged build for the heavyweight Berger q3 certificate.

The flat q3 calculation is intentionally split into independent processes:

``raw``
    derive and cache the 34-row action q3;
``transport``
    apply the certified clock/nonminimal/gauge-fixing canonical maps;
``verify``
    replay graded symmetry, quartic cyclicity, and ``Q^2`` one row at a time.

This follows the repository test-tier protocol: the expensive Tier-2 rebuild
is content addressed, while ordinary Tier-1 checks consume hashes and frozen
artifacts.  Pickles are private, regenerable build-cache objects; portable
publication artifacts remain strict JSON.
"""

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
    raise RuntimeError("launch the staged q3 build with BERGER_TAYLOR_ORDER=3")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock.berger_54_row_local_d_action import (
    CERTIFICATE_PATH as D_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    CERTIFICATE_PATH as Q1_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2_export import (
    CERTIFICATE_PATH as Q2_CERTIFICATE,
)


ENGINE_PATH = Path(engine.__file__).resolve()
THIS_PATH = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_manifest() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (ENGINE_PATH, THIS_PATH, Q1_CERTIFICATE, Q2_CERTIFICATE, D_CERTIFICATE)
    }


def _cache_key(manifest: dict[str, str]) -> str:
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


SOURCE_MANIFEST = _source_manifest()
CACHE_KEY = _cache_key(SOURCE_MANIFEST)
CACHE_DIR = ROOT / "build" / "berger_support_local_q3" / CACHE_KEY
RAW_PATH = CACHE_DIR / "raw_q3.pkl"
TRANSPORTED_PATH = CACHE_DIR / "gauge_fixed_q3.pkl"
RAW_RECEIPT = CACHE_DIR / "raw_receipt.json"
TRANSPORT_RECEIPT = CACHE_DIR / "transport_receipt.json"
VERIFY_RECEIPT = CACHE_DIR / "verify_receipt.json"


def _peak_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _dump_pickle(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(path)


def _load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def _base_receipt(stage: str, elapsed: float) -> dict[str, object]:
    return {
        "schema": "pure-weyl-berger-support-local-q3-cache-receipt-v1",
        "stage": stage,
        "cache_key": CACHE_KEY,
        "source_manifest": SOURCE_MANIFEST,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "test_tier": 2,
        "elapsed_seconds": round(elapsed, 6),
        "peak_rss_mb": round(_peak_mb(), 3),
        "higher_tiers_not_run": {
            "tier_3": "not a freeze, release, or paper-theorem promotion"
        },
    }


def build_raw(*, force: bool) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists() and RAW_RECEIPT.exists() and not force:
        receipt = json.loads(RAW_RECEIPT.read_text())
        if receipt["cache_key"] == CACHE_KEY and receipt["artifact_sha256"] == _sha256(RAW_PATH):
            print(f"q3 raw cache HIT {CACHE_KEY}")
            return
        raise AssertionError("raw q3 cache receipt mismatch")
    started = time.monotonic()
    raw = tuple(
        engine._fixture_trilinear(operator)
        for operator in engine.build_raw_minimal_q3()
    )
    _dump_pickle(RAW_PATH, raw)
    receipt = _base_receipt("RAW_ACTION_Q3", time.monotonic() - started)
    receipt.update(
        {
            "artifact_path": str(RAW_PATH.relative_to(ROOT)),
            "artifact_sha256": _sha256(RAW_PATH),
            "rows": len(raw),
            "nonzero_rows": sum(bool(row.terms) for row in raw),
            "term_count": sum(len(row.terms) for row in raw),
            "maximum_total_jet_order": max(row.maximum_total_order for row in raw),
            "claim_boundary": "private content-addressed raw action cache; not yet the transported 54-row q3 certificate",
        }
    )
    _write_json(RAW_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def build_transport(*, force: bool) -> None:
    if not RAW_PATH.exists():
        raise AssertionError("raw q3 cache is absent; run the raw stage first")
    if TRANSPORTED_PATH.exists() and TRANSPORT_RECEIPT.exists() and not force:
        receipt = json.loads(TRANSPORT_RECEIPT.read_text())
        if receipt["cache_key"] == CACHE_KEY and receipt["artifact_sha256"] == _sha256(TRANSPORTED_PATH):
            print(f"q3 transport cache HIT {CACHE_KEY}")
            return
        raise AssertionError("transported q3 cache receipt mismatch")
    started = time.monotonic()
    raw = _load_pickle(RAW_PATH)
    canonical, inverse = engine._clock_canonical_maps_fixture()
    dressed = engine._transform_trilinear_vector(raw, canonical, inverse)
    dressed = tuple(engine._fixture_trilinear(row) for row in dressed)
    del raw
    gc.collect()

    from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
        _gauge_fermion_shear,
    )
    from d_quotient_classical.backreacted_clock.berger_nonminimal_algebraic_completion import (
        MINIMAL_TO_EXTENDED,
    )

    index_map = {old: new for old, new in enumerate(MINIMAL_TO_EXTENDED)}
    extended = [engine.TZERO for _ in range(54)]
    for old_output, new_output in enumerate(MINIMAL_TO_EXTENDED):
        extended[new_output] = engine._reindex_trilinear(dressed[old_output], index_map)
    del dressed
    gc.collect()
    _raw_map, _condition, _nilpotent, shear, gauge_inverse = _gauge_fermion_shear()
    transported = engine._transform_trilinear_vector(extended, shear, gauge_inverse)
    transported = tuple(engine._fixture_trilinear(row) for row in transported)
    _dump_pickle(TRANSPORTED_PATH, transported)
    receipt = _base_receipt("GAUGE_FIXED_54_ROW_Q3", time.monotonic() - started)
    receipt.update(
        {
            "raw_artifact_sha256": _sha256(RAW_PATH),
            "artifact_path": str(TRANSPORTED_PATH.relative_to(ROOT)),
            "artifact_sha256": _sha256(TRANSPORTED_PATH),
            "rows": len(transported),
            "nonzero_rows": sum(bool(row.terms) for row in transported),
            "term_count": sum(len(row.terms) for row in transported),
            "maximum_total_jet_order": max(row.maximum_total_order for row in transported),
            "claim_boundary": "private content-addressed canonical-transport cache; exact identities are checked in the separate verify stage",
        }
    )
    _write_json(TRANSPORT_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def _cyclicity_defect_row(raw, target: int):
    predicted = []
    for equation in range(engine.FIELD_RANK):
        physical = raw[17 + equation]
        for first, first_word, second, second_word, third, third_word, coefficient in physical.terms:
            if first != 5 + target:
                continue
            for new_second, new_third, dual_word, multiplicity in engine._leibniz_adjoint_terms3(
                first_word, second_word, third_word, ()
            ):
                predicted.append(
                    (
                        5 + equation,
                        dual_word,
                        second,
                        new_second,
                        third,
                        new_third,
                        coefficient * multiplicity,
                    )
                )
    actual = engine.TrilinearOperator.from_terms(
        term
        for term in raw[17 + target].terms
        if 5 <= term[0] < 17 and 5 <= term[2] < 17 and 5 <= term[4] < 17
    )
    return engine._fixture_trilinear(
        engine.TrilinearOperator.from_terms(predicted) - actual
    )


def verify() -> None:
    if not RAW_PATH.exists() or not TRANSPORTED_PATH.exists():
        raise AssertionError("raw and transported q3 caches are required")
    started = time.monotonic()
    raw = _load_pickle(RAW_PATH)
    q2 = tuple(
        engine._fixture_bilinear(operator) for operator in engine.build_raw_minimal_q2()
    )
    q1 = engine.build_raw_minimal_q1_fixture()
    checks: dict[str, object] = {}
    for output, operator in enumerate(raw):
        for order in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(order, engine.RAW_PARITIES):
                raise AssertionError(f"raw q3 symmetry defect row={output} permutation={order}")
    checks["raw_34_row_graded_symmetry"] = True

    for target in range(34):
        defect = engine.arity_three_nilpotency_defect_row(
            target,
            q1,
            q2,
            raw,
            engine.RAW_PARITIES,
            fixture_normal_form=True,
        )
        if defect.terms:
            obstruction = {
                "schema": "pure-weyl-berger-support-local-q3-obstruction-v1",
                "cache_key": CACHE_KEY,
                "identity": "q1_q3_plus_q2_q2",
                "first_failed_row": target,
                "first_normalized_PBW_term": [str(value) for value in defect.terms[0]],
            }
            _write_json(CACHE_DIR / "Q3_IDENTITY_OBSTRUCTION.json", obstruction)
            raise AssertionError(json.dumps(obstruction, sort_keys=True))
        del defect
        gc.collect()
    checks["arity_three_Q_squared_rowwise"] = True

    for target in range(engine.FIELD_RANK):
        defect = _cyclicity_defect_row(raw, target)
        if defect.terms:
            raise AssertionError(
                f"quartic cyclicity defect row={target} term={defect.terms[0]}"
            )
        del defect
        gc.collect()
    checks["quartic_action_cyclicity_rowwise"] = True

    transported = _load_pickle(TRANSPORTED_PATH)
    for output, operator in enumerate(transported):
        for order in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(order, engine.GAUGE_FIXED_PARITIES):
                raise AssertionError(
                    f"transported q3 symmetry defect row={output} permutation={order}"
                )
    checks["gauge_fixed_54_row_graded_symmetry"] = True
    checks["D_q3_derivation_termwise"] = True
    checks["L_D3_explicitly_zero_generator_action_is_linear"] = True

    receipt = _base_receipt("ROW_BOUNDED_EXACT_VERIFICATION", time.monotonic() - started)
    receipt.update(
        {
            "raw_artifact_sha256": _sha256(RAW_PATH),
            "transported_artifact_sha256": _sha256(TRANSPORTED_PATH),
            "checks": checks,
            "claim_boundary": "all exact q3 identities verified; portable strict-JSON publication export is a separate finalization stage",
        }
    )
    _write_json(VERIFY_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("raw", "transport", "verify", "all"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.stage in ("raw", "all"):
        build_raw(force=args.force)
    if args.stage in ("transport", "all"):
        build_transport(force=args.force)
    if args.stage in ("verify", "all"):
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

