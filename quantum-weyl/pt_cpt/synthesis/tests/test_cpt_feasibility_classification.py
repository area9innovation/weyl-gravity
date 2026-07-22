import importlib.util,json,copy
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[4]
def load(n,r):
 s=importlib.util.spec_from_file_location(n,ROOT/r);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_current():
 p=load("p","quantum-weyl/pt_cpt/synthesis/cpt_feasibility_classification.py");c=p.build();assert json.loads(p.OUTPUT.read_text())==c;assert json.loads(p.PAPER.read_text())==p.paper_request(c)
def test_verifier():
 v=load("v","quantum-weyl/pt_cpt/synthesis/verify_cpt_feasibility_classification.py");v.verify(json.loads(v.CERT.read_text()))
def test_promotions_rejected():
 v=load("vm","quantum-weyl/pt_cpt/synthesis/verify_cpt_feasibility_classification.py");c=json.loads(v.CERT.read_text())
 for field,value in (("conformal_gravity_unitarity","ESTABLISHED"),("ghost_normalizer","CLOSED")):
  m=copy.deepcopy(c);m["decision"][field]=value
  with pytest.raises(Exception):v.verify(m,pins=False)
def test_receipt():
 v=load("vr","quantum-weyl/pt_cpt/synthesis/verify_cpt_feasibility_classification.py");v.verify_receipt(json.loads(v.RECEIPT.read_text()),json.loads(v.CERT.read_text()))
