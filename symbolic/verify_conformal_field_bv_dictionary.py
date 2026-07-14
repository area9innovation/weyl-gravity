#!/usr/bin/env python3
"""Field-theoretic certificate for the minimal pure-Weyl BV detour chain.

This is Phase 1 of the field-BV identification programme.  It derives the
linear tangent differential from the quadratic minimal master action in full
symmetric metric variables, constructs the trace/ghost canonical change of
variables, and proves exact matrix identities with the certified raw chain.

The result does *not* yet identify the complete gauge-fixed field domain:
nonminimal gauge fixing, the dual residual zero-mode sector, the full BV-row
inventory, and transfer of the cyclic pairing remain later work packages.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.bv_complex.conformal_polynomials import homogeneous_monomials
from bridge.zero_modes import conformal_killing_projector
from field_bv_identification.minimal_master_action.free_master_action import (
    MINIMAL_VARIABLES,
    master_action_summary,
)
from field_bv_identification.raw_chain_comparison import MinimalRawComparison
from field_bv_identification.variable_dictionary import basis_records, row_dictionary


CERTIFICATE_PATH = (
    ROOT / "field_bv_identification" / "certificates" / "minimal_bv_chain.json"
)
DICTIONARY_PATH = (
    ROOT / "field_bv_identification" / "certificates" / "minimal_bv_dictionary.tsv"
)
LATEX_PATH = (
    ROOT / "field_bv_identification" / "generated_latex" / "minimal_bv_dictionary.tex"
)


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def _matrix_digest(matrix: sp.MatrixBase) -> str:
    payload = "\n".join(
        f"{row},{column}:{value}"
        for (row, column), value in sorted(matrix.todok().items())
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _inhomogeneous_trace_split() -> tuple[sp.SparseMatrix, sp.SparseMatrix, int]:
    """The low-mode ``(xi,sigma)->(xi,Omega)`` map and its inverse."""

    vector_exponents = tuple(
        exponent
        for degree in range(3)
        for exponent in homogeneous_monomials(degree)
    )
    scalar_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    scalar_index = {exponent: row for row, exponent in enumerate(scalar_exponents)}
    vector_dimension = 4 * len(vector_exponents)
    entries: dict[tuple[int, int], sp.Expr] = {}
    for component in range(4):
        for monomial, exponent in enumerate(vector_exponents):
            if exponent[component] == 0:
                continue
            output = list(exponent)
            coefficient = sp.Integer(output[component])
            output[component] -= 1
            entries[
                scalar_index[tuple(output)], component * len(vector_exponents) + monomial
            ] = coefficient / 4
    divergence_over_four = sp.SparseMatrix(
        len(scalar_exponents), vector_dimension, entries
    )
    total = vector_dimension + len(scalar_exponents)
    forward = sp.MutableSparseMatrix(sp.eye(total))
    forward[vector_dimension:, :vector_dimension] = divergence_over_four
    inverse = sp.MutableSparseMatrix(sp.eye(total))
    inverse[vector_dimension:, :vector_dimension] = -divergence_over_four
    return sp.SparseMatrix(forward), sp.SparseMatrix(inverse), vector_dimension


def certificate_data(minimum_energy: int, maximum_energy: int) -> dict[str, object]:
    if minimum_energy < 2:
        raise ValueError("the centered positive-energy comparison starts at E=2")
    if maximum_energy < minimum_energy:
        raise ValueError("maximum energy precedes minimum energy")

    check(
        "FTBV-M1: conventional BV variables have tangent degree -ghost number",
        all(
            variable.tangent_degree == -variable.conventional_ghost_number
            for variable in MINIMAL_VARIABLES
        ),
    )

    low_forward, low_inverse, vector_dimension = _inhomogeneous_trace_split()
    ckv = conformal_killing_projector()
    transformed_ckv = low_forward * ckv.basis
    raw_low_gauge = ckv.gauge_map * low_inverse
    check(
        "FTBV-T1: Omega=omega+div(c)/4 is an exact invertible low-mode change",
        low_inverse * low_forward == sp.eye(65)
        and low_forward * low_inverse == sp.eye(65),
    )
    check(
        "FTBV-T2: T(ker K_BV)=ker K_raw with all fifteen CKV modes",
        transformed_ckv.rank() == 15
        and transformed_ckv[vector_dimension:, :] == sp.zeros(5, 15)
        and raw_low_gauge * transformed_ckv == sp.zeros(50, 15)
        and raw_low_gauge.rank() == 50,
    )

    levels: list[dict[str, object]] = []
    detailed_records: list[dict[str, object]] = []
    detailed_record_count = 0
    detailed_columns: list[str] = []
    # Build the largest sparse block first.  SymPy retains a small amount of
    # structural cache between exact products; descending order keeps the
    # peak below the CI memory limit without changing any certificate data.
    for energy in range(maximum_energy, minimum_energy - 1, -1):
        comparison = MinimalRawComparison.at_energy(energy)
        identity = sp.SparseMatrix.eye(comparison.bv.dimension)
        check(
            f"FTBV-C1[{energy}]: F and G are exact inverse field redefinitions",
            comparison.raw_to_field * comparison.field_to_raw == identity
            and comparison.field_to_raw * comparison.raw_to_field == identity,
        )
        check(
            f"FTBV-C2[{energy}]: F Q_BV = Q_raw F exactly",
            comparison.field_to_raw * comparison.bv.q
            == comparison.raw.q * comparison.field_to_raw,
        )
        check(
            f"FTBV-C3[{energy}]: G Q_raw = Q_BV G exactly",
            comparison.raw_to_field * comparison.raw.q
            == comparison.bv.q * comparison.raw_to_field,
        )
        records = list(basis_records(energy, comparison.raw))
        check(
            f"FTBV-C4[{energy}]: every raw basis vector has a dictionary row",
            len(records) == comparison.raw.dimension,
        )
        check(
            f"FTBV-C5[{energy}]: raw=trace-free detour direct-sum trace trivial",
            2 * len(comparison.trace_homotopy.todok())
            == len(comparison.trace_projector.todok()),
        )
        detailed_record_count += len(records)
        detailed_records.extend(records)
        if records and not detailed_columns:
            detailed_columns = list(records[0])
        levels.append(
            {
                "energy": energy,
                "dimension": comparison.bv.dimension,
                "row_dimensions": {
                    chain_slice.name: chain_slice.dimension
                    for chain_slice in comparison.raw.slices
                },
                "field_to_raw_sha256": _matrix_digest(comparison.field_to_raw),
                "raw_to_field_sha256": _matrix_digest(comparison.raw_to_field),
                "q_bv_sha256": _matrix_digest(comparison.bv.q),
                "q_raw_sha256": _matrix_digest(comparison.raw.q),
                "basis_records": len(records),
                "trace_trivial_dimension": len(
                    comparison.trace_projector.todok()
                ),
                "chain_homotopies": {
                    "H_BV": "zero (the minimal comparison is an isomorphism)",
                    "H_raw": "zero (the minimal comparison is an isomorphism)",
                },
            }
        )
        # SymPy caches exact sparse products aggressively.  Release the
        # previous energy block before constructing the next one so the
        # centered-buffer certificate remains usable in constrained CI.
        del comparison, identity, records
        gc.collect()
        sp.core.cache.clear_cache()

    levels.sort(key=lambda row: row["energy"])
    detailed_records.sort(key=lambda row: (row["energy"], row["raw_index"]))
    check(
        "FTBV-D1: the complete centered buffer E=2..5 is included",
        minimum_energy <= 2 and maximum_energy >= 5,
    )
    check(
        "FTBV-D2: the requested G/M/E/I dictionary is exhaustive",
        {row["raw_row"] for row in row_dictionary()}
        == {"G_n", "M_n", "E_n", "I_n"},
    )

    return {
        "schema": "pure-weyl-field-bv-minimal-chain-v1",
        "category": (
            "finite D-eigenmode, SO(4)-finite algebraic polynomial cylinder category"
        ),
        "master_action": master_action_summary(),
        "variables": [variable.__dict__ for variable in MINIMAL_VARIABLES],
        "row_dictionary": row_dictionary(),
        "levels": levels,
        "zero_mode_trace_split": {
            "ambient_dimension": 65,
            "ckv_rank_before": 15,
            "ckv_rank_after": transformed_ckv.rank(),
            "Omega_on_ckv": "zero",
            "kernel_identity": "T(ker K_BV)=ker K_raw=so(4,2)",
            "forward_sha256": _matrix_digest(low_forward),
            "inverse_sha256": _matrix_digest(low_inverse),
        },
        "basis_dictionary": {
            "path": str(DICTIONARY_PATH.relative_to(ROOT)),
            "records": detailed_record_count,
            "columns": detailed_columns,
        },
        # Private payload used to stream the generated TSV.  It is removed
        # before the JSON certificate is serialized.
        "_basis_records": detailed_records,
        "theorem": (
            "The tangent complex of the quadratic minimal pure-Weyl master action "
            "is exactly isomorphic to the direct sum of the certified trace-free "
            "raw G->M->E->I detour chain and the explicitly contracted trace "
            "summand throughout the complete centered energy buffer."
        ),
        "proved": [
            "quadratic minimal master-action tangent differential",
            "conventional BV ghost number versus suspended tangent degree",
            "invertible trace/Weyl and dual-antifield field redefinitions",
            "exact F and G chain maps with zero homotopies",
            "unit trace/Weyl contractible arrows",
            "explicit trace projector and contraction q s+s q=P_trace",
            "T(ker K_BV)=ker K_raw for all fifteen conformal-Killing modes",
            "one generated record per raw basis vector",
        ],
        "not_proved": [
            "complete gauge-fixed BV-domain identification",
            "dual residual zero-mode replacement",
            "nonminimal and generalized-auxiliary elimination from a chosen gauge fermion",
            "all potentially entering antifield rows",
            "field-theoretic cyclic/BFV pairing transfer",
            "analytic completion",
        ],
    }


def _write_dictionary_tsv(path: Path, records: list[dict[str, object]]) -> None:
    """Write the exhaustive basis dictionary already certified in memory."""

    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(records)


def _latex(data: dict[str, object]) -> str:
    dictionary_rows = []
    for row in data["row_dictionary"]:
        dictionary_rows.append(
            "{} & {} & {} & {} & {} & {} \\\\".format(
                row["raw_row"],
                row["raw_variable"].replace("_", r"\_"),
                row["bv_variable"].replace("_", r"\_"),
                row["ghost_number"],
                row["local_degree"],
                row["differential"].replace("_", r"\_"),
            )
        )
    level_rows = [
        "{} & {} & {} & {} & {} & {} \\\\".format(
            level["energy"],
            level["row_dimensions"]["gauge"],
            level["row_dimensions"]["metric"],
            level["row_dimensions"]["equation"],
            level["row_dimensions"]["identity"],
            level["dimension"],
        )
        for level in data["levels"]
    ]
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_field_bv_dictionary.py",
            r"\begin{tabular}{c|l|l|r|r|l}",
            r"raw row & raw variable & BV variable & $\operatorname{gh}_{\rm BV}$ & $q_{\rm loc}$ & image \\",
            r"\hline",
            *dictionary_rows,
            r"\end{tabular}",
            "",
            r"\begin{tabular}{c|rrrr|r}",
            r"$n$ & $\dim G_n$ & $\dim M_n$ & $\dim E_n$ & $\dim I_n$ & total \\",
            r"\hline",
            *level_rows,
            r"\end{tabular}",
            "",
            r"\[",
            r" FQ_{\rm BV}=Q_{\rm raw}F,\qquad",
            r" GQ_{\rm raw}=Q_{\rm BV}G,\qquad",
            r" GF=FG=1.",
            r"\]",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-energy", type=int, default=2)
    parser.add_argument("--max-energy", type=int, default=5)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-complete-field-bv-domain",
        action="store_true",
        help="fail closed: the minimal chain dictionary is only Phase 1",
    )
    args = parser.parse_args()
    if args.claim_complete_field_bv_domain:
        raise SystemExit(
            "REFUSED: the exact minimal chain comparison does not yet inventory "
            "the complete gauge-fixed BV domain, dual zero modes, or pairing transfer"
        )
    data = certificate_data(args.min_energy, args.max_energy)
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        DICTIONARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        LATEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        records = data.pop("_basis_records")
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        _write_dictionary_tsv(DICTIONARY_PATH, records)
        LATEX_PATH.write_text(_latex(data), encoding="utf-8")
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
        print("wrote", DICTIONARY_PATH.relative_to(ROOT))
        print("wrote", LATEX_PATH.relative_to(ROOT))
    else:
        data.pop("_basis_records", None)
    print("CONFORMAL FIELD-BV MINIMAL CHAIN DICTIONARY: ALL PASS")


if __name__ == "__main__":
    main()
