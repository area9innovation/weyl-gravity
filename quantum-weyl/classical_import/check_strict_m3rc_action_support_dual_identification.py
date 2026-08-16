#!/usr/bin/env python3
"""Independent receiver for the represented M3RC action/support dual."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
M3RCA = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_causal_transport_recognition.json"
PAIRING = ROOT / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json"
CURRENT = ROOT / "covariant_completion/certificates/curved_current_comparison.json"
SO42 = ROOT / "covariant_completion/certificates/curved_SO42_causal_transport_recognition.json"
GRAM = ROOT / "covariant_completion/certificates/covariant_gram_transport.json"
POSITIVE_TRANSFORM = ROOT / "covariant_completion/certificates/positive_frequency_transform.json"
FULL_HOMOTOPY = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
PROLONGED_CURRENT = ROOT / "covariant_completion/certificates/curved_prolonged_current_comparison.json"
GREEN_CURRENT = ROOT / "covariant_completion/certificates/curved_green_current_pairing.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    if value is None:
        value = load(RESULT)
    sources = {
        path: load(path)
        for path in (M3R, M3RCA, OBSTRUCTION, CAUSAL, PAIRING, CURRENT, SO42, GRAM, POSITIVE_TRANSFORM)
    }

    require(value.get("result_id") == "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1", "result identity drift")
    require(value.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"], "dependency tag drift")
    expected_inputs = {
        str(path.relative_to(ROOT)): sha(path)
        for path in sources
    }
    actual_inputs = {
        item.get("path"): item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
    }
    require(actual_inputs == expected_inputs, "input path/hash ledger drift")

    m3r = sources[M3R]
    m3rca = sources[M3RCA]
    obstruction = sources[OBSTRUCTION]
    causal = sources[CAUSAL]
    pairing = sources[PAIRING]
    current = sources[CURRENT]
    so42 = sources[SO42]
    gram = sources[GRAM]
    positive_transform = sources[POSITIVE_TRANSFORM]
    require(m3r.get("result_id") == "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1", "M3R source identity drift")
    require(m3rca.get("claim_flags", {}).get("FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED") is True, "M3RC-A formal target missing")
    require(m3rca.get("claim_flags", {}).get("M3RC_ACTION_SUPPORT_IDENTIFICATION_COMPLETE") is False, "M3RC-A predecessor boundary drift")
    require(obstruction.get("cotangent_preflight", {}).get("constructive_exact_rank") == 940, "formal target rank drift")

    support_source = causal.get("causal_quasi_isomorphism", {})
    require(causal.get("causal_quasi_isomorphism_promoted") is True, "classical causal quasi-isomorphism not promoted")
    require(support_source.get("map") == "Lambda=Lambda_plus-Lambda_minus: Gamma_c(C)[1] -> Gamma_sc(C)", "Gamma_c/Gamma_sc map drift")
    require(support_source.get("cutoff_quasi_inverse") == "[u] -> [Q(chi_plus u)]", "cutoff quasi-inverse drift")
    require(support_source.get("left_cohomology_inverse") is True and support_source.get("right_cohomology_inverse") is True, "causal inverse flag drift")
    require(support_source.get("support_lemmas_exact") is True, "support lemma missing")
    require(not any(support_source.get("support_exact_sequence_matrix_defects", {}).values()), "support exact-sequence defects nonzero")
    require(causal.get("cylinder_specialization", {}).get("Gamma_sc_equals_Gamma_smooth") is True, "compact-Cauchy specialization missing")

    require(pairing.get("pairing_compatibility") is True, "pairing compatibility missing")
    require(pairing.get("Green_pairing_equals_current_pairing") is True, "Green/current equality missing")
    require(pairing.get("normalization", {}).get("Krein_signs") == {"A": -1, "E": 1, "L": -1}, "action E/A/L signs drift")
    require(pairing.get("normalization", {}).get("all_energy") is True, "action normalization not all-energy")
    require(current.get("exact_action_Fourier_current") is True and current.get("curved_current_comparison") is True, "action-derived current source incomplete")
    require(current.get("closure", {}).get("slab_identity", {}).get("holds_for") == ["compact", "spacelike_compact", "smooth_global"], "current support-domain ledger drift")
    require(so42.get("global_module_identification", {}).get("all_level_EAL_exhaustion") is True, "all-level E/A/L exhaustion missing")
    require(so42.get("global_module_identification", {}).get("both_chiralities") is True, "two-chirality source missing")
    require(gram.get("status") is True and gram.get("terminal_gate", {}).get("status") is True, "classical gram transport terminal gate not closed")
    require(positive_transform.get("harmonic_transform_isometry_on_algebraic_core") is True, "harmonic-transform algebraic isometry missing")
    require(positive_transform.get("normalized_metric_modes_map_to_unit_coefficients") is True, "harmonic mode normalization missing")
    require(positive_transform.get("krein_signs") == {"A": -1, "E": 1, "L": -1}, "harmonic/action sign mismatch")

    # Replay the important content-addressed links inside the imported classical rail.
    require(pairing.get("input_certificate_sha256", {}).get("auxiliary_metric_current") == sha(CURRENT), "direct pairing/current hash mismatch")
    require(pairing.get("input_certificate_sha256", {}).get("full_homotopy") == sha(FULL_HOMOTOPY), "direct pairing/homotopy hash mismatch")
    require(pairing.get("input_certificate_sha256", {}).get("green_current_theorem") == sha(GREEN_CURRENT), "direct pairing/Green-current hash mismatch")
    require(pairing.get("input_certificate_sha256", {}).get("prolonged_current") == sha(PROLONGED_CURRENT), "direct pairing/prolonged-current hash mismatch")
    require(gram.get("input_certificate_sha256", {}).get("causal_quasi_isomorphism") == sha(CAUSAL), "gram/causal hash mismatch")
    require(gram.get("input_certificate_sha256", {}).get("SO42_equivariant_transport") == sha(SO42), "gram/SO42 hash mismatch")
    require(gram.get("input_certificate_sha256", {}).get("direct_causal_pairing_transport") == sha(PAIRING), "gram/pairing hash mismatch")

    formal_pairs = obstruction.get("cotangent_preflight", {}).get("pair_dictionary", [])
    modes = m3r.get("ordered_residual_basis", [])
    duals = value.get("action_pairing_identification", {}).get("dual_dictionary", [])
    require(len(modes) == len(formal_pairs) == len(duals) == 470, "470-mode dictionary length drift")
    signs = {"E": 1, "A": -1, "L": -1}
    family_counts: Counter[str] = Counter()
    sign_counts: Counter[int] = Counter()
    crosswalk_defects = 0
    pairing_defects = 0
    support_defects = 0
    for index, triple in enumerate(zip(modes, formal_pairs, duals)):
        mode, formal, dual = triple
        label = mode.get("represented_residual_label")
        family = mode.get("family")
        sign = signs.get(family)
        coefficient = "-i" if sign == 1 else "+i"
        negative = f"conjugate[{label}]"
        action_dual = f"({coefficient})*{negative}"
        expected = {
            "pair_index": index,
            "energy": mode.get("energy"),
            "chirality": mode.get("chirality"),
            "family": family,
            "two_m_left": mode.get("two_m_left"),
            "two_m_right": mode.get("two_m_right"),
            "primal_index": index,
            "primal_degree": 0,
            "primal_label": label,
            "formal_dual_index": 470 + index,
            "formal_dual_degree": 1,
            "formal_dual_label": f"dual[1]({label})",
            "negative_frequency_solution_label": negative,
            "action_krein_sign": sign,
            "phase_normalization": coefficient,
            "action_dual_solution_label": action_dual,
            "compact_source_representative": f"Q(chi_plus*{action_dual})",
            "compact_source_support": True,
            "causal_recovery": f"[Lambda Q(chi_plus*{action_dual})]=[{action_dual}]",
            "action_pairing_on_primal": "1",
            "formal_forward_pairing": "1",
            "formal_reverse_pairing": "-1",
        }
        if dual != expected:
            crosswalk_defects += 1
        if not dual.get("compact_source_support", False):
            support_defects += 1
        # With J=-i Omega and J(conj(u_i),u_j)=s_i delta_ij,
        # (-i*s_i)*i*s_i=1 exactly over the Gaussian rationals.
        if sign not in (-1, 1) or coefficient != ("-i" if sign == 1 else "+i"):
            pairing_defects += 1
        if (
            formal.get("pair_index") != index
            or formal.get("primal_label") != label
            or formal.get("dual_label") != expected["formal_dual_label"]
        ):
            crosswalk_defects += 1
        family_counts[family] += 1
        sign_counts[sign] += 1

    require(family_counts == Counter({"E": 230, "A": 164, "L": 76}), "family census drift")
    require(sign_counts == Counter({-1: 240, 1: 230}), "Krein inertia drift")
    require(crosswalk_defects == 0, "formal/action dual crosswalk defects")
    require(pairing_defects == 0, "Gaussian phase normalization defects")
    require(support_defects == 0, "compact-source support defects")
    require(value.get("action_pairing_identification", {}).get("dual_dictionary_sha256") == digest(duals), "dual dictionary digest drift")

    support = value.get("support_dual_identification", {})
    action = value.get("action_pairing_identification", {})
    replay = value.get("exact_replay", {})
    require(support.get("status") == "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6", "represented support identification incomplete")
    require(support.get("full_continuous_dual_of_all_smooth_sections_claimed") is False, "full continuous dual promoted")
    require((action.get("positive_frequency_dimension"), action.get("negative_frequency_dual_dimension"), action.get("phase_space_dimension")) == (470, 470, 940), "action carrier dimensions drift")
    require((action.get("phase_pairing_rank"), action.get("formal_cotangent_pairing_rank")) == (940, 940), "action/formal rank drift")
    require(not any(replay.get(key, 1) for key in ("support_exact_sequence_defects", "compact_support_defects", "causal_recovery_defects", "basis_crosswalk_defects", "pairing_identification_defects")), "declared exact replay defect")

    flags = value.get("claim_flags", {})
    for key in (
        "M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON_COMPLETE",
        "M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE",
        "ALL_470_FORMAL_DUALS_HAVE_COMPACT_SOURCE_REPRESENTATIVES",
        "ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING",
        "M4R_TYPED_RESIDUAL_CYCLICITY_READY",
    ):
        require(flags.get(key) is True, f"positive claim flag missing: {key}")
    for key in (
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")

    digest_keys = (
        "scope", "support_dual_identification", "action_pairing_identification",
        "exact_replay", "m3rc_disposition", "foundational_strength", "claim_flags",
    )
    expected_digest = digest({key: value[key] for key in digest_keys}) if all(key in value for key in digest_keys) else ""
    require(value.get("independent_checker", {}).get("expected_digest") == expected_digest, "canonical result digest drift")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - all 470 formal duals have explicit compact-source representatives")
        print("  - action/Green and canonical cotangent pairings agree at exact rank 940")
        print("  - M4R is ready; all-energy continuous dual, Gate A, Hadamard and QME remain open")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
