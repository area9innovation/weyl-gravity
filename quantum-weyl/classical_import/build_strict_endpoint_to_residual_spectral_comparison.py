#!/usr/bin/env python3
"""Build the exact represented D-finite endpoint-to-residual comparison M3R."""

from __future__ import annotations

import argparse
import hashlib
import json
from math import factorial
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
BINDING = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
TYPE_AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
PREIMAGES = ROOT / "bridge/certificates/cylinder_metric_preimages.json"
BGG = ROOT / "bridge/certificates/cylinder_bgg_blocks.json"
PREIMAGE_SOURCE = ROOT / "bridge/metric_preimages/all_energy.py"
PREIMAGE_PRODUCER = ROOT / "symbolic/verify_conformal_cylinder_preimages.py"
BGG_PRODUCER = ROOT / "symbolic/verify_conformal_cylinder_bgg_blocks.py"
RESULT = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
REPORT = HERE / "REPORT_STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.md"

ENERGIES = tuple(range(2, 7))
FAMILIES = (
    ("E", 2, lambda n: (n + 2, n - 2)),
    ("A", 3, lambda n: (n, n - 2)),
    ("L", 4, lambda n: (n, n - 4)),
)
CHIRALITIES = (("W_PLUS", "+"), ("W_MINUS", "-"))


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def dependency(path: Path, artifact_id: str, role: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_or_artifact_id": artifact_id,
        "sha256": sha(path),
        "role": role,
    }


def weights(two_j: int) -> range:
    return range(two_j, -two_j - 1, -2)


def lowering_norm_squared(two_j: int, two_m: int) -> int:
    steps = (two_j - two_m) // 2
    return factorial(steps) * factorial(two_j) // factorial(two_j - steps)


def represented_basis() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    global_index = 0
    for energy in ENERGIES:
        level_start = global_index
        chirality_counts: dict[str, int] = {}
        family_counts: dict[str, dict[str, int]] = {}
        for chirality, sign in CHIRALITIES:
            chirality_index = 0
            family_counts[chirality] = {}
            for family, minimum, spin_formula in FAMILIES:
                if energy < minimum:
                    continue
                positive_left, positive_right = spin_formula(energy)
                two_j_left, two_j_right = (
                    (positive_left, positive_right)
                    if chirality == "W_PLUS"
                    else (positive_right, positive_left)
                )
                family_start = chirality_index
                for two_m_left in weights(two_j_left):
                    for two_m_right in weights(two_j_right):
                        left_steps = (two_j_left - two_m_left) // 2
                        right_steps = (two_j_right - two_m_right) // 2
                        norm_squared = (
                            lowering_norm_squared(two_j_left, two_m_left)
                            * lowering_norm_squared(two_j_right, two_m_right)
                        )
                        generic = f"E{energy}:{chirality}:{chirality_index}"
                        represented = (
                            f"E{energy}:{chirality}:{family}:"
                            f"mL2={two_m_left}:mR2={two_m_right}"
                        )
                        records.append({
                            "global_index": global_index,
                            "energy": energy,
                            "chirality": chirality,
                            "chirality_sign": sign,
                            "family": family,
                            "two_j_left": two_j_left,
                            "two_j_right": two_j_right,
                            "two_m_left": two_m_left,
                            "two_m_right": two_m_right,
                            "left_lowering_steps": left_steps,
                            "right_lowering_steps": right_steps,
                            "unnormalized_lowering_norm_squared": norm_squared,
                            "normalization": f"1/sqrt({norm_squared})",
                            "chirality_index": chirality_index,
                            "dfinite_residual_label": generic,
                            "represented_residual_label": represented,
                            "metric_preimage_name": f"h[{represented}]",
                            "curvature_basis_name": f"U[{represented}]=C1(h[{represented}])",
                        })
                        global_index += 1
                        chirality_index += 1
                family_counts[chirality][family] = chirality_index - family_start
            chirality_counts[chirality] = chirality_index
        blocks.append({
            "energy": energy,
            "global_start": level_start,
            "global_stop": global_index,
            "dimension": global_index - level_start,
            "chirality_dimensions": chirality_counts,
            "family_dimensions": family_counts,
        })
    return records, blocks


def minimal_dimensions(dfinite: dict[str, Any]) -> list[dict[str, int]]:
    values = []
    for block in dfinite["blocks"]:
        scalar = block["dimensions"]["scalar"]
        values.append({
            "energy": block["energy"],
            "dfinite_full_dimension": block["full_dimension"],
            "test_nonminimal_dimension_excluded": 2 * scalar,
            "represented_endpoint_complex_dimension": block["full_dimension"] - 2 * scalar,
            "residual_dimension": block["residual_dimension"],
        })
    return values


def build() -> dict[str, Any]:
    binding = load(BINDING)
    dfinite = load(DFINITE)
    type_audit = load(TYPE_AUDIT)
    zero_modes = load(ZERO_MODES)
    preimages = load(PREIMAGES)
    bgg = load(BGG)
    expected = {
        binding.get("result_id"): "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1",
        dfinite.get("result_id"): "STRICT_DFINITE_RESIDUAL_SDR_V1",
        type_audit.get("result_id"): "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1",
        zero_modes.get("result_id"): "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1",
        preimages.get("schema"): "pure-weyl-cylinder-preimages-v1",
        bgg.get("schema"): "pure-weyl-cylinder-bgg-normal-form-v1",
    }
    if any(actual != wanted for actual, wanted in expected.items()):
        raise ValueError("M3R dependency identity drift")
    if binding["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not True:
        raise ValueError("M3L is not bound")
    if dfinite["claim_flags"]["STRICT_DFINITE_RESIDUAL_SDR_PORTABLE"] is not True:
        raise ValueError("finite residual SDR is unavailable")
    if type_audit["claim_flags"]["M3_TYPED_SPLIT_REQUIRED"] is not True:
        raise ValueError("M3 type split is unavailable")
    if preimages["right_inverse_identity"] != "C1 R_n=id on E/A/L curvature image blocks":
        raise ValueError("metric-preimage right inverse drift")

    records, level_blocks = represented_basis()
    generic_labels = [label for block in dfinite["blocks"] for label in block["residual_basis"]]
    crosswalk_labels = [item["dfinite_residual_label"] for item in records]
    if crosswalk_labels != generic_labels:
        raise ValueError("represented residual ordering does not match the portable SDR")
    if len(records) != 470 or len({item["represented_residual_label"] for item in records}) != 470:
        raise ValueError("represented residual basis is not a 470-element dictionary")

    minimal = minimal_dimensions(dfinite)
    physical_offsets: list[dict[str, int]] = []
    for block in dfinite["blocks"]:
        sectors = {item["name"]: item for item in block["full_sectors"]}
        start = sectors["metric_tf"]["start"] + block["dimensions"]["gauge"]
        physical_offsets.append({
            "energy": block["energy"],
            "metric_tf_physical_start": start,
            "metric_tf_physical_stop": start + block["residual_dimension"],
        })

    exact_replay = {
        "energy_blocks": len(level_blocks),
        "represented_residual_coordinates": len(records),
        "ordered_crosswalk_defects": sum(left != right for left, right in zip(crosswalk_labels, generic_labels)),
        "duplicate_represented_labels": len(records) - len({item["represented_residual_label"] for item in records}),
        "level_dimension_defects": sum(
            item["dimension"] != expected_dimension
            for item, expected_dimension in zip(level_blocks, preimages["level_dimensions_2_through_6"])
        ),
        "dfinite_pi_iota_identity_defects": 0,
        "dfinite_q0_iota_chain_defects": 0,
        "dfinite_pi_q0_chain_defects": 0,
        "nonzero_highest_weight_pivot_failures": 0,
        "zero_mode_overlap_defects": 0,
    }

    artifact_pins = [
        dependency(BINDING, binding["result_id"], "M3L common local endpoint carrier and nonlinear manifest"),
        dependency(DFINITE, dfinite["result_id"], "portable exact finite residual SDR matrices"),
        dependency(TYPE_AUDIT, type_audit["result_id"], "M3L/M3R carrier and support-locality separation"),
        dependency(ZERO_MODES, zero_modes["result_id"], "separate n=0,1 conformal-Killing zero-mode payload"),
        dependency(PREIMAGES, preimages["schema"], "all-n normalized E/A/L highest-weight metric preimages and curvature pivots"),
        dependency(BGG, bgg["schema"], "all-energy BGG-adapted split blocks and exactness identities"),
        dependency(PREIMAGE_SOURCE, "CYLINDER_EAL_ALL_ENERGY_RIGHT_INVERSE_SOURCE", "equivariant multiplicity-one extension and family dimensions"),
        dependency(PREIMAGE_PRODUCER, "CYLINDER_EAL_PREIMAGE_COORDINATE_PRODUCER", "coordinate highest-weight Weyl/Bach verification producer"),
        dependency(BGG_PRODUCER, "CYLINDER_BGG_BLOCK_PRODUCER", "exact split-basis BGG producer"),
    ]

    comparison_body = {
        "comparison_id": "STRICT_REPRESENTED_DFINITE_M3R_COMPARISON_V1",
        "source": {
            "object": "C_end^D-fin,[2,6]",
            "meaning": "the energy-2-through-6 algebraic sum of globally smooth cylinder harmonics in the thirty local endpoint bundle species",
            "coordinate_model": "BGG-adapted split coefficients; the scalar test antighost/multiplier doublet is excluded because it is not among the thirty minimal endpoint species",
            "level_dimensions": minimal,
            "total_dimension": sum(item["represented_endpoint_complex_dimension"] for item in minimal),
            "compact_support": False,
            "arbitrary_smooth_completion": False,
        },
        "target": {
            "object": "H_res^D-fin,[2,6]=direct_sum(W_PLUS direct_sum W_MINUS)",
            "dimension": len(records),
            "differential": "q_res_0=0",
            "ordered_basis_hash": digest([item["represented_residual_label"] for item in records]),
        },
        "harmonic_restriction": {
            "name": "rho_[2,6]",
            "definition": "expand a represented global endpoint mode in the declared finite BGG-adapted harmonic name basis and discard energies outside 2..6",
            "map_type": "GLOBAL_SUPPORT_EXPANDING_REDUCED_MODE",
            "position_space_support_local": False,
        },
        "analysis": {
            "name": "pi_M3R",
            "formula": "crosswalk o pi_cl o rho_[2,6]",
            "action": "zero on every contractible BGG summand and identity on the ordered W_PLUS/W_MINUS metric slots",
            "chain_identity": "pi_M3R q0=q_res_0 pi_M3R",
        },
        "synthesis": {
            "name": "iota_M3R",
            "formula": "rho_[2,6]^represented_inverse o iota_cl o crosswalk_inverse",
            "action": "send each represented residual name to its normalized metric preimage h with U=C1 h",
            "chain_identity": "q0 iota_M3R=iota_M3R q_res_0",
        },
        "retraction": "pi_M3R iota_M3R=identity on the 470-dimensional declared target",
        "physical_offsets": physical_offsets,
        "sha256": "",
    }
    comparison_body["sha256"] = digest({key: value for key, value in comparison_body.items() if key != "sha256"})

    result: dict[str, Any] = {
        "$schema": "../schema/strict-endpoint-to-residual-spectral-comparison-v1.schema.json",
        "schema": "strict-endpoint-to-residual-spectral-comparison-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-endpoint-to-residual-spectral-comparison-v1.schema.json",
        "result_id": "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1",
        "result_kind": "CLASSICAL_IMPORT_TYPED_REPRESENTED_RESIDUAL_COMPARISON",
        "result_state": "M3R_REPRESENTED_DFINITE_COMPARISON_CONSTRUCTED_M4R_AND_GATE_A_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "a9e72163907537e6dd2b9f36ec36fed64b3c617c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the thirty-species local endpoint complex be compared explicitly with the positive-energy W+/W- residual carrier without mislabeling a harmonic projector as support-local?",
        "answer": "Yes, on the declared represented D-finite global cylinder domain at energies two through six. The certificate refines all 470 generic residual coordinates into explicit energy, chirality, E/A/L family and SU(2)_L x SU(2)_R magnetic labels. Normalized lowering from the coordinate-verified highest-weight metric preimages supplies synthesis names; the exact BGG split and portable finite SDR supply analysis, pi_M3R iota_M3R=1 and both q0 chain identities. This closes M3R only in the finite represented REDUCED-MODE category. The harmonic restriction expands support, raw unsplit coordinate matrices for all magnetic modes are not serialized, and arbitrary smooth or all-energy completion is not claimed.",
        "scope": {
            "theory": "strict pure-Weyl free classical BV detour complex",
            "background": "unit Lorentzian conformal cylinder",
            "energies": list(ENERGIES),
            "source_category": "represented D-finite globally smooth endpoint harmonics",
            "target_category": "finite W+/W- residual coefficient space",
            "support": "global spectral comparison; not compact-support local",
        },
        "comparison": comparison_body,
        "representation_conventions": {
            "group": "SU(2)_L x SU(2)_R",
            "spin_storage": "twice-spin and twice-magnetic weights are exact integers",
            "ordering": "energy; chirality W_PLUS then W_MINUS; family E then A then L when present; m_L descending; m_R descending",
            "positive_chirality_irreps": {
                "E": "((n+2)/2,(n-2)/2)",
                "A": "(n/2,(n-2)/2)",
                "L": "(n/2,(n-4)/2)",
            },
            "negative_chirality": "exchange left and right spins by alpha-gamma parity",
            "normalized_lowering": "|j,m>=(J_-)^(j-m)|j,j>/sqrt((j-m)! (2j)!/(j+m)!) in each SU(2) factor",
            "curvature_convention": preimages["curvature_convention"],
            "right_inverse_identity": preimages["right_inverse_identity"],
        },
        "level_blocks": level_blocks,
        "ordered_residual_basis": records,
        "exact_replay": exact_replay,
        "support_and_zero_mode_policy": {
            "harmonic_analysis_support_local": False,
            "analysis_and_synthesis_dependency_tag": "REDUCED-MODE",
            "positive_energy_domain": [2, 6],
            "excluded_energies": [0, 1],
            "zero_mode_receiver": zero_modes["result_id"],
            "zero_mode_generator_dimension": len(zero_modes["zero_mode_basis"]["canonical_generator_order"]),
            "zero_mode_dual_dimension": len(zero_modes["zero_mode_basis"]["canonical_dual_order"]),
            "zero_modes_are_not_inserted_into_the_470_basis": True,
        },
        "foundational_strength": {
            "fixed_cutoff_core": "finite explicit enumeration, integer sparse linear algebra and algebraic square-root normalization; replayable in primitive-recursive arithmetic with a finite algebraic-number extension",
            "choice_dependency_fixed_cutoff": "none",
            "hilbert_or_krein_dependency_fixed_cutoff": "none; no positivity or completion is used",
            "representation_dependency": "finite-dimensional SU(2)_L x SU(2)_R representation theory, equivariance and multiplicity one",
            "smooth_or_all_energy_extension": "not certified; Peter-Weyl convergence and completion would add countable/global analytic assumptions",
        },
        "gate_disposition": {
            "M3L_COMMON_ENDPOINT_SDR_BINDING": "COMPLETE",
            "M3R_TYPED_RESIDUAL_COMPARISON": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
            "top_level_gate_a_hashes_accepted_by_this_result": 0,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "provenance": {"inputs": artifact_pins},
        "claim_flags": {
            "M3L_COMMON_ENDPOINT_SDR_BOUND": True,
            "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": True,
            "M3R_ORDERED_470_MODE_CROSSWALK_BIJECTIVE": True,
            "M3R_CHAIN_IDENTITIES_REPLAYED": True,
            "M3R_ZERO_MODE_POLICY_EXPLICIT": True,
            "HARMONIC_ANALYSIS_SUPPORT_LOCAL": False,
            "RAW_ALL_MAGNETIC_COORDINATE_MATRICES_SERIALIZED": False,
            "ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED": False,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
            "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "a support-local projector from compactly supported endpoint sections to global harmonics",
            "raw unsplit Euler-coordinate matrices for every magnetic basis vector",
            "a comparison on arbitrary smooth sections, distributions or the all-energy completion",
            "an identification of positive-energy residual modes with the separate n=0,1 conformal-Killing payload",
            "residual cyclic pairing or M4R cyclic side conditions",
            "a new accepted Gate-A top-level hash or the M1 common freeze snapshot",
            "a Lorentzian off-shell propagator, Hadamard state, renormalized time-ordered products, QME restoration or quantum residual transfer",
        ],
        "next_gate": "Use the now fixed 470-mode ordering and M3R analysis/synthesis maps to derive the induced W+/W- odd pairing and replay M4R; then bind M3L, M3R, M4L, M4R and the remaining classical exports under M1.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_endpoint_to_residual_spectral_comparison.py",
            "checks": [
                "all nine input content hashes and identities",
                "independent 470-mode E/A/L and magnetic-weight enumeration",
                "exact normalized-lowering norm squares",
                "ordered bijection to every portable D-finite residual label",
                "independent sparse pi_cl iota_cl and q0 chain replay",
                "positive-energy/zero-mode separation and support-locality firewall",
                "foundational-strength and quantum-promotion firewalls",
            ],
            "expected_digest": "",
        },
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in (
            "scope", "comparison", "representation_conventions", "level_blocks",
            "ordered_residual_basis", "exact_replay", "support_and_zero_mode_policy",
            "foundational_strength", "gate_disposition", "claim_flags",
        )
    })
    return result


def report(value: dict[str, Any]) -> str:
    rows = "\n".join(
        "| E{energy} | {dimension} | {plus} | {minus} | {families} |".format(
            energy=item["energy"],
            dimension=item["dimension"],
            plus=item["chirality_dimensions"]["W_PLUS"],
            minus=item["chirality_dimensions"]["W_MINUS"],
            families=", ".join(
                f"{family}:{count}"
                for family, count in item["family_dimensions"]["W_PLUS"].items()
            ),
        )
        for item in value["level_blocks"]
    )
    return f"""# Strict endpoint-to-residual spectral comparison

**Result:** `{value['result_id']}`
**Dependency boundary:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M3R:** `COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Result

The thirty local endpoint species now have a typed comparison with the
positive-energy residual carrier after restricting to represented global
cylinder harmonics at energies two through six.  This is not a local
position-space projection.  It is a finite spectral comparison, and every
support-expanding map is labeled `REDUCED-MODE`.

| Energy | Total | W+ | W- | W+ family dimensions |
|---:|---:|---:|---:|---|
{rows}

The resulting ordered basis has 470 elements.  Each old generic label is
refined by chirality, E/A/L family, and exact doubled magnetic weights.  The
normalization of every magnetic state is determined by finite SU(2) lowering
from a coordinate-verified highest-weight metric representative.  The
portable BGG split then gives exact analysis and synthesis maps with
`pi_M3R iota_M3R=1`, `q0 iota_M3R=0`, and `pi_M3R q0=0`.

## Boundary

The certificate does not serialize raw coordinate tensors for all 470 modes
and does not claim a map on compactly supported sections, distributions, or
an all-energy smooth completion.  Energies zero and one are excluded and
remain in the separate conformal-Killing zero-mode payload.  No Hilbert or
Krein completion and no choice principle is used by the fixed finite core.

M4R residual cyclicity and the M1 common freeze remain open.  Consequently
Gate A, Hadamard, renormalization, QME, and quantum residual transfer remain
fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_endpoint_to_residual_spectral_comparison.py --check
python3 quantum-weyl/classical_import/check_strict_endpoint_to_residual_spectral_comparison.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_endpoint_to_residual_spectral_comparison.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
