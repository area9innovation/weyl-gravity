import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def ld(n,p): s=importlib.util.spec_from_file_location(n,ROOT/p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def test_current():
 g=ld("pgen","quantum-weyl/transfer/two_phase_counterflow_physical_state_positivity_nonactivation.py"); c,a,_=g.build(); assert json.loads(g.CERT.read_text())==c and json.loads(g.ATLAS.read_text())==a
def test_verify():
 v=ld("pver","quantum-weyl/transfer/verify_two_phase_counterflow_physical_state_positivity_nonactivation.py"); v.verify(json.loads(v.C.read_text()),json.loads(v.A.read_text()))
def test_receipt_hashes():
 v=ld("pver_receipt","quantum-weyl/transfer/verify_two_phase_counterflow_physical_state_positivity_nonactivation.py"); c=json.loads(v.C.read_text()); v.verify_receipt(json.loads(v.R.read_text()),c)
def test_closed():
 c=json.loads((ROOT/"quantum-weyl/transfer/certificates/TWO_PHASE_COUNTERFLOW_PHYSICAL_STATE_POSITIVITY_NONACTIVATION_V1.json").read_text()); assert c["activation_gate"]["gate_passed"] is False
