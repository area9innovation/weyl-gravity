#!/usr/bin/env python3
"""Serialize the exact finite D x SO(4) strict pure-Weyl residual SDR."""
from __future__ import annotations

import argparse
from hashlib import sha256
from json import dumps, loads
from math import comb
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_STRICT_DFINITE_RESIDUAL_SDR_V1.md"
ENERGIES = tuple(range(2, 7))
INPUTS = (
    ("bridge/certificates/cylinder_bgg_blocks.json", "PURE_WEYL_CYLINDER_BGG_NORMAL_FORM_V1", "exact split-basis BGG dimensions and partial-identity arrows"),
    ("bridge/certificates/cyclic_bv_retract.json", "PURE_WEYL_CYCLIC_BV_RETRACT_V1", "historical internal-map SDR and cyclicity certificate"),
    ("bridge/bgg_operators/normal_form.py", "CYLINDER_BGG_NORMAL_FORM_SOURCE", "producer implementation provenance; not independent proof authority"),
    ("bridge/bv_complex/free_block.py", "FREE_BV_BLOCK_SOURCE", "producer implementation provenance; not independent proof authority"),
    ("quantum-weyl/classical_import/snapshots/bootstrap-v1.json", "CLASSICAL_IMPORT_BOOTSTRAP_V1", "historical twenty-export and ten-identity receiver contract"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json", "CLASSICAL_IMPORT_GATE_V2_RECONCILIATION", "current six-family missing-object ledger"),
)


def file_hash(path: str) -> str:
    return sha256((ROOT / path).read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256(dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def choose(value: int, degree: int) -> int:
    return comb(value, degree) if value >= degree >= 0 else 0


def dimensions(energy: int) -> dict[str, int]:
    n = energy
    gauge = 4 * choose(n + 4, 3)
    metric = 9 * choose(n + 3, 3)
    chirality = 3 * n * n - 7
    physical = 2 * chirality
    equation = (n - 2) * (n - 3) * (5 * n + 7) // 6
    bach_target = 9 * choose(n - 1, 3)
    noether = 4 * choose(n - 2, 3)
    scalar = choose(n + 3, 3)
    return {
        "gauge": gauge,
        "metric": metric,
        "chirality": chirality,
        "physical": physical,
        "equation": equation,
        "bach_target": bach_target,
        "noether_identity": noether,
        "scalar": scalar,
    }


def add_identity(entries: list[list[Any]], row_start: int, column_start: int, size: int) -> None:
    entries.extend([row_start + index, column_start + index, "1"] for index in range(size))


def matrix(name: str, rows: int, columns: int, entries: list[list[Any]]) -> dict[str, Any]:
    entries.sort(key=lambda item: (item[0], item[1]))
    payload = {"name": name, "rows": rows, "columns": columns, "entries": entries}
    payload["sha256"] = canonical_hash({key: payload[key] for key in ("name", "rows", "columns", "entries")})
    return payload


def block(energy: int, full_offset: int, residual_offset: int) -> dict[str, Any]:
    d = dimensions(energy)
    sector_specs = (
        ("diff_ghost", d["gauge"], -1, 0, "minimal Diff ghost after CKV separation"),
        ("weyl_ghost", d["scalar"], -1, 0, "minimal Weyl ghost"),
        ("metric_trace", d["scalar"], 0, 0, "Weyl-contractible trace"),
        ("metric_tf", d["metric"], 0, 0, "trace-free metric; gauge | W+ | W- | equation"),
        ("metric_antifield", d["bach_target"], 1, 1, "Bach equation row; equation | Noether complement"),
        ("diff_ghost_antifield", d["noether_identity"], 2, 2, "Noether identity row"),
        ("trace_antifield", d["scalar"], 1, 1, "dual Weyl-contractible source"),
        ("weyl_ghost_antifield", d["scalar"], 2, 2, "dual Weyl-contractible target"),
        ("antighost", d["scalar"], -1, 0, "scalar test nonminimal source"),
        ("multiplier", d["scalar"], 0, 0, "scalar test nonminimal target"),
    )
    sectors: list[dict[str, Any]] = []
    cursor = 0
    full_basis: list[str] = []
    starts: dict[str, int] = {}
    for name, size, ghost_number, antifield_number, role in sector_specs:
        starts[name] = cursor
        sectors.append({
            "name": name,
            "start": cursor,
            "stop": cursor + size,
            "dimension": size,
            "ghost_number": ghost_number,
            "antifield_number": antifield_number,
            "role": role,
        })
        full_basis.extend(f"E{energy}:{name}:{index}" for index in range(size))
        cursor += size
    full_dimension = cursor
    residual_basis = [
        *(f"E{energy}:W_PLUS:{index}" for index in range(d["chirality"])),
        *(f"E{energy}:W_MINUS:{index}" for index in range(d["chirality"])),
    ]
    residual_dimension = len(residual_basis)

    q0: list[list[Any]] = []
    add_identity(q0, starts["metric_tf"], starts["diff_ghost"], d["gauge"])
    add_identity(q0, starts["metric_trace"], starts["weyl_ghost"], d["scalar"])
    add_identity(q0, starts["metric_antifield"], starts["metric_tf"] + d["gauge"] + d["physical"], d["equation"])
    add_identity(q0, starts["diff_ghost_antifield"], starts["metric_antifield"] + d["equation"], d["noether_identity"])
    add_identity(q0, starts["weyl_ghost_antifield"], starts["trace_antifield"], d["scalar"])
    add_identity(q0, starts["multiplier"], starts["antighost"], d["scalar"])

    iota: list[list[Any]] = []
    add_identity(iota, starts["metric_tf"] + d["gauge"], 0, residual_dimension)
    pi: list[list[Any]] = []
    add_identity(pi, 0, starts["metric_tf"] + d["gauge"], residual_dimension)
    s_cl: list[list[Any]] = []
    add_identity(s_cl, starts["diff_ghost"], starts["metric_tf"], d["gauge"])
    add_identity(s_cl, starts["weyl_ghost"], starts["metric_trace"], d["scalar"])
    add_identity(s_cl, starts["metric_tf"] + d["gauge"] + d["physical"], starts["metric_antifield"], d["equation"])
    add_identity(s_cl, starts["metric_antifield"] + d["equation"], starts["diff_ghost_antifield"], d["noether_identity"])
    add_identity(s_cl, starts["trace_antifield"], starts["weyl_ghost_antifield"], d["scalar"])
    add_identity(s_cl, starts["antighost"], starts["multiplier"], d["scalar"])

    matrices = {
        "q0": matrix("q0", full_dimension, full_dimension, q0),
        "iota_cl": matrix("iota_cl", full_dimension, residual_dimension, iota),
        "pi_cl": matrix("pi_cl", residual_dimension, full_dimension, pi),
        "s_cl": matrix("s_cl", full_dimension, full_dimension, s_cl),
        "q_res_0": matrix("q_res_0", residual_dimension, residual_dimension, []),
    }
    return {
        "energy": energy,
        "full_offset": full_offset,
        "residual_offset": residual_offset,
        "full_dimension": full_dimension,
        "residual_dimension": residual_dimension,
        "dimensions": d,
        "full_sectors": sectors,
        "full_basis": full_basis,
        "residual_basis": residual_basis,
        "basis_hashes": {"full": canonical_hash(full_basis), "residual": canonical_hash(residual_basis)},
        "matrices": matrices,
    }


def build() -> dict[str, Any]:
    bgg = loads((ROOT / INPUTS[0][0]).read_text())
    cyclic = loads((ROOT / INPUTS[1][0]).read_text())
    if bgg.get("category") != "D-finite SO(4)-finite BGG-adapted harmonic blocks":
        raise ValueError("BGG category drift")
    if cyclic.get("category") != "BGG-split algebraic free BV blocks":
        raise ValueError("cyclic retract category drift")
    bgg_by_energy = {item["energy"]: item for item in bgg["levels"]}
    cyclic_by_energy = {item["energy"]: item for item in cyclic["levels"]}
    blocks: list[dict[str, Any]] = []
    full_offset = residual_offset = 0
    for energy in ENERGIES:
        item = block(energy, full_offset, residual_offset)
        if item["residual_dimension"] != bgg_by_energy[energy]["dim_kerB_mod_imK"]:
            raise ValueError(f"BGG residual dimension drift at energy {energy}")
        if item["full_dimension"] != cyclic_by_energy[energy]["full_dimension"]:
            raise ValueError(f"cyclic full dimension drift at energy {energy}")
        blocks.append(item)
        full_offset += item["full_dimension"]
        residual_offset += item["residual_dimension"]
    global_projection = {
        "ordered_block_energies": list(ENERGIES),
        "full_dimension": full_offset,
        "residual_dimension": residual_offset,
        "block_offsets": [
            {"energy": item["energy"], "full": item["full_offset"], "residual": item["residual_offset"]}
            for item in blocks
        ],
        "field_dictionary_hash": canonical_hash([label for item in blocks for label in item["full_basis"]]),
        "residual_basis_hash": canonical_hash([label for item in blocks for label in item["residual_basis"]]),
        "differential_hash": canonical_hash([item["matrices"]["q0"]["sha256"] for item in blocks]),
        "residual_sdr_hash": canonical_hash([
            [item["matrices"][name]["sha256"] for name in ("iota_cl", "pi_cl", "s_cl", "q_res_0")]
            for item in blocks
        ]),
    }
    result: dict[str, Any] = {
        "schema": "strict-dfinite-residual-sdr-v1",
        "result_id": "STRICT_DFINITE_RESIDUAL_SDR_V1",
        "result_kind": "SCOPED_CLASSICAL_RESIDUAL_SDR_EXPORT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "1ffc17e215f5a5e55ce7c095bccd25210af0698c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the exact strict pure-Weyl D-finite residual inclusion, projection and contracting homotopy that were previously present only as internal matrices and hashes be exported portably and independently replayed?",
        "answer": "Yes, for the declared energies 2 through 6 in the BGG-adapted D x SO(4)-finite split carrier. The result serializes 4,490 ordered full coordinates, 470 ordered residual W+/W- coordinates, q0, q_res^(0)=0, iota_cl, pi_cl and s_cl as exact sparse integer matrices. An implementation-independent receiver replays q0^2=0, pi_cl iota_cl=1, iota_cl pi_cl=1-q0 s_cl-s_cl q0, both chain intertwiners and all normalized SDR side conditions. This closes the historical portable-map absence only in the finite split category. It does not supply the common full support-local Gate-A carrier, vector nonminimal sector, arbitrary-support local fields, full cyclic pairing, noncompact-equivariant representative SDR, q2 or D.",
        "scope": {
            "theory": "strict pure-Weyl free BV detour complex",
            "carrier": "BGG-adapted D-finite SO(4)-finite split harmonic blocks with the scalar test nonminimal doublet",
            "energies": list(ENERGIES),
            "support": "finite harmonic coefficient space; no arbitrary-support or distributional claim",
            "residual": "W+ direct-sum W- metric cohomology in each positive-energy block",
        },
        "conventions": {
            "contraction": "iota_cl pi_cl = 1 - q0 s_cl - s_cl q0",
            "projection_name": "pi_cl",
            "kinetic_operator_reserved_name": "P or mathcal_P",
            "matrix_entry_format": "[zero-based row, zero-based column, exact rational string]",
            "global_map": "block diagonal in the ordered energy list",
        },
        "global_direct_sum": global_projection,
        "blocks": blocks,
        "independent_identity_contract": [
            "q0 q0=0",
            "pi_cl iota_cl=1_res",
            "iota_cl pi_cl=1_full-q0 s_cl-s_cl q0",
            "q0 iota_cl=iota_cl q_res_0",
            "pi_cl q0=q_res_0 pi_cl",
            "s_cl s_cl=0",
            "s_cl iota_cl=0",
            "pi_cl s_cl=0",
        ],
        "foundational_strength": {
            "exactness_type": "FINITE_EXACT_INTEGER_SPARSE_LINEAR_ALGEBRA",
            "fixed_fixture_base": "Primitive-recursive arithmetic suffices to replay each declared finite block and the finite direct sum.",
            "choice_dependency": "No choice principle is used by the serialized finite matrices or receiver.",
            "infinity_dependency": "None inside the declared five-block cutoff; the all-energy or continuum extension is not certified.",
            "constructive_content": "All bases, maps and witnesses are explicitly enumerated; every equality is decidable by finite exact arithmetic.",
        },
        "gate_a_effect": {
            "historical_missing_exports_scoped_now_portable": ["classical_inclusion_iota_cl", "classical_projection_pi_cl", "classical_homotopy_s_cl"],
            "historical_checks_scoped_now_replayed": ["pi_cl_iota_cl_identity", "classical_contraction_identity", "q0_iota_intertwining", "pi_q0_intertwining"],
            "gate_a_status": "FAIL_CLOSED",
            "remaining_m3_gap": "Extend or reconstruct these maps on the one common authoritative support-local strict carrier, including the complete nonminimal sector and common pairing conventions.",
        },
        "provenance": {
            "inputs": [
                {"path": path, "result_or_artifact_id": artifact_id, "sha256": file_hash(path), "role": role}
                for path, artifact_id, role in INPUTS
            ]
        },
        "claim_flags": {
            "STRICT_DFINITE_RESIDUAL_SDR_PORTABLE": True,
            "ALL_EIGHT_SDR_IDENTITIES_INDEPENDENTLY_REPLAYABLE": True,
            "FINITE_EXACT_FOUNDATIONAL_CLASSIFICATION_RECORDED": True,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_SUPPORT_LOCAL_RESIDUAL_SDR_CONSTRUCTED": False,
            "FULL_CYCLIC_PAIRING_EXPORTED": False,
            "NONCOMPACT_EQUIVARIANT_REPRESENTATIVE_SDR": False,
            "STRICT_SUPPORT_LOCAL_Q2_D_CONSTRUCTED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "the common full support-local classical Gate-A snapshot",
            "the complete vector and scalar nonminimal field domain",
            "an arbitrary-support, smooth, distributional or causal residual contraction",
            "strict noncompact SO(4,2) equivariance of the chosen representative SDR",
            "the full cyclic pairing required by M4",
            "strict support-local q2 or D",
            "a Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Use the exact block payload as a receiver control while constructing the common full support-local strict carrier. The next irreducible target-theory coefficient task remains M2 (strict q2 and D); the remaining M3 task is the same maps on that common carrier, not another finite-mode hash.",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_dfinite_residual_sdr.py",
            "expected_blocks": len(blocks),
            "expected_full_dimension": full_offset,
            "expected_residual_dimension": residual_offset,
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_DFINITE_RESIDUAL_SDR_V1.md",
    }
    result["independent_checker"]["expected_digest"] = canonical_hash({
        key: result[key]
        for key in ("scope", "conventions", "global_direct_sum", "blocks", "independent_identity_contract", "foundational_strength", "gate_a_effect")
    })
    return result


def report(value: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {item['energy']} | {item['full_dimension']} | {item['residual_dimension']} | {len(item['matrices']['q0']['entries'])} | {len(item['matrices']['s_cl']['entries'])} |"
        for item in value["blocks"]
    )
    return f"""# Strict D-finite residual SDR export v1

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

The strict pure-Weyl finite harmonic SDR is now a portable exact object rather
than an internal matrix hash.  The ordered direct sum contains
**{value['global_direct_sum']['full_dimension']} full coordinates** and
**{value['global_direct_sum']['residual_dimension']} residual coordinates**.
It serializes `q0`, `q_res_0`, `iota_cl`, `pi_cl`, and `s_cl` block by block.

| Energy | Full dimension | Residual dimension | nonzero q0 | nonzero s_cl |
|---:|---:|---:|---:|---:|
{rows}

The independent receiver uses only standard-library exact rational sparse
arithmetic.  It reconstructs the expected BGG-split arrows from the declared
sector ledger and replays all eight identities, rather than trusting producer
booleans.

## Foundational strength

For this fixed five-block fixture, primitive-recursive arithmetic suffices:
the bases and witnesses are finite, explicitly enumerated, and all equality
questions reduce to exact integer sparse-matrix multiplication.  No form of
Choice and no completed infinity enters the certified replay.  This statement
does **not** transfer to the all-energy direct sum or continuum field carrier.

## Gate-A effect

The three historically absent portable maps and four associated identities
are now receiver-replayable in the `D`-finite split category.  Gate A remains
`FAIL_CLOSED`: the payload is not the common full support-local strict carrier,
does not include the complete nonminimal field domain or M4 pairing, and does
not supply strict `q2` or `D`.

## Exact commands

```bash
python3 quantum-weyl/classical_import/build_strict_dfinite_residual_sdr.py --check
python3 quantum-weyl/classical_import/check_strict_dfinite_residual_sdr.py
python3 quantum-weyl/classical_import/verify_strict_dfinite_residual_sdr.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_dfinite_residual_sdr.py
```

## What this does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    expected = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in expected if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("STRICT_DFINITE_RESIDUAL_SDR_V1: stale: " + ", ".join(stale))
            return 1
        print("STRICT_DFINITE_RESIDUAL_SDR_V1: generated artifacts current")
        return 0
    for path, content in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_DFINITE_RESIDUAL_SDR_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
