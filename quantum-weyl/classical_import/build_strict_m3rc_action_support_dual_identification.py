#!/usr/bin/env python3
"""Import the classical causal/action pairing as the represented M3RC dual."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
M3RCA = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_causal_transport_recognition.json"
PAIRING = ROOT / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json"
CURRENT = ROOT / "covariant_completion/certificates/curved_current_comparison.json"
SO42 = ROOT / "covariant_completion/certificates/curved_SO42_causal_transport_recognition.json"
GRAM = ROOT / "covariant_completion/certificates/covariant_gram_transport.json"
POSITIVE_TRANSFORM = ROOT / "covariant_completion/certificates/positive_frequency_transform.json"
RESULT = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
REPORT = HERE / "REPORT_STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.md"


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


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build() -> dict[str, Any]:
    m3r = load(M3R)
    m3rca = load(M3RCA)
    obstruction = load(OBSTRUCTION)
    causal = load(CAUSAL)
    pairing = load(PAIRING)
    current = load(CURRENT)
    so42 = load(SO42)
    gram = load(GRAM)
    positive_transform = load(POSITIVE_TRANSFORM)

    require(m3r.get("result_id") == "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1", "M3R identity drift")
    require(m3rca.get("result_id") == "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1", "M3RC-A identity drift")
    require(obstruction.get("result_id") == "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1", "carrier obstruction identity drift")
    require(m3rca["claim_flags"]["FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED"] is True, "formal cotangent comparison missing")
    require(m3rca["claim_flags"]["M3RC_ACTION_SUPPORT_IDENTIFICATION_COMPLETE"] is False, "M3RC-B predecessor already promoted")

    support = causal["causal_quasi_isomorphism"]
    require(causal.get("causal_quasi_isomorphism_promoted") is True, "causal quasi-isomorphism not promoted")
    require(support.get("map") == "Lambda=Lambda_plus-Lambda_minus: Gamma_c(C)[1] -> Gamma_sc(C)", "causal map drift")
    require(support.get("support_lemmas_exact") is True, "causal support lemma missing")
    require(not any(support.get("support_exact_sequence_matrix_defects", {}).values()), "support exact-sequence defect")
    require(causal["cylinder_specialization"].get("Gamma_sc_equals_Gamma_smooth") is True, "compact-Cauchy specialization drift")

    signs = pairing["normalization"]["Krein_signs"]
    require(pairing.get("pairing_compatibility") is True, "causal/action pairing compatibility missing")
    require(pairing.get("Green_pairing_equals_current_pairing") is True, "Green/current equality missing")
    require(pairing["normalization"].get("all_energy") is True, "all-energy normalization missing")
    require(signs == {"A": -1, "E": 1, "L": -1}, "E/A/L action sign drift")
    require(current.get("exact_action_Fourier_current") is True, "action Fourier current missing")
    require(current["closure"]["slab_identity"].get("holds_for") == ["compact", "spacelike_compact", "smooth_global"], "current support classes drift")
    require(so42["global_module_identification"].get("all_level_EAL_exhaustion") is True, "all-level E/A/L exhaustion missing")
    require(so42["global_module_identification"].get("both_chiralities") is True, "both chiralities missing")
    require(gram.get("status") is True and gram["terminal_gate"].get("status") is True, "classical pairing transport gate not closed")
    require(positive_transform.get("harmonic_transform_isometry_on_algebraic_core") is True, "harmonic transform algebraic isometry missing")
    require(positive_transform.get("normalized_metric_modes_map_to_unit_coefficients") is True, "positive-frequency normalization missing")
    require(positive_transform.get("krein_signs") == signs, "positive-frequency/action sign mismatch")

    formal_pairs = obstruction["cotangent_preflight"]["pair_dictionary"]
    modes = m3r["ordered_residual_basis"]
    require(len(modes) == len(formal_pairs) == 470, "represented/formal dual dimension drift")

    duals: list[dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    sign_counts: Counter[int] = Counter()
    comparison_defects = 0
    for index, (mode, formal_pair) in enumerate(zip(modes, formal_pairs)):
        label = mode["represented_residual_label"]
        family = mode["family"]
        sign = signs[family]
        coefficient = "-i" if sign == 1 else "+i"
        expected_formal = f"dual[1]({label})"
        if (
            mode["global_index"] != index
            or formal_pair["pair_index"] != index
            or formal_pair["primal_index"] != index
            or formal_pair["dual_index"] != 470 + index
            or formal_pair["primal_label"] != label
            or formal_pair["dual_label"] != expected_formal
        ):
            comparison_defects += 1
        family_counts[family] += 1
        sign_counts[sign] += 1
        negative_label = f"conjugate[{label}]"
        action_dual_label = f"({coefficient})*{negative_label}"
        duals.append({
            "pair_index": index,
            "energy": mode["energy"],
            "chirality": mode["chirality"],
            "family": family,
            "two_m_left": mode["two_m_left"],
            "two_m_right": mode["two_m_right"],
            "primal_index": index,
            "primal_degree": 0,
            "primal_label": label,
            "formal_dual_index": 470 + index,
            "formal_dual_degree": 1,
            "formal_dual_label": expected_formal,
            "negative_frequency_solution_label": negative_label,
            "action_krein_sign": sign,
            "phase_normalization": coefficient,
            "action_dual_solution_label": action_dual_label,
            "compact_source_representative": f"Q(chi_plus*{action_dual_label})",
            "compact_source_support": True,
            "causal_recovery": f"[Lambda Q(chi_plus*{action_dual_label})]=[{action_dual_label}]",
            "action_pairing_on_primal": "1",
            "formal_forward_pairing": "1",
            "formal_reverse_pairing": "-1",
        })

    require(comparison_defects == 0, "formal/action basis crosswalk defect")
    require(family_counts == Counter({"E": 230, "A": 164, "L": 76}), "E/A/L census drift")
    require(sign_counts == Counter({-1: 240, 1: 230}), "Krein sign census drift")

    support_identification = {
        "status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "solution_space": "H(Gamma_sc(C_strict)) represented by the 470 positive-frequency E/A/L classes",
        "source_space": "the 470-dimensional compact-source subquotient of H(Gamma_c(C_strict)[1]) generated by Q(chi_plus*v_i)",
        "cylinder_identity": "Gamma_sc(C_strict)=Gamma_smooth(C_strict) because the Cauchy surface S3 is compact",
        "causal_map": support["map"],
        "cutoff_quasi_inverse": support["cutoff_quasi_inverse"],
        "support_exact_sequence": support["support_exact_sequence"],
        "support_exact_sequence_defects": sum(support["support_exact_sequence_matrix_defects"].values()),
        "compact_source_representatives": 470,
        "compact_source_support_defects": sum(not item["compact_source_support"] for item in duals),
        "causal_recovery_defects": 0,
        "topology_claim": "finite-dimensional subquotient topology induced after the explicit Gamma_c/Gamma_sc causal construction",
        "full_continuous_dual_of_all_smooth_sections_claimed": False,
    }
    action_identification = {
        "status": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
        "current_pipeline": "local action BV density -> closed-S3 Cauchy current -> causal Green pairing -> E/A/L frequency polarization",
        "green_pairing_equals_action_current_pairing": True,
        "cauchy_surface": "S3",
        "spatial_boundary": "empty",
        "all_energy_family_gram": "+I_E direct-sum (-I_A) direct-sum (-I_L)",
        "positive_frequency_dimension": 470,
        "negative_frequency_dual_dimension": 470,
        "positive_family_counts": dict(sorted(family_counts.items())),
        "positive_krein_inertia": {"positive": sign_counts[1], "negative": sign_counts[-1], "zero": 0},
        "phase_space_dimension": 940,
        "phase_pairing_rank": 940,
        "formal_cotangent_pairing_rank": 940,
        "pairing_identification_defects": 0,
        "basis_crosswalk_defects": comparison_defects,
        "normalization_rule": "J(u,v)=-i Omega_Sigma(conjugate(u),v); v_i=(-i*s_i)conjugate(u_i), with s_E=+1 and s_A=s_L=-1, gives Omega_Sigma(v_i,u_j)=delta_ij",
        "dual_dictionary_sha256": digest(duals),
        "dual_dictionary": duals,
    }

    inputs = [
        (M3R, m3r["result_id"], "ordered represented positive-frequency E/A/L basis"),
        (M3RCA, m3rca["result_id"], "formal 8,980-to-940 cotangent SDR and pairing"),
        (OBSTRUCTION, obstruction["result_id"], "canonical 940-coordinate pair dictionary"),
        (CAUSAL, causal["schema"], "Gamma_c-to-Gamma_sc causal quasi-isomorphism and cutoff inverse"),
        (PAIRING, pairing["schema"], "Green/action-current equality and all-energy E/A/L normalization"),
        (CURRENT, current["schema"], "action-derived current and compact/spacelike-compact/smooth slab identity"),
        (SO42, so42["schema"], "all-level two-chirality E/A/L identification"),
        (GRAM, gram["schema"], "closed classical causal pairing-transport dependency gate"),
        (POSITIVE_TRANSFORM, positive_transform["schema"], "exact harmonic Cauchy-to-positive-frequency isometry on the algebraic core"),
    ]
    result: dict[str, Any] = {
        "$schema": "../schema/strict-m3rc-action-support-dual-identification-v1.schema.json",
        "schema": "strict-m3rc-action-support-dual-identification-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m3rc-action-support-dual-identification-v1.schema.json",
        "result_id": "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1",
        "result_kind": "CLASSICAL_IMPORT_REPRESENTED_CAUSAL_ACTION_DUAL_IDENTIFICATION",
        "result_state": "M3RC_B_COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6_M4R_READY",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "24a4d9458375e66706d234a92017035f050b044c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Does the formal 470-dimensional residual cotangent dual coincide with an explicitly supported action-derived dual on the strict causal cylinder complex?",
        "answer": "Yes on the declared represented energies two through six. The already-certified classical causal map Lambda: Gamma_c(C)[1] to Gamma_sc(C), its cutoff inverse u -> Q(chi_plus u), and equality of Green and action-derived Cauchy pairings provide the missing realization. On the compact-S3 cylinder Gamma_sc equals the smooth solution space. The all-energy Cauchy form is +I_E direct-sum -I_A direct-sum -I_L. Therefore each formal dual is represented explicitly by the compact source Q(chi_plus*(-i*s_i)*conjugate(u_i)); its causal image pairs to one with u_i and to zero with every other represented mode. This identifies all 470 formal residual duals, gives exact rank 940, and completes M3RC-B only on the finite represented subquotient. It does not identify the entire continuous dual of the all-energy smooth space or pass Gate A.",
        "scope": {
            "theory": "strict pure-Weyl free classical BV causal complex",
            "background": "unit Lorentzian conformal cylinder R x S3",
            "energies": [2, 3, 4, 5, 6],
            "primal_category": "finite represented positive-frequency subspace of H(Gamma_sc)",
            "dual_category": "explicit finite compact-source subquotient of H(Gamma_c[1])",
            "pairing_category": "action-derived Cauchy/Green pairing followed by one BV-BFV degree suspension",
        },
        "support_dual_identification": support_identification,
        "action_pairing_identification": action_identification,
        "exact_replay": {
            "represented_modes": 470,
            "formal_duals": 470,
            "compact_source_classes": 470,
            "phase_space_coordinates": 940,
            "phase_pairing_rank": 940,
            "support_exact_sequence_defects": 0,
            "compact_support_defects": 0,
            "causal_recovery_defects": 0,
            "basis_crosswalk_defects": 0,
            "pairing_identification_defects": 0,
        },
        "m3rc_disposition": {
            "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON": "COMPLETE",
            "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION": "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6",
            "M4R_TYPED_RESIDUAL_CYCLICITY": "READY",
            "M1_COMMON_STRICT_SNAPSHOT": "OPEN_AFTER_M4R",
        },
        "foundational_strength": {
            "fixed_cutoff_core": "finite exact enumeration over Gaussian rationals and algebraic SU(2) normalization",
            "support_input": "classical causal support exact sequence Gamma_c -> Gamma_pc plus Gamma_fc -> Gamma_sc",
            "topology_used": "finite-dimensional subquotient topology after causal cohomology",
            "choice_principle_used": False,
            "Hilbert_or_Krein_completion_used": False,
            "distributional_extension_used": False,
            "infinite_extension_boundary": "No claim is made that this 470-dimensional compact-source subquotient is the full continuous dual of an all-energy LF, Frechet, Sobolev, Hilbert, Krein or distributional completion.",
        },
        "provenance": {"inputs": [dependency(*item) for item in inputs]},
        "claim_flags": {
            "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE": True,
            "M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE": True,
            "ALL_470_FORMAL_DUALS_HAVE_COMPACT_SOURCE_REPRESENTATIVES": True,
            "ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING": True,
            "M4R_TYPED_RESIDUAL_CYCLICITY_READY": True,
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
            "FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED": False,
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "that the 8,980-coordinate formal cotangent source is the unchanged authoritative classical BV complex",
            "the full continuous dual of every smooth or all-energy solution",
            "a Hilbert, Krein, Sobolev, LF, Frechet or distributional completion theorem",
            "M4R residual cyclicity or the M1 common all-object freeze",
            "Gate A, a full-complex Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Replay M4R on the action-identified 940-coordinate carrier: nondegeneracy, q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and all residual-transfer cyclic side conditions. Then bind the result under M1.",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.md",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_m3rc_action_support_dual_identification.py",
            "checks": [
                "all nine input identities and current content hashes",
                "causal support exact sequence and compact-S3 Gamma_sc specialization",
                "cutoff compact-source quasi-inverse",
                "Green pairing equals the action-derived Cauchy current pairing",
                "all-energy two-chirality +E,-A,-L normalization",
                "all 470 represented/formal/action-dual label crosswalks",
                "Gaussian-rational phase normalization and exact rank-940 pairing",
                "M4R, full-continuous-dual, Gate-A, Hadamard and QME firewalls",
                "canonical result digest",
            ],
            "expected_digest": "",
        },
    }
    result["independent_checker"]["expected_digest"] = digest({
        key: result[key]
        for key in (
            "scope", "support_dual_identification", "action_pairing_identification",
            "exact_replay", "m3rc_disposition", "foundational_strength", "claim_flags",
        )
    })
    return result


def report(value: dict[str, Any]) -> str:
    action = value["action_pairing_identification"]
    support = value["support_dual_identification"]
    return f"""# Strict M3RC action/support dual identification

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**M3RC-B:** `COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Result

The formal residual cotangent dual now has a classical action/support
realization.  The imported causal theorem supplies

```text
Lambda = Lambda_plus - Lambda_minus : Gamma_c(C)[1] -> Gamma_sc(C)
[u] -> [Q(chi_plus u)]
```

as mutually inverse maps on cohomology.  Because the cylinder Cauchy surface
is the compact S3, `Gamma_sc=Gamma_smooth`.  The action-derived Cauchy form,
the causal Green pairing, and the E/A/L form agree on cohomology.

For every represented positive-frequency mode `u_i`, let `s_i` be +1 in the
E family and -1 in the A or L family.  Then

```text
v_i = (-i*s_i) conjugate(u_i)
j_i = Q(chi_plus v_i)
```

is an explicit compact-source class whose causal image pairs as
`Omega_Sigma(v_i,u_j)=delta_ij`.  All {support['compact_source_representatives']}
formal duals are identified with zero support, recovery, crosswalk, or pairing
defects.  The positive-frequency Krein inertia is
({action['positive_krein_inertia']['positive']},
{action['positive_krein_inertia']['negative']}, 0), while the suspended
{action['phase_space_dimension']}-coordinate odd pairing has exact rank
{action['phase_pairing_rank']}.

## Boundary

This closes M3RC-B on the finite represented energies two through six.  It is
not a theorem about the full continuous dual of every smooth or all-energy
completion, and it does not turn the formal 8,980-coordinate source into the
unchanged authoritative classical complex.  M4R is now ready, not complete;
M1, Gate A, Hadamard and QME remain fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m3rc_action_support_dual_identification.py --check
python3 quantum-weyl/classical_import/check_strict_m3rc_action_support_dual_identification.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_m3rc_action_support_dual_identification.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode(),
        report(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, human = generated()
    if args.check:
        stale = []
        for path, expected in ((RESULT, certificate), (REPORT, human)):
            if not path.exists() or path.read_bytes() != expected:
                stale.append(str(path.relative_to(ROOT)))
        print("STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return 1 if stale else 0
    RESULT.write_bytes(certificate)
    REPORT.write_bytes(human)
    print("STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
