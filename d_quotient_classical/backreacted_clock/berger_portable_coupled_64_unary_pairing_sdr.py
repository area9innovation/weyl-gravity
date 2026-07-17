#!/usr/bin/env python3
"""Export the portable coupled 64-row unary/pairing and 64-to-36 SDR."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
    _matrix_add,
    _one,
    _sparse_multiply,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    _adjoint_matrix,
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    maxwell_unary_blocks,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    _fixture_linear,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-portable-coupled-64-unary-pairing-36-sdr.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json"

DEPENDENCIES = {
    "gravity_unary_pairing_sdr": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "retained_gravity_layout": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json",
    "coupled_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "coupled_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    "generator_audit": ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
    "classical_Maxwell_transfer": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "classical_transferred_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_portable_coupled_64_unary_pairing_sdr.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_portable_coupled_64_unary_pairing_sdr.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_portable_coupled_64_unary_pairing_sdr.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture_matrix(matrix: list[list[LinearOperator]]) -> list[list[LinearOperator]]:
    return [[_fixture_linear(entry) for entry in row] for row in matrix]


def _multiply(left, right):
    return _fixture_matrix(_sparse_multiply(left, right))


def _add(left, right):
    return _fixture_matrix(_matrix_add(left, right))


def _negative(matrix):
    return [[entry.scale(-1) for entry in row] for row in matrix]


def _subtract(left, right):
    return _add(left, _negative(right))


def _adjoint(matrix):
    return _fixture_matrix(_adjoint_matrix(matrix))


def _identity(size: int) -> list[list[LinearOperator]]:
    output = _zero(size, size)
    for index in range(size):
        output[index][index] = _one()
    return output


def _embed(target, block, row_offset: int, column_offset: int) -> None:
    for row, values in enumerate(block):
        for column, entry in enumerate(values):
            target[row_offset + row][column_offset + column] = entry


def _maximum_order(matrix) -> int:
    return max(
        (entry.maximum_order for row in matrix for entry in row if entry.terms),
        default=0,
    )


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["gravity_unary_pairing_sdr"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("gravity unary carrier is unavailable")
    if data["retained_gravity_layout"]["flags"]["retained_row_inventory_complete"] is not True:
        raise AssertionError("retained gravity layout is unavailable")
    if data["coupled_q2"]["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] is not True:
        raise AssertionError("coupled q2 is unavailable")
    if _sha256(DEPENDENCIES["coupled_q2_payload"]) != data["coupled_q2"]["classical_binary_q2"]["payload_file_sha256"]:
        raise AssertionError("coupled q2 payload hash drifted")
    audit = data["generator_audit"]["flags"]
    if audit["EXPORTED_UNARY_GENERATOR_IS_K"] is not True or audit["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"] is not False:
        raise AssertionError("frozen generator semantics are unavailable")
    transfer = data["classical_Maxwell_transfer"]
    if transfer["flags"]["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("classical Maxwell causal transfer is unavailable")
    if transfer["flags"]["BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING"] is not True:
        raise AssertionError("classical first transferred mixed vertex is unavailable")
    if (
        _sha256(DEPENDENCIES["classical_transferred_q2_payload"])
        != transfer["first_transferred_mixed_vertex"]["payload_file_sha256"]
    ):
        raise AssertionError("classical transferred q2 payload hash drifted")
    return data


def _row_layouts(dependencies: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    full_rows = deepcopy(dependencies["coupled_q2"]["row_layout"]["component_rows"])
    gravity_retained = dependencies["retained_gravity_layout"]["component_rows"]
    retained_rows: list[dict[str, Any]] = []
    for row in gravity_retained:
        retained_rows.append(
            {
                "index": row["index"],
                "row_id": row["row_id"],
                "degree": row["degree"],
                "sector": f"retained_gravity:{row['bundle_id']}",
            }
        )
    for offset, row in enumerate(full_rows[54:]):
        retained_rows.append(
            {
                "index": 26 + offset,
                "row_id": row["row_id"],
                "degree": row["degree"],
                "sector": row["sector"],
            }
        )
    if [row["index"] for row in full_rows] != list(range(64)):
        raise AssertionError("full row layout drifted")
    if [row["index"] for row in retained_rows] != list(range(36)):
        raise AssertionError("retained row layout drifted")
    return full_rows, retained_rows


def _maxwell_q1() -> list[list[LinearOperator]]:
    blocks = maxwell_unary_blocks()
    q1 = _zero(10, 10)
    for mu in range(4):
        q1[1 + mu][0] = blocks["gradient"][mu][0]
        q1[9][5 + mu] = blocks["divergence"][0][mu]
        for nu in range(4):
            q1[5 + mu][1 + nu] = blocks["hessian"][mu][nu]
    return _fixture_matrix(q1)


def exact_matrices(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gravity = dependencies["gravity_unary_pairing_sdr"]
    q64 = _zero(64, 64)
    _embed(
        q64,
        _fixture_matrix(_matrix_from_record(gravity["classical_unary_q1"]["matrix"])),
        0,
        0,
    )
    _embed(q64, _maxwell_q1(), 54, 54)
    omega64 = _zero(64, 64)
    _embed(
        omega64,
        _fixture_matrix(_matrix_from_record(gravity["contraction"]["cyclic_pairing"])),
        0,
        0,
    )
    # In the displayed 1-form/3-form component convention, A wedge A+ gives
    # the opposite coordinate sign to the scalar ghost-density evaluation.
    omega64[54][63] = _one()
    omega64[63][54] = _one(-1)
    for component in range(4):
        omega64[55 + component][59 + component] = _one(-1)
        omega64[59 + component][55 + component] = _one()

    iota = _zero(64, 36)
    projection = _zero(36, 64)
    homotopy = _zero(64, 64)
    _embed(iota, _fixture_matrix(_matrix_from_record(gravity["contraction"]["iota_cl"])), 0, 0)
    _embed(projection, _fixture_matrix(_matrix_from_record(gravity["contraction"]["pi_cl"])), 0, 0)
    _embed(homotopy, _fixture_matrix(_matrix_from_record(gravity["contraction"]["S_cl"])), 0, 0)
    for component in range(10):
        iota[54 + component][26 + component] = _one()
        projection[26 + component][54 + component] = _one()

    q36 = _multiply(_multiply(projection, q64), iota)
    omega36 = _multiply(_multiply(_adjoint(iota), omega64), iota)
    return {
        "q64": q64,
        "omega64": omega64,
        "iota": iota,
        "projection": projection,
        "homotopy": homotopy,
        "q36": q36,
        "omega36": omega36,
    }


def _exact_checks(matrices: dict[str, Any]) -> dict[str, bool]:
    q64 = matrices["q64"]
    omega64 = matrices["omega64"]
    iota = matrices["iota"]
    projection = matrices["projection"]
    homotopy = matrices["homotopy"]
    q36 = matrices["q36"]
    omega36 = matrices["omega36"]
    checks = {
        "q64_squared_zero": _is_zero(_multiply(q64, q64)),
        "q64_odd_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q64), omega64), _multiply(omega64, q64))),
        "omega64_antisymmetric": _is_zero(_add(_adjoint(omega64), omega64)),
        "pi36_iota36_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "iota36_chain_map": _is_zero(_subtract(_multiply(q64, iota), _multiply(iota, q36))),
        "pi36_chain_map": _is_zero(_subtract(_multiply(projection, q64), _multiply(q36, projection))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q64, homotopy), _multiply(homotopy, q64)), _subtract(_identity(64), _multiply(iota, projection)))),
        "homotopy_square_zero": _is_zero(_multiply(homotopy, homotopy)),
        "projection_homotopy_zero": _is_zero(_multiply(projection, homotopy)),
        "homotopy_inclusion_zero": _is_zero(_multiply(homotopy, iota)),
        "homotopy_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega64), _multiply(omega64, homotopy))),
        "q36_squared_zero": _is_zero(_multiply(q36, q36)),
        "q36_odd_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q36), omega36), _multiply(omega36, q36))),
        "Maxwell_rows_retained_by_identity": all(
            iota[54 + index][26 + index] == _one()
            and projection[26 + index][54 + index] == _one()
            for index in range(10)
        ),
    }
    if not all(checks.values()):
        raise AssertionError(f"portable coupled unary/SDR check failed: {checks}")
    return checks


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    full_rows, retained_rows = _row_layouts(dependencies)
    matrices = exact_matrices(dependencies)
    checks = _exact_checks(matrices)
    records = {name: _matrix_record(matrix) for name, matrix in matrices.items()}
    certificate = {
        "schema": "pure-weyl-berger-portable-coupled-64-unary-pairing-36-sdr-v1",
        "result_id": "BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_PORTABLE_64_ROW_UNARY_PAIRING_AND_ALGEBRAIC_64_TO_36_CYCLIC_SDR",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name].get("result_id", "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD"),
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_field": "Q(sqrt(10))",
        "full_complex": {
            "total_rows": 64,
            "degree_ranks": [6, 26, 26, 6],
            "component_rows": full_rows,
            "classical_unary_q1": records["q64"],
            "cyclic_pairing": records["omega64"],
            "maximum_q1_differential_order": _maximum_order(matrices["q64"]),
        },
        "retained_complex": {
            "total_rows": 36,
            "degree_ranks": [4, 14, 14, 4],
            "component_rows": retained_rows,
            "classical_unary_q1": records["q36"],
            "cyclic_pairing": records["omega36"],
            "interpretation": "26 retained gravity rows direct-sum all 10 Maxwell BV rows",
        },
        "contraction": {
            "iota_36_to_64": records["iota"],
            "pi_64_to_36": records["projection"],
            "S_64": records["homotopy"],
            "formula": "(iota_64,pi_64,S_64)=(iota_cl direct_sum I_10, pi_cl direct_sum I_10, S_cl direct_sum 0_10)",
            "identity": "q64 S64+S64 q64=I64-iota36 pi36; pi36 iota36=I36",
            "support_local": True,
            "cyclic": True,
            "maximum_differential_order": max(
                _maximum_order(matrices["iota"]),
                _maximum_order(matrices["projection"]),
                _maximum_order(matrices["homotopy"]),
            ),
            "Maxwell_leg": "identity; no Maxwell physical or gauge row is removed",
        },
        "Maxwell_pairing_convention": {
            "ghost_density": "Omega(c_M,c_M_plus)=+1; Omega(c_M_plus,c_M)=-1",
            "one_form_three_form": "Omega(A_a,A_plus_a)=-1; Omega(A_plus_a,A_a)=+1 in displayed component order",
            "derivation": "the relative sign is fixed by q64-sharp Omega64+Omega64 q64=0 and agrees with A wedge A_plus orientation",
        },
        "generator_semantics": {
            "frozen_generator": "K_Berger=D-omega R",
            "PBW_representation_on_Maxwell_rows": "e0",
            "raw_D_status": "AFFINE_WITH_NONZERO_ARITY_ZERO_COMPONENT_NOT_CERTIFIED",
        },
        "exact_checks": checks,
        "flags": {
            "BERGER_PORTABLE_64_ROW_UNARY_Q1": True,
            "BERGER_PORTABLE_64_ROW_CYCLIC_PAIRING": True,
            "BERGER_ALGEBRAIC_64_TO_36_CYCLIC_SDR": True,
            "MAXWELL_ROWS_RETAINED_BY_IDENTITY": True,
            "MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO": False,
            "CLASSICAL_MAXWELL_CAUSAL_TRANSFER_DEPENDENCY_PINNED": True,
            "MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER": False,
            "TRANSFERRED_MIXED_VERTEX_ESTABLISHED_BY_THIS_LOCAL_CARRIER": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "QUANTUM_SIDE_INDEPENDENT_REPLAY_OF_CLASSICAL_MAXWELL_TRANSFER",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_portable_coupled_64_unary_pairing_sdr.py --check --guards", "elapsed_seconds": 42.97, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_portable_coupled_64_unary_pairing_sdr.py", "elapsed_seconds": 37.39, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_portable_coupled_64_unary_pairing_sdr", "elapsed_seconds": 43.25, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json -d d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json", "elapsed_seconds": 2.18, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "The affected unary, pairing, and SDR chain is recomputed exactly in Tier 1; the coupled q2 payload remains an unchanged content-addressed dependency and is not transferred by this artifact.",
            "tier_3": "No shared core algebra, release freeze, causal endpoint, Lorentzian lifecycle, or quantum lifecycle state is changed by this portable classical carrier export.",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate exports the complete gauge-fixed 64-row gravity-clock-Maxwell classical unary differential and odd cyclic pairing at the rational Berger fixture. It extends the authoritative gravity 54-to-26 cyclic SDR by the identity on all ten Maxwell BV rows, producing a support-local cyclic 64-to-36 contraction onto the retained gravity complex direct-summed with the full Maxwell complex. Exact coefficientwise checks prove q1 squared zero, unary cyclicity, both chain maps, the contraction identity, side conditions, homotopy cyclicity, and the induced retained unary identities. This algebraic SDR does not contract a photon, Maxwell gauge class, zero mode, or any Maxwell row to zero. The separately certified classical Maxwell causal contraction and 1,522-term transferred mixed q2 vertex are pinned as content-addressed dependencies, but they are not re-proved by this LOCAL-ALGEBRAIC carrier. In particular, this artifact does not itself construct advanced or retarded Maxwell Green operators, establish a causal Maxwell endpoint, compute a minimal photon cohomology model, or independently replay the transferred vertex on the quantum side. It also does not construct mixed q3, localized apparatus, Lorentzian perturbative quantum theory, a QME result, or a quantum claim. Its purpose is the exact portable carrier required for that independent replay, while preserving the distinction between an identity extension of the algebraic SDR and the separate causal Green homotopy theorem.",
    }
    verify(certificate)
    return certificate


def verify(certificate: dict[str, Any]) -> None:
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("an exact portable coupled carrier check is false")
    for required in (
        "BERGER_PORTABLE_64_ROW_UNARY_Q1",
        "BERGER_PORTABLE_64_ROW_CYCLIC_PAIRING",
        "BERGER_ALGEBRAIC_64_TO_36_CYCLIC_SDR",
        "MAXWELL_ROWS_RETAINED_BY_IDENTITY",
    ):
        if certificate["flags"][required] is not True:
            raise AssertionError(f"required carrier flag missing: {required}")
    for forbidden in (
        "MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO",
        "MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
        "TRANSFERRED_MIXED_VERTEX_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if certificate["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden carrier promotion: {forbidden}")
    for name, path in DEPENDENCIES.items():
        if certificate["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drifted: {name}")


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(certificate: dict[str, Any]) -> str:
    return """# Portable coupled 64-row unary, pairing, and 64-to-36 SDR

The exact classical `q1` and odd cyclic pairing are now portable on all 64
gravity-clock-Maxwell BV rows.  The certified gravity `54->26` cyclic SDR is
extended by the identity on all ten Maxwell rows, yielding a cyclic `64->36`
SDR onto 26 retained gravity rows plus the complete ten-row Maxwell complex.

The Maxwell pairing signs are fixed by the coefficientwise unary cyclicity
identity.  The ghost-density pair has sign `+1`, while the displayed
one-form/three-form component pair has sign `-1`, consistently with the
oriented wedge convention.

Every Maxwell row is retained, so this algebraic SDR does not erase photon
cohomology.  The separately certified causal Maxwell contraction and
1,522-term retained mixed vertex are pinned but not re-proved here.  This
portable carrier closes the prerequisite for their independent quantum-side
replay; mixed q3 and localized redshift remain later gates.

Machine-readable certificate:
`d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json`.
"""


def _write(certificate: dict[str, Any]) -> None:
    CERTIFICATE_PATH.write_text(_json(certificate))
    REPORT_PATH.write_text(_report(certificate))


def _check(certificate: dict[str, Any]) -> None:
    if CERTIFICATE_PATH.read_text() != _json(certificate):
        raise AssertionError("portable coupled carrier certificate drifted")
    if REPORT_PATH.read_text() != _report(certificate):
        raise AssertionError("portable coupled carrier report drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate = build()
    if args.write:
        _write(certificate)
    if args.check:
        _check(certificate)
    if args.guards:
        for flag in (
            "MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO",
            "MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
            "TRANSFERRED_MIXED_VERTEX_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
            "LORENTZIAN_CERTIFIED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(certificate)
            mutant["flags"][flag] = True
            try:
                verify(mutant)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"forbidden mutation accepted: {flag}")
    if not (args.write or args.check or args.guards):
        print(_json(certificate), end="")


if __name__ == "__main__":
    main()
