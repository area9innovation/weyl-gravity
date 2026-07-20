#!/usr/bin/env python3
"""Independent verifier for the full-dilation covariance transport."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_full_dilation_hadamard_krein_covariance_transport import (
    DEPENDENCIES,
    transport_replay,
    validate,
)
from .berger_full_dilation_hadamard_krein_covariance_transport_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload != build_certificate():
        raise ValueError("full-dilation covariance certificate does not reproduce")
    schema = json.loads(
        (
            HERE
            / "schema/berger-full-dilation-hadamard-krein-covariance-transport-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"full-dilation covariance schema failed: {errors}")
    validate(payload)
    for name, path in DEPENDENCIES.items():
        ref = payload["dependency_refs"][name]
        if ref["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"full-dilation covariance dependency drift: {name}")
    replay = transport_replay()
    if (
        not replay["all_pass"]
        or "i E_full" not in replay["composite"]["CCR_calculation"]
    ):
        raise ValueError("independent full-dilation CCR replay failed")
    no_inverse = transport_replay(quotient_inverses=False)
    if no_inverse["checks"]["full_transport_preserves_exact_CCR"]:
        raise ValueError("quotient-inverse negative control failed")
    no_cone = transport_replay(cone_action=False)
    if no_cone["checks"]["full_transport_is_Hadamard"]:
        raise ValueError("cone-action negative control failed")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("graded-BV Hadamard overpromotion was accepted")
    return payload


def main() -> int:
    verify()
    print(
        "BERGER FULL DILATION HADAMARD KREIN COVARIANCE "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
