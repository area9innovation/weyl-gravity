#!/usr/bin/env python3
"""Export the explicit typed Maxwell pairing on the coupled 64/36 SDR."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_portable_coupled_64_unary_pairing_sdr import (
    _add,
    _adjoint,
    _identity,
    _multiply,
    _one,
    _subtract,
    _zero,
)


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-portable-coupled-64-typed-pairing-36-sdr.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-portable-coupled-64-typed-pairing-36-sdr-v1.schema.json"
LEGACY = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
SOURCE_PATHS = (
    Path(__file__).resolve(),
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_portable_coupled_typed_pairing_sdr.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_portable_coupled_typed_pairing_sdr.py",
    SCHEMA,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scale(size: int, first_maxwell: int):
    output = _zero(size, size)
    for index in range(size):
        output[index][index] = _one(2 if index >= first_maxwell else 1)
    return output


def exact_matrices(legacy: dict):
    full = legacy["full_complex"]
    retained = legacy["retained_complex"]
    contraction = legacy["contraction"]
    q64 = _matrix_from_record(full["classical_unary_q1"])
    old_omega64 = _matrix_from_record(full["cyclic_pairing"])
    q36 = _matrix_from_record(retained["classical_unary_q1"])
    old_omega36 = _matrix_from_record(retained["cyclic_pairing"])
    iota = _matrix_from_record(contraction["iota_36_to_64"])
    projection = _matrix_from_record(contraction["pi_64_to_36"])
    homotopy = _matrix_from_record(contraction["S_64"])
    scale64 = _scale(64, 54)
    scale36 = _scale(36, 26)
    omega64 = _multiply(old_omega64, scale64)
    omega36 = _multiply(old_omega36, scale36)
    return {
        "q64": q64,
        "omega64": omega64,
        "scale64": scale64,
        "q36": q36,
        "omega36": omega36,
        "scale36": scale36,
        "iota": iota,
        "projection": projection,
        "homotopy": homotopy,
    }


def exact_checks(m):
    q64, omega64 = m["q64"], m["omega64"]
    q36, omega36 = m["q36"], m["omega36"]
    iota, projection, homotopy = m["iota"], m["projection"], m["homotopy"]
    checks = {
        "typed_pairing64_antisymmetric": _is_zero(_add(_adjoint(omega64), omega64)),
        "typed_pairing36_antisymmetric": _is_zero(_add(_adjoint(omega36), omega36)),
        "q64_typed_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q64), omega64), _multiply(omega64, q64))),
        "q36_typed_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q36), omega36), _multiply(omega36, q36))),
        "typed_pairing_induced_by_iota": _is_zero(_subtract(_multiply(_multiply(_adjoint(iota), omega64), iota), omega36)),
        "pi_iota_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q64, homotopy), _multiply(homotopy, q64)), _subtract(_identity(64), _multiply(iota, projection)))),
        "homotopy_typed_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega64), _multiply(omega64, homotopy))),
        "scale_intertwines_iota": _is_zero(_subtract(_multiply(m["scale64"], iota), _multiply(iota, m["scale36"]))),
        "scale_intertwines_projection": _is_zero(_subtract(_multiply(projection, m["scale64"]), _multiply(m["scale36"], projection))),
    }
    if not all(checks.values()):
        raise AssertionError(f"typed carrier identity failed: {checks}")
    return checks


def build() -> dict:
    legacy = json.loads(LEGACY.read_text())
    matrices = exact_matrices(legacy)
    checks = exact_checks(matrices)
    records = {name: _matrix_record(value) for name, value in matrices.items()}
    return {
        "schema": "pure-weyl-berger-portable-coupled-64-typed-pairing-36-sdr-v1",
        "result_id": "BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_EXPLICIT_TYPED_64_36_CYCLIC_CARRIER",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "legacy_carrier": {"path": str(LEGACY.relative_to(ROOT)), "sha256": _sha256(LEGACY), "result_id": legacy["result_id"]},
        },
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "normalization": {
            "formula": "S64=diag(I54,2 I10); S36=diag(I26,2 I10); Omega_typed=Omega_legacy S",
            "Maxwell_pairing_weight": 2,
            "gravity_pairing_weight": 1,
            "lowered_q2_tensor_preserved": True,
        },
        "full_complex": {
            "total_rows": 64,
            "classical_unary_q1": records["q64"],
            "typed_cyclic_pairing": records["omega64"],
            "typing_scale": records["scale64"],
        },
        "retained_complex": {
            "total_rows": 36,
            "classical_unary_q1": records["q36"],
            "typed_cyclic_pairing": records["omega36"],
            "typing_scale": records["scale36"],
        },
        "contraction": {
            "iota_36_to_64": records["iota"],
            "pi_64_to_36": records["projection"],
            "S_64": records["homotopy"],
            "support_local": True,
            "cyclic_for_typed_pairing": True,
        },
        "exact_checks": checks,
        "flags": {
            "BERGER_EXPLICIT_TYPED_PAIRING_64": True,
            "BERGER_EXPLICIT_TYPED_PAIRING_36": True,
            "BERGER_TYPED_64_TO_36_CYCLIC_SDR": True,
            "BERGER_RETAINED_MIXED_ELL3_TRANSFER": False,
            "QUANTUM_CLAIM": False,
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_portable_coupled_typed_pairing_sdr.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_portable_coupled_typed_pairing_sdr.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_portable_coupled_typed_pairing_sdr -v",
        ],
        "claim_boundary": "This LOCAL-ALGEBRAIC carrier emits the complete typed 64-row and retained 36-row odd pairings, unary differentials, typing scales, inclusion, projection, and homotopy. It proves coefficientwise unary cyclicity and a cyclic support-local SDR after assigning weight two to every Maxwell Darboux row. It does not transfer ell3, construct new Green operators, establish quantum acceptance, restore a QME, or make a quantum claim.",
    }


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write() -> None:
    value = build()
    CERTIFICATE.write_text(_json(value))
    REPORT.write_text(
        "# Explicit typed coupled 64/36 carrier\n\n"
        "The Maxwell Darboux block now has explicit weight two in both the 64-row and retained 36-row pairings. "
        "The unary differential and 64-to-36 SDR remain coefficientwise cyclic and support local. "
        "No retained ell3 or quantum claim is made.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check and json.loads(CERTIFICATE.read_text()) != build():
        raise AssertionError("typed carrier artifact drifted")
    if args.guards:
        flags = json.loads(CERTIFICATE.read_text())["flags"]
        if flags["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] or flags["QUANTUM_CLAIM"]:
            raise AssertionError("typed carrier overclaim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
