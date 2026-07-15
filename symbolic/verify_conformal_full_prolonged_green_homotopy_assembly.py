#!/usr/bin/env python3
"""Verify the conditional 356+30 full causal homotopy assembly."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.full_prolonged_green_homotopy_assembly import (
    FullProlongedGreenHomotopyAssembly,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"
OUTPUT = CERTIFICATES / "curved_full_prolonged_green_homotopy_assembly.json"
REPORT = GENERATED / "curved_full_prolonged_green_homotopy_assembly.md"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a JSON object")
    return value


def _rejects(action) -> bool:
    try:
        action()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument(
        "--green-transfer",
        type=Path,
        help="optional regenerated adjoint-tractor transfer certificate",
    )
    args = parser.parse_args()

    hybrid = _load("curved_prolonged_hybrid_algebraic_projector.json")
    endpoint = _load("curved_prolonged_metric_endpoint_complex.json")
    backward = _load("curved_prolonged_metric_endpoint_backward_witness.json")
    filtration = _load("curved_endpoint_green_filtration_boundary.json")
    chain_maps = _load("curved_chain_maps.json")
    if args.green_transfer is None:
        transfer = _load("adjoint_tractor_green_transfer.json")
    else:
        transfer = json.loads(args.green_transfer.read_text(encoding="utf-8"))
        if not isinstance(transfer, dict):
            raise AssertionError("green transfer certificate is not an object")

    theorem = FullProlongedGreenHomotopyAssembly.build()
    certificate = theorem.certificate(
        hybrid_certificate=hybrid,
        endpoint_certificate=endpoint,
        backward_witness_certificate=backward,
        filtration_certificate=filtration,
        curved_chain_maps_certificate=chain_maps,
        green_transfer_certificate=transfer,
    )

    channels = certificate["endpoint_channel_assembly"]
    full = certificate["full_hybrid_assembly"]
    gate = certificate["future_gate"]
    checks = {
        "dimension split exact": certificate["dimension_ledger"]["identity"]
        == "386=356+30",
        "endpoint triangular homotopy algebra exact": channels[
            "homotopy_identity_exact_conditionally"
        ]
        is True,
        "endpoint easy-channel inverses exact": channels[
            "easy_channel_same_sided_inverses_exact"
        ]
        is True
        and channels["finite_triangular_chain_extension"] is True,
        "explicit trace/Weyl shear exact": all(
            channels["explicit_trace_Weyl_shear"][key] is True
            for key in (
                "inverse_checks_exact",
                "q_U_equals_U_q_split",
                "cyclic_U_sharp_equals_U_inverse",
            )
        )
        and channels["explicit_trace_Weyl_shear"]["trace_qh_plus_hq"]
        == "identity_4",
        "no unsupported canonical endpoint inverse": channels[
            "canonical_D_TF_inverse_claimed"
        ]
        is False
        and channels["global_W0_G_end_identification_claimed"] is False,
        "full hybrid homotopy algebra exact": full[
            "algebraic_identity_exact_conditionally"
        ]
        is True,
        "full causal support transfer exact": full[
            "causal_support_exact_conditionally"
        ]
        is True
        and "finite-order local" in full["support"],
        "full graded adjoint transfer exact": full[
            "graded_adjoint_exact_conditionally"
        ]
        is True,
        "actual transfer gate controls full status": certificate[
            "causal_green_homotopy"
        ]
        is gate["upstream_green_transfer_ready"]
        and certificate["status_flags_promoted"]
        == (
            ["causal_green_homotopy"]
            if gate["upstream_green_transfer_ready"]
            else []
        ),
        "no witness overpromotion": certificate["prolonged_green_witness"]
        is False
        and certificate["curvature_causal_green_operators"] is False,
    }

    if args.guards:
        bad_hybrid = deepcopy(hybrid)
        bad_hybrid["composite_SDR"]["P_alg_idempotent"] = False
        checks["broken hybrid projector rejected"] = _rejects(
            lambda: theorem.certificate(
                hybrid_certificate=bad_hybrid,
                endpoint_certificate=endpoint,
                backward_witness_certificate=backward,
                filtration_certificate=filtration,
                curved_chain_maps_certificate=chain_maps,
                green_transfer_certificate=transfer,
            )
        )

        bad_filtration = deepcopy(filtration)
        bad_filtration["ghost_channel"]["right_inverse"] = False
        checks["one-sided ghost inverse rejected"] = _rejects(
            lambda: theorem.certificate(
                hybrid_certificate=hybrid,
                endpoint_certificate=endpoint,
                backward_witness_certificate=backward,
                filtration_certificate=bad_filtration,
                curved_chain_maps_certificate=chain_maps,
                green_transfer_certificate=transfer,
            )
        )

        bad_chain_maps = deepcopy(chain_maps)
        for item in bad_chain_maps["row_ledger"]["reattached_direct_summands"]:
            if item["name"] == "trace/Weyl doublet and antifield dual":
                item["differential"] = "missing"
        checks["missing trace/Weyl identity rows rejected"] = _rejects(
            lambda: theorem.certificate(
                hybrid_certificate=hybrid,
                endpoint_certificate=endpoint,
                backward_witness_certificate=backward,
                filtration_certificate=filtration,
                curved_chain_maps_certificate=bad_chain_maps,
                green_transfer_certificate=transfer,
            )
        )

        forged_transfer = deepcopy(transfer)
        forged_transfer["tracefree_causal_green_homotopy"] = True
        forged_transfer["endpoint_assembly"][
            "tracefree_parent_transfer_ready"
        ] = True
        forged_transfer["curved_BGG_gate"]["future_certificate_sha256"] = None
        forged_transfer["dependency_sha256"].pop("curved_bgg", None)
        checks["unbound causal transfer rejected"] = _rejects(
            lambda: theorem.certificate(
                hybrid_certificate=hybrid,
                endpoint_certificate=endpoint,
                backward_witness_certificate=backward,
                filtration_certificate=filtration,
                curved_chain_maps_certificate=chain_maps,
                green_transfer_certificate=forged_transfer,
            )
        )

        valid_transfer = deepcopy(transfer)
        fake_hash = "a" * 64
        valid_transfer["tracefree_causal_green_homotopy"] = True
        valid_transfer["curved_BGG_gate"].update(
            {
                "future_certificate_schema_valid": True,
                "all_required_keys_true": True,
                "upstream_transfer_flag_remains_false": True,
                "future_certificate_sha256": fake_hash,
            }
        )
        valid_transfer["dependency_sha256"]["curved_bgg"] = fake_hash
        valid_transfer["endpoint_assembly"].update(
            {
                "tracefree_parent_transfer_ready": True,
                "complete_30_row_endpoint_causal_homotopy": False,
            }
        )
        promoted = theorem.certificate(
            hybrid_certificate=hybrid,
            endpoint_certificate=endpoint,
            backward_witness_certificate=backward,
            filtration_certificate=filtration,
            curved_chain_maps_certificate=chain_maps,
            green_transfer_certificate=valid_transfer,
        )
        checks["authoritatively bound transfer activates full assembly"] = (
            promoted["future_gate"]["upstream_green_transfer_ready"] is True
            and promoted["causal_green_homotopy"] is True
            and promoted["status_flags_promoted"] == ["causal_green_homotopy"]
        )

    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"full prolonged assembly checks failed: {failed}")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(
            "# Full prolonged Green-homotopy assembly\n\n"
            "The exact hybrid SDR contracts 356 of 386 prolonged components "
            "locally and cyclically. The remaining 30-row endpoint combines "
            "the transferred trace-free 4--9--9--4 homotopy with the exact "
            "trace/Weyl identity contraction by a finite triangular chain "
            "isomorphism; the ghost/identity Green blocks remain independent "
            "easy-channel checks. No canonical `D_TF` inverse or global "
            "`W0 G_end` formula is asserted.\n\n"
            "The formula `Lambda_full,+/- = H_alg + i_end "
            "Lambda_end,+/- p_end` satisfies the all-row chain identity, "
            "causal support, and the graded advanced/retarded adjoint "
            "relation. "
            + (
                "The SHA-bound curved PBW transfer receipt passes, so the "
                "complete 30-row endpoint and 386-row causal homotopies are "
                "promoted.\n"
                if certificate["causal_green_homotopy"]
                else "The curved PBW transfer is absent, so the causal flag "
                "remains false.\n"
            )
        )
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {REPORT.relative_to(ROOT)}")

    if args.guards:
        for name, value in checks.items():
            print(f"{'PASS' if value else 'FAIL'}: {name}")
    print(
        "FULL PROLONGED GREEN-HOMOTOPY ASSEMBLY: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
