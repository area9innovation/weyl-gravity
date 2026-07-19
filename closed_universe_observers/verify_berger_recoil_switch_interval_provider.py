#!/usr/bin/env python3
import json
from closed_universe_observers.generate_berger_recoil_switch_interval_provider import CERTIFICATE, build
def main():
    value=json.loads(CERTIFICATE.read_text()); assert value==build(); assert value["flags"]["NORMALIZED_SWITCH_AND_TIME_DERIVATIVE_INTERVAL_PROVIDER_EXPORTED"]; assert not value["flags"]["SWITCH_KERNEL_CONVOLUTION_BOUND"]; print("Berger recoil switch interval provider verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
