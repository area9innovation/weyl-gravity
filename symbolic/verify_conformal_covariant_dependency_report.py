#!/usr/bin/env python3
"""Generate and guard the fail-closed final covariant claim dependency DAG."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.dependencies import FinalClaimDependencyReport
from covariant_completion.dependencies.final_claims import (
    direct_causal_pairing_certificate_passes,
    so42_authoritative_certificate_passes,
)


CERTIFICATE = ROOT / "covariant_completion" / "certificates" / "final_claim_dependencies.json"
MARKDOWN = ROOT / "covariant_completion" / "generated" / "final_claim_dependencies.md"


CLAIM_FLAGS = {
    "claim_curved_operator": "curved_operator_identity",
    "claim_curved_retract": "curved_deformation_retract",
    "claim_curved_current": "curved_current_comparison",
    "claim_complete_green_hyperbolicity": "complete_bv_green_hyperbolicity",
    "claim_final_covariant_h4": "final_covariant_H4",
}

EXPECTED_FINAL_REQUIREMENTS = (
    "curved_operator_identity",
    "curved_deformation_retract",
    "curved_current_comparison",
    "scalar_wave_witness_no_go",
    "weyl_symbol_helicity_isomorphism",
    "curved_EB_equations",
    "curved_EB_first_order_closure",
    "curved_EB_symmetric_hyperbolicity",
    "curved_sourced_constraint_identity",
    "curved_constraint_propagation",
    "EAL_curvature_spectrum_match",
    "support_local_prolongation_retract",
    "prolonged_BV_operator_identity",
    "direct_tractor_causal_homotopy",
    "causal_green_homotopy",
    "causal_quasi_isomorphism",
    "residual_endpoint_recovery",
    "SO42_equivariant_transport",
    "prolonged_current_comparison",
    "direct_causal_pairing_transport",
    "pairing_compatibility",
    "residual_H4_is_C2",
    "residual_gram_is_I2",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-curved-operator", action="store_true")
    parser.add_argument("--claim-curved-retract", action="store_true")
    parser.add_argument("--claim-curved-current", action="store_true")
    parser.add_argument("--claim-complete-green-hyperbolicity", action="store_true")
    parser.add_argument("--claim-final-covariant-h4", action="store_true")
    args = parser.parse_args()

    report = FinalClaimDependencyReport.build()
    for argument_name, claim_name in CLAIM_FLAGS.items():
        if not getattr(args, argument_name):
            continue
        claim = report.nodes[claim_name]
        if not claim.status:
            blockers = report.certificate()["claims"][claim_name][
                "blocking_dependencies"
            ]
            raise SystemExit(
                f"REFUSED: {claim_name} is false; blocking atomic dependencies: "
                + ", ".join(blockers)
            )
        print(f"CERTIFIED: {claim_name}")

    if args.emit:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        MARKDOWN.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(
            json.dumps(report.certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MARKDOWN.write_text(report.markdown(), encoding="utf-8")
        print("wrote", CERTIFICATE.relative_to(ROOT))
        print("wrote", MARKDOWN.relative_to(ROOT))

    if args.guards:
        certificate = report.certificate()
        for name, node in report.nodes.items():
            dependency_statuses = [
                report.nodes[dependency].status for dependency in node.requires
            ]
            expected = (
                all(dependency_statuses)
                if node.dependency_mode == "all"
                else any(dependency_statuses)
            )
            if node.requires and node.status != expected:
                raise AssertionError(
                    f"derived claim {name} does not implement dependency mode "
                    f"{node.dependency_mode!r}"
                )
            blockers = certificate["claims"][name]["blocking_dependencies"]
            if node.status and blockers:
                raise AssertionError(f"true claim {name} still reports blockers")
        final = report.nodes["final_covariant_H4"]
        if final.requires != EXPECTED_FINAL_REQUIREMENTS:
            raise AssertionError(
                "final_covariant_H4 does not implement the expanded causal bridge"
            )
        if bool(certificate["final_claim_atomic_blockers"]) == bool(final.status):
            raise AssertionError(
                "final atomic blockers must be present exactly while the theorem is false"
            )
        if not report.nodes["residual_H4_is_C2"].status:
            raise AssertionError("the certified residual H4 input regressed")
        if not report.nodes["residual_gram_is_I2"].status:
            raise AssertionError("the certified residual Gram input regressed")
        direct_path = (
            ROOT
            / "covariant_completion"
            / "certificates"
            / "curved_direct_causal_pairing_transport.json"
        )
        direct = json.loads(direct_path.read_text(encoding="utf-8"))
        if not direct_causal_pairing_certificate_passes(direct):
            raise AssertionError("authoritative direct pairing receipt regressed")
        if direct_causal_pairing_certificate_passes({}):
            raise AssertionError("missing direct pairing receipt was recognized")
        mutations = []
        for path, value in (
            (("schema",), "forged-schema"),
            (("dependency_tag",), "REDUCED-MODE"),
            (("fail_closed",), False),
            (("input_certificate_sha256", "curved_pbw"), "0" * 64),
            (("pairing_compatibility",), False),
            (("fail_closed_guards", "manual_final_H4_promotion_rejected"), False),
        ):
            forged = deepcopy(direct)
            cursor = forged
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            mutations.append(forged)
        if any(direct_causal_pairing_certificate_passes(item) for item in mutations):
            raise AssertionError("forged direct pairing receipt was recognized")
        if "direct_causal_pairing_transport" not in final.requires:
            raise AssertionError("terminal gate omits direct causal pairing")
        if "pairing_compatibility" not in final.requires:
            raise AssertionError("terminal gate omits pairing compatibility")
        if all(
            False if name == "direct_causal_pairing_transport" else report.nodes[name].status
            for name in final.requires
        ):
            raise AssertionError("missing direct pairing receipt did not block terminal promotion")
        so42_path = (
            ROOT
            / "covariant_completion"
            / "certificates"
            / "curved_SO42_causal_transport_recognition.json"
        )
        so42 = json.loads(so42_path.read_text(encoding="utf-8"))
        if not so42_authoritative_certificate_passes(so42):
            raise AssertionError("authoritative SO(4,2) receipt regressed")
        forged_so42 = deepcopy(so42)
        forged_so42["input_certificate_sha256"]["raw_bv_transfer"] = "0" * 64
        if so42_authoritative_certificate_passes(forged_so42):
            raise AssertionError("forged SO(4,2) input hash was recognized")
        if not report.nodes["SO42_equivariant_transport"].status:
            raise AssertionError("SHA-bound SO(4,2) terminal atom regressed")
        if all(
            False if name == "SO42_equivariant_transport" else report.nodes[name].status
            for name in final.requires
        ):
            raise AssertionError("forged SO(4,2) receipt did not block terminal promotion")
        print("COVARIANT CLAIM DEPENDENCY GUARDS: 22/22 PASS")

    print("COVARIANT FINAL CLAIM DEPENDENCY REPORT: ALL LOGIC CHECKS PASS")


if __name__ == "__main__":
    main()
