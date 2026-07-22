import copy
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[4]

def load(name, relative):
    spec=importlib.util.spec_from_file_location(name, ROOT/relative); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def test_generated_outputs_current():
    p=load("compact_producer","quantum-weyl/pt_cpt/compact_blocks/compact_block_feasibility.py")
    c=p.build(); assert json.loads(p.OUTPUT.read_text())==c; assert json.loads(p.ATLAS.read_text())==p.atlas_fragment(c)

def test_independent_verifier():
    v=load("compact_verifier","quantum-weyl/pt_cpt/compact_blocks/verify_compact_block_feasibility.py")
    v.verify_certificate(json.loads(v.CERTIFICATE.read_text()))

def test_decisive_mutations():
    v=load("compact_mutations","quantum-weyl/pt_cpt/compact_blocks/verify_compact_block_feasibility.py"); c=json.loads(v.CERTIFICATE.read_text())
    for path,value in (("eigen",True),("C",True),("quantum","ESTABLISHED")):
        m=copy.deepcopy(c)
        if path=="eigen": m["basis_invariance"]["unconstrained_eigenbasis_metric_accepted"]=value
        elif path=="C": m["Mannheim_C_gate"]["genuine_Mannheim_C_certified"]=value
        else: m["decision"]["particles_scattering_or_unitarity"]=value
        with pytest.raises(Exception): v.verify_certificate(m,pins=False)

def test_receipt_hashes():
    v=load("compact_receipt","quantum-weyl/pt_cpt/compact_blocks/verify_compact_block_feasibility.py")
    v.verify_receipt(json.loads(v.RECEIPT.read_text()),json.loads(v.CERTIFICATE.read_text()))
