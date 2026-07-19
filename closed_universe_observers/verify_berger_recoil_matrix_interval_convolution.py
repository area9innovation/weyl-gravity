#!/usr/bin/env python3
import json
from closed_universe_observers.generate_berger_recoil_matrix_interval_convolution import CERTIFICATE, build
def main():
    value=json.loads(CERTIFICATE.read_text()); assert value==build(); assert value["flags"]["COMPLEX_MATRIX_VECTOR_INTERVAL_CONVOLUTION_EXPORTED"]; assert not value["flags"]["PHYSICAL_BERGER_FORM_CHAIN_BOUND"]; print("Berger recoil matrix interval convolution verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
