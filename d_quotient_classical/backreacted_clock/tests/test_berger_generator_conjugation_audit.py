from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import berger_generator_conjugation_audit as audit


def test_generator_conjugation_builds() -> None:
    payload = audit.build()
    assert payload["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"] is True
    assert payload["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"] is False
    assert payload["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"] is True


def test_generator_conjugation_matches_frozen_certificate() -> None:
    payload = audit.build()
    assert json.loads(audit.CERTIFICATE_PATH.read_text()) == payload


def test_generator_conjugation_guards() -> None:
    audit._guards(audit.build())
