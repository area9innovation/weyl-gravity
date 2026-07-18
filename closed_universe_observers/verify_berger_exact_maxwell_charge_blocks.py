#!/usr/bin/env python3
import json
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import CERTIFICATE,build
def main():
 v=json.loads(CERTIFICATE.read_text());assert v==build();assert v["dense_engine_audit"]["laplacian_entry_defect_count"]==0;assert v["dense_engine_audit"]["codifferential_entry_defect_count"]==0;print("exact Maxwell charge blocks verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
