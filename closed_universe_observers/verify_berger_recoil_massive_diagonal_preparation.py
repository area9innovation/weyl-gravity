#!/usr/bin/env python3
import json

from closed_universe_observers.generate_berger_recoil_massive_diagonal_preparation import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["flags"]["DIAGONAL_MASSIVE_DEGREE_TWO_ADVANCED_IMAGE_AT_SUPPORT_LEFT_EXPORTED"]
    assert not value["flags"]["PHYSICAL_PROCA_TWO_FORM_GREEN_CORRECTION_EXPORTED"]
    print("Berger recoil massive diagonal preparation verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
