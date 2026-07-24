import json
from fractions import Fraction
from .runner import CERT,RAW,AGG,P,sha
def main():
 c=json.loads(CERT.read_text()); r=json.loads(RAW.read_text()); a=json.loads(AGG.read_text())
 assert c["runs"]["raw"]["sha256"]==sha(RAW) and c["runs"]["aggregate"]["sha256"]==sha(AGG)
 assert c["imports"]["v4_raw"]["sha256"]==sha(P/"adaptive-raw-run.json")
 assert r["observations"][0]["kind"]=="imported_parent_observation"
 assert [e["panel"] for e in r["accepted_segments"]]==[206,207]
 assert Fraction(a["summary"]["coverage_stop"])==Fraction(104,512)
 assert not any(a["closed_claim_gates"].values())
 print("v5 verifier: PASS (children 206/207; coverage 104/512)")
if __name__=="__main__": main()
