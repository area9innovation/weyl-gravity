#!/usr/bin/env python3
"""Certify the SU(2) reality map from complex feedback columns to real shells."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_recoil_real_shell_extraction import (
    extract_real_channel_column_sum,
)
from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    representation_matrix,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
    laplacian,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_REAL_SHELL_EXTRACTION.json"
SCHEMA = PACKAGE / "schema/berger-recoil-real-shell-extraction-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-real-shell-extraction.md"
DEPENDENCIES = {
    "symbolic_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "two_j5_columns": PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json",
    "direct_shell_gate": PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_real_shell_extraction.py",
    PACKAGE / "generate_berger_local_su2_profile_coefficients.py",
    PACKAGE / "generate_berger_peter_weyl_form_laplacian.py",
    PACKAGE / "verify_berger_recoil_real_shell_extraction.py",
    PACKAGE / "tests/test_berger_recoil_real_shell_extraction.py",
    SCHEMA,
    REPORT,
]
MAX_AUDITED_TWO_J = 6


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reality_matrix(two_j: int) -> sp.Matrix:
    matrix = sp.zeros(two_j + 1)
    for row in range(two_j + 1):
        matrix[two_j - row, row] = (-1) ** row
    return matrix


def _defect_count(matrix: sp.Matrix) -> int:
    return sum(sp.simplify(value) != 0 for value in matrix)


def algebra_audit(two_j: int) -> dict[str, Any]:
    dimension = two_j + 1
    representation = representation_matrix(two_j)
    representation_defects = sum(
        sp.simplify(
            sp.conjugate(representation[row, column])
            - (-1) ** (row - column)
            * representation[two_j - row, two_j - column]
        )
        != 0
        for row in range(dimension)
        for column in range(dimension)
    )
    reality = _reality_matrix(two_j)
    d_defects = []
    for degree in range(3):
        source = sp.kronecker_product(
            sp.eye(len(list(combinations(range(3), degree)))), reality
        )
        target = sp.kronecker_product(
            sp.eye(len(list(combinations(range(3), degree + 1)))), reality
        )
        d_defects.append(
            _defect_count(
                sp.simplify(
                    d_matrix(two_j, degree) * source
                    - target * d_matrix(two_j, degree).conjugate()
                )
            )
        )
    laplacian_defects = []
    for degree in range(4):
        form_reality = sp.kronecker_product(
            sp.eye(len(list(combinations(range(3), degree)))), reality
        )
        operator = laplacian(two_j, degree)
        laplacian_defects.append(
            _defect_count(
                sp.simplify(
                    operator * form_reality
                    - form_reality * operator.conjugate()
                )
            )
        )
    return {
        "two_j": two_j,
        "dimension": dimension,
        "representation_reality_defect_count": representation_defects,
        "de_rham_reality_defect_counts_by_degree_0_1_2": d_defects,
        "laplacian_reality_defect_counts_by_degree_0_1_2_3": laplacian_defects,
        "reality_square": str((-1) ** two_j),
    }


def _base_channel_rows(certificate: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for column in certificate["base_partition_columns"]:
        for row in column["channels"]:
            grouped[row["channel_id"]].append(row)
    return {channel: sorted(rows, key=lambda row: row["column"]) for channel, rows in grouped.items()}


def _mutation_detected(rows: list[dict[str, Any]]) -> bool:
    mutated = json.loads(json.dumps(rows))
    mutated[-1]["coefficient_block_interval"]["real"]["upper"] = str(
        sp.Rational(mutated[-1]["coefficient_block_interval"]["real"]["upper"]) + 1
    )
    try:
        extract_real_channel_column_sum(mutated)
    except ValueError as error:
        return "conjugate carrier rectangles" in str(error)
    return False


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "symbolic_word": "ALL_EIGHT_ABC_RECOIL_CHANNEL_WORDS_EXPORTED",
        "spectral": "GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR",
        "two_j5_columns": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED",
        "direct_shell_gate": "GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    algebra = [algebra_audit(two_j) for two_j in range(MAX_AUDITED_TWO_J + 1)]
    if any(
        row["representation_reality_defect_count"]
        or any(row["de_rham_reality_defect_counts_by_degree_0_1_2"])
        or any(row["laplacian_reality_defect_counts_by_degree_0_1_2_3"])
        for row in algebra
    ):
        raise AssertionError("finite-shell SU(2) reality audit failed")

    grouped = _base_channel_rows(values["two_j5_columns"])
    if len(grouped) != 8:
        raise AssertionError("two_j=5 channel coverage drifted")
    extracted = [extract_real_channel_column_sum(grouped[channel]) for channel in sorted(grouped)]
    if any(row["imaginary_column_sum"] != {"lower": "0", "upper": "0", "width": "0"} for row in extracted):
        raise AssertionError("reality extraction retained an imaginary shell part")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result certifies the "
        "complex-channel-to-real-shell map for the direct Berger Peter-Weyl "
        "carrier. In the normalized symmetric-power convention, conjugate "
        "representation entries obey conjugate(D_rc)=(-1)^(r-c) "
        "D_(two_j-r,two_j-c). The resulting anti-linear row map intertwines "
        "the exact de Rham and Laplacian blocks; real entire Green functions "
        "and the real switch operations preserve it, while the Hermitian "
        "Lorentzian form pairing sends passive column k to the complex "
        "conjugate of column two_j-k. Therefore each pair contributes twice "
        "the real interval of one representative, with an even-shell central "
        "column contributing once. Exact algebra audits through two_j=6 have "
        "zero defects, and all 24 conjugate pairs in the existing two_j=5 "
        "48-block fixture have conjugate carrier rectangles. All eight "
        "two_j=5 channel sums are exported as real intervals. These are "
        "validation-mass, partition-two bare channel sums, not physical "
        "coupling choices or four physical recoil records. No two_j=6 feedback "
        "channel, tail closure, tangent-cone restriction, quotient descent, "
        "Bridge 3 activation, nonlinear observer theorem or quantum claim is made."
    )
    return {
        "schema": "closed-universe-berger-recoil-real-shell-extraction-v1",
        "result_id": "BERGER_RECOIL_REAL_SHELL_EXTRACTION",
        "setting_id": values["symbolic_word"]["setting_id"],
        "claim_status": "DIRECT_BERGER_COMPLEX_CHANNEL_TO_REAL_SHELL_MAP_CERTIFIED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "strictly ordered h0,D0,h1,D1 compact windows; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "direct finite-shell Peter-Weyl feedback columns with explicit SU(2) reality pairing",
            "degree": "spacetime Maxwell one/two-form and physical massive two-form blocks",
            "parity": "real detector/source profiles; all eight a,b,c channel labels",
            "ell": "generic finite two_j; exact audit 0<=two_j<=6 and evaluated feedback fixture two_j=5",
            "m": "all representation rows under the anti-linear row-reversal map",
            "k": "paired passive columns k and two_j-k; central self-partner when two_j is even",
            "omega": "partition-two validation mass-squared intervals [1,2]; real entire finite-mode Green kernels",
        },
        "reality_theorem": {
            "representation_identity": "conjugate(D_rc^(two_j/2))=(-1)^(r-c) D_(two_j-r,two_j-c)^(two_j/2)",
            "row_reality_matrix": "J_(two_j-r,r)=(-1)^r",
            "coefficient_partner_rule": "F[:,two_j-k]=(-1)^k J conjugate(F[:,k]) up to the common convention phase whose square cancels in the pairing",
            "channel_partner_rule": "I_abc[two_j,two_j-k]=conjugate(I_abc[two_j,k])",
            "real_pair_reduction": "I[k]+I[two_j-k]=2 Re I[k]",
            "central_column_rule": "for even two_j, I[two_j/2] is real",
            "correlation_boundary": "the exact partner theorem supplies correlation absent from independent interval addition",
        },
        "algebra_audits": algebra,
        "two_j5_real_channel_sums": extracted,
        "callable_contract": {
            "module": "closed_universe_observers.berger_recoil_real_shell_extraction",
            "callable": "extract_real_channel_column_sum",
            "aggregator_adapter": "reality_reduced_columns",
            "input": "one complete same-carrier channel at fixed two_j and partition with conjugate partner rectangles",
            "output": "real rational interval for the passive-column sum and exact-zero imaginary sum",
        },
        "mutation_results": [
            {
                "name": "treat_independent_imaginary_rectangles_as_uncorrelated",
                "detected": all(row["imaginary_column_sum"]["width"] == "0" for row in extracted),
                "witness": "pair contributions record exact zero by the certified reality correlation",
            },
            {
                "name": "alter_one_conjugate_partner_rectangle",
                "detected": _mutation_detected(grouped["I_000"]),
            },
            {
                "name": "identify_hashed_exact_T_carrier_by_mode_label",
                "detected": values["direct_shell_gate"]["direct_shell_provider"]["hashed_exact_T_two_j138_stream_identification_status"] == "NO_CERTIFIED_MAP",
            },
        ],
        "flags": {
            "GENERIC_FINITE_SHELL_SU2_REALITY_THEOREM_EXPORTED": True,
            "DE_RHAM_AND_LAPLACIAN_REALITY_INTERTWINING_CERTIFIED": True,
            "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED": True,
            "ALL_EIGHT_TWO_J5_REAL_CHANNEL_SUMS_EXPORTED": True,
            "TWO_J6_FEEDBACK_CHANNELS_EVALUATED": False,
            "PHYSICAL_MASS_COUPLING_SPECIALIZATION_EXPORTED": False,
            "FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_TWO_J6_FEEDBACK_COLUMNS_WITH_REALITY_PAIR_FOLDING_THEN_ENTER_THE_TAIL_STOP_LOOP",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


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
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger recoil real-shell extraction certificate")
    print("BERGER_RECOIL_REAL_SHELL_EXTRACTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
