#!/usr/bin/env python3
"""Construct the exact cyclic rank-46 STF2 graph carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
    _one,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_portable_coupled_64_unary_pairing_sdr import (
    _add,
    _adjoint,
    _identity,
    _multiply,
    _negative,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    _fixture_linear,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-46-stf2-prolongation-branch-carrier.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_retained_46_stf2_prolongation_branch_carrier"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-prolongation-branch-carrier-v1.schema.json"
VERIFIER_PATH = HERE / "verify_berger_retained_46_stf2_prolongation_branch_carrier.py"
TEST_PATH = HERE / "tests/test_berger_retained_46_stf2_prolongation_branch_carrier.py"

TYPED_36 = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
LEGACY_36 = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
WAVE_PATH = ROOT / "d_quotient_classical/generated/berger_metric_lower_by_two_biwave/rough_tensor_wave.json"
OBSTRUCTION = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"

ARTIFACT_PATHS = {
    "q1_46": GENERATED_DIR / "q1_46.json",
    "omega_46": GENERATED_DIR / "omega_46.json",
    "iota_36_to_46": GENERATED_DIR / "iota_36_to_46.json",
    "pi_46_to_36": GENERATED_DIR / "pi_46_to_36.json",
    "S_46": GENERATED_DIR / "S_46.json",
    "stf2_extractor_T": GENERATED_DIR / "stf2_extractor_T.json",
    "stf2_right_inverse_J": GENERATED_DIR / "stf2_right_inverse_J.json",
    "stf2_wave_F": GENERATED_DIR / "stf2_wave_F.json",
}

AUX_FIELD_IDS = (
    "Y_stf_12",
    "Y_stf_13",
    "Y_stf_23",
    "Y_stf_11_minus_22",
    "Y_stf_11_plus_22_minus_2_33",
)
AUX_DUAL_IDS = tuple(f"{name}_star" for name in AUX_FIELD_IDS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(matrix):
    return [[_fixture_linear(entry) for entry in row] for row in matrix]


def _embed(target, block, rows, columns) -> None:
    for row, target_row in enumerate(rows):
        for column, target_column in enumerate(columns):
            target[target_row][target_column] = block[row][column]


def _maximum_order(matrix) -> int:
    return max(
        (entry.maximum_order for row in matrix for entry in row if entry.terms),
        default=0,
    )


def _nonzero_blocks(matrix) -> int:
    return sum(bool(entry.terms) for row in matrix for entry in row)


def _spatial_stf_maps():
    # Metric order: 00,01,02,03,11,12,13,22,23,33.
    T = _zero(5, 10)
    T[0][5] = _one()
    T[1][6] = _one()
    T[2][8] = _one()
    T[3][4], T[3][7] = _one(), _one(-1)
    T[4][4], T[4][7], T[4][9] = _one(), _one(), _one(-2)

    J = _zero(10, 5)
    J[5][0] = _one()
    J[6][1] = _one()
    J[8][2] = _one()
    J[4][3], J[7][3] = _one(sp.Rational(1, 2)), _one(sp.Rational(-1, 2))
    J[4][4], J[7][4], J[9][4] = (
        _one(sp.Rational(1, 6)),
        _one(sp.Rational(1, 6)),
        _one(sp.Rational(-1, 3)),
    )
    if not _is_zero(_subtract(_multiply(T, J), _identity(5))):
        raise AssertionError("spatial STF2 right inverse failed")
    projector = _multiply(J, T)
    if not _is_zero(_subtract(_multiply(projector, projector), projector)):
        raise AssertionError("spatial STF2 projector is not idempotent")
    return T, J


def _ordered_index(internal: int) -> int:
    if internal <= 12:
        return internal
    if 13 <= internal <= 22:
        return internal + 5
    if 23 <= internal <= 35:
        return internal + 10
    if 36 <= internal <= 40:
        return internal - 23
    if 41 <= internal <= 45:
        return internal - 13
    raise ValueError(internal)


def _permutation():
    P = _zero(46, 46)
    for internal in range(46):
        P[_ordered_index(internal)][internal] = _one()
    return P


def exact_matrices() -> dict:
    typed = json.loads(TYPED_36.read_text())
    q36 = _fixture(_matrix_from_record(typed["retained_complex"]["classical_unary_q1"]))
    omega36 = _fixture(_matrix_from_record(typed["retained_complex"]["typed_cyclic_pairing"]))
    wave = _fixture(_matrix_from_record(json.loads(WAVE_PATH.read_text())))
    T, J = _spatial_stf_maps()
    F = _multiply(T, wave)

    q_direct = _zero(46, 46)
    omega_direct = _zero(46, 46)
    _embed(q_direct, q36, range(36), range(36))
    _embed(omega_direct, omega36, range(36), range(36))
    for index in range(5):
        q_direct[41 + index][36 + index] = _one()
        omega_direct[36 + index][41 + index] = _one()
        omega_direct[41 + index][36 + index] = _one(-1)

    F_adj = _adjoint(F)
    U = _identity(46)
    U_inv = _identity(46)
    _embed(U, F, range(36, 41), range(3, 13))
    _embed(U_inv, _negative(F), range(36, 41), range(3, 13))
    _embed(U, _negative(F_adj), range(13, 23), range(41, 46))
    _embed(U_inv, F_adj, range(13, 23), range(41, 46))
    if not _is_zero(_subtract(_multiply(U, U_inv), _identity(46))):
        raise AssertionError("STF2 cotangent shear inverse failed")
    if not _is_zero(
        _subtract(_multiply(_multiply(_adjoint(U), omega_direct), U), omega_direct)
    ):
        raise AssertionError("STF2 cotangent shear is not cyclic")

    q_internal = _multiply(_multiply(U, q_direct), U_inv)
    i0 = _zero(46, 36)
    p0 = _zero(36, 46)
    for index in range(36):
        i0[index][index] = _one()
        p0[index][index] = _one()
    H0 = _zero(46, 46)
    for index in range(5):
        H0[36 + index][41 + index] = _one()
    i_internal = _multiply(U, i0)
    p_internal = _multiply(p0, U_inv)
    S_internal = _multiply(_multiply(U, H0), U_inv)

    P = _permutation()
    P_inv = _adjoint(P)
    return {
        "q1_46": _multiply(_multiply(P, q_internal), P_inv),
        "omega_46": _multiply(_multiply(P, omega_direct), P_inv),
        "iota_36_to_46": _multiply(P, i_internal),
        "pi_46_to_36": _multiply(p_internal, P_inv),
        "S_46": _multiply(_multiply(P, S_internal), P_inv),
        "stf2_extractor_T": T,
        "stf2_right_inverse_J": J,
        "stf2_wave_F": F,
        "q1_36": q36,
        "omega_36": omega36,
    }


def exact_checks(m: dict) -> dict[str, bool]:
    q, omega = m["q1_46"], m["omega_46"]
    iota, projection, homotopy = (
        m["iota_36_to_46"],
        m["pi_46_to_36"],
        m["S_46"],
    )
    checks = {
        "q1_46_squared_zero": _is_zero(_multiply(q, q)),
        "omega_46_antisymmetric": _is_zero(_add(_adjoint(omega), omega)),
        "q1_46_typed_cyclic": _is_zero(_add(_multiply(_adjoint(q), omega), _multiply(omega, q))),
        "pi_iota_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "iota_chain_map": _is_zero(_subtract(_multiply(q, iota), _multiply(iota, m["q1_36"]))),
        "pi_chain_map": _is_zero(_subtract(_multiply(projection, q), _multiply(m["q1_36"], projection))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q, homotopy), _multiply(homotopy, q)), _subtract(_identity(46), _multiply(iota, projection)))),
        "homotopy_square_zero": _is_zero(_multiply(homotopy, homotopy)),
        "homotopy_iota_zero": _is_zero(_multiply(homotopy, iota)),
        "pi_homotopy_zero": _is_zero(_multiply(projection, homotopy)),
        "homotopy_typed_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega), _multiply(omega, homotopy))),
        "pairing_induced_by_iota": _is_zero(_subtract(_multiply(_multiply(_adjoint(iota), omega), iota), m["omega_36"])),
        "stf2_right_inverse": _is_zero(_subtract(_multiply(m["stf2_extractor_T"], m["stf2_right_inverse_J"]), _identity(5))),
        "stf2_wave_order_two": _maximum_order(m["stf2_wave_F"]) == 2,
    }
    if not all(checks.values()):
        raise AssertionError(f"rank-46 graph carrier checks failed: {checks}")
    return checks


def _component_rows() -> list[dict]:
    legacy = json.loads(LEGACY_36.read_text())
    old = legacy["retained_complex"]["component_rows"]
    rows = []
    for row in old:
        old_index = row["index"]
        internal = old_index
        rows.append({**row, "index": _ordered_index(internal)})
    rows.extend(
        {"index": 13 + index, "row_id": row_id, "degree": 0, "sector": "retained_gravity:STF2_prolongation"}
        for index, row_id in enumerate(AUX_FIELD_IDS)
    )
    rows.extend(
        {"index": 28 + index, "row_id": row_id, "degree": 1, "sector": "retained_gravity:STF2_prolongation_dual"}
        for index, row_id in enumerate(AUX_DUAL_IDS)
    )
    return sorted(rows, key=lambda row: row["index"])


def _canonical_body(record: dict) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


def build() -> tuple[dict, dict[Path, bytes]]:
    obstruction = json.loads(OBSTRUCTION.read_text())
    if obstruction["smallest_carrier_enlargement_required"]["smallest_natural_support_local_candidate"]["candidate_retained_rank"] != 46:
        raise AssertionError("rank-46 authority drifted")
    matrices = exact_matrices()
    checks = exact_checks(matrices)
    artifact_matrices = {name: matrices[name] for name in ARTIFACT_PATHS}
    bodies = {
        ARTIFACT_PATHS[name]: _canonical_body(_matrix_record(matrix))
        for name, matrix in artifact_matrices.items()
    }
    artifacts = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(bodies[path]).hexdigest(),
            "shape": _matrix_record(artifact_matrices[name])["shape"],
            "nonzero_row_pair_blocks": _nonzero_blocks(artifact_matrices[name]),
            "maximum_differential_order": _maximum_order(artifact_matrices[name]),
        }
        for name, path in ARTIFACT_PATHS.items()
    }
    rows = _component_rows()
    payload = {
        "schema": "pure-weyl-berger-retained-46-stf2-prolongation-branch-carrier-v1",
        "result_id": "BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1",
        "result_state": "CERTIFIED_CYCLIC_GRAPH_CARRIER_PROJECTOR_OPEN",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "typed_retained_36": {"path": str(TYPED_36.relative_to(ROOT)), "sha256": _sha256(TYPED_36)},
            "legacy_retained_36_layout": {"path": str(LEGACY_36.relative_to(ROOT)), "sha256": _sha256(LEGACY_36)},
            "rough_tensor_wave": {"path": str(WAVE_PATH.relative_to(ROOT)), "sha256": _sha256(WAVE_PATH)},
            "rank_36_projector_obstruction": {"path": str(OBSTRUCTION.relative_to(ROOT)), "sha256": _sha256(OBSTRUCTION)},
        },
        "carrier": {
            "total_rows": 46,
            "degree_ranks": {"-1": 4, "0": 19, "1": 19, "2": 4},
            "component_rows": rows,
            "added_bundle": "spatial STF2 prolongation variable Y=T_STF Box_2 h plus its cyclic dual",
            "added_configuration_rows": 5,
            "added_cyclic_dual_rows": 5,
            "coefficient_field": "Q(sqrt(10))",
        },
        "graph_construction": {
            "spatial_STF_coordinates": ["h12", "h13", "h23", "h11-h22", "h11+h22-2h33"],
            "constraint": "Y=F h with F=T_STF Box_2",
            "cotangent_shear": "B=[[I10,0],[F,I5]], equation transform=(B^-1)^dagger",
            "extended_metric_Hessian": "[[A10+F^dagger F,-F^dagger],[-F,I5]]",
            "Schur_complement": "A10",
            "inverse_shear_support_local": True,
            "interpretation": "exact cyclic graph prolongation with a contractible STF2 complement; not a branch projector",
        },
        "artifacts": artifacts,
        "exact_checks": checks,
        "diagnostics": {
            "q1_46_nonzero_row_pair_blocks": _nonzero_blocks(matrices["q1_46"]),
            "q1_46_maximum_differential_order": _maximum_order(matrices["q1_46"]),
            "iota_nonzero_row_pair_blocks": _nonzero_blocks(matrices["iota_36_to_46"]),
            "pi_nonzero_row_pair_blocks": _nonzero_blocks(matrices["pi_46_to_36"]),
            "S_nonzero_row_pair_blocks": _nonzero_blocks(matrices["S_46"]),
            "STF2_wave_nonzero_row_pair_blocks": _nonzero_blocks(matrices["stf2_wave_F"]),
        },
        "flags": {
            "BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1": True,
            "CYCLIC_GRAPH_SDR_46_TO_36": True,
            "CANONICAL_BRANCH_PROJECTOR_CERTIFIED": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "Q2_Q3_LIFT_MATERIALIZED": False,
            "K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "LORENTZIAN_CAUSAL": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        "provenance": {
            "producer": str(Path(__file__).resolve().relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__).resolve()),
            "verifier": str(VERIFIER_PATH.relative_to(ROOT)),
            "verifier_sha256": _sha256(VERIFIER_PATH),
            "tests": str(TEST_PATH.relative_to(ROOT)),
            "tests_sha256": _sha256(TEST_PATH),
            "schema": str(SCHEMA_PATH.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA_PATH),
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC certificate constructs the natural rank-46 support-local STF2 graph prolongation and its cyclic dual as a cyclic SDR over the retained 36-row complex. The triangular cotangent shear and its inverse are finite-order local, the added complement is contractible, and the Schur complement is the original A10 endpoint. It therefore supplies an honest enlarged carrier without changing retained cohomology. It does not certify an Einstein-like/extra-Weyl projector, materialize q2 or q3 on rank 46, authorize a branch mixing table, prove K_Berger equivariance or causal support for the enlarged carrier, or make a quantum claim.",
    }
    return payload, bodies


def verify(payload: dict) -> None:
    if payload["carrier"]["total_rows"] != 46:
        raise AssertionError("rank-46 carrier drifted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an exact carrier check failed")
    if payload["flags"]["CANONICAL_BRANCH_PROJECTOR_CERTIFIED"] is not False:
        raise AssertionError("carrier scaffold promoted to a branch projector")
    if payload["flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"] is not False:
        raise AssertionError("branch mixing promoted before a projector")
    if payload["flags"]["Q2_Q3_LIFT_MATERIALIZED"] is not False:
        raise AssertionError("nonlinear lift falsely materialized")


def _report(payload: dict) -> str:
    d = payload["diagnostics"]
    return f"""# Berger retained rank-46 STF2 prolongation carrier

## Exact construction

The natural local enlargement requested by the retained-36 projector
obstruction is now constructed as a cyclic graph carrier.  Five spatial STF2
coordinates

```text
h12, h13, h23, h11-h22, h11+h22-2h33
```

define `T_STF`, and the new prolongation variable obeys

```text
Y = F h,    F = T_STF Box_2.
```

The cotangent shear gives the extended metric Hessian

```text
[[A10 + F^dagger F, -F^dagger], [-F, I5]],
```

whose Schur complement is exactly `A10`.  Adding the five cyclic-dual rows
gives degree ranks `(4,19,19,4)` and total rank 46.

The exact 46-to-36 graph SDR passes nilpotency, unary cyclicity, both chain
maps, contraction, all three side conditions, homotopy cyclicity and induced
pairing checks.  The exported q1 has {d['q1_46_nonzero_row_pair_blocks']}
nonzero row-pair blocks and maximum differential order
{d['q1_46_maximum_differential_order']}.

## Boundary

This is the honest carrier construction, not yet the branch theorem.  The
added STF2 complement is contractible, so no new cohomology or physical branch
has been declared.  A rank-46 Einstein-like/extra-Weyl projector or normalized
obstruction remains the next gate.  The nonlinear q2/q3 lift, K_Berger
equivariance, causal support and branch-space ell3 table remain false.
"""


def _text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload, bodies = build()
    verify(payload)
    if args.write:
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        for path, body in bodies.items():
            path.write_bytes(body)
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _text(payload):
            raise AssertionError("rank-46 certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("rank-46 report drifted")
        for path, body in bodies.items():
            if path.read_bytes() != body:
                raise AssertionError(f"rank-46 artifact drifted: {path}")
    if args.guards:
        for key in ("CANONICAL_BRANCH_PROJECTOR_CERTIFIED", "ELL3_BRANCH_MIXING_AUTHORIZED", "Q2_Q3_LIFT_MATERIALIZED"):
            mutant = deepcopy(payload)
            mutant["flags"][key] = True
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted {key}")
    print("BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1: PASS")


if __name__ == "__main__":
    main()
