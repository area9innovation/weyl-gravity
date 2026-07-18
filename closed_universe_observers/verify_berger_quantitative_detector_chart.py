#!/usr/bin/env python3
import json
from jsonschema import Draft202012Validator
from closed_universe_observers.generate_berger_quantitative_detector_chart import CERTIFICATE,DEPENDENCIES,SCHEMA,_sha256,chart_audit
def main()->int:
 v=json.loads(CERTIFICATE.read_text());s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v)
 for n,p in DEPENDENCIES.items():assert v["dependency_refs"][n]["sha256"]==_sha256(p)
 assert chart_audit()["positive_branch_margin_y_norm_squared_below_1_over_10000"];assert not chart_audit(double_radius=True)["positive_branch_margin_y_norm_squared_below_1_over_10000"]
 print("BERGER_QUANTITATIVE_DETECTOR_ROD_CHART verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
