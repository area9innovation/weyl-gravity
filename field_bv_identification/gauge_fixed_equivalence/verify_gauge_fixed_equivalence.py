#!/usr/bin/env python3
"""Machine certificate for the gauge-fixed/nonminimal equivalence theorem."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.gauge_fixed_equivalence.auxiliary_elimination import (
    elimination_ledger,
    generalized_auxiliary_report,
)
from field_bv_identification.gauge_fixed_equivalence.contraction import (
    GaugeFixedContraction,
    ZeroModePreservation,
)
from field_bv_identification.gauge_fixed_equivalence.dictionary import (
    gauge_fixed_records,
)


PACKAGE = ROOT / "field_bv_identification" / "gauge_fixed_equivalence"
CERTIFICATE_DIR = PACKAGE / "certificates"
DICTIONARY_PATH = CERTIFICATE_DIR / "gauge_fixed_dictionary.tsv"
PAIR_PATH = CERTIFICATE_DIR / "nonminimal_pairs.json"
CONTRACTION_PATH = CERTIFICATE_DIR / "contraction.json"
ZERO_MODE_PATH = CERTIFICATE_DIR / "zero_mode_preservation.json"
LATEX_PATH = ROOT / "field_bv_identification" / "generated_latex" / "gauge_fixed_equivalence.tex"


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


def _write_tsv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise AssertionError("cannot emit an empty gauge-fixed dictionary")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(records)


def certificate_data(minimum_energy: int, maximum_energy: int):
    if minimum_energy < 2 or maximum_energy < minimum_energy:
        raise ValueError("use a nonempty centered positive-energy buffer starting at E>=2")

    zero_modes = ZeroModePreservation.build()
    check(
        "FTBV-GF-Z1: P_Z Q_gf=Q_gf P_Z and all fifteen CKVs remain closed",
        zero_modes.extended_projector * zero_modes.q_gauge_fixed_model
        == zero_modes.q_gauge_fixed_model * zero_modes.extended_projector
        and zero_modes.q_gauge_fixed_model * zero_modes.extended_projector
        == sp.zeros(zero_modes.q_gauge_fixed_model.rows)
        and zero_modes.extended_projector.rank() == 15,
    )
    check(
        "FTBV-GF-Z2: the local complement is exact and counted once",
        zero_modes.complement_basis.cols == 50
        and zero_modes.local_gauge_map.rank() == 50
        and zero_modes.projector + zero_modes.complement_projector == sp.eye(65),
    )
    check(
        "FTBV-GF-Z3: the zero-mode projector is D x SO(4) equivariant",
        zero_modes.projector * zero_modes.compact_dilation
        == zero_modes.compact_dilation * zero_modes.projector
        and all(
            zero_modes.projector * rotation == rotation * zero_modes.projector
            for rotation in zero_modes.compact_rotations
        ),
    )

    levels: list[dict[str, object]] = []
    pair_levels: list[dict[str, object]] = []
    all_records: list[dict[str, object]] = []
    fermion_summary: dict[str, object] | None = None
    for energy in range(maximum_energy, minimum_energy - 1, -1):
        contraction = GaugeFixedContraction.at_energy(energy)
        block = contraction.block
        check(
            f"FTBV-GF-F1[{energy}]: one explicit D x SO(4) Landau fermion generates the shear",
            block.gauge_fermion.summary()["ghost_number"] == -1
            and block.gauge_fermion.summary()["density_weight"] == 4
            and block.gauge_fermion.summary()["multiplier_square"] is False,
        )
        check(
            f"FTBV-GF-N1[{energy}]: all Diff and Weyl nonminimal pairs and antifield duals contract",
            block.nonminimal.tangent_q * block.nonminimal.tangent_homotopy
            + block.nonminimal.tangent_homotopy * block.nonminimal.tangent_q
            == sp.eye(block.nonminimal.dimension),
        )
        check(
            f"FTBV-GF-C1[{energy}]: the gauge-fermion canonical shear is exactly invertible",
            block.canonical_map * block.canonical_inverse == sp.eye(block.dimension)
            and block.shear * block.shear == sp.zeros(block.dimension),
        )
        check(
            f"FTBV-GF-C2[{energy}]: Q_gf=T_Psi Q_ext T_Psi^-1 is exactly nilpotent",
            block.q_gauge_fixed
            == block.canonical_map * block.q_unfixed * block.canonical_inverse
            and block.q_gauge_fixed * block.q_gauge_fixed
            == sp.zeros(block.dimension),
        )
        check(
            f"FTBV-GF-C3[{energy}]: p_gf,j_gf,s_gf give the required strong deformation retract",
            contraction.projection * contraction.inclusion == sp.eye(block.raw.dimension)
            and contraction.inclusion * contraction.projection
            == sp.eye(block.dimension)
            - block.q_gauge_fixed * contraction.homotopy
            - contraction.homotopy * block.q_gauge_fixed,
        )
        records = list(gauge_fixed_records(contraction))
        check(
            f"FTBV-GF-C4[{energy}]: every gauge-fixed coordinate has an explicit classification",
            len(records) == block.dimension
            and not any(row["equality_certificate"] != "exact" for row in records),
        )
        ledger = list(elimination_ledger(block.nonminimal))
        check(
            f"FTBV-GF-C5[{energy}]: no multiplier or antifield is silently discarded",
            len(ledger) == 8
            and all(not row["silently_discarded"] for row in ledger)
            and not any(row["generalized_auxiliary"] for row in ledger),
        )
        fermion_summary = block.gauge_fermion.summary()
        all_records.extend(records)
        levels.append(
            {
                "energy": energy,
                "minimal_dimension": block.raw.dimension,
                "nonminimal_dimension": block.nonminimal.dimension,
                "gauge_fixed_dimension": block.dimension,
                "q_gauge_fixed_sha256": _matrix_digest(block.q_gauge_fixed),
                "canonical_map_sha256": _matrix_digest(block.canonical_map),
                "canonical_inverse_sha256": _matrix_digest(block.canonical_inverse),
                "projection_sha256": _matrix_digest(contraction.projection),
                "inclusion_sha256": _matrix_digest(contraction.inclusion),
                "homotopy_sha256": _matrix_digest(contraction.homotopy),
                "dictionary_records": len(records),
            }
        )
        pair_levels.append(
            {
                "energy": energy,
                "coordinate_brst_rules": list(block.nonminimal.coordinate_brst_rules()),
                "tangent_arrows": [
                    "vector_multiplier -> vector_antighost",
                    "scalar_multiplier -> scalar_antighost",
                    "vector_antighost_antifield -> vector_multiplier_antifield",
                    "scalar_antighost_antifield -> scalar_multiplier_antifield",
                ],
                "fields": [field.__dict__ for field in block.nonminimal.slices],
                "homotopy_sha256": _matrix_digest(block.nonminimal.tangent_homotopy),
            }
        )
        del contraction, block, records
        gc.collect()
        sp.core.cache.clear_cache()

    levels.sort(key=lambda row: row["energy"])
    pair_levels.sort(key=lambda row: row["energy"])
    all_records.sort(key=lambda row: (row["energy"], row["full_index"]))
    check(
        "FTBV-GF-D1: the complete centered buffer E=2..5 is included",
        minimum_energy <= 2 and maximum_energy >= 5,
    )
    check(
        "FTBV-GF-D2: the dictionary exhausts minimal, nonminimal, multiplier, and antifield coordinates",
        {row["sector"] for row in all_records} == {"minimal", "nonminimal"}
        and {row["classification"] for row in all_records}
        == {"proven minimal raw chain", "nonminimal doublet"},
    )

    contraction_data = {
        "schema": "pure-weyl-gauge-fixed-contraction-v1",
        "category": "finite D-eigenmode, SO(4)-finite algebraic cylinder category",
        "gauge_fermion": fermion_summary,
        "identity": "j_gf p_gf = 1-Q_gf s_gf-s_gf Q_gf; p_gf j_gf=1",
        "levels": levels,
        "generalized_auxiliary_report": generalized_auxiliary_report(),
        "proved": [
            "canonical BV gauge-fermion conjugation of the quadratic tangent complex",
            "complete Diff and Weyl nonminimal sector including antifield duals",
            "explicit strong deformation retract to the proven minimal raw chain",
            "preservation of all fifteen conformal-Killing modes",
            "exhaustive gauge-fixed coordinate classification",
        ],
        "not_proved": [
            "one-scalar bulk-endpoint-to-BFV transgression",
            "complete polarized-state spectral-row inventory",
            "field BV/BFV pairing transfer",
            "analytic completion",
        ],
    }
    pair_data = {
        "schema": "pure-weyl-nonminimal-pairs-v1",
        "coordinate_vs_tangent_convention": (
            "coordinate BRST has s(bar_c)=b; suspended tangent differential has b->bar_c"
        ),
        "levels": pair_levels,
    }
    zero_data = {
        "schema": "pure-weyl-gauge-fixed-zero-mode-preservation-v1",
        "ambient_ghost_dimension": 65,
        "zero_mode_dimension": zero_modes.projector.rank(),
        "local_complement_dimension": zero_modes.complement_basis.cols,
        "compact_decomposition": [4, 7, 4],
        "labels": list(zero_modes.labels),
        "compact_degrees": list(zero_modes.compact_degrees),
        "identities": [
            "P_Z^2=P_Z",
            "P_Z Q_gf=Q_gf P_Z",
            "Q_gf P_Z=0",
            "G=Z direct-sum G_perp",
            "ker(K|G_perp)=0",
            "[P_Z,D]=0",
            "[P_Z,SO(4)]=0",
        ],
        "projector_sha256": _matrix_digest(zero_modes.projector),
        "complement_basis_sha256": _matrix_digest(zero_modes.complement_basis),
        "local_gauge_map_sha256": _matrix_digest(zero_modes.local_gauge_map),
        "compact_gram_sha256": _matrix_digest(zero_modes.compact_gram),
        "compact_dilation_sha256": _matrix_digest(zero_modes.compact_dilation),
        "compact_rotation_sha256": [
            _matrix_digest(rotation) for rotation in zero_modes.compact_rotations
        ],
    }
    return contraction_data, pair_data, zero_data, all_records


def _latex(data: dict[str, object]) -> str:
    rows = [
        "{} & {} & {} & {} \\\\".format(
            row["energy"],
            row["minimal_dimension"],
            row["nonminimal_dimension"],
            row["gauge_fixed_dimension"],
        )
        for row in data["levels"]
    ]
    return "\n".join(
        [
            "% Generated by verify_gauge_fixed_equivalence.py",
            r"\begin{tabular}{c|rrr}",
            r"$E$ & $\dim C_{\rm min}$ & $\dim C_{\rm nm}$ & $\dim C_{\rm gf}$ \\",
            r"\hline",
            *rows,
            r"\end{tabular}",
            "",
            r"\[",
            r"Q_{\rm gf}=T_\Psi Q_{\rm ext}T_\Psi^{-1},\qquad",
            r"\jmath_{\rm gf}p_{\rm gf}=1-Q_{\rm gf}s_{\rm gf}-s_{\rm gf}Q_{\rm gf}.",
            r"\]",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-energy", type=int, default=2)
    parser.add_argument("--max-energy", type=int, default=5)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-dual-zero-mode-replacement", action="store_true")
    parser.add_argument("--claim-complete-row-inventory", action="store_true")
    parser.add_argument("--claim-pairing-transfer", action="store_true")
    parser.add_argument("--claim-complete-field-bv-domain", action="store_true")
    args = parser.parse_args()
    if args.claim_dual_zero_mode_replacement:
        raise SystemExit(
            "REFUSED: this gauge-fixing executable preserves the fifteen CKVs "
            "but does not itself construct the separately certified endpoint suspension"
        )
    if args.claim_complete_row_inventory:
        raise SystemExit(
            "REFUSED: the gauge-fixed dictionary is exhaustive for this extension, "
            "but the centered row ledger must be built after BFV reduction and polarization"
        )
    if args.claim_pairing_transfer:
        raise SystemExit(
            "REFUSED: canonical gauge fixing is proved, but the even field form and "
            "residual BFV/CE normalization are transferred by a separate certificate"
        )
    if args.claim_complete_field_bv_domain:
        raise SystemExit(
            "REFUSED: this gauge-fixing certificate alone does not prove the "
            "separately certified BFV suspension, polarized ledger, and pairing transfer"
        )
    contraction, pairs, zero_modes, records = certificate_data(
        args.min_energy, args.max_energy
    )
    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        LATEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        _write_tsv(DICTIONARY_PATH, records)
        CONTRACTION_PATH.write_text(
            json.dumps(contraction, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        PAIR_PATH.write_text(
            json.dumps(pairs, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        ZERO_MODE_PATH.write_text(
            json.dumps(zero_modes, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        LATEX_PATH.write_text(_latex(contraction), encoding="utf-8")
        for path in (
            DICTIONARY_PATH,
            PAIR_PATH,
            CONTRACTION_PATH,
            ZERO_MODE_PATH,
            LATEX_PATH,
        ):
            print("wrote", path.relative_to(ROOT))
    print("CONFORMAL FIELD-BV GAUGE-FIXED EQUIVALENCE: ALL PASS")


if __name__ == "__main__":
    main()
