#!/usr/bin/env python3
"""Independent verification of the 108-row component/jet contract."""
import hashlib, json
from fractions import Fraction
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"closed_universe_observers"
CERT=P/"certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json"; SCHEMA=P/"schema/berger-108-row-component-jet-contract-v1.schema.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
    v=json.loads(CERT.read_text()); s=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(v)
    for ref in v["dependency_refs"].values():
        if sha(ROOT/ref["path"])!=ref["sha256"]: raise AssertionError("dependency hash drift")
    c=v["carrier_contract"]; rows=c["rows"]; pairing=c["pairing_entries"]
    assert [r["index"] for r in rows]==list(range(108)); assert len({r["row_id"] for r in rows})==108
    assert digest(rows)==c["rows_canonical_sha256"] and digest(pairing)==c["pairing_canonical_sha256"]
    matrix=[[Fraction(0) for _ in range(108)] for _ in range(108)]
    for left,right,terms in pairing:
        assert terms[0][0]==[0,0,0,0]; matrix[left][right]=Fraction(terms[0][1])
    assert all(sum(x != 0 for x in row)==1 for row in matrix)
    assert all(matrix[i][j]==-matrix[j][i] for i in range(108) for j in range(108))
    spec=v["coefficient_algebra"]["exact_profile_specializations"]
    assert spec["detector_profiles"]["epsilon_0"]==spec["detector_profiles"]["epsilon_1"]=="1/128"
    assert spec["emitter_switches"]["h0_radius"]=="1/64" and spec["emitter_switches"]["h1_radius"]=="3/64"
    audit=v["coefficient_algebra"]["audit"]; assert audit["Leibniz_defect_count"]==0 and audit["arbitrary_finite_jet_tower"]
    assert all(row["detected"] for row in v["mutations"])
    assert not v["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"] and not v["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_COMPONENT_JET_CONTRACT independent verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
