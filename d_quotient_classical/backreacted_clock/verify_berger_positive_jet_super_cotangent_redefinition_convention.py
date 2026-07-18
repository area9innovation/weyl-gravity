#!/usr/bin/env python3
"""Independent verifier for the positive-jet cotangent convention."""

from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as result,
)


def main() -> None:
    value = json.loads(result.OUTPUT.read_text())
    result.validate(value)
    replay = value["scientific_replay"]
    zero = replay["zero_word_restriction"]
    controls = replay["positive_jet_controls"]
    if zero["defects"] != 0:
        raise ValueError("zero-word restriction has defects")
    if not controls["first_jet_fixture"]["formal_adjoint_sign_mutation_changed_dual"]:
        raise ValueError("first-jet mutation is insensitive")
    if not controls["noncommuting_second_jet_fixture"]["order_one_commutator_tail_present"]:
        raise ValueError("second-jet PBW commutator tail is absent")
    print("BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1: VERIFIED")


if __name__ == "__main__":
    main()
