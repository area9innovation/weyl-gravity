#!/usr/bin/env python3
"""Emit and mutation-test conditional SO(4,2) causal transport."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.final_transport.equivariant_transport import (
    INPUT_DIGEST_KEYS,
    SO42CausalTransportRecognition,
    _certificate_digest,
    cutoff_equivariance_defect,
    recognition_certificate_passes,
)


CERT = ROOT / "covariant_completion" / "certificates"
BRIDGE = ROOT / "bridge" / "certificates"
OUTPUT = CERT / "curved_SO42_causal_transport_recognition.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a certificate object")
    return value


def _build(**overrides: dict[str, object]) -> SO42CausalTransportRecognition:
    values = {
        "causal_transport": _load(CERT / "curved_causal_transport_recognition.json"),
        "auxiliary_retract": _load(CERT / "curved_auxiliary_canonical_split.json"),
        "curvature_mapping_cylinder": _load(
            CERT / "curved_curvature_mapping_cylinder_substitution.json"
        ),
        "curvature_causal_pde": _load(
            CERT / "curved_weyl_cotton_causal_pde.json"
        ),
        "raw_bv_transfer": _load(BRIDGE / "raw_bv_transfer.json"),
        "bgg_blocks": _load(BRIDGE / "cylinder_bgg_blocks.json"),
        "metric_preimages": _load(BRIDGE / "cylinder_metric_preimages.json"),
        "eal_spectrum": _load(CERT / "curved_EAL_spectrum_all_level.json"),
    }
    values.update(overrides)
    return SO42CausalTransportRecognition(**values)


def _rejects(**overrides: dict[str, object]) -> bool:
    try:
        _build(**overrides).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    proof = _build()
    certificate = proof.certificate()
    expected_input_sha256 = {
        "actual_causal_quasi_isomorphism": _certificate_digest(
            proof.causal_transport
        ),
        "auxiliary_retract": _certificate_digest(proof.auxiliary_retract),
        "curvature_mapping_cylinder": _certificate_digest(
            proof.curvature_mapping_cylinder
        ),
        "curvature_causal_pde": _certificate_digest(proof.curvature_causal_pde),
        "raw_bv_transfer": _certificate_digest(proof.raw_bv_transfer),
        "cylinder_bgg_blocks": _certificate_digest(proof.bgg_blocks),
        "cylinder_metric_preimages": _certificate_digest(proof.metric_preimages),
        "curvature_EAL_spectrum": _certificate_digest(proof.eal_spectrum),
    }
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    checks = {
        "formal_cutoff_defect_zero": cutoff_equivariance_defect() == {},
        "conditional_recognition_exact": recognition_certificate_passes(
            certificate,
            expected_input_sha256=expected_input_sha256,
        ),
        "all_checked_inputs_content_bound": (
            certificate["input_certificate_sha256"] == expected_input_sha256
            and tuple(sorted(expected_input_sha256))
            == tuple(sorted(INPUT_DIGEST_KEYS))
        ),
        "causal_input_required": certificate["conditional_theorem"][
            "requires_causal_quasi_isomorphism"
        ],
        "actual_causal_input_bound": certificate["conditional_theorem"][
            "actual_causal_quasi_isomorphism_bound"
        ],
        "Cauchy_split_not_claimed_strict": certificate["promotion_boundary"][
            "does_not_claim_strict_Cauchy_split"
        ],
        "pairing_transport_not_claimed": certificate["promotion_boundary"][
            "does_not_claim_pairing_transport"
        ],
    }
    if args.guards:
        causal = _load(CERT / "curved_causal_transport_recognition.json")
        bad = deepcopy(causal)
        bad["cylinder_specialization"]["Gamma_sc_equals_Gamma_smooth"] = False
        checks["noncompact_cauchy_surface_rejected"] = _rejects(causal_transport=bad)
        bad = deepcopy(causal)
        bad["actual_causal_input"]["causal_green_homotopy"] = False
        checks["missing_actual_causal_homotopy_rejected"] = _rejects(
            causal_transport=bad
        )

        auxiliary = _load(CERT / "curved_auxiliary_canonical_split.json")
        bad = deepcopy(auxiliary)
        bad["auxiliary_eom_shift"]["uses_nonlocal_projector"] = True
        checks["nonlocal_auxiliary_retract_rejected"] = _rejects(auxiliary_retract=bad)

        mapping = _load(CERT / "curved_curvature_mapping_cylinder_substitution.json")
        bad = deepcopy(mapping)
        bad["kernel"]["I_P_minus_identity"] = "unproved"
        checks["broken_mapping_SDR_rejected"] = _rejects(
            curvature_mapping_cylinder=bad
        )

        pde = _load(CERT / "curved_weyl_cotton_causal_pde.json")
        bad = deepcopy(pde)
        bad["exact_covariant_curvature_system"]["smooth_solution_spaces_equal"] = False
        checks["nonequivalent_first_order_state_rejected"] = _rejects(
            curvature_causal_pde=bad
        )

        raw = _load(BRIDGE / "raw_bv_transfer.json")
        bad = deepcopy(raw)
        bad["induced_result"] = "vector-space action only"
        checks["nonequivariant_raw_transfer_rejected"] = _rejects(raw_bv_transfer=bad)

        bgg = _load(BRIDGE / "cylinder_bgg_blocks.json")
        bad = deepcopy(bgg)
        bad["external_theorem_dependency"] = "missing"
        checks["missing_global_BGG_rejected"] = _rejects(bgg_blocks=bad)

        eal = _load(CERT / "curved_EAL_spectrum_all_level.json")
        bad = deepcopy(eal)
        bad["all_level_not_finite_cutoff"] = False
        checks["finite_EAL_cutoff_rejected"] = _rejects(eal_spectrum=bad)

        for section, key, value in (
            ("cutoff_homotopy", "formal_defect", 1),
            ("conditional_theorem", "actual_causal_quasi_isomorphism_bound", False),
            ("cutoff_homotopy", "homotopy_support_compact", False),
            ("global_module_identification", "smooth_global_BGG_equivariant", False),
            ("residual_action", "strict_so42_action_on_cohomology", False),
            ("promotion_boundary", "does_not_claim_pairing_transport", False),
        ):
            broken = deepcopy(certificate)
            broken[section][key] = value
            checks[f"broken_output_{key}_rejected"] = not (
                recognition_certificate_passes(
                    broken,
                    expected_input_sha256=expected_input_sha256,
                )
            )

        for input_name in INPUT_DIGEST_KEYS:
            broken = deepcopy(certificate)
            broken["input_certificate_sha256"][input_name] = "0" * 64
            checks[f"mutated_input_hash_{input_name}_rejected"] = not (
                recognition_certificate_passes(
                    broken,
                    expected_input_sha256=expected_input_sha256,
                )
            )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("SO(4,2) causal transport failed: " + ", ".join(failed))
    if args.guards:
        print(f"SO42 CAUSAL TRANSPORT GUARDS: {len(checks)}/{len(checks)} PASS")
    print("SO42 CAUSAL TRANSPORT: EXACT CONDITIONAL RECOGNITION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
