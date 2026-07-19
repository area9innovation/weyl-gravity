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
def rational(numerator, denominator=1): return {"numerator":numerator,"denominator":denominator}

def expected_jet(generator_kind, axis, coefficient):
    name, vertical = ("f0", [1]) if generator_kind == "profile" else ("R0_1", [])
    spacetime = [0,0,0,0]; spacetime[axis] = 1
    return [{
        "coefficient": {
            "rational": rational(coefficient[0].numerator, coefficient[0].denominator),
            "sqrt10": rational(coefficient[1].numerator, coefficient[1].denominator),
        },
        "factors": [{
            "kind": generator_kind,
            "name": name,
            "vertical_multiindex": vertical,
            "spacetime_multiindex": spacetime,
        }],
    }]

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
    assert audit["frame_structure_constants"] == {
        "[e0,ei]":"0 for i=1,2,3",
        "[e1,e2]":"(3 sqrt(10)/20)e3",
        "[e2,e3]":"(2 sqrt(10)/3)e1",
        "[e3,e1]":"(2 sqrt(10)/3)e2",
    }
    bracket_data = {
        "[e1,e2]=(3 sqrt(10)/20)e3": (3, (Fraction(0), Fraction(3,20))),
        "[e2,e3]=(2 sqrt(10)/3)e1": (1, (Fraction(0), Fraction(2,3))),
        "[e3,e1]=(2 sqrt(10)/3)e2": (2, (Fraction(0), Fraction(2,3))),
    }
    assert len(audit["commutator_replay"]) == 12
    for row in audit["commutator_replay"]:
        if row["identity"] in bracket_data:
            axis, coefficient = bracket_data[row["identity"]]
            independent = expected_jet(row["generator_kind"], axis, coefficient)
        else:
            assert row["identity"] in {"[e0,e1]=0","[e0,e2]=0","[e0,e3]=0"}
            independent = []
        assert row["actual"] == independent == row["expected"]
        assert row["defect_count"] == 0
    assert audit["commutator_defect_count"] == 0
    assert audit["drop_e1_e2_structure_defect_count"] == 2
    assert audit["flip_e1_e2_structure_defect_count"] == 2
    assert all(row["detected"] for row in v["mutations"])
    assert v["flags"]["NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED"] is True
    assert not v["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"] and not v["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_COMPONENT_JET_CONTRACT independent verification: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
