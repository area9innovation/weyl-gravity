#!/usr/bin/env python3
import json

from closed_universe_observers.generate_berger_recoil_detector_form_binding import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["flags"]["EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE"]
    assert value["flags"]["PHYSICAL_TIME_DERIVATIVE_TAIL_BOUND_EXPORTED"]
    assert not value["flags"]["ADVANCED_MASSIVE_TWO_FORM_IMAGE_EVALUATED"]
    print("Berger recoil detector/form binding verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
