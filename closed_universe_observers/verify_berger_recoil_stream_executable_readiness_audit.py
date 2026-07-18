#!/usr/bin/env python3
"""Verify the fail-closed Berger recoil executable-readiness audit."""

import json

from closed_universe_observers.generate_berger_recoil_stream_executable_readiness_audit import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["readiness"]["symbolic_word_ready"] is True
    assert value["readiness"]["internal_executable_stream_ready"] is False
    assert value["readiness"]["external_specialization_deferred"] is True
    assert value["readiness"]["four_scalar_stream_active"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger recoil executable-readiness audit verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
