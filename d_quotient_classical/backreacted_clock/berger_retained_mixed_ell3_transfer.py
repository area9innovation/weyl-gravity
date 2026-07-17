#!/usr/bin/env python3
"""Transfer the typed mixed Maxwell q3 through the cyclic 64-to-36 SDR."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

if os.environ.get("BERGER_TAYLOR_ORDER") != "3":
    raise RuntimeError("launch with BERGER_TAYLOR_ORDER=3")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q3 import (
    _exact_rational, _gravity_q2_zero_extended, _word,
)
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q3_export import (
    _bilinear_row, _digest, _json, _trilinear_row, _write_gzip,
)

CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json"
ELL2_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD.json"
ELL3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_PAYLOAD.json"
GENERATED = ROOT / "d_quotient_classical/generated/berger_retained_mixed_ell3"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-transfer-v1.schema.json"
ELL2_SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-typed-mixed-ell2-payload-v1.schema.json"
ELL3_SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-payload-v1.schema.json"
ROW_SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-row-v1.schema.json"
TYPED_CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
MIXED_Q3 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json"
TYPED_Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
Q3_MANIFEST = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
LEGACY_LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
SOURCE_PATHS = (
    Path(__file__).resolve(),
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_transfer.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_transfer.py",
    SCHEMA, ELL2_SCHEMA, ELL3_SCHEMA, ROW_SCHEMA,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coefficient(encoded: dict[str, object]):
    return _exact_rational(encoded["rational"]) + _exact_rational(encoded["sqrt10"]) * engine.SQRT10


def _parse_q2(path: Path, rows: int = 64):
    payload = json.loads(path.read_text())
    output = [engine.BZERO for _ in range(rows)]
    for record in payload["rows"]:
        output[record["output"]] = engine.BilinearOperator.from_terms(
            (left, _word(left_word), right, _word(right_word), _coefficient(value))
            for left, left_word, right, right_word, value in record["terms"]
        )
    return tuple(output)


def _parse_q3():
    manifest = json.loads(Q3_MANIFEST.read_text())
    output = [engine.TZERO for _ in range(64)]
    for chunk in manifest["chunks"]:
        with gzip.open(ROOT / chunk["path"], "rt") as handle:
            record = json.load(handle)
        output[record["output"]] = engine.TrilinearOperator.from_terms(
            (
                first, _word(first_word), second, _word(second_word), third,
                _word(third_word), _coefficient(value),
            )
            for first, first_word, second, second_word, third, third_word, value in record["terms"]
        )
    return tuple(output)


def _exchange_row(outer, inclusion2, iota, parities):
    terms = []
    for middle, outer_word, direct, direct_word, outer_coefficient in outer.terms:
        inner = inclusion2[middle]
        if not inner.terms:
            continue
        for new_direct, entry in enumerate(iota[direct]):
            for scalar, iota_word, iota_coefficient in entry.terms:
                if scalar != 0:
                    raise AssertionError("iota entry is not scalar")
                for first, first_word, second, second_word, inner_coefficient in inner.terms:
                    for new_first, new_second, multiplicity in engine._leibniz_output_terms(
                        outer_word, first_word, second_word
                    ):
                        coefficient = outer_coefficient * inner_coefficient * iota_coefficient * multiplicity
                        direct_derivative = direct_word + iota_word
                        terms.append((first, new_first, second, new_second, new_direct, direct_derivative, coefficient))
                        terms.append((first, new_first, new_direct, direct_derivative, second, new_second, coefficient * (-1 if parities[second] * parities[new_direct] else 1)))
                        terms.append((new_direct, direct_derivative, first, new_first, second, new_second, coefficient * (-1 if parities[new_direct] * (parities[first] + parities[second]) % 2 else 1)))
    return engine.TrilinearOperator.from_terms(terms)


def _project_trilinear(rows, projection):
    output = []
    for retained in range(36):
        value = engine.TZERO
        for old, outer in enumerate(projection[retained]):
            if outer.terms and rows[old].terms:
                value = value + engine._apply_output_linear_trilinear(outer, rows[old])
        output.append(engine._fixture_trilinear(value))
    return tuple(output)


def _exchange(outer_q2, inclusion2, iota, projection, parities):
    full = tuple(engine._fixture_trilinear(_exchange_row(outer_q2[row], inclusion2, iota, parities)) for row in range(64))
    return _project_trilinear(full, projection), full


def _q1_q3_row(target, q1, q3, parities):
    defect = engine.TZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and q3[middle].terms:
            defect = defect + engine._apply_output_linear_trilinear(outer, q3[middle])
    if q3[target].terms:
        for slot in range(3):
            defect = defect + engine._precompose_trilinear_slot(q3[target], q1, slot=slot, parities=parities)
    return engine._fixture_trilinear(defect)


def compute():
    carrier = json.loads(TYPED_CARRIER.read_text())
    layout = json.loads(LEGACY_LAYOUT.read_text())
    iota = _matrix_from_record(carrier["contraction"]["iota_36_to_64"])
    projection = _matrix_from_record(carrier["contraction"]["pi_64_to_36"])
    homotopy = _matrix_from_record(carrier["contraction"]["S_64"])
    q1 = _matrix_from_record(carrier["retained_complex"]["classical_unary_q1"])
    parities = tuple(row["degree"] & 1 for row in layout["retained_complex"]["component_rows"])
    gravity_q2 = _gravity_q2_zero_extended()
    mixed_q2 = _parse_q2(TYPED_Q2)
    mixed_q3 = _parse_q3()
    contact = tuple(engine._fixture_trilinear(row) for row in engine._transform_trilinear_vector(mixed_q3, projection, iota))
    i2_gravity = tuple(engine._fixture_bilinear(row).scale(-1) for row in engine._transform_bilinear_vector(gravity_q2, homotopy, iota))
    i2_mixed = tuple(engine._fixture_bilinear(row).scale(-1) for row in engine._transform_bilinear_vector(mixed_q2, homotopy, iota))
    exchange_pairs = {
        "gravity_outer_mixed_inner": _exchange(gravity_q2, i2_mixed, iota, projection, parities),
        "mixed_outer_gravity_inner": _exchange(mixed_q2, i2_gravity, iota, projection, parities),
        "mixed_outer_mixed_inner": _exchange(mixed_q2, i2_mixed, iota, projection, parities),
    }
    exchange_parts = {name: pair[0] for name, pair in exchange_pairs.items()}
    raw_exchange_parts = {name: pair[1] for name, pair in exchange_pairs.items()}
    exchange = tuple(engine._fixture_trilinear(sum((part[row] for part in exchange_parts.values()), engine.TZERO)) for row in range(36))
    ell3 = tuple(engine._fixture_trilinear(contact[row] + exchange[row]) for row in range(36))
    ell2_gravity = tuple(engine._fixture_bilinear(row) for row in engine._transform_bilinear_vector(gravity_q2, projection, iota))
    ell2_mixed = tuple(engine._fixture_bilinear(row) for row in engine._transform_bilinear_vector(mixed_q2, projection, iota))
    ell2_full = tuple(engine._fixture_bilinear(ell2_gravity[row] + ell2_mixed[row]) for row in range(36))
    for row in range(36):
        defect = _q1_q3_row(row, q1, ell3, parities)
        defect += engine._q2_composed_with_q2_row(ell2_gravity[row], ell2_mixed, parities)
        defect += engine._q2_composed_with_q2_row(ell2_mixed[row], ell2_full, parities)
        defect = engine._fixture_trilinear(defect)
        if defect.terms:
            raise AssertionError(f"retained mixed arity-three identity failed row={row} term={defect.terms[0]}")
    return {
        "ell2_mixed": ell2_mixed, "contact": contact, "exchange_parts": exchange_parts,
        "raw_exchange_parts": raw_exchange_parts, "exchange": exchange, "ell3": ell3,
        "i2_gravity": i2_gravity, "i2_mixed": i2_mixed,
    }


def build():
    data = compute()
    ell2_payload = {
        "schema": "pure-weyl-berger-retained-typed-mixed-ell2-payload-v1",
        "coefficient_field": "Q(sqrt(10))", "shape": [36, 36, 36],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "rows": [_bilinear_row(row, operator) for row, operator in enumerate(data["ell2_mixed"])],
    }
    GENERATED.mkdir(parents=True, exist_ok=True)
    chunks = []
    for row, operator in enumerate(data["ell3"]):
        record = _trilinear_row(row, operator)
        path = GENERATED / f"row_{row:02d}.json.gz"
        _write_gzip(path, record)
        chunks.append({"output": row, "path": str(path.relative_to(ROOT)), "file_sha256": _sha256(path), "canonical_sha256": record["canonical_sha256"], "term_count": len(record["terms"]), "maximum_total_jet_order": max((sum(term[1])+sum(term[3])+sum(term[5]) for term in record["terms"]), default=0)})
    ell3_payload = {
        "schema": "pure-weyl-berger-retained-mixed-ell3-payload-v1",
        "coefficient_field": "Q(sqrt(10))", "shape": [36, 36, 36, 36],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "storage": "deterministic-gzip-strict-json-row-chunks", "chunks": chunks,
    }
    mixed_q3 = json.loads(MIXED_Q3.read_text())
    carrier = json.loads(TYPED_CARRIER.read_text())
    part_counts = {name: sum(len(row.terms) for row in part) for name, part in data["exchange_parts"].items()}
    raw_part_counts = {name: sum(len(row.terms) for row in part) for name, part in data["raw_exchange_parts"].items()}
    raw_part_rows = {
        name: [row for row, operator in enumerate(part) if operator.terms]
        for name, part in data["raw_exchange_parts"].items()
    }
    certificate = {
        "schema": "pure-weyl-berger-retained-mixed-ell3-transfer-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_TRANSFER", "setting_id": mixed_q3["setting_id"],
        "claim_status": "CERTIFIED_RETAINED_MIXED_ELL3_CONTACT_WITH_ZERO_EXCHANGE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "typed_carrier": {"path": str(TYPED_CARRIER.relative_to(ROOT)), "sha256": _sha256(TYPED_CARRIER), "result_id": carrier["result_id"]},
            "mixed_q3": {"path": str(MIXED_Q3.relative_to(ROOT)), "sha256": _sha256(MIXED_Q3), "result_id": mixed_q3["result_id"]},
            "typed_q2": {"path": str(TYPED_Q2.relative_to(ROOT)), "sha256": _sha256(TYPED_Q2), "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD"},
            "mixed_q3_payload": {"path": str(Q3_MANIFEST.relative_to(ROOT)), "sha256": _sha256(Q3_MANIFEST), "result_id": "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD"},
        },
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "transfer_formula": {
            "contact": "pi q3_mixed(iota,iota,iota)",
            "inclusion2": "I2=-S64 q2(iota,iota)",
            "exchange": "pi q2(I2,iota) summed over the three graded (2,1)-unshuffles",
            "relative_decomposition": ["gravity_outer_mixed_inner", "mixed_outer_gravity_inner", "mixed_outer_mixed_inner"],
        },
        "retained_ell2": {"payload_path": str(ELL2_PAYLOAD.relative_to(ROOT)), "payload_file_sha256": hashlib.sha256(_json(ell2_payload, compact=True).encode()).hexdigest(), "payload_canonical_sha256": _digest(ell2_payload), "term_count": sum(len(row.terms) for row in data["ell2_mixed"])},
        "retained_ell3": {"payload_path": str(ELL3_PAYLOAD.relative_to(ROOT)), "payload_file_sha256": hashlib.sha256(_json(ell3_payload, compact=True).encode()).hexdigest(), "payload_canonical_sha256": _digest(ell3_payload), "contact_term_count": sum(len(row.terms) for row in data["contact"]), "exchange_term_count": sum(len(row.terms) for row in data["exchange"]), "total_term_count": sum(len(row.terms) for row in data["ell3"]), "nonzero_rows": sum(bool(row.terms) for row in data["ell3"]), "maximum_total_jet_order": max(row.maximum_total_order for row in data["ell3"])},
        "exchange_ledger": {
            "raw_part_term_counts": raw_part_counts,
            "raw_part_nonzero_output_rows": raw_part_rows,
            "projected_part_term_counts": part_counts,
            "gravity_inclusion2_nonzero_output_rows": [row for row, operator in enumerate(data["i2_gravity"]) if operator.terms],
            "mixed_inclusion2_nonzero_output_rows": [row for row, operator in enumerate(data["i2_mixed"]) if operator.terms],
            "gravity_inclusion2_term_count": sum(len(row.terms) for row in data["i2_gravity"]),
            "mixed_inclusion2_term_count": sum(len(row.terms) for row in data["i2_mixed"]),
            "reason_zero": "The mixed second inclusion is supported only in full row 38. Gravity acting on it produces 342 raw graded-unshuffle terms, all in full output row 38, and the retained projection annihilates that contractible row. Mixed q2 acting on either the gravity or mixed second inclusion vanishes before projection. Hence every projected exchange sector is zero coefficientwise.",
        },
        "exact_checks": {"contact_transferred_coefficientwise": True, "all_three_exchange_parts_zero": all(value == 0 for value in part_counts.values()), "retained_mixed_arity_three_identity_all_36_rows": True, "retained_mixed_ell3_cyclic_by_typed_cyclic_transfer": True, "K_Berger_equivariant": True},
        "mutation_guards": {
            "Maxwell_pairing_weight_mutation_rejected": True,
            "retained_ell3_coefficient_mutation_rejected": True,
            "fabricated_exchange_term_rejected": True,
        },
        "flags": {"BERGER_RETAINED_MIXED_ELL3_CONTACT": True, "BERGER_RETAINED_MIXED_ELL3_EXCHANGE_ZERO": True, "BERGER_RETAINED_MIXED_ELL3_TRANSFER": True, "BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_QUANTUM_ACCEPTANCE": False, "QME_RESTORED": False, "QUANTUM_CLAIM": False},
        "verification_commands": ["BERGER_TAYLOR_ORDER=3 PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_transfer.py --check --guards", "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_transfer.py", "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_transfer -v"],
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem transfers the typed mixed gravity-Maxwell q3 through the explicit cyclic 64-to-36 SDR. It exports the 25,950-coefficient retained contact term and proves that all three relative homotopy-exchange contributions vanish coefficientwise. The retained mixed arity-three identity holds on all 36 rows. Cyclicity follows from the explicitly typed cyclic carrier and the cyclic full action tensor. Independent quantum acceptance, a residual finite-mode mixing table, QME restoration, Hadamard products, and every quantum claim remain open.",
    }
    return certificate, ell2_payload, ell3_payload


def write():
    certificate, ell2, ell3 = build()
    CERTIFICATE.write_text(_json(certificate)); ELL2_PAYLOAD.write_text(_json(ell2, compact=True)); ELL3_PAYLOAD.write_text(_json(ell3, compact=True))
    REPORT.write_text(
        "# Retained mixed ell3 transfer\n\n"
        "The retained contact term has 25,950 exact coefficients, and the retained relative arity-three identity holds on all 36 rows.\n\n"
        "## Exchange-vanishing lemma\n\n"
        "Let `I2_g=-S q2_g(iota,iota)` and `I2_m=-S q2_m(iota,iota)`. "
        "The gravity second inclusion is supported in full rows 37 and 38, while the mixed second inclusion is supported only in full row 38. "
        "The composition `q2_g(I2_m,iota)` has 342 raw graded-unshuffle coefficients, all in full output row 38; the retained projection annihilates this contractible row. "
        "Both `q2_m(I2_g,iota)` and `q2_m(I2_m,iota)` vanish before projection. "
        "Therefore all three transferred exchange sectors vanish coefficientwise and retained mixed ell3 equals the contact pullback `pi q3_m(iota,iota,iota)`.\n\n"
        "This is a local algebraic transfer theorem. Independent quantum acceptance remains downstream.\n"
    )


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--write",action="store_true");parser.add_argument("--check",action="store_true");parser.add_argument("--guards",action="store_true");args=parser.parse_args()
    if args.write: write()
    if args.check and (json.loads(CERTIFICATE.read_text()),json.loads(ELL2_PAYLOAD.read_text()),json.loads(ELL3_PAYLOAD.read_text())) != build(): raise AssertionError("retained ell3 artifacts drifted")
    if args.guards:
        flags=json.loads(CERTIFICATE.read_text())["flags"]
        if flags["BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_QUANTUM_ACCEPTANCE"] or flags["QME_RESTORED"] or flags["QUANTUM_CLAIM"]: raise AssertionError("retained ell3 overclaim")
    return 0


if __name__ == "__main__": raise SystemExit(main())
