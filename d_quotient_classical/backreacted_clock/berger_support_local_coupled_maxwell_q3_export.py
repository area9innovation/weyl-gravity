#!/usr/bin/env python3
"""Publish the typed coupled Maxwell q2 and action-derived mixed q3."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys
from typing import Any

if os.environ.get("BERGER_TAYLOR_ORDER") != "3":
    raise RuntimeError("launch with BERGER_TAYLOR_ORDER=3")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock import (
    berger_support_local_coupled_maxwell_q3_cache as cache,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2_export import (
    _multiindex,
    _quadratic_coefficient,
)


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json"
Q2_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
Q3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
GENERATED = ROOT / "d_quotient_classical/generated/berger_support_local_coupled_maxwell_q3"
REPORT = ROOT / "d_quotient_classical/reports/berger-support-local-coupled-maxwell-q3.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-v1.schema.json"
Q2_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-typed-payload-v1.schema.json"
Q3_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-payload-v1.schema.json"
ROW_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-row-v1.schema.json"
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3.py",
    ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3_cache.py",
    Path(__file__).resolve(),
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_support_local_coupled_maxwell_q3.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_support_local_coupled_maxwell_q3.py",
    SCHEMA,
    Q2_SCHEMA,
    Q3_SCHEMA,
    ROW_SCHEMA,
)

DEPENDENCIES = {
    "gravity_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "gravity_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
    "gravity_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json",
    "legacy_arity_two_presentation": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "legacy_arity_two_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    "portable_unary_pairing_sdr": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "generator_signoff": ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _json(value: object, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_pickle(path: Path):
    with path.open("rb") as handle:
        return pickle.load(handle)


def _bilinear_row(output: int, operator) -> dict[str, Any]:
    terms = [
        [
            left,
            _multiindex(left_word),
            right,
            _multiindex(right_word),
            _quadratic_coefficient(coefficient),
        ]
        for left, left_word, right, right_word, coefficient in operator.terms
    ]
    terms.sort(key=lambda term: (term[0], tuple(term[1]), term[2], tuple(term[3])))
    body = {"output": output, "terms": terms}
    return {**body, "canonical_sha256": _digest(body)}


def _trilinear_row(output: int, operator) -> dict[str, Any]:
    terms = [
        [
            first,
            _multiindex(first_word),
            second,
            _multiindex(second_word),
            third,
            _multiindex(third_word),
            _quadratic_coefficient(coefficient),
        ]
        for first, first_word, second, second_word, third, third_word, coefficient in operator.terms
    ]
    terms.sort(
        key=lambda term: (
            term[0], tuple(term[1]), term[2], tuple(term[3]), term[4], tuple(term[5])
        )
    )
    body = {"output": output, "terms": terms}
    return {**body, "canonical_sha256": _digest(body)}


def _write_gzip(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _json(value, compact=True).encode()
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
            handle.write(encoded)


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not cache.BUILD_RECEIPT.exists() or not cache.VERIFY_RECEIPT.exists():
        raise AssertionError("content-addressed mixed q3 build and verify receipts are absent")
    build_receipt = json.loads(cache.BUILD_RECEIPT.read_text())
    verify_receipt = json.loads(cache.VERIFY_RECEIPT.read_text())
    if not all(verify_receipt["checks"].values()):
        raise AssertionError("mixed q3 exact verification is not complete")
    q2 = _load_pickle(cache.Q2_PATH)
    q3 = _load_pickle(cache.Q3_PATH)

    q2_payload = {
        "schema": "pure-weyl-berger-support-local-coupled-maxwell-q2-typed-payload-v1",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3",
        "shape": [64, 64, 64],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "composition": "zero-extend the pinned 54-row gravity q2 and add this typed Maxwell overlay; pair with Omega_typed=Omega_legacy diag(I54,2 I10)",
        "rows": [_bilinear_row(output, operator) for output, operator in enumerate(q2)],
    }

    GENERATED.mkdir(parents=True, exist_ok=True)
    chunks = []
    for output, operator in enumerate(q3):
        row = _trilinear_row(output, operator)
        path = GENERATED / f"row_{output:02d}.json.gz"
        _write_gzip(path, row)
        chunks.append(
            {
                "output": output,
                "path": str(path.relative_to(ROOT)),
                "file_sha256": _sha256(path),
                "canonical_sha256": row["canonical_sha256"],
                "term_count": len(row["terms"]),
                "maximum_total_jet_order": max(
                    (
                        sum(term[1]) + sum(term[3]) + sum(term[5])
                        for term in row["terms"]
                    ),
                    default=0,
                ),
            }
        )
    q3_payload = {
        "schema": "pure-weyl-berger-support-local-coupled-maxwell-q3-payload-v1",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3",
        "shape": [64, 64, 64, 64],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "storage": "deterministic-gzip-strict-json-row-chunks",
        "chunks": chunks,
    }

    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    carrier = dependencies["portable_unary_pairing_sdr"]
    certificate = {
        "schema": "pure-weyl-berger-support-local-coupled-maxwell-q3-v1",
        "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_TYPED_SUPPORT_LOCAL_MIXED_GRAVITY_MAXWELL_Q3",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name].get("result_id", name),
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
        },
        "typed_cyclic_presentation": {
            "scale_operator": "S=diag(I_54,2 I_10)",
            "pairing": "Omega_typed=Omega_legacy S",
            "binary_operation": "q2_typed=S^{-1} q2_legacy",
            "lowered_tensor_identity": "Omega_typed q2_typed=Omega_legacy q2_legacy",
            "canonical_shear": "F2_typed=S^{-1} F2_legacy",
            "reason": "output-only normalization is not functorial under coderivation composition; the factor two belongs to the Maxwell fibre pairing",
            "unary_pairing_source": {
                "path": str(DEPENDENCIES["portable_unary_pairing_sdr"].relative_to(ROOT)),
                "legacy_pairing_canonical_sha256": carrier["full_complex"]["cyclic_pairing"]["sha256"],
            },
        },
        "derivation": {
            "source": "fourth derivative of -1/4 sqrt(-g) F_ab F^ab plus the finite BV-canonical covariant-ghost shear",
            "formula": "q3_mixed=A3_Maxwell+[B2_full,F2_typed]+1/2[[q1,F2_typed],F2_typed]",
            "not_fitted_to_residual_or_defect_data": True,
            "raw_action_term_count": 25662,
            "linearly_transported_action_term_count": 59094,
        },
        "classical_binary_q2_typed": {
            "payload_path": str(Q2_PAYLOAD.relative_to(ROOT)),
            "payload_file_sha256": hashlib.sha256(_json(q2_payload, compact=True).encode()).hexdigest(),
            "payload_canonical_sha256": _digest(q2_payload),
            "term_count": sum(len(row.terms) for row in q2),
            "support_local": True,
        },
        "classical_ternary_q3_mixed": {
            "payload_path": str(Q3_PAYLOAD.relative_to(ROOT)),
            "payload_file_sha256": hashlib.sha256(_json(q3_payload, compact=True).encode()).hexdigest(),
            "payload_canonical_sha256": _digest(q3_payload),
            "term_count": sum(len(row.terms) for row in q3),
            "nonzero_rows": sum(bool(row.terms) for row in q3),
            "maximum_total_jet_order": max(row.maximum_total_order for row in q3),
            "support_local": True,
        },
        "exact_checks": verify_receipt["checks"],
        "cache_receipts": {
            "cache_key": cache.CACHE_KEY,
            "build": {
                "elapsed_seconds": build_receipt["elapsed_seconds"],
                "peak_rss_mb": build_receipt["peak_rss_mb"],
                "q2_sha256": build_receipt["q2_sha256"],
                "q3_sha256": build_receipt["q3_sha256"],
            },
            "verify": {
                "elapsed_seconds": verify_receipt["elapsed_seconds"],
                "peak_rss_mb": verify_receipt["peak_rss_mb"],
            },
        },
        "flags": {
            "BERGER_TYPED_MAXWELL_DARBOUX_NORMALIZATION": True,
            "BERGER_TYPED_COUPLED_Q2": True,
            "BERGER_ACTION_DERIVED_MIXED_Q3": True,
            "BERGER_MIXED_ARITY_THREE_IDENTITY": True,
            "BERGER_MIXED_Q3_K_EQUIVARIANT": True,
            "BERGER_RETAINED_MIXED_ELL3_TRANSFER": False,
            "BERGER_MIXED_Q3_INDEPENDENT_QUANTUM_ACCEPTANCE": False,
            "QUANTUM_CLAIM": False,
        },
        "verification_commands": [
            "BERGER_TAYLOR_ORDER=3 PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3_cache.py all",
            "BERGER_TAYLOR_ORDER=3 PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_support_local_coupled_maxwell_q3_export.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_support_local_coupled_maxwell_q3.py",
        ],
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem exports the exact typed 64-row gravity-clock-Maxwell q2 presentation and the 59,598-term mixed q3 overlay derived from the Maxwell action and a finite BV-canonical shear. It proves the all-row mixed arity-three L-infinity identity and K_Berger equivariance. It supersedes the output-only arity-two normalization only for nonlinear coderivation composition; both presentations have the identical lowered cubic action tensor. It does not yet transfer ell3 through the 64-to-36 SDR, construct the exchange contribution, perform independent quantum-side acceptance, restore a QME, or make a quantum claim.",
    }
    return certificate, q2_payload, q3_payload


def _report(certificate: dict[str, Any]) -> str:
    q3 = certificate["classical_ternary_q3_mixed"]
    return f"""# Typed coupled Maxwell q2 and mixed q3

The exact mixed gravity--Maxwell arity-three operation is now exported on all
64 gauge-fixed BV rows.  It contains **{q3['term_count']:,}** PBW
coefficients in {q3['nonzero_rows']} nonzero output rows and has maximum
total jet order {q3['maximum_total_jet_order']}.

The factor-two arity-two repair is now typed correctly.  With
`S=diag(I54,2 I10)`, the nonlinear presentation uses
`Omega_typed=Omega_legacy S` and `q2_typed=S^-1 q2_legacy`; hence the lowered
cubic tensor is unchanged.  This matters at q3 because output scaling alone
does not commute with coderivation composition.

The mixed operation is derived from the fourth Maxwell action derivative and
the finite BV-canonical ghost shear.  Exact row-bounded replay proves the
mixed part of `q1 q3+q2 q2=0` on every row.  The retained ell3 transfer and
independent quantum consumer remain fail-closed.
"""


def write() -> None:
    certificate, q2_payload, q3_payload = build()
    Q2_PAYLOAD.write_text(_json(q2_payload, compact=True))
    Q3_PAYLOAD.write_text(_json(q3_payload, compact=True))
    CERTIFICATE.write_text(_json(certificate))
    REPORT.write_text(_report(certificate))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check:
        expected = build()
        current = (
            json.loads(CERTIFICATE.read_text()),
            json.loads(Q2_PAYLOAD.read_text()),
            json.loads(Q3_PAYLOAD.read_text()),
        )
        if current != expected:
            raise AssertionError("mixed q3 publication artifacts drifted")
    if args.guards:
        certificate = json.loads(CERTIFICATE.read_text())
        if certificate["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] is not False:
            raise AssertionError("retained ell3 was overclaimed")
        if certificate["flags"]["QUANTUM_CLAIM"] is not False:
            raise AssertionError("quantum result was overclaimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
